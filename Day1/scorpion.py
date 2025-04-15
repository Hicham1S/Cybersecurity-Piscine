import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

def get_file_metadata(file_path):
    try:
        stat_info = os.stat(file_path)
        size = stat_info.st_size
        created_time = datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        return size, created_time
    except Exception as e:
        return None, None

def get_exif_data(img):
    exif_data = {}
    info = img._getexif()

    if info:
        for tag, value in info.items():
            tag_name = TAGS.get(tag, tag)
            exif_data[tag_name] = value
    return exif_data

def process_image(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"[✖] Skipping unsupported file: {file_path}")
        return

    if not os.path.exists(file_path):
        print(f"[✖] File does not exist: {file_path}")
        return

    print(f"\n File: {file_path}")

    size, created = get_file_metadata(file_path)
    if size is not None:
        print(f"   - Size: {round(size / 1024, 2)} KB")
        print(f"   - Created: {created}")

    try:
        with Image.open(file_path) as img:
            print(f"   - Format: {img.format}")
            print(f"   - Mode: {img.mode}")
            print(f"   - Dimensions: {img.size[0]} x {img.size[1]}")

            if hasattr(img, '_getexif'):
                exif = get_exif_data(img)
                if exif:
                    print("   - EXIF Data:")
                    for key, value in exif.items():
                        print(f"       • {key}: {value}")
                else:
                    print("   - EXIF Data: None")
            else:
                print("   - EXIF not supported for this format.")
    except Exception as e:
        print(f"   [!] Failed to process image: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scorpion.py FILE1 [FILE2 ...]")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        process_image(file_path)

if __name__ == "__main__":
    main()
