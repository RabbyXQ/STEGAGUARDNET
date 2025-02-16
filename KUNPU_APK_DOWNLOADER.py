import subprocess
import time
import json
import os
import re  # To use regular expressions for pattern matching
from PIL import Image
import pytesseract

BACKUP_DIR = "/Volumes/Shared/rabbyx/APKS_PLAY"

# Ensure backup directory exists

# Load package names from JSON file
def load_package_names(filename="package_names.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            if isinstance(data, list):  # If the data is a list, return it directly
                return data
            return data.get("packages", [])  # Otherwise, use the "packages" key
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save updated package names back to JSON file
def save_package_names(package_names, filename="package_names.json"):
    with open(filename, "w") as file:
        json.dump({"packages": package_names}, file, indent=4)

# Check if the app is unavailable in the country
def is_app_unavailable():
    try:
        print("Checking if app is unavailable in the country...")

        # Capture a screenshot of the Play Store page
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
        subprocess.run(["adb", "pull", "/sdcard/screen.png", "screen.png"], check=True)

        # Preprocess the image for better OCR results
        image = Image.open("screen.png").convert("L")  # Convert to grayscale
        text_output = pytesseract.image_to_string(image)

        # Look for country restriction messages
        if re.search(r"not available in your country|isn’t available in your country|in your country|is not compatible|This phone is'n compatible this app|compatible this app|This phone isn|this phone isn", text_output, re.IGNORECASE):
            print("App is unavailable in this country. Skipping...")
            return True

        return False
    finally:
        os.remove("screen.png") if os.path.exists("screen.png") else None
        subprocess.run(["adb", "shell", "rm", "/sdcard/screen.png"], check=True)

# Check if the app is paid
def is_paid_app(package_name):
    try:
        print(f"Checking if {package_name} is a paid app...")

        # Open the Play Store for the app
        subprocess.run(["adb", "shell", "am", "start", f"com.android.vending://details?id={package_name}"], check=True)
        time.sleep(5)  # Wait for the Play Store to load

        # Capture a screenshot
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
        subprocess.run(["adb", "pull", "/sdcard/screen.png", "screen.png"], check=True)

        # Extract text and check for price
        text_output = pytesseract.image_to_string(Image.open("screen.png"))
        if re.search(r"BDT\s\d{1,3}(?:,\d{3})?", text_output):
            print(f"App {package_name} is paid. Skipping...")
            return True

        return False
    finally:
        os.remove("screen.png") if os.path.exists("screen.png") else None
        subprocess.run(["adb", "shell", "rm", "/sdcard/screen.png"], check=True)

# Install the app from Play Store with a cancellation option
def install_from_play_via_url(package_name):
    try:
        print(f"Opening Play Store for {package_name}...")
        subprocess.run(["adb", "shell", "am", "start", f"market://details?id={package_name}"], check=True)
        time.sleep(10)  # Wait for the Play Store to load

        if is_app_unavailable() or is_paid_app(package_name):
            return False

        print("Clicking the 'Install' button...")
        for coordinates in [(738, 1000), (738, 900), (738, 1072), (1125, 462)]:
            subprocess.run(["adb", "shell", "input", "tap", str(coordinates[0]), str(coordinates[1])], check=True)

        time.sleep(5)

        # Wait for installation and allow cancellation if needed
        timeout = 300  # Set a timeout in seconds (e.g., 5 minutes)
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print(f"Timeout exceeded for {package_name}. Cancelling installation and removing from list.")
                # Uninstall the app if it is being installed and remove from the list
                uninstall_apk(package_name)
                package_names = load_package_names()
                package_names.remove(package_name)
                save_package_names(package_names)
                print(f"{package_name} removed from the list.")
                return False

            installed_packages = subprocess.check_output(["adb", "shell", "pm", "list", "packages"]).decode()
            if f"package:{package_name}" in installed_packages:
                print(f"App {package_name} installed successfully.")
                return True

            print("Waiting for installation...")
            time.sleep(2)

    except subprocess.CalledProcessError as e:
        print(f"Error installing {package_name}: {e}")
        return False

# Backup APK
def pull_apk(package_name):
    try:
        print(f"Getting APK path for {package_name}...")
        apk_paths = subprocess.check_output(["adb", "shell", "pm", "path", package_name]).decode().strip().splitlines()

        if not apk_paths:
            print(f"No APK found for {package_name}.")
            return

        for apk_path in apk_paths:
            apk_path = apk_path.replace("package:", "").strip()
            destination = os.path.join(BACKUP_DIR, f"{package_name}-{os.path.basename(apk_path)}")
            print(f"Pulling APK to {destination}...")
            subprocess.run(["adb", "pull", apk_path, destination], check=True)
            print(f"Backup saved at {destination}")

    except subprocess.CalledProcessError as e:
        print(f"Failed to pull APK: {e}")

# Uninstall the app
def uninstall_apk(package_name):
    try:
        print(f"Uninstalling {package_name}...")
        subprocess.run(["adb", "shell", "pm", "uninstall", package_name], check=True)
        print(f"{package_name} uninstalled.")
    except subprocess.CalledProcessError as e:
        print(f"Error uninstalling {package_name}: {e}")

# Check if the package is available and compatible
def check_package_status(package_name):
    try:
        print(f"Checking availability and compatibility for {package_name}...")

        # Check if the app is already installed
        installed_packages = subprocess.check_output(["adb", "shell", "pm", "list", "packages"]).decode()
        if f"package:{package_name}" in installed_packages:
            print(f"{package_name} is already installed.")
            return True

        # Get package details using dumpsys (for compatibility check)
        package_info = subprocess.check_output(["adb", "shell", "dumpsys", "package", package_name]).decode()

        if "pkgFlags=[ SYSTEM" in package_info:
            print(f"{package_name} is a system app, skipping...")
            return False

        return True
    except subprocess.CalledProcessError:
        print(f"{package_name} is not available on this device.")
        return False

# Main execution loop
def main():
    package_names = load_package_names()
    if not package_names:
        print("No packages found in package_names.json")
        return

    for package_name in package_names[:]:  # Iterate over a copy of the list
        if check_package_status(package_name) and install_from_play_via_url(package_name):
            pull_apk(package_name)
            uninstall_apk(package_name)
            package_names.remove(package_name)
            save_package_names(package_names)
            print(f"{package_name} processed and removed from list.")
        else:
            print(f"Skipping {package_name} due to installation failure, country restriction, or being a paid app.")

    print("All packages processed.")

if __name__ == "__main__":
    main()
