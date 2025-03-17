import cv2
import numpy as np
import requests
import time
import threading  # Import threading for parallel processing

# ESP32 address
esp32_address = "http://192.168.10.5"  # Replace with your ESP32's IP address

# DroidCam IP-based camera address (replace with your DroidCam URL)
camera_url = "http://192.168.10.3:4747/video"  # Update with your DroidCam stream URL

# Known corner angles
corner_angles = {
    "left_bottom": (107, 105),
    "right_bottom": (68, 105),
    "right_top": (68, 69),
    "left_top": (110, 71),
}

# Known pixel coordinates for the corners (replace with actual values)
corner_pixels = {
    "left_bottom": (0, 480),
    "right_bottom": (640, 480),
    "right_top": (640, 0),
    "left_top": (0, 0),
}

# Function to interpolate joint angles based on pixel coordinates
def pixel_to_angles(x, y):
    x_ratio = x / 640
    y_ratio = y / 480

    top_base = corner_angles["left_top"][0] + x_ratio * (
        corner_angles["right_top"][0] - corner_angles["left_top"][0]
    )
    bottom_base = corner_angles["left_bottom"][0] + x_ratio * (
        corner_angles["right_bottom"][0] - corner_angles["left_bottom"][0]
    )
    base_angle = bottom_base + y_ratio * (top_base - bottom_base)

    top_joint = corner_angles["left_top"][1] + x_ratio * (
        corner_angles["right_top"][1] - corner_angles["left_top"][1]
    )
    bottom_joint = corner_angles["left_bottom"][1] + x_ratio * (
        corner_angles["right_bottom"][1] - corner_angles["left_bottom"][1]
    )
    joint_angle = bottom_joint + y_ratio * (top_joint - bottom_joint)

    return int(round(base_angle)), int(round(joint_angle))


# Function to move servos to specific angles
def move_servos_in_sequence():
    hardcoded_movements = [(90, 90), (84, 81), (93, 77)]
    for base, joint in hardcoded_movements:
        print(f"Moving to angles Base: {base}, Joint: {joint}")
        try:
            response = requests.get(
                f"{esp32_address}/set?base={base}&joint={joint}"
            )
            if response.status_code == 200:
                print("Servo angles updated successfully.")
            else:
                print(f"Failed to update servo angles. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending data to ESP32: {e}")
        time.sleep(10)  # Wait for 10 seconds between movements


# Function to display the camera feed
def display_camera():
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("Error: Could not open IP camera stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Simulate 3.2x zoom by cropping the center of the frame
        frame_height, frame_width = frame.shape[:2]
        crop_x1 = int((frame_width - frame_width / 3.2) / 2)
        crop_x2 = int((frame_width + frame_width / 3.2) / 2)
        crop_y1 = int((frame_height - frame_height / 3.2) / 2)
        crop_y2 = int((frame_height + frame_height / 3.2) / 2)
        frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]

        # Resize the frame for consistent processing
        frame = cv2.resize(frame, (640, 480))

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian Blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use adaptive thresholding to detect black dots
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Perform morphological operations to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

        # Find contours of detected objects
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 500:
                x, y, w, h = cv2.boundingRect(contour)
                dot_center = (x + w // 2, y + h // 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"Dot ({dot_center[0]}, {dot_center[1]})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

        # Display debugging windows
        cv2.imshow("Captured Image with Dots", frame)
        cv2.imshow("Binary Output", binary)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# Start threads for camera display and servo movements
camera_thread = threading.Thread(target=display_camera)
servo_thread = threading.Thread(target=move_servos_in_sequence)

camera_thread.start()
servo_thread.start()

# Wait for both threads to finish
camera_thread.join()
servo_thread.join()

print("Finished all operations.")
