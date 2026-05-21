"""
Scene Understanding Module
Generates natural language descriptions of visual scenes using BLIP.
"""
import time
from typing import Optional
import numpy as np
from PIL import Image
import config


class SceneUnderstanding:
    """Generates scene captions using BLIP vision-language model."""

    def __init__(self):
        self._model = None
        self._processor = None
        self._last_caption_time = 0.0
        self._last_caption = "Initializing scene understanding..."
        self._device = config.DEVICE

    def _load_model(self):
        """Lazy-load the BLIP model on first use."""
        if self._model is not None:
            return

        from transformers import BlipProcessor, BlipForConditionalGeneration
        import torch

        print("[SceneUnderstanding] Loading BLIP model...")
        self._processor = BlipProcessor.from_pretrained(config.SCENE_MODEL)
        self._model = BlipForConditionalGeneration.from_pretrained(config.SCENE_MODEL)
        self._model.to(self._device)
        self._model.eval()
        print("[SceneUnderstanding] BLIP model loaded.")

    def describe(self, frame: np.ndarray, force: bool = False) -> str:
        """
        Generate a natural language description of the scene.
        Only runs at SCENE_CAPTION_INTERVAL to save compute.
        Returns the latest caption.
        """
        now = time.time()
        if not force and (now - self._last_caption_time) < config.SCENE_CAPTION_INTERVAL:
            return self._last_caption

        try:
            self._load_model()

            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_frame = frame[:, :, ::-1]
            image = Image.fromarray(rgb_frame)

            # Resize for efficiency
            image = image.resize((384, 384))

            inputs = self._processor(image, return_tensors="pt").to(self._device)

            import torch
            with torch.no_grad():
                out = self._model.generate(
                    **inputs,
                    max_new_tokens=50,
                    num_beams=3,
                )

            caption = self._processor.decode(out[0], skip_special_tokens=True)
            self._last_caption = caption.strip()
            self._last_caption_time = now

        except Exception as e:
            self._last_caption = f"Scene analysis unavailable: {str(e)[:50]}"

        return self._last_caption

    def get_last_caption(self) -> str:
        """Return the most recent caption without recomputing."""
        return self._last_caption
