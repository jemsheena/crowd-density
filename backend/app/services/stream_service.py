"""Stream service for managing stream lifecycle."""
import asyncio
from typing import Dict, Optional
import logging

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
from core.utils.logger import get_logger

logger = get_logger(__name__)


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
        logger.info(f"[{self.stream_id}] Starting stream worker...")
        logger.debug(f"[{self.stream_id}] Config: {self.config}")
        
        self.running = True
        
        try:
            # Initialize reader based on source
            source = self.config["source"]
            logger.info(f"[{self.stream_id}] Initializing {source['kind']} reader...")
            
            if source["kind"] == "rtsp":
                self.reader = RTSPReader(source["url"])
                logger.info(f"[{self.stream_id}] RTSP URL: {source['url']}")
            elif source["kind"] == "file":
                self.reader = FileReader(source["url"])
                logger.info(f"[{self.stream_id}] File path: {source['url']}")
            elif source["kind"] == "webcam":
                device_idx = source.get("device_index", 0)
                self.reader = WebcamReader(device_idx)
                logger.info(f"[{self.stream_id}] Webcam device: {device_idx}")
            else:
                raise ValueError(f"Unknown source kind: {source['kind']}")
            
            await self.reader.start()
            logger.info(f"[{self.stream_id}] Reader started successfully")
        except Exception as e:
            logger.error(f"[{self.stream_id}] Failed to start reader: {e}", exc_info=True)
            raise
        
        # Initialize models
        inference_config = self.config.get("inference", {})
        mode = inference_config.get("mode", "hybrid")
        logger.info(f"[{self.stream_id}] Inference mode: {mode}")
        
        yolo = None
        csrnet = None
        
        try:
            if mode in ["detector", "hybrid"]:
                detector_cfg = inference_config.get("detector", {})
                model_name = detector_cfg.get("model", "yolov8n")
                logger.info(f"[{self.stream_id}] Loading YOLO model: {model_name}")
                yolo = YoloDetector(
                    model_path=model_name,
                    conf_threshold=detector_cfg.get("conf", 0.25),
                    img_size=detector_cfg.get("imgsz", 960)
                )
                logger.info(f"[{self.stream_id}] YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"[{self.stream_id}] Failed to load YOLO model: {e}", exc_info=True)
            if mode == "detector":
                raise  # Fail if detector is required
        
        try:
            if mode in ["density", "hybrid"]:
                density_cfg = inference_config.get("density", {})
                logger.info(f"[{self.stream_id}] Loading CSRNet model...")
                csrnet = CSRNetInference(
                    model_path=settings.CSRNET_MODEL_PATH,
                    input_size=density_cfg.get("input_size", 768)
                )
                logger.info(f"[{self.stream_id}] CSRNet model loaded successfully")
        except Exception as e:
            logger.warning(f"[{self.stream_id}] Failed to load CSRNet model: {e}", exc_info=True)
            if mode == "density":
                logger.error(f"[{self.stream_id}] Density mode requires CSRNet - failing")
                raise
        
        # Initialize pipeline
        zones = self.config.get("zones", [])
        logger.info(f"[{self.stream_id}] Initializing pipeline with {len(zones)} zones")
        self.pipeline = InferencePipeline(
            yolo_detector=yolo,
            csrnet=csrnet,
            ema_alpha=settings.DEFAULT_EMA_ALPHA,
            zones=zones
        )
        
        # Set status
        StreamState.set_status(self.stream_id, "running")
        logger.info(f"[{self.stream_id}] Stream worker started successfully")
        
        # Start processing loop
        self.task = asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Stop the stream worker."""
        logger.info(f"[{self.stream_id}] Stopping stream worker...")
        self.running = False
        if self.reader:
            try:
                await self.reader.stop()
                logger.info(f"[{self.stream_id}] Reader stopped")
            except Exception as e:
                logger.error(f"[{self.stream_id}] Error stopping reader: {e}", exc_info=True)
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        StreamState.set_status(self.stream_id, "stopped")
        logger.info(f"[{self.stream_id}] Stream worker stopped")
    
    async def _process_loop(self):
        """Main processing loop."""
        from core.postprocess.heatmap import density_to_heatmap_image
        
        frame_count = 0
        error_count = 0
        
        try:
            inference_config = self.config.get("inference", {})
            mode = inference_config.get("mode", "hybrid")
            logger.info(f"[{self.stream_id}] Starting frame processing loop (mode: {mode})")
            
            async for frame in self.reader.frames():
                if not self.running:
                    logger.info(f"[{self.stream_id}] Processing stopped by flag")
                    break
                
                frame_count += 1
                
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
                    
                    # Encode frame as base64 (for WebSocket)
                    import cv2
                    import base64
                    frame_data = None
                    if frame_count % 2 == 0:  # Send every other frame to reduce bandwidth
                        # Resize frame if too large (max 1920x1080)
                        h, w = frame.shape[:2]
                        if w > 1920 or h > 1080:
                            scale = min(1920 / w, 1080 / h)
                            new_w, new_h = int(w * scale), int(h * scale)
                            frame_resized = cv2.resize(frame, (new_w, new_h))
                        else:
                            frame_resized = frame
                        
                        # Encode frame as JPEG (smaller than PNG)
                        _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        frame_base64 = base64.b64encode(buffer).decode('utf-8')
                        frame_data = f"data:image/jpeg;base64,{frame_base64}"
                    
                    # Prepare stats
                    # Use raw count for current frame (not smoothed/cumulative)
                    current_frame_count = result.get("count", 0)  # Raw count for current frame
                    stats = {
                        "id": self.stream_id,
                        "count": current_frame_count,  # Current frame count
                        "count_smoothed": result.get("count_smoothed", current_frame_count),  # EMA smoothed (for reference)
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
                    
                    # Log every 30 frames (about once per second at 30 FPS)
                    if frame_count % 30 == 0:
                        logger.debug(
                            f"[{self.stream_id}] Frame {frame_count}: "
                            f"count={stats['count']}, fps={stats['fps']:.1f}, "
                            f"latency={stats['latency_ms']:.1f}ms, model={stats['model_used']}"
                        )
                    
                    # Update Redis state
                    StreamState.update_stats(self.stream_id, stats)
                    
                    # Publish to Redis pub/sub with heatmap and frame (WebSocket will pick it up)
                    StreamState.publish_update(self.stream_id, stats, heatmap_data, frame_data)
                    
                    # Reset error count on success
                    error_count = 0
                    
                    # Small delay to control FPS
                    await asyncio.sleep(0.033)  # ~30 FPS max
                    
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"[{self.stream_id}] Error processing frame {frame_count}: {e}",
                        exc_info=True
                    )
                    
                    # Log warning if too many consecutive errors
                    if error_count >= 10:
                        logger.warning(
                            f"[{self.stream_id}] Too many consecutive errors ({error_count}). "
                            "Stopping processing."
                        )
                        break
                    
                    continue
        
        except Exception as e:
            logger.error(f"[{self.stream_id}] Stream worker fatal error: {e}", exc_info=True)
            StreamState.set_status(self.stream_id, "error")
        finally:
            self.running = False
            logger.info(
                f"[{self.stream_id}] Processing loop ended. "
                f"Processed {frame_count} frames, {error_count} errors"
            )


# Global worker registry
_active_workers: Dict[str, StreamWorker] = {}


class StreamService:
    """Service for managing streams."""
    
    @staticmethod
    async def create_stream(stream_data: StreamCreate) -> str:
        """Create and start a new stream."""
        import uuid
        stream_id = f"str_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating new stream: {stream_id} (name: {stream_data.name})")
        
        # Store config
        config = {
            "id": stream_id,
            "name": stream_data.name,
            "source": stream_data.source.dict(),
            "inference": stream_data.inference.dict(),
            "zones": [z.dict() for z in stream_data.zones],
            "output": stream_data.output.dict() if stream_data.output else {},
        }
        
        logger.debug(f"Stream config: {config}")
        
        # Create and start worker
        worker = StreamWorker(stream_id, config)
        _active_workers[stream_id] = worker
        
        # Start in background
        asyncio.create_task(worker.start())
        
        logger.info(f"Stream {stream_id} worker started in background")
        return stream_id
    
    @staticmethod
    async def stop_stream(stream_id: str):
        """Stop a stream."""
        logger.info(f"Stopping stream: {stream_id}")
        if stream_id in _active_workers:
            worker = _active_workers[stream_id]
            await worker.stop()
            del _active_workers[stream_id]
            logger.info(f"Stream {stream_id} stopped and removed")
        else:
            logger.warning(f"Stream {stream_id} not found in active workers")
    
    @staticmethod
    def get_worker(stream_id: str) -> Optional[StreamWorker]:
        """Get active worker for stream."""
        return _active_workers.get(stream_id)

