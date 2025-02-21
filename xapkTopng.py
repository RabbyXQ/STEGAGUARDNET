import zipfile
import os
import numpy as np
import cv2
from androguard.core.bytecodes.apk import APK

def get_package_name(apk_path):
    """
    Extract the package name from the APK or XPK.
    """
    try:
        apk = APK(apk_path)
        return apk.get_package()
    except Exception as e:
        print(f"Error extracting package name from {apk_path}: {e}")
        return None

def extract_apk(apk_path, output_dir):
    """
    Extract APK/XPK contents (DEX files) manually without apktool.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isfile(apk_path):
        print(f"Error: The file '{apk_path}' does not exist.")
        return []

    try:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            dex_files = [file for file in zip_ref.namelist() if file.endswith('.dex')]

            for dex_file in dex_files:
                zip_ref.extract(dex_file, output_dir)
        
        return dex_files
    except zipfile.BadZipFile:
        print(f"Error: '{apk_path}' is not a valid ZIP file. Skipping it.")
        return []

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
    Process all APK/XPKs, extract DEX, visualize as bitmap, and rename using package name or APK name.
    Avoid processing the same APK/XPK multiple times.
    """
    apk_files = [f for f in os.listdir(apk_folder) if f.endswith('.apk') or f.endswith('.xpk') or not os.path.splitext(f)[1]]
    processed_files = set()  # Track processed APK/XPK files to avoid duplicates

    for apk_file in apk_files:
        # Treat files without extensions as .apk
        if not os.path.splitext(apk_file)[1]:
            apk_file = apk_file + '.apk'
        
        apk_path = os.path.join(apk_folder, apk_file)
        
        # Check if the APK/XPK file has been processed already
        if apk_file in processed_files:
            print(f"Skipping already processed file: {apk_file}")
            continue

        print(f"Processing APK/XPK: {apk_path}")

        # Get package name or use APK filename if package name is missing
        package_name = get_package_name(apk_path)
        if not package_name:
            package_name = os.path.splitext(apk_file)[0]
            print(f"Using APK/XPK file name '{package_name}' as package name.")

        output_dir = os.path.join(output_folder, package_name)
        dex_files = extract_apk(apk_path, output_dir)

        for i, dex_file in enumerate(dex_files, start=1):
            dex_path = os.path.join(output_dir, dex_file)
            image_output_path = os.path.join(output_dir, f"{package_name}_dex{i}.png")
            visualize_dex_as_bitmap(dex_path, image_output_path)

        # Mark this APK/XPK as processed
        processed_files.add(apk_file)

if __name__ == "__main__":
    apk_folder = '/Volumes/Shared/rabbyx/Adware'  # Update with your folder path
    output_folder = '/Volumes/Shared/rabbyx/Adware/adware_images'  # Update with your desired output path
    
    process_apks_in_folder(apk_folder, output_folder)
