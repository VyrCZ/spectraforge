import os
from PIL import Image
from pathlib import Path

def rotate_images_in_folder(input_folder, rotation_angle=-90):
    """Rotate all images in a folder and its subfolders by the specified angle."""
    
    supported_formats = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
    
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if Path(file).suffix.lower() in supported_formats:
                image_path = os.path.join(root, file)
                try:
                    image = Image.open(image_path)
                    rotated_image = image.rotate(rotation_angle, expand=True)
                    rotated_image.save(image_path)
                    print(f"Rotated: {image_path}")
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")


if __name__ == "__main__":
    input_folder = "calibration/images/little_tree"
    
    if os.path.isdir(input_folder):
        rotate_images_in_folder(input_folder)
        print("Image rotation complete!")
    else:
        print("Invalid folder path.")