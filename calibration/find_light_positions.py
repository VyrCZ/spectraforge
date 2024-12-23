import cv2
import numpy as np
import os
# Directory for images and output file
image_paths = [
    "images/front/",
    "images/right/",
    "images/back/",
    "images/left/"
]
selected_view = 0
output_file = "coordinates.txt"
center = (354, 880)
led = 0

# Initialize global variables
coordinates = [
    [0, 0, 0] for i in range(200)
]
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        for i, line in enumerate(f):
            pos = line.strip().split(",")
            coordinates[i] = [int(pos[0]), int(pos[1]), int(pos[2])]

current_point = (-1, -1)
current_coordinates = [0, 0, 0]

# Mouse callback function to update the point
def mouse_callback(event, x, y, flags, param):
    global current_point, current_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        current_point = (x, y)
        current_coordinates = edit_pos(current_coordinates, image_to_world(current_point, selected_view))

def image_to_world(pos, view) -> list[int, int, int]:
    # Convert pixel coordinates to world coordinates
    x, y = pos
    if view == 0:
        return [x - center[0], y - center[1], None]
    elif view == 1:
        return [None, y - center[1], x - center[0]]
    elif view == 2:
        return [center[0] - x, y - center[1], None]
    elif view == 3:
        return [None, y - center[1], center[0] - x]
    
def world_to_image(pos: list[int, int, int], view: int) -> list[int, int]:
    # Convert world coordinates to pixel coordinates
    x, y, z = pos
    if view == 0:
        return [x + center[0], y + center[1]]
    elif view == 1:
        return [z + center[0], y + center[1]]
    elif view == 2:
        return [center[0] - x, y + center[1]]
    elif view == 3:
        return [center[0] - z, y + center[1]]

def edit_pos(old_pos: list[int, int, int], new_pos: list[int, int, int]) -> list[int, int, int]:
    return_pos = old_pos.copy()
    for i in range(3):
        if new_pos[i] is not None:
            return_pos[i] = new_pos[i]
    return return_pos

# Load images and process them
led_setup = True
while led < 200:
    if led_setup:
        led_setup = False

        if coordinates[led] == [0, 0, 0]:
            image_front = cv2.imread(f"{image_paths[0]}{led}.jpg")
            image_right = cv2.imread(f"{image_paths[1]}{led}.jpg")
            if image_front is None or image_right is None:
                print(f"Image {image_path} not found.")
                led += 1
                continue

            # Estimate using brightest pixel
            brightest_pixels = []
            for i in range(4):
                gray_image = cv2.cvtColor(cv2.imread(f"{image_paths[i]}{led}.jpg"), cv2.COLOR_BGR2GRAY)
                brightest_pixels.append(cv2.minMaxLoc(gray_image))
            # x, y from front
            if brightest_pixels[0][1] > brightest_pixels[2][1]:
                current_point = brightest_pixels[0][3]
                current_coordinates = image_to_world(current_point, 0)
            else:
                current_point = brightest_pixels[2][3]
                current_coordinates = image_to_world(current_point, 2)
            
            # z from right
            if brightest_pixels[1][1] > brightest_pixels[3][1]:
                current_coordinates[2] = image_to_world(brightest_pixels[1][3], 1)[2]
            else:
                current_coordinates[2] = image_to_world(brightest_pixels[3][3], 3)[2]

        

    image_path = f"{image_paths[selected_view]}{led}.jpg"
    image = cv2.imread(image_path)
    # Create a window and set mouse callback
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouse_callback)

    while True:
        # Display the image with the current point marked
        display_image = image.copy()
        cv2.putText(display_image, f"View {selected_view}", (10, 30), 0, 1, (255, 255, 255), 2)
        cv2.putText(display_image, f"Pos: {current_coordinates}", (10, 60), 0, 1, (255, 255, 255), 2)
        cv2.circle(display_image, center, 3, (0, 255, 0), -1)
        cv2.circle(display_image, world_to_image(current_coordinates, selected_view), 5, (0, 0, 255), -1)

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
        elif key == 2424832:  # Left arrow key
            selected_view = (selected_view - 1) % 4
            break
            
        elif key == 2555904:  # Right arrow key
            selected_view = (selected_view + 1) % 4
            break

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
        f.write(f"{point[0]},{point[1]},{point[2]}\n".encode())

cv2.destroyAllWindows()
print(f"Coordinates saved to {output_file}")
