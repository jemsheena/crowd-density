"""CSRNet density estimation wrapper."""
import torch
import torch.nn as nn
import numpy as np
import cv2
from typing import Tuple, Optional
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)


class CSRNet(nn.Module):
    """CSRNet model architecture (stub - needs real weights)."""
    
    def __init__(self, load_weights: bool = True):
        super(CSRNet, self).__init__()
        # TODO: Implement full CSRNet architecture
        # For now, this is a placeholder
        self.conv = nn.Conv2d(3, 1, 3, padding=1)
        if load_weights:
            # TODO: Load actual weights
            pass
    
    def forward(self, x):
        # TODO: Implement forward pass
        return self.conv(x)


class CSRNetInference:
    """CSRNet inference wrapper."""
    
    def __init__(self, model_path: Optional[str] = None, input_size: int = 768, device: str = "cpu"):
        """
        Initialize CSRNet inference.
        
        Args:
            model_path: Path to model weights (.pt or .pth)
            input_size: Input size (long side)
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.input_size = input_size
        self.device = torch.device(device)
        
        # Load model
        if model_path and Path(model_path).exists():
            # TODO: Load actual model weights
            self.model = CSRNet(load_weights=True)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        else:
            # Use stub for now
            self.model = CSRNet(load_weights=False)
        
        self.model.to(self.device)
        self.model.eval()
        
        # Ensure model is in float32 mode
        self.model = self.model.float()
        logger.info(f"CSRNet model initialized on {self.device}, dtype=float32")
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for CSRNet.
        
        Args:
            image: BGR image (H, W, 3)
            
        Returns:
            Preprocessed tensor (1, 3, H', W')
        """
        h, w = image.shape[:2]
        
        # Resize to input_size (long side)
        scale = min(self.input_size / h, self.input_size / w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize
        rgb = rgb.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        rgb = (rgb - mean) / std
        
        # Convert to tensor and add batch dimension
        # Explicitly set dtype to float32 to match model weights
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0)
        tensor = tensor.to(dtype=torch.float32)  # Ensure float32, not float64 (double)
        return tensor.to(self.device)
    
    def postprocess(self, density_map: torch.Tensor, original_shape: Tuple[int, int]) -> np.ndarray:
        """
        Postprocess density map to original image size.
        
        Args:
            density_map: Model output (1, 1, H', W')
            original_shape: (H, W) of original image
            
        Returns:
            Density map resized to original size (H, W)
        """
        # Remove batch and channel dimensions
        density = density_map.squeeze().cpu().numpy()
        
        # Resize to original size
        h, w = original_shape
        density_resized = cv2.resize(density, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Ensure non-negative
        density_resized = np.maximum(density_resized, 0)
        
        return density_resized
    
    def infer(self, image: np.ndarray) -> np.ndarray:
        """
        Run inference on image.
        
        Args:
            image: BGR image (numpy array)
            
        Returns:
            Density map (H, W) where sum ≈ count
        """
        original_shape = image.shape[:2]
        
        # Preprocess
        input_tensor = self.preprocess(image)
        
        # Verify dtype
        if input_tensor.dtype != torch.float32:
            logger.warning(f"Input tensor dtype is {input_tensor.dtype}, converting to float32")
            input_tensor = input_tensor.float()
        
        # Inference
        with torch.no_grad():
            output = self.model(input_tensor)
        
        # Postprocess
        density_map = self.postprocess(output, original_shape)
        
        return density_map
    
    def to_torchscript(self, output_path: str):
        """Export model to TorchScript."""
        # TODO: Implement TorchScript export
        pass
    
    @staticmethod
    def load_torchscript(model_path: str, device: str = "cpu"):
        """Load TorchScript model."""
        # TODO: Implement TorchScript loading
        return CSRNetInference(model_path=model_path, device=device)

