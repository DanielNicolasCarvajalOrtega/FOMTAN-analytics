import math
import time
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict

@dataclass
class BatchMetrics:
    total_count: int
    good_count: int
    medium_count: int
    bad_count: int
    timestamp: float

class HarvestAnalytics:
    def __init__(self):
        # PRECIOS DE MERCADO (Ganancia) por unidad en USD
        self.market_prices = {
            "buen-estado": 0.50,     # Precio Premium
            "mediano-estado": 0.30,  # Precio Estándar
            "mal-estado": 0.00       # Sin valor
        }
        
        # PRECIOS DE PÉRDIDA (Costo) por unidad en USD
        self.loss_prices = {
            "buen-estado": 0.00,     # Sin pérdida
            "mediano-estado": 0.10,  # Costo de procesamiento extra
            "mal-estado": 0.25       # Costo de descarte + trabajo desperdiciado
        }
        
        # Historial de métricas para análisis temporal
        self.history: List[BatchMetrics] = []
        
        # Acumulador de ganancias por TIPO DE FRUTA (no por estado)
        self.minute_start_time = time.time()
        self.minute_earnings_by_fruit = defaultdict(float)  # {'Manzana': $X, 'Tomate': $Y}
        self.minute_counts_by_fruit = defaultdict(int)      # {'Manzana': N, 'Tomate': M}
        
        # Constante para el modelo logarítmico
        self.LOG_K_FACTOR = 10.0

    def _extract_fruit_name(self, full_label):
        """
        Extrae el nombre de la fruta del label completo.
        'Manzana-buen-estado' -> 'Manzana'
        'Tomate-mal-estado' -> 'Tomate'
        """
        if '-' in full_label:
            return full_label.split('-')[0]
        return full_label

    def _extract_state(self, full_label):
        """
        Extrae el estado del label completo.
        'Manzana-buen-estado' -> 'buen-estado'
        """
        if '-' in full_label:
            parts = full_label.split('-', 1)  # Split en el primer guion solamente
            if len(parts) > 1:
                return parts[1]
        return "buen-estado"  # Default

    def add_sample(self, detections_df, timestamp):
        """Ingresa un frame de datos crudos para análisis"""
        if detections_df is None or detections_df.empty:
            return

        # Contar por categorías (para estadísticas generales)
        counts = {"buen-estado": 0, "mediano-estado": 0, "mal-estado": 0}
        
        for name in detections_df['name']:
            fruit = self._extract_fruit_name(name)
            state = self._extract_state(name)
            
            # Actualizar contadores generales de estado
            if state in counts:
                counts[state] += 1
            
            # Actualizar contadores POR FRUTA
            self.minute_counts_by_fruit[fruit] += 1
            
            # Calcular ganancia neta de esta fruta en este estado
            net_value = self.market_prices.get(state, 0) - self.loss_prices.get(state, 0)
            self.minute_earnings_by_fruit[fruit] += net_value
        
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

    def should_reset_minute(self, current_time):
        """Verifica si ha pasado 1 minuto para resetear contadores"""
        return (current_time - self.minute_start_time) >= 60.0

    def reset_minute_counters(self, current_time):
        """Resetea los contadores del minuto"""
        self.minute_start_time = current_time
        self.minute_earnings_by_fruit.clear()
        self.minute_counts_by_fruit.clear()

    def get_minute_earnings_by_fruit(self):
        """
        Retorna las ganancias acumuladas del minuto actual POR FRUTA
        Retorna: {'Manzana': $X, 'Tomate': $Y, 'Cereza': $Z, 'Total': $W}
        """
        earnings = dict(self.minute_earnings_by_fruit)
        earnings['Total'] = sum(earnings.values())
        return earnings

    def get_minute_counts_by_fruit(self):
        """
        Retorna los conteos del minuto actual POR FRUTA
        Retorna: {'Manzana': N, 'Tomate': M, 'Cereza': P}
        """
        return dict(self.minute_counts_by_fruit)

    # --- MATEMÁTICA DE NEGOCIO (Métodos antiguos mantenidos para compatibilidad) ---

    def calculate_projected_yield(self, hours_ahead=8) -> float:
        """
        FUNCIÓN LINEAL: y = mx + b
        Proyecta la cantidad de fruta basada en la velocidad actual de detección.
        """
        if len(self.history) < 2:
            return 0.0

        recent_samples = self.history[-100:]
        
        start_time = recent_samples[0].timestamp
        end_time = recent_samples[-1].timestamp
        time_diff_minutes = (end_time - start_time) / 60.0
        
        if time_diff_minutes <= 0: return 0.0
        
        total_harvested = sum(m.total_count for m in recent_samples)
        rate_per_minute = total_harvested / time_diff_minutes
        projection = rate_per_minute * (hours_ahead * 60)
        return round(projection, 2)

    def calculate_sorting_effort_index(self) -> float:
        """
        FUNCIÓN LOGARÍTMICA: E = k * ln(Total / Buenos)
        """
        if not self.history: return 0.0
        
        latest = self.history[-1]
        if latest.good_count == 0: return 100.0
        
        ratio = latest.total_count / latest.good_count
        effort_index = self.LOG_K_FACTOR * math.log(ratio)
        return min(100.0, round(effort_index, 2))

    def calculate_estimated_value(self) -> float:
        """
        ARITMÉTICA FINANCIERA
        Calcula el valor monetario del lote actual visible.
        """
        if not self.history: return 0.0
        latest = self.history[-1]
        
        value = (latest.good_count * self.market_prices["buen-estado"] +
                 latest.medium_count * self.market_prices["mediano-estado"] +
                 latest.bad_count * self.market_prices["mal-estado"])
                 
        return round(value, 2)

    def get_manager_report(self) -> str:
        """Genera un reporte ejecutivo en texto"""
        if not self.history: return "Esperando datos..."
        
        yield_proj = self.calculate_projected_yield(8)
        effort = self.calculate_sorting_effort_index()
        value = self.calculate_estimated_value()
        viability = "ALTA" if effort < 20 else "MEDIA" if effort < 50 else "BAJA (Riesgo)"
        
        return (
            f"--- REPORTE EJECUTIVO ---\n"
            f"💰 Valor Lote Actual: ${value} USD\n"
            f"📈 Proyección (8h): {yield_proj} unidades\n"
            f"⚠️ Índice de Esfuerzo: {effort}/100 ({viability})\n"
            f"-------------------------"
        )
