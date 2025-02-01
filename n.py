import hashlib
import os
import base64
import subprocess
import xml.etree.ElementTree as ET
import math
import chardet
import csv
from zipfile import ZipFile
from androguard.core.bytecodes.apk import APK  # Import Androguard to extract the package name

# Directory containing APKs
apk_directory = "apks"
output_directory = "output_folder"
csv_file = "obfuscation_analysis.csv"

csv_columns = ['package_name', 'file_resource', 'obfuscation_flag', 'entropy']

def write_to_csv(data):
    """Writes detection data to CSV."""
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def extract_package_name(apk_path):
    """Extracts the package name from the APK file using Androguard."""
    try:
        apk = APK(apk_path)
        return apk.get_package()
    except Exception as e:
        print(f"Error extracting package name: {e}")
        return "Unknown"

def calculate_entropy(data):
    """Calculates the entropy of a given data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    byte_freq = [0] * 256
    for byte in data:
        byte_freq[byte] += 1
    entropy = -sum((freq / len(data)) * math.log2(freq / len(data)) for freq in byte_freq if freq > 0)
    return entropy

def get_certificate_fingerprint(apk_path):
    try:
        with ZipFile(apk_path) as zip_file:
            for file_name in zip_file.namelist():
                if file_name.lower().endswith('cert') or file_name.lower().endswith('sf'):
                    cert_data = zip_file.read(file_name)
                    cert_entropy = calculate_entropy(cert_data)
                    obfuscation_flag = "Yes" if cert_entropy > 7.5 else "No"
                    package_name = extract_package_name(apk_path)
                    write_to_csv([package_name, file_name, obfuscation_flag, cert_entropy])
                    return hashlib.sha256(cert_data).hexdigest()
    except Exception as e:
        print(f"Error processing certificate: {e}")
    return None

def extract_manifest(apk_path):
    try:
        with ZipFile(apk_path) as zip_file:
            for file_name in zip_file.namelist():
                if file_name.lower() == 'androidmanifest.xml':
                    return zip_file.read(file_name).decode(errors='ignore')
    except Exception as e:
        print(f"Error extracting manifest: {e}")
    return None

def detect_obfuscated_manifest(apk_path):
    manifest_data = extract_manifest(apk_path)
    if manifest_data:
        manifest_entropy = calculate_entropy(manifest_data)
        obfuscation_flag = "Yes" if manifest_entropy > 7.5 else "No"
        package_name = extract_package_name(apk_path)
        write_to_csv([package_name, 'AndroidManifest.xml', obfuscation_flag, manifest_entropy])

def decompile_apk(apk_path):
    try:
        subprocess.run(['apktool', 'd', apk_path, '-o', output_directory, '-f'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error decompiling APK: {e}")

def detect_smali_obfuscation(apk_path):
    decompile_apk(apk_path)
    for root, _, files in os.walk(output_directory):
        for file in files:
            if file.endswith('.smali'):
                with open(os.path.join(root, file), 'r', errors='ignore') as f:
                    content = f.read()
                    file_entropy = calculate_entropy(content)
                    obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
                    package_name = extract_package_name(apk_path)
                    write_to_csv([package_name, file, obfuscation_flag, file_entropy])

def analyze_java_code(apk_path):
    java_output_dir = os.path.join(output_directory, "jadx_output")
    try:
        subprocess.run(['jadx', '-d', java_output_dir, apk_path], check=True)
        for root, _, files in os.walk(java_output_dir):
            for file in files:
                if file.endswith('.java'):
                    with open(os.path.join(root, file), 'r', errors='ignore') as f:
                        content = f.read()
                        file_entropy = calculate_entropy(content)
                        obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
                        package_name = extract_package_name(apk_path)
                        write_to_csv([package_name, file, obfuscation_flag, file_entropy])
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing Java code with JADX: {e}")

def analyze_apk(apk_path):
    print(f"Processing: {apk_path}")
    package_name = extract_package_name(apk_path)
    print(f"Package Name: {package_name}")
    get_certificate_fingerprint(apk_path)
    detect_obfuscated_manifest(apk_path)
    detect_smali_obfuscation(apk_path)
    analyze_java_code(apk_path)
    cleanup()
    os.remove(apk_path)  # Remove the APK file after processing
    print(f"Deleted {apk_path} after processing.")

def cleanup():
    """Removes all generated output files."""
    if os.path.exists(output_directory):
        subprocess.run(['rm', '-rf', output_directory], check=True)
    print("Cleaned up generated files.")

if __name__ == '__main__':
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_columns)
    
    if not os.path.exists(apk_directory):
        print(f"APK directory '{apk_directory}' not found.")
    else:
        for apk_file in os.listdir(apk_directory):
            if apk_file.endswith('.apk'):
                analyze_apk(os.path.join(apk_directory, apk_file))
