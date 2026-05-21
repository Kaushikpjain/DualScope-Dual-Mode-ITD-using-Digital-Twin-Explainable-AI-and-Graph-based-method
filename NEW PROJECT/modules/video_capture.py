"""
Video Capture Module
Wraps OpenCV VideoCapture for webcam, file, or RTSP streams.
"""
import cv2
import config


class VideoCapture:
    """Manages video input from webcam, file, or RTSP stream."""

    def __init__(self, source=None):
        self.source = source if source is not None else config.VIDEO_SOURCE
        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")

        # Try to set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    def read_frame(self):
        """Read a single frame. Returns (success, frame)."""
        ret, frame = self.cap.read()
        return ret, frame

    def get_fps(self):
        """Return the FPS of the video source."""
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return fps if fps > 0 else 30.0

    def get_resolution(self):
        """Return (width, height) of the video source."""
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return w, h

    def release(self):
        """Release the video source."""
        if self.cap.isOpened():
            self.cap.release()

    def __del__(self):
        self.release()
