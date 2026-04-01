import pandas as pd
import os

def load_all_data(data_folder="."):
    """
    Load all Excel/CSV files from the application.
    Menggunakan pencarian rekursif (os.walk) agar kebal terhadap error 
    case-sensitivity di Streamlit Cloud (Linux).
    """
    # Mundur ke root folder jika app.py mengirim path dengan embel-embel /Data
    base_search_path = data_folder
    if data_folder.endswith("Data") or data_folder.endswith("data"):
        base_search_path = os.path.dirname(data_folder)
        
    # Jika masih string kosong, paksa ke current directory
    if not base_search_path:
        base_search_path = "."

    # 1. Cari semua file CSV dan XLSX di seluruh sub-folder
    files = []
    for root, dirs, filenames in os.walk(base_search_path):
        # Abaikan folder sistem/hidden agar pencarian cepat
        if '/.' in root or '\\.' in root or 'venv' in root or '__pycache__' in root:
            continue
        for f in filenames:
            if f.endswith('.csv') or f.endswith('.xlsx'):
                files.append(os.path.join(root, f))
    
    if not files:
        # Tampilkan isi folder root untuk mempermudah debugging jika file benar-benar tidak ada
        try:
            available_items = os.listdir(base_search_path)
            raise FileNotFoundError(f"TIDAK ADA file .xlsx atau .csv! Isi folder '{base_search_path}' saat ini: {available_items}")
        except Exception as e:
            raise FileNotFoundError(f"Gagal melacak direktori. Pastikan Anda sudah mengunggah file data ke GitHub. Error: {e}")

    # 2. Proses semua file yang ditemukan
    all_data = []
    for file in files:
        # Skip 3 baris pertama (metadata text dari sumber data)
        try:
            if file.endswith('.csv'):
                df = pd.read_csv(file, skiprows=3)
            else:
                df = pd.read_excel(file, skiprows=3)
        except Exception as e:
            print(f"Gagal membaca {file}: {e}")
            continue

        if df.empty:
            continue

        # Deteksi kolom 'Wilayah' (case insensitive)
        if 'Wilayah' not in df.columns:
            wilayah_col = [c for c in df.columns if 'wilayah' in str(c).lower()]
            if wilayah_col:
                df = df.rename(columns={wilayah_col[0]: 'Wilayah'})
            else:
                continue

        # Cleansing baris non-data ("Sumber Data : SP2KP...")
        df = df.dropna(subset=['Wilayah'])
        df = df[~df['Wilayah'].astype(str).str.contains('Sumber Data', case=False, na=False)]
        
        # Melt data: Wide (tanggal di kolom) -> Long (tanggal jadi baris)
        date_columns = [col for col in df.columns if col != 'Wilayah' and not str(col).startswith('Unnamed')]
        df_melted = pd.melt(
            df, id_vars=['Wilayah'], value_vars=date_columns, 
            var_name='Tanggal', value_name='Harga'
        )

        # Standardisasi data
        df_melted['Tanggal'] = pd.to_datetime(df_melted['Tanggal'], errors='coerce')
        if df_melted['Harga'].dtype == 'object':
            df_melted['Harga'] = df_melted['Harga'].astype(str).str.replace(',', '').str.replace('.', '')
            
        df_melted['Harga'] = pd.to_numeric(df_melted['Harga'], errors='coerce')
        df_melted['Wilayah'] = df_melted['Wilayah'].astype(str).str.strip()

        # Buang baris invalid & harga 0
        df_melted = df_melted.dropna(subset=['Tanggal', 'Harga'])
        df_melted = df_melted[df_melted['Harga'] > 0]
        
        if not df_melted.empty:
            all_data.append(df_melted)

    # 3. Validasi akhir sebelum return
    if not all_data:
        raise ValueError(f"File ditemukan, tapi tidak ada data yang valid untuk dibaca. File yg di-scan: {[os.path.basename(f) for f in files]}")

    combined_df = pd.concat(all_data, ignore_index=True)
    
    # 4. Injeksi kolom Lat/Lon kosong untuk mencegah error st.map/plotly map di app.py
    if 'Lat' not in combined_df.columns:
        combined_df['Lat'] = None
    if 'Lon' not in combined_df.columns:
        combined_df['Lon'] = None
        
    return combined_df
