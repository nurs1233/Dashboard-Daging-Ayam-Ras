import pandas as pd
import glob
import os
import re
import numpy as np

def load_all_data(data_folder="Data"):
    """
    Load all Excel files, detect columns, clean data, and combine.
    """
    pattern = os.path.join(data_folder, "*.xlsx")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"Tidak ada file Excel (*.xlsx) ditemukan di folder '{data_folder}'.")

    all_data = []
    
    # Regex lebih fleksibel: menerima 1 atau lebih underscore/pemisah
    date_pattern = re.compile(r'(\d{8})[_-]+(\d{8})')

    for file in files:
        try:
            # Tambahkan engine='openpyxl' untuk memastikan kompatibilitas .xlsx
            df = pd.read_excel(file, engine='openpyxl') 
        except Exception as e:
            print(f"[ERROR] Gagal membaca file {file}: {e}")
            continue

        if df.empty:
            print(f"[SKIP] File {file} kosong.")
            continue

        # 1. Bersihkan nama kolom (strip spasi)
        df.columns = df.columns.str.strip()

        # 2. Deteksi kolom (Ambil yang PERTAMA ditemukan untuk menghindari ambiguitas)
        col_mapping = {}
        keywords = {
            'tanggal': ['tanggal', 'date', 'time'],
            'wilayah': ['wilayah', 'region', 'daerah', 'lokasi', 'provinsi'],
            'harga': ['harga', 'price', 'nilai', 'cost']
        }

        for col in df.columns:
            col_lower = col.lower()
            for key, words in keywords.items():
                if key not in col_mapping:  # Hanya isi jika belum ada
                    if any(word in col_lower for word in words):
                        col_mapping[key] = col
                        break 
        
        # Validasi kolom wajib
        required_cols = ['tanggal', 'wilayah', 'harga']
        if not all(k in col_mapping for k in required_cols):
            missing = [k for k in required_cols if k not in col_mapping]
            print(f"[SKIP] File {file} kekurangan kolom: {missing}. Dilewati.")
            continue

        # Rename kolom
        df = df.rename(columns={col_mapping[k]: k for k in required_cols})
        
        # 3. Ekstrak metadata dari filename
        basename = os.path.basename(file)
        match = date_pattern.search(basename)
        start_date = pd.NaT
        end_date = pd.NaT
        
        if match:
            try:
                s_str, e_str = match.groups()
                start_date = pd.to_datetime(s_str, format='%Y%m%d')
                end_date = pd.to_datetime(e_str, format='%Y%m%d')
            except Exception:
                pass # Biarkan NaT jika parsing gagal

        # 4. Konversi Tipe Data & Pembersihan
        # dayfirst=True penting untuk format DD/MM/YYYY khas Indonesia
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce', dayfirst=True)
        df['harga'] = pd.to_numeric(df['harga'], errors='coerce')
        df['wilayah'] = df['wilayah'].astype(str).str.strip().str.title() # Title case untuk konsistensi
        
        # Drop baris invalid
        initial_count = len(df)
        df = df.dropna(subset=['tanggal', 'harga', 'wilayah']) # Wilayah juga harus ada
        df = df[df['wilayah'].str.lower() != 'nan'] # Hindari string 'nan'
        
        dropped_count = initial_count - len(df)
        if dropped_count > 0:
            print(f"[CLEAN] File {file}: menghapus {dropped_count} baris invalid.")

        if df.empty:
            continue

        # 5. Tambahkan Metadata
        df['source_file'] = basename
        df['file_start_date'] = start_date
        df['file_end_date'] = end_date

        all_data.append(df)

    if not all_data:
        raise ValueError("Tidak ada data valid yang berhasil dimuat dari semua file.")

    # 6. Gabungkan dan Hapus Duplikat
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Hapus duplikat berdasarkan Tanggal + Wilayah (ambil data terakhir jika ada konflik)
    before_dup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['tanggal', 'wilayah'], keep='last')
    after_dup = len(combined_df)
    
    if after_dup < before_dup:
        print(f"[INFO] Ditemukan {before_dup - after_dup} data duplikat (tanggal+wilayah) dan telah dibersihkan.")

    # Urutkan data agar rapi
    combined_df = combined_df.sort_values(by=['tanggal', 'wilayah']).reset_index(drop=True)

    return combined_df
