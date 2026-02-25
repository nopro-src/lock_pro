# Optional: quality filters (blur/brightness/face-size...)
# MVP: chưa dùng. Sau này bạn có thể triển khai:
# - variance of Laplacian để đo blur
# - brightness mean để đo tối
# - face bbox size để reject face quá nhỏ
import numpy as np

def is_blurry(bgr: np.ndarray, thresh: float = 80.0) -> bool:
    # optional: variance of Laplacian
    import cv2
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    v = cv2.Laplacian(gray, cv2.CV_64F).var()
    return v < thresh