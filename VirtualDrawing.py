import cv2
import numpy as np
import mediapipe as mp
import math
import time
import os

class VirtualStudioApp:

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, max_num_hands=2)
        self.mp_draw = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280) 
        self.cap.set(4, 720)

        self.current_mode = "IDLE" 
        self.previous_mode = "IDLE"
        self.draw_color = (0, 255, 0)
        self.brush_thickness = 15
        self.eraser_thickness = 100
        self.show_color_palette = False
        self.shape_start_point = None
        self.prev_x, self.prev_y = 0, 0
        self.eraser_button_rect = (1080, 10, 1260, 90)

        self.gesture_hold_start_time = 0
        self.current_gesture = None
        self.GESTURE_HOLD_DURATION = 1.0

        self.canvas = np.zeros((720, 1280, 3), np.uint8)
        self.canvas_history = []
        self._save_canvas_state()

        if not os.path.exists("HasilKarya"):
            os.makedirs("HasilKarya")
        
        # Inisialisasi UI
        self._create_color_palette()

    def _create_color_palette(self):
        """Membuat gambar palet warna dan peta lokasinya."""
        self.palette_width, self.palette_height, self.box_size = 400, 150, 50
        self.palette = np.zeros((self.palette_height, self.palette_width, 3), np.uint8)
        self.color_map = {}
        colors = [
            (0, 0, 255), (0, 128, 255), (0, 255, 255), (0, 255, 128), (0, 255, 0),
            (128, 255, 0), (255, 255, 0), (255, 128, 0), (255, 0, 0), (255, 0, 128),
            (255, 0, 255), (128, 0, 255), (255, 255, 255), (128, 128, 128), (0, 0, 0)
        ]
        rows, cols = self.palette_height // self.box_size, self.palette_width // self.box_size
        for r in range(rows):
            for c in range(cols):
                color_idx = (r * cols + c) % len(colors)
                x1, y1, x2, y2 = c * self.box_size, r * self.box_size, (c+1) * self.box_size, (r+1) * self.box_size
                cv2.rectangle(self.palette, (x1, y1), (x2, y2), colors[color_idx], -1)
                self.color_map[(x1, y1, x2, y2)] = colors[color_idx]

    def _save_canvas_state(self):
        """Menyimpan kondisi kanvas saat ini untuk fitur Undo."""
        if len(self.canvas_history) > 10: self.canvas_history.pop(0)
        self.canvas_history.append(self.canvas.copy())

    def _process_one_hand_gestures(self, hand_data):
        """Memproses semua gestur jika hanya satu tangan yang terdeteksi."""
        num_fingers_up = hand_data['num_fingers_up']
        fingers_up = hand_data['fingers_up']
        fingers = hand_data['positions']
        
        new_mode = "IDLE" 
        
        if num_fingers_up == 4: new_mode = "UNDO"
        elif num_fingers_up == 5: new_mode = "CLEAR"
        elif fingers_up == [1, 0, 0, 0, 0]: new_mode = "SAVE"
        elif fingers_up == [0, 1, 1, 1, 0]: new_mode = "PICKER"
        else: 
            dist_select = math.hypot(fingers['index'][0] - fingers['thumb'][0], fingers['index'][1] - fingers['thumb'][1])
            if dist_select < 40: 
                ix, iy = fingers['index']
                ex1, ey1, ex2, ey2 = self.eraser_button_rect
                if ex1 < ix < ex2 and ey1 < iy < ey2:
                    self.draw_color = (0, 0, 0)
                    self.temp_message = ("ERASER SELECTED", time.time() + 1)
            elif fingers_up == [0, 1, 0, 0, 1]: new_mode = "SHAPE"
            elif fingers_up == [0, 1, 0, 0, 0]: new_mode = "DRAW"
            else:
                dist_idle = math.hypot(fingers['index'][0] - fingers['middle'][0], fingers['index'][1] - fingers['middle'][1])
                if dist_idle < 40: new_mode = "CURSOR"
        
        return new_mode

    def _process_two_hand_gestures(self, right_hand_data, left_hand_data):
        """Memproses gestur jika dua tangan terdeteksi (peran terpisah)."""
        new_mode = "IDLE"
        if left_hand_data:
            num_fingers_up = left_hand_data['num_fingers_up']
            fingers_up = left_hand_data['fingers_up']
            if num_fingers_up == 4: new_mode = "UNDO"
            elif num_fingers_up == 5: new_mode = "CLEAR"
            elif fingers_up == [1, 0, 0, 0, 0]: new_mode = "SAVE"
            elif fingers_up == [0, 1, 1, 1, 0]: new_mode = "PICKER"

        if right_hand_data and new_mode == "IDLE":
            fingers = right_hand_data['positions']
            fingers_up = right_hand_data['fingers_up']
            dist_select = math.hypot(fingers['index'][0] - fingers['thumb'][0], fingers['index'][1] - fingers['thumb'][1])
            if dist_select < 40:
                ix, iy = fingers['index']
                ex1, ey1, ex2, ey2 = self.eraser_button_rect
                if ex1 < ix < ex2 and ey1 < iy < ey2:
                    self.draw_color = (0, 0, 0)
                    self.temp_message = ("ERASER SELECTED", time.time() + 1)
            elif fingers_up == [0, 1, 0, 0, 1]: new_mode = "SHAPE"
            elif fingers_up == [0, 1, 0, 0, 0]: new_mode = "DRAW"
            else:
                dist_idle = math.hypot(fingers['index'][0] - fingers['middle'][0], fingers['index'][1] - fingers['middle'][1])
                if dist_idle < 40: new_mode = "CURSOR"
        return new_mode

    def run(self):
        while True:
            success, frame = self.cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            all_hands_data = []
            if results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    h, w, c = frame.shape
                    all_lm = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
                    self._draw_custom_landmarks(frame, all_lm)
                    
                    hand_label = results.multi_handedness[i].classification[0].label
                    
                    fingers = {'thumb': all_lm[4], 'index': all_lm[8], 'middle': all_lm[12], 'ring': all_lm[16], 'pinky': all_lm[20]}
                    fingers_up = []
                    if (hand_label == "Right" and all_lm[4][0] < all_lm[3][0]) or \
                       (hand_label == "Left" and all_lm[4][0] > all_lm[3][0]):
                        fingers_up.append(1)
                    else: fingers_up.append(0)
                    for tip_id in [8, 12, 16, 20]:
                        if all_lm[tip_id][1] < all_lm[tip_id - 2][1]: fingers_up.append(1)
                        else: fingers_up.append(0)
                    
                    hand_data = {
                        'label': hand_label, 'positions': fingers, 
                        'fingers_up': fingers_up, 'num_fingers_up': fingers_up.count(1)
                    }
                    all_hands_data.append(hand_data)
            
            self._process_and_execute_gestures(all_hands_data)

            final_frame = self._draw_ui_and_visuals(frame, all_hands_data)
            cv2.imshow("Virtual Studio Pro", final_frame)
            if cv2.waitKey(1) & 0xFF == ord('s'): break
        
        self.cleanup()

    def _process_and_execute_gestures(self, all_hands_data):
        """Menentukan mode berdasarkan jumlah tangan dan mengeksekusi aksi."""
        num_hands = len(all_hands_data)
        new_mode = "IDLE"
        
        action_hand_data = None

        if num_hands == 1:
            action_hand_data = all_hands_data[0]
            new_mode = self._process_one_hand_gestures(action_hand_data)
            dist = math.hypot(action_hand_data['positions']['index'][0] - action_hand_data['positions']['pinky'][0], 
                              action_hand_data['positions']['index'][1] - action_hand_data['positions']['pinky'][1])
            self.brush_thickness = int(np.interp(dist, [30, 350], [10, 70]))

        elif num_hands == 2:
            right_hand = next((hand for hand in all_hands_data if hand['label'] == "Right"), None)
            left_hand = next((hand for hand in all_hands_data if hand['label'] == "Left"), None)
            action_hand_data = right_hand
            new_mode = self._process_two_hand_gestures(right_hand, left_hand)
            if right_hand:
                dist = math.hypot(right_hand['positions']['index'][0] - right_hand['positions']['pinky'][0], 
                                  right_hand['positions']['index'][1] - right_hand['positions']['pinky'][1])
                self.brush_thickness = int(np.interp(dist, [30, 350], [10, 70]))
        
        self.previous_mode = self.current_mode
        self.current_mode = new_mode

        self._execute_mode_actions(action_hand_data)

    def _execute_mode_actions(self, action_hand_data):
        """Menjalankan fungsi sesuai mode saat ini."""
        if self.current_mode == "UNDO":
            current_time = time.time()
            if current_time - self.last_undo_time > 1.5:
                if len(self.canvas_history) > 1:
                    self.canvas_history.pop(); self.canvas = self.canvas_history[-1].copy()
                self.last_undo_time = current_time
        else: self.last_undo_time = 0

        if self.current_mode in ["CLEAR", "SAVE"]:
            if self.current_gesture != self.current_mode:
                self.current_gesture, self.gesture_hold_start_time = self.current_mode, time.time()
            if time.time() - self.gesture_hold_start_time > self.GESTURE_HOLD_DURATION:
                if self.current_mode == "CLEAR":
                    self.canvas = np.zeros((720, 1280, 3), np.uint8); self._save_canvas_state()
                elif self.current_mode == "SAVE":
                    filename = f"HasilKarya/Karya_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    cv2.imwrite(filename, self.canvas); self.temp_message = ("SAVED!", time.time() + 1)
                self.gesture_hold_start_time = time.time() + 999
        else: self.current_gesture = None

        self.show_color_palette = (self.current_mode == "PICKER")
        
        if self.previous_mode == "DRAW" and self.current_mode != "DRAW": self._save_canvas_state()

        if action_hand_data:
            fingers = action_hand_data['positions']
            if self.current_mode == "PICKER":
                self.prev_x, self.prev_y = 0, 0
                px, py = fingers['index']
                w, h = self.cap.get(3), self.cap.get(4)
                palette_x, palette_y = int((w-self.palette_width)//2), int((h-self.palette_height)//2)
                for (x1,y1,x2,y2), color in self.color_map.items():
                    if (palette_x+x1 < px < palette_x+x2) and (palette_y+y1 < py < palette_y+y2):
                        self.draw_color = color; break
            elif self.current_mode == "SHAPE":
                if self.shape_start_point is None: self.shape_start_point = fingers['index']
                self.preview_shape_end = fingers['index']
            elif self.current_mode == "DRAW":
                if self.prev_x == 0 and self.prev_y == 0: self.prev_x, self.prev_y = fingers['index']
                effective_thickness = self.eraser_thickness if self.draw_color == (0, 0, 0) else self.brush_thickness
                cv2.line(self.canvas, (self.prev_x, self.prev_y), fingers['index'], self.draw_color, effective_thickness)
                self.prev_x, self.prev_y = fingers['index']
            else:
                if self.previous_mode == "SHAPE" and self.shape_start_point:
                    cv2.rectangle(self.canvas, self.shape_start_point, fingers['index'], self.draw_color, cv2.FILLED)
                    self._save_canvas_state()
                self.shape_start_point = None
                self.prev_x, self.prev_y = 0, 0
        else: 
            self.prev_x, self.prev_y = 0, 0
            self.shape_start_point = None

    def _draw_ui_and_visuals(self, frame, all_hands_data):
        """Menggambar semua elemen UI dan feedback visual."""
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, inv_mask)
        frame = cv2.bitwise_or(frame, self.canvas)

        if self.show_color_palette:
            palette_x = (frame.shape[1] - self.palette_width) // 2
            palette_y = (frame.shape[0] - self.palette_height) // 2
            frame[palette_y:palette_y+self.palette_height, palette_x:palette_x+self.palette_width] = self.palette

        action_hand = None
        if len(all_hands_data) == 1: action_hand = all_hands_data[0]
        elif len(all_hands_data) == 2: action_hand = next((h for h in all_hands_data if h['label'] == "Right"), None)
        
        if action_hand:
            fingers = action_hand['positions']
            if self.draw_color == (0, 0, 0):
                pt1 = (fingers['index'][0] - self.eraser_thickness // 2, fingers['index'][1] - self.eraser_thickness // 2)
                pt2 = (fingers['index'][0] + self.eraser_thickness // 2, fingers['index'][1] + self.eraser_thickness // 2)
                cv2.rectangle(frame, pt1, pt2, (255, 255, 255), 2) # Kursor kotak putih
            elif self.current_mode == "CURSOR": cv2.circle(frame, fingers['index'], 10, (255, 255, 255), 2)
            elif self.current_mode == "DRAW": cv2.circle(frame, fingers['index'], self.brush_thickness // 2, self.draw_color, cv2.FILLED)
            elif self.current_mode == "SHAPE" and self.shape_start_point: cv2.rectangle(frame, self.shape_start_point, self.preview_shape_end, self.draw_color, 3)

        if hasattr(self, 'temp_message') and time.time() < self.temp_message[1]:
            cv2.putText(frame, self.temp_message[0], (500, 360), cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 0), 5)
        
        header = np.zeros((100, 1280, 3), np.uint8); header[:] = (100, 100, 100)
        cv2.rectangle(header, (20, 10), (120, 90), self.draw_color, -1)
        cv2.rectangle(header, (20, 10), (120, 90), (255, 255, 255), 3)
        cv2.putText(header, f"MODE: {self.current_mode}", (150, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        cv2.putText(header, f"SIZE: {self.brush_thickness}", (600, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        ex1, ey1, ex2, ey2 = self.eraser_button_rect
        eraser_bg_color = (200, 200, 200) if self.draw_color == (0, 0, 0) else (255, 255, 255)
        cv2.rectangle(header, (ex1, ey1), (ex2, ey2), eraser_bg_color, cv2.FILLED)
        cv2.rectangle(header, (ex1, ey1), (ex2, ey2), (0, 0, 0), 2)
        cv2.putText(header, "ERASER", (ex1 + 15, ey1 + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        frame[0:100, 0:1280] = header
        
        return frame

    def _draw_custom_landmarks(self, frame, landmarks):
        """Menggambar node dan edge kustom."""
        for connection in self.mp_hands.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                cv2.line(frame, landmarks[start_idx], landmarks[end_idx], (255, 255, 255), 2)
        for landmark in landmarks:
            cv2.circle(frame, landmark, 5, (0, 255, 0), -1)
    
    def cleanup(self):
        """Membersihkan resource saat aplikasi ditutup."""
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = VirtualStudioApp()
    app.run()
