import os
import pandas as pd
import re


def extract_nacc_id(name):
    match = re.search(r"NACC\d{6}", name)
    return match.group() if match else None


def get_naccids_from_folder(folder_path):
    nacc_ids = set()
    for name in os.listdir(folder_path):
        nacc_id = extract_nacc_id(name)
        if nacc_id:
            nacc_ids.add(nacc_id)
    return nacc_ids


def categorize_cdrglob(score):
    category_map = {
        0.0: "0_No_Alzheimers",
        0.5: "0.5_Cognitively_Impaired",
        1.0: "1_Mild",
        2.0: "2_Moderate",
        3.0: "3_Severe"
    }
    return category_map.get(score, "Unknown")


def analyze_patient_categories(folder_path, csv_path, output_excel):
    print(f"🔍 Scanning folder: {folder_path}")
    nacc_ids = get_naccids_from_folder(folder_path)
    print(f"🧠 Found {len(nacc_ids)} unique patients (NACCIDs) in folder.")

    df = pd.read_csv(csv_path)
    df['NACCID'] = df['NACCID'].astype(str).str.strip()
    df_map = dict(zip(df['NACCID'], df['CDRGLOB']))

    category_counts = {}
    summary_rows = []
    matched_count = 0

    for nacc_id in sorted(nacc_ids):
        if nacc_id in df_map:
            score = df_map[nacc_id]
            category = categorize_cdrglob(score)
            category_counts[category] = category_counts.get(category, 0) + 1
            matched_count += 1
        else:
            print(f"⚠️ NACCID {nacc_id} not found in CSV.")

    print("\n📊 Patients per Alzheimer's Category:")
    for category, count in sorted(category_counts.items()):
        print(f"{category}: {count} patients")
        summary_rows.append({"Category": category, "Patient Count": count})

    print(f"\n✅ Total matched in CSV: {matched_count}")
    print(f"🔎 Total NACCIDs scanned: {len(nacc_ids)}")

    # Save summary to Excel
    summary_df = pd.DataFrame(summary_rows)
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Summary')

    print(f"\n💾 Saved summary to Excel: {output_excel}")


def main():
    dicom_folder = "DICOM_cleaned_output"              # Folder with NACCID-named subfolders
    csv_path = "commercial_nacc65.csv"                     # Metadata CSV
    output_excel = "DICOM_cleaned_output\\summary.xlsx"  # Summary Excel

    analyze_patient_categories(dicom_folder, csv_path, output_excel)


if __name__ == "__main__":
    main()
