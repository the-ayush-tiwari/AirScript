import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np
import mediapipe as mp

st.set_page_config(page_title="AirScript Live", layout="wide")
st.title("AirScript - Touchless Air Writing")
st.markdown(
    "Index finger se hawa me likhein. Middle finger uthaane par drawing pause hogi."
)

# Sidebar controls
st.sidebar.title("Controls")
brush_color = st.sidebar.color_picker("Brush Color", "#00FFFF")
# Convert HEX to BGR for OpenCV
bgr_color = tuple(int(brush_color.lstrip("#")[i : i + 2], 16) for i in (4, 2, 0))
brush_size = st.sidebar.slider("Brush Size", 2, 20, 6)

if st.sidebar.button("Clear Canvas"):
    st.session_state["clear_canvas"] = True
else:
    st.session_state["clear_canvas"] = False


class AirScriptProcessor(VideoProcessorBase):
    def __init__(self):
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0
        # Model initialization
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        if self.canvas is None or self.canvas.shape[:2] != (h, w):
            self.canvas = np.zeros((h, w, 3), np.uint8)

        if st.session_state.get("clear_canvas", False):
            self.canvas = np.zeros((h, w, 3), np.uint8)
            st.session_state["clear_canvas"] = False

        # Lightweight processing: convert to RGB for MediaPipe
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        rgb_img.flags.writeable = False
        results = self.hands.process(rgb_img)
        rgb_img.flags.writeable = True

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # Fingertip coordinates
                x8 = int(hand_landmarks.landmark[8].x * w)
                y8 = int(hand_landmarks.landmark[8].y * h)
                x12 = int(hand_landmarks.landmark[12].x * w)
                y12 = int(hand_landmarks.landmark[12].y * h)

                # Drawing condition: Index finger tip (8) is higher than Middle finger tip (12)
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

        # Merge canvas with webcam frame
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, self.canvas)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# Resolution limits prevent freezing and frame dropping on Cloud instances
webrtc_streamer(
    key="airscript-live-stream",
    video_processor_factory=AirScriptProcessor,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
    media_stream_constraints={
        "video": {
            "width": {"ideal": 640},
            "height": {"ideal": 480},
            "frameRate": {"ideal": 24},
        },
        "audio": False,
    },
    async_processing=True,
)
