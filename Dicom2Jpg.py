import os
import zipfile
import shutil
import re
import pydicom
from PIL import Image


def sanitize_filename(name, max_len=100):
    """
    Shortens the filename by removing long junk after multiple underscores.
    Keeps the first 2-3 parts, trims the rest.
    """
    base = os.path.basename(name)
    parts = base.split('_')
    if len(parts) > 3:
        base = '_'.join(parts[:3]) + os.path.splitext(base)[1]
    # Remove any trailing slashes and illegal characters just in case
    base = re.sub(r'[\\/*?:"<>|]', "", base)
    return base[:max_len]


def safe_extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                # Skip directories
                if member.is_dir():
                    continue

                # Sanitize filename
                original_filename = os.path.basename(member.filename)
                cleaned_name = sanitize_filename(original_filename)

                # Rebuild full safe path
                rel_dir = os.path.dirname(member.filename)
                safe_dir = os.path.join(extract_to, rel_dir)
                safe_path = os.path.join(safe_dir, cleaned_name)

                # Prevent zip slip
                if not os.path.abspath(safe_path).startswith(os.path.abspath(extract_to)):
                    print(f"❌ Unsafe path skipped: {safe_path}")
                    continue

                os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                with zip_ref.open(member) as source, open(safe_path, "wb") as target:
                    shutil.copyfileobj(source, target)

        print(f"✅ Extracted: {zip_path}")
    except Exception as e:
        print(f"❌ Failed to extract {zip_path}: {e}")


def extract_all_zips(base_path, output_base):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                folder_name = os.path.splitext(file)[0]
                extract_path = os.path.join(output_base, folder_name)
                safe_extract_zip(zip_path, extract_path)


def find_dicom_files(root_folder):
    dicom_files = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files


def convert_dicom_to_jpg(dicom_path, output_path):
    try:
        ds = pydicom.dcmread(dicom_path)
        pixel_array = ds.pixel_array
        image = Image.fromarray(pixel_array)
        image = image.convert("L")  # Convert to grayscale
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        print(f"🖼️ Converted to JPG: {output_path}")
    except Exception as e:
        print(f"❌ Failed to convert {dicom_path}: {e}")


def convert_dicom_files(extract_base, output_jpg_base):
    dicom_files = find_dicom_files(extract_base)
    print(f"🔍 Found {len(dicom_files)} DICOM files")

    for dicom_path in dicom_files:
        rel_path = os.path.relpath(dicom_path, extract_base)
        jpg_path = os.path.join(output_jpg_base, os.path.splitext(rel_path)[0] + ".jpg")
        convert_dicom_to_jpg(dicom_path, jpg_path)


def main():
    input_folder = "OneDrive_1_4-6-2025"
    extract_base = os.path.join(input_folder, "extracted_zips")
    output_jpg_folder = os.path.join(input_folder, "jpg_outputs")

    # Step 1: Extract all zips recursively
    extract_all_zips(input_folder, extract_base)

    # Step 2: Convert DICOM files to JPG
    convert_dicom_files(extract_base, output_jpg_folder)


if __name__ == "__main__":
    main()

