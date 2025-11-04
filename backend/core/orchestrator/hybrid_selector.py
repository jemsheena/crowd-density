"""Hybrid model selector based on scene characteristics."""
import cv2
import numpy as np
from typing import Literal, Optional


def scene_score(image: np.ndarray) -> float:
    """
    Compute scene complexity score using Laplacian variance.
    Higher values indicate more texture/detail (good for detector).
    Lower values indicate smoother scenes (good for density model).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(laplacian_var)


class HybridSelector:
    """Hybrid model selector with hysteresis to prevent frequent toggling."""
    
    def __init__(
        self,
        threshold_low: float = 120.0,
        threshold_high: float = 180.0,
        initial_mode: Literal["detector", "density", "hybrid"] = "density"
    ):
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.mode = initial_mode
        self._last_score = None
    
    def choose_model(self, image: np.ndarray) -> Literal["detector", "density"]:
        """
        Choose model based on scene score with hysteresis.
        
        Returns:
            "detector" for high-detail scenes (YOLO)
            "density" for low-detail scenes (CSRNet)
        """
        score = scene_score(image)
        self._last_score = score
        
        # Hysteresis logic
        if self.mode == "density" and score > self.threshold_high:
            self.mode = "detector"
        elif self.mode == "detector" and score < self.threshold_low:
            self.mode = "density"
        # If in hybrid mode, choose based on score
        elif self.mode == "hybrid":
            self.mode = "detector" if score > (self.threshold_low + self.threshold_high) / 2 else "density"
        
        return self.mode
    
    def get_last_score(self) -> Optional[float]:
        """Get the last computed scene score."""
        return self._last_score

