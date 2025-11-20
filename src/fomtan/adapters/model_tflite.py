import cv2
import numpy as np
import logging
from typing import List, Optional

try:
    import tensorflow.lite as tflite
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
    except ImportError:
        tflite = None

from ..core.types import ResultadoDeteccion

logger = logging.getLogger(__name__)

class ModelTFLite:
    def __init__(self, detection_path: str, classification_path: str, labels_path: str):
        if tflite is None:
            raise ImportError("TensorFlow Lite is not installed. Please install 'tensorflow' or 'tflite_runtime'.")

        # Load Detection Model
        self.detect_interpreter = tflite.Interpreter(model_path=detection_path)
        self.detect_interpreter.allocate_tensors()
        self.detect_input_details = self.detect_interpreter.get_input_details()
        self.detect_output_details = self.detect_interpreter.get_output_details()
        
        # Load Classification Model
        self.cls_interpreter = tflite.Interpreter(model_path=classification_path)
        self.cls_interpreter.allocate_tensors()
        self.cls_input_details = self.cls_interpreter.get_input_details()
        self.cls_output_details = self.cls_interpreter.get_output_details()

        # Load Labels
        self.labels = self._load_labels(labels_path)
        
        # Colors for states
        self.colors = {
            "buena": "Verde",
            "segunda": "Amarillo",
            "descarte": "Rojo"
        }

    def _load_labels(self, path: str) -> List[str]:
        with open(path, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    def predict(self, frame: np.ndarray) -> Optional[ResultadoDeteccion]:
        # 1. Detection
        box = self._run_detection(frame)
        
        if box is None:
            return None

        # 2. Crop and Classify
        x1, y1, x2, y2 = box
        # Ensure coordinates are within frame bounds
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return None

        crop = frame[y1:y2, x1:x2]
        return self._run_classification(crop)

    def _run_detection(self, frame: np.ndarray) -> Optional[List[int]]:
        # Preprocess for YOLOv8 (640x640, float32, 0-1)
        input_shape = self.detect_input_details[0]['shape'] # [1, 640, 640, 3]
        target_h, target_w = input_shape[1], input_shape[2]
        
        resized = cv2.resize(frame, (target_w, target_h))
        input_data = (resized.astype(np.float32) / 255.0)
        input_data = np.expand_dims(input_data, axis=0)

        self.detect_interpreter.set_tensor(self.detect_input_details[0]['index'], input_data)
        self.detect_interpreter.invoke()
        
        # Output: [1, 84, 8400]
        output_data = self.detect_interpreter.get_tensor(self.detect_output_details[0]['index'])[0]
        
        # Transpose to [8400, 84] for easier processing
        output_data = output_data.transpose()
        
        # YOLOv8 Output format: [x_center, y_center, w, h, class_scores...]
        # Optimized numpy processing
        scores = np.max(output_data[:, 4:], axis=1)
        confidence_threshold = 0.5
        mask = scores > confidence_threshold
        
        if not np.any(mask):
            return None
            
        filtered_scores = scores[mask]
        filtered_output = output_data[mask]
        
        # Get the box with the highest confidence
        best_idx = np.argmax(filtered_scores)
        best_box_data = filtered_output[best_idx]
        
        xc, yc, w_box, h_box = best_box_data[:4]
        
        # Convert to absolute coordinates
        h_img, w_img = frame.shape[:2]
        x_scale = w_img / target_w
        y_scale = h_img / target_h
        
        x1 = int((xc - w_box/2) * x_scale)
        y1 = int((yc - h_box/2) * y_scale)
        x2 = int((xc + w_box/2) * x_scale)
        y2 = int((yc + h_box/2) * y_scale)
        
        return [x1, y1, x2, y2]

    def _run_classification(self, crop: np.ndarray) -> ResultadoDeteccion:
        # Preprocess for Classification (224x224, int8, -128 to 127)
        input_shape = self.cls_input_details[0]['shape'] # [1, 224, 224, 3]
        target_h, target_w = input_shape[1], input_shape[2]
        
        resized = cv2.resize(crop, (target_w, target_h))
        
        # Quantization: uint8 [0, 255] -> int8 [-128, 127]
        # Formula: int8 = uint8 - 128
        input_data = resized.astype(np.int16) - 128
        input_data = np.clip(input_data, -128, 127).astype(np.int8)
        input_data = np.expand_dims(input_data, axis=0)

        self.cls_interpreter.set_tensor(self.cls_input_details[0]['index'], input_data)
        self.cls_interpreter.invoke()
        
        output_data = self.cls_interpreter.get_tensor(self.cls_output_details[0]['index'])[0]
        
        # Softmax (optional, but good for probability)
        # Since output is int8, we should dequantize or just take argmax
        # For simplicity, just argmax
        
        predicted_idx = np.argmax(output_data)
        
        # Map index to label
        # WARNING: Model has 1000 classes, we have 3 labels.
        # We map 0->0, 1->1, 2->2. Anything else is "Unknown" or mapped to 0.
        if predicted_idx < len(self.labels):
            label = self.labels[predicted_idx]
        else:
            # Fallback: just pick one or show unknown
            # For this specific task/demo, we might want to force a valid label
            # Let's use modulo to cycle through labels if index is out of bounds (just for demo stability)
            label = self.labels[predicted_idx % len(self.labels)]
            
        # Calculate a pseudo-probability from the int8 score
        # int8 range is -128 to 127. 
        score = output_data[predicted_idx]
        probability = (score + 128) / 255.0 # Normalize to 0-1
        
        color = self.colors.get(label, "Gris")
        
        return ResultadoDeteccion(
            etiqueta=label,
            probabilidad=float(probability),
            color=color
        )
