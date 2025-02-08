import hashlib
import os
import base64
import subprocess
import xml.etree.ElementTree as ET
import math
import csv
from zipfile import ZipFile
from androguard.core.bytecodes.apk import APK
from multiprocessing import Pool, cpu_count, get_context
from concurrent.futures import ThreadPoolExecutor

# Directories
apk_directory = "app"
output_directory = "output_folder"
csv_file = "obfuscation_analysis.csv"

csv_columns = ['package_name', 'file_resource', 'obfuscation_flag', 'entropy']

# ThreadPool Executor for I/O operations
thread_pool = ThreadPoolExecutor(max_workers=5)


def write_to_csv(data):
    """Writes detection data to CSV using a separate thread."""
    thread_pool.submit(_write_to_csv, data)


def _write_to_csv(data):
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
                if file_name.lower().endswith(('cert', 'sf')):
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
    """Process each APK in parallel."""
    print(f"Processing: {apk_path}")
    package_name = extract_package_name(apk_path)
    print(f"Package Name: {package_name}")

    get_certificate_fingerprint(apk_path)
    detect_obfuscated_manifest(apk_path)
    detect_smali_obfuscation(apk_path)
    analyze_java_code(apk_path)

    print(f"Completed {apk_path}")


def cleanup():
    """Removes all generated output files safely."""
    if os.path.exists(output_directory):
        subprocess.run(['rm', '-rf', output_directory], check=True)
    print("Cleaned up generated files.")


def main():
    """Main function to run parallel APK analysis."""
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_columns)

    if not os.path.exists(apk_directory):
        print(f"APK directory '{apk_directory}' not found.")
        return

    apk_files = [os.path.join(apk_directory, f) for f in os.listdir(apk_directory) if f.endswith('.apk')]

    if not apk_files:
        print("No APKs found for analysis.")
        return

    # Use multiprocessing with spawn mode for macOS compatibility
    num_workers = min(10, cpu_count())  # Use up to 10 workers or available CPU cores
    ctx = get_context("spawn")  # macOS compatibility
    with ctx.Pool(num_workers) as pool:
        pool.map(analyze_apk, apk_files)

    cleanup()


if __name__ == '__main__':
    main()
