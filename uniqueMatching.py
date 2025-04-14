import os
import pandas as pd

# Specify the paths
image_folder = 'NACC_jpg'  # Update this path
excel_path = 'uniquePatientData.xlsx'  # Update this path

# Load unique IDs from the Excel file
df = pd.read_excel(excel_path)
excel_ids = set(df['NACCID'].astype(str))  # Assuming the column is named 'NACCID'

# Initialize a set to store IDs found in the image folder
image_ids = set()

# Iterate through the files in the image folder
for file_name in os.listdir(image_folder):
    if file_name.endswith('.jpg'):  # Process only .jpg files
        # Extract the part of the filename before the first underscore
        base_id = file_name.split('_')[0]  # Get the base ID
        image_ids.add(base_id)

# Find matches and non-matches
matching_ids = excel_ids.intersection(image_ids)
non_matching_ids = excel_ids.difference(image_ids)

# Output the results
print(f"Total IDs in Excel: {len(excel_ids)}")
print(f"Total IDs in Image Folder: {len(image_ids)}")
print(f"Matching IDs: {len(matching_ids)}")
print(f"Non-Matching IDs: {len(non_matching_ids)}")

# Save the results to a text file
output_path = 'outputMatches.txt'  # Update this path
with open(output_path, 'w') as file:
    file.write("Matching IDs:\n")
    file.write("\n".join(matching_ids) + "\n\n")
    file.write("Non-Matching IDs:\n")
    file.write("\n".join(non_matching_ids) + "\n")

print(f"Results saved to {output_path}")
