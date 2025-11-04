"""Zone management and integration."""
import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import Polygon, Point
from dataclasses import dataclass


@dataclass
class ZoneStats:
    """Zone statistics."""
    id: str
    count: int
    alert: bool = False


class ZoneManager:
    """Manage zones and compute zone-based counts."""
    
    def __init__(self, zones: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize zone manager.
        
        Args:
            zones: List of zone configs with 'id', 'name', 'polygon', 'threshold'
        """
        self.zones = zones or []
        self.masks: Dict[str, np.ndarray] = {}
        self.polygons: Dict[str, Polygon] = {}
    
    def create_mask(self, zone_id: str, polygon: List[List[float]], image_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create binary mask for zone polygon.
        
        Args:
            zone_id: Zone identifier
            polygon: List of [x, y] points
            image_shape: (height, width) of image
            
        Returns:
            Binary mask (H, W)
        """
        h, w = image_shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Convert polygon to integer points
        pts = np.array(polygon, dtype=np.int32)
        
        # Fill polygon
        cv2.fillPoly(mask, [pts], 255)
        
        return mask
    
    def setup_zones(self, image_shape: Tuple[int, int]):
        """Setup zone masks for given image shape."""
        self.masks = {}
        self.polygons = {}
        
        for zone in self.zones:
            zone_id = zone["id"]
            polygon_pts = zone["polygon"]
            
            # Create mask
            mask = self.create_mask(zone_id, polygon_pts, image_shape)
            self.masks[zone_id] = mask
            
            # Create shapely polygon for point-in-polygon checks
            poly = Polygon(polygon_pts)
            self.polygons[zone_id] = poly
    
    def integrate_by_mask(self, density_map: np.ndarray, mask: np.ndarray) -> float:
        """
        Integrate density map within zone mask.
        
        Args:
            density_map: Density map (H, W)
            mask: Binary mask (H, W)
            
        Returns:
            Total count in zone
        """
        # Normalize mask to 0-1
        mask_norm = mask.astype(np.float32) / 255.0
        
        # Integrate
        count = float((density_map * mask_norm).sum())
        return count
    
    def integrate_boxes(self, boxes: List[Any], mask: np.ndarray) -> int:
        """
        Count boxes whose centers are within zone mask.
        
        Args:
            boxes: List of Box objects with x1, y1, x2, y2
            mask: Binary mask (H, W)
            
        Returns:
            Count of boxes in zone
        """
        count = 0
        for box in boxes:
            # Box center
            cx = int((box.x1 + box.x2) / 2)
            cy = int((box.y1 + box.y2) / 2)
            
            # Check if center is in mask
            if 0 <= cy < mask.shape[0] and 0 <= cx < mask.shape[1]:
                if mask[cy, cx] > 0:
                    count += 1
        
        return count
    
    def compute_stats(
        self,
        density_map: Optional[np.ndarray] = None,
        boxes: Optional[List[Any]] = None,
        image_shape: Tuple[int, int] = None
    ) -> List[ZoneStats]:
        """
        Compute statistics for all zones.
        
        Args:
            density_map: Density map (H, W) - for density model
            boxes: List of Box objects - for detector model
            image_shape: (H, W) of image
            
        Returns:
            List of ZoneStats
        """
        if not self.zones:
            return []
        
        # Setup zones if not done
        if image_shape and not self.masks:
            self.setup_zones(image_shape)
        
        stats = []
        for zone in self.zones:
            zone_id = zone["id"]
            threshold = zone.get("threshold")
            
            # Get mask
            mask = self.masks.get(zone_id)
            if mask is None:
                continue
            
            # Compute count
            if density_map is not None:
                count = self.integrate_by_mask(density_map, mask)
            elif boxes is not None:
                count = self.integrate_boxes(boxes, mask)
            else:
                count = 0
            
            # Check alert threshold
            alert = False
            if threshold is not None:
                alert = count >= threshold
            
            stats.append(ZoneStats(
                id=zone_id,
                count=int(count),
                alert=alert
            ))
        
        return stats

