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

# CSV file setup
csv_file = "obfuscation_analysis.csv"
csv_columns = ['package_name', 'file_resource', 'obfuscation_flag', 'entropy']

def write_to_csv(data):
    """Writes detection data to CSV."""
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def extract_package_name(apk_path):
    """Extracts the package name from the APK file using Androguard."""
    apk = APK(apk_path)  # Load the APK file
    package_name = apk.get_package()  # Extract the package name
    return package_name

def detect_encoding(file_data):
    """Detect the encoding of the given file data."""
    result = chardet.detect(file_data)
    encoding = result['encoding']
    confidence = result['confidence']
    return encoding

# 1. Calculate Entropy
def calculate_entropy(data):
    """Calculates the entropy of a given data."""
    if isinstance(data, str):
        data = data.encode('utf-8')  # Convert string to bytes

    byte_freq = [0] * 256
    for byte in data:
        byte_freq[byte] += 1
    
    entropy = 0
    for freq in byte_freq:
        if freq > 0:
            prob = freq / len(data)
            entropy -= prob * math.log2(prob)
    return entropy

# 2. Certificate Obfuscation Detection and Steganography
def get_certificate_fingerprint(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.lower().endswith('cert') or file_name.lower().endswith('sf'):
                cert_data = zip_file.read(file_name)
                cert_hash = hashlib.sha256(cert_data).hexdigest()
                cert_entropy = calculate_entropy(cert_data)
                obfuscation_flag = "Yes" if cert_entropy > 7.5 else "No"
                package_name = extract_package_name(apk_path)  # Extract package name
                write_to_csv([package_name, file_name, obfuscation_flag, cert_entropy])  # Use package name in CSV
                return cert_hash
    return None

def detect_steganography_certificate_fingerprint(apk_path):
    """Detect steganography in APK certificate fingerprint."""
    cert_hash = get_certificate_fingerprint(apk_path)
    if cert_hash:
        print(f"Certificate fingerprint: {cert_hash}")

# 3. Manifest Extraction and Obfuscation Detection with Steganography
def extract_manifest(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.lower() == 'androidmanifest.xml':
                manifest_data = zip_file.read(file_name)
                try:
                    manifest_data = manifest_data.decode('utf-8')  # Decode the byte data to string
                    return manifest_data
                except UnicodeDecodeError:
                    return None
    return None

def detect_obfuscated_manifest(manifest_data, apk_path):
    if manifest_data is None:
        return False
    manifest_entropy = calculate_entropy(manifest_data.encode('utf-8'))
    obfuscation_flag = "Yes" if manifest_entropy > 7.5 else "No"
    package_name = extract_package_name(apk_path)  # Extract package name
    write_to_csv([package_name, 'AndroidManifest.xml', obfuscation_flag, manifest_entropy])  # Use package name in CSV

def detect_steganography_manifest(apk_path):
    manifest_data = extract_manifest(apk_path)
    if manifest_data:
        detect_obfuscated_manifest(manifest_data, apk_path)

# 4. Java Code Analysis and Obfuscation Detection with Steganography
def detect_obfuscated_code(java_code_folder, apk_path):
    obfuscation_patterns = ['a', 'b', 'c', 'x', 'y', 'z']
    for root, dirs, files in os.walk(java_code_folder):
        for file in files:
            if file.endswith('.java'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    file_entropy = calculate_entropy(content)
                    obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
                    package_name = extract_package_name(apk_path)  # Extract package name
                    write_to_csv([package_name, file, obfuscation_flag, file_entropy])  # Use package name in CSV

def decompile_dex_to_java(apk_path):
    """Decompile DEX files to Java code using apktool."""
    output_dir = 'output_folder'  # Define the folder where decompiled files will be saved
    subprocess.run(['apktool', 'd', apk_path, '-o', output_dir, '-f'], check=True)  # Add '-f' to force overwrite
    print(f"APK decompiled to {output_dir}")

def detect_steganography_dex(apk_path):
    decompile_dex_to_java(apk_path)
    detect_obfuscated_code('output_folder', apk_path)

# 5. Media File Obfuscation with Steganography Detection
def detect_media_obfuscation(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.lower().endswith(('.mp3', '.mp4', '.ogg')):
                media_data = zip_file.read(file_name)
                media_entropy = calculate_entropy(media_data)
                obfuscation_flag = "Yes" if media_entropy > 7.5 else "No"
                package_name = extract_package_name(apk_path)  # Extract package name
                write_to_csv([package_name, file_name, obfuscation_flag, media_entropy])  # Use package name in CSV

def detect_steganography_media(apk_path):
    detect_media_obfuscation(apk_path)

# 6. Permission Analysis and Steganography Detection
def analyze_permissions(apk_path):
    suspicious_permissions = [
        'ACCESS_FINE_LOCATION', 'READ_SMS', 'WRITE_SMS', 'INTERNET', 
        'ACCESS_COARSE_LOCATION', 'READ_CONTACTS', 'SEND_SMS', 'WRITE_EXTERNAL_STORAGE'
    ]
    manifest_data = extract_manifest(apk_path)
    if manifest_data is None:
        return False
    
    manifest_entropy = calculate_entropy(manifest_data.encode('utf-8'))
    obfuscation_flag = "Yes" if manifest_entropy > 7.5 else "No"
    package_name = extract_package_name(apk_path)  # Extract package name
    write_to_csv([package_name, 'permissions', obfuscation_flag, manifest_entropy])  # Use package name in CSV

    tree = ET.ElementTree(ET.fromstring(manifest_data))
    root = tree.getroot()
    for elem in root.iter('uses-permission'):
        permission_name = elem.attrib.get('android:name')
        if permission_name and any(perm in permission_name for perm in suspicious_permissions):
            print(f"Suspicious permission found: {permission_name}")
            write_to_csv([package_name, permission_name, 'Yes', 0])  # 0 entropy for permissions

# 7. Hash Extraction and Steganography Detection
def extract_file_hashes(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            file_data = zip_file.read(file_name)
            file_entropy = calculate_entropy(file_data)
            obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
            package_name = extract_package_name(apk_path)  # Extract package name
            write_to_csv([package_name, file_name, obfuscation_flag, file_entropy])  # Use package name in CSV

# 8. APK File Analysis for Obfuscation using Entropy and Steganography
def analyze_apk_files(apk_path):
    package_name = extract_package_name(apk_path)  # Extract package name here
    print(f"Package Name: {package_name}")
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            file_data = zip_file.read(file_name)
            file_entropy = calculate_entropy(file_data)
            obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
            write_to_csv([package_name, file_name, obfuscation_flag, file_entropy])  # Use package name in CSV

# 9. Smali Code Obfuscation Detection
def detect_smali_obfuscation(apk_path):
    smali_folder = 'smali_folder'
    subprocess.run(['apktool', 'd', apk_path, '-o', smali_folder, '-f'], check=True)  # Fixed folder name and added '-f'

    for root, dirs, files in os.walk(smali_folder):
        for file in files:
            if file.endswith('.smali'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    file_entropy = calculate_entropy(content)
                    obfuscation_flag = "Yes" if file_entropy > 7.5 else "No"
                    package_name = extract_package_name(apk_path)  # Extract package name
                    write_to_csv([package_name, file, obfuscation_flag, file_entropy])  # Use package name in CSV

def detect_steganography_smali(apk_path):
    detect_smali_obfuscation(apk_path)

# Main function for executing all the detection checks
if __name__ == '__main__':
    # Initialize the CSV with header
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_columns)
    
    apk_path = 'b.apk'

    # Perform Analysis
    detect_steganography_certificate_fingerprint(apk_path)
    detect_steganography_manifest(apk_path)
    detect_steganography_dex(apk_path)
    detect_steganography_media(apk_path)
    analyze_permissions(apk_path)
    extract_file_hashes(apk_path)
    analyze_apk_files(apk_path)
    detect_steganography_smali(apk_path)
