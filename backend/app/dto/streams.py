"""DTOs for stream management."""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class StreamSource(BaseModel):
    """Stream source configuration."""
    kind: Literal["rtsp", "file", "webcam"] = Field(..., description="Source type")
    url: Optional[str] = Field(None, description="URL for RTSP/file, None for webcam")
    device_index: Optional[int] = Field(None, description="Webcam device index (0, 1, ...)")


class DetectorConfig(BaseModel):
    """YOLO detector configuration."""
    model: str = Field("yolov8n", description="Model name: yolov8n, yolov8s, etc.")
    conf: float = Field(0.25, ge=0.0, le=1.0, description="Confidence threshold")
    imgsz: int = Field(960, description="Input image size (long side)")


class DensityConfig(BaseModel):
    """CSRNet density model configuration."""
    model: str = Field("csrnet_v1", description="Model name/version")
    input_size: int = Field(768, description="Input size (long side)")


class InferenceConfig(BaseModel):
    """Inference pipeline configuration."""
    mode: Literal["detector", "density", "hybrid"] = Field("hybrid", description="Inference mode")
    detector: Optional[DetectorConfig] = None
    density: Optional[DensityConfig] = None


class ZonePoint(BaseModel):
    """Point in a polygon zone."""
    x: float = Field(..., ge=0.0)
    y: float = Field(..., ge=0.0)


class ZoneConfig(BaseModel):
    """Zone configuration for counting and alerts."""
    id: str = Field(..., description="Unique zone identifier")
    name: str = Field(..., description="Zone name")
    polygon: List[List[float]] = Field(..., description="Polygon vertices as [[x,y], ...]")
    threshold: Optional[int] = Field(None, description="Alert threshold (count)")


class OutputConfig(BaseModel):
    """Output configuration."""
    heatmap: Optional[dict] = Field(None, description="Heatmap rendering config")
    colormap: Optional[str] = Field("JET", description="Colormap name")
    alpha: Optional[float] = Field(0.55, ge=0.0, le=1.0, description="Heatmap alpha blending")


class StreamCreate(BaseModel):
    """Request to create a new stream."""
    name: str = Field(..., description="Stream name")
    source: StreamSource = Field(..., description="Stream source")
    inference: InferenceConfig = Field(default_factory=InferenceConfig, description="Inference config")
    zones: List[ZoneConfig] = Field(default_factory=list, description="Monitoring zones")
    output: Optional[OutputConfig] = Field(None, description="Output configuration")


class ZoneStats(BaseModel):
    """Zone statistics."""
    id: str
    count: int
    alert: bool = False


class StreamStats(BaseModel):
    """Current stream statistics."""
    id: str
    count: int
    fps: float
    latency_ms: float
    zones: List[ZoneStats]
    model_decision: str = Field(..., description="Current model used: 'yolo' or 'csrnet'")
    updated_at: datetime


class StreamResponse(BaseModel):
    """Stream creation response."""
    id: str
    status: str = Field(..., description="Stream status: starting, running, stopped, error")


class StreamListResponse(BaseModel):
    """List of streams."""
    streams: List[StreamResponse]
    total: int

