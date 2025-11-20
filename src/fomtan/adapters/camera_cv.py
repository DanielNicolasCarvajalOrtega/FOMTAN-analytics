import cv2
from typing import Optional
from ..core.types import Frame


class CameraCV:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Inicia la camara del sistema """
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera with index {self.camera_index}")
        
        # Reducir resolución para mejor rendimiento
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def read_frame(self) -> Optional[Frame]:
        """Lee un cuadro (frame) de la cámara. Retorna None si falla la lectura."""
        if self.cap is None or not self.cap.isOpened():
            print("error al iniciar la camara")
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def close(self) -> None:
        """Libera el recurso de la cámara."""
        if self.cap:
            self.cap.release()
            self.cap = None
