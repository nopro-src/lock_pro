from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np


class AntiSpoofBase(ABC):
    """
    Placeholder interface for anti-spoof (liveness).
    Future: IR/depth/blink/challenge-response models.
    """

    @abstractmethod
    def check_liveness(self, bgr_image: np.ndarray) -> tuple[bool, dict]:
        raise NotImplementedError