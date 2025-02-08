import pandas as pd

# Load the CSV file
df = pd.read_csv("adwares.csv")

# Filter rows where obfuscation_flag is "Yes"
filtered_df = df[df["obfuscation_flag"] == "Yes"]

# Display the filtered rows
print(filtered_df)

# Optionally, save the filtered data to a new CSV file
filtered_df.to_csv("filtered_obfuscation.csv", index=False)
