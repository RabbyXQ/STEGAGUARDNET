import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, skew, kurtosis

# List of CSV files to load
file_names = ["b1.csv", "b2.csv", "b3.csv", "b4.csv", "b5.csv", "b6.csv", "b7.csv"]

# Load and concatenate all CSV files into a single DataFrame
df_list = [pd.read_csv(file_name) for file_name in file_names]
df = pd.concat(df_list, ignore_index=True)

# Extract file extension from 'file_resource' column
df["file_extension"] = df["file_resource"].apply(lambda x: x.split('.')[-1] if '.' in x else 'none')

# Compute statistics for entropy
mean_entropy = np.mean(df["entropy"])
std_dev_entropy = np.std(df["entropy"])

# Plot Histogram for different file extensions
plt.figure(figsize=(12, 6))

# Loop through unique file extensions and plot
for ext in df["file_extension"].unique():
    # Filter by file extension
    ext_data = df[df["file_extension"] == ext]
    
    # Plot histogram for each file extension
    plt.hist(ext_data["entropy"], bins=10, alpha=0.5, label=f"{ext.upper()} Files", density=True)

# Generate values for the Gaussian (normal) distribution based on the data
xmin, xmax = plt.xlim()
x_values = np.linspace(xmin, xmax, 100)
gaussian_values = norm.pdf(x_values, mean_entropy, std_dev_entropy)

# Plot the Gaussian function
plt.plot(x_values, gaussian_values, 'r-', label=f'Gaussian Fit (μ={mean_entropy:.2f}, σ={std_dev_entropy:.2f})')

# Plot Mean & Standard Deviation lines
plt.axvline(mean_entropy, color="red", linestyle="dashed", linewidth=2, label=f"Mean = {mean_entropy:.2f}")
plt.axvline(mean_entropy + std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean + 1σ = {mean_entropy + std_dev_entropy:.2f}")
plt.axvline(mean_entropy - std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean - 1σ = {mean_entropy - std_dev_entropy:.2f}")

# Labels and Title
plt.xlabel("Entropy")
plt.ylabel("Density")
plt.title("Entropy Distribution with Gaussian Fit")
plt.legend()

# Save the plot as PNG
plt.savefig("entropy_distribution_gaussian.png", format="png")

# Show the plot
plt.show()

# Display further statistics
print(f"Mean Entropy: {mean_entropy:.2f}")
print(f"Standard Deviation of Entropy: {std_dev_entropy:.2f}")

# Boxplot for Entropy Distribution
plt.figure(figsize=(12, 6))
sns.boxplot(x="file_extension", y="entropy", data=df, palette="Set3")
plt.title("Boxplot of Entropy by File Extension")
plt.xlabel("File Extension")
plt.ylabel("Entropy")
plt.show()

# Histogram with KDE (Kernel Density Estimation)
plt.figure(figsize=(12, 6))
sns.histplot(df["entropy"], kde=True, bins=15, color="blue", stat="density")
plt.axvline(mean_entropy, color="red", linestyle="dashed", linewidth=2, label=f"Mean = {mean_entropy:.2f}")
plt.axvline(mean_entropy + std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean + 1σ = {mean_entropy + std_dev_entropy:.2f}")
plt.axvline(mean_entropy - std_dev_entropy, color="green", linestyle="dashed", linewidth=2, label=f"Mean - 1σ = {mean_entropy - std_dev_entropy:.2f}")
plt.title("Entropy Distribution with KDE")
plt.xlabel("Entropy")
plt.ylabel("Density")
plt.legend()
plt.show()
