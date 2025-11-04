"""Webcam frame reader."""
import cv2
import asyncio
from typing import AsyncIterator, Optional
import numpy as np


class WebcamReader:
    """Async webcam reader."""
    
    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self.cap: Optional[cv2.VideoCapture] = None
    
    async def start(self):
        """Open webcam."""
        loop = asyncio.get_event_loop()
        self.cap = await loop.run_in_executor(
            None, cv2.VideoCapture, self.device_index
        )
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open webcam: {self.device_index}")
    
    async def stop(self):
        """Close webcam."""
        if self.cap:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.cap.release)
            self.cap = None
    
    async def frames(self) -> AsyncIterator[np.ndarray]:
        """Async iterator of frames."""
        loop = asyncio.get_event_loop()
        while self.cap and self.cap.isOpened():
            ret, frame = await loop.run_in_executor(None, self.cap.read)
            if not ret:
                break
            yield frame
            await asyncio.sleep(0.033)  # ~30 FPS

