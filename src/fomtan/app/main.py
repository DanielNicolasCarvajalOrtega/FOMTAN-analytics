import cv2
import torch
import numpy as np
import sys
import os
import time
from pathlib import Path

# Configuración robusta del path para importaciones
FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.fomtan.adapters.audio_tts import VoiceAssistant
from src.fomtan.analytics.harvest_stats import HarvestAnalytics
from src.fomtan.ui.dashboard import HarvestDashboard

# Cargar modelo
print("Cargando modelo...")
model = torch.hub.load('ultralytics/yolov5', 'custom', 
                      path='/Users/macbook/Desktop/Python/FOMTAN-analytics/models/best.pt',
                      force_reload=False)

# Inicializar Sistemas
print("Inicializando sistemas...")
voice_assistant = VoiceAssistant()
analytics = HarvestAnalytics()
dashboard = HarvestDashboard(update_interval=10.0)

# CONFIGURACIÓN DE ALTA PRECISIÓN
model.conf = 0.60
model.iou = 0.45
model.max_det = 5
model.amp = True

# Abrir cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1220)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("\n=== DETECTOR + ANALYTICS INICIADO ===")
print("Presiona ESC para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_time = time.time()
    
    # Detectar objetos
    results = model(frame, size=640)
    detections = results.pandas().xyxy[0]
    
    # 1. PROCESAR AUDIO
    voice_assistant.process_detections(detections)
    
    # 2. PROCESAR ANALÍTICA
    analytics.add_sample(detections, current_time)
    
    # 3. ACTUALIZAR UI (Dashboard)
    if dashboard.should_update():
        dashboard.update(analytics)
    
    # Renderizado de Video (OpenCV)
    annotated_frame = frame.copy()
    valid_detections = 0
    
    for idx, row in detections.iterrows():
        confidence = row['confidence']
        name = row['name']
        
        if confidence < model.conf:
            continue

        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        
        # Visualización
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        label = f"{name} {confidence:.0%}"
        cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        valid_detections += 1
    
    # Info en pantalla
    cv2.imshow('Detector FOMTAN', annotated_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
dashboard.close()
print("\nSistema cerrado")