# 🍎 FOMTAN Analytics (Prototipo v3.0)

> 🚧 **ESTADO DEL PROYECTO: EN DESARROLLO / PROTOTIPO** 🚧
>
> Este software es una versión de prueba técnica diseñada para validar la lógica de negocio y los algoritmos de visión artificial en un entorno controlado (PC/Mac). **NO es la versión final para producción.**
>
> El objetivo final es migrar esta lógica a una **Aplicación Móvil (Android/iOS)** usando tecnología Edge AI (TFLite/CoreML) para su uso en campo sin internet.

---

## � Descripción General

**FOMTAN Analytics** es un sistema inteligente para el sector agrícola (AgroTech) que utiliza Visión Artificial para detectar, clasificar y analizar la cosecha en tiempo real.

### 🌟 Características Principales (Actuales)

1.  **👁️ Detección de Objetos (YOLOv5)**:
    *   Identifica frutas (Manzanas, Tomates, Cerezas) y su estado (Bueno, Regular, Malo).
    *   Alta precisión ajustada para evitar falsos positivos.

2.  **🗣️ Asistente de Voz Neural (Edge TTS)**:
    *   Te habla en tiempo real usando voces ultra-realistas (Microsoft Azure Neural Voices).
    *   Avisa qué frutas ve sin necesidad de mirar la pantalla.
    *   *Voz actual: "Dalia" (Español México).*

3.  **🧠 Harvest Intelligence (Analítica de Negocio)**:
    *   **Proyección de Rendimiento**: Predice cuántas unidades se cosecharán en el día (Función Lineal).
    *   **Índice de Esfuerzo**: Calcula la dificultad del lote usando logaritmos (si hay mucha fruta mala, el índice sube).
    *   **Valoración Financiera**: Estima el dinero ($ USD) visible en pantalla.

4.  **📊 Dashboard en Tiempo Real**:
    *   Ventana gráfica independiente que muestra los KPIs de negocio actualizados cada 10 segundos.

---

## 🚀 Cómo Ejecutar el Sistema

### Requisitos Previos
*   Python 3.8+
*   Entorno virtual configurado (`.venv`)
*   Cámara Web
*   Conexión a Internet (Solo para la voz neural de alta calidad)

### Pasos para Iniciar

1.  **Activar el entorno virtual**:
    ```bash
    source .venv/bin/activate
    ```

2.  **Ejecutar el programa principal**:
    ```bash
    python src/fomtan/app/main.py
    ```
    *(Nota: El sistema abrirá dos ventanas: la cámara y el dashboard estadístico)*

3.  **Controles**:
    *   `ESC`: Salir del programa.

---

## 📂 Arquitectura del Proyecto

El código ha sido refactorizado para seguir principios de **Arquitectura Limpia y Modular**:

```
FOMTAN-analytics/
├── models/                 # Modelos de IA (YOLOv5 .pt)
├── src/
│   └── fomtan/
│       ├── app/
│       │   └── main.py     # 🎮 Orquestador Principal (Solo lógica de control)
│       ├── adapters/
│       │   └── audio_tts.py # 🗣️ Adaptador de Voz (Edge TTS / Subprocess)
│       ├── analytics/
│       │   └── harvest_stats.py # 🧠 Lógica Matemática (Proyecciones, Logaritmos)
│       └── ui/
│           └── dashboard.py # 📊 Interfaz Gráfica (Matplotlib / TkAgg)
└── README.md               # Documentación
```

---

## 🔮 Roadmap (Siguientes Pasos)

Este prototipo en Python sirve para calibrar las matemáticas y la experiencia de usuario. El siguiente paso es la **Migración a Móvil**:

1.  **Exportación de Modelo**: Convertir `best.pt` a `.tflite` (Android) y `.mlmodel` (iOS).
2.  **App Nativa**: Desarrollar la interfaz en **Flutter** o **Kotlin/Swift**.
3.  **Edge AI**: Ejecutar la detección directamente en el procesador del celular (NPU) sin necesidad de internet ni PC.

---

**Desarrollado por el equipo de FOMTAN Analytics**
*Versión de Desarrollo - Noviembre 2025*
