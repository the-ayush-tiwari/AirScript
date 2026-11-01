import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_draw

st.set_page_config(page_title="AirScript Live", layout="wide")
st.title("AirScript - Touchless Air Writing")
st.markdown("Apna webcam start karein aur hawa me ungli se likhein.")

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)


class AirScriptTransformer(VideoTransformerBase):
    def __init__(self):
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, c = img.shape

        if self.canvas is None:
            self.canvas = np.zeros((h, w, 3), np.uint8)

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Index finger tip (id: 8)
                x = int(hand_landmarks.landmark[8].x * w)
                y = int(hand_landmarks.landmark[8].y * h)

                # Middle finger tip (id: 12)
                x_mid = int(hand_landmarks.landmark[12].x * w)
                y_mid = int(hand_landmarks.landmark[12].y * h)

                # Drawing mode: index up, middle down
                if y < y_mid:
                    if self.prev_x == 0 and self.prev_y == 0:
                        self.prev_x, self.prev_y = x, y
                    cv2.line(
                        self.canvas,
                        (self.prev_x, self.prev_y),
                        (x, y),
                        (0, 255, 255),
                        6,
                    )
                    self.prev_x, self.prev_y = x, y
                else:
                    self.prev_x, self.prev_y = 0, 0

        # Merge canvas with webcam feed
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 20, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, self.canvas)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_streamer(
    key="airscript-stream",
    video_transformer_factory=AirScriptTransformer,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)
