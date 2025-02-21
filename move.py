import os
import shutil

def move_png_files(src_dir, dest_dir):
    # Walk through the directory
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith('.png'):  # Check if the file is a PNG
                # Construct full file path
                file_path = os.path.join(root, file)

                # Move the file to the destination directory
                shutil.move(file_path, os.path.join(dest_dir, file))
                print(f"Moved: {file_path} -> {dest_dir}/{file}")

# Example usage
src_directory = "/Volumes/Shared/rabbyx/mal_fourier"  # Replace with the source directory path
dest_directory = "/Volumes/Shared/rabbyx/dataset_malware"  # Replace with the destination directory path

# Make sure the destination directory exists
os.makedirs(dest_directory, exist_ok=True)

# Move all PNG files
move_png_files(src_directory, dest_directory)
