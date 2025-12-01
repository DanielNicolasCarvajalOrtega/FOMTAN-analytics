"""
Script para analizar el rendimiento del modelo de detección
y diagnosticar problemas de reconocimiento de objetos
"""
import torch
import cv2
import os
from pathlib import Path
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Nombres de clases
CLASS_NAMES = {
    0: 'Manzana-buen-estado',
    1: 'Manzana-mediano-estado',
    2: 'Manzana-mal-estado',
    3: 'Tomate-buen-estado',
    4: 'Tomate-mediano-estado',
    5: 'Tomate-mal-estado',
    6: 'Cereza-buen-estado',
    7: 'Cereza-mediano-estado',
    8: 'Cereza-mal-estado',
    9: 'Durazno-buen-estado',
    10: 'Durazno-mediano-estado',
    11: 'Durazno-mal-estado',
    12: 'Platano-buen-estado',
    13: 'Platano-mediano-estado',
    14: 'Platano-mal-estado'
}

def load_ground_truth_labels(label_path):
    """Lee las etiquetas reales de un archivo de anotación"""
    labels = []
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:5])
                    labels.append({
                        'class_id': class_id,
                        'class_name': CLASS_NAMES[class_id],
                        'bbox': (x_center, y_center, width, height)
                    })
    return labels

def analyze_model_predictions(model_path='models/best.pt', 
                              image_dir='yolov5/data/images/val',
                              label_dir='yolov5/data/labels/val',
                              num_samples=10,
                              conf_threshold=0.60):
    """
    Analiza las predicciones del modelo vs las etiquetas reales
    """
    print("="*80)
    print("🔍 ANÁLISIS DE RENDIMIENTO DEL MODELO")
    print("="*80)
    
    # Cargar modelo
    print(f"\n1️⃣ Cargando modelo: {model_path}")
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
    model.conf = conf_threshold
    model.iou = 0.45
    print(f"   ✅ Modelo cargado con confianza mínima: {conf_threshold}")
    
    # Obtener lista de imágenes
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    if not image_files:
        print(f"\n❌ No se encontraron imágenes en {image_dir}")
        return
    
    print(f"\n2️⃣ Encontradas {len(image_files)} imágenes en el conjunto de validación")
    
    # Métricas globales
    total_gt_objects = 0  # Ground truth objects
    total_predictions = 0
    class_gt_counts = Counter()
    class_pred_counts = Counter()
    class_correct = Counter()
    
    # Analizar muestras
    samples_to_analyze = min(num_samples, len(image_files))
    print(f"\n3️⃣ Analizando {samples_to_analyze} imágenes de muestra...\n")
    
    for i, img_file in enumerate(image_files[:samples_to_analyze]):
        print(f"\n{'='*80}")
        print(f"📸 Imagen {i+1}/{samples_to_analyze}: {img_file}")
        print(f"{'='*80}")
        
        # Cargar imagen
        img_path = os.path.join(image_dir, img_file)
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"   ⚠️  No se pudo cargar la imagen")
            continue
        
        # Obtener etiquetas reales
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(label_dir, label_file)
        gt_labels = load_ground_truth_labels(label_path)
        
        print(f"\n📋 GROUND TRUTH (Etiquetas Reales):")
        if gt_labels:
            for label in gt_labels:
                print(f"   - {label['class_name']}")
                class_gt_counts[label['class_name']] += 1
                total_gt_objects += 1
        else:
            print(f"   (Sin etiquetas o archivo no encontrado: {label_path})")
        
        # Predicciones del modelo
        results = model(img)
        predictions = results.pandas().xyxy[0]
        
        print(f"\n🤖 PREDICCIONES DEL MODELO:")
        if len(predictions) > 0:
            for _, pred in predictions.iterrows():
                class_name = pred['name']
                confidence = pred['confidence']
                print(f"   - {class_name} ({confidence:.1%} confianza)")
                class_pred_counts[class_name] += 1
                total_predictions += 1
                
                # Verificar si es correcto (simplificado: solo por clase)
                if any(gt['class_name'] == class_name for gt in gt_labels):
                    class_correct[class_name] += 1
        else:
            print(f"   ⚠️  NO SE DETECTÓ NADA")
        
        # Comparar
        gt_classes = set(label['class_name'] for label in gt_labels)
        pred_classes = set(predictions['name'].tolist())
        
        missing = gt_classes - pred_classes
        false_positives = pred_classes - gt_classes
        
        if missing:
            print(f"\n❌ OBJETOS NO DETECTADOS:")
            for cls in missing:
                print(f"   - {cls}")
        
        if false_positives:
            print(f"\n⚠️  FALSOS POSITIVOS:")
            for cls in false_positives:
                print(f"   - {cls}")
        
        if not missing and not false_positives and len(gt_labels) > 0:
            print(f"\n✅ ¡Detección perfecta!")
    
    # Resumen final
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN GENERAL")
    print(f"{'='*80}")
    
    print(f"\n📈 Estadísticas:")
    print(f"   - Total objetos reales (ground truth): {total_gt_objects}")
    print(f"   - Total predicciones del modelo: {total_predictions}")
    
    print(f"\n🎯 Distribución por Clase (Ground Truth):")
    for class_name, count in sorted(class_gt_counts.items(), key=lambda x: x[1], reverse=True):
        pred_count = class_pred_counts.get(class_name, 0)
        correct = class_correct.get(class_name, 0)
        recall = (correct / count * 100) if count > 0 else 0
        print(f"   {class_name:30s} | GT: {count:3d} | Detectado: {pred_count:3d} | Recall: {recall:5.1f}%")
    
    print(f"\n🔍 Clases que el modelo predice incorrectamente:")
    for class_name, count in sorted(class_pred_counts.items(), key=lambda x: x[1], reverse=True):
        gt_count = class_gt_counts.get(class_name, 0)
        if gt_count == 0 and count > 0:
            print(f"   ⚠️  {class_name}: {count} predicciones (pero NO existe en ground truth)")
    
    print(f"\n{'='*80}")
    
    return {
        'total_gt': total_gt_objects,
        'total_pred': total_predictions,
        'class_gt_counts': class_gt_counts,
        'class_pred_counts': class_pred_counts,
        'class_correct': class_correct
    }

if __name__ == "__main__":
    # Ejecutar análisis
    results = analyze_model_predictions(
        model_path='models/best.pt',
        image_dir='yolov5/data/images/val',
        label_dir='yolov5/data/labels/val',
        num_samples=15,  # Analizar hasta 15 imágenes
        conf_threshold=0.60
    )
    
    print("\n✅ Análisis completado")
