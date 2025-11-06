import mediapipe as mp
import cv2
import numpy as np
import pyautogui
import sys
import time

# Initialization safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def init_camera():
    """Initialize camera with multiple attempts and different backends"""
    backends = [cv2.CAP_AVFOUNDATION]  # MacOS-specific backend
    
    for backend in backends:
        print(f"Trying camera with backend {backend}")
        cap = cv2.VideoCapture(0, backend)
        
        if cap is None or not cap.isOpened():
            print(f"Failed to open camera with backend {backend}")
            continue
            
        # Try to read a test frame
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Successfully initialized camera")
            return cap
            
        cap.release()
    
    raise RuntimeError("Failed to initialize camera with any backend")

def main():
    try:
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        print(f"Screen dimensions: {screen_width}x{screen_height}")
        
        # Initialize MediaPipe
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        
        print("Initializing camera...")
        cap = init_camera()
        
        # Read one frame to get dimensions
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Could not read initial frame")
            
        # Set frame size
        frame_height, frame_width = frame.shape[:2]
        print(f"Frame size: {frame_width}x{frame_height}")
        
        # Define ROI (Region of Interest)
        left = int(frame_width * 0.2)
        right = int(frame_width * 0.8)
        top = int(frame_height * 0.2)
        bottom = int(frame_height * 0.8)
        
        # Initialize hand detection
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        print("Starting main loop...")
        
        # Initialize click states
        is_left_clicked = False
        is_right_clicked = False
        click_start_time = None
        click_duration = 0.2  # 0.2 seconds for a click
        click_threshold = 0.1  # 0.1 distance threshold for click
        right_click_threshold = 0.1  # distance threshold for right-click

        # Help text
        help_text = [
            "Gestures:",
            "- Bring thumb and index finger close to left click",
            "- Bring thumb and ring finger close to right click",
            "- Move hand to control cursor",
            "Press ESC to exit"
        ]
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to read frame")
                break
                
            # Basic frame processing
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            results = hands.process(rgb_frame)
            
            # Draw ROI
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Display help text
            y = 30
            for text in help_text:
                cv2.putText(frame, text, (10, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y += 25
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Get wrist for cursor control (changed from using average of wrist and middle finger)
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    
                    # Use only wrist position for cursor control
                    cursor_x = int(wrist.x * frame_width)
                    cursor_y = int(wrist.y * frame_height)

                    if left <= cursor_x <= right and top <= cursor_y <= bottom:
                        screen_x = (cursor_x - left) / (right - left) * screen_width
                        screen_y = (cursor_y - top) / (bottom - top) * screen_height

                        try:
                            pyautogui.moveTo(
                                int(screen_x),
                                int(screen_y),
                                duration=0.1,
                                _pause=False
                            )
                        except pyautogui.FailSafeException:
                            print("FailSafe triggered - mouse in corner")

                    # Check for left click gesture
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    distance = np.linalg.norm([thumb_tip.x - index_finger_tip.x, thumb_tip.y - index_finger_tip.y])

                    if distance < click_threshold and not is_left_clicked:
                        print("Left click detected")
                        is_left_clicked = True
                        click_start_time = time.time()
                        pyautogui.click(button='left')
                    elif is_left_clicked and time.time() - click_start_time > click_duration:
                        is_left_clicked = False

                    # Check for right click gesture
                    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    distance_right_click = np.linalg.norm([thumb_tip.x - ring_tip.x, thumb_tip.y - ring_tip.y])

                    if distance_right_click < right_click_threshold and not is_right_clicked:
                        print("Right click detected")
                        is_right_clicked = True
                        click_start_time = time.time()
                        pyautogui.click(button='right')
                    elif is_right_clicked and time.time() - click_start_time > click_duration:
                        is_right_clicked = False

            # Display frame
            cv2.imshow('Hand Gesture Control', frame)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                print("ESC pressed, exiting...")
                break
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("Cleaning up...")
        try:
            cap.release()
            cv2.destroyAllWindows()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    print(f"OpenCV version: {cv2.__version__}")
    print(f"Python version: {sys.version}")
    main()
