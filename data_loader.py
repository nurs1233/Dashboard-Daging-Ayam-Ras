import pandas as pd
import glob
import os
import re

def load_all_data(data_folder="Data"):
    """
    Load all Excel files from the specified folder that match the pattern:
    Statistik_Harian_*.xlsx (or any Excel file)
    Automatically detect columns for date, region, and price.
    """
    pattern = os.path.join(data_folder, "*.xlsx")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"Tidak ada file Excel ditemukan di folder '{data_folder}'.")

    all_data = []
    for file in files:
        # Read Excel file
        try:
            df = pd.read_excel(file)
        except Exception as e:
            print(f"Gagal membaca file {file}: {e}")
            continue

        if df.empty:
            print(f"File {file} kosong, dilewati.")
            continue

        # Detect column names based on keywords
        col_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'tanggal' in col_lower or 'date' in col_lower:
                col_mapping['tanggal'] = col
            elif 'wilayah' in col_lower or 'region' in col_lower or 'daerah' in col_lower:
                col_mapping['wilayah'] = col
            elif 'harga' in col_lower or 'price' in col_lower:
                col_mapping['harga'] = col

        # If missing critical columns, skip this file
        if not all(k in col_mapping for k in ['tanggal', 'wilayah', 'harga']):
            print(f"File {file} tidak memiliki kolom yang diperlukan (tanggal, wilayah, harga). Dilewati.")
            continue

        # Rename to standard names
        df = df.rename(columns={col_mapping['tanggal']: 'tanggal',
                                col_mapping['wilayah']: 'wilayah',
                                col_mapping['harga']: 'harga'})

        # Extract date range from filename if possible
        basename = os.path.basename(file)
        # Pattern: Statistik_Harian_YYYYMMDD__YYYYMMDD_...
        match = re.search(r'(\d{8})__(\d{8})', basename)
        if match:
            start_date_str, end_date_str = match.groups()
            start_date = pd.to_datetime(start_date_str, format='%Y%m%d')
            end_date = pd.to_datetime(end_date_str, format='%Y%m%d')
        else:
            start_date = None
            end_date = None

        # Convert data types
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df['harga'] = pd.to_numeric(df['harga'], errors='coerce')
        df['wilayah'] = df['wilayah'].astype(str).str.strip()

        # Drop rows with invalid date or price
        before = len(df)
        df = df.dropna(subset=['tanggal', 'harga'])
        after = len(df)
        if after < before:
            print(f"File {file}: menghapus {before - after} baris dengan tanggal/harga tidak valid.")

        if df.empty:
            continue

        # Add metadata
        df['source_file'] = basename
        df['start_date'] = start_date
        df['end_date'] = end_date

        all_data.append(df)

    if not all_data:
        raise ValueError("Tidak ada data yang berhasil dimuat. Periksa struktur file Excel.")

    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df
