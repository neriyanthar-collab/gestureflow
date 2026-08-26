import time
import cv2
import mediapipe as mp
import numpy as np
import pyautogui

CAM_INDEX = 0             #change if you have multiple cameras
FRAME_W, FRAME_H = 640, 480
FRAME_MARGIN = 100            
SMOOTHING = 5                     
CLICK_DISTANCE_THRESHOLD = 40    
SHOW_CAMERA_WINDOW = True         
pyautogui.FAILSAFE = False    
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

        frame = cv2.flip(frame, 1)
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

           
            x = np.interp(index_tip[0], (FRAME_MARGIN, FRAME_W - FRAME_MARGIN), (0, SCREEN_W))
            y = np.interp(index_tip[1], (FRAME_MARGIN, FRAME_H - FRAME_MARGIN), (0, SCREEN_H))

          
            curr_x = prev_x + (x - prev_x) / SMOOTHING
            curr_y = prev_y + (y - prev_y) / SMOOTHING
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

           
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
