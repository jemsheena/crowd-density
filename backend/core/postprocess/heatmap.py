"""Heatmap rendering utilities."""
import cv2
import numpy as np
import base64
from io import BytesIO
from typing import Optional


def density_to_heatmap_image(
    density_map: np.ndarray,
    colormap: str = "JET",
    alpha: float = 0.55
) -> str:
    """
    Convert density map to base64-encoded PNG image.
    
    Args:
        density_map: Density map (H, W)
        colormap: Colormap name (JET, VIRIDIS, etc.)
        alpha: Alpha blending factor (not used in this function, kept for compatibility)
        
    Returns:
        Base64-encoded PNG image data URL
    """
    # Normalize to 0-1
    if density_map.max() > 0:
        normalized = density_map / density_map.max()
    else:
        normalized = density_map
    
    # Convert to 0-255
    normalized = (normalized * 255).astype(np.uint8)
    
    # Apply colormap
    colormap_code = getattr(cv2, f"COLORMAP_{colormap}", cv2.COLORMAP_JET)
    heatmap = cv2.applyColorMap(normalized, colormap_code)
    
    # Convert BGR to RGB
    heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # Encode to PNG
    _, buffer = cv2.imencode('.png', heatmap_rgb)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"

