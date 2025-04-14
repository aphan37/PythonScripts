import os
import shutil
import pandas as pd

# Specify file paths
unique_ids_path = 'uniquePatientData.xlsx'  # Path to the Excel file with unique IDs
classification_path = 'commercial_nacc65a.csv'  # Path to the CSV file with CDRGLOB classifications
image_folder = 'NACC_jpg'  # Path to the folder containing the images
output_base_folder = 'uniqueNACCImage'  # Base folder for classified images

# Load the unique IDs from the Excel file
unique_ids_df = pd.read_excel(unique_ids_path)
if 'NACCID' not in unique_ids_df.columns:
    raise ValueError("The unique IDs file must contain a column named 'NACCID'.")

unique_ids = set(unique_ids_df['NACCID'].astype(str))  # Convert to string and store in a set

# Load the classification data from the CSV file
classification_df = pd.read_csv(classification_path)
if 'NACCID' not in classification_df.columns or 'CDRGLOB' not in classification_df.columns:
    raise ValueError("The classification file must contain 'NACCID' and 'CDRGLOB' columns.")

# Map CDRGLOB to readable categories
alzheimers_category = {
    0: 'NoAlzheimers',
    0.5: 'Mild',
    1: 'CognitivelyIntact',
    2: 'Moderate',
    3: 'Severe'
}

# Add a column with mapped categories
classification_df['Type'] = classification_df['CDRGLOB'].map(alzheimers_category)

# Filter the classification data for only the unique IDs
classification_filtered = classification_df[classification_df['NACCID'].astype(str).isin(unique_ids)]

# Create a dictionary to map NACCID to classification type
id_to_type = classification_filtered.set_index('NACCID')['Type'].to_dict()

# Create the base output folder
if not os.path.exists(output_base_folder):
    os.mkdir(output_base_folder)

# Create type subfolders
types = set(id_to_type.values())  # Get all unique types
type_folders = {}
for t in types:
    type_folder = os.path.join(output_base_folder, f'type_{t}')
    if not os.path.exists(type_folder):
        os.mkdir(type_folder)
    type_folders[t] = type_folder

# Initialize a dictionary to count the number of images in each type folder
type_image_counts = {t: 0 for t in types}

# Classify the images
for file_name in os.listdir(image_folder):
    if file_name.endswith('.jpg'):  # Process only .jpg files
        # Extract the base ID before the first underscore
        base_id = file_name.split('_')[0]

        # Check if the base ID exists in the classification data
        if base_id in id_to_type:
            image_type = id_to_type[base_id]  # Get the corresponding type
            target_folder = type_folders[image_type]  # Get the corresponding folder

            # Copy the image to the target folder
            src_path = os.path.join(image_folder, file_name)
            dst_path = os.path.join(target_folder, file_name)
            shutil.copy(src_path, dst_path)

            # Increment the image count for the type folder
            type_image_counts[image_type] += 1

# Write the summary file for each folder
for image_type, count in type_image_counts.items():
    type_folder = type_folders[image_type]
    summary_file = os.path.join(type_folder, 'folder_summary.txt')
    with open(summary_file, 'w') as file:
        file.write(f"Folder Name: type_{image_type}\n")
        file.write(f"Total Images: {count}\n")

print(f"Images classified into subfolders under {output_base_folder}")
