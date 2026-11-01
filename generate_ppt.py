from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def add_slide(prs, title, bullet_points):
    """Helper function to create a slide with a title and bullet points."""
    slide_layout = prs.slide_layouts[1] # 1 is Title and Content
    slide = prs.slides.add_slide(slide_layout)
    
    title_shape = slide.shapes.title
    title_shape.text = title
    
    body_shape = slide.shapes.placeholders[1]
    tf = body_shape.text_frame
    
    for i, point in enumerate(bullet_points):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = point
        p.font.size = Pt(24)

def create_presentation():
    prs = Presentation()

    # Slide 1: Title Slide
    title_slide_layout = prs.slide_layouts[0] # 0 is Title Slide
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = "AirScript: Writing in Air Using Computer Vision"
    subtitle.text = "A Minor Project Presentation\nDeveloped using Python, OpenCV, and MediaPipe"

    # Slide 2: Introduction
    add_slide(prs, "Introduction", [
        "Traditional writing requires physical surfaces like paper, whiteboards, or touch screens.",
        "AirScript introduces a touchless Human-Computer Interaction (HCI) interface.",
        "It uses a standard webcam to track hand movements in real-time.",
        "The tracked movements are translated into digital ink on the screen, allowing the user to write literally in the air."
    ])

    # Slide 3: Problem Statement & Objectives
    add_slide(prs, "Problem Statement & Objectives", [
        "Problem: Physical contact is often required for digital drawing/writing, which limits accessibility and sanitation in public spaces.",
        "Objective 1: Develop an accurate, real-time hand-tracking system without using specialized hardware (like depth cameras or gloves).",
        "Objective 2: Provide an intuitive gesture-based interface (draw, select, stop).",
        "Objective 3: Implement advanced features like Text-To-Speech (TTS) for accessibility."
    ])

    # Slide 4: Technology Stack
    add_slide(prs, "Technology Stack", [
        "Python: Core programming language.",
        "OpenCV (Open Source Computer Vision Library): Used for capturing webcam frames, processing images, and drawing the UI overlays.",
        "MediaPipe: Google's open-source framework used for robust, real-time 3D hand and finger tracking.",
        "NumPy: Used for matrix operations and efficient image masking.",
        "pyttsx3: Used for offline Text-to-Speech functionality."
    ])

    # Slide 5: System Architecture & Algorithm
    add_slide(prs, "Algorithm Flow", [
        "1. Capture: OpenCV reads video frames from the webcam.",
        "2. Detect: MediaPipe processes the frame to identify 21 3D hand landmarks.",
        "3. Gesture Recognition: The relative positions of the fingertips are calculated to determine if they are 'up' or 'down'.",
        "4. Mapping: If the index finger is up, its coordinates are stored.",
        "5. Rendering: A line is drawn connecting the previous coordinate to the current one on a virtual canvas.",
        "6. Blending: The canvas is overlayed seamlessly onto the live webcam feed."
    ])

    # Slide 6: Key Features & Gestures
    add_slide(prs, "Key Features & Gestures", [
        "Draw Mode (1 Finger): Keep index finger up to draw smoothly on screen.",
        "Selection Mode (2 Fingers): Keep index and middle fingers up to act as a cursor without drawing.",
        "Standby Mode (Fist): Close hand to pause drawing and save the stroke to memory.",
        "Customization: Select between 5 different brush colors or an Eraser.",
        "Undo/Redo: Easily correct mistakes using a state stack.",
        "TTS Integration: Press 'T' to have the computer read out text (if OCR is configured)."
    ])

    # Slide 7: Real-Life Applications
    add_slide(prs, "Real-Life Applications", [
        "Interactive Education: Teachers can draw diagrams virtually while facing their students.",
        "Accessibility: Allows individuals with limited motor skills to draw/write without handling a physical mouse or pen.",
        "Smart Boards & Kiosks: Touchless interaction in public spaces to maintain hygiene.",
        "Augmented Reality (AR): A fundamental technology for spatial computing interfaces."
    ])

    # Slide 8: Future Scope
    add_slide(prs, "Future Scope", [
        "Multi-Hand Support: Allow drawing with both hands simultaneously.",
        "Shape Auto-Correction: Detect messy circles or squares and snap them into perfect geometric shapes.",
        "Sign Language Recognition: Expand the gesture logic to recognize full sign language phrases.",
        "Cloud Integration: Auto-sync written notes directly to Google Drive or Evernote."
    ])

    # Slide 9: Conclusion
    add_slide(prs, "Conclusion", [
        "AirScript successfully bridges the gap between physical motion and digital rendering.",
        "By leveraging MediaPipe and OpenCV, we achieved high-accuracy tracking on standard hardware.",
        "The project demonstrates the immense potential of AI-driven computer vision in revolutionizing how we interact with machines."
    ])

    # Slide 10: Q&A
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = "Thank You!"
    subtitle = slide.placeholders[1]
    subtitle.text = "Any Questions?"

    # Save the presentation
    prs.save("AirScript_Presentation.pptx")
    print("Presentation generated successfully!")

if __name__ == "__main__":
    create_presentation()
