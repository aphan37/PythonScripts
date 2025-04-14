import os

# Specify the path to the folder containing the images
image_folder = 'NACC_jpg'  # Update this path

# Initialize a set to store unique IDs
unique_ids = set()

# Iterate through the files in the folder
for file_name in os.listdir(image_folder):
    if file_name.endswith('.jpg'):  # Process only .jpg files
        # Extract the part of the filename before the first underscore
        id_part = file_name.split('_')[0]  # Get the part before the first underscore
        unique_ids.add(id_part)

# Count the total number of unique IDs
num_unique_ids = len(unique_ids)

# Output the results
print(f"Total unique IDs: {num_unique_ids}")
print("Unique IDs:")
print(unique_ids)

# Export the total unique IDs and the unique IDs to a text file
with open('uniqueID.txt', 'w') as f:
    f.write(f"Total unique IDs: {num_unique_ids}\n\n")  # Write the total number of unique IDs
    for unique_id in unique_ids:
        f.write(unique_id + '\n')  # Write each unique ID

print("Total unique IDs and the list of unique IDs have been exported to 'uniqueID.txt'.")
