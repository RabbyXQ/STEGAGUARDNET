import os
import shutil
import random

# Paths
malware_dir = "/Volumes/Shared/rabbyx/dataset_malware"
benign_dir = "/Volumes/Shared/rabbyx/dataset_benign"
dataset_path = "/Volumes/Shared/rabbyx/dataset"

train_dir = os.path.join(dataset_path, "train")
test_dir = os.path.join(dataset_path, "test")

# Create directories
for cls in ["malware", "benign"]:
    os.makedirs(os.path.join(train_dir, cls), exist_ok=True)
    os.makedirs(os.path.join(test_dir, cls), exist_ok=True)

# Function to split dataset
def split_and_copy(src_dir, dest_train, dest_test, split_ratio=0.8):
    files = os.listdir(src_dir)
    random.shuffle(files)

    split_index = int(len(files) * split_ratio)
    train_files, test_files = files[:split_index], files[split_index:]

    for f in train_files:
        shutil.copy(os.path.join(src_dir, f), os.path.join(dest_train, f))
    for f in test_files:
        shutil.copy(os.path.join(src_dir, f), os.path.join(dest_test, f))

# Split both classes
split_and_copy(malware_dir, os.path.join(train_dir, "malware"), os.path.join(test_dir, "malware"))
split_and_copy(benign_dir, os.path.join(train_dir, "benign"), os.path.join(test_dir, "benign"))

print("Dataset successfully split into train and test!")
