import os
import subprocess
from shutil import which

import cv2

from .utils import rotate_360_image


def process_image(image_path, auto_adjust, pitch, yaw, roll, quality=95, compression=1):

    if which("exiftool") is None:
        print(
            "ExifTool is not installed or not found in PATH. Please install it before proceeding."
        )
        quit()

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error loading image {image_path}")
        return

    process = subprocess.run(["exiftool", "-csv", "-XMP-GPano:PosePitchDegrees", "-XMP-GPano:PoseHeadingDegrees", "-XMP-GPano:PoseRollDegrees", image_path], text=True, capture_output=True, check=True)
    pitchyawroll = map(float, process.stdout.replace("\n","").split(",")[4:7])
    if auto_adjust:
        pitch, yaw, roll = [-1 * item for item in pitchyawroll]
        newpitch = 0
        newyaw = 0
        newroll = 0        
    else:
        oldpitch, oldyaw, oldroll = pitchyawroll
        newpitch  = round(pitch + oldpitch, 1)
        newyaw = round(yaw + oldyaw, 1)
        newroll = round(roll + oldroll, 1)     
            
    rotated_img = rotate_360_image(img, pitch, yaw, roll)

    # Extract file extension
    file_extension = os.path.splitext(image_path)[-1]#.lower()
    save_path = os.path.join('ajusted', os.path.split(image_path)[1])
    #save_path = os.path.splitext(image_path)[0] + "_adjusted" + file_extension

    # Ensure high-quality saving
    if file_extension.lower() in [".jpg", ".jpeg"]:
        cv2.imwrite(save_path, rotated_img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif file_extension.lower() in [".png"]:
        cv2.imwrite(save_path, rotated_img, [cv2.IMWRITE_PNG_COMPRESSION, compression])
    else:
        cv2.imwrite(save_path, rotated_img)

    subprocess.run(["exiftool", "-TagsFromFile", image_path, save_path], check=True)
    os.remove(f"{save_path}_original")
    subprocess.run(["exiftool", "-overwrite_original", "-XMP-GPano:PosePitchDegrees=" + str(newpitch), "-XMP-GPano:PoseHeadingDegrees=" + str(newyaw), "-XMP-GPano:PoseRollDegrees=" + str(newroll), save_path], check=True)

    print(
        f"Image saved as {save_path} with JPEG quality of {quality} and PNG compression of {compression}!"
    )
