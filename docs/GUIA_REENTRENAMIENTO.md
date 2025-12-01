# Guía para Reentrenar el Modelo YOLOv5 - FOMTAN Analytics

## 🎯 Objetivo
Crear un modelo que detecte **correctamente** Manzanas, Tomates y Cerezas (en 3 estados cada una) sin confundir objetos del fondo.

---

## 📋 Requisitos del Dataset

### 1. **Cantidad Mínima de Imágenes**
- **Mínimo por clase**: 100-150 imágenes
- **Recomendado**: 300-500 imágenes por clase
- **Total**: ~900-4500 imágenes (para 9 clases)

### 2. **Calidad de las Imágenes**

#### ✅ BUENAS PRÁCTICAS:
- **Fondos variados**: blanco, negro, madera, metal, tierra, hojas
- **Iluminación variada**: luz natural, artificial, sombras
- **Ángulos diversos**: frontal, lateral, desde arriba
- **Escalas diferentes**: objetos cerca, lejos, tamaños variados
- **Múltiples objetos**: 1-5 frutas por imagen
- **Contextos reales**: en plantas, manos, cestas

#### ❌ EVITAR:
- ❌ Siempre el mismo fondo (el modelo aprende el fondo, no la fruta)
- ❌ Solo una fruta por imagen
- ❌ Imágenes de Google (derechos de autor + no representan tu caso real)
- ❌ Fondos con patrones que no existen en agricultura (marcos decorativos, cuadros)

### 3. **Estados de las Frutas**

- **Buen estado**: Firmes, color uniforme, sin manchas
- **Mediano estado**: Pequeñas manchas, ligera decoloración
- **Mal estado**: Magulladuras, muy manchadas, podridas

---

## 🛠️ Herramientas de Anotación

### Recomendadas (Gratis):
1. **Roboflow** (https://roboflow.com) - La más fácil
   - Anota en el navegador
   - Exporta directo a formato YOLOv5
   - Aumentación de datos automática
   
2. **LabelImg** (Desktop)
   ```bash
   pip install labelImg
   labelImg
   ```

3. **CVAT** (https://cvat.ai) - Profesional, gratuito

---

## 📁 Estructura del Dataset

```
dataset_fomtan/
├── images/
│   ├── train/          (70-80% de imágenes)
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── val/            (20-30% de imágenes)
│       ├── img101.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── img001.txt  (Formato YOLO)
│   │   ├── img002.txt
│   │   └── ...
│   └── val/
│       ├── img101.txt
│       └── ...
└── data.yaml
```

### Formato de `data.yaml`:
```yaml
train: /ruta/absoluta/dataset_fomtan/images/train
val: /ruta/absoluta/dataset_fomtan/images/val

nc: 9

names:
  - Manzana-buen-estado
  - Manzana-mediano-estado
  - Manzana-mal-estado
  - Tomate-buen-estado
  - Tomate-mediano-estado
  - Tomate-mal-estado
  - Cereza-buen-estado
  - Cereza-mediano-estado
  - Cereza-mal-estado
```

### Formato de archivos `.txt` (YOLO):
```
# Cada línea: clase x_centro y_centro ancho alto (normalizados 0-1)
0 0.516 0.438 0.312 0.425
2 0.723 0.621 0.198 0.287
```

---

## 🚀 Comando de Entrenamiento

```bash
# Instalar YOLOv5
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt

# Entrenar (desde el directorio yolov5/)
python train.py \
  --img 640 \
  --batch 16 \
  --epochs 100 \
  --data /ruta/absoluta/dataset_fomtan/data.yaml \
  --weights yolov5s.pt \
  --name fomtan_v2 \
  --patience 20

# El modelo entrenado estará en: runs/train/fomtan_v2/weights/best.pt
```

### Parámetros Explicados:
- `--img 640`: Tamaño de entrada
- `--batch 16`: Imágenes por lote (reducir si hay error de memoria)
- `--epochs 100`: Iteraciones máximas
- `--weights yolov5s.pt`: Partir de modelo pre-entrenado
- `--patience 20`: Parar si no mejora en 20 épocas

---

## 📊 Validación del Modelo

Después de entrenar, **CRUCIAL** validar:

```bash
# Probar en imágenes nuevas (nunca vistas)
python detect.py \
  --weights runs/train/fomtan_v2/weights/best.pt \
  --source /ruta/a/imagenes_prueba/ \
  --conf 0.60

# Ver resultados en: runs/detect/exp/
```

### Checks de Calidad:
1. **Precision**: ¿Detecta solo frutas reales?
2. **Recall**: ¿Detecta TODAS las frutas en la imagen?
3. **No confusión**: ¿No detecta personas, paredes, marcos?

---

## 🔄 Integrar Nuevo Modelo

Una vez tengas `best.pt` nuevo:

```bash
# Reemplazar modelo viejo
cp runs/train/fomtan_v2/weights/best.pt \
   /Users/macbook/Desktop/Python/FOMTAN-analytics/models/best.pt

# Probar
python src/fomtan/app/main.py
```

---

## 💡 Tips Adicionales

### Aumentación de Datos (si usas Roboflow):
- Rotación: ±15°
- Flip horizontal: Sí
- Brillo: ±20%
- Ruido: Leve
- Blur: Leve

### Si tienes POCAS imágenes:
1. Toma fotos con tu teléfono en diferentes momentos del día
2. Usa técnicas de augmentation en Roboflow
3. Captura video y extrae frames cada 10 frames

### Verificar Balance de Clases:
Cada clase debe tener cantidad similar de imágenes. Si "Cereza-mal-estado" tiene 50 y "Manzana-buen-estado" tiene 500, el modelo será sesgado.

---

## 🆘 Recursos Útiles

- **YOLOv5 Docs**: https://docs.ultralytics.com
- **Roboflow Tutorial**: https://blog.roboflow.com/getting-started-with-roboflow/
- **Dataset Público (inspiración)**: https://public.roboflow.com/object-detection

---

## ✅ Checklist Final

Antes de entrenar:
- [ ] Tengo 100+ imágenes por clase
- [ ] Fondos son variados (no repetitivos)
- [ ] Incluí ejemplos con 1-5 objetos por imagen
- [ ] Las anotaciones están correctas (revisé al menos 50)
- [ ] Dividí en 80% train / 20% val
- [ ] `data.yaml` tiene rutas absolutas correctas

¡Buena suerte con el entrenamiento! 🚀
