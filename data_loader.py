import pandas as pd
import glob
import os

def load_all_data(data_folder="Data"):
    """
    Load all Excel/CSV files from the specified folder.
    Automatically detects 'Wilayah' and melts date columns into rows.
    """
    # Deteksi file .xlsx dan .csv
    pattern_xlsx = os.path.join(data_folder, "*.xlsx")
    pattern_csv = os.path.join(data_folder, "*.csv")
    files = glob.glob(pattern_xlsx) + glob.glob(pattern_csv)
    
    if not files:
        raise FileNotFoundError(f"Tidak ada file .xlsx atau .csv ditemukan di folder '{data_folder}'.")

    all_data = []
    for file in files:
        # Baca file dan skip 3 baris pertama karena merupakan judul/metadata laporan
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file, skiprows=3)
            else:
                df = pd.read_excel(file, skiprows=3)
        except Exception as e:
            print(f"Gagal membaca file {file}: {e}")
            continue

        if df.empty:
            print(f"File {file} kosong, dilewati.")
            continue

        # Validasi minimal ada kolom 'Wilayah'
        if 'Wilayah' not in df.columns:
            print(f"File {file} tidak memiliki kolom 'Wilayah'. Dilewati.")
            continue

        # Cleansing baris non-data (misal teks "Sumber Data : ...") di baris bawah
        df = df.dropna(subset=['Wilayah'])
        df = df[~df['Wilayah'].astype(str).str.contains('Sumber Data', case=False, na=False)]
        
        # Melt data: Ubah dari Wide format (tanggal sebagai kolom) ke Long format
        # Ambil semua nama kolom kecuali 'Wilayah' dan kolom-kolom 'Unnamed' (sisa koma di csv)
        date_columns = [col for col in df.columns if col != 'Wilayah' and not str(col).startswith('Unnamed')]
        
        df_melted = pd.melt(
            df, 
            id_vars=['Wilayah'], 
            value_vars=date_columns, 
            var_name='Tanggal', 
            value_name='Harga'
        )

        # Konversi tipe data
        df_melted['Tanggal'] = pd.to_datetime(df_melted['Tanggal'], errors='coerce')
        df_melted['Harga'] = pd.to_numeric(df_melted['Harga'], errors='coerce')
        df_melted['Wilayah'] = df_melted['Wilayah'].astype(str).str.strip()

        # Cleansing: Hapus baris dengan tanggal/harga yang tidak valid, atau harga = 0
        sebelum = len(df_melted)
        df_melted = df_melted.dropna(subset=['Tanggal', 'Harga'])
        df_melted = df_melted[df_melted['Harga'] > 0]  # Abaikan harga 0
        setelah = len(df_melted)
        
        if setelah < sebelum:
            print(f"File {os.path.basename(file)}: menghapus {sebelum - setelah} baris data kosong/0.")

        if not df_melted.empty:
            all_data.append(df_melted)

    if not all_data:
        raise ValueError("Tidak ada data yang berhasil dimuat. Periksa struktur file data Anda.")

    # Gabungkan semua data dari semua file
    combined_df = pd.concat(all_data, ignore_index=True)
    
    return combined_df
