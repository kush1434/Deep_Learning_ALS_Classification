import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import random

def load_pathway_data(folder_path):
    """Loads all pathway mapping CSV files from a given folder and merges them."""
    all_pathways = []
    
    for file in os.listdir(folder_path):
        if file.endswith("_pathways.csv"):
            df = pd.read_csv(os.path.join(folder_path, file))
            all_pathways.append(df)
    
    if all_pathways:
        merged_df = pd.concat(all_pathways, ignore_index=True)
        return merged_df
    else:
        print(f"No pathway files found in {folder_path}")
        return None

# Load pathways for each group
male_als_pathways = load_pathway_data("data/mapped_pathways/male_ALS")
female_als_pathways = load_pathway_data("data/mapped_pathways/female_ALS")
control_pathways = load_pathway_data("data/mapped_pathways/control")

# Debugging: Print available columns and total pathways
for label, df in zip(["Male ALS", "Female ALS", "Control"], [male_als_pathways, female_als_pathways, control_pathways]):
    if df is not None:
        print(f"Columns in {label} pathways file: {df.columns}")
        print(f"Total pathways in {label} dataset: {len(df)}")

# Identify the correct column name
def get_column_name(df):
    if df is not None:
        for col in ["term_name", "name", "description"]:
            if col in df.columns:
                return col
    return None

male_col = get_column_name(male_als_pathways)
female_col = get_column_name(female_als_pathways)
control_col = get_column_name(control_pathways)

# Extract unique pathways per group
male_als_list = list(male_als_pathways[male_col]) if male_col else []
female_als_list = list(female_als_pathways[female_col]) if female_col else []
control_list = list(control_pathways[control_col]) if control_col else []

# Downsample to 50% ALS (25% Male, 25% Female) and 50% Control
total_als = len(male_als_list) + len(female_als_list)
als_target = int(0.5 * (total_als + len(control_list)))
male_target = int(0.5 * als_target)
female_target = als_target - male_target
control_target = als_target  # Ensuring 50:50 ALS vs Control

def downsample_list(pathway_list, target_size):
    return random.sample(pathway_list, target_size) if len(pathway_list) > target_size else pathway_list

male_als_list = downsample_list(male_als_list, male_target)
female_als_list = downsample_list(female_als_list, female_target)
control_list = downsample_list(control_list, control_target)

# Convert lists back to sets for unique comparisons
male_als_set = set(male_als_list)
female_als_set = set(female_als_list)
control_set = set(control_list)

# Identify unique & shared pathways
male_unique = male_als_set - (female_als_set | control_set)
female_unique = female_als_set - (male_als_set | control_set)
als_shared = male_als_set & female_als_set
als_vs_control = als_shared - control_set
control_unique = control_set - (male_als_set | female_als_set)

summary_data = {
    "Category": ["Male ALS Unique", "Female ALS Unique", "Shared ALS", "ALS vs Control", "Control Unique"],
    "Count": [len(male_unique), len(female_unique), len(als_shared), len(als_vs_control), len(control_unique)]
}
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv("data/mapped_pathways/pathway_summary.csv", index=False)
print("Summary report saved after downsampling.")

# Save unique Control pathways to CSV
control_unique_df = pd.DataFrame({"Control Unique Pathways": list(control_unique)})
control_unique_df.to_csv("data/mapped_pathways/control_unique_pathways.csv", index=False)
print("Unique Control pathways saved to control_unique_pathways.csv")

# Adjust Venn Diagram proportions
plt.figure(figsize=(6, 6))
venn3([
    male_als_set,
    female_als_set,
    control_set
], ('Male ALS', 'Female ALS', 'Control'))
plt.title("Pathway Overlap Between Groups After Downsampling (50:50 ALS vs Control)")
plt.savefig("data/mapped_pathways/pathway_venn_diagram.png")
plt.show()

print("Pathway analysis complete! Summary saved to pathway_summary.csv")
