from dataclasses import dataclass
from typing import Any, Tuple
import numpy as np

# Alias para un fotograma de video (típicamente un array numpy de OpenCV)
Fotograma = np.ndarray
Frame = np.ndarray

@dataclass
class ResultadoDeteccion:
    """
    Representa el resultado de un modelo de detección/clasificación.
    """
    etiqueta: str
    probabilidad: float
    color: str  # 'verde', 'amarillo', 'rojo'

# Alias to keep backward compatibility with existing imports
DetectionResult = ResultadoDeteccion
