import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np
import mediapipe as mp

st.set_page_config(page_title="AirScript Live", layout="wide")
st.title("AirScript - Touchless Air Writing")
st.markdown("""
**Gestures Guide:**
- ☝️ **Sirf Index Finger khuli:** Drawing Mode (Likhega).
- ✌️ **Index + Middle dono khuli:** Selection Mode (Toolbar se Color, Brush Size ya Clear select karein).
- ✊ **Mutthi band (All fingers down):** Quick Clear (Canvas saaf karein).
""")

RTC_CONFIG = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:global.stun.twilio.com:3478"]},
        ]
    }
)


class AirScriptProcessor(VideoProcessorBase):
    def __init__(self):
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0

        # Colors: Blue, Green, Red, Yellow, Orange
        self.colors = [
            (255, 0, 0),  # Blue (BGR)
            (0, 255, 0),  # Green
            (0, 0, 255),  # Red
            (0, 255, 255),  # Yellow
            (0, 165, 255),  # Orange
        ]
        self.color_index = 0
        self.brush_size = 6

        # Optimized MediaPipe for Cloud CPU (Fastest latency)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,  # 0 is the fastest model for cloud
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        if self.canvas is None or self.canvas.shape[:2] != (h, w):
            self.canvas = np.zeros((h, w, 3), np.uint8)

        # Draw On-Screen Interactive Toolbar
        # Top bar background
        cv2.rectangle(img, (0, 0), (w, 65), (25, 25, 25), -1)
        cv2.line(img, (0, 65), (w, 65), (70, 70, 70), 2)

        # Color boxes
        for i, col in enumerate(self.colors):
            x1 = 20 + (i * 55)
            cv2.rectangle(img, (x1, 10), (x1 + 45, 55), col, -1)
            if i == self.color_index:
                cv2.rectangle(img, (x1 - 2, 8), (x1 + 47, 57), (255, 255, 255), 2)

        # Size Buttons: [-] and [+]
        cv2.rectangle(img, (310, 10), (355, 55), (45, 45, 45), -1)
        cv2.putText(
            img, "-", (325, 42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )

        cv2.rectangle(img, (365, 10), (410, 55), (45, 45, 45), -1)
        cv2.putText(
            img, "+", (378, 42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )

        # Size display
        cv2.putText(
            img,
            f"Size: {self.brush_size}",
            (420, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (200, 200, 200),
            2,
        )

        # Clear Button
        cv2.rectangle(img, (w - 110, 10), (w - 15, 55), (0, 0, 180), -1)
        cv2.putText(
            img,
            "CLEAR",
            (w - 98, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Lightweight AI Inference (320px downscale for 3x FPS boost)
        small_img = cv2.resize(img, (320, 240))
        rgb_small = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)
        rgb_small.flags.writeable = False
        results = self.hands.process(rgb_small)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                lm = hand_landmarks.landmark
                # Fingertip coordinates
                x8, y8 = int(lm[8].x * w), int(lm[8].y * h)  # Index tip
                x12, y12 = int(lm[12].x * w), int(lm[12].y * h)  # Middle tip

                # Finger states (Up vs Down)
                index_up = lm[8].y < lm[6].y
                middle_up = lm[12].y < lm[10].y
                ring_up = lm[16].y < lm[14].y
                pinky_up = lm[20].y < lm[18].y

                # Gesture 1: FIST (Sabhi ungliya band) -> Instant Clear Canvas
                if not index_up and not middle_up and not ring_up and not pinky_up:
                    self.canvas = np.zeros((h, w, 3), np.uint8)
                    cv2.putText(
                        img,
                        "CANVAS CLEARED",
                        (w // 2 - 120, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3,
                    )
                    self.prev_x, self.prev_y = 0, 0

                # Gesture 2: SELECTION MODE (Index + Middle dono upar)
                elif index_up and middle_up:
                    self.prev_x, self.prev_y = 0, 0
                    cv2.circle(img, (x8, y8), 8, (255, 255, 255), cv2.FILLED)

                    # Toolbar interactions
                    if y8 < 65:
                        # Color selection
                        for i in range(len(self.colors)):
                            x1 = 20 + (i * 55)
                            if x1 <= x8 <= x1 + 45:
                                self.color_index = i

                        # Brush Size [-]
                        if 310 <= x8 <= 355:
                            if self.brush_size > 2:
                                self.brush_size -= 1
                                cv2.waitKey(100)

                        # Brush Size [+]
                        if 365 <= x8 <= 410:
                            if self.brush_size < 30:
                                self.brush_size += 1
                                cv2.waitKey(100)

                        # Clear Button
                        if (w - 110) <= x8 <= (w - 15):
                            self.canvas = np.zeros((h, w, 3), np.uint8)

                # Gesture 3: DRAWING MODE (Sirf Index upar, baki niche)
                elif index_up and not middle_up:
                    current_color = self.colors[self.color_index]
                    cv2.circle(
                        img,
                        (x8, y8),
                        self.brush_size // 2 + 2,
                        current_color,
                        cv2.FILLED,
                    )

                    if y8 > 65:  # Toolbar ke niche draw karein
                        if self.prev_x == 0 and self.prev_y == 0:
                            self.prev_x, self.prev_y = x8, y8
                        cv2.line(
                            self.canvas,
                            (self.prev_x, self.prev_y),
                            (x8, y8),
                            current_color,
                            self.brush_size,
                        )
                        self.prev_x, self.prev_y = x8, y8
                    else:
                        self.prev_x, self.prev_y = 0, 0
                else:
                    self.prev_x, self.prev_y = 0, 0
        else:
            self.prev_x, self.prev_y = 0, 0

        # Fast bitwise merge
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
        inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, inv)
        img = cv2.bitwise_or(img, self.canvas)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="airscript-interactive-stream",
    video_processor_factory=AirScriptProcessor,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 640},
            "height": {"ideal": 480},
            "frameRate": {"ideal": 30},
        },
        "audio": False,
    },
    async_processing=True,
)
