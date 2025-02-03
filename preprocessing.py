import pandas as pd
import numpy as np
import glob
import re

def load_gpr(file_path):
    """
    Load a .gpr file and extract relevant gene expression data.
    """which python3
python3 --version
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find where the data table starts (after headers)
    for i, line in enumerate(lines):
        if line.startswith("Block"):  # This marks the start of tabular data
            header_index = i
            break
    
    df = pd.read_csv(file_path, sep='\t', skiprows=header_index)
    return df

def preprocess_gpr(df):
    """
    Preprocess the .gpr data:
    - Remove flagged spots
    - Normalize intensities (log transformation)
    - Remove low-expressed genes
    """
    # Remove flagged spots (if any flags exist in the dataset)
    if 'Flags' in df.columns:
        df = df[df['Flags'] == 0]
    
    # Log transformation of fluorescence intensity
    df['Log_F532_Median'] = np.log1p(df['F532 Median'] - df['B532 Median'])
    
    # Remove low-intensity genes (genes with very low fluorescence)
    threshold = np.percentile(df['Log_F532_Median'], 5)  # Bottom 5% are considered low expression
    df = df[df['Log_F532_Median'] > threshold]
    
    return df

def process_all_gpr_files(input_folder, output_folder):
    """
    Process all .gpr files in a folder and save preprocessed versions.
    """
    gpr_files = glob.glob(f"{input_folder}/*.gpr")
    for file_path in gpr_files:
        df = load_gpr(file_path)
        df_clean = preprocess_gpr(df)
        output_file = output_folder + '/' + file_path.split('/')[-1].replace('.gpr', '_processed.csv')
        df_clean.to_csv(output_file, index=False)
        print(f"Processed {file_path} -> {output_file}")

# Example usage:
# process_all_gpr_files("data/raw_gpr", "data/processed_gpr")
