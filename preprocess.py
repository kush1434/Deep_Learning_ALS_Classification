import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import QuantileTransformer

def preprocess_cel_data(input_folder, output_folder):
    def extract_intensity_data(file_path):
        with open(file_path, 'r', encoding="latin1") as file:
            lines = file.readlines()

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "[INTENSITY]":
                start_idx = i + 2
                break

        if start_idx is None:
            raise ValueError("No [INTENSITY] section found in the file.")

        data = []
        for line in lines[start_idx:]:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            
            try:
                x, y, mean_intensity, stddev, pixels = map(float, parts)
                data.append([x, y, mean_intensity, stddev, pixels])
            except ValueError:
                continue

        df = pd.DataFrame(data, columns=["X", "Y", "Mean_Intensity", "StdDev", "Pixels"])
        return df

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    processed_data = []
    files = [f for f in os.listdir(input_folder) if f.endswith(".cel")]
    
    if not files:
        print(f"No .cel files found in {input_folder}. Please check the directory.")
        return None

    print(f"Processing {len(files)} .cel files from {input_folder}...")
    
    for file_name in files:
        file_path = os.path.join(input_folder, file_name)
        try:
            print(f"Processing {file_name}...")
            df = extract_intensity_data(file_path)

            # Background correction (removing lowest 5% values to reduce bias)
            lower_threshold = np.percentile(df["Mean_Intensity"], 5)
            df["Corrected_Intensity"] = np.maximum(df["Mean_Intensity"] - lower_threshold, 0)

            # Log transformation for normalization
            df["Log_Intensity"] = np.log1p(df["Corrected_Intensity"])

            # Quantile normalization per file
            qt = QuantileTransformer(output_distribution='normal', random_state=0)
            df["Normalized_Intensity"] = qt.fit_transform(df[["Log_Intensity"]])

            df["File"] = file_name  # File identifier
            processed_data.append(df)
            
            # Save each processed file individually
            output_file_path = os.path.join(output_folder, file_name.replace(".cel", "_processed.csv"))
            df.to_csv(output_file_path, index=False)
            print(f"Saved processed data to {output_file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    final_df = pd.concat(processed_data, ignore_index=True) if processed_data else None
    if final_df is not None:
        print(f"All files processed successfully. Processed data saved in {output_folder}.")
    return final_df

if __name__ == "__main__":
    input_folder = "data/raw"
    output_folder = "data/preprocessed/raw"
    preprocess_cel_data(input_folder, output_folder)
