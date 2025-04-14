import pandas as pd
import os

# Load the original CSV file
csv_path = 'commercial_nacc65a.csv'  # Update this path
df = pd.read_csv(csv_path)

# Map CDRGLOB values to categories
alzheimers_category = {
    0: 'No Alzheimers',
    0.5: 'Mild',
    1: 'Cognitively Intact',
    2: 'Moderate',
    3: 'Severe'
}

# Add a column with mapped categories
df['AlzheimerClassification'] = df['CDRGLOB'].map(alzheimers_category)

# Define the base output directory
output_base_dir = 'typeClassified'  # Update this path
if not os.path.exists(output_base_dir):
    os.mkdir(output_base_dir)

# Filter the data for years 2021, 2022, and 2023
df_filtered_years = df[df['VISITYR'].isin([2021, 2022, 2023])]

# Group by year and Alzheimer classification
for year, year_group in df_filtered_years.groupby('VISITYR'):
    # Create a folder for the year
    year_folder = os.path.join(output_base_dir, str(year))
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)

    # Create subfolders for each Alzheimer’s category (No Alzheimers, Mild, etc.)
    for category_code, category_name in alzheimers_category.items():
        category_folder = os.path.join(year_folder, category_name)
        if not os.path.exists(category_folder):
            os.mkdir(category_folder)

        # Filter patients for this category and year
        category_patients = year_group[year_group['CDRGLOB'] == category_code]

        # Save patient IDs to the corresponding category folder
        for _, row in category_patients.iterrows():
            patient_id = row['NACCID']
            # Create a file for each patient ID if it doesn't exist
            patient_file_path = os.path.join(category_folder, f"{patient_id}.txt")
            with open(patient_file_path, 'a') as file:
                file.write(f"Patient ID: {patient_id}\n")

print(f"Patient data has been written to {output_base_dir}")
