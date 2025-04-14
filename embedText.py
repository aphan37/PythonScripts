import os
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

# Specify file paths
unique_ids_path = 'uniquePatientData.xlsx'
classification_path = 'commercial_nacc65a.csv'
image_folder = 'NACC_jpg'
output_base_folder = 'labeledNACCImages'

# Load the unique IDs from the Excel file
unique_ids_df = pd.read_excel(unique_ids_path)
if 'NACCID' not in unique_ids_df.columns:
    raise ValueError("The unique IDs file must contain a column named 'NACCID'.")

unique_ids = set(unique_ids_df['NACCID'].astype(str))

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

classification_df['Type'] = classification_df['CDRGLOB'].map(alzheimers_category)

# Filter and handle duplicate NACCIDs
classification_filtered = classification_df[classification_df['NACCID'].astype(str).isin(unique_ids)]
classification_filtered = classification_filtered.drop_duplicates(subset='NACCID', keep='first')

# Create a dictionary mapping NACCID to classification info
id_to_classification = classification_filtered.set_index('NACCID')[['CDRGLOB', 'Type']].to_dict('index')

# Create the base output folder
if not os.path.exists(output_base_folder):
    os.mkdir(output_base_folder)

# Define font for the labels
try:
    font = ImageFont.truetype("arial.ttf", 24)
except IOError:
    font = ImageFont.load_default()

# Process and label each image
for file_name in os.listdir(image_folder):
    if file_name.endswith('.jpg'):
        base_id = file_name.split('_')[0]

        if base_id in id_to_classification:
            classification_info = id_to_classification[base_id]
            classification_number = classification_info['CDRGLOB']
            classification_label = classification_info['Type']

            src_path = os.path.join(image_folder, file_name)
            img = Image.open(src_path)

            draw = ImageDraw.Draw(img)
            text = f"NACCID: {base_id}\nType: {classification_number}\nClassification: {classification_label}"
            draw.multiline_text((10, 10), text, fill="white", font=font)

            output_path = os.path.join(output_base_folder, file_name)
            img.save(output_path)

print(f"Labeled images saved to {output_base_folder}")
