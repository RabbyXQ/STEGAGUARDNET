import hashlib
import os
import base64
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import math
import chardet


def detect_encoding(file_data):
    """Detect the encoding of the given file data."""
    result = chardet.detect(file_data)
    encoding = result['encoding']
    confidence = result['confidence']
    print(f"Detected encoding: {encoding} with confidence: {confidence}")
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
                print(f"Certificate fingerprint: {cert_hash}")
                # Calculate entropy of certificate data
                cert_entropy = calculate_entropy(cert_data)
                print(f"Certificate entropy: {cert_entropy}")
                if cert_entropy > 7.5:
                    print(f"Possible steganography detected in certificate due to high entropy!")
                return cert_hash
    return None


def detect_obfuscated_certificate_fingerprint(cert_data):
    """Detect obfuscation in certificate data by checking patterns and entropy."""
    cert_entropy = calculate_entropy(cert_data)
    print(f"Certificate data entropy for obfuscation detection: {cert_entropy}")
    if cert_entropy > 7.5:
        print(f"Obfuscation detected in certificate due to high entropy!")
    return cert_entropy


def detect_steganography_certificate_fingerprint(apk_path):
    """Detect steganography in APK certificate fingerprint."""
    print("Detecting steganography in certificate fingerprint...")
    cert_hash = get_certificate_fingerprint(apk_path)
    if cert_hash:
        # You can add additional checks here to look for hidden data patterns
        print(f"Certificate fingerprint: {cert_hash}")


# 3. Manifest Extraction and Obfuscation Detection with Steganography
def extract_manifest(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.lower() == 'androidmanifest.xml':
                manifest_data = zip_file.read(file_name)
                try:
                    # Ensure the manifest is in a valid XML format
                    manifest_data = manifest_data.decode('utf-8')  # Decode the byte data to string
                    return manifest_data
                except UnicodeDecodeError:
                    print(f"Error decoding {file_name}. It may not be a valid UTF-8 file.")
                    return None
    return None

def detect_obfuscated_manifest(manifest_data):
    print("Calculating entropy for the manifest data...")
    if manifest_data is None:
        print("No manifest data found or could not decode the file.")
        return False

    manifest_entropy = calculate_entropy(manifest_data.encode('utf-8'))  # Encode back to bytes for entropy calculation
    print(f"Manifest entropy: {manifest_entropy}")
    
    if manifest_entropy > 7.5:
        print(f"Possible steganography detected in manifest due to high entropy!")

    try:
        tree = ET.ElementTree(ET.fromstring(manifest_data))  # Parse the manifest XML
        root = tree.getroot()
        obfuscated = False

        # Check for suspicious patterns in standard Android components
        suspicious_patterns = ['a', 'b', 'c', 'x', 'y', 'z', '1234', 'random']
        for elem in root.iter():
            if elem.tag in ['activity', 'service', 'receiver', 'provider']:
                component_name = elem.attrib.get('name')
                if component_name and any(pattern in component_name for pattern in suspicious_patterns):
                    obfuscated = True
                    print(f"Suspicious {elem.tag} detected: {component_name}")
            if elem.tag == 'application':
                app_name = elem.attrib.get('name')
                if app_name and any(pattern in app_name for pattern in suspicious_patterns):
                    obfuscated = True
                    print(f"Suspicious application name: {app_name}")
            if elem.tag == 'uses-permission':
                permission_name = elem.attrib.get('android:name')
                if permission_name and any(pattern in permission_name for pattern in suspicious_patterns):
                    obfuscated = True
                    print(f"Suspicious permission detected: {permission_name}")

        print(f"Obfuscated Manifest Detected: {obfuscated}")
        return obfuscated
    except ET.ParseError as e:
        print(f"Error parsing manifest XML: {e}")
        return False
    
    

def detect_steganography_manifest(apk_path):
    """Detect steganography in APK manifest."""
    print("Detecting steganography in manifest...")
    manifest_data = extract_manifest(apk_path)
    if manifest_data:
        detect_obfuscated_manifest(manifest_data)


def detect_obfuscated_code(java_code_folder):
    obfuscation_patterns = ['a', 'b', 'c', 'x', 'y', 'z']
    obfuscated = False
    for root, dirs, files in os.walk(java_code_folder):
        for file in files:
            if file.endswith('.java'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    file_entropy = calculate_entropy(content)
                    print(f"Entropy of {file}: {file_entropy}")
                    if file_entropy > 7.5:  # High entropy could indicate obfuscation
                        obfuscated = True
                        print(f"Obfuscation detected in file: {file}")
                    if file_entropy > 7.5:
                        print(f"Possible steganography detected in Java code due to high entropy!")
    return obfuscated


def detect_steganography_dex(apk_path):
    """Detect steganography in APK DEX files."""
    print("Detecting steganography in DEX files...")
    decompile_dex_to_java(apk_path)
    detect_obfuscated_code('output_folder')


# 4. Java Code Analysis and Obfuscation Detection with Steganography
def decompile_dex_to_java(apk_path):
    # Run the command with the correct arguments
    subprocess.run(['jadx', apk_path, '-d', 'output_folder'])


# 5. Media File Obfuscation with Steganography Detection
def detect_media_obfuscation(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            if file_name.lower().endswith(('.mp3', '.mp4', '.ogg')):
                media_data = zip_file.read(file_name)
                media_entropy = calculate_entropy(media_data)
                print(f"Entropy of media file {file_name}: {media_entropy}")
                if media_entropy > 7.5:
                    print(f"Possible steganography detected in media due to high entropy!")
                try:
                    base64.b64decode(media_data)
                    print(f"Base64 obfuscation detected in media file: {file_name}")
                except:
                    pass
    return False


def detect_steganography_media(apk_path):
    """Detect steganography in APK media files."""
    print("Detecting steganography in media files...")
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
    
    manifest_entropy = calculate_entropy(manifest_data)
    print(f"Manifest entropy: {manifest_entropy}")

    if manifest_entropy > 7.5:
        print(f"Possible steganography detected in permissions due to high entropy!")

    tree = ET.ElementTree(ET.fromstring(manifest_data))
    root = tree.getroot()

    obfuscated = False
    for elem in root.iter('uses-permission'):
        permission_name = elem.attrib.get('android:name')
        if permission_name:
            if any(perm in permission_name for perm in suspicious_permissions):
                print(f"Suspicious permission found: {permission_name}")
                obfuscated = True
    return obfuscated


def detect_steganography_permissions(apk_path):
    """Detect steganography in APK permissions."""
    print("Detecting steganography in permissions...")
    analyze_permissions(apk_path)


# 7. Hash Extraction and Steganography Detection
def extract_file_hashes(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            file_data = zip_file.read(file_name)
            file_entropy = calculate_entropy(file_data)
            print(f"Entropy of file {file_name}: {file_entropy}")
            if file_entropy > 7.5:
                print(f"Possible steganography detected in file {file_name} due to high entropy!")
            file_hash = hashlib.sha256(file_data).hexdigest()
            print(f"File: {file_name}, Hash: {file_hash}")
    return False


def detect_steganography_file_hashes(apk_path):
    """Detect steganography in APK file hashes."""
    print("Detecting steganography in file hashes...")
    extract_file_hashes(apk_path)


# 8. APK File Analysis for Obfuscation using Entropy and Steganography
def analyze_apk_files(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            file_data = zip_file.read(file_name)
            file_entropy = calculate_entropy(file_data)
            print(f"Entropy of {file_name}: {file_entropy}")
            if file_entropy > 7.5:
                print(f"Possible steganography detected in APK file {file_name} due to high entropy!")
            analyze_file_for_obfuscation(file_data, file_name)
            detect_encoding(file_data)




def detect_smali_obfuscation(apk_path):
    """Detect obfuscation or steganography in smali files."""
    smali_folder = 'smali_folder'  # Temporary folder to store extracted smali files
    
    # Extract DEX files and decompile them into smali
    subprocess.run(['apktool', 'd', apk_path, '-o', smali_folder])

    obfuscated = False
    for root, dirs, files in os.walk(smali_folder):
        for file in files:
            if file.endswith('.smali'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    file_entropy = calculate_entropy(content)
                    print(f"Entropy of smali file {file}: {file_entropy}")
                    if file_entropy > 7.5:  # High entropy could indicate obfuscation
                        obfuscated = True
                        print(f"Obfuscation detected in smali file: {file}")
                    if file_entropy > 7.5:
                        print(f"Possible steganography detected in smali file due to high entropy!")
    return obfuscated

def analyze_file_for_obfuscation(file_data, file_name):
    """Analyze a file for obfuscation patterns."""
    obfuscation_patterns = ['a', 'b', 'c', 'x', 'y', 'z']  # List of common patterns to check
    file_entropy = calculate_entropy(file_data)
    print(f"Entropy of {file_name}: {file_entropy}")
    
    # Check if file entropy is high (which could indicate obfuscation)
    if file_entropy > 7.5:
        print(f"Possible obfuscation detected in {file_name} due to high entropy!")
    
    # Check for suspicious patterns in the file content
    if any(pattern in str(file_data) for pattern in obfuscation_patterns):
        print(f"Suspicious pattern found in {file_name}!")


def analyze_assets(apk_path):
    with ZipFile(apk_path) as zip_file:
        for file_name in zip_file.namelist():
            # Check if the file is an asset (like images, XML files, etc.)
            if file_name.lower().endswith(('.png', '.jpg', '.xml', '.json')):
                file_data = zip_file.read(file_name)
                file_entropy = calculate_entropy(file_data)
                print(f"Entropy of asset {file_name}: {file_entropy}")
                if file_entropy > 7.5:
                    print(f"Possible steganography detected in asset {file_name} due to high entropy!")



def detect_steganography_smali(apk_path):
    """Detect steganography in APK's smali code."""
    print("Detecting steganography in smali code...")
    detect_smali_obfuscation(apk_path)


# Main function for executing all the detection checks
if __name__ == '__main__':
    apk_path = 'sample.apk'

    # 1. Certificate Obfuscation
    detect_steganography_certificate_fingerprint(apk_path)

    # 2. Manifest Extraction and Obfuscation
    detect_steganography_manifest(apk_path)

    # 3. Java Code Analysis and Obfuscation
    detect_steganography_dex(apk_path)

    # 4. Resources and Assets Analysis
    analyze_assets(apk_path)

    # 5. Media File Obfuscation
    detect_steganography_media(apk_path)

    # 6. Permission Analysis
    detect_steganography_permissions(apk_path)

    # 7. Hash Extraction and Obfuscation Detection
    detect_steganography_file_hashes(apk_path)

    # 8. APK File Analysis for Obfuscation using Entropy
    analyze_apk_files(apk_path)
    
    detect_steganography_smali(apk_path)
