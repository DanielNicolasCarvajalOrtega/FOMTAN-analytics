# 📋 Configuración del Sistema FOMTAN - 15 Clases

**Fecha actualización**: 2025-11-30  
**Versión**: 2.0  
**Branch**: US-03.1-voz-de-la-decisión-upgrade

---

## 🎯 Modelo Entrenado

El sistema ahora trabaja con **15 clases** distribuidas en **5 tipos de frutas**:

### Clases por Tipo de Fruta:

#### 🍎 Manzana (3 estados)
- `Manzana-buen-estado` - Precio: $0.50
- `Manzana-mediano-estado` - Precio: $0.30
- `Manzana-mal-estado` - Sin valor

#### 🍅 Tomate (3 estados)
- `Tomate-buen-estado` - Precio: $0.50
- `Tomate-mediano-estado` - Precio: $0.30
- `Tomate-mal-estado` - Sin valor

#### 🍒 Cereza (3 estados)
- `Cereza-buen-estado` - Precio: $0.50
- `Cereza-mediano-estado` - Precio: $0.30
- `Cereza-mal-estado` - Sin valor

#### 🍑 Durazno (3 estados) **NUEVO**
- `Durazno-buen-estado` - Precio: $0.50
- `Durazno-mediano-estado` - Precio: $0.30
- `Durazno-mal-estado` - Sin valor

#### 🍌 Plátano (3 estados) **NUEVO**
- `Platano-buen-estado` - Precio: $0.50
- `Platano-mediano-estado` - Precio: $0.30
- `Platano-mal-estado` - Sin valor

---

## ⚙️ Configuración del Sistema

### Pipeline de Detección (3 Capas de Filtrado)

```
Frame de Cámara
    ↓
YOLOv5 Detección (confidence ≥ 60%)
    ↓
[FILTRO 1] Whitelist de 15 clases válidas
    ↓
[FILTRO 2] Filtro Temporal (2 frames en 1.5s)
    ↓
[FILTRO 3] Procesar solo detecciones validadas
    ↓
Audio + Analytics + Dashboard
```

### Parámetros Clave

| Componente | Parámetro | Valor | Justificación |
|------------|-----------|-------|---------------|
| **Modelo YOLOv5** | Confidence | 60% | Balance entre sensibilidad y precisión |
| | IOU Threshold | 45% | Reducir duplicados |
| | Max Detecciones | 30 | Óptimo para agricultura |
| **Filtro Temporal** | Frames Requeridos | 2 | Elimina parpadeos |
| | Timeout | 1.5s | Ventana de validación |
| **Voz Neural** | Cooldown | 10s | Evita repetición |
| | Confidence Mínima | 75% | Solo anuncios seguros |
| | Cantidad Mínima | 2 objetos | Reduce ruido |
| **Dashboard** | Intervalo Actualización | 60s | Métricas por minuto |

---

## 💰 Sistema de Precios

### Precios de Mercado (Ganancias)
- **Buen Estado**: $0.50/unidad
- **Mediano Estado**: $0.30/unidad
- **Mal Estado**: $0.00/unidad

### Precios de Pérdida (Costos)
- **Buen Estado**: $0.00/unidad (sin costo)
- **Mediano Estado**: $0.10/unidad (procesamiento extra)
- **Mal Estado**: $0.25/unidad (descarte + trabajo desperdiciado)

### Ganancia Neta por Estado
- **Buen Estado**: $0.50 - $0.00 = **$0.50**
- **Mediano Estado**: $0.30 - $0.10 = **$0.20**
- **Mal Estado**: $0.00 - $0.25 = **-$0.25** (pérdida)

---

## 🔄 Flujo de Trabajo del Sistema

### 1. Detección
- Cámara captura frame
- YOLOv5 procesa imagen (640px)
- Detecciones brutas generadas

### 2. Filtrado (3 pasos)
1. **Whitelist**: Solo 15 clases válidas pasan
2. **Temporal**: Añade al historial de frames
3. **Validación**: Solo detecciones en ≥2 frames pasan

### 3. Procesamiento
- **Audio**: Anuncia objetos validados (si cumplen criterios)
- **Analytics**: Acumula métricas por fruta
- **Dashboard**: Actualiza cada 60s con ganancias

### 4. Visualización
- Video con bounding boxes verdes
- Labels con confianza
- Dashboard integrado lateral
- Interface unificada

---

## 🎮 Controles del Usuario

| Tecla | Acción |
|-------|--------|
| `ESC` | Salir del sistema |
| `F` | Pantalla completa ON/OFF |

---

## 📊 Dashboard de Ganancias

El dashboard muestra:
- **Ganancias por tipo de fruta** (Manzana, Tomate, Cereza, Durazno, Plátano)
- **Barra de Total** (suma de todas las frutas)
- **Código de colores**:
  - 🟢 Verde = Ganancia
  - 🔴 Rojo = Pérdida
  - 🔵 Azul = Total
- **Información por barra**:
  - Monto en USD
  - Cantidad de unidades procesadas

### Ciclo de Actualización
1. Sistema acumula detecciones durante 60 segundos
2. Dashboard se actualiza con totales
3. Contadores se resetean
4. Nuevo ciclo comienza

---

## 🚀 Optimizaciones Implementadas

### Reducción de Falsos Positivos
✅ Whitelist de clases (elimina detecciones de clases no entrenadas)  
✅ Filtro temporal (elimina parpadeos de 1 frame)  
✅ Confidence threshold optimizado (60%)  

### Mejora de UX
✅ Dashboard integrado (sin ventanas separadas)  
✅ Voz menos intrusiva (10s cooldown, 2+ objetos)  
✅ Información clara en pantalla  
✅ Controles simples (ESC, F)  

### Performance
✅ AMP activado (procesamiento más rápido)  
✅ Max detecciones limitado a 30  
✅ Dashboard renderizado eficiente (backend Agg)  

---

## 🔧 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `models/custom-coco128.yaml` | nc: 9 → 15, agregadas 6 clases |
| `src/fomtan/app/main.py` | Whitelist expandida, filtro temporal activado |
| `src/fomtan/analytics/harvest_stats.py` | Tracking por tipo de fruta |
| `src/fomtan/ui/dashboard.py` | Gráfico de ganancias por fruta |
| `src/fomtan/core/detection_filter.py` | Creado y activado |

---

## ⚠️ Próximos Pasos Recomendados

1. **Entrenar modelo con dataset limpio** - Eliminar detecciones erróneas de marcos
2. **Validar precios** - Ajustar valores de mercado según realidad
3. **Testing exhaustivo** - Probar con las 5 frutas en diferentes condiciones
4. **Optimización de filtro temporal** - Ajustar parámetros según resultados

---

## 📝 Notas Técnicas

- El filtro temporal usa `deque` con `maxlen=10` para eficiencia de memoria
- La validación temporal requiere que un objeto aparezca en **al menos 2 frames** dentro de una ventana de **1.5 segundos**
- El dashboard usa backend `Agg` (sin GUI) y convierte matplotlib figures a arrays numpy BGR
- La integración usa `np.hstack` para combinar video y dashboard horizontalmente
