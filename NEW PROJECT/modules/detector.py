"""
YOLOv8 Object Detection Module
Wraps Ultralytics YOLO for real-time object detection.
"""
from dataclasses import dataclass
from typing import List
import numpy as np
from ultralytics import YOLO
import config


@dataclass
class Detection:
    """Single detection result."""
    bbox: tuple        # (x1, y1, x2, y2) in pixels
    class_name: str
    confidence: float
    class_id: int


class ObjectDetector:
    """YOLOv8-based object detector."""

    def __init__(self, model_path=None, device=None):
        model_path = model_path or config.YOLO_MODEL
        self.device = device or config.DEVICE
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.class_names = self.model.names  # {0: 'person', 1: 'bicycle', ...}

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run detection on a single frame.
        Returns list of Detection objects.
        """
        results = self.model(
            frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            device=self.device,
            verbose=False,
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu())
                cls_id = int(box.cls[0].cpu())
                cls_name = self.class_names.get(cls_id, f"class_{cls_id}")

                detections.append(Detection(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    class_name=cls_name,
                    confidence=round(conf, 3),
                    class_id=cls_id,
                ))

        return detections
