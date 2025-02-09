import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, norm
from sklearn.preprocessing import LabelEncoder
import psutil
import os

# List of new CSV files to load
file_names = [
    "Ben0.csv", "Ben1.csv", "Ben2.csv", "Ben3.csv", "Ben4.csv"
]

# Function to check memory usage
def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 ** 2)  # Convert bytes to MB

# Print initial memory usage
print(f"Initial Memory usage: {get_memory_usage():.2f} MB")

# Load and process each CSV file separately in chunks
chunk_size = 5000  # Adjust based on memory
df = pd.DataFrame()

for file_name in file_names:
    try:
        # Process CSV file in chunks
        for chunk in pd.read_csv(file_name, chunksize=chunk_size):
            # Process the chunk
            # Automatically detect numeric columns
            numeric_columns = chunk.select_dtypes(include=[np.number]).columns
            non_numeric_columns = chunk.select_dtypes(exclude=[np.number]).columns

            # Encode non-numeric columns
            for col in non_numeric_columns:
                le = LabelEncoder()
                chunk[col] = le.fit_transform(chunk[col])

            # Convert numeric columns to smaller data types
            for col in chunk.select_dtypes(include=[np.number]).columns:
                if chunk[col].dtype == 'float64':
                    chunk[col] = chunk[col].astype('float32')
                elif chunk[col].dtype == 'int64':
                    chunk[col] = chunk[col].astype('int32')

            # Compute Shannon entropy for each row in the chunk
            def shannon_entropy(row):
                prob = row / row.sum()
                return -np.sum(prob * np.log2(prob + np.finfo(float).eps))  # Adding epsilon to avoid log(0)

            entropy_column = chunk[numeric_columns].apply(shannon_entropy, axis=1)
            z_score_column = (entropy_column - entropy_column.mean()) / entropy_column.std()

            # Concatenate the new columns to avoid fragmentation
            chunk = pd.concat([chunk, entropy_column.rename('entropy'), z_score_column.rename('z_score')], axis=1)

            # Optionally, copy the chunk to avoid fragmentation
            chunk = chunk.copy()

            # Append the chunk to the full dataframe (if needed)
            df = pd.concat([df, chunk], ignore_index=True)

    except FileNotFoundError:
        print(f"Error: {file_name} not found. Skipping.")
    except Exception as e:
        print(f"Error loading {file_name}: {e}")

# Final memory usage after loading data
print(f"Memory usage after loading data: {get_memory_usage():.2f} MB")

# Check the dataframe size
print(f"Dataframe size: {df.shape[0]} rows and {df.shape[1]} columns")

# Now you can proceed to analyze the 'df' dataframe as before
# For example, compute statistics for entropy and Gaussian fitting:
mean_entropy = np.mean(df["entropy"])
std_dev_entropy = np.std(df["entropy"])

# Fit Gaussian distribution to the entropy values
mu, std = norm.fit(df["entropy"])

# Plot the Histogram for Entropy
plt.figure(figsize=(12, 6))
sns.histplot(df["entropy"], kde=True, bins=15, color="blue", stat="density")
plt.axvline(mean_entropy, color="red", linestyle="dashed", linewidth=2, label=f"Mean = {mean_entropy:.2f}")
plt.axvline(mean_entropy + std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean + 1σ = {mean_entropy + std_dev_entropy:.2f}")
plt.axvline(mean_entropy - std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean - 1σ = {mean_entropy - std_dev_entropy:.2f}")

# Plot Gaussian (Normal) Distribution
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2, label=f'Gaussian Fit: μ = {mu:.2f}, σ = {std:.2f}')
plt.title("Entropy Distribution with KDE and Gaussian Fit")
plt.xlabel("Entropy")
plt.ylabel("Density")
plt.legend()
plt.show()

# Save the Histogram as PNG (Optional)
plt.figure(figsize=(12, 6))
sns.histplot(df["entropy"], kde=True, bins=15, color="blue", stat="density")
plt.axvline(mean_entropy, color="red", linestyle="dashed", linewidth=2, label=f"Mean = {mean_entropy:.2f}")
plt.axvline(mean_entropy + std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean + 1σ = {mean_entropy + std_dev_entropy:.2f}")
plt.axvline(mean_entropy - std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean - 1σ = {mean_entropy - std_dev_entropy:.2f}")
plt.plot(x, p, 'k', linewidth=2, label=f'Gaussian Fit: μ = {mu:.2f}, σ = {std:.2f}')
plt.title("Entropy Distribution with KDE and Gaussian Fit")
plt.xlabel("Entropy")
plt.ylabel("Density")
plt.legend()
plt.savefig("entropy_distribution_gaussian.png", dpi=300)
plt.close()

# Print memory usage after processing
print(f"Memory usage after processing: {get_memory_usage():.2f} MB")
