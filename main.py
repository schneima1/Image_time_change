"""
This script adjusts the EXIF timestamp of images in a specified folder. e.g. if the time of your camera is set incorrectly, you can adjust the timestamps of all images taken by that camera by selecting the correct time difference.
It is useful to first test it with only a single image by changing the `folder_path` variable to point to a single image file, e.g. images_test.
"""

import piexif
from PIL import Image
import os
from datetime import datetime, timedelta



def adjust_timestamp(img_path, delta):
    img = Image.open(img_path)
    # exif_dict = piexif.load(img.info.get('exif', b''))
    exif_dict = piexif.load(img_path)



    original_time = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
    if not original_time:
        print(f"No DateTimeOriginal found in {img_path}")
        return

    # Convert from bytes to string, then to datetime object
    original_time_str = original_time.decode("utf-8")
    original_dt = datetime.strptime(original_time_str, "%Y:%m:%d %H:%M:%S")
    new_dt = original_dt + delta
    new_time_str = new_dt.strftime("%Y:%m:%d %H:%M:%S").encode("utf-8")

    # Update all relevant fields
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = new_time_str
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_time_str
    exif_dict["0th"][piexif.ImageIFD.DateTime] = new_time_str

    exif_bytes = piexif.dump(exif_dict)
    img.save(img_path, exif=exif_bytes)
    print(f"Updated timestamp for {os.path.basename(img_path)}")


if __name__ == "__main__":

    # Folder containing your images
    folder_path = "images"
    time_delta = timedelta(hours=0, minutes=5)

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        exit(1)

    # Process all JPG/JPEG files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg")):
            adjust_timestamp(os.path.join(folder_path, filename), time_delta)
