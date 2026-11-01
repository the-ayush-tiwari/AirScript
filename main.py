import cv2
import time
import numpy as np

from hand_tracker import HandTracker
from canvas import Canvas
from utils import UIDrawer, AdvancedFeatures

def main():
    # 1. Setup Video Capture
    # Standard resolution for modern webcams
    wCam, hCam = 1280, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    
    # Check if webcam opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # 2. Initialize Modules
    tracker = HandTracker(detection_con=0.85) # High confidence needed for precise writing
    canvas = Canvas(width=wCam, height=hCam)
    ui = UIDrawer()
    ai = AdvancedFeatures()

    # FPS Calculation Variables
    pTime = 0
    
    # State variables
    is_eraser = False
    current_mode = "Standby"
    recognized_text = ""
    
    print("AirScript Started.")
    print("Keyboard shortcuts:")
    print("  's' - Save canvas")
    print("  'u' - Undo")
    print("  'r' - Redo")
    print("  'c' - OCR (Read text)")
    print("  't' - TTS (Speak text)")
    print("  'q' - Quit")

    while True:
        # 1. Read Frame
        success, img = cap.read()
        if not success:
            break
            
        # Flip the image horizontally for a selfie-view display
        img = cv2.flip(img, 1)
        
        # 2. Find Hand Landmarks
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img, draw=False)
        
        # UI overlays
        cTime = time.time()
        fps = int(1 / (cTime - pTime)) if pTime != 0 else 0
        pTime = cTime
        img, eraser_x1, clear_x1 = ui.draw_ui(img, fps, current_mode, recognized_text)

        if len(lm_list) != 0:
            # Tip of index and middle fingers
            x1, y1 = lm_list[8][1:]
            x2, y2 = lm_list[12][1:]

            # 3. Check which fingers are up
            fingers = tracker.fingers_up()
            
            # 4. Mode Selection logic
            
            # If Two Fingers are up: Selection Mode
            if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
                current_mode = "Selection"
                # Reset previous point so we don't draw a line when returning to draw mode
                canvas.reset_point()
                
                # Check for click (hovering for a brief moment, or simply based on position)
                selection = ui.check_selection(x1, y1, eraser_x1, clear_x1)
                
                if selection == "Color":
                    canvas.set_color(ui.get_color())
                    is_eraser = False
                elif selection == "Eraser":
                    is_eraser = True
                elif selection == "Clear":
                    canvas.clear()
                    is_eraser = False

                # Draw a selection cursor
                cv2.circle(img, (x1, y1), 15, (255, 255, 255), cv2.FILLED)
                
            # If Index Finger is up (and middle is down): Drawing Mode
            elif fingers[1] and not fingers[2]:
                current_mode = "Drawing (Eraser)" if is_eraser else "Drawing"
                cv2.circle(img, (x1, y1), 15, (0, 0, 0) if is_eraser else canvas.draw_color, cv2.FILLED)
                
                canvas.update_point(x1, y1, is_drawing=True, is_eraser=is_eraser)
                
            # If fist is closed (or just all fingers down): Standby Mode
            elif not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
                current_mode = "Standby"
                canvas.reset_point()
                # Save the stroke state to undo stack when a stroke is finished
                canvas.save_stroke()
                
            else:
                current_mode = "Hovering"
                canvas.reset_point()
                
        else:
            current_mode = "No Hand Detected"
            canvas.reset_point()

        # 5. Blend Canvas and Image
        img_canvas = canvas.get_canvas()
        
        # Convert canvas to grayscale then threshold to create a mask
        img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        
        # Add canvas to frame (where canvas is black, show frame. Where canvas has color, show color)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, img_canvas)
        
        # 6. Show the frame
        cv2.imshow("AirScript", img)
        
        # 7. Keyboard Input Handling
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            canvas.save_image()
        elif key == ord('c'):
            # OCR logic
            print("Running OCR...")
            recognized_text = ai.recognize_text(img_canvas)
            print(f"Recognized: {recognized_text}")
        elif key == ord('t'):
            # TTS logic
            if recognized_text:
                print("Speaking...")
                ai.speak(recognized_text)
            else:
                print("No text recognized to speak. Press 'c' first.")
        elif key == ord('u'):
            canvas.undo()
        elif key == ord('r'):
            canvas.redo()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
