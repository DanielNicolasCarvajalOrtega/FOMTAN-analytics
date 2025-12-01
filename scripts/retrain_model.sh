#!/bin/bash
# Script de Re-entrenamiento del Modelo YOLOv5
# Configurado para superar el problema de dataset pequeño y desbalanceado

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🚀 RE-ENTRENAMIENTO YOLOV5 - FOMTAN Analytics v2.0"
echo "════════════════════════════════════════════════════════════════════════════════"

# Activar entorno virtual
source .venv/bin/activate

# Verificar que el dataset augmentado existe
TRAIN_IMAGES="yolov5/data/images/train"
NUM_IMAGES=$(ls -1 $TRAIN_IMAGES | wc -l)
echo ""
echo "📊 Dataset actual: $NUM_IMAGES imágenes de entrenamiento"

if [ $NUM_IMAGES -lt 200 ]; then
    echo "⚠️  ADVERTENCIA: Dataset pequeño ($NUM_IMAGES imágenes)"
    echo "    Recomendado: 300+ imágenes"
    echo ""
    read -p "¿Continuar de todos modos? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🔧 Configuración de Entrenamiento:"
echo "   • Modelo base: yolov5s.pt (pre-entrenado)"
echo "   • Imagen size: 640px (óptimo)"
echo "   • Batch size: 16"
echo "   • Épocas: 100 (con early stopping)"
echo "   • Paciencia: 20 épocas sin mejora"
echo "   • Optimizador: SGD (momentum 0.937)"
echo ""

# Crear backup del modelo actual
echo "💾 Creando backup del modelo actual..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp models/best.pt models/best_backup_$TIMESTAMP.pt
echo "   ✅ Backup guardado: models/best_backup_$TIMESTAMP.pt"
echo ""

# Iniciar entrenamiento
echo "🏋️  Iniciando entrenamiento..."
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

python yolov5/yolov5/train.py \
  --img 640 \
  --batch 16 \
  --epochs 100 \
  --data models/custom-coco128.yaml \
  --weights yolov5n.pt \
  --cache \
  --patience 20 \
  --project models/runs \
  --name fomtan_v2_retrain_nano \
  --exist-ok \
  --save-period 10 \
  --hyp yolov5/yolov5/data/hyps/hyp.scratch-low.yaml

# Verificar si el entrenamiento fue exitoso
if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "✅ ENTRENAMIENTO COMPLETADO"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Copiar el mejor modelo
    BEST_MODEL="models/runs/fomtan_v2_retrain_nano/weights/best.pt"
    if [ -f "$BEST_MODEL" ]; then
        echo "📦 Copiando modelo entrenado a models/best.pt"
        cp $BEST_MODEL models/best.pt
        echo "   ✅ Modelo actualizado"
        echo ""
        echo "📊 Resultados disponibles en:"
        echo "   - models/runs/fomtan_v2_retrain_nano/results.png"
        echo "   - models/runs/fomtan_v2_retrain_nano/confusion_matrix.png"
        echo ""
        echo "🎯 Próximos pasos:"
        echo "   1. Revisar métricas en results.png"
        echo "   2. Si mAP > 0.70, actualizar main.py: model.conf = 0.60"
        echo "   3. Probar detección en tiempo real: python src/fomtan/app/main.py"
        echo ""
    else
        echo "⚠️  No se encontró el modelo entrenado en $BEST_MODEL"
    fi
else
    echo ""
    echo "❌ ERROR: El entrenamiento falló"
    echo "   Revisar logs arriba para identificar el problema"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════════════════════"
