import cv2
import numpy as np
import os
import time
from concurrent.futures import ThreadPoolExecutor

def apply_fourier_transform(image_path, output_image_path):
    """
    Apply 2D Fourier Transform to an image and save the result as a PNG.
    """
    # Read the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if image is None:
        print(f"Failed to load image: {image_path}")
        return
    
    # Perform the Fourier Transform
    f = np.fft.fft2(image)
    fshift = np.fft.fftshift(f)

    # Calculate magnitude spectrum
    magnitude_spectrum = np.abs(fshift)
    magnitude_spectrum = np.log(magnitude_spectrum + 1)
    
    # Normalize to [0, 255]
    magnitude_spectrum = np.uint8(magnitude_spectrum / np.max(magnitude_spectrum) * 255)
    
    # Save the magnitude spectrum as a new PNG file
    cv2.imwrite(output_image_path, magnitude_spectrum)
    print(f"Fourier Transform applied and saved: {output_image_path}")
    
    # Delete the original image
    os.remove(image_path)
    print(f"Deleted processed image: {image_path}")

def monitor_folder(input_folder, output_folder, interval=5, max_threads=8):
    """
    Continuously monitors the input folder for new images and processes them with threading.
    This version supports nested directories.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print(f"Monitoring folder: {input_folder}")
    
    # Create a ThreadPoolExecutor with the specified number of threads
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        while True:
            # Walk through the directory and its subdirectories
            for root, dirs, files in os.walk(input_folder):
                for filename in files:
                    if filename.endswith('.png'):
                        image_path = os.path.join(root, filename)
                        # Preserve subdirectories in output folder
                        relative_path = os.path.relpath(root, input_folder)
                        output_dir = os.path.join(output_folder, relative_path)
                        
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        output_image_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}_fourier.png')
                        
                        # Submit the Fourier Transform task to the thread pool
                        executor.submit(apply_fourier_transform, image_path, output_image_path)
            
            time.sleep(interval)  # Wait before checking again

if __name__ == "__main__":
    input_folder = '/Volumes/Shared/rabbyx/Riskware/riskware_images'
    output_folder = '/Volumes/Shared/rabbyx/Riskware_fourier'  # Folder to save transformed images
    monitor_folder(input_folder, output_folder)
