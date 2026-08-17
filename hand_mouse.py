"""
Hand Gesture Mouse Control
---------------------------
Move your index finger to move the cursor. Pinch your thumb and index
finger together to click/drag. Release the pinch to let go. Press 'q'
in the camera window to quit.

Tune the constants below to your camera, lighting, and hand size.
"""

import time

import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# ---------------- Configuration ----------------
CAM_INDEX = 0                    # change if you have multiple cameras
FRAME_W, FRAME_H = 640, 480
FRAME_MARGIN = 100                # pixels of camera frame ignored at edges
                                   # (keeps you from having to reach the physical
                                   # edge of frame to reach the edge of the screen)
SMOOTHING = 5                      # higher = smoother cursor, more lag
CLICK_DISTANCE_THRESHOLD = 40      # pixels; distance between thumb+index tip to count as a pinch
SHOW_CAMERA_WINDOW = True          # set False to run without a visible preview

pyautogui.FAILSAFE = False         # disable pyautogui's corner-abort safety
                                    # (re-enable if you want a manual kill-switch:
                                    #  yanking mouse to a screen corner aborts)
SCREEN_W, SCREEN_H = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)

cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

if not cap.isOpened():
    raise RuntimeError(
        f"Could not open camera index {CAM_INDEX}. Check that no other app is "
        "using the camera and that camera permissions are granted."
    )

prev_x, prev_y = 0.0, 0.0
is_dragging = False


def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # mirror so movement feels natural
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        hand_detected = bool(result.multi_hand_landmarks)

        if hand_detected:
            hand_landmarks = result.multi_hand_landmarks[0]
            if SHOW_CAMERA_WINDOW:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            lm = hand_landmarks.landmark

            index_tip = (int(lm[8].x * w), int(lm[8].y * h))
            thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))

            # Map index fingertip position (inside the margin box) to screen coords
            x = np.interp(index_tip[0], (FRAME_MARGIN, FRAME_W - FRAME_MARGIN), (0, SCREEN_W))
            y = np.interp(index_tip[1], (FRAME_MARGIN, FRAME_H - FRAME_MARGIN), (0, SCREEN_H))

            # Exponential smoothing to cut down on jitter
            curr_x = prev_x + (x - prev_x) / SMOOTHING
            curr_y = prev_y + (y - prev_y) / SMOOTHING
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Pinch = mouse down. Holding + moving = drag. Releasing = mouse up.
            # A quick pinch/release therefore acts as a plain click.
            pinch_dist = distance(index_tip, thumb_tip)
            if pinch_dist < CLICK_DISTANCE_THRESHOLD:
                if not is_dragging:
                    pyautogui.mouseDown()
                    is_dragging = True
                if SHOW_CAMERA_WINDOW:
                    cv2.circle(frame, index_tip, 15, (0, 255, 0), cv2.FILLED)
            else:
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False

            if SHOW_CAMERA_WINDOW:
                cv2.rectangle(
                    frame,
                    (FRAME_MARGIN, FRAME_MARGIN),
                    (FRAME_W - FRAME_MARGIN, FRAME_H - FRAME_MARGIN),
                    (255, 0, 255),
                    2,
                )
        else:
            # Hand left the frame — don't leave the mouse button stuck down
            if is_dragging:
                pyautogui.mouseUp()
                is_dragging = False

        if SHOW_CAMERA_WINDOW:
            cv2.imshow("Hand Mouse Control (press q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    if is_dragging:
        pyautogui.mouseUp()
    cap.release()
    cv2.destroyAllWindows()
