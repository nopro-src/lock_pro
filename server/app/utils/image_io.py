import base64
import numpy as np
import cv2
from app.core.exceptions import bad_request


def dataurl_to_bgr(data_url: str) -> np.ndarray:
    """
    Accept:
    - raw base64 string
    - data:image/jpeg;base64,...
    """
    if not data_url:
        raise bad_request("Empty image")

    if "," in data_url and data_url.strip().startswith("data:"):
        data_url = data_url.split(",", 1)[1]

    try:
        raw = base64.b64decode(data_url)
    except Exception:
        raise bad_request("Invalid base64 image")

    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise bad_request("Cannot decode image")
    return img