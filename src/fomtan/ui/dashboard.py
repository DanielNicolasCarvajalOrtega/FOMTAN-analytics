import matplotlib
matplotlib.use('Agg')  # Backend sin GUI, genera imágenes

import matplotlib.pyplot as plt
import numpy as np
import time
import io
from PIL import Image

class HarvestDashboard:
    def __init__(self, update_interval=60.0, width=800, height=600):
        self.update_interval = update_interval
        self.last_update = time.time()
        self.width = width
        self.height = height
        
        # Crear figura de Matplotlib (sin mostrar ventana)
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Imagen placeholder inicial
        self.current_image = self._create_placeholder()
        
        print("✅ Dashboard integrado inicializado")
        print("   → Mostrará ganancias/pérdidas por TIPO DE FRUTA")
        print("   → Se actualizará cada 60 segundos en la pantalla principal")

    def _create_placeholder(self):
        """Crea una imagen placeholder inicial"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Esperando datos...\n(Actualización cada 60s)', 
                    ha='center', va='center', fontsize=20,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        return self._fig_to_array()

    def _fig_to_array(self):
        """Convierte la figura de Matplotlib a un array numpy (imagen BGR para OpenCV)"""
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
        buf.seek(0)
        
        pil_img = Image.open(buf)
        img_array = np.array(pil_img)
        
        if img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
        
        img_bgr = img_array[:, :, ::-1].copy()
        buf.close()
        return img_bgr

    def should_update(self):
        """Verifica si ha pasado el tiempo suficiente para actualizar"""
        return (time.time() - self.last_update) > self.update_interval

    def update(self, analytics_engine):
        """
        Actualiza el gráfico con ganancias/pérdidas POR FRUTA
        """
        current_time = time.time()
        
        print("\n📊 Actualizando Dashboard de Ganancias POR FRUTA...")
        
        # Obtener datos del minuto (ahora por fruta)
        earnings = analytics_engine.get_minute_earnings_by_fruit()
        counts = analytics_engine.get_minute_counts_by_fruit()
        
        self.ax.clear()
        
        # Preparar datos
        # Ordenar frutas alfabéticamente y agregar Total al final
        fruit_names = sorted([k for k in earnings.keys() if k != 'Total'])
        fruit_names.append('Total')
        
        valores = [earnings.get(fruit, 0.0) for fruit in fruit_names]
        
        # Colores según ganancia/pérdida
        colores = []
        for fruit, valor in zip(fruit_names, valores):
            if fruit == 'Total':
                colores.append('blue')
            elif valor > 0:
                colores.append('green')  # Ganancia
            elif valor < 0:
                colores.append('red')     # Pérdida
            else:
                colores.append('gray')    # Neutral
        
        # Crear gráfico de barras
        bars = self.ax.bar(fruit_names, valores, color=colores, alpha=0.7, 
                          edgecolor='black', linewidth=2)
        
        # Añadir etiquetas sobre cada barra
        for bar, fruit, valor in zip(bars, fruit_names, valores):
            height = bar.get_height()
            count = counts.get(fruit, 0) if fruit != 'Total' else sum(counts.values())
            
            # Posicionar label arriba o abajo según si es positivo o negativo
            if height >= 0:
                y_pos = height
                va = 'bottom'
            else:
                y_pos = height
                va = 'top'
            
            # Formatear label
            if fruit == 'Total':
                label = f'${valor:.2f}'
                print(f"   💰 TOTAL: ${valor:.2f} USD")
            else:
                label = f'${valor:.2f}\n({count} un.)'
                signo = "+" if valor >= 0 else ""
                print(f"   🍎 {fruit}: {signo}${valor:.2f} USD ({count} unidades)")
            
            self.ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                        label, ha='center', va=va, 
                        fontsize=11, fontweight='bold')
        
        # Configuración del gráfico
        self.ax.axhline(y=0, color='black', linestyle='-', linewidth=1)  # Línea en y=0
        self.ax.set_ylabel('Ganancias / Pérdidas (USD)', fontsize=13, fontweight='bold')
        self.ax.set_title('GANANCIAS POR FRUTA (Minuto)\nVerde=Ganancia | Rojo=Pérdida', 
                         fontsize=15, fontweight='bold', pad=15)
        
        # Ajustar límites del eje Y para que se vean bien valores positivos y negativos
        max_abs = max(abs(min(valores)), abs(max(valores))) if valores else 1
        self.ax.set_ylim(-max_abs * 1.3, max_abs * 1.3)
        self.ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Información adicional
        total_items = sum(counts.values())
        info_text = f'Total procesado: {total_items} unidades'
        self.ax.text(0.02, 0.98, info_text,
                    transform=self.ax.transAxes,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6),
                    fontsize=10)
        
        plt.tight_layout()
        
        # Convertir a imagen
        self.current_image = self._fig_to_array()
        
        self.last_update = current_time
        
        # Resetear contadores
        analytics_engine.reset_minute_counters(current_time)
        print("   ✅ Dashboard actualizado\n")

    def get_image(self):
        """Retorna la imagen actual del dashboard"""
        return self.current_image

    def close(self):
        plt.close(self.fig)
