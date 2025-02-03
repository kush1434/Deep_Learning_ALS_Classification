import pandas as pd
import numpy as np
import glob
import os

def load_gpr(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    for i, line in enumerate(lines):
        if line.startswith("Block"):
            header_index = i
            break
    
    df = pd.read_csv(file_path, sep='\t', skiprows=header_index)
    return df

def preprocess_gpr(df):
    if 'Flags' in df.columns:
        df = df[df['Flags'] == 0]
    
    df['Log_F532_Median'] = np.log1p(df['F532 Median'] - df['B532 Median'])
    
    threshold = np.percentile(df['Log_F532_Median'], 5)
    df = df[df['Log_F532_Median'] > threshold]
    
    return df

def process_all_gpr_files(input_folder):
    gpr_files = glob.glob(f"{input_folder}/*.gpr")
    for file_path in gpr_files:
        df = load_gpr(file_path)
        df_clean = preprocess_gpr(df)
        
        folder_name = file_path.split('/')[-2]
        output_folder = os.path.join("data", "preprocessed", folder_name)
        
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, file_path.split('/')[-1].replace('.gpr', '.csv'))
        df_clean.to_csv(output_file, index=False)
        
        print(f"Processed {file_path} -> {output_file}")


    
raw_data_path = "data/raw"

categories = ["control", "male_ALS", "female_ALS"]

for category in categories:
    folder_path = os.path.join(raw_data_path, category)
    process_all_gpr_files(folder_path)
    