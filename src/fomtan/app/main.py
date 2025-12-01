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
from src.fomtan.core.detection_filter import TemporalDetectionFilter

# WHITELIST: Todas las 15 clases válidas del modelo entrenado
VALID_CLASSES = {
    'Manzana-buen-estado', 'Manzana-mediano-estado', 'Manzana-mal-estado',
    'Tomate-buen-estado', 'Tomate-mediano-estado', 'Tomate-mal-estado',
    'Cereza-buen-estado', 'Cereza-mediano-estado', 'Cereza-mal-estado',
    'Durazno-buen-estado', 'Durazno-mediano-estado', 'Durazno-mal-estado',
    'Platano-buen-estado', 'Platano-mediano-estado', 'Platano-mal-estado'
}

# Cargar modelo
print("Cargando modelo...")
model = torch.hub.load('ultralytics/yolov5', 'custom', 
                      path='/Users/macbook/Desktop/Python/FOMTAN-analytics/models/best.pt',
                      force_reload=False)

# Inicializar Sistemas
print("Inicializando sistemas...")
voice_assistant = VoiceAssistant()
analytics = HarvestAnalytics()
dashboard = HarvestDashboard(update_interval=60.0, width=800, height=600)
temporal_filter = TemporalDetectionFilter(required_frames=2, timeout=1.5)

# CONFIGURACIÓN TEMPORAL (Dataset insuficiente - re-entrenamiento pendiente)
# Threshold reducido para compensar modelo sub-entrenado
# TODO: Volver a 0.60 después de re-entrenar con dataset aumentado
model.conf = 0.25  # TEMPORAL: Reducido para ver más detecciones
model.iou = 0.45   # Umbral de intersección sobre unión
model.max_det = 30 # Cantidad óptima para escenarios agrícolas
model.amp = True   # Automatic Mixed Precision para mejor rendimiento

# Abrir cámara
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Obtener dimensiones reales
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

print("\n" + "="*80)
print("🚀 SISTEMA FOMTAN INICIADO - Interfaz Unificada")
print("="*80)
print(f"📹 Cámara: {frame_width}x{frame_height}")
print(f"🍎 Modelo: 15 clases (Manzana, Tomate, Cereza, Durazno, Plátano)")
print(f"📊 Dashboard: Actualización cada 60 segundos")
print(f"🎤 Voz Neural: Cooldown 10s | Confianza mín. 75%")
print(f"🔧 Detección: Confianza mín. {model.conf*100:.0f}% | Max objetos {model.max_det}")
print(f"⏱️  Filtro Temporal: 2 frames consistentes en 1.5s")
print("\n⌨️  Controles:")
print("   ESC - Salir del sistema")
print("   F - Alternar pantalla completa")
print("="*80 + "\n")

# Variable para pantalla completa
fullscreen = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_time = time.time()
    
    # Detectar objetos (YOLOv5 AutoShape maneja BGR automáticamente)
    results = model(frame, size=640)
    raw_detections = results.pandas().xyxy[0]
    
    # PASO 1: Filtro de Whitelist - Solo clases válidas del modelo
    whitelist_detections = raw_detections[raw_detections['name'].isin(VALID_CLASSES)]
    
    # PASO 2: Filtro Temporal - Añadir al historial
    temporal_filter.add_detections(whitelist_detections)
    
    # PASO 3: Validar detecciones consistentes (aparecer en múltiples frames)
    detections = temporal_filter.get_validated_detections(whitelist_detections)
    
    # DEBUG: Mostrar estadísticas de detección
    if not detections.empty:
        avg_conf = detections['confidence'].mean()
        print(f"✅ Validadas: {len(detections)} detecciones | Confianza promedio: {avg_conf:.0%}")
    elif not whitelist_detections.empty:
        print(f"⏳ Pendientes: {len(whitelist_detections)} detectadas, esperando validación temporal...")
    
    # PROCESAR AUDIO
    voice_assistant.process_detections(detections)
    
    # PROCESAR ANALÍTICA
    analytics.add_sample(detections, current_time)
    
    # ACTUALIZAR DASHBOARD (si corresponde)
    if dashboard.should_update():
        dashboard.update(analytics)
    
    # RENDERIZAR VIDEO CON DETECCIONES
    annotated_frame = frame.copy()
    
    for idx, row in detections.iterrows():
        confidence = row['confidence']
        name = row['name']

        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        
        # Bounding box verde
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Label con fondo
        label = f"{name} {confidence:.0%}"
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(annotated_frame, (x1, y1 - label_height - 10), 
                     (x1 + label_width, y1), (0, 255, 0), -1)
        cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # 5. OBTENER IMAGEN DEL DASHBOARD
    dashboard_img = dashboard.get_image()
    
    # 6. REDIMENSIONAR DASHBOARD PARA QUE TENGA LA MISMA ALTURA QUE EL VIDEO
    dashboard_resized = cv2.resize(dashboard_img, (800, frame_height))
    
    # 7. COMBINAR AMBAS IMÁGENES HORIZONTALMENTE
    # [Video | Dashboard]
    combined = np.hstack([annotated_frame, dashboard_resized])
    
    # 8. AÑADIR TÍTULO EN LA PARTE SUPERIOR
    cv2.putText(combined, "FOMTAN Analytics - Sistema Integrado", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    cv2.putText(combined, "FOMTAN Analytics - Sistema Integrado", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    
    # 9. MOSTRAR VENTANA ÚNICA
    cv2.imshow('FOMTAN Analytics', combined)
    
    # 10. CONTROLES
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('f') or key == ord('F'):  # F para fullscreen
        fullscreen = not fullscreen
        if fullscreen:
            cv2.setWindowProperty('FOMTAN Analytics', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('FOMTAN Analytics', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

cap.release()
cv2.destroyAllWindows()
dashboard.close()
print("\n✅ Sistema cerrado correctamente")