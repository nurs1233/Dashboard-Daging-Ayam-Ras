import pandas as pd
import glob
import os
import re
from datetime import datetime

# Koordinat Provinsi di Indonesia untuk Visualisasi Peta
PROVINCE_COORDINATES = {
    'Aceh': [4.6951, 96.7494],
    'Sumatera Utara': [2.1121, 99.0557],
    'Sumatera Barat': [-0.7392, 100.8000],
    'Riau': [0.2933, 101.7068],
    'Jambi': [-1.6183, 103.6238],
    'Sumatera Selatan': [-3.3194, 103.9144],
    'Bengkulu': [-3.7928, 102.2608],
    'Lampung': [-4.5586, 105.4068],
    'Kepulauan Bangka Belitung': [-2.7410, 106.4406],
    'Kepulauan Riau': [3.9456, 108.1429],
    'DKI Jakarta': [-6.2088, 106.8456],
    'Jawa Barat': [-7.0909, 107.6689],
    'Jawa Tengah': [-7.1510, 110.1403],
    'Daerah Istimewa Yogyakarta': [-7.8753, 110.4262],
    'Jawa Timur': [-7.5361, 112.2384],
    'Banten': [-6.4058, 106.0605],
    'Bali': [-8.4095, 115.1889],
    'Nusa Tenggara Barat': [-8.6529, 117.3616],
    'Nusa Tenggara Timur': [-8.6574, 121.0794],
    'Kalimantan Barat': [-0.2784, 109.9754],
    'Kalimantan Tengah': [-1.6815, 113.3824],
    'Kalimantan Selatan': [-3.0926, 115.2838],
    'Kalimantan Timur': [0.5387, 116.4194],
    'Kalimantan Utara': [3.0731, 116.0414],
    'Sulawesi Utara': [0.6247, 123.9750],
    'Sulawesi Tengah': [-1.4300, 121.4456],
    'Sulawesi Selatan': [-3.9722, 119.8159],
    'Sulawesi Tenggara': [-4.1449, 122.1746],
    'Gorontalo': [0.6999, 122.4467],
    'Sulawesi Barat': [-2.8441, 119.2321],
    'Maluku': [-3.2385, 130.1453],
    'Maluku Utara': [1.5709, 127.8088],
    'Papua': [-4.2699, 138.0804],
    'Papua Barat': [-1.3361, 132.5753],
    'Papua Selatan': [-7.5000, 139.0000],
    'Papua Tengah': [-3.5000, 136.0000],
    'Papua Pegunungan': [-4.0000, 139.0000],
    'Papua Barat Daya': [-0.8000, 131.5000]
}

def load_single_csv(filepath):
    """Membaca file CSV hasil export Excel dengan struktur metadata di awal"""
    try:
        # File CSV memiliki 3 baris metadata, header mulai di baris ke-4 (index 3)
        df = pd.read_csv(filepath, skiprows=3)
        
        # Kolom pertama biasanya nama wilayah
        df = df.rename(columns={df.columns[0]: 'Wilayah'})
        
        # Hapus baris kosong atau baris 'Sumber Data' jika ada
        df = df[df['Wilayah'].notna()]
        df = df[~df['Wilayah'].str.contains('Sumber Data', na=False, case=False)]
        
        # Melt data dari format kolom tanggal ke format baris (long format)
        id_vars = ['Wilayah']
        date_cols = [c for c in df.columns if c not in id_vars and not c.startswith('Unnamed')]
        
        melted = df.melt(id_vars=id_vars, value_vars=date_cols, var_name='Tanggal', value_name='Harga')
        
        # Bersihkan data
        melted['Harga'] = pd.to_numeric(melted['Harga'], errors='coerce')
        melted['Tanggal'] = pd.to_datetime(melted['Tanggal'], errors='coerce')
        
        # Hapus data yang tidak valid (Harga 0 atau Tanggal null)
        melted = melted.dropna(subset=['Tanggal', 'Harga'])
        melted = melted[melted['Harga'] > 0]
        
        return melted
    except Exception as e:
        print(f"Gagal memuat {filepath}: {e}")
        return pd.DataFrame()

def load_all_data(data_folder='Data'):
    """Memuat semua file CSV dari folder Data"""
    # Cari file .csv (karena file yang diupload adalah CSV hasil export)
    csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
    
    if not csv_files:
        return pd.DataFrame()
    
    all_dfs = []
    for f in csv_files:
        df_part = load_single_csv(f)
        if not df_part.empty:
            all_dfs.append(df_part)
            
    if not all_dfs:
        return pd.DataFrame()
        
    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # Tambahkan koordinat
    full_df['Lat'] = full_df['Wilayah'].map(lambda x: PROVINCE_COORDINATES.get(x, [0,0])[0])
    full_df['Lon'] = full_df['Wilayah'].map(lambda x: PROVINCE_COORDINATES.get(x, [0,0])[1])
    
    # Tambahkan Prev_Harga untuk kalkulasi delta
    full_df = full_df.sort_values(['Wilayah', 'Tanggal'])
    full_df['Prev_Harga'] = full_df.groupby('Wilayah')['Harga'].shift(1)
    
    return full_df.reset_index(drop=True)
