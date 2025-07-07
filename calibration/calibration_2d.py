import cv2
import numpy as np
import os
# Directory for images and output file
image_path = "calibration/images/the_wall/"
output_file = "coordinates.txt"
center = (354, 880)
led = 0

# Initialize global variables
coordinates = [
    [0, 0] for i in range(200)
]
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        for i, line in enumerate(f):
            pos = line.strip().split(",")
            coordinates[i] = [int(pos[0]), int(pos[1])]

current_point = (-1, -1)
current_coordinates = [0, 0]

# Mouse callback function to update the point
def mouse_callback(event, x, y, flags, param):
    global current_point, current_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        current_point = (x, y)
        current_coordinates = image_to_world(current_point)

def image_to_world(pos) -> list[int, int]:
    # Convert pixel coordinates to world coordinates
    x, y = pos
    return [x - center[0], y - center[1]]
    
def world_to_image(pos: list[int, int]) -> list[int, int]:
    # Convert world coordinates to pixel coordinates
    x, y = pos
    return [x + center[0], y + center[1]]

# Load images and process them
led_setup = True
while led < 200:
    if led_setup:
        led_setup = False

        if coordinates[led] == [0, 0]:
            image_file = f"{image_path}{led}.png"
            image = cv2.imread(image_file)
            if image is None:
                print(f"Image {image_file} not found.")
                led += 1
                continue

            # Estimate using brightest pixel
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _minVal, _maxVal, _minLoc, maxLoc = cv2.minMaxLoc(gray_image)
            current_point = maxLoc
            current_coordinates = image_to_world(current_point)
        

    image_file = f"{image_path}{led}.png"
    image = cv2.imread(image_file)
    # Create a window and set mouse callback
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)

    while True:
        # Display the image with the current point marked
        display_image = image.copy()
        cv2.putText(display_image, f"Pos: {current_coordinates}", (10, 60), 0, 1, (255, 255, 255), 2)
        cv2.circle(display_image, center, 3, (0, 255, 0), -1)
        cv2.circle(display_image, world_to_image(current_coordinates), 5, (0, 0, 255), -1)

        cv2.imshow(f"Image", display_image)
        key = cv2.waitKeyEx(1)

        # Press Enter to save the point and move to the next image
        if key == 13:  # Enter key
            coordinates[led] = current_coordinates
            print(f"Coordinates {current_coordinates} saved for image {led}")
            led += 1
            led_setup = True
            break

        # Press 'r' to reset the point to the brightest pixel
        elif key == ord('r'):
            led_setup = True
            break

        # Press 'q' to quit early
        elif key == 113:
            break

    # Quit the loop early if 'q' is pressed
    if key == 113:
        break

# Save coordinates to a file
with open(output_file, "wb") as f:
    for point in coordinates:
        f.write(f"{point[0]},{point[1]}\n".encode())

cv2.destroyAllWindows()
print(f"Coordinates saved to {output_file}")
