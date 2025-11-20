import sys
print(f"Python version: {sys.version}")

print("\n--- Intentando importar tensorflow.lite ---")
try:
    import tensorflow.lite as tflite
    print("✅ ÉXITO: tensorflow.lite importado correctamente")
    print(f"Ruta: {tflite}")
except Exception as e:
    print(f"❌ ERROR al importar tensorflow.lite: {type(e).__name__}: {e}")

print("\n--- Intentando importar tensorflow completo ---")
try:
    import tensorflow as tf
    print(f"✅ ÉXITO: tensorflow importado. Versión: {tf.__version__}")
except Exception as e:
    print(f"❌ ERROR al importar tensorflow: {type(e).__name__}: {e}")
