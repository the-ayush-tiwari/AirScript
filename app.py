import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np
import mediapipe as mp

st.set_page_config(page_title="AirScript Live", layout="wide")
st.title("AirScript - Touchless Air Writing")
st.markdown(
    "Niche **START** par click karke camera allow karein. Index finger se hawa me draw karein."
)

# Sidebar controls
st.sidebar.title("Controls")
brush_color = st.sidebar.color_picker("Brush Color", "#00FFFF")
bgr_color = tuple(int(brush_color.lstrip("#")[i : i + 2], 16) for i in (4, 2, 0))
brush_size = st.sidebar.slider("Brush Size", 2, 20, 6)

# Multiple reliable STUN servers for WebRTC handshake
RTC_CONFIG = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {"urls": ["stun:global.stun.twilio.com:3478"]},
        ]
    }
)


class AirScriptProcessor(VideoProcessorBase):
    def __init__(self):
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
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

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # Index tip (8) and Middle tip (12)
                x8 = int(hand_landmarks.landmark[8].x * w)
                y8 = int(hand_landmarks.landmark[8].y * h)
                y12 = int(hand_landmarks.landmark[12].y * h)

                # Draw when index is higher than middle
                if y8 < y12:
                    if self.prev_x == 0 and self.prev_y == 0:
                        self.prev_x, self.prev_y = x8, y8
                    cv2.line(
                        self.canvas,
                        (self.prev_x, self.prev_y),
                        (x8, y8),
                        bgr_color,
                        brush_size,
                    )
                    self.prev_x, self.prev_y = x8, y8
                else:
                    self.prev_x, self.prev_y = 0, 0
        else:
            self.prev_x, self.prev_y = 0, 0

        # Merge canvas
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
        inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, inv)
        img = cv2.bitwise_or(img, self.canvas)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="airscript-streamer-v2",
    video_processor_factory=AirScriptProcessor,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
