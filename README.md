# FOMTAN Analytics

Sistema de análisis y clasificación de frutas en tiempo real usando TensorFlow Lite.

## Inicio Rápido

### Opción 1: Usando el script de inicio (Recomendado)
```bash
./start.sh
```

### Opción 2: Usando el entorno virtual directamente
```bash
source .venv/bin/activate
python run.py
```

### Opción 3: Sin activar el entorno virtual
```bash
.venv/bin/python run.py
```

## Requisitos

- Python 3.8+
- Cámara conectada
- Dependencias instaladas (ver `requirements.txt`)

## Instalación de Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar TensorFlow
pip install tensorflow
```

## Estructura del Proyecto

```
FOMTAN-analytics/
├── models/tflite/          # Modelos TensorFlow Lite
│   ├── detect_fruit.tflite # Modelo de detección
│   ├── cls_estado.tflite   # Modelo de clasificación
│   └── labels.txt          # Etiquetas (buena, segunda, descarte)
├── src/fomtan/
│   ├── adapters/           # Adaptadores (cámara, modelos, UI)
│   ├── app/                # Aplicación principal
│   └── core/               # Tipos y utilidades
├── run.py                  # Script de entrada
└── start.sh                # Script de inicio (recomendado)
```

## Uso

1. Ejecuta el programa con `./start.sh`
2. La aplicación abrirá la cámara y comenzará a detectar frutas
3. Los resultados se mostrarán en pantalla:
   - **Verde**: Pieza buena (primera calidad)
   - **Amarillo**: Pieza segunda
   - **Rojo**: Pieza de descarte
4. Presiona 'q' para salir

## Solución de Problemas

### Error: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Error: "TensorFlow Lite is not installed"
```bash
pip install tensorflow
```

### Error: "cannot import name 'DetectionResult'"
Este error ya está solucionado en la versión actual del código.

### La cámara no se abre
- Verifica que la cámara esté conectada
- Verifica los permisos de la cámara en Configuración del Sistema
- Prueba con un índice de cámara diferente en `camera_cv.py`

## Desarrollo

Para contribuir al proyecto, sigue la estructura de código existente y asegúrate de que todos los imports usen rutas relativas dentro del paquete `fomtan`.
