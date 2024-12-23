import socket
import time
import cv2 as cv
import os

# Networking setup
HOST = "192.168.1.69"  # Change to the server's IP if running on a different device
PORT = 65432

# Number of LEDs
NUM_LEDS = 200

# Ensure the directory for saving images exists
os.makedirs("images/left", exist_ok=True)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Initialize the camera
        camera = cv.VideoCapture(0)
        if not camera.isOpened():
            raise Exception("Could not open video device")

        # Allow the camera to warm up
        time.sleep(5)

        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        for i in range(NUM_LEDS):
            # Send the LED index to the server
            client_socket.sendall(str(i).encode())
            print(f"Sent index: {i}")

            time.sleep(0.5)  # Delay for any necessary processing or effects

            # Capture a frame
            result, image = camera.read()
            if not result or image is None:
                print(f"Failed to capture image for index {i}")
                continue

            # Save the captured image
            save_path = f"images/left/{i}.jpg"
            cv.imwrite(save_path, image)
            print(f"Saved frame {i} to {save_path}")

            # Display the frame
            cv.imshow("Frame", image)
            cv.waitKey(1)  # Display the image for a brief moment

        # Release the camera resource
        camera.release()
        cv.destroyAllWindows()
except Exception as e:
    print(f"An error occurred: {e}")
