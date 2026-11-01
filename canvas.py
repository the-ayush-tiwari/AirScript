import cv2
import numpy as np
import os
from datetime import datetime

class Canvas:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        # Black canvas to draw on
        self.img_canvas = np.zeros((self.height, self.width, 3), np.uint8)
        
        self.draw_color = (255, 0, 255) # Default color (Magenta)
        self.brush_thickness = 15
        self.eraser_thickness = 50
        
        self.xp, self.yp = 0, 0
        
        # Stacks for undo/redo
        # We will save a copy of the canvas for every "stroke" completed
        self.undo_stack = []
        self.redo_stack = []
        
        # Save initial blank state
        self.undo_stack.append(self.img_canvas.copy())

    def update_point(self, x, y, is_drawing=True, is_eraser=False):
        """Draws a line from the previous point to the current point."""
        if self.xp == 0 and self.yp == 0:
            self.xp, self.yp = x, y

        if is_drawing:
            if is_eraser:
                cv2.line(self.img_canvas, (self.xp, self.yp), (x, y), (0, 0, 0), self.eraser_thickness)
            else:
                cv2.line(self.img_canvas, (self.xp, self.yp), (x, y), self.draw_color, self.brush_thickness)

        self.xp, self.yp = x, y

    def reset_point(self):
        """Resets the previous point when a stroke ends."""
        self.xp, self.yp = 0, 0

    def save_stroke(self):
        """Saves the current canvas state to the undo stack."""
        # Only save if there was a change to avoid duplicate empty states
        if len(self.undo_stack) == 0 or not np.array_equal(self.undo_stack[-1], self.img_canvas):
            self.undo_stack.append(self.img_canvas.copy())
            # Clear redo stack when a new stroke is made
            self.redo_stack.clear()
            
            # Limit undo history to save memory
            if len(self.undo_stack) > 20:
                self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 1: # Must keep at least the blank state
            # Pop the current state and put it in redo
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            
            # Revert to previous state
            self.img_canvas = self.undo_stack[-1].copy()

    def redo(self):
        if len(self.redo_stack) > 0:
            # Pop from redo and put back to undo
            next_state = self.redo_stack.pop()
            self.undo_stack.append(next_state)
            
            # Apply state
            self.img_canvas = self.undo_stack[-1].copy()

    def clear(self):
        self.img_canvas = np.zeros((self.height, self.width, 3), np.uint8)
        self.save_stroke()

    def save_image(self, folder="assets"):
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
        filepath = os.path.join(folder, filename)
        cv2.imwrite(filepath, self.img_canvas)
        print(f"Image saved to {filepath}")
        return filepath

    def get_canvas(self):
        return self.img_canvas

    def set_color(self, color):
        self.draw_color = color
