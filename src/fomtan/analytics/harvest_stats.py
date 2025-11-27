import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BatchMetrics:
    total_count: int
    good_count: int
    medium_count: int
    bad_count: int
    timestamp: float

class HarvestAnalytics:
    def __init__(self):
        # Precios de mercado simulados (en USD o moneda local por unidad)
        self.prices = {
            "buen-estado": 0.50,    # Precio Premium
            "mediano-estado": 0.30, # Precio Estándar
            "mal-estado": 0.00      # Pérdida
        }
        
        # Historial de métricas para análisis temporal
        self.history: List[BatchMetrics] = []
        
        # Constante para el modelo logarítmico (ajustable según dificultad real)
        self.LOG_K_FACTOR = 10.0

    def add_sample(self, detections_df, timestamp):
        """Ingresa un frame de datos crudos para análisis"""
        if detections_df is None or detections_df.empty:
            return

        # Contar por categorías
        counts = {"buen-estado": 0, "mediano-estado": 0, "mal-estado": 0}
        
        for name in detections_df['name']:
            if "buen-estado" in name:
                counts["buen-estado"] += 1
            elif "mediano-estado" in name:
                counts["mediano-estado"] += 1
            elif "mal-estado" in name:
                counts["mal-estado"] += 1
        
        total = sum(counts.values())
        if total == 0: return

        metrics = BatchMetrics(
            total_count=total,
            good_count=counts["buen-estado"],
            medium_count=counts["mediano-estado"],
            bad_count=counts["mal-estado"],
            timestamp=timestamp
        )
        self.history.append(metrics)

    # --- MATEMÁTICA DE NEGOCIO ---

    def calculate_projected_yield(self, hours_ahead=8) -> float:
        """
        FUNCIÓN LINEAL: y = mx + b
        Proyecta la cantidad de fruta basada en la velocidad actual de detección.
        """
        if len(self.history) < 2:
            return 0.0

        # Usamos los últimos 60 segundos para calcular la velocidad actual (m)
        # m = (y2 - y1) / (x2 - x1)
        recent_samples = self.history[-100:] # Últimas 100 muestras
        
        start_time = recent_samples[0].timestamp
        end_time = recent_samples[-1].timestamp
        time_diff_minutes = (end_time - start_time) / 60.0
        
        if time_diff_minutes <= 0: return 0.0
        
        total_harvested = sum(m.total_count for m in recent_samples)
        
        # Velocidad: Frutas por minuto
        rate_per_minute = total_harvested / time_diff_minutes
        
        # Proyección Lineal: Rate * Minutos Futuros
        projection = rate_per_minute * (hours_ahead * 60)
        return round(projection, 2)

    def calculate_sorting_effort_index(self) -> float:
        """
        FUNCIÓN LOGARÍTMICA: E = k * ln(Total / Buenos)
        
        Mide qué tan difícil es procesar este lote.
        - Si todo es bueno: ln(1) = 0 (Esfuerzo nulo)
        - Si hay mucha basura: El esfuerzo sube logarítmicamente (se dispara).
        """
        if not self.history: return 0.0
        
        latest = self.history[-1]
        if latest.good_count == 0: return 100.0 # Esfuerzo máximo (todo basura)
        
        # Evitar división por cero y calcular ratio
        ratio = latest.total_count / latest.good_count
        
        # Fórmula Logarítmica
        effort_index = self.LOG_K_FACTOR * math.log(ratio)
        
        # Normalizar a escala 0-100 para gerencia
        return min(100.0, round(effort_index, 2))

    def calculate_estimated_value(self) -> float:
        """
        ARITMÉTICA FINANCIERA
        Calcula el valor monetario del lote actual visible.
        """
        if not self.history: return 0.0
        latest = self.history[-1]
        
        value = (latest.good_count * self.prices["buen-estado"] +
                 latest.medium_count * self.prices["mediano-estado"] +
                 latest.bad_count * self.prices["mal-estado"])
                 
        return round(value, 2)

    def get_manager_report(self) -> str:
        """Genera un reporte ejecutivo en texto"""
        if not self.history: return "Esperando datos..."
        
        yield_proj = self.calculate_projected_yield(8)
        effort = self.calculate_sorting_effort_index()
        value = self.calculate_estimated_value()
        
        # Interpretación para Gerencia
        viability = "ALTA" if effort < 20 else "MEDIA" if effort < 50 else "BAJA (Riesgo)"
        
        return (
            f"--- REPORTE EJECUTIVO ---\n"
            f"💰 Valor Lote Actual: ${value} USD\n"
            f"📈 Proyección (8h): {yield_proj} unidades\n"
            f"⚠️ Índice de Esfuerzo: {effort}/100 ({viability})\n"
            f"-------------------------"
        )
