import pandas as pd
import numpy as np
import glob
import os

def load_gpr(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    header_index = None

    for i, line in enumerate(lines):
        if "\t" in line and line.count("\t") > 5:
            header_index = i
            break

    if header_index is None:
        print(f"\nERROR: Header not found in {file_path}")
        print("File preview:")
        for line in lines[:10]:
            print(line.strip())
        raise ValueError(f"Header not found in file: {file_path}")

    df = pd.read_csv(file_path, sep='\t', skiprows=header_index, engine='python')

    df.columns = df.columns.str.replace('"', '')

    return df

def preprocess_gpr(df):
    df = df.copy()
    
    if df.empty:
        print("Warning: Empty dataframe encountered, skipping processing.")
        return df  

    if 'Flags' in df.columns:
        df = df[df['Flags'] == 0]

    if 'F532 Median' in df.columns and 'B532 Median' in df.columns:
        df.dropna(subset=['F532 Median', 'B532 Median'], inplace=True)

        df.loc[:, 'Log_F532_Median'] = np.log1p(np.maximum(df['F532 Median'] - df['B532 Median'], 0.0001))

        if not df['Log_F532_Median'].isnull().all():
            threshold = np.percentile(df['Log_F532_Median'].dropna(), 5)
            df = df[df['Log_F532_Median'] > threshold]
    else:
        print("Warning: 'F532 Median' or 'B532 Median' column missing. Skipping log transformation.")

    return df


def process_all_gpr_files(input_folder):
    gpr_files = glob.glob(f"{input_folder}/*.gpr")
    for file_path in gpr_files:
        print(file_path)
        df = load_gpr(file_path)
        df_clean = preprocess_gpr(df)
        
        folder_name = file_path.split('/')[-2]
        output_folder = os.path.join("data", "preprocessed", folder_name)
        
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, file_path.split('/')[-1].replace('.gpr', '.csv'))
        df_clean.to_csv(output_file, index=False)
        
        print(f"Processed {file_path} -> {output_file}")


    
raw_data_path = "data/raw_data"

categories = ["control", "male_ALS", "female_ALS"]

for category in categories:
    folder_path = os.path.join(raw_data_path, category)
    process_all_gpr_files(folder_path)
    