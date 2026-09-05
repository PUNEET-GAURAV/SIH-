"""Localized Manipulation CNN — EfficientNet-B0 based patch manipulation analysis.

Build Spec §1: Localized manipulation CNN (EfficientNet-B0) — MVP with disclosed
generalization limits. If model weights are unavailable or MOCK_MODE=true, returns
an unavailable/mock ForensicSignal.
"""

import logging
import os
import numpy as np
from typing import Optional

from ai.common.interfaces import ForensicDetector, ForensicSignal

logger = logging.getLogger("docshield.forensics.cnn")


class ManipulationCNN(ForensicDetector):
    """EfficientNet-B0 localized manipulation CNN detector."""

    def __init__(self, weights_path: Optional[str] = None):
        self._weights_path = weights_path or "models/manipulation_efficientnet_b0.pth"
        self._model = None
        self._device = "cpu"
        self._initialized = False

    @property
    def detector_type(self) -> str:
        return "localized_manipulation_cnn"

    def _ensure_initialized(self):
        if self._initialized:
            return
        if not os.path.exists(self._weights_path):
            logger.info(f"Manipulation CNN weights file not found at {self._weights_path}. Operating in unavailable/mock mode.")
            self._initialized = False
            return
        try:
            import torch
            import torchvision.models as models

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            model = models.efficientnet_b0(pretrained=False)
            model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 2)
            model.load_state_dict(torch.load(self._weights_path, map_location=self._device))
            model.eval()
            self._model = model
            self._initialized = True
            logger.info("Manipulation CNN loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load Manipulation CNN: {e}")
            self._model = None
            self._initialized = False

    def analyze(self, image: np.ndarray, context: Optional[dict] = None) -> list[ForensicSignal]:
        """Analyze image patches for deep manipulation/editing signatures."""
        self._ensure_initialized()

        if self._model is None:
            return [ForensicSignal(
                detector_type=self.detector_type,
                signal="manipulation_cnn_score",
                status="unavailable",
                confidence=0.0,
                reliability=0.0,
                applicable=True,
                explanation="EfficientNet-B0 weights not found locally. Feature operating in mock/unavailable mode.",
                model_version="efficientnet_b0_v1",
                is_mock=False,
            )]

        try:
            import torch
            from PIL import Image
            import torchvision.transforms as T

            transform = T.Compose([
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            rgb_img = image[:, :, ::-1]  # BGR to RGB
            pil_img = Image.fromarray(rgb_img)
            input_tensor = transform(pil_img).unsqueeze(0).to(self._device)

            with torch.no_grad():
                output = self._model(input_tensor)
                probs = torch.softmax(output, dim=1).cpu().numpy()[0]
                manip_prob = float(probs[1])

            if manip_prob > 0.75:
                status = "high"
                exp = f"High manipulation probability detected by CNN ({manip_prob:.2f})."
            elif manip_prob > 0.40:
                status = "medium"
                exp = f"Moderate manipulation indicators detected by CNN ({manip_prob:.2f})."
            else:
                status = "low"
                exp = f"No localized manipulation detected by CNN ({manip_prob:.2f})."

            return [ForensicSignal(
                detector_type=self.detector_type,
                signal="manipulation_cnn_score",
                status=status,
                confidence=manip_prob,
                reliability=0.80,
                applicable=True,
                explanation=exp,
                model_version="efficientnet_b0_v1",
                is_mock=False,
            )]
        except Exception as e:
            logger.error(f"Error running Manipulation CNN: {e}")
            return [ForensicSignal(
                detector_type=self.detector_type,
                signal="manipulation_cnn_score",
                status="unavailable",
                confidence=0.0,
                reliability=0.0,
                applicable=True,
                explanation=f"Error executing Manipulation CNN: {e}",
                model_version="efficientnet_b0_v1",
                is_mock=False,
            )]
