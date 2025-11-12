# hawaAi

Lightweight hand-gesture mouse controller using MediaPipe, OpenCV and PyAutoGUI.

## Summary
main.py captures webcam input, detects up to 2 hands using MediaPipe, and provides intuitive mouse control:
- **Right hand**: Controls cursor movement using index finger tip position within a configurable Region of Interest (ROI)
- **Left hand**: Handles click gestures:
  - Left click: bring thumb and index finger tips close
  - Right click: bring thumb and ring finger tips close
- Press ESC in the camera window to exit

## Prerequisites
- Python 3.7+
- Working webcam
- macOS recommended (script uses CAP_AVFOUNDATION by default), but Linux/Windows may work with backend changes
- On macOS: grant Camera and Accessibility permissions to your Terminal/IDE to use the camera and control the mouse

## Required Python packages
- mediapipe
- opencv-python
- numpy
- pyautogui

## Exact install commands (recommended)
Open a terminal in the project directory:
```bash
cd /Users/surajrathor/Desktop/hawaAi

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Update pip and install packages
pip install --upgrade pip
pip install mediapipe opencv-python numpy pyautogui
```

If any package fails to install, follow platform-specific instructions for mediapipe or OpenCV (e.g., system libraries on Linux).

## Run the app
With the virtual environment activated:
```bash
python3 main.py
```
A window titled "Hand Gesture Control" will appear with the camera feed, a green ROI rectangle, landmark drawing, and help text.

## What main.py does (quick)
- Initializes camera (tries CAP_AVFOUNDATION on macOS).
- Starts MediaPipe Hands with max_num_hands=2 to detect both hands.
- Uses the **right hand's index finger tip** as the cursor control point.
- Uses the **left hand** for click gestures by measuring distances between specific landmarks.
- Maps cursor position from ROI to your screen using pyautogui.moveTo.
- Detects clicks by measuring distances between landmarks on the left hand:
  - Left click: THUMB_TIP ↔ INDEX_FINGER_TIP
  - Right click: THUMB_TIP ↔ RING_FINGER_TIP
- Debounces clicks with a short click_duration to avoid repeated clicks.

## Variables you can tune in main.py
Open main.py and edit values near the start of main() or top-level configuration section:
- ROI (percentages used to compute pixel coordinates):
  - left/right/top/bottom multipliers (currently 0.01 and 0.99 of frame size for nearly full screen)
- click_threshold — float (e.g., 0.08–0.15) distance threshold for left click
- right_click_threshold — float (e.g., 0.08–0.15) threshold for right click
- click_duration — seconds (e.g., 0.15–0.3) debounce time
- max_num_hands — int (currently 2 to detect both hands)
- min_detection_confidence / min_tracking_confidence — floats to trade accuracy vs performance
- pyautogui.FAILSAFE — True/False (default True; moving mouse to screen corner raises FailSafeException)
- Camera backend list in init_camera() — modify for other OS/backends if needed

Example places to edit:
- ROI lines:
  left = int(frame_width * 0.01)
  right = int(frame_width * 0.99)
  top = int(frame_height * 0.01)
  bottom = int(frame_height * 0.99)
- Click and threshold variables:
  click_duration = 0.2
  click_threshold = 0.1
  right_click_threshold = 0.1

## Gesture mapping (details)
- **Cursor movement** (Right hand):
  - Index finger tip landmark (HandLandmark.INDEX_FINGER_TIP) is used. When the index finger is inside the green ROI, its x/y coordinates are converted to pixel coordinates and mapped linearly to your screen resolution.
  - A red circle indicates the current cursor control position.
- **Left click** (Left hand):
  - If Euclidean distance between THUMB_TIP and INDEX_FINGER_TIP < click_threshold and not currently "clicked", perform pyautogui.click(button='left') and start debounce timer.
  - Visual feedback: blue line connects thumb and index finger, "LEFT CLICK" text appears.
- **Right click** (Left hand):
  - If Euclidean distance between THUMB_TIP and RING_FINGER_TIP < right_click_threshold and not currently "clicked", perform pyautogui.click(button='right') and start debounce timer.
  - Visual feedback: yellow line connects thumb and ring finger, "RIGHT CLICK" text appears.
- **Exit**:
  - Press ESC in the OpenCV window to exit cleanly.

## macOS permissions and notes
- Camera access: System Preferences → Security & Privacy → Privacy → Camera → add Terminal/IDE
- Accessibility (mouse control): System Preferences → Security & Privacy → Privacy → Accessibility → add Terminal/IDE
- If camera fails to initialize:
  - Ensure permissions granted and camera not used by other apps
  - Try running from a different Terminal or change backend in init_camera()
- PyAutoGUI FAILSAFE: enabled by default; move mouse to a screen corner to abort automated control (safer during testing).

## Troubleshooting
- "Failed to initialize camera": camera index in use, missing permissions, or wrong backend. Try granting permissions, closing other apps, or modifying init_camera() to try other cv2 backends.
- "Could not read initial frame": verify camera is accessible and try different device index.
- "FailSafe triggered - mouse in corner": move the cursor away or temporarily set pyautogui.FAILSAFE = False (not recommended).
- Low detection accuracy: increase detection/tracking confidence, improve lighting and background contrast, hold hands facing camera.
- Cursor jitter / sensitivity: increase ROI size, smooth movements (increase pyautogui.moveTo duration), or apply simple low-pass filter to mapped coordinates.
- High CPU usage: reduce camera resolution, lower MediaPipe confidence thresholds, or process every Nth frame.
- Hand recognition issues: ensure both hands are clearly visible and properly oriented towards the camera.

## Tips for best results
- Use good lighting and a plain background.
- Keep both hands roughly facing the camera.
- **Right hand**: Use for cursor control, keep index finger extended and visible within the ROI.
- **Left hand**: Use for clicks, make deliberate gestures bringing thumb close to index finger (left click) or ring finger (right click).
- Tune thresholds gradually while observing gesture reliability.
- Keep pyautogui.PAUSE small (or 0) for snappy responses, but a small pause can stabilize behavior.
- The ROI is set to nearly full screen (1% margins) for maximum control area.

## Safety & privacy
- The script controls your mouse. Test carefully and be ready to regain control (keyboard shortcuts, move mouse to corner to trigger PyAutoGUI failsafe).
- Remove accessibility permissions when not using the app if desired.
- Start with larger click thresholds to avoid accidental clicks while learning the gestures.

## Example quick start (summary)
1. cd /Users/surajrathor/Desktop/hawaAi
2. python3 -m venv .venv && source .venv/bin/activate
3. pip install mediapipe opencv-python numpy pyautogui
4. python3 main.py
5. Grant Camera and Accessibility permissions on macOS when prompted
6. Use right hand index finger to control cursor, left hand for clicks

## License
MIT License — use and modify as needed.
