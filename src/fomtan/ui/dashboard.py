import matplotlib
# Configurar backend para asegurar que la ventana aparezca en Mac/Windows
try:
    matplotlib.use('TkAgg')
except:
    pass # Si falla, usa el default

import matplotlib.pyplot as plt
import time

class HarvestDashboard:
    def __init__(self, update_interval=10.0):
        self.update_interval = update_interval
        self.last_update = time.time()
        
        # Configuración de Matplotlib
        plt.ion() # Modo interactivo
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(6, 8))
        self.fig.canvas.manager.set_window_title('FOMTAN - Harvest Intelligence Dashboard')
        plt.tight_layout(pad=3.0)
        
        # FORZAR QUE LA VENTANA APAREZCA
        plt.show(block=False)
        
        print("✅ Dashboard UI inicializado (Ventana Gráfica)")

    def should_update(self):
        """Verifica si ha pasado el tiempo suficiente para actualizar"""
        return (time.time() - self.last_update) > self.update_interval

    def update(self, analytics_engine):
        """
        Recibe el motor de analítica y actualiza los gráficos.
        """
        current_time = time.time()
        
        # Calcular KPIs usando el motor de analítica
        proj = analytics_engine.calculate_projected_yield(8)
        effort = analytics_engine.calculate_sorting_effort_index()
        value = analytics_engine.calculate_estimated_value()
        
        # Limpiar ejes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Gráfico 1: Proyección (Barras)
        self.ax1.bar(['Proyección (8h)'], [proj], color='green')
        self.ax1.set_title(f'Proyección de Cosecha: {int(proj)} un.')
        self.ax1.set_ylim(0, max(100, proj * 1.2))
        
        # Gráfico 2: Esfuerzo (Medidor)
        color_effort = 'green' if effort < 30 else 'orange' if effort < 60 else 'red'
        self.ax2.barh(['Esfuerzo'], [effort], color=color_effort)
        self.ax2.set_xlim(0, 100)
        self.ax2.set_title(f'Índice de Esfuerzo (Log): {effort:.1f}/100')
        
        # Gráfico 3: Valor Financiero (Texto grande)
        self.ax3.text(0.5, 0.5, f"${value:.2f} USD", 
                fontsize=30, ha='center', va='center', color='blue')
        self.ax3.set_title('Valor Estimado del Lote Actual')
        self.ax3.axis('off')
        
        # Refrescar ventana
        plt.draw()
        plt.pause(0.001)
        
        self.last_update = current_time

    def close(self):
        plt.close(self.fig)
