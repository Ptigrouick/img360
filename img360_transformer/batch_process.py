import os
import subprocess
from shutil import which

import cv2

from .utils import rotate_360_image


def process_image(image_path, auto_adjust, pitch, yaw, roll, quality=95, compression=1):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading image {image_path}")
        return

    if auto_adjust:
        if which("exiftool") is not None:
            process = subprocess.run(["exiftool", "-csv", "-XMP-GPano:PosePitchDegrees", "-XMP-GPano:PoseHeadingDegrees", "-XMP-GPano:PoseRollDegrees", image_path], text=True, capture_output=True, check=True)
            pitchyawroll = map(float, process.stdout.replace("\n","").split(",")[4:7])
            pitch, yaw, roll = [-1 * item for item in pitchyawroll]          
        else:
            print(
                "ExifTool is not installed or not found in PATH. Can't use --auto-adjust option."
            )
            quit()
        
            
    rotated_img = rotate_360_image(img, pitch, yaw, roll)

    # Extract file extension
    file_extension = os.path.splitext(image_path)[-1]#.lower()
    save_path = os.path.join('ajusted',os.path.split(image_path)[1])
    #save_path = os.path.splitext(image_path)[0] + "_adjusted" + file_extension

    # Ensure high-quality saving
    if file_extension.lower() in [".jpg", ".jpeg"]:
        cv2.imwrite(save_path, rotated_img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif file_extension.lower() in [".png"]:
        cv2.imwrite(save_path, rotated_img, [cv2.IMWRITE_PNG_COMPRESSION, compression])
    else:
        cv2.imwrite(save_path, rotated_img)

    if which("exiftool") is not None:
        subprocess.run(["exiftool", "-TagsFromFile", image_path, save_path], check=True)
        os.remove(f"{save_path}_original")
        if auto_adjust:
            subprocess.run(["exiftool", "-overwrite_original", "-XMP-GPano:PosePitchDegrees=0", "-XMP-GPano:PoseHeadingDegrees=0", "-XMP-GPano:PoseRollDegrees=0", save_path], check=True)
    else:
        print(
            "ExifTool is not installed or not found in PATH. Image metadata will not be copied."
        )

    print(
        f"Image saved as {save_path} with JPEG quality of {quality} and PNG compression of {compression}!"
    )
