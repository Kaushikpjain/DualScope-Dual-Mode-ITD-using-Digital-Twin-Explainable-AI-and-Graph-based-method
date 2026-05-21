"""
Traffic Violation Detection Module
Detects vehicles crossing stop lines during red signals.
"""
import time
from dataclasses import dataclass
from typing import List, Dict, Set
import config


@dataclass
class Violation:
    """A recorded traffic violation."""
    track_id: int
    violation_type: str   # "STOP_LINE_CROSSED", "RESTRICTED_ZONE", "NO_HELMET"
    timestamp: float
    details: str


class TrafficMonitor:
    """Monitors traffic rule compliance using tracked vehicle positions."""

    def __init__(self):
        self.signal_state: str = "GREEN"  # "RED" or "GREEN"
        self._signal_toggle_time: float = time.time()
        self._signal_cycle: float = 10.0  # seconds per signal phase
        self._auto_signal: bool = True     # auto-cycle or manual

        # Track which vehicles have already been flagged to avoid duplicates
        self._flagged_vehicles: Set[int] = set()
        self._prev_positions: Dict[int, tuple] = {}

    def set_signal(self, state: str):
        """Manually set signal state to RED or GREEN."""
        self.signal_state = state.upper()
        self._auto_signal = False

    def toggle_signal(self):
        """Toggle between RED and GREEN."""
        self.signal_state = "GREEN" if self.signal_state == "RED" else "RED"

    def enable_auto_signal(self, cycle_seconds: float = 10.0):
        """Enable automatic signal cycling."""
        self._auto_signal = True
        self._signal_cycle = cycle_seconds
        self._signal_toggle_time = time.time()

    def _update_auto_signal(self):
        """Auto-cycle the traffic signal."""
        if self._auto_signal:
            elapsed = time.time() - self._signal_toggle_time
            if elapsed >= self._signal_cycle:
                self.signal_state = "GREEN" if self.signal_state == "RED" else "RED"
                self._signal_toggle_time = time.time()

    def check_violations(self, tracked_objects) -> List[Violation]:
        """
        Check tracked objects for traffic violations.
        Returns new violations detected in this frame.
        """
        self._update_auto_signal()
        violations = []

        for obj in tracked_objects:
            # Only process vehicles
            if not self._is_vehicle(obj):
                continue

            tid = obj.track_id
            cx, cy = obj.center
            x1, y1, x2, y2 = obj.bbox

            # --- Stop line violation ---
            if self.signal_state == "RED" and config.STOP_LINE_Y is not None:
                bottom_y = y2  # bottom edge of vehicle

                # Check if vehicle crossed the stop line
                prev = self._prev_positions.get(tid)
                if prev is not None:
                    prev_bottom_y = prev[1]
                    # Vehicle was above stop line, now below it
                    if prev_bottom_y <= config.STOP_LINE_Y < bottom_y:
                        if tid not in self._flagged_vehicles:
                            violations.append(Violation(
                                track_id=tid,
                                violation_type="STOP_LINE_CROSSED",
                                timestamp=time.time(),
                                details=f"Vehicle {obj.class_name} (ID:{tid}) crossed stop line during RED signal",
                            ))
                            self._flagged_vehicles.add(tid)

                self._prev_positions[tid] = (cx, bottom_y)

            # --- Restricted zone violation ---
            if config.RESTRICTED_ZONE is not None:
                zx1, zy1, zx2, zy2 = config.RESTRICTED_ZONE
                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    if tid not in self._flagged_vehicles:
                        violations.append(Violation(
                            track_id=tid,
                            violation_type="RESTRICTED_ZONE",
                            timestamp=time.time(),
                            details=f"Vehicle {obj.class_name} (ID:{tid}) entered restricted zone",
                        ))
                        self._flagged_vehicles.add(tid)

        # Reset flags when signal turns green
        if self.signal_state == "GREEN":
            self._flagged_vehicles.clear()

        return violations

    def _is_vehicle(self, obj) -> bool:
        """Check if tracked object is a vehicle."""
        if hasattr(obj, 'class_id') and obj.class_id in config.VEHICLE_CLASSES:
            return True
        if hasattr(obj, 'class_name'):
            return obj.class_name in ('car', 'motorcycle', 'bus', 'truck')
        return False

    def get_signal_state(self) -> str:
        """Return current signal state."""
        self._update_auto_signal()
        return self.signal_state
