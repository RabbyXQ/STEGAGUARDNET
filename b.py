import math
import hashlib
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.misc import AnalyzeAPK
from lxml.etree import tostring


# Utility: Calculate Entropy
def calculate_entropy(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    byte_freq = [0] * 256
    for byte in data:
        byte_freq[byte] += 1
    entropy = 0
    for freq in byte_freq:
        if freq > 0:
            prob = freq / len(data)
            entropy -= prob * math.log2(prob)
    return entropy


# 1. Certificate Analysis
def analyze_certificates(apk):
    print("Analyzing APK certificates...")
    try:
        signatures = apk.get_signature_names()
        if signatures:
            print(f"Signature Names: {signatures}")
        for cert in apk.get_certificates():
            cert_bytes = bytes(cert)
            cert_hash = hashlib.sha256(cert_bytes).hexdigest()
            cert_entropy = calculate_entropy(cert_bytes)
            print(f"Certificate SHA-256: {cert_hash}")
            print(f"Certificate entropy: {cert_entropy}")
            if cert_entropy > 7.5:
                print("Possible obfuscation or steganography detected in certificate due to high entropy!")
    except Exception as e:
        print(f"Error analyzing certificates: {e}")


# 2. Manifest Analysis
def analyze_manifest(apk):
    print("Analyzing AndroidManifest.xml...")
    try:
        manifest_axml = apk.get_android_manifest_axml()
        if manifest_axml is not None:
            # We print the manifest content directly without serializing it
            manifest_str = tostring(manifest_axml, encoding="utf-8").decode("utf-8")
            manifest_entropy = calculate_entropy(manifest_str)
            print(f"Manifest entropy: {manifest_entropy}")
            if manifest_entropy > 7.5:
                print("Possible obfuscation or steganography detected in the manifest due to high entropy!")
        else:
            print("Manifest is not available or could not be decoded.")
    except Exception as e:
        print(f"Error analyzing manifest: {e}")


# 3. DEX Analysis
def analyze_dex(apk, dvm):
    print("Analyzing DEX files...")
    try:
        dex_files = apk.get_dex()
        if isinstance(dex_files, list):  # Ensure it's a list of DEX files
            for dex in dex_files:
                dex_entropy = calculate_entropy(dex)
                print(f"DEX entropy: {dex_entropy}")
                if dex_entropy > 7.5:
                    print("Possible obfuscation or steganography detected in DEX files!")
            analyze_methods(dvm)
        else:
            print("No DEX files found or unable to retrieve them.")
    except Exception as e:
        print(f"Error analyzing DEX files: {e}")


# 4. Analyze Methods for Obfuscation
def analyze_methods(dvm):
    print("Analyzing methods...")
    try:
        for method in dvm.get_methods():
            code = method.get_code()
            if code:
                bytecode = code.get_bc().get_raw()
                method_entropy = calculate_entropy(bytecode)
                print(f"Method {method.get_name()}: Entropy: {method_entropy}")
                if method_entropy > 7.5:
                    print(f"Obfuscation detected in method {method.get_name()}!")
    except Exception as e:
        print(f"Error analyzing methods: {e}")


# 5. Permission Analysis
def analyze_permissions(apk):
    print("Analyzing permissions...")
    suspicious_permissions = [
        "ACCESS_FINE_LOCATION",
        "READ_SMS",
        "WRITE_SMS",
        "INTERNET",
        "ACCESS_COARSE_LOCATION",
        "READ_CONTACTS",
        "SEND_SMS",
        "WRITE_EXTERNAL_STORAGE",
    ]
    try:
        for permission in apk.get_permissions():
            print(f"Permission: {permission}")
            if any(suspicious in permission for suspicious in suspicious_permissions):
                print(f"Suspicious permission detected: {permission}")
    except Exception as e:
        print(f"Error analyzing permissions: {e}")


# 6. Asset Analysis
def analyze_assets(apk):
    print("Analyzing assets...")
    try:
        for file_name in apk.get_files():
            file_data = apk.get_file(file_name)
            entropy = calculate_entropy(file_data)
            print(f"File: {file_name}, Entropy: {entropy}")
            if entropy > 7.5:
                print(f"Possible steganography detected in asset {file_name} due to high entropy!")
    except Exception as e:
        print(f"Error analyzing assets: {e}")


# Main Function
def main(apk_path):
    print(f"Analyzing APK: {apk_path}")
    try:
        apk, dvm, analysis = AnalyzeAPK(apk_path)
    except Exception as e:
        print(f"Error analyzing APK file: {e}")
        return

    # Analyze each component
    analyze_certificates(apk)
    analyze_manifest(apk)
    analyze_dex(apk, dvm)
    analyze_permissions(apk)
    analyze_assets(apk)


if __name__ == "__main__":
    apk_path = "sample.apk"  # Replace with the actual path to your APK
    main(apk_path)
