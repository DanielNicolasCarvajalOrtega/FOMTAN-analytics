from ..core.types import DetectionResult
import sys

class ConsoleUI:
    def display_status(self, result: DetectionResult) -> None:
        """
        Muestra el resultado de la detección en la consola con colores.
        """
        color_map = {
            'verde': '\033[92m',
            'amarillo': '\033[93m',
            'rojo': '\033[91m',
        }
        reset_code = '\033[0m'
        
        color_code = color_map.get(result.color, reset_code)
        
        # Limpia la línea e imprime el estado
        # mueve el cursor al principio de la línea
        sys.stdout.write(f"\r{color_code}Status: {result.color.upper()} | Etiqueta: {result.etiqueta} | Prob: {result.probabilidad:.2f}{reset_code}")
        sys.stdout.flush()
