import os
import zipfile
import shutil
import re
import hashlib


def extract_nacc_id(name):
    """Extract NACC ID from any filename or folder"""
    match = re.search(r"NACC\d{6}", name)
    return match.group() if match else None


def long_path(path):
    """Ensure compatibility with Windows long paths"""
    try:
        abs_path = os.path.abspath(path)
        if os.name == 'nt' and len(abs_path) > 240:
            return r"\\?\{}".format(abs_path)
        return abs_path
    except Exception as e:
        print(f"⚠️ Invalid path skipped: {path} ({e})")
        return path  # fallback


def unzip_file(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ Unzipped: {zip_path} ➜ {extract_to}")
    except Exception as e:
        print(f"❌ Failed to unzip {zip_path}: {e}")


def safe_extract_zip_to_naccid(zip_path, extract_root):
    try:
        zip_name = os.path.basename(zip_path)
        folder_naccid = extract_nacc_id(zip_name)
        if not folder_naccid:
            print(f"⚠️ Skipped (no NACC ID in zip name): {zip_name}")
            return

        extract_path = long_path(os.path.join(extract_root, folder_naccid))
        os.makedirs(os.path.dirname(extract_path), exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                if member.is_dir():
                    continue

                # Try to extract NACC ID from filename or fallback to folder
                nacc_id = extract_nacc_id(member.filename) or folder_naccid
                ext = os.path.splitext(member.filename)[1]
                filename = f"{nacc_id}{ext}"

                safe_path = long_path(os.path.join(extract_path, filename))

                # Avoid overwriting with hash if name repeats
                if os.path.exists(safe_path):
                    short_hash = hashlib.md5(member.filename.encode()).hexdigest()[:6]
                    filename = f"{nacc_id}_{short_hash}{ext}"
                    safe_path = long_path(os.path.join(extract_path, filename))

                os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                with zip_ref.open(member) as source, open(safe_path, "wb") as target:
                    shutil.copyfileobj(source, target)

        print(f"✅ Clean-extracted: {zip_path} ➜ {extract_path}")
    except Exception as e:
        print(f"❌ Failed to extract {zip_path}: {e}")


def process_main_zip(main_zip_path, temp_extract_dir, final_output_dir):
    # Step 1: Unzip the main archive
    unzip_file(main_zip_path, temp_extract_dir)

    # Step 2: Find all .zip files inside and extract to NACCID folders
    for root, dirs, files in os.walk(temp_extract_dir):
        for file in files:
            if file.endswith(".zip"):
                inner_zip_path = os.path.join(root, file)
                safe_extract_zip_to_naccid(inner_zip_path, final_output_dir)


def main():
    main_zip = "DICOM_0417.zip"
    temp_folder = "C:\\extraction_temp"         # Keep root-level for short path
    clean_output = "C:\\DICOM_cleaned_output"   # Final cleaned location

    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(clean_output, exist_ok=True)

    process_main_zip(main_zip, temp_folder, clean_output)


if __name__ == "__main__":
    main()
