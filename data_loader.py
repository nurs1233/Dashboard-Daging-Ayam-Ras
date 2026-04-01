import pandas as pd
import glob
import os
from datetime import datetime

# Koordinat Provinsi di Indonesia untuk Visualisasi Peta
PROVINCE_COORDINATES = {
    'Aceh': [4.6951, 96.7494], 'Sumatera Utara': [2.1121, 99.0557], 'Sumatera Barat': [-0.7392, 100.8000],
    'Riau': [0.2933, 101.7068], 'Jambi': [-1.6183, 103.6238], 'Sumatera Selatan': [-3.3194, 103.9144],
    'Bengkulu': [-3.7928, 102.2608], 'Lampung': [-4.5586, 105.4068], 'Kepulauan Bangka Belitung': [-2.7410, 106.4406],
    'Kepulauan Riau': [3.9456, 108.1429], 'DKI Jakarta': [-6.2088, 106.8456], 'Jawa Barat': [-7.0909, 107.6689],
    'Jawa Tengah': [-7.1510, 110.1403], 'Daerah Istimewa Yogyakarta': [-7.8753, 110.4262], 'Jawa Timur': [-7.5361, 112.2384],
    'Banten': [-6.4058, 106.0605], 'Bali': [-8.4095, 115.1889], 'Nusa Tenggara Barat': [-8.6529, 117.3616],
    'Nusa Tenggara Timur': [-8.6574, 121.0794], 'Kalimantan Barat': [-0.2784, 109.9754], 'Kalimantan Tengah': [-1.6815, 113.3824],
    'Kalimantan Selatan': [-3.0926, 115.2838], 'Kalimantan Timur': [0.5387, 116.4194], 'Kalimantan Utara': [3.0731, 116.0414],
    'Sulawesi Utara': [0.6247, 123.9750], 'Sulawesi Tengah': [-1.4300, 121.4456], 'Sulawesi Selatan': [-3.9722, 119.8159],
    'Sulawesi Tenggara': [-4.1449, 122.1746], 'Gorontalo': [0.6999, 122.4467], 'Sulawesi Barat': [-2.8441, 119.2321],
    'Maluku': [-3.2385, 130.1453], 'Maluku Utara': [1.5709, 127.8088], 'Papua': [-4.2699, 138.0804],
    'Papua Barat': [-1.3361, 132.5753], 'Papua Selatan': [-7.5000, 139.0000], 'Papua Tengah': [-3.5000, 136.0000],
    'Papua Pegunungan': [-4.0000, 139.0000], 'Papua Barat Daya': [-0.8000, 131.5000]
}

def load_single_file(filepath):
    """Membaca file (CSV atau XLSX) dan mengolahnya menjadi format panjang (long format)"""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        
        # Baca file sesuai ekstensi
        if ext == '.csv':
            # Coba deteksi header dengan membaca beberapa baris awal
            df_test = pd.read_csv(filepath, nrows=10)
            skip_n = 0
            for i, row in df_test.iterrows():
                if any(str(val).strip().lower() in ['wilayah', 'no', 'provinsi'] for val in row.values):
                    skip_n = i + 1
                    break
            df = pd.read_csv(filepath, skiprows=skip_n if skip_n > 0 else 3)
        else:
            # Untuk Excel, biasanya metadata ada di 3-5 baris pertama
            df = pd.read_excel(filepath, skiprows=3)

        # Cari kolom Wilayah/Provinsi
        if 'Wilayah' not in df.columns:
            for col in df.columns:
                # Cek jika kolom mengandung nama provinsi populer
                if df[col].astype(str).str.contains('Jakarta|Jawa|Bali|Papua', na=False).any():
                    df = df.rename(columns={col: 'Wilayah'})
                    break
        
        if 'Wilayah' not in df.columns:
            return pd.DataFrame()

        # Bersihkan baris non-data
        df = df[df['Wilayah'].notna()]
        df = df[~df['Wilayah'].astype(str).str.contains('Sumber|Keterangan|Total|Rata-rata', na=False, case=False)]
        
        # Identifikasi kolom tanggal (biasanya format string atau datetime)
        id_vars = ['Wilayah']
        # Kolom tanggal adalah semua kolom kecuali 'Wilayah' dan kolom index/nomor
        date_cols = [c for c in df.columns if c != 'Wilayah' and not str(c).startswith('Unnamed')]
        
        melted = df.melt(id_vars=id_vars, value_vars=date_cols, var_name='Tanggal', value_name='Harga')
        
        # Bersihkan Harga (hilangkan titik ribuan jika string)
        if melted['Harga'].dtype == object:
            melted['Harga'] = melted['Harga'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        
        melted['Harga'] = pd.to_numeric(melted['Harga'], errors='coerce')
        
        # Bersihkan Tanggal
        # Terkadang Excel mengimpor tanggal sebagai angka (serial), pandas to_datetime biasanya menangani ini
        melted['Tanggal'] = pd.to_datetime(melted['Tanggal'], errors='coerce')
        
        # Drop baris yang tidak valid
        melted = melted.dropna(subset=['Tanggal', 'Harga'])
        melted = melted[melted['Harga'] > 0]
        
        return melted
    except Exception as e:
        print(f"Error pada file {filepath}: {e}")
        return pd.DataFrame()

def load_all_data(base_path):
    """Mencari semua file di folder Data dengan ekstensi .xlsx atau .csv"""
    data_dir = os.path.join(base_path, 'Data')
    
    # Cari file .xlsx dan .csv
    files = glob.glob(os.path.join(data_dir, '*.xlsx')) + glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not files:
        # Coba cari di root jika tidak ketemu di folder Data
        files = glob.glob(os.path.join(base_path, '*.xlsx')) + glob.glob(os.path.join(base_path, '*.csv'))

    if not files:
        return pd.DataFrame()
    
    all_dfs = []
    for f in files:
        # Lewati file sementara (temp files) yang dibuat Excel
        if os.path.basename(f).startswith('~$'): continue
        
        df_part = load_single_file(f)
        if not df_part.empty:
            all_dfs.append(df_part)
            
    if not all_dfs:
        return pd.DataFrame()
        
    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # Normalisasi nama wilayah (hapus spasi berlebih)
    full_df['Wilayah'] = full_df['Wilayah'].astype(str).str.strip()
    
    # Tambahkan Geodata
    full_df['Lat'] = full_df['Wilayah'].map(lambda x: PROVINCE_COORDINATES.get(x, [None, None])[0])
    full_df['Lon'] = full_df['Wilayah'].map(lambda x: PROVINCE_COORDINATES.get(x, [None, None])[1])
    
    # Hitung Delta
    full_df = full_df.sort_values(['Wilayah', 'Tanggal'])
    full_df['Prev_Harga'] = full_df.groupby('Wilayah')['Harga'].shift(1)
    
    return full_df.reset_index(drop=True)
