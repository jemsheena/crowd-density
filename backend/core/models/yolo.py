"""YOLO detector wrapper."""
from ultralytics import YOLO
import numpy as np
import cv2
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Box:
    """Bounding box with class and confidence."""
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float
    cls: int  # class ID (0 = person)


class YoloDetector:
    """YOLO detector for person detection."""
    
    def __init__(self, model_path: str = "yolov8n", conf_threshold: float = 0.25, img_size: int = 960):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Model name (yolov8n, yolov8s) or path to weights
            conf_threshold: Confidence threshold
            img_size: Input image size (long side)
        """
        self.conf_threshold = conf_threshold
        self.img_size = img_size
        self.model = YOLO(model_path)
        self.model.fuse()  # Fuse model for faster inference
    
    def infer(self, image: np.ndarray) -> List[Box]:
        """
        Run inference on image.
        
        Args:
            image: BGR image (numpy array)
            
        Returns:
            List of detected boxes (person class only)
        """
        # Run inference
        results = self.model(image, conf=self.conf_threshold, imgsz=self.img_size, verbose=False)
        
        boxes = []
        if results and len(results) > 0:
            result = results[0]
            boxes_tensor = result.boxes
            
            for i in range(len(boxes_tensor)):
                # Get box coordinates
                box = boxes_tensor.xyxy[i].cpu().numpy()
                conf = float(boxes_tensor.conf[i].cpu().numpy())
                cls = int(boxes_tensor.cls[i].cpu().numpy())
                
                # Only return person class (class 0)
                if cls == 0:
                    boxes.append(Box(
                        x1=float(box[0]),
                        y1=float(box[1]),
                        x2=float(box[2]),
                        y2=float(box[3]),
                        conf=conf,
                        cls=cls
                    ))
        
        return boxes
    
    def boxes_to_heatmap(self, image_shape: Tuple[int, int], boxes: List[Box]) -> np.ndarray:
        """
        Convert bounding boxes to a density-like heatmap.
        
        Args:
            image_shape: (height, width) of original image
            boxes: List of detected boxes
            
        Returns:
            Density map (H, W) with Gaussian kernels at box centers
        """
        h, w = image_shape
        heatmap = np.zeros((h, w), dtype=np.float32)
        
        for box in boxes:
            # Box center
            cx = int((box.x1 + box.x2) / 2)
            cy = int((box.y1 + box.y2) / 2)
            
            # Box size
            box_w = box.x2 - box.x1
            box_h = box.y2 - box.y1
            radius = max(int(min(box_w, box_h) / 2), 3)
            
            # Draw Gaussian kernel
            cv2.circle(heatmap, (cx, cy), radius, 1.0, -1)
        
        # Normalize
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        return heatmap

