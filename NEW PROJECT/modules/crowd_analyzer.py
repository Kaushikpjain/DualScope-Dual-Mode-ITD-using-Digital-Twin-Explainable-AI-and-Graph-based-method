"""
Crowd Density Estimation Module
Counts people, computes density levels, and generates heatmaps.
"""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import cv2
import config


@dataclass
class CrowdStats:
    """Crowd analysis results for a single frame."""
    count: int
    density_level: str        # LOW, MEDIUM, HIGH
    density_value: float      # people per 100k pixels
    heatmap: Optional[np.ndarray] = None


class CrowdAnalyzer:
    """Analyzes crowd density from person detections."""

    def __init__(self):
        self._heatmap_accumulator = None

    def analyze(self, detections, frame_shape: tuple) -> CrowdStats:
        """
        Analyze crowd from a list of detections.
        detections: list of Detection or TrackedObject (must have .class_name / .class_id and .bbox / .center)
        frame_shape: (height, width, channels)
        """
        h, w = frame_shape[:2]

        # Filter person detections
        people = [d for d in detections if self._is_person(d)]
        count = len(people)

        # Calculate density
        frame_area = h * w
        density_value = (count / frame_area) * 100000 if frame_area > 0 else 0

        # Density level
        if count <= config.CROWD_THRESHOLD_LOW:
            density_level = "LOW"
        elif count <= config.CROWD_THRESHOLD_HIGH:
            density_level = "MEDIUM"
        else:
            density_level = "HIGH"

        # Update heatmap
        heatmap = self._update_heatmap(people, h, w)

        return CrowdStats(
            count=count,
            density_level=density_level,
            density_value=round(density_value, 2),
            heatmap=heatmap,
        )

    def _is_person(self, det) -> bool:
        """Check if detection is a person."""
        if hasattr(det, 'class_id') and det.class_id == config.PERSON_CLASS_ID:
            return True
        if hasattr(det, 'class_name') and det.class_name == 'person':
            return True
        return False

    def _update_heatmap(self, people, h: int, w: int) -> np.ndarray:
        """Accumulate person positions into a heatmap."""
        if self._heatmap_accumulator is None:
            self._heatmap_accumulator = np.zeros((h, w), dtype=np.float32)

        # Decay existing heatmap
        self._heatmap_accumulator *= config.HEATMAP_DECAY

        # Add Gaussian blobs at person centers
        for det in people:
            if hasattr(det, 'center'):
                cx, cy = det.center
            elif hasattr(det, 'bbox'):
                x1, y1, x2, y2 = det.bbox
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            else:
                continue

            # Clamp to frame bounds
            cx = max(0, min(cx, w - 1))
            cy = max(0, min(cy, h - 1))

            # Add Gaussian blob (radius ~30 pixels)
            radius = 30
            y_min = max(0, cy - radius)
            y_max = min(h, cy + radius)
            x_min = max(0, cx - radius)
            x_max = min(w, cx + radius)

            for yy in range(y_min, y_max):
                for xx in range(x_min, x_max):
                    dist = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                    if dist < radius:
                        self._heatmap_accumulator[yy, xx] += max(0, 1.0 - dist / radius)

        # Normalize for display
        heatmap_norm = self._heatmap_accumulator.copy()
        max_val = heatmap_norm.max()
        if max_val > 0:
            heatmap_norm = (heatmap_norm / max_val * 255).astype(np.uint8)
        else:
            heatmap_norm = heatmap_norm.astype(np.uint8)

        heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
        return heatmap_color
