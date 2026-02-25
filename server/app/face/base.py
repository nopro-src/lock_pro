from abc import ABC, abstractmethod
import numpy as np


class FaceEngineBase(ABC):
    @property
    @abstractmethod
    def model_key(self) -> str:
        ...

    @property
    @abstractmethod
    def dim(self) -> int:
        ...

    @abstractmethod
    def embed(self, bgr_image: np.ndarray) -> np.ndarray:
        """
        Return normalized embedding (float32, shape=(dim,))
        Must handle detect+align internally or raise a clear error if no face.
        """
        ...