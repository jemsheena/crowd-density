"""Prometheus metrics instrumentation."""
from prometheus_client import Counter, Gauge, Histogram
from typing import Optional
import time


# Metrics
inference_counter = Counter(
    'inference_total',
    'Total number of inferences',
    ['model', 'stream_id']
)

inference_latency = Histogram(
    'inference_latency_ms',
    'Inference latency in milliseconds',
    ['model', 'stream_id'],
    buckets=[10, 25, 50, 100, 200, 500, 1000]
)

inference_fps = Gauge(
    'inference_fps',
    'Current inference FPS',
    ['stream_id']
)

selector_decision_total = Counter(
    'selector_decision_total',
    'Total number of model selections',
    ['model', 'stream_id']
)

errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['kind', 'stream_id']
)

stream_count = Gauge(
    'stream_count_current',
    'Current count for stream',
    ['stream_id', 'zone_id']
)

stream_active = Gauge(
    'stream_active',
    'Number of active streams',
    []
)


class InferenceTimer:
    """Context manager for timing inference."""
    
    def __init__(self, model: str, stream_id: str = "default"):
        self.model = model
        self.stream_id = stream_id
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            latency_ms = (time.time() - self.start_time) * 1000
            inference_latency.labels(
                model=self.model,
                stream_id=self.stream_id
            ).observe(latency_ms)
            
            if exc_type is None:
                inference_counter.labels(
                    model=self.model,
                    stream_id=self.stream_id
                ).inc()
            else:
                errors_total.labels(
                    kind=exc_type.__name__,
                    stream_id=self.stream_id
                ).inc()


def record_fps(stream_id: str, fps: float):
    """Record FPS for a stream."""
    inference_fps.labels(stream_id=stream_id).set(fps)


def record_selector_decision(model: str, stream_id: str = "default"):
    """Record model selection decision."""
    selector_decision_total.labels(model=model, stream_id=stream_id).inc()


def record_stream_count(stream_id: str, count: int, zone_id: str = "total"):
    """Record current count for a stream/zone."""
    stream_count.labels(stream_id=stream_id, zone_id=zone_id).set(count)


def record_stream_active(count: int):
    """Record number of active streams."""
    stream_active.set(count)

