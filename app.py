import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, datetime
import os
import numpy as np

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Agrarian Intelligence | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS KUSTOM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif !important; 
        background-color: #F8FAF9 !important;
    }
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Manrope', sans-serif !important; 
        color: #012D1D !important;
    }
    
    header[data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    
    .top-nav { 
        background: linear-gradient(135deg, #ffffff 0%, #F8FAF9 100%); 
        padding: 1rem 2.5rem; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        border-bottom: 1px solid #E8EDEA; 
        margin: -2.5rem -2.5rem 2rem -2.5rem; 
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(10px);
    }
    .top-nav-brand { 
        font-family: 'Manrope', sans-serif; 
        font-weight: 800; 
        font-size: 1.35rem; 
        color: #012D1D; 
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-nav-brand::before { content: "🐔"; font-size: 1.2rem; }
    .top-nav-links { 
        color: #5B6B63; 
        font-size: 13px; 
        font-weight: 600;
        display: flex;
        gap: 24px;
    }
    .top-nav-links span { cursor: pointer; transition: color 0.2s; padding: 4px 0; }
    .top-nav-links span:hover { color: #16A34A; }
    
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #012D1D 0%, #0A3D2E 100%) !important; 
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #D8F3DC !important; }
    
    .live-badge { 
        display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px;
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        border-radius: 20px; margin-bottom: 12px; border: 1px solid #86EFAC;
    }
    .pulse { 
        width: 8px; height: 8px; background: #16A34A; border-radius: 50%; 
        animation: pulse 2s infinite; box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4);
    }
    @keyframes pulse { 
        0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 
        70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); } 
        100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } 
    }
    
    .bento-card { 
        background: linear-gradient(145deg, #ffffff 0%, #FAFBFA 100%); 
        border-radius: 16px; padding: 1.5rem; 
        box-shadow: 0 4px 20px rgba(1, 45, 29, 0.08); 
        height: 100%; border: 1px solid #E8EDEA;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .bento-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(1, 45, 29, 0.12); }
    
    .metric-card { display: flex; flex-direction: column; justify-content: space-between; min-height: 130px; position: relative; }
    .metric-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
    .border-secondary::before { background: linear-gradient(180deg, #8E4E14, #C47A2E); }
    .border-success::before { background: linear-gradient(180deg, #16A34A, #22C55E); }
    .border-error::before { background: linear-gradient(180deg, #BA1A1A, #EF4444); }
    .border-primary::before { background: linear-gradient(180deg, #012D1D, #0A3D2E); }
    
    .chart-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid #E8EDEA;
    }
    .chart-title { font-size: 1.1rem; font-weight: 700; color: #012D1D; margin: 0; display: flex; align-items: center; gap: 8px; }
    .chart-subtitle { color: #6B7A72; font-size: 0.85rem; margin: 4px 0 0 0; }
    
    .footer { text-align: center; margin-top: 3rem; padding: 2rem; border-top: 1px solid #E8EDEA; color: #6B7A72; font-size: 0.85rem; }
    
    .stButton > button {
        background: linear-gradient(135deg, #16A34A 0%, #0A3D2E 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 600 !important; padding: 0.5rem 1.5rem !important;
        transition: transform 0.1s, box-shadow 0.2s !important;
    }
    .stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

# --- TOP NAVIGATION ---
st.markdown("""
<div class="top-nav">
    <div class="top-nav-brand">Agrarian Intelligence</div>
    <div class="top-nav-links">
        <span>📊 Dashboard</span>
        <span>🔍 Analysis</span>
        <span>📑 Reports</span>
        <span>⚙️ Settings</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- FUNGSI UTILITAS ---
def calculate_sma(series, window):
    return series.rolling(window=window, min_periods=1).mean()

def calculate_ema(series, span):
    return series.ewm(span=span, min_periods=1).mean()

def calculate_bollinger(series, window=20, num_std=2):
    sma = calculate_sma(series, window)
    std = series.rolling(window=window, min_periods=1).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def detect_anomalies_zscore(series, threshold=2.5):
    rolling_mean = series.rolling(window=20, min_periods=1).mean()
    rolling_std = series.rolling(window=20, min_periods=1).std()
    z_score = (series - rolling_mean) / rolling_std.replace(0, np.nan)
    return z_score.abs() > threshold, z_score

def get_holiday_annotations(date_range):
    """Return list of Indonesian holidays for chart annotation"""
    holidays = {
        '2026-01-01': 'Tahun Baru',
        '2026-01-29': 'Maulid Nabi',
        '2026-02-26': 'Mulai Ramadan',
        '2026-03-29': 'Hari Raya Nyepi',
        '2026-03-30': 'Wafat Isa Al-Masih',
        '2026-04-01': 'Isra Mi\'raj',
        '2026-04-10': 'Jumat Agung',
        '2026-04-11': 'Paskah',
        '2026-05-01': 'Hari Buruh',
        '2026-05-21': 'Kenaikan Isa',
        '2026-05-29': 'Waisak',
        '2026-06-06': 'Idul Fitri (Est)',
        '2026-06-07': 'Idul Fitri+1',
        '2026-08-17': 'HUT RI',
        '2026-08-27': 'Idul Adha (Est)',
        '2026-09-16': 'Tahun Baru Islam',
        '2026-11-15': 'Maulid Nabi',
        '2026-12-25': 'Natal',
    }
    annotations = []
    for date_str, name in holidays.items():
        try:
            date = pd.to_datetime(date_str)
            if date_range[0] <= date <= date_range[1]:
                annotations.append((date, name))
        except:
            pass
    return annotations

@st.cache_data
def load_all_data():
    base_search_path = "."
    files = []
    for root, dirs, filenames in os.walk(base_search_path):
        if '/.' in root or '\\.' in root or 'venv' in root or '__pycache__' in root:
            continue
        for f in filenames:
            if f.endswith('.csv') or (f.endswith('.xlsx') and not f.startswith('~$')):
                files.append(os.path.join(root, f))
    
    if not files:
        raise FileNotFoundError("TIDAK ADA file .xlsx atau .csv ditemukan!")

    all_data, file_errors = [], []
    
    for file in files:
        df = None
        err = None
        try:
            if file.endswith('.csv'):
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                header_idx = next((i for i, line in enumerate(lines[:30]) if 'wilayah' in line.lower()), -1)
                if header_idx != -1:
                    df = pd.read_csv(file, skiprows=header_idx, dtype=str)
                    df = df.drop(columns=[c for c in df.columns if 'unnamed' in str(c).lower() or pd.isna(c)])
                else:
                    err = "Kata 'Wilayah' tidak ditemukan di 30 baris pertama."
            elif file.endswith('.xlsx'):
                xls = pd.ExcelFile(file)
                for sheet_name in xls.sheet_names:
                    df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None, dtype=str)
                    header_idx = next((i for i in range(min(30, len(df_raw))) 
                                     if 'wilayah' in " ".join([str(v).lower() for v in df_raw.iloc[i].values])), -1)
                    if header_idx != -1:
                        df_raw.columns = df_raw.iloc[header_idx].astype(str).tolist()
                        df = df_raw.iloc[header_idx + 1:].copy()
                        df = df.drop(columns=[c for c in df.columns if 'nan' in str(c).lower() or str(c).strip() == ''])
                        break
                else:
                    err = "Kata 'Wilayah' tidak ditemukan di sheet Excel."
        except Exception as e:
            err = f"ERROR: {str(e)}"
            
        if df is not None and not df.empty:
            try:
                wilayah_col = [c for c in df.columns if 'wilayah' in str(c).lower()][0]
                df = df.rename(columns={wilayah_col: 'Wilayah'})
                df = df.dropna(subset=['Wilayah'])
                df = df[~df['Wilayah'].astype(str).str.contains('Sumber Data|Laporan|Periode', case=False, na=False)]
                
                date_columns = [c for c in df.columns if c != 'Wilayah']
                df_melted = pd.melt(df, id_vars=['Wilayah'], value_vars=date_columns, var_name='Tanggal', value_name='Harga')
                df_melted['Tanggal'] = pd.to_datetime(df_melted['Tanggal'], errors='coerce')
                df_melted['Harga'] = pd.to_numeric(df_melted['Harga'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
                df_melted = df_melted.dropna(subset=['Tanggal', 'Harga'])
                df_melted = df_melted[df_melted['Harga'] > 0]
                
                if not df_melted.empty:
                    all_data.append(df_melted)
            except Exception as e:
                file_errors.append(f"{os.path.basename(file)}: {str(e)}")
        elif err:
            file_errors.append(f"{os.path.basename(file)}: {err}")

    if not all_data:
        raise ValueError("Gagal memproses data valid.\n" + "\n".join([f"• {e}" for e in file_errors]))

    combined = pd.concat(all_data, ignore_index=True)
    combined['Lat'] = None
    combined['Lon'] = None
    return combined

# --- KOORDINAT PROVINSI INDONESIA ---
KOORDINAT = {
    'DKI Jakarta': (-6.2088, 106.8456), 'Jawa Barat': (-6.9175, 107.6191),
    'Jawa Tengah': (-7.1506, 110.1403), 'Jawa Timur': (-7.2575, 112.7521),
    'Banten': (-6.4058, 106.0640), 'DI Yogyakarta': (-7.7956, 110.3695),
    'Bali': (-8.4095, 115.1889), 'Sumatera Utara': (3.5952, 98.6722),
    'Sumatera Barat': (-0.9471, 100.4172), 'Sumatera Selatan': (-3.3194, 103.9140),
    'Riau': (0.2933, 101.7068), 'Kepulauan Riau': (3.9456, 108.1429),
    'Jambi': (-1.6101, 103.6131), 'Bengkulu': (-3.7928, 102.2608),
    'Lampung': (-5.4292, 105.2619), 'Bangka Belitung': (-2.7411, 106.4406),
    'Aceh': (4.6951, 96.7494), 'Kalimantan Barat': (-0.2788, 111.4752),
    'Kalimantan Tengah': (-1.6815, 113.3824), 'Kalimantan Selatan': (-3.0926, 115.2838),
    'Kalimantan Timur': (-0.5022, 116.4194), 'Kalimantan Utara': (3.0731, 116.0419),
    'Sulawesi Utara': (1.4748, 124.8421), 'Sulawesi Tengah': (-1.4300, 121.4456),
    'Sulawesi Selatan': (-5.1477, 119.4327), 'Sulawesi Tenggara': (-4.1449, 122.1746),
    'Gorontalo': (0.6999, 122.4467), 'Sulawesi Barat': (-2.8441, 119.2320),
    'Maluku': (-3.2384, 130.1453), 'Maluku Utara': (1.5709, 127.8087),
    'Papua': (-4.2699, 138.0804), 'Papua Barat': (-1.3361, 133.1747),
    'Papua Pegunungan': (-4.0817, 138.5167), 'Papua Selatan': (-5.7096, 140.3889),
    'Papua Tengah': (-3.5000, 136.0000), 'Papua Barat Daya': (-1.8000, 132.0000),
    'Nusa Tenggara Barat': (-8.6529, 117.3616), 'Nusa Tenggara Timur': (-8.6573, 121.0794),
}

# --- PEMUATAN DATA ---
try:
    df_full = load_all_data()
except Exception as e:
    st.error(f"❌ **Error Memuat Data:** {str(e)}")
    st.info("💡 Pastikan file CSV/Excel memiliki kolom 'Wilayah' dan format tanggal yang valid.")
    st.stop()

if df_full.empty:
    st.error("⚠️ Data berhasil dibaca tetapi hasilnya kosong.")
    st.stop()

# --- Tambahkan koordinat otomatis ---
for prov, (lat, lon) in KOORDINAT.items():
    mask = df_full['Wilayah'] == prov
    df_full.loc[mask, 'Lat'] = lat
    df_full.loc[mask, 'Lon'] = lon

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style='display:flex; align-items:center; gap:12px; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.2);'>
        <div style='width:48px; height:48px; background:linear-gradient(135deg, #1B4332, #2D5A45); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:24px;'>🐔</div>
        <div>
            <h1 style='color:white; margin:0; font-size:17px; font-weight:700;'>Daging Ayam Ras</h1>
            <p style='color:#A7C4B5; font-size:10px; margin:4px 0 0 0; letter-spacing:1.5px; text-transform:uppercase;'>Market Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    max_d, min_d = df_full['Tanggal'].max().date(), df_full['Tanggal'].min().date()
    default_start = min_d if max_d == min_d else max(max_d - timedelta(days=90), min_d)
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600;'>📅 Timeframe</p>", unsafe_allow_html=True)
    date_range = st.date_input("", value=(default_start, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:1rem;'>⚙️ Indikator Teknikal</p>", unsafe_allow_html=True)
    show_sma = st.checkbox("📈 SMA (20 hari)", value=True)
    show_bb = st.checkbox("📊 Bollinger Bands", value=False)
    show_anomaly = st.checkbox("🔍 Deteksi Anomali", value=True)
    show_holidays = st.checkbox("🎉 Hari Raya/Libur", value=True)
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:1rem;'>⚠️ Threshold</p>", unsafe_allow_html=True)
    threshold = st.slider("", 25000, 60000, 40000, label_visibility="collapsed")
    z_threshold = st.slider("Z-Score Anomali", 1.5, 4.0, 2.5, 0.5)
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:1rem;'>📍 Filter Wilayah</p>", unsafe_allow_html=True)
    all_regs = sorted(df_full['Wilayah'].unique())
    default_sel = ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur'] if all(r in all_regs for r in ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur']) else all_regs[:3]
    selected_regions = st.multiselect("", all_regs, default=default_sel, label_visibility="collapsed")
    
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.2);'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

# --- FILTERING ---
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df_full[(df_full['Tanggal'] >= start) & (df_full['Tanggal'] <= end)].copy()
else:
    df = df_full.copy()

df['Status'] = df['Harga'].apply(lambda x: 'Waspada' if x > threshold else 'Stabil')
df_filtered = df[df['Wilayah'].isin(selected_regions)] if selected_regions else df
latest_date = df['Tanggal'].max()
df_now = df[df['Tanggal'] == latest_date]

# --- HEADER ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"""
    <div>
        <div class='live-badge'>
            <div class='pulse'></div>
            <span style='font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase;'>● Market Live</span>
        </div>
        <h1 style='font-size: 2rem; font-weight: 800; color: #012D1D; margin: 0;'>Dashboard Harga Daging Ayam Ras</h1>
        <p style='color: #5B6B63; font-size: 0.95rem; margin-top: 8px;'>Update: <strong>{latest_date.strftime('%d %B %Y')}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown(f"""
    <div style='text-align: right; background: #F0FDF4; padding: 12px 16px; border-radius: 12px; border: 1px solid #BBF7D0;'>
        <p style='margin: 0; font-size: 11px; color: #6B7A72; text-transform: uppercase; font-weight: 600;'>Data Source</p>
        <p style='margin: 4px 0 0 0; font-size: 13px; font-weight: 600; color: #012D1D;'>SP2KP Kemendag</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #E8EDEA, transparent); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

# --- METRIC CARDS ---
if not df_now.empty:
    avg_now = df_now['Harga'].mean()
    min_row, max_row = df_now.loc[df_now['Harga'].idxmin()], df_now.loc[df_now['Harga'].idxmax()]
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='bento-card metric-card border-secondary'><span style='font-size:11px;font-weight:700;color:#6B7A72;text-transform:uppercase;'>📊 Rata-rata Nasional</span><div style='display:flex;align-items:baseline;gap:6px;margin-top:8px;'><span style='font-size:1rem;font-weight:700;color:#8A9A92;'>Rp</span><span style='font-size:2rem;font-weight:800;color:#012D1D;'>{avg_now:,.0f}</span></div><span style='font-size:0.8rem;color:#6B7A72;margin-top:8px;'>Per {latest_date.strftime('%d/%m')}</span></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='bento-card metric-card border-success'><span style='font-size:11px;font-weight:700;color:#6B7A72;text-transform:uppercase;'>📉 Terendah</span><div style='display:flex;align-items:baseline;gap:6px;margin-top:8px;'><span style='font-size:1rem;font-weight:700;color:#8A9A92;'>Rp</span><span style='font-size:2rem;font-weight:800;color:#012D1D;'>{min_row['Harga']:,.0f}</span></div><span style='font-size:0.8rem;color:#6B7A72;margin-top:8px;'>📍 {min_row['Wilayah']}</span></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='bento-card metric-card border-error'><span style='font-size:11px;font-weight:700;color:#6B7A72;text-transform:uppercase;'>📈 Tertinggi</span><div style='display:flex;align-items:baseline;gap:6px;margin-top:8px;'><span style='font-size:1rem;font-weight:700;color:#8A9A92;'>Rp</span><span style='font-size:2rem;font-weight:800;color:#012D1D;'>{max_row['Harga']:,.0f}</span></div><span style='font-size:0.8rem;color:#6B7A72;margin-top:8px;'>📍 {max_row['Wilayah']}</span></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='bento-card metric-card border-primary'><span style='font-size:11px;font-weight:700;color:#6B7A72;text-transform:uppercase;'>🗄️ Total Data</span><div style='display:flex;align-items:baseline;gap:6px;margin-top:8px;'><span style='font-size:2rem;font-weight:800;color:#012D1D;'>{len(df_full):,}</span></div><span style='font-size:0.8rem;color:#6B7A72;margin-top:8px;'>✅ Validated</span></div>", unsafe_allow_html=True)

# --- CHART UTAMA DENGAN FITUR INTERAKTIF ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='bento-card'><div class='chart-header'><h3 class='chart-title'>📈 Tren Harga Interaktif</h3><p class='chart-subtitle'>Scroll untuk zoom • Hover untuk detail • Toggle indikator di sidebar</p></div>", unsafe_allow_html=True)

# Prepare data for main chart
df_line = df.groupby('Tanggal')['Harga'].mean().reset_index()

# Create subplot with secondary y-axis for indicators if needed
fig_main = go.Figure()

# Main price line
fig_main.add_trace(go.Scatter(
    x=df_line['Tanggal'], y=df_line['Harga'], name="🇮🇩 Nasional (Avg)",
    line=dict(color='#F0B429', width=2.5),
    hovertemplate='<b>%{x|%d %b %Y}</b><br>Harga: Rp %{y:,.0f}<extra></extra>'
))

# Regional lines
colors = ['#012D1D', '#16A34A', '#BA1A1A', '#EA9147', '#7C3AED', '#0891B2']
if selected_regions:
    for i, r in enumerate(selected_regions[:5]):
        rd = df[df['Wilayah']==r].groupby('Tanggal')['Harga'].mean().reset_index()
        if not rd.empty:
            fig_main.add_trace(go.Scatter(
                x=rd['Tanggal'], y=rd['Harga'], name=f"📍 {r}",
                line=dict(color=colors[i%len(colors)], width=1.8),
                hovertemplate='<b>%{x|%d %b %Y}</b><br>{name}: Rp %{y:,.0f}<extra></extra>'
            ))

# Technical Indicators
if show_sma and not df_line.empty:
    sma_20 = calculate_sma(df_line.set_index('Tanggal')['Harga'], 20)
    fig_main.add_trace(go.Scatter(
        x=sma_20.index, y=sma_20.values, name="📊 SMA 20",
        line=dict(color='#9F7AEA', width=1.5, dash='dash'),
        hovertemplate='SMA 20: Rp %{y:,.0f}<extra></extra>'
    ))

if show_bb and not df_line.empty:
    bb_upper, bb_mid, bb_lower = calculate_bollinger(df_line.set_index('Tanggal')['Harga'])
    fig_main.add_trace(go.Scatter(
        x=bb_upper.index, y=bb_upper.values, name="BB Upper",
        line=dict(color='rgba(255,200,100,0.7)', width=1, dash='dot'),
        hovertemplate='BB Upper: Rp %{y:,.0f}<extra></extra>'
    ))
    fig_main.add_trace(go.Scatter(
        x=bb_lower.index, y=bb_lower.values, name="BB Lower",
        line=dict(color='rgba(255,200,100,0.7)', width=1, dash='dot'),
        fill='tonexty', fillcolor='rgba(255,200,100,0.05)',
        hovertemplate='BB Lower: Rp %{y:,.0f}<extra></extra>'
    ))

# Anomaly detection
if show_anomaly and not df_line.empty:
    price_series = df_line.set_index('Tanggal')['Harga']
    anomalies, z_scores = detect_anomalies_zscore(price_series, z_threshold)
    anom_points = price_series[anomalies]
    if not anom_points.empty:
        fig_main.add_trace(go.Scatter(
            x=anom_points.index, y=anom_points.values, mode='markers', name="⚠️ Anomali",
            marker=dict(color='red', size=10, symbol='x', line=dict(width=2, color='white')),
            hovertemplate='<b>ANOMALI DETECTED</b><br>Tanggal: %{x|%d %b %Y}<br>Harga: Rp %{y:,.0f}<br>Z-Score: %{customdata:.2f}<extra></extra>',
            customdata=z_scores[anomalies].values
        ))

# Holiday annotations
if show_holidays:
    holidays = get_holiday_annotations((start, end))
    for holiday_date, holiday_name in holidays:
        fig_main.add_vline(x=holiday_date, line=dict(color='rgba(255,255,100,0.4)', dash='dot', width=1))
        fig_main.add_annotation(
            x=holiday_date, y=0.98, xref='x', yref='paper',
            text=f"🎉 {holiday_name}", showarrow=False,
            font=dict(size=8, color='rgba(255,255,100,0.8)'),
            textangle=-90, xanchor='right', yanchor='top',
            bgcolor='rgba(0,0,0,0.3)', borderpad=4
        )

# Weekend shading
for sat in df_line['Tanggal'][df_line['Tanggal'].dt.dayofweek == 5]:
    fig_main.add_vrect(x0=sat, x1=sat + pd.Timedelta(days=2),
                       fillcolor="rgba(128,128,128,0.08)", layer="below", line_width=0)

# Layout configuration
fig_main.update_layout(
    height=400, margin=dict(l=20, r=20, t=10, b=20),
    hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=9)),
    xaxis=dict(showgrid=False, tickfont=dict(size=9), rangeslider=dict(visible=True)),
    yaxis=dict(gridcolor='#E8EDEA', tickfont=dict(size=9), tickformat=',.0f', title='Harga (Rp)'),
    dragmode='zoom'
)

st.plotly_chart(fig_main, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
st.markdown("</div>", unsafe_allow_html=True)

# --- MAP INTERAKTIF DENGAN MULTI-METRIC ---
st.markdown("<br>", unsafe_allow_html=True)
c_map, c_dist = st.columns([2, 1])

with c_map:
    st.markdown("<div class='bento-card'><div class='chart-header'><h3 class='chart-title'>🗺️ Peta Sebaran Harga</h3></div>", unsafe_allow_html=True)
    
    # Metric selector for map
    map_metric = st.radio("Tampilan Peta:", ["💰 Harga", "📈 Volatilitas", "📊 Z-Score"], horizontal=True, key="map_metric")
    
    df_map = df_now.dropna(subset=['Lat', 'Lon']).copy()
    
    if not df_map.empty and df_map['Lat'].notna().any():
        # Calculate metrics
        df_map['Volatilitas'] = df_now.groupby('Wilayah')['Harga'].pct_change().std() * np.sqrt(252) * 100
        df_map['Z_Score'] = (df_now['Harga'] - df_now['Harga'].mean()) / df_now['Harga'].std()
        
        # Select metric column
        metric_col = 'Harga' if map_metric == "💰 Harga" else 'Volatilitas' if map_metric == "📈 Volatilitas" else 'Z_Score'
        color_title = "Harga (Rp)" if map_metric == "💰 Harga" else "Volatilitas (%)" if map_metric == "📈 Volatilitas" else "Z-Score"
        
        # Color scale based on metric
        if map_metric == "💰 Harga":
            colorscale = ['#16A34A', '#EAB308', '#BA1A1A']
        elif map_metric == "📈 Volatilitas":
            colorscale = ['#22C55E', '#F59E0B', '#EF4444']
        else:
            colorscale = ['#3B82F6', '#F59E0B', '#EF4444']  # Blue to Red for Z-score
        
        fig_map = px.scatter_mapbox(
            df_map, lat="Lat", lon="Lon", color=metric_col, size="Harga",
            hover_name="Wilayah", color_continuous_scale=colorscale,
            size_max=30, zoom=3.5, mapbox_style="carto-positron",
            hover_data={
                'Harga': ':,.0f',
                'Volatilitas': ':.1f' if map_metric != "💰 Harga" else False,
                'Z_Score': ':.2f' if map_metric == "📊 Z-Score" else False,
                'Lat': False, 'Lon': False
            }
        )
        
        fig_map.update_layout(
            height=400, margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=True,
            coloraxis_colorbar=dict(title=color_title, tickfont=dict(size=9)),
            mapbox=dict(
                style="carto-positron", zoom=3.5,
                center={"lat": -2.5, "lon": 118},
                pitch=0
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("""
        **📍 Data Koordinat Tidak Tersedia**
        
        Tambahkan kolom `Lat` dan `Lon` pada data untuk menampilkan peta interaktif.
        """)
    st.markdown("</div>", unsafe_allow_html=True)

with c_dist:
    st.markdown("<div class='bento-card'><div class='chart-header'><h3 class='chart-title'>📦 Distribusi Harga</h3></div>", unsafe_allow_html=True)
    
    plot_df = df_filtered if selected_regions else df[df['Wilayah'].isin(df['Wilayah'].unique()[:6])]
    if not plot_df.empty:
        fig_box = px.box(
            plot_df, x="Harga", y="Wilayah", color="Wilayah",
            color_discrete_sequence=['#012D1D', '#8E4E14', '#16A34A', '#EA9147', '#BA1A1A', '#7C3AED'],
            hover_data={'Harga': ':,.0f'}
        )
        fig_box.update_layout(
            height=400, margin=dict(l=0, r=10, t=0, b=10),
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder':'median ascending', 'tickfont': dict(size=9)},
            xaxis=dict(title="Harga (Rp)", gridcolor='#E8EDEA', tickfont=dict(size=9), tickformat=',.0f'),
            hoverlabel=dict(bgcolor="white", font_size=10)
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("⚠️ Tidak ada data untuk filter saat ini.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- CORRELATION HEATMAP (NEW FEATURE) ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='bento-card'><div class='chart-header'><h3 class='chart-title'>🔗 Korelasi Antar Wilayah</h3><p class='chart-subtitle'>Seberapa erat pergerakan harga antar provinsi</p></div>", unsafe_allow_html=True)

# Calculate correlation matrix
pivot_df = df.pivot_table(index='Tanggal', columns='Wilayah', values='Harga', aggfunc='mean')
if len(pivot_df.columns) >= 2 and not pivot_df.empty:
    corr_matrix = pivot_df.corr()
    
    # Show top correlations
    corr_pairs = [(c1, c2, corr_matrix.loc[c1, c2]) 
                  for i, c1 in enumerate(corr_matrix.columns) 
                  for j, c2 in enumerate(corr_matrix.columns) if j > i]
    corr_df = pd.DataFrame(corr_pairs, columns=['Provinsi 1', 'Provinsi 2', 'Korelasi'])
    
    # Display heatmap for top 15 provinces
    top_provs = corr_matrix.columns[:15] if len(corr_matrix.columns) > 15 else corr_matrix.columns
    corr_subset = corr_matrix.loc[top_provs, top_provs]
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_subset.values, x=corr_subset.columns, y=corr_subset.index,
        colorscale='RdYlGn', zmin=-1, zmax=1,
        text=np.round(corr_subset.values, 2), texttemplate="%{text}",
        textfont=dict(size=8), colorbar=dict(title="r"),
        hovertemplate="%{y} ↔ %{x}<br>Korelasi: %{z:.3f}<extra></extra>"
    ))
    
    fig_corr.update_layout(
        height=400, margin=dict(l=100, r=20, t=10, b=100),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=-45, tickfont=dict(size=8)),
        yaxis=dict(tickfont=dict(size=8)),
        title=dict(text="Matriks Korelasi Pearson", font=dict(size=12), x=0.5)
    )
    
    col_corr1, col_corr2 = st.columns([2, 1])
    with col_corr1:
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col_corr2:
        st.markdown("##### 🔝 Korelasi Tertinggi")
        top_corr = corr_df.nlargest(5, 'Korelasi')
        for _, row in top_corr.iterrows():
            st.markdown(f"<span style='color:#16A34A'>✓</span> {row['Provinsi 1'][:15]} ↔ {row['Provinsi 2'][:15]}<br>&nbsp;&nbsp;&nbsp;&nbsp;r = {row['Korelasi']:.3f}", unsafe_allow_html=True)
        
        st.markdown("##### 🔻 Korelasi Terendah")
        bottom_corr = corr_df.nsmallest(3, 'Korelasi')
        for _, row in bottom_corr.iterrows():
            st.markdown(f"<span style='color:#BA1A1A'>✗</span> {row['Provinsi 1'][:15]} ↔ {row['Provinsi 2'][:15]}<br>&nbsp;&nbsp;&nbsp;&nbsp;r = {row['Korelasi']:.3f}", unsafe_allow_html=True)
else:
    st.info("⚠️ Data tidak cukup untuk menghitung korelasi. Pilih rentang tanggal yang lebih panjang.")

st.markdown("</div>", unsafe_allow_html=True)

# --- ANOMALY ALERT CARDS (NEW FEATURE) ---
if show_anomaly and not df_now.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='bento-card'><div class='chart-header'><h3 class='chart-title'>🚨 Early Warning System</h3><p class='chart-subtitle'>Provinsi dengan harga anomali (Z-Score > threshold)</p></div>", unsafe_allow_html=True)
    
    # Calculate Z-scores for current date
    z_scores_now = (df_now['Harga'] - df['Harga'].mean()) / df['Harga'].std()
    df_now_z = df_now.copy()
    df_now_z['Z_Score'] = z_scores_now.values
    
    anomaly_provs = df_now_z[abs(df_now_z['Z_Score']) > z_threshold].sort_values('Z_Score', key=abs, ascending=False)
    
    if not anomaly_provs.empty:
        cols = st.columns(min(len(anomaly_provs), 4))
        for idx, (_, row) in enumerate(anomaly_provs.head(4).iterrows()):
            with cols[idx]:
                severity = "KRITIS" if abs(row['Z_Score']) > 3 else "WASPADA"
                color = "border-error" if row['Z_Score'] > 0 else "border-success"
                direction = "🔺 MAHAL" if row['Z_Score'] > 0 else "🔻 MURAH"
                st.markdown(f"""
                <div class='bento-card metric-card {color}' style='min-height:100px;'>
                    <div>
                        <span style='font-size:11px;font-weight:700;color:#6B7A72;text-transform:uppercase;'>{row['Wilayah']}</span>
                        <div style='display:flex;align-items:center;gap:4px;margin:8px 0;'>
                            <span style='font-size:1.5rem;font-weight:800;color:#012D1D;'>{direction}</span>
                        </div>
                        <span style='font-size:0.8rem;color:#6B7A72;'>Z-Score: <strong>{row['Z_Score']:+.2f}</strong></span>
                        <div style='margin-top:4px;'><span class='status-badge {'status-waspada' if severity=='WASPADA' else 'status-waspada'}'>{severity}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ Tidak ada anomali terdeteksi dengan threshold saat ini.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- DATA TABLE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class='bento-card' style='padding: 0; overflow: hidden;'>
    <div style='padding: 1.25rem 1.5rem; border-bottom: 1px solid #E8EDEA; background: linear-gradient(135deg, #F8FAF9 0%, #ffffff 100%); border-radius: 16px 16px 0 0;'>
        <h3 style='font-size: 1.1rem; font-weight: 700; color: #012D1D; margin: 0; display: flex; align-items: center; gap: 8px;'>📋 Rincian Data Harga</h3>
        <p style='color: #6B7A72; font-size: 0.85rem; margin: 4px 0 0 0;'>Update terbaru per provinsi</p>
    </div>
""", unsafe_allow_html=True)

if not df_now.empty:
    styled_df = df_now[['Tanggal', 'Wilayah', 'Harga', 'Status']].sort_values('Harga', ascending=False).copy()
    styled_df['Tanggal'] = styled_df['Tanggal'].dt.strftime('%d %b %Y')
    styled_df['Harga_Formatted'] = styled_df['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    
    def status_badge(status):
        if status == 'Waspada':
            return '<span class="status-badge status-waspada">⚠️ Waspada</span>'
        return '<span class="status-badge status-stabil">✅ Stabil</span>'
    
    styled_df['Status_Badge'] = styled_df['Status'].apply(status_badge)
    display_df = styled_df[['Tanggal', 'Wilayah', 'Harga_Formatted', 'Status_Badge']].copy()
    display_df.columns = ['📅 Tanggal', '📍 Wilayah', '💰 Harga', '🔔 Status']
    
    st.dataframe(
        display_df, use_container_width=True, hide_index=True, height=350,
        column_config={
            "📅 Tanggal": st.column_config.TextColumn(width="small"),
            "📍 Wilayah": st.column_config.TextColumn(width="medium"),
            "💰 Harga": st.column_config.TextColumn(width="small"),
            "🔔 Status": st.column_config.TextColumn(width="small")
        }
    )
    
    col_exp1, col_exp2 = st.columns([4, 1])
    with col_exp2:
        csv = styled_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Export CSV", data=csv,
            file_name=f"harga_ayam_{latest_date.strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )
else:
    st.warning("⚠️ Tidak ada data untuk tanggal terpilih.")

st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class='footer'>
    <p style='color: #012D1D; font-weight: 700; font-size: 0.9rem; margin: 0 0 4px 0;'>🐔 Agrarian Intelligence Dashboard</p>
    <p style='margin: 0;'>Data: <strong>SP2KP Kemendag</strong> • Analisis: SMA, Bollinger Bands, Z-Score Anomaly Detection</p>
    <p style='margin: 8px 0 0 0; opacity: 0.8;'>© 2026 Agrarian Intelligence • Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)
