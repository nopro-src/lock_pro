import numpy as np

def emb_to_bytes(emb: np.ndarray) -> bytes:
    return emb.astype(np.float32).tobytes()

def bytes_to_emb(b: bytes, dim: int) -> np.ndarray:
    arr = np.frombuffer(b, dtype=np.float32)
    return arr.reshape((dim,))