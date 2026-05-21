"""
Multi-Object Tracker with Target Locking
Uses DeepSORT for persistent identity tracking across frames.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from collections import defaultdict
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
import config


@dataclass
class TrackedObject:
    """A tracked object with identity and trajectory."""
    track_id: int
    bbox: tuple                 # (x1, y1, x2, y2)
    class_name: str
    confidence: float
    class_id: int
    center: tuple               # (cx, cy)
    velocity: tuple = (0, 0)    # (vx, vy) pixels per frame
    trajectory: list = field(default_factory=list)


class ObjectTracker:
    """DeepSORT-based multi-object tracker with target locking."""

    def __init__(self):
        self.tracker = DeepSort(
            max_age=config.MAX_AGE,
            n_init=config.N_INIT,
            max_cosine_distance=config.MAX_COSINE_DISTANCE,
            max_iou_distance=0.7,
        )
        self._locked_id: Optional[int] = None
        self._trajectories: Dict[int, list] = defaultdict(list)
        self._prev_centers: Dict[int, tuple] = {}

    def update(self, detections, frame: np.ndarray) -> List[TrackedObject]:
        """
        Update tracker with new detections.
        Returns list of TrackedObject with persistent IDs.
        """
        if not detections:
            # Still update tracker with empty to age out tracks
            self.tracker.update_tracks([], frame=frame)
            return []

        # Format detections for DeepSORT: [([x1, y1, w, h], confidence, class_name), ...]
        raw_dets = []
        det_meta = {}
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det.bbox
            w, h = x2 - x1, y2 - y1
            raw_dets.append(([x1, y1, w, h], det.confidence, det.class_name))
            det_meta[i] = det

        tracks = self.tracker.update_tracks(raw_dets, frame=frame)

        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = [int(v) for v in ltrb]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Calculate velocity
            vx, vy = 0, 0
            if track_id in self._prev_centers:
                px, py = self._prev_centers[track_id]
                vx, vy = cx - px, cy - py
            self._prev_centers[track_id] = (cx, cy)

            # Store trajectory (keep last 60 points)
            self._trajectories[track_id].append((cx, cy))
            if len(self._trajectories[track_id]) > 60:
                self._trajectories[track_id] = self._trajectories[track_id][-60:]

            # Get class info from the detection metadata if available
            det_class = track.det_class if hasattr(track, 'det_class') and track.det_class else "unknown"
            det_conf = track.det_conf if hasattr(track, 'det_conf') and track.det_conf else 0.0

            # Try to get class name from the original class string
            class_name = det_class if isinstance(det_class, str) else "unknown"
            class_id = -1

            tracked_objects.append(TrackedObject(
                track_id=track_id,
                bbox=(x1, y1, x2, y2),
                class_name=class_name,
                confidence=float(det_conf) if det_conf else 0.0,
                class_id=class_id,
                center=(cx, cy),
                velocity=(vx, vy),
                trajectory=list(self._trajectories[track_id]),
            ))

        return tracked_objects

    def lock_target(self, track_id: int):
        """Lock onto a specific tracked object by ID."""
        self._locked_id = track_id

    def unlock_target(self):
        """Unlock the current target."""
        self._locked_id = None

    def get_locked_target(self, tracked_objects: List[TrackedObject]) -> Optional[TrackedObject]:
        """Return the currently locked target, if still tracked."""
        if self._locked_id is None:
            return None
        for obj in tracked_objects:
            if obj.track_id == self._locked_id:
                return obj
        return None

    def get_trajectory(self, track_id: int) -> list:
        """Get the trajectory history for a given track ID."""
        return self._trajectories.get(track_id, [])
