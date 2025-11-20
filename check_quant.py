import tensorflow.lite as tflite
import os

path = "models/tflite/cls_estado.tflite"

interpreter = tflite.Interpreter(model_path=path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]

print(f"Input Quantization: {input_details['quantization']}")
print(f"Output Quantization: {output_details['quantization']}")
