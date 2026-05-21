"""
Suspicious Behavior Detection Module
Detects unattended objects (person leaves bag behind).
"""
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import math
import config


@dataclass
class BehaviorAlert:
    """A suspicious behavior alert."""
    alert_type: str       # "UNATTENDED_OBJECT", "LOITERING", etc.
    location: tuple       # (x, y) center of the event
    timestamp: float
    details: str
    severity: str = "WARNING"  # "WARNING" or "CRITICAL"


class BehaviorAnalyzer:
    """Analyzes object relationships across time to detect suspicious behavior."""

    def __init__(self):
        # Person-bag associations: {bag_track_id: person_track_id}
        self._bag_owner: Dict[int, int] = {}

        # Stationary bag tracking: {bag_track_id: (first_seen_pos, frames_stationary)}
        self._stationary_bags: Dict[int, Tuple[tuple, int]] = {}

        # Person last seen positions for proximity checks
        self._person_positions: Dict[int, tuple] = {}

        # Alerts already raised (to avoid repeats)
        self._raised_alerts: set = set()

    def analyze(self, tracked_objects) -> List[BehaviorAlert]:
        """
        Analyze tracked objects for suspicious behavior patterns.
        Returns list of new alerts.
        """
        alerts = []

        # Separate people and bags
        people = [o for o in tracked_objects if self._is_person(o)]
        bags = [o for o in tracked_objects if self._is_bag(o)]

        # Update person positions
        for person in people:
            self._person_positions[person.track_id] = person.center

        # Associate bags with nearest person
        for bag in bags:
            if bag.track_id not in self._bag_owner:
                nearest_person = self._find_nearest_person(bag, people)
                if nearest_person is not None:
                    self._bag_owner[bag.track_id] = nearest_person.track_id

        # Check for unattended bags
        active_person_ids = {p.track_id for p in people}

        for bag in bags:
            bid = bag.track_id
            bag_center = bag.center

            # Track stationary status
            if bid in self._stationary_bags:
                prev_pos, frames = self._stationary_bags[bid]
                dist = self._distance(bag_center, prev_pos)
                if dist < 10:  # barely moved
                    self._stationary_bags[bid] = (prev_pos, frames + 1)
                else:
                    self._stationary_bags[bid] = (bag_center, 0)
            else:
                self._stationary_bags[bid] = (bag_center, 1)

            # Check if bag is unattended
            _, frames_stationary = self._stationary_bags[bid]

            if frames_stationary >= config.UNATTENDED_FRAMES_THRESH:
                owner_id = self._bag_owner.get(bid)

                # Owner is gone OR far away
                owner_gone = owner_id is not None and owner_id not in active_person_ids
                owner_far = False
                if owner_id and owner_id in self._person_positions:
                    owner_pos = self._person_positions[owner_id]
                    if self._distance(bag_center, owner_pos) > config.UNATTENDED_DISTANCE_THRESH:
                        owner_far = True

                if (owner_gone or owner_far) and bid not in self._raised_alerts:
                    alerts.append(BehaviorAlert(
                        alert_type="UNATTENDED_OBJECT",
                        location=bag_center,
                        timestamp=time.time(),
                        details=f"Bag (ID:{bid}) left unattended — owner {'left the scene' if owner_gone else 'moved away'}",
                        severity="CRITICAL" if owner_gone else "WARNING",
                    ))
                    self._raised_alerts.add(bid)

        # Clean up stale data
        active_ids = {o.track_id for o in tracked_objects}
        self._stationary_bags = {k: v for k, v in self._stationary_bags.items() if k in active_ids}

        return alerts

    def _is_person(self, obj) -> bool:
        if hasattr(obj, 'class_id') and obj.class_id == config.PERSON_CLASS_ID:
            return True
        return hasattr(obj, 'class_name') and obj.class_name == 'person'

    def _is_bag(self, obj) -> bool:
        if hasattr(obj, 'class_id') and obj.class_id in config.BAG_CLASSES:
            return True
        return hasattr(obj, 'class_name') and obj.class_name in ('backpack', 'handbag', 'suitcase')

    def _find_nearest_person(self, bag, people) -> Optional[object]:
        """Find the person closest to a bag."""
        if not people:
            return None
        min_dist = float('inf')
        nearest = None
        for person in people:
            d = self._distance(bag.center, person.center)
            if d < min_dist and d < config.UNATTENDED_DISTANCE_THRESH:
                min_dist = d
                nearest = person
        return nearest

    @staticmethod
    def _distance(p1: tuple, p2: tuple) -> float:
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
