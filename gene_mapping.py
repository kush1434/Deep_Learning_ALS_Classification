import os
import pandas as pd
from gprofiler import GProfiler
from multiprocessing import Pool

gp = GProfiler(return_dataframe=True)

def map_genes_to_pathways(file_info):
    """Loads a CSV file, extracts gene names, and maps them to pathways."""
    input_folder, output_folder, file = file_info
    file_path = os.path.join(input_folder, file)
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return
    
    if "GeneName" not in df.columns:
        print(f"Skipping {file} (no GeneName column)")
        return
    
    genes = df["GeneName"].dropna().unique().tolist()
    if not genes:
        print(f"Skipping {file} (no valid genes)")
        return
    
    try:
        # Perform pathway mapping
        mapped_pathways = gp.profile(organism='hsapiens', query=genes)
        
        # Save the results
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, file.replace(".csv", "_pathways.csv"))
        mapped_pathways.to_csv(output_file, index=False)
        print(f"Mapped pathways saved: {output_file}")
    except Exception as e:
        print(f"Error mapping pathways for {file}: {e}")

def process_category(category):
    input_path = os.path.join("data/preprocessed", category)
    output_path = os.path.join("data/mapped_pathways", category)
    os.makedirs(output_path, exist_ok=True)
    
    files = [(input_path, output_path, file) for file in os.listdir(input_path) if file.endswith(".csv")]
    
    if __name__ == "__main__":
        # Use multiprocessing to process files in parallel
        with Pool(processes=4) as pool:  # Adjust number of processes as needed
            pool.map(map_genes_to_pathways, files)

# Process each category in parallel
categories = ["male_ALS", "female_ALS", "control"]
for category in categories:
    process_category(category)

print("Pathway mapping complete for all datasets!")
