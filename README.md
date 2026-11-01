# AirScript: Writing in Air Using Computer Vision

AirScript is an AI-based computer vision project that allows users to write in the air using their hand movements, capturing the writing in real-time through a webcam and drawing it on the screen. It features a modern, colorful UI, customizable brushes, and advanced AI features like OCR (Optical Character Recognition) to convert handwritten text into editable text, and Text-To-Speech (TTS) to speak it aloud.

## Main Features
- **Hand Tracking**: Uses MediaPipe to accurately track your hand and index finger.
- **Gesture Control**:
  - **1 Finger Up (Index)**: Draw mode.
  - **2 Fingers Up (Index + Middle)**: Selection mode (hover over buttons to select colors or tools without drawing).
  - **Fist / All Fingers Down**: Stop drawing (pause).
- **Virtual Canvas**: Draw on a transparent overlay with smooth, anti-aliased lines.
- **Tools**: Color palette (including eraser) and adjustable brush thickness.
- **Undo / Redo**: Easily fix mistakes.
- **Save Output**: Export your masterpiece as an image.
- **Advanced OCR & TTS**: Recognize text written on the screen and read it aloud!

## Setup Instructions

### Prerequisites
- Python 3.7+
- A webcam
- **Tesseract OCR**: Required for the OCR feature. 
  - **Mac**: `brew install tesseract`
  - **Windows**: Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and ensure the executable is in your system PATH.
  - **Linux**: `sudo apt install tesseract-ocr`

### Installation
1. Clone this repository or download the files.
2. Navigate to the project directory:
   ```bash
   cd "airscript minor project"
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
Run the main script to launch the application:
```bash
python main.py
```

#### Keyboard Shortcuts:
- `S`: Save canvas to `assets/` folder.
- `U`: Undo the last stroke.
- `R`: Redo the last undone stroke.
- `C`: Capture canvas and perform OCR (Optical Character Recognition) to read the text.
- `T`: Perform Text-To-Speech (reads aloud the text currently on canvas).
- `Q`: Quit the application.

## How It Works (Algorithm Flow)
1. **Frame Capture**: OpenCV captures the video feed from the webcam.
2. **Hand Tracking**: MediaPipe processes each frame, detecting the hand landmarks in 3D space.
3. **Gesture Recognition**: We calculate which fingers are extended based on the relative y-coordinates of the finger tips and their corresponding lower joints.
4. **Coordinate Mapping**: The index fingertip's coordinate is mapped to the screen. 
5. **Drawing & Smoothing**: When in "Draw" mode, we draw a line connecting the previous frame's fingertip coordinate to the current one.
6. **Overlay**: The separate drawing canvas is merged with the webcam feed and the UI elements to create a seamless augmented reality experience.

## Real-Life Applications
- **Interactive Education**: Teachers can draw diagrams or write notes virtually while looking directly at their students via webcam.
- **Accessibility**: Hands-free digital writing for individuals who struggle with using a traditional mouse or keyboard.
- **Signage and Public Displays**: Touchless interaction with public kiosks.
- **AR/VR Integration**: Core technology for writing notes in spatial computing environments.

## Future Scope
- **Multi-hand Support**: Allow drawing with both hands simultaneously.
- **Advanced Gestures**: Detect specific shapes (circles, squares) and auto-correct them.
- **Sign Language Recognition**: Integrate deep learning models to recognize entire sign language phrases, not just drawing lines.
- **Cloud Sync**: Save drawn notes directly to Google Drive or Evernote.

## Interview Questions & Answers

**Q1: Why did you choose MediaPipe over Haar Cascades for hand tracking?**
*A1:* MediaPipe provides robust 3D landmark tracking out-of-the-box using advanced machine learning models (BlazePalm and Hand Landmark Model), which is significantly faster and more accurate for articulated objects like hands compared to Haar Cascades, which primarily detect rigid objects.

**Q2: How do you handle the "shakiness" when drawing in the air?**
*A2:* The shakiness is reduced by drawing thick lines and potentially applying a simple low-pass filter or moving average to the coordinates over the last few frames, smoothing out sudden high-frequency jumps in the finger tracking. (Note: standard implementation relies on the inherent smoothness of MediaPipe's tracking combined with appropriate brush thickness).

**Q3: How does the OCR feature work on handwritten air text?**
*A3:* We use Tesseract OCR. We first isolate the drawing canvas (which has high contrast since it's on a pure black background), optionally apply morphological operations (dilation/erosion) to make the text clearer, and then pass it to `pytesseract` to extract the string.
