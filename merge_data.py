import os
import pandas as pd

# Define paths
parkinsons_folder = "data/preprocessed/raw/"
control_folder = "data/preprocessed/control/"
output_dir = "data/processed"
output_path = os.path.join(output_dir, "gene_expression_combined.csv")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to load and append CSV files in chunks
def load_and_append(folder, label, chunk_size=10000):
    files = [f for f in os.listdir(folder) if f.endswith("_processed.csv")]
    print(f"Processing {len(files)} files from {folder}...")
    for file in files:
        file_path = os.path.join(folder, file)
        chunk_iter = pd.read_csv(file_path, chunksize=chunk_size)  # Read in chunks
        for chunk in chunk_iter:
            chunk["Label"] = label  # Assign label
            yield chunk

# Open file for writing in chunks
with open(output_path, "w") as writer:
    first_chunk = True
    for df_chunk in load_and_append(parkinsons_folder, label=1):
        df_chunk.to_csv(writer, index=False, header=first_chunk)
        first_chunk = False  # Ensure only first chunk has headers
    for df_chunk in load_and_append(control_folder, label=0):
        df_chunk.to_csv(writer, index=False, header=False)

print(f"Dataset merged and saved at {output_path}")
