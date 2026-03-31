# Dashboard Harga Daging Ayam Ras

Dashboard interaktif untuk memvisualisasikan data harga daging ayam ras dari berbagai wilayah di Indonesia.

## Fitur

- **Auto-detect Data**: Secara otomatis mendeteksi dan memuat semua file Excel dari folder `Data/`
- **Filter Interaktif**: Filter berdasarkan tanggal dan wilayah
- **Visualisasi Chart**:
  - Line chart: Tren harga over time per wilayah
  - Bar chart: Rata-rata harga per wilayah
  - Heatmap: Distribusi harga per wilayah dan tanggal
  - Box plot: Distribusi statistik harga per wilayah
- **Export Data**: Download data yang sudah difilter dalam format CSV
- **Statistik Ringkas**: Min, Max, Mean, Median, Std Dev per wilayah

## Cara Menjalankan

1. Pastikan dependencies terinstall:
```bash
pip install pandas openpyxl plotly streamlit
```

2. Jalankan aplikasi Streamlit:
```bash
streamlit run app.py
```

3. Buka browser dan akses `http://localhost:8501`

## Struktur Data

Aplikasi ini secara otomatis membaca semua file Excel dengan pattern:
`Statistik_Harian_YYYYMMDD__YYYYMMDD_Daging_Ayam_Ras.xlsx`

dari folder `Data/`.

## File

- `data_loader.py`: Module untuk loading dan preprocessing data
- `app.py`: Aplikasi dashboard Streamlit
- `Data/`: Folder berisi file Excel sumber data
