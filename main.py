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
        left = int(frame_width * 0.01)
        right = int(frame_width * 0.99)
        top = int(frame_height * 0.01)
        bottom = int(frame_height * 0.99)
        
        # Initialize hand detection - now detect up to 2 hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Changed to detect 2 hands
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
            "- Right hand: Move index finger to control cursor",
            "- Left hand: Thumb+Index finger close = Left click",
            "- Left hand: Thumb+Ring finger close = Right click",
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
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Get hand label (Left or Right)
                    hand_label = handedness.classification[0].label
                    
                    if hand_label == "Right":  # Right hand controls cursor movement
                        # Use index finger tip for cursor control
                        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        
                        cursor_x = int(index_finger_tip.x * frame_width)
                        cursor_y = int(index_finger_tip.y * frame_height)

                        # Draw cursor position indicator
                        cv2.circle(frame, (cursor_x, cursor_y), 10, (0, 0, 255), -1)
                        cv2.putText(frame, "Cursor", (cursor_x + 15, cursor_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

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
                    
                    elif hand_label == "Left":  # Left hand handles clicks
                        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                        
                        # Check for left click gesture (thumb + index finger)
                        distance_left_click = np.linalg.norm([thumb_tip.x - index_finger_tip.x, thumb_tip.y - index_finger_tip.y])
                        
                        if distance_left_click < click_threshold and not is_left_clicked:
                            print("Left click detected")
                            is_left_clicked = True
                            click_start_time = time.time()
                            pyautogui.click(button='left')
                        elif is_left_clicked and time.time() - click_start_time > click_duration:
                            is_left_clicked = False

                        # Check for right click gesture (thumb + ring finger)
                        distance_right_click = np.linalg.norm([thumb_tip.x - ring_tip.x, thumb_tip.y - ring_tip.y])

                        if distance_right_click < right_click_threshold and not is_right_clicked:
                            print("Right click detected")
                            is_right_clicked = True
                            click_start_time = time.time()
                            pyautogui.click(button='right')
                        elif is_right_clicked and time.time() - click_start_time > click_duration:
                            is_right_clicked = False
                        
                        # Visual feedback for left hand gestures
                        thumb_pos = (int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height))
                        index_pos = (int(index_finger_tip.x * frame_width), int(index_finger_tip.y * frame_height))
                        ring_pos = (int(ring_tip.x * frame_width), int(ring_tip.y * frame_height))
                        
                        # Draw lines to show gesture distances
                        cv2.line(frame, thumb_pos, index_pos, (255, 0, 0), 2)  # Blue for left click
                        cv2.line(frame, thumb_pos, ring_pos, (0, 255, 255), 2)  # Yellow for right click
                        
                        # Show click states
                        if is_left_clicked:
                            cv2.putText(frame, "LEFT CLICK", (10, frame_height - 60), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                        if is_right_clicked:
                            cv2.putText(frame, "RIGHT CLICK", (10, frame_height - 30), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

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
