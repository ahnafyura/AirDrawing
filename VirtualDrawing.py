import cv2
import numpy as np
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 1280) 
cap.set(4, 720)  

canvas = np.zeros((720, 1280, 3), np.uint8)
prev_x, prev_y = 0, 0
draw_color = (0, 255, 0) 
brush_thickness = 15
eraser_thickness = 100

while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            h, w, c = frame.shape
            ix, iy = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w), int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h)
            tx, ty = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * w), int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * h)
            mx, my = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * w), int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * h)

            dist_select = math.hypot(ix - tx, iy - ty) 
            dist_draw = math.hypot(ix - mx, iy - my)   
            
            
            if dist_select < 40:
                prev_x, prev_y = 0, 0
                
                cx, cy = (ix + tx) // 2, (iy + ty) // 2
                cv2.circle(frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)

                if 0 < ix < 200 and 0 < iy < 100:
                    draw_color = (0, 0, 255) 
                elif 220 < ix < 420 and 0 < iy < 100:
                    draw_color = (0, 255, 0) 
                elif 440 < ix < 640 and 0 < iy < 100:
                    draw_color = (255, 0, 0) 
                elif 1080 < ix < 1280 and 0 < iy < 100:
                    draw_color = (0, 0, 0) 
            
            elif dist_draw < 40:
                current_thickness = eraser_thickness if draw_color == (0, 0, 0) else brush_thickness
                cv2.circle(frame, (ix, iy), 15, draw_color, cv2.FILLED)
                
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = ix, iy
                cv2.line(canvas, (prev_x, prev_y), (ix, iy), draw_color, current_thickness)
                prev_x, prev_y = ix, iy
            else:
                prev_x, prev_y = 0, 0
    else:
        prev_x, prev_y = 0, 0
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, inv_mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
    inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
    
    frame = cv2.bitwise_and(frame, inv_mask)
    frame = cv2.bitwise_or(frame, canvas)

    cv2.rectangle(frame, (0,0), (200,100), (0,0,255), cv2.FILLED)
    cv2.rectangle(frame, (220,0), (420,100), (0,255,0), cv2.FILLED)
    cv2.rectangle(frame, (440,0), (640,100), (255,0,0), cv2.FILLED)
    cv2.rectangle(frame, (1080,0), (1280,100), (255,255,255), cv2.FILLED)
    cv2.putText(frame, "ERASER", (1100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    
    cv2.imshow("Virtual Painter", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('s'):
        break

cap.release()
cv2.destroyAllWindows()
