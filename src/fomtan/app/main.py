import cv2
import time
import os
from ..adapters.camera_cv import CameraCV
from ..adapters.console_ui import ConsoleUI
from ..adapters.model_tflite import ModelTFLite

def run_live_mode():
    camera = CameraCV()
    ui = ConsoleUI()

    print("Starting FOMTAN Live Mode...")
    print("Loading models...")
    
    # Resolve paths relative to the project root
    # src/fomtan/app/__file__ -> ../../../ -> Project Root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    models_dir = os.path.join(root_dir, "models", "tflite")
    
    try:
        model = ModelTFLite(
            detection_path=os.path.join(models_dir, "detect_fruit.tflite"),
            classification_path=os.path.join(models_dir, "cls_estado.tflite"),
            labels_path=os.path.join(models_dir, "labels.txt")
        )
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        return

    print("Press 'q' to quit.")

    try:
        camera.open()
        
        # OPTIMIZACIONES DE RENDIMIENTO
        frame_count = 0
        last_result = None
        fps_start = time.time()
        fps_counter = 0
        
        while True:
            frame = camera.read_frame()
            if frame is None:
                print("\nFailed to capture frame. Exiting...")
                break

            # Procesar inferencia solo cada 3 frames (reduce carga de CPU/GPU)
            if frame_count % 3 == 0:
                result = model.predict(frame)
                if result:
                    last_result = result
            
            frame_count += 1
            
            # Usar el último resultado válido
            if last_result:
                ui.display_status(last_result)
                
                # Draw result on frame
                label_text = f"{last_result.etiqueta} ({last_result.probabilidad:.2f})"
                color_map = {"Verde": (0, 255, 0), "Amarillo": (0, 255, 255), "Rojo": (0, 0, 255)}
                color = color_map.get(last_result.color, (255, 255, 255))
                
                cv2.putText(frame, label_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            else:
                # No detection
                cv2.putText(frame, "Buscando...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
            
            # Calcular y mostrar FPS
            fps_counter += 1
            if fps_counter >= 48:
                fps = fps_counter / (time.time() - fps_start)
                fps_start = time.time()
                fps_counter = 0
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Show camera feed in a window
            cv2.imshow('FOMTAN Live Feed', frame)

            # Check for 'q' key press in the GUI window (waitKey ya controla FPS)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        camera.close()
        cv2.destroyAllWindows()
        print("\nSession closed.")

if __name__ == "__main__":
    run_live_mode()
