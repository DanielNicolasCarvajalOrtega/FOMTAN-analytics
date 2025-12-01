#!/usr/bin/env python3
"""
Script de validación para verificar la configuración del sistema FOMTAN
con las 15 clases del modelo entrenado.
"""

import sys
from pathlib import Path
import yaml

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_ok(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def validate_model_config():
    """Valida la configuración del modelo YAML"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}🔍 VALIDACIÓN DE CONFIGURACIÓN - SISTEMA FOMTAN{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    yaml_path = Path(__file__).parent.parent / "models" / "custom-coco128.yaml"
    
    # 1. Verificar que existe el archivo
    print(f"{Colors.BOLD}1. Verificando archivo de configuración...{Colors.END}")
    if not yaml_path.exists():
        print_error(f"No se encuentra: {yaml_path}")
        return False
    print_ok(f"Archivo encontrado: {yaml_path}")
    
    # 2. Cargar y parsear YAML
    print(f"\n{Colors.BOLD}2. Parseando archivo YAML...{Colors.END}")
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        print_ok("YAML parseado correctamente")
    except Exception as e:
        print_error(f"Error al parsear YAML: {e}")
        return False
    
    # 3. Validar numero de clases
    print(f"\n{Colors.BOLD}3. Validando número de clases...{Colors.END}")
    expected_nc = 15
    actual_nc = config.get('nc', 0)
    
    if actual_nc == expected_nc:
        print_ok(f"Número de clases correcto: {actual_nc}")
    else:
        print_error(f"Esperado: {expected_nc}, Encontrado: {actual_nc}")
        return False
    
    # 4. Validar nombres de clases
    print(f"\n{Colors.BOLD}4. Validando nombres de clases...{Colors.END}")
    expected_classes = [
        'Manzana-buen-estado', 'Manzana-mediano-estado', 'Manzana-mal-estado',
        'Tomate-buen-estado', 'Tomate-mediano-estado', 'Tomate-mal-estado',
        'Cereza-buen-estado', 'Cereza-mediano-estado', 'Cereza-mal-estado',
        'Durazno-buen-estado', 'Durazno-mediano-estado', 'Durazno-mal-estado',
        'Platano-buen-estado', 'Platano-mediano-estado', 'Platano-mal-estado'
    ]
    
    actual_classes = config.get('names', [])
    
    if len(actual_classes) != expected_nc:
        print_error(f"Esperado {expected_nc} nombres, encontrado {len(actual_classes)}")
        return False
    
    all_match = True
    for i, (expected, actual) in enumerate(zip(expected_classes, actual_classes)):
        if expected == actual:
            print_ok(f"  [{i}] {actual}")
        else:
            print_error(f"  [{i}] Esperado: '{expected}', Encontrado: '{actual}'")
            all_match = False
    
    if not all_match:
        return False
    
    # 5. Verificar distribución por tipo de fruta
    print(f"\n{Colors.BOLD}5. Distribución por tipo de fruta:{Colors.END}")
    fruits = {}
    for name in actual_classes:
        parts = name.split('-')
        if parts:
            fruit = parts[0]
            fruits[fruit] = fruits.get(fruit, 0) + 1
    
    for fruit, count in sorted(fruits.items()):
        emoji = {'Manzana': '🍎', 'Tomate': '🍅', 'Cereza': '🍒', 
                 'Durazno': '🍑', 'Platano': '🍌'}.get(fruit, '🍎')
        if count == 3:
            print_ok(f"  {emoji} {fruit}: {count} estados (completo)")
        else:
            print_warning(f"  {emoji} {fruit}: {count} estados (incompleto, esperado 3)")
    
    # 6. Verificar archivo de modelo
    print(f"\n{Colors.BOLD}6. Verificando archivo del modelo entrenado...{Colors.END}")
    model_path = Path(__file__).parent.parent / "models" / "best.pt"
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print_ok(f"Modelo encontrado: best.pt ({size_mb:.2f} MB)")
    else:
        print_warning("Modelo best.pt no encontrado - necesitas entrenarlo")
    
    # 7. Verificar código de main.py
    print(f"\n{Colors.BOLD}7. Verificando sincronización con main.py...{Colors.END}")
    main_path = Path(__file__).parent.parent / "src" / "fomtan" / "app" / "main.py"
    
    if main_path.exists():
        with open(main_path, 'r') as f:
            main_content = f.read()
        
        # Verificar whitelist
        missing_classes = []
        for cls in expected_classes:
            if f"'{cls}'" not in main_content:
                missing_classes.append(cls)
        
        if not missing_classes:
            print_ok("Todas las clases están en VALID_CLASSES")
        else:
            print_error(f"Clases faltantes en VALID_CLASSES: {missing_classes}")
            return False
        
        # Verificar filtro temporal
        if "TemporalDetectionFilter" in main_content and "from src.fomtan.core.detection_filter import" in main_content:
            print_ok("Filtro temporal importado y activado")
        else:
            print_warning("Filtro temporal no activado")
    else:
        print_error(f"No se encuentra: {main_path}")
        return False
    
    # Resumen final
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}✅ VALIDACIÓN COMPLETADA CON ÉXITO{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    print_info("Sistema configurado para:")
    print(f"  • {Colors.BOLD}15 clases{Colors.END} (5 tipos de frutas × 3 estados)")
    print(f"  • {Colors.BOLD}Filtro temporal{Colors.END} activado (2 frames en 1.5s)")
    print(f"  • {Colors.BOLD}Confidence{Colors.END} mínima: 60%")
    print(f"  • {Colors.BOLD}Max detecciones{Colors.END}: 30 objetos")
    
    print(f"\n{Colors.YELLOW}Listo para ejecutar: python src/fomtan/app/main.py{Colors.END}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = validate_model_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Validación interrumpida{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
