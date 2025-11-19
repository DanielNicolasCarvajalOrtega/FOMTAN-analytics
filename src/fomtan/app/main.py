import cv2
import time
import random

from ..adapters.camera_cv import CameraCV
from ..adapters.console_ui import ConsoleUI
from ..core.types import DetectionResult

def mock_inference(frame) -> DetectionResult:
    """
    Mock inference function to simulate model output.
    """
    # Randomly generate a result for demonstration
    prob = random.random()
    if prob > 0.7:
        return DetectionResult(label="Good", probability=prob, color="Verde")
    elif prob > 0.4:
        return DetectionResult(label="Warning", probability=prob, color="Amarillo")
    else:
        return DetectionResult(label="Bad", probability=prob, color="Rojo")

def run_live_mode():
    camera = CameraCV()
    ui = ConsoleUI()

    print("Starting FOMTAN Live Mode...")
    print("Press 'q' to quit.")


    try:
        camera.open()
        
        while True:
            frame = camera.read_frame()
            if frame is None:
                print("\nFailed to capture frame. Exiting...")
                break

            # In a real scenario, we would pass the frame to a model here
            result = mock_inference(frame)
            
            ui.display_status(result)
            
            # Show camera feed in a window
            cv2.imshow('FOMTAN Live Feed', frame)

            # Check for 'q' key press in the GUI window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Simulate some processing time
            time.sleep(3.0)

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
