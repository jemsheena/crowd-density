"""File-based video frame reader."""
import cv2
import asyncio
from typing import AsyncIterator, Optional
import numpy as np


class FileReader:
    """Async file video reader."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.cap: Optional[cv2.VideoCapture] = None
    
    async def start(self):
        """Open video file."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self.cap = await loop.run_in_executor(
            None, cv2.VideoCapture, self.file_path
        )
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video file: {self.file_path}")
    
    async def stop(self):
        """Close video file."""
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

