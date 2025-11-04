"""Stream service for managing stream lifecycle."""
import asyncio
from typing import Dict, Optional
from app.dto.streams import StreamCreate
from app.config import settings
from core.ingestion.rtsp import RTSPReader
from core.ingestion.file import FileReader
from core.ingestion.webcam import WebcamReader
from core.orchestrator.pipeline import InferencePipeline
from core.models.yolo import YoloDetector
from core.models.csrnet import CSRNetInference
from datetime import datetime
from core.state.redis_state import StreamState


class StreamWorker:
    """Background worker for processing a stream."""
    
    def __init__(self, stream_id: str, config: Dict):
        self.stream_id = stream_id
        self.config = config
        self.reader = None
        self.pipeline = None
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the stream worker."""
        self.running = True
        
        # Initialize reader based on source
        source = self.config["source"]
        if source["kind"] == "rtsp":
            self.reader = RTSPReader(source["url"])
        elif source["kind"] == "file":
            self.reader = FileReader(source["url"])
        elif source["kind"] == "webcam":
            self.reader = WebcamReader(source.get("device_index", 0))
        else:
            raise ValueError(f"Unknown source kind: {source['kind']}")
        
        await self.reader.start()
        
        # Initialize models
        inference_config = self.config.get("inference", {})
        mode = inference_config.get("mode", "hybrid")
        
        yolo = None
        csrnet = None
        
        if mode in ["detector", "hybrid"]:
            detector_cfg = inference_config.get("detector", {})
            yolo = YoloDetector(
                model_path=detector_cfg.get("model", "yolov8n"),
                conf_threshold=detector_cfg.get("conf", 0.25),
                img_size=detector_cfg.get("imgsz", 960)
            )
        
        if mode in ["density", "hybrid"]:
            density_cfg = inference_config.get("density", {})
            csrnet = CSRNetInference(
                model_path=settings.CSRNET_MODEL_PATH,
                input_size=density_cfg.get("input_size", 768)
            )
        
        # Initialize pipeline
        zones = self.config.get("zones", [])
        self.pipeline = InferencePipeline(
            yolo_detector=yolo,
            csrnet=csrnet,
            ema_alpha=settings.DEFAULT_EMA_ALPHA,
            zones=zones
        )
        
        # Set status
        StreamState.set_status(self.stream_id, "running")
        
        # Start processing loop
        self.task = asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Stop the stream worker."""
        self.running = False
        if self.reader:
            await self.reader.stop()
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        StreamState.set_status(self.stream_id, "stopped")
    
    async def _process_loop(self):
        """Main processing loop."""
        from core.postprocess.heatmap import density_to_heatmap_image
        
        try:
            inference_config = self.config.get("inference", {})
            mode = inference_config.get("mode", "hybrid")
            
            async for frame in self.reader.frames():
                if not self.running:
                    break
                
                try:
                    # Process frame
                    result = self.pipeline.process_frame(frame, inference_mode=mode)
                    
                    # Generate heatmap
                    heatmap_data = None
                    if result["density_map"] is not None:
                        heatmap_data = density_to_heatmap_image(
                            result["density_map"],
                            colormap="JET",
                            alpha=0.55
                        )
                    
                    # Prepare stats
                    stats = {
                        "id": self.stream_id,
                        "count": result["count"],
                        "fps": self.pipeline.last_fps,
                        "latency_ms": result["latency_ms"],
                        "zones": [
                            {
                                "id": z.id,
                                "count": z.count,
                                "alert": z.alert
                            }
                            for z in result["zones"]
                        ],
                        "model_used": result["model_used"],
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    
                    # Update Redis state
                    StreamState.update_stats(self.stream_id, stats)
                    
                    # Publish to Redis pub/sub with heatmap (WebSocket will pick it up)
                    StreamState.publish_update(self.stream_id, stats, heatmap_data)
                    
                    # Small delay to control FPS
                    await asyncio.sleep(0.033)  # ~30 FPS max
                    
                except Exception as e:
                    print(f"Error processing frame for {self.stream_id}: {e}")
                    continue
        
        except Exception as e:
            print(f"Stream worker error for {self.stream_id}: {e}")
            StreamState.set_status(self.stream_id, "error")
        finally:
            self.running = False


# Global worker registry
_active_workers: Dict[str, StreamWorker] = {}


class StreamService:
    """Service for managing streams."""
    
    @staticmethod
    async def create_stream(stream_data: StreamCreate) -> str:
        """Create and start a new stream."""
        import uuid
        stream_id = f"str_{uuid.uuid4().hex[:8]}"
        
        # Store config
        config = {
            "id": stream_id,
            "name": stream_data.name,
            "source": stream_data.source.dict(),
            "inference": stream_data.inference.dict(),
            "zones": [z.dict() for z in stream_data.zones],
            "output": stream_data.output.dict() if stream_data.output else {},
        }
        
        # Create and start worker
        worker = StreamWorker(stream_id, config)
        _active_workers[stream_id] = worker
        
        # Start in background
        asyncio.create_task(worker.start())
        
        return stream_id
    
    @staticmethod
    async def stop_stream(stream_id: str):
        """Stop a stream."""
        if stream_id in _active_workers:
            worker = _active_workers[stream_id]
            await worker.stop()
            del _active_workers[stream_id]
    
    @staticmethod
    def get_worker(stream_id: str) -> Optional[StreamWorker]:
        """Get active worker for stream."""
        return _active_workers.get(stream_id)

