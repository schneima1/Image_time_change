"""
This script adjusts the EXIF timestamp of images in a specified folder. e.g. if the time of your camera is set incorrectly, you can adjust the timestamps of all images taken by that camera by selecting the correct time difference.
It is useful to first test it with only a single image by changing the `folder_path` variable to point to a single image file, e.g. images_test.
"""

import piexif
from PIL import Image
import os
from datetime import datetime, timedelta

def adjust_timestamp(img_path, delta, tz_offset=None):
    img = Image.open(img_path)
    exif_dict = piexif.load(img_path)

    original_time = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
    if not original_time:
        print(f"No DateTimeOriginal found in {img_path}")
        return

    # Check and print existing time zone offset
    existing_offset = exif_dict["Exif"].get(piexif.ExifIFD.OffsetTimeOriginal)
    if existing_offset:
        print(f"Existing time zone offset for {os.path.basename(img_path)}: {existing_offset.decode('utf-8')}")
    else:
        print(f"No time zone offset found in {os.path.basename(img_path)}")

    # Convert from bytes to string, then to datetime object
    original_time_str = original_time.decode("utf-8")
    original_dt = datetime.strptime(original_time_str, "%Y:%m:%d %H:%M:%S")
    new_dt = original_dt + delta
    new_time_str = new_dt.strftime("%Y:%m:%d %H:%M:%S").encode("utf-8")

    # Update all relevant fields
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = new_time_str
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_time_str
    exif_dict["0th"][piexif.ImageIFD.DateTime] = new_time_str

    # Set time zone offset if provided
    if tz_offset is not None:
        offset_str = f"{tz_offset:+03.0f}:00".encode("utf-8")
        exif_dict["Exif"][piexif.ExifIFD.OffsetTimeOriginal] = offset_str
        exif_dict["Exif"][piexif.ExifIFD.OffsetTimeDigitized] = offset_str

    exif_bytes = piexif.dump(exif_dict)
    img.save(img_path, exif=exif_bytes)
    print(f"Updated timestamp for {os.path.basename(img_path)}")

def get_user_input():
    print("Image Timestamp Adjuster")
    print("=" * 30)
    
    folder_path = input("Enter the folder path containing images (or image file): ").strip()
    if not folder_path:
        folder_path = "images"
    
    try:
        hours = int(input("Enter hours to add/subtract (positive to add, negative to subtract): ").strip() or "0")
    except ValueError:
        hours = 0
    
    try:
        minutes = int(input("Enter minutes to add/subtract: ").strip() or "0")
    except ValueError:
        minutes = 0
    
    tz_choice = input("Do you want to set a time zone offset? (y/n): ").strip().lower()
    tz_offset = None
    if tz_choice == 'y':
        try:
            tz_offset = int(input("Enter time zone offset in hours from UTC (e.g., +10 for AEST): ").strip())
        except ValueError:
            tz_offset = None
    
    return folder_path, timedelta(hours=hours, minutes=minutes), tz_offset

if __name__ == "__main__":
    folder_path, time_delta, tz_offset = get_user_input()

    # Ensure the folder/file exists
    if not os.path.exists(folder_path):
        print(f"Path {folder_path} does not exist.")
        exit(1)

    # If it's a file, process just that file
    if os.path.isfile(folder_path):
        if folder_path.lower().endswith((".jpg", ".jpeg")):
            adjust_timestamp(folder_path, time_delta, tz_offset)
        else:
            print("File must be a JPG or JPEG image.")
    else:
        # Process all JPG/JPEG files in the folder
        files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg"))]
        if not files:
            print("No JPG/JPEG files found in the folder.")
            exit(1)
        
        for filename in files:
            adjust_timestamp(os.path.join(folder_path, filename), time_delta, tz_offset)
    
    print("Done!")
