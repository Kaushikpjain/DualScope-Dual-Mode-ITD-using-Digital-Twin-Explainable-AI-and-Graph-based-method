"""
Object Identification Module
Uses YOLO class labels for primary identification.
"""
from typing import Tuple
import numpy as np
import config


class ObjectIdentifier:
    """Identifies objects using YOLO detection class labels."""

    def __init__(self, detector=None):
        self.detector = detector
        # COCO class descriptions for richer identification output
        self._class_descriptions = {
            0: "Person / Human", 1: "Bicycle", 2: "Car", 3: "Motorcycle",
            4: "Airplane", 5: "Bus", 6: "Train", 7: "Truck", 8: "Boat",
            9: "Traffic Light", 10: "Fire Hydrant", 11: "Stop Sign",
            12: "Parking Meter", 13: "Bench", 14: "Bird", 15: "Cat",
            16: "Dog", 17: "Horse", 18: "Sheep", 19: "Cow", 20: "Elephant",
            21: "Bear", 22: "Zebra", 23: "Giraffe", 24: "Backpack",
            25: "Umbrella", 26: "Handbag", 27: "Tie", 28: "Suitcase",
            29: "Frisbee", 30: "Skis", 31: "Snowboard", 32: "Sports Ball",
            33: "Kite", 34: "Baseball Bat", 35: "Baseball Glove",
            36: "Skateboard", 37: "Surfboard", 38: "Tennis Racket",
            39: "Bottle", 40: "Wine Glass", 41: "Cup", 42: "Fork",
            43: "Knife", 44: "Spoon", 45: "Bowl", 46: "Banana",
            47: "Apple", 48: "Sandwich", 49: "Orange", 50: "Broccoli",
            51: "Carrot", 52: "Hot Dog", 53: "Pizza", 54: "Donut",
            55: "Cake", 56: "Chair", 57: "Couch", 58: "Potted Plant",
            59: "Bed", 60: "Dining Table", 61: "Toilet", 62: "TV",
            63: "Laptop", 64: "Mouse", 65: "Remote", 66: "Keyboard",
            67: "Cell Phone", 68: "Microwave", 69: "Oven", 70: "Toaster",
            71: "Sink", 72: "Refrigerator", 73: "Book", 74: "Clock",
            75: "Vase", 76: "Scissors", 77: "Teddy Bear", 78: "Hair Dryer",
            79: "Toothbrush",
        }

    def identify(self, class_name: str, class_id: int, confidence: float) -> Tuple[str, float]:
        """
        Identify an object given its YOLO class info.
        Returns (description, confidence).
        """
        description = self._class_descriptions.get(class_id, class_name)
        return description, confidence

    def identify_from_frame(self, frame: np.ndarray, bbox: tuple) -> Tuple[str, float]:
        """
        Identify the primary object in a cropped region.
        Falls back to YOLO detection on the cropped area.
        """
        if self.detector is None:
            return "Unknown", 0.0

        x1, y1, x2, y2 = bbox
        crop = frame[max(0, y1):y2, max(0, x1):x2]
        if crop.size == 0:
            return "Unknown", 0.0

        detections = self.detector.detect(crop)
        if detections:
            best = max(detections, key=lambda d: d.confidence)
            return self.identify(best.class_name, best.class_id, best.confidence)
        return "Unknown", 0.0
