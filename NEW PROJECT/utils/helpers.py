"""
Common Helper Functions
"""
import time
from collections import deque


class FPSCounter:
    """Tracks frames-per-second with a rolling window."""

    def __init__(self, window_size: int = 30):
        self._timestamps = deque(maxlen=window_size)

    def tick(self):
        """Record a frame timestamp."""
        self._timestamps.append(time.time())

    def get_fps(self) -> float:
        """Calculate current FPS."""
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / elapsed


def format_timestamp(ts: float) -> str:
    """Format a Unix timestamp to a readable string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def clamp(value, min_val, max_val):
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))
