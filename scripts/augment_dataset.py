"""
Script de Data Augmentation para FOMTAN Analytics
Multiplica el dataset existente usando transformaciones
"""
import cv2
import os
import numpy as np
from pathlib import Path
import shutil
from tqdm import tqdm
import albumentations as A

# Configuración
TRAIN_IMAGES = 'yolov5/data/images/train'
TRAIN_LABELS = 'yolov5/data/labels/train'
AUGMENTATION_FACTOR = 5  # Cuántas versiones augmentadas crear por imagen

# Definir transformaciones de augmentation
transform = A.Compose([
    A.OneOf([
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.Rotate(limit=30, p=0.7),
    ], p=1.0),
    
    A.OneOf([
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.8),
        A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.8),
        A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=0.5),
    ], p=1.0),
    
    A.OneOf([
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
        A.GaussianBlur(blur_limit=(3, 7), p=0.5),
        A.MotionBlur(blur_limit=7, p=0.3),
    ], p=0.5),
    
    A.RandomShadow(p=0.3),
    A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, alpha_coef=0.08, p=0.2),
    
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def load_yolo_annotations(label_path):
    """Carga anotaciones en formato YOLO"""
    bboxes = []
    class_labels = []
    
    if not os.path.exists(label_path):
        return bboxes, class_labels
    
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:5])
                bboxes.append([x_center, y_center, width, height])
                class_labels.append(class_id)
    
    return bboxes, class_labels

def save_yolo_annotations(label_path, bboxes, class_labels):
    """Guarda anotaciones en formato YOLO"""
    with open(label_path, 'w') as f:
        for bbox, class_id in zip(bboxes, class_labels):
            x_center, y_center, width, height = bbox
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def augment_dataset(train_images_dir, train_labels_dir, augmentation_factor=5):
    """
    Aumenta el dataset aplicando transformaciones a las imágenes y ajustando las anotaciones
    """
    print("="*80)
    print("🔧 DATA AUGMENTATION - FOMTAN Analytics")
    print("="*80)
    
    # Obtener lista de imágenes
    image_files = [f for f in os.listdir(train_images_dir) 
                   if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    print(f"\n📊 Dataset Original:")
    print(f"   - Imágenes de entrenamiento: {len(image_files)}")
    print(f"   - Factor de augmentation: {augmentation_factor}x")
    print(f"   - Total imágenes después: {len(image_files) * (augmentation_factor + 1)}")
    
    print(f"\n🚀 Iniciando proceso de augmentation...\n")
    
    augmented_count = 0
    failed_count = 0
    
    for img_file in tqdm(image_files, desc="Procesando imágenes"):
        # Rutas originales
        img_path = os.path.join(train_images_dir, img_file)
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(train_labels_dir, label_file)
        
        # Cargar imagen
        image = cv2.imread(img_path)
        if image is None:
            failed_count += 1
            continue
        
        # Convertir BGR to RGB para albumentations
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Cargar anotaciones
        bboxes, class_labels = load_yolo_annotations(label_path)
        
        # Si no hay anotaciones, solo augmentar la imagen
        if len(bboxes) == 0:
            print(f"\n⚠️  {img_file}: Sin anotaciones, saltando...")
            continue
        
        # Generar versiones augmentadas
        for i in range(augmentation_factor):
            try:
                # Aplicar transformación
                transformed = transform(image=image_rgb, bboxes=bboxes, class_labels=class_labels)
                
                aug_image = transformed['image']
                aug_bboxes = transformed['bboxes']
                aug_labels = transformed['class_labels']
                
                # Si la transformación eliminó todos los bboxes, saltar
                if len(aug_bboxes) == 0:
                    continue
                
                # Convertir RGB de vuelta a BGR para guardar
                aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
                
                # Crear nombres para archivos augmentados
                base_name = os.path.splitext(img_file)[0]
                ext = os.path.splitext(img_file)[1]
                aug_img_name = f"{base_name}_aug{i+1}{ext}"
                aug_label_name = f"{base_name}_aug{i+1}.txt"
                
                # Guardar imagen augmentada
                aug_img_path = os.path.join(train_images_dir, aug_img_name)
                cv2.imwrite(aug_img_path, aug_image_bgr)
                
                # Guardar anotaciones augmentadas
                aug_label_path = os.path.join(train_labels_dir, aug_label_name)
                save_yolo_annotations(aug_label_path, aug_bboxes, aug_labels)
                
                augmented_count += 1
                
            except Exception as e:
                print(f"\n❌ Error procesando {img_file} (versión {i+1}): {e}")
                failed_count += 1
    
    print(f"\n{'='*80}")
    print("✅ AUGMENTATION COMPLETADO")
    print(f"{'='*80}")
    print(f"   - Imágenes originales: {len(image_files)}")
    print(f"   - Imágenes augmentadas creadas: {augmented_count}")
    print(f"   - Errores: {failed_count}")
    print(f"   - Total final: {len(image_files) + augmented_count}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    # Verificar que albumentations está instalado
    try:
        import albumentations
        print("✅ Albumentations instalado correctamente\n")
    except ImportError:
        print("❌ ERROR: Albumentations no está instalado")
        print("Instalar con: pip install albumentations")
        exit(1)
    
    # Ejecutar augmentation
    augment_dataset(TRAIN_IMAGES, TRAIN_LABELS, AUGMENTATION_FACTOR)
    
    print("🎉 ¡Proceso completado! Ahora tienes 5-6x más datos de entrenamiento")
    print("📝 Próximo paso: Re-entrenar el modelo con el dataset aumentado")
