# data_loader.py
import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_all_data(data_folder="Data"):
    """
    Load semua file .xlsx dan .csv dari folder data_folder
    Returns: DataFrame gabungan atau DataFrame kosong jika tidak ada file
    """
    all_dfs = []
    
    # Cek apakah folder ada
    if not os.path.exists(data_folder):
        st.warning(f"⚠️ Folder '{data_folder}' tidak ditemukan!")
        return pd.DataFrame()
    
    # List semua file di folder
    files = os.listdir(data_folder)
    
    # Filter file Excel dan CSV
    excel_files = [f for f in files if f.endswith('.xlsx') or f.endswith('.xls')]
    csv_files = [f for f in files if f.endswith('.csv')]
    
    if not excel_files and not csv_files:
        st.warning(f"⚠️ Tidak ada file .xlsx atau .csv di folder '{data_folder}'")
        return pd.DataFrame()
    
    # Process Excel files
    for file in excel_files:
        try:
            file_path = os.path.join(data_folder, file)
            # skiprows=3 disesuaikan dengan struktur file Anda
            df = pd.read_excel(file_path, skiprows=3)
            df['source_file'] = file  # Tandai sumber file
            all_dfs.append(df)
            st.success(f"✅ Loaded: {file}")
        except Exception as e:
            st.error(f"❌ Error membaca {file}: {str(e)}")
            continue
    
    # Process CSV files
    for file in csv_files:
        try:
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path, skiprows=3)
            df['source_file'] = file
            all_dfs.append(df)
            st.success(f"✅ Loaded: {file}")
        except Exception as e:
            st.error(f"❌ Error membaca {file}: {str(e)}")
            continue
    
    # Gabungkan semua dataframe
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        st.info(f"📊 Total data: {len(combined_df)} baris dari {len(all_dfs)} file")
        return combined_df
    else:
        return pd.DataFrame()


@st.cache_data
def load_single_file(file_path):
    """
    Load satu file Excel/CSV secara individual
    """
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path, skiprows=3)
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path, skiprows=3)
    else:
        raise ValueError("Format file tidak didukung")
