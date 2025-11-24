# 🚀 Virtual Gesture Studio (Advanced Air Painter)

Welcome to **Virtual Gesture Studio**! This is an advanced computer vision application that transforms your webcam into an interactive digital canvas. Forget your mouse and keyboard draw, design, and manage your artwork using only hand gestures.

This project leverages **OpenCV** for real-time image processing and **Google MediaPipe** for precise 21-point hand landmark detection, supporting intuitive two-hand control.

---

## ✨ Key Features

### 🎨 Dual-Hand Control

* **Left Hand**: Acts as the *Tool Palette* (mode selection).
* **Right Hand**: Acts as the *Brush* (for drawing).

### 🧠 Smart Mode System

| Mode       | Description                                      |
| ---------- | ------------------------------------------------ |
| **DRAW**   | Freestyle drawing on the canvas.                 |
| **SHAPE**  | Instantly draw rectangles.                       |
| **PICKER** | Opens a 15-color palette for selection.          |
| **CURSOR** | Idle mode for moving the cursor without drawing. |

### 🖼️ Full Canvas Management

* **Undo**: Revert up to 10 recent actions (canvas history).
* **Clear**: Wipe the entire canvas (hold 1 second for confirmation).
* **Save**: Save your artwork to the *HasilKarya/* folder (hold 1 second).

### 🖌️ Dynamic Brush & Eraser

* **Brush Size**: Adjust dynamically by changing the distance between your right-hand index and pinky fingers.
* **Eraser**: Dedicated UI button for a large eraser mode.

### 💡 Interactive UI (Header)

* Displays current mode (IDLE, DRAW, SHAPE, etc.).
* Shows active color preview.
* Displays brush size (SIZE).
* Temporary notifications (e.g., *“SAVED!”*).

---

## 🛠️ Technologies Used

* **Python 3.x**
* **OpenCV (opencv-python)**
* **MediaPipe (mediapipe)**
* **NumPy**

---

## ⚙️ Installation & Usage Guide

### 1️⃣ Initial Setup

Ensure Python 3.8+ is installed.

Clone this repository:

```bash
git clone https://github.com/ahnafyura/AirDrawing.git
cd AirDrawing
```

### 2️⃣ Create Virtual Environment

Using a virtual environment is recommended for dependency isolation.

```bash
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install opencv-python mediapipe numpy
```

### 4️⃣ Run the Application

Make sure your Python file is named `app.py` (or adjust the command):

```bash
python your_file_name.py
```

The app will open a webcam window — you’re ready to paint with your hands!

---

## 🖐️ Gesture Control Guide

### 🫱 Left Hand (Controller / Tool Palette)

| Gesture                         | Mode       | Action                         |
| ------------------------------- | ---------- | ------------------------------ |
| 3 Fingers (Index, Middle, Ring) | **PICKER** | Opens 15-color palette.        |
| 4 Fingers (All except Thumb)    | **UNDO**   | Reverts last stroke.           |
| 5 Fingers (Palm Open)           | **CLEAR**  | Hold 1 second to clear canvas. |
| Thumb Up                        | **SAVE**   | Hold 1 second to save artwork. |

### ✋ Right Hand (Action / Brush)

| Gesture                         | Mode          | Action                                          |
| ------------------------------- | ------------- | ----------------------------------------------- |
| 1 Finger (Index)                | **DRAW**      | Draw/erase on canvas.                           |
| “Spiderman” (Index + Pinky)     | **SHAPE**     | Draw rectangle between start/end points.        |
| “Peace” Closed (Index + Middle) | **CURSOR**    | Move cursor without drawing.                    |
| Pinch (Thumb + Index)           | **SELECTION** | Point to “ERASER” button to enable eraser mode. |

### 🌍 Global Controls

* **Brush Size**: Adjust using distance between right-hand Index & Pinky.
* **Exit**: Press **S** on your keyboard.

---

## 📜 License

This project is licensed under the **MIT License**.
