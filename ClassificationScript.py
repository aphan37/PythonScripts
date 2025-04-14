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
output_base_dir = 'Categorization'  # Update this path
if not os.path.exists(output_base_dir):
    os.mkdir(output_base_dir)

# Group the data by year and process each year separately
for year, group in df.groupby('VISITYR'):
    # Create a folder for the year
    year_folder = os.path.join(output_base_dir, str(year))
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)

    # Group by NACCID for this year and write to separate files
    for naccid, patient_group in group.groupby('NACCID'):
        # Combine the diagnosis information for this patient
        diagnoses = [
            f"{row['VISITYR']} - {row['AlzheimerClassification']}"
            for _, row in patient_group.iterrows()
        ]

        # Create a text file for this patient
        patient_file_path = os.path.join(year_folder, f"{naccid}.txt")
        with open(patient_file_path, 'w') as file:
            file.write(f"Patient ID: {naccid}\n")
            file.write("Diagnoses:\n")
            for diagnosis in diagnoses:
                file.write(f"- {diagnosis}\n")

print(f"Data has been written to folders in {output_base_dir}")
