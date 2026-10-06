from pathlib import Path
import cv2
import numpy as np

def load_image_from_disk(image_path: str) -> np.ndarray:
    """
    Loads an image safely from a file path (Handles Windows path issues).
    """
    path_obj = Path(image_path).resolve()
    
    if not path_obj.is_file():
        raise FileNotFoundError(f"File not found: {path_obj}")
    
    image = cv2.imread(str(path_obj))
    
    # Fallback reading method for Windows path issues
    if image is None:
        image = cv2.imdecode(np.fromfile(str(path_obj), dtype=np.uint8), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Corrupt or unreadable image file: {path_obj}")
        
    return image

def read_uploaded_file(file_bytes: bytes) -> np.ndarray:
    """
    Converts uploaded byte stream into OpenCV image format.
    """
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image