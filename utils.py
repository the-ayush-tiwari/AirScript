import cv2
# pyrefly: ignore [missing-import]
import pytesseract
# pyrefly: ignore [missing-import]
import pyttsx3
import numpy as np

class UIDrawer:
    def __init__(self):
        # Colors (B, G, R)
        self.colors = [
            (255, 0, 255),  # Magenta
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255)   # Yellow
        ]
        
        self.color_names = ["Magenta", "Red", "Green", "Blue", "Yellow"]
        self.current_color_idx = 0
        
        # UI Layout
        self.box_width = 100
        self.box_height = 80
        self.margin_top = 20
        self.margin_left = 20
        
    def draw_ui(self, img, fps=0, current_mode="None", text_overlay=""):
        # Draw color palette
        for i, color in enumerate(self.colors):
            x1 = self.margin_left + i * (self.box_width + 10)
            y1 = self.margin_top
            x2 = x1 + self.box_width
            y2 = y1 + self.box_height
            
            # Highlight selected color
            if color == self.colors[self.current_color_idx]:
                cv2.rectangle(img, (x1-5, y1-5), (x2+5, y2+5), (255, 255, 255), cv2.FILLED)
                
            cv2.rectangle(img, (x1, y1), (x2, y2), color, cv2.FILLED)
            cv2.putText(img, self.color_names[i], (x1 + 10, y1 + 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255) if color != (0,255,255) else (0,0,0), 2)

        # Draw Eraser box
        eraser_x1 = self.margin_left + len(self.colors) * (self.box_width + 10)
        cv2.rectangle(img, (eraser_x1, self.margin_top), (eraser_x1 + self.box_width, self.margin_top + self.box_height), (255, 255, 255), 2)
        cv2.putText(img, "Eraser", (eraser_x1 + 15, self.margin_top + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Draw Clear box
        clear_x1 = eraser_x1 + self.box_width + 10
        cv2.rectangle(img, (clear_x1, self.margin_top), (clear_x1 + self.box_width, self.margin_top + self.box_height), (100, 100, 100), cv2.FILLED)
        cv2.putText(img, "Clear", (clear_x1 + 20, self.margin_top + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Overlay FPS and Mode
        cv2.putText(img, f"FPS: {fps}", (20, img.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Mode: {current_mode}", (200, img.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Display OCR text if present
        if text_overlay:
            cv2.putText(img, f"Recognized: {text_overlay}", (img.shape[1]//2 - 100, img.shape[0] - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

        return img, eraser_x1, clear_x1

    def get_color(self):
        return self.colors[self.current_color_idx]
        
    def check_selection(self, x, y, eraser_x1, clear_x1):
        """Checks if a point (x,y) is hovering over a UI button."""
        if self.margin_top < y < self.margin_top + self.box_height:
            # Check colors
            for i in range(len(self.colors)):
                x1 = self.margin_left + i * (self.box_width + 10)
                if x1 < x < x1 + self.box_width:
                    self.current_color_idx = i
                    return "Color"
            
            # Check Eraser
            if eraser_x1 < x < eraser_x1 + self.box_width:
                return "Eraser"
            
            # Check Clear
            if clear_x1 < x < clear_x1 + self.box_width:
                return "Clear"
                
        return None

class AdvancedFeatures:
    def __init__(self):
        # Initialize Text-To-Speech engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150) # Speed
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            self.engine = None

    def recognize_text(self, canvas_img):
        """Extracts text from the black canvas using Tesseract OCR."""
        # The canvas has colored text on black background. 
        # Convert to grayscale and threshold to white text on black for better OCR, 
        # or invert to black text on white.
        gray = cv2.cvtColor(canvas_img, cv2.COLOR_BGR2GRAY)
        
        # Anything not black becomes white
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        
        # Optional: Invert image (black text on white background is often preferred by Tesseract)
        inverted = cv2.bitwise_not(thresh)
        
        # Dilate slightly to connect broken lines typical of hand drawing
        kernel = np.ones((3,3), np.uint8)
        processed = cv2.erode(inverted, kernel, iterations=1) # Erode inverted = thicken text
        
        try:
            # Requires tesseract to be installed on system
            text = pytesseract.image_to_string(processed, config='--psm 7').strip()
            return text
        except Exception as e:
            print(f"OCR Error: {e}. Is Tesseract installed and in PATH?")
            return ""

    def speak(self, text):
        """Speaks the provided text."""
        if self.engine and text:
            # Run in a separate thread or use a simple blocking call if okay with slight pause
            self.engine.say(text)
            self.engine.runAndWait()
