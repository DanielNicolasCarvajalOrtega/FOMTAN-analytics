
# FOMTAN – Clasificador de frutas para pre-selección antes del packing

FOMTAN (**Frescura Óptima Medida con Tecnología de ANálisis**) es un prototipo local que usa visión computacional para **apoyar la selección de frutas antes de la exportación**.  
A partir de la imagen capturada por la cámara del computador, el modelo de IA clasifica cada pieza en:

- 🟢 **VERDE**   → fruta de primera calidad (exportación / mercado premium)  
- 🟡 **AMARILLO** → segunda selección / industria / procesado  
- 🔴 **ROJO**    → descarte (daño severo, hongo, pudrición)

La aplicación muestra la cámara en tiempo real, un “semáforo” en otra ventana y reproduce un mensaje de voz con la decisión. El objetivo es **evitar que fruta defectuosa entre a las cajas de exportación** y reducir mermas en el packing.

---

## Contexto de uso

En la práctica, mucha fruta se clasifica “a ojo” en el campo o en la recepción del packing.  
Si se cuela fruta con hongos, golpes o sobremadurez en las cajas de exportación:

- baja la calidad comercial del lote completo,
- aumentan las mermas en cámara y transporte,
- se generan reclamos y descuentos por parte del comprador.

FOMTAN busca entregar una **herramienta simple** (semáforo + voz) que estandarice la decisión de calidad **antes** del empacado.

---

## Funcionalidades principales

- Captura de imagen desde **webcam**.
- Clasificación en 3 estados de calidad (`primera`, `segunda`, `descarte`) con un modelo de IA entrenado con dataset de frutas.
- Ventana de cámara + ventana de **semáforo de estado** (verde/amarillo/rojo).
- Mensaje de voz (Text-To-Speech) con la decisión para uso tipo “manos ocupadas”.
- Registro opcional en archivo CSV (fecha, clase, decisión) para análisis posterior.

---

## Arquitectura del prototipo

Arquitectura por capas, pensada para ser simple y extensible:

- **Core (dominio, funcional):**
  - Preprocesamiento de la imagen.
  - Conversión de predicción → decisión de negocio (VERDE/AMARILLO/ROJO + mensaje).
- **Adapters (IO):**
  - Captura de cámara con **OpenCV**.
  - Carga e inferencia del modelo (YOLOv8 clasificación o TFLite).
  - UI de ventanas (cámara + semáforo).
  - Audio con **pyttsx3** (TTS offline).
  - Logger en CSV.
- **App / Orquestador:**
  - Bucle principal que une todo y maneja la configuración.

---

## Tecnologías

- **Python 3.10+**
- **OpenCV** (`opencv-python`) – captura de cámara y visualización.
- **Ultralytics YOLOv8 (clasificación)** – entrenamiento/inferencia del modelo.
- **NumPy** – manipulación numérica de imágenes.
- **pyttsx3** – síntesis de voz offline.
- (Opcional) `tflite-runtime` si se usa un modelo exportado desde Google Cloud / AutoML.

---

## Dataset

El prototipo utiliza un dataset de frutas basado en:

- Conjunto tipo **Fruits-360** y/o datasets “fresh vs rotten” (Kaggle).
- Re-etiquetado en **tres clases de calidad**:
  - `primera`  → fruta visualmente sana.
  - `segunda`  → defectos leves pero comercializable.
  - `descarte` → fruta con hongos/pudrición/daño severo.
