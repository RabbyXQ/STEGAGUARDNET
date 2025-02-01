from androguard.core.bytecodes.apk import APK

def extract_package_name(apk_path):
    """Extracts the package name from the APK file using Androguard."""
    apk = APK(apk_path)  # Load the APK file
    package_name = apk.get_package()  # Extract the package name
    return package_name

# Example usage
apk_path = 'b.apk'
package_name = extract_package_name(apk_path)
print(f"Package Name: {package_name}")
