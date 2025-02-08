import pandas as pd
import os

# Load CSV file
df = pd.read_csv("smswares.csv")

# Extract file extensions
df["file_extension"] = df["file_resource"].apply(lambda x: os.path.splitext(x)[1].lower() if "." in os.path.basename(x) else "none")

# Save the modified CSV
df.to_csv("entropy_data_with_extensions.csv", index=False)

print(df.head())  # Preview results
