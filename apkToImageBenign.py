import zipfile
import os
import numpy as np
import cv2
from androguard.core.bytecodes.apk import APK

def get_package_name(apk_path):
    """
    Extract the package name from the APK.
    """
    try:
        apk = APK(apk_path)
        return apk.get_package()
    except Exception as e:
        print(f"Error extracting package name from {apk_path}: {e}")
        return None

def extract_apk(apk_path, output_dir):
    """
    Extract APK contents (DEX files) manually without apktool.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(apk_path, 'r') as zip_ref:
        dex_files = [file for file in zip_ref.namelist() if file.endswith('.dex')]
        
        for dex_file in dex_files:
            zip_ref.extract(dex_file, output_dir)
    
    return dex_files

def visualize_dex_as_bitmap(dex_path, output_image_path):
    """
    Visualize the binary content of the DEX file as a bitmap.
    """
    with open(dex_path, 'rb') as file:
        dex_data = file.read()

    byte_data = np.frombuffer(dex_data, dtype=np.uint8)
    size = len(byte_data)
    side_length = int(np.ceil(np.sqrt(size)))
    
    byte_data = np.pad(byte_data, (0, side_length**2 - size), 'constant')
    byte_data = np.reshape(byte_data, (side_length, side_length))

    cv2.imwrite(output_image_path, byte_data)
    print(f"Saved: {output_image_path}")

def process_apks_in_folder(apk_folder, output_folder):
    """
    Process all APKs, extract DEX, visualize as bitmap, and rename using package name.
    """
    apk_files = [f for f in os.listdir(apk_folder) if f.endswith('.apk')]

    for apk_file in apk_files:
        apk_path = os.path.join(apk_folder, apk_file)
        package_name = get_package_name(apk_path)

        if not package_name:
            print(f"Skipping {apk_file} due to missing package name.")
            continue

        output_dir = os.path.join(output_folder, package_name)
        dex_files = extract_apk(apk_path, output_dir)

        for i, dex_file in enumerate(dex_files, start=1):
            dex_path = os.path.join(output_dir, dex_file)
            image_output_path = os.path.join(output_dir, f"{package_name}_dex{i}.png")
            visualize_dex_as_bitmap(dex_path, image_output_path)

if __name__ == "__main__":
    apk_folder = 'benign_apks'
    output_folder = 'output_images'
    
    process_apks_in_folder(apk_folder, output_folder)
