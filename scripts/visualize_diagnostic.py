"""
Script para visualizar la distribución del dataset y problemas identificados
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter
import os

# Datos del análisis
CLASS_NAMES = [
    'Manzana-buen-estado', 'Manzana-mediano-estado', 'Manzana-mal-estado',
    'Tomate-buen-estado', 'Tomate-mediano-estado', 'Tomate-mal-estado',
    'Cereza-buen-estado', 'Cereza-mediano-estado', 'Cereza-mal-estado',
    'Durazno-buen-estado', 'Durazno-mediano-estado', 'Durazno-mal-estado',
    'Platano-buen-estado', 'Platano-mediano-estado', 'Platano-mal-estado'
]

# Distribución actual del dataset (del análisis)
CURRENT_DISTRIBUTION = {
    0: 33,  # Manzana-buen-estado
    1: 0,   # Manzana-mediano-estado
    2: 3,   # Manzana-mal-estado
    3: 6,   # Tomate-buen-estado
    4: 4,   # Tomate-mediano-estado
    5: 6,   # Tomate-mal-estado
    6: 16,  # Cereza-buen-estado
    7: 0,   # Cereza-mediano-estado
    8: 23,  # Cereza-mal-estado
    9: 6,   # Durazno-buen-estado
    10: 6,  # Durazno-mediano-estado
    11: 0,  # Durazno-mal-estado
    12: 15, # Platano-buen-estado
    13: 0,  # Platano-mediano-estado
    14: 0   # Platano-mal-estado
}

def create_diagnostic_visualization():
    """Crea visualización del diagnóstico"""
    
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('🔍 DIAGNÓSTICO: Problemas de Reconocimiento de Objetos - FOMTAN Analytics', 
                 fontsize=16, fontweight='bold')
    
    # Subplot 1: Distribución del Dataset Actual
    ax1 = plt.subplot(2, 2, 1)
    counts = [CURRENT_DISTRIBUTION[i] for i in range(15)]
    colors = ['red' if c == 0 else 'orange' if c < 10 else 'yellow' if c < 20 else 'green' 
              for c in counts]
    
    bars = ax1.barh(range(15), counts, color=colors, alpha=0.7)
    ax1.set_yticks(range(15))
    ax1.set_yticklabels(CLASS_NAMES, fontsize=8)
    ax1.set_xlabel('Número de Muestras de Entrenamiento', fontweight='bold')
    ax1.set_title('📊 Distribución ACTUAL del Dataset (Total: 118 muestras)', fontweight='bold')
    ax1.axvline(x=150, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Mínimo Recomendado (150)')
    ax1.legend()
    ax1.grid(axis='x', alpha=0.3)
    
    # Añadir valores en las barras
    for i, (bar, count) in enumerate(zip(bars, counts)):
        if count > 0:
            ax1.text(count + 1, i, f'{count}', va='center', fontsize=8)
    
    # Subplot 2: Distribución IDEAL vs ACTUAL
    ax2 = plt.subplot(2, 2, 2)
    ideal_dist = [150] * 15
    
    x = range(15)
    width = 0.35
    
    bars1 = ax2.bar([i - width/2 for i in x], counts, width, label='Actual', color='orange', alpha=0.7)
    bars2 = ax2.bar([i + width/2 for i in x], ideal_dist, width, label='Ideal (Mínimo)', color='green', alpha=0.5)
    
    ax2.set_ylabel('Número de Muestras', fontweight='bold')
    ax2.set_title('📈 Comparación: Dataset Actual vs Ideal', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'C{i}' for i in range(15)], fontsize=8)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Subplot 3: Rendimiento en Validación
    ax3 = plt.subplot(2, 2, 3)
    
    # Datos del análisis de validación
    validation_results = {
        'Cereza-buen-estado': (6, 1),  # (ground truth, detectado)
        'Tomate-mal-estado': (2, 0),
        'Manzana-mal-estado': (2, 0),
        'Platano-buen-estado': (1, 0),
        'Tomate-mediano-estado': (1, 0),
        'Manzana-buen-estado': (1, 0),
    }
    
    classes = list(validation_results.keys())
    gt_counts = [validation_results[c][0] for c in classes]
    detected_counts = [validation_results[c][1] for c in classes]
    
    x = range(len(classes))
    width = 0.35
    
    bars1 = ax3.bar([i - width/2 for i in x], gt_counts, width, label='Objetos Reales', color='blue', alpha=0.7)
    bars2 = ax3.bar([i + width/2 for i in x], detected_counts, width, label='Detectados', color='red', alpha=0.7)
    
    ax3.set_ylabel('Cantidad', fontweight='bold')
    ax3.set_title('🎯 Rendimiento en Validación (15 imágenes)', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(classes, rotation=45, ha='right', fontsize=7)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # Añadir texto con tasa de detección
    ax3.text(0.5, 0.95, 'Tasa de Detección: 7.7% (1/13 objetos)', 
             transform=ax3.transAxes, ha='center', va='top',
             bbox=dict(boxstyle='round', facecolor='red', alpha=0.3),
             fontsize=10, fontweight='bold')
    
    # Subplot 4: Problemas Identificados
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    problems_text = """
🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS

1. DATASET INSUFICIENTE
   • Total: 118 anotaciones para 15 clases
   • Promedio: ~8 muestras por clase
   • Mínimo recomendado: 150+ por clase
   • Déficit: 92% menos datos del requerido

2. CLASES SIN DATOS (5 clases = 33%)
   • Manzana-mediano-estado: 0 muestras
   • Cereza-mediano-estado: 0 muestras
   • Durazno-mal-estado: 0 muestras
   • Platano-mediano-estado: 0 muestras
   • Platano-mal-estado: 0 muestras

3. DESBALANCE EXTREMO
   • Clase más representada: 33 muestras (28%)
   • 5 clases con 0 muestras
   • 7 clases con < 10 muestras

4. OVERFITTING
   • Modelo memoriza en vez de generalizar
   • Tasa de detección: 7.7% en validación
   
💡 SOLUCIÓN PRINCIPAL
   → Aumentar dataset a 2,250+ anotaciones
   → Data Augmentation (5x multiplicador)
   → Recolección de nuevas imágenes
   → Re-entrenamiento con configuración óptima
    """
    
    ax4.text(0.05, 0.95, problems_text, transform=ax4.transAxes,
             fontsize=9, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Guardar figura
    output_path = 'docs/diagnostic_visualization.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Visualización guardada en: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    create_diagnostic_visualization()
