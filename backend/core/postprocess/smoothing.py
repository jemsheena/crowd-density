"""Temporal smoothing for counts."""
from typing import Optional


class EMA:
    """Exponential Moving Average for temporal smoothing."""
    
    def __init__(self, alpha: float = 0.7):
        """
        Initialize EMA.
        
        Args:
            alpha: Smoothing factor (0-1). Higher = more responsive to changes.
        """
        self.alpha = alpha
        self.val: Optional[float] = None
    
    def update(self, x: float) -> float:
        """
        Update EMA with new value.
        
        Args:
            x: New value
            
        Returns:
            Smoothed value
        """
        if self.val is None:
            self.val = x
            return x
        
        self.val = self.alpha * self.val + (1 - self.alpha) * x
        return self.val
    
    def reset(self):
        """Reset EMA to initial state."""
        self.val = None
    
    def get(self) -> Optional[float]:
        """Get current EMA value."""
        return self.val

