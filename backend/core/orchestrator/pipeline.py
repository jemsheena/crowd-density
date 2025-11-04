"""Main inference pipeline."""
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import time

from core.orchestrator.hybrid_selector import HybridSelector
from core.models.yolo import YoloDetector
from core.models.csrnet import CSRNetInference
from core.postprocess.smoothing import EMA
from core.postprocess.zones import ZoneManager


class InferencePipeline:
    """Main inference pipeline orchestrating models and postprocessing."""
    
    def __init__(
        self,
        yolo_detector: Optional[YoloDetector] = None,
        csrnet: Optional[CSRNetInference] = None,
        hybrid_selector: Optional[HybridSelector] = None,
        ema_alpha: float = 0.7,
        zones: Optional[List[Dict[str, Any]]] = None,
    ):
        self.yolo = yolo_detector
        self.csrnet = csrnet
        self.selector = hybrid_selector or HybridSelector()
        self.count_ema = EMA(alpha=ema_alpha)
        self.zone_manager = ZoneManager(zones) if zones else None
        
        # Stats
        self.last_count = 0
        self.last_fps = 0.0
        self.last_latency_ms = 0.0
        self.last_model = "unknown"
        self.frame_times = []
    
    def process_frame(
        self,
        image: np.ndarray,
        inference_mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Process a single frame and return results.
        
        Returns:
            {
                "count": int,
                "density_map": Optional[np.ndarray],
                "boxes": Optional[List[Box]],
                "model_used": str,
                "zones": List[ZoneStats],
                "latency_ms": float,
            }
        """
        start_time = time.time()
        
        # Choose model
        if inference_mode == "hybrid":
            model_choice = self.selector.choose_model(image)
        elif inference_mode == "detector":
            model_choice = "detector"
        elif inference_mode == "density":
            model_choice = "density"
        else:
            model_choice = "detector"  # fallback
        
        # Run inference
        count = 0
        density_map = None
        boxes = None
        
        if model_choice == "detector" and self.yolo:
            boxes = self.yolo.infer(image)
            count = len([b for b in boxes if b.cls == 0])  # person class
            # Convert boxes to density-like heatmap
            density_map = self.yolo.boxes_to_heatmap(image.shape[:2], boxes)
        elif model_choice == "density" and self.csrnet:
            density_map = self.csrnet.infer(image)
            count = int(density_map.sum())
        
        # Apply EMA smoothing
        smoothed_count = self.count_ema.update(count)
        self.last_count = int(smoothed_count)
        
        # Zone integration
        zone_stats = []
        if self.zone_manager and (density_map is not None or boxes is not None):
            zone_stats = self.zone_manager.compute_stats(
                density_map=density_map,
                boxes=boxes,
                image_shape=image.shape[:2]
            )
        
        # Update stats
        latency_ms = (time.time() - start_time) * 1000
        self.last_latency_ms = latency_ms
        self.last_model = model_choice
        
        self.frame_times.append(time.time())
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        if len(self.frame_times) >= 2:
            elapsed = self.frame_times[-1] - self.frame_times[0]
            self.last_fps = (len(self.frame_times) - 1) / elapsed if elapsed > 0 else 0.0
        
        return {
            "count": self.last_count,
            "density_map": density_map,
            "boxes": boxes,
            "model_used": model_choice,
            "zones": zone_stats,
            "latency_ms": latency_ms,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current pipeline statistics."""
        return {
            "count": self.last_count,
            "fps": self.last_fps,
            "latency_ms": self.last_latency_ms,
            "model": self.last_model,
        }

