"""RTSP stream frame reader."""
import cv2
import asyncio
from typing import AsyncIterator, Optional
import numpy as np
from threading import Thread
from queue import Queue


class RTSPReader:
    """Async RTSP frame reader using OpenCV VideoCapture in a thread."""
    
    def __init__(self, url: str, buffer_size: int = 2):
        self.url = url
        self.buffer_size = buffer_size
        self.queue: Queue = Queue(maxsize=buffer_size)
        self.cap: Optional[cv2.VideoCapture] = None
        self.thread: Optional[Thread] = None
        self.running = False
    
    def _read_loop(self):
        """Background thread that reads frames."""
        cap = cv2.VideoCapture(self.url)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open RTSP stream: {self.url}")
        
        self.cap = cap
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Drop oldest frame if queue is full
            if self.queue.full():
                try:
                    self.queue.get_nowait()
                except:
                    pass
            
            try:
                self.queue.put_nowait(frame)
            except:
                pass
        
        cap.release()
    
    async def start(self):
        """Start reading frames."""
        self.running = True
        self.thread = Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        
        # Wait a bit for first frame
        await asyncio.sleep(0.1)
    
    async def stop(self):
        """Stop reading frames."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    async def read_frame(self) -> Optional[np.ndarray]:
        """Read next frame (non-blocking)."""
        try:
            frame = self.queue.get_nowait()
            return frame
        except:
            return None
    
    async def frames(self) -> AsyncIterator[np.ndarray]:
        """Async iterator of frames."""
        while self.running:
            frame = await self.read_frame()
            if frame is not None:
                yield frame
            else:
                await asyncio.sleep(0.01)  # Small delay if no frame

