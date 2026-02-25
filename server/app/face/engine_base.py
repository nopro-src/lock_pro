from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np


class FaceEngineBase(ABC):
    """
    Production contract for face recognition engines.
    - input: BGR np.ndarray (H,W,3) uint8
    - output embedding: np.ndarray float32 (dim,)
    """

    @property
    @abstractmethod
    def model_key(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def extract_embedding(self, bgr_image: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Returns:
          embedding (float32, normalized NOT guaranteed)
          meta: may include face bbox, pose, detection score ...
        """
        raise NotImplementedError