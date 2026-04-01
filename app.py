import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta, datetime
import os
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriPulse | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:       #0D1117;
    --surface:  #161B22;
    --surface2: #1C232D;
    --border:   #2A3142;
    --accent:   #3DD68C;
    --accent2:  #F0B429;
    --danger:   #F87171;
    --safe:     #34D399;
    --muted:    #6B7A8D;
    --text:     #E6EDF3;
    --textsoft: #9BAABD;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

h1,h2,h3,h4,h5,h6 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--text) !important;
}

header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 1.5rem 2rem !important; }
footer { display: none !important; }

section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--textsoft) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: var(--text) !important; }
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(61,214,140,0.15) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    height: 100%;
    transition: border-color 0.2s;
}
.card:hover { border-color: rgba(61,214,140,0.35); }

.card-metric {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.card-metric::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.card-metric.acc::after  { background: var(--accent2); }
.card-metric.safe::after { background: var(--safe); }
.card-metric.dng::after  { background: var(--danger); }
.card-metric.pri::after  { background: #60A5FA; }
.card-metric.pur::after  { background: #A78BFA; }

.card-metric .label {
    font-size: 10px; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: var(--muted); margin-bottom: 6px;
}
.card-metric .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem; font-weight: 600; color: var(--text);
    letter-spacing: -.02em; line-height: 1.1;
}
.card-metric .value .prefix {
    font-size: .9rem; color: var(--muted); margin-right: 2px;
}
.card-metric .sub {
    font-size: 11px; color: var(--muted); margin-top: 6px;
}
.card-metric .delta-pos { color: var(--safe); font-weight: 600; }
.card-metric .delta-neg { color: var(--danger); font-weight: 600; }

.live-dot {
    display: inline-block; width: 7px; height: 7px;
    background: var(--accent); border-radius: 50%;
    animation: livepulse 1.8s infinite;
    vertical-align: middle; margin-right: 6px;
}
@keyframes livepulse {
    0%,100% { opacity:1; box-shadow: 0 0 0 0 rgba(61,214,140,.5); }
    50%      { opacity:.7; box-shadow: 0 0 0 6px rgba(61,214,140,0); }
}

.section-head {
    display: flex; align-items: baseline; gap: 10px;
    margin-bottom: .75rem; padding-bottom: .6rem;
    border-bottom: 1px solid var(--border);
}
.section-head h3 {
    font-size: 1rem; font-weight: 600; margin: 0;
    font-family: 'DM Sans', sans-serif !important;
}
.section-head .tag {
    font-size: 10px; color: var(--muted); letter-spacing: .08em;
    text-transform: uppercase;
}

.stButton > button {
    background: rgba(61,214,140,.1) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(61,214,140,.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    background: rgba(61,214,140,.2) !important;
    border-color: var(--accent) !important;
}
div[data-testid="stDataFrame"] {
    border-radius: 8px; overflow: hidden;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: 10px; padding: 4px; gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important; border-radius: 7px !important;
    font-size: 13px !important; font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(61,214,140,.15) !important;
    color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem !important; }

/* Styling Expander */
.streamlit-expanderHeader {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    background-color: var(--surface2) !important;
    border-radius: 8px !important;
}

.hdiv {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#9BAABD', size=11),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(
        gridcolor='#2A3142', 
        showgrid=False, 
        tickfont=dict(size=9), 
        zeroline=False
    ),
    yaxis=dict(
        gridcolor='#2A3142', 
        showgrid=True, 
        tickfont=dict(size=9), 
        zeroline=False
    ),
    hoverlabel=dict(
        bgcolor='#1C232D', 
        bordercolor='#2A3142', 
        font=dict(size=12)
    ),
    legend=dict(
        bgcolor='rgba(0,0,0,0)', 
        bordercolor='rgba(0,0,0,0)',
        font=dict(size=10), 
        orientation='h', 
        yanchor='bottom',
        y=-0.28, 
        xanchor='center', 
        x=.5
    ),
)
PALETTE = ['#3DD68C','#F0B429','#60A5FA','#F472B6','#A78BFA','#FB923C','#22D3EE','#FBBF24', '#E879F9', '#38BDF8', '#4ADE80', '#FCD34D']

def get_base_layout(*exclude_keys):
    return {k: v for k, v in PLOTLY_BASE.items() if k not in exclude_keys}

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def sma(s, w):       return s.rolling(w, min_periods=1).mean()
def ema(s, span):    return s.ewm(span=span, min_periods=1).mean()

def bollinger(s, w=20, n=2):
    m = sma(s, w)
    std = s.rolling(w, min_periods=1).std().fillna(0)
    return m + std*n, m, m - std*n

def zscore_anomaly(s, w=30, threshold=2.5):
    mu  = s.rolling(w, min_periods=5).mean()
    sig = s.rolling(w, min_periods=5).std().replace(0, np.nan)
    z   = (s - mu) / sig
    return z.abs() > threshold, z

def disparity_index(s, w=20):
    return (s / sma(s, w) - 1) * 100

def rsi(s, w=14):
    delta = s.diff()
    gain  = delta.clip(lower=0).rolling(w, min_periods=1).mean()
    loss  = (-delta.clip(upper=0)).rolling(w, min_periods=1).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_macd(s, fast=12, slow=26, sign=9):
    ema_fast = s.ewm(span=fast, adjust=False).mean()
    ema_slow = s.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=sign, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def coeff_of_variation(s):
    return (s.std() / s.mean() * 100) if s.mean() != 0 else 0

INDONESIAN_HOLIDAYS = {
    '2025-01-01':'Tahun Baru','2025-01-29':'Maulid Nabi','2025-03-29':'Nyepi','2025-03-30':'Wafat Isa','2025-03-31':'Isra Mi\'raj','2025-04-18':'Jumat Agung','2025-04-20':'Paskah','2025-05-01':'Hari Buruh','2025-05-12':'Waisak','2025-05-29':'Kenaikan Isa','2025-06-01':'Pancasila','2025-06-06':'Idul Adha','2025-06-27':'Tahun Baru Islam','2025-08-17':'HUT RI','2025-09-05':'Maulid Nabi','2025-12-25':'Natal','2025-12-26':'Cuti Natal',
    '2026-01-01':'Tahun Baru','2026-01-29':'Maulid Nabi','2026-02-26':'Mulai Ramadan','2026-03-29':'Nyepi','2026-03-30':'Wafat Isa','2026-04-01':'Isra Mi\'raj','2026-04-10':'Jumat Agung','2026-04-11':'Paskah','2026-05-01':'Hari Buruh','2026-05-21':'Kenaikan Isa','2026-05-29':'Waisak','2026-06-06':'Idul Fitri','2026-06-07':'Idul Fitri+1','2026-08-17':'HUT RI','2026-08-27':'Idul Adha','2026-12-25':'Natal',
}

def holidays_in_range(start, end):
    result = []
    for ds, name in INDONESIAN_HOLIDAYS.items():
        try:
            d = pd.to_datetime(ds)
            if start <= d <= end:
                result.append((d, name))
        except:
            pass
    return result

# ─────────────────────────────────────────────────────────────────────────────
# KOORDINAT PROVINSI & MAP PULAU
# ─────────────────────────────────────────────────────────────────────────────
KOORDINAT = {
    'DKI Jakarta':(-6.2088,106.8456),'Jawa Barat':(-6.9175,107.6191),'Jawa Tengah':(-7.1506,110.1403),'Jawa Timur':(-7.2575,112.7521),'Banten':(-6.4058,106.064),'DI Yogyakarta':(-7.7956,110.3695),
    'Bali':(-8.4095,115.1889),'Sumatera Utara':(3.5952,98.6722),'Sumatera Barat':(-0.9471,100.4172),'Sumatera Selatan':(-3.3194,103.914),'Riau':(0.2933,101.7068),'Kepulauan Riau':(3.9456,108.1429),'Jambi':(-1.6101,103.6131),'Bengkulu':(-3.7928,102.2608),'Lampung':(-5.4292,105.2619),'Bangka Belitung':(-2.7411,106.4406),'Aceh':(4.6951,96.7494),
    'Kalimantan Barat':(-0.2788,111.4752),'Kalimantan Tengah':(-1.6815,113.3824),'Kalimantan Selatan':(-3.0926,115.2838),'Kalimantan Timur':(-0.5022,116.4194),'Kalimantan Utara':(3.0731,116.0419),
    'Sulawesi Utara':(1.4748,124.8421),'Sulawesi Tengah':(-1.43,121.4456),'Sulawesi Selatan':(-5.1477,119.4327),'Sulawesi Tenggara':(-4.1449,122.1746),'Gorontalo':(0.6999,122.4467),'Sulawesi Barat':(-2.8441,119.232),
    'Maluku':(-3.2384,130.1453),'Maluku Utara':(1.5709,127.8087),'Papua':(-4.2699,138.0804),'Papua Barat':(-1.3361,133.1747),'Papua Pegunungan':(-4.0817,138.5167),'Papua Selatan':(-5.7096,140.3889),'Papua Tengah':(-3.5,136.0),'Papua Barat Daya':(-1.8,132.0),
    'Nusa Tenggara Barat':(-8.6529,117.3616),'Nusa Tenggara Timur':(-8.6573,121.0794),
}

PULAU_MAP = {
    'Sumatera': ['Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Kepulauan Riau', 'Jambi', 'Sumatera Selatan', 'Bangka Belitung', 'Bengkulu', 'Lampung'],
    'Jawa': ['Banten', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur'],
    'Bali & Nusa Tenggara': ['Bali', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur'],
    'Kalimantan': ['Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara'],
    'Sulawesi': ['Sulawesi Utara', 'Gorontalo', 'Sulawesi Tengah', 'Sulawesi Barat', 'Sulawesi Selatan', 'Sulawesi Tenggara'],
    'Maluku & Papua': ['Maluku Utara', 'Maluku', 'Papua Barat Daya', 'Papua Barat', 'Papua Tengah', 'Papua', 'Papua Pegunungan', 'Papua Selatan']
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    base = "."
    files = []
    for root, dirs, filenames in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv','__pycache__','node_modules')]
        for f in filenames:
            if f.endswith('.csv') or (f.endswith('.xlsx') and not f.startswith('~$')):
                files.append(os.path.join(root, f))

    if not files: raise FileNotFoundError("Tidak ada file .xlsx atau .csv ditemukan di direktori ini.")

    all_data, errors = [], []
    for fpath in files:
        df = None
        try:
            if fpath.endswith('.csv'):
                with open(fpath,'r', encoding='utf-8', errors='ignore') as fh: lines = fh.readlines()
                hidx = next((i for i,l in enumerate(lines[:30]) if 'wilayah' in l.lower()), -1)
                if hidx == -1: errors.append(f"{os.path.basename(fpath)}: kolom 'Wilayah' tidak ditemukan"); continue
                df = pd.read_csv(fpath, skiprows=hidx, dtype=str)
                df = df.loc[:, ~df.columns.str.contains(r'^[Uu]nnamed|^\s*$', na=True)]

            elif fpath.endswith('.xlsx'):
                xls = pd.ExcelFile(fpath)
                for sheet in xls.sheet_names:
                    raw = pd.read_excel(fpath, sheet_name=sheet, header=None, dtype=str)
                    hidx = next((i for i in range(min(30,len(raw))) if 'wilayah' in ' '.join(str(v) for v in raw.iloc[i].values).lower()), -1)
                    if hidx != -1:
                        raw.columns = raw.iloc[hidx].astype(str).tolist()
                        df = raw.iloc[hidx+1:].copy()
                        df = df.loc[:, ~df.columns.str.contains(r'^nan$|^\s*$', na=True)]
                        break
                if df is None: errors.append(f"{os.path.basename(fpath)}: kolom 'Wilayah' tidak ditemukan"); continue

            wcol = next((c for c in df.columns if 'wilayah' in str(c).lower()), None)
            if wcol is None: errors.append(f"{os.path.basename(fpath)}: kolom Wilayah tidak dapat diidentifikasi"); continue
            df = df.rename(columns={wcol:'Wilayah'})
            df = df[~df['Wilayah'].astype(str).str.contains(r'Sumber|Laporan|Periode|Catatan|nan', case=False, na=False)]
            df = df.dropna(subset=['Wilayah'])

            date_cols = [c for c in df.columns if c != 'Wilayah']
            melted = pd.melt(df, id_vars=['Wilayah'], value_vars=date_cols, var_name='Tanggal', value_name='Harga')
            melted['Tanggal'] = pd.to_datetime(melted['Tanggal'], errors='coerce')
            melted['Harga']   = pd.to_numeric(melted['Harga'].astype(str).str.replace(r'[^\d.]','',regex=True), errors='coerce')
            melted = melted.dropna(subset=['Tanggal','Harga'])
            melted = melted[melted['Harga'] > 1000]

            if not melted.empty: all_data.append(melted)
        except Exception as ex:
            errors.append(f"{os.path.basename(fpath)}: {ex}")

    if not all_data: raise ValueError("Tidak ada data valid.\n" + "\n".join(f"• {e}" for e in errors))

    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.drop_duplicates(subset=['Wilayah','Tanggal'])
    combined = combined.sort_values(['Wilayah','Tanggal']).reset_index(drop=True)

    combined['Lat'] = combined['Wilayah'].map(lambda w: KOORDINAT.get(w,(None,None))[0])
    combined['Lon'] = combined['Wilayah'].map(lambda w: KOORDINAT.get(w,(None,None))[1])

    return combined, errors

try:
    df_full, load_errors = load_all_data()
except Exception as e:
    st.error(f"❌ **Gagal memuat data:** {e}"); st.stop()
if df_full.empty:
    st.error("⚠️ Data berhasil dibaca tetapi kosong."); st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #2A3142;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:38px;height:38px;background:linear-gradient(135deg,#3DD68C22,#3DD68C44);
                        border:1px solid #3DD68C55;border-radius:10px;display:flex;
                        align-items:center;justify-content:center;font-size:20px;'>🐔</div>
            <div>
                <div style='font-family:"DM Serif Display",serif;font-size:15px; color:#E6EDF3;font-weight:700;'>AgriPulse</div>
                <div style='font-size:10px;color:#6B7A8D;letter-spacing:.1em; text-transform:uppercase;'>Daging Ayam Ras</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_dates_min = df_full['Tanggal'].min().date()
    all_dates_max = df_full['Tanggal'].max().date()

    def set_dates(days=None):
        if days is None: st.session_state.d_picker = (all_dates_min, all_dates_max)
        else: st.session_state.d_picker = (max(all_dates_max - timedelta(days=days), all_dates_min), all_dates_max)

    if 'd_picker' not in st.session_state: st.session_state.d_picker = (all_dates_min, all_dates_max)

    st.markdown("<div style='font-size:11px;color:#9BAABD;font-weight:600;margin-bottom:6px;'>📅 Rentang Waktu</div>", unsafe_allow_html=True)
    cd1, cd2, cd3, cd4, cd5 = st.columns(5)
    cd1.button("1B", on_click=set_dates, args=(30,), use_container_width=True, help="1 Bulan Terakhir")
    cd2.button("3B", on_click=set_dates, args=(90,), use_container_width=True, help="3 Bulan Terakhir")
    cd3.button("6B", on_click=set_dates, args=(180,), use_container_width=True, help="6 Bulan Terakhir")
    cd4.button("1T", on_click=set_dates, args=(365,), use_container_width=True, help="1 Tahun Terakhir")
    cd5.button("All", on_click=set_dates, args=(None,), use_container_width=True, help="Tampilkan Seluruh Data")
    date_range = st.date_input("", key='d_picker', min_value=all_dates_min, max_value=all_dates_max, label_visibility="collapsed")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    all_regions = sorted(df_full['Wilayah'].unique())
    if 'sel_regions' not in st.session_state: st.session_state.sel_regions = all_regions

    st.markdown("<div style='font-size:11px;color:#9BAABD;font-weight:600;margin-bottom:6px;'>🌏 Filter Wilayah</div>", unsafe_allow_html=True)
    pulau_opts = ["Semua Provinsi", "Pulau Sumatera", "Pulau Jawa", "Pulau Kalimantan", "Pulau Sulawesi", "Bali & Nusa Tenggara", "Maluku & Papua", "-- Kustom Wilayah --"]
    
    def on_pulau_change():
        p = st.session_state.pulau_sel
        if p == "Semua Provinsi": st.session_state.sel_regions = all_regions
        elif p == "Pulau Sumatera": st.session_state.sel_regions = [r for r in PULAU_MAP['Sumatera'] if r in all_regions]
        elif p == "Pulau Jawa": st.session_state.sel_regions = [r for r in PULAU_MAP['Jawa'] if r in all_regions]
        elif p == "Pulau Kalimantan": st.session_state.sel_regions = [r for r in PULAU_MAP['Kalimantan'] if r in all_regions]
        elif p == "Pulau Sulawesi": st.session_state.sel_regions = [r for r in PULAU_MAP['Sulawesi'] if r in all_regions]
        elif p == "Bali & Nusa Tenggara": st.session_state.sel_regions = [r for r in PULAU_MAP['Bali & Nusa Tenggara'] if r in all_regions]
        elif p == "Maluku & Papua": st.session_state.sel_regions = [r for r in PULAU_MAP['Maluku & Papua'] if r in all_regions]

    st.selectbox("Filter Cepat Pulau", pulau_opts, key='pulau_sel', on_change=on_pulau_change, label_visibility="collapsed")
    selected_regions = st.multiselect("Provinsi Terpilih", all_regions, key="sel_regions", label_visibility="collapsed")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    with st.expander("⚙️ Parameter Analisis", expanded=False):
        threshold = st.slider("Threshold Harga Waspada (Rp)", 25000, 65000, 40000, 500)
        show_sma      = st.checkbox("Tampilkan SMA 7 & 20", value=True)
        show_bb       = st.checkbox("Tampilkan Bollinger Bands", value=False)
        show_anomaly  = st.checkbox("Tampilkan Deteksi Anomali", value=True)
        show_holidays = st.checkbox("Tandai Hari Raya / Libur", value=True)
        show_forecast = st.checkbox("Tampilkan Proyeksi (7 Hari)", value=False)
        z_thr = st.slider("Sensitivitas Anomali (Z-Score)", 1.5, 4.0, 2.5, 0.25)

    if load_errors:
        with st.expander("⚠️ Log Error Parsing"):
            for e in load_errors: st.caption(e)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True): st.cache_data.clear(); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────────────────────────────────────
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
elif isinstance(date_range, tuple) and len(date_range) == 1:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(all_dates_max)
else:
    d_start, d_end = (pd.Timestamp(date_range) if date_range else pd.Timestamp(all_dates_min)), pd.Timestamp(all_dates_max)

df_view = df_full[(df_full['Tanggal'] >= d_start) & (df_full['Tanggal'] <= d_end)].copy()
df_sel = df_view[df_view['Wilayah'].isin(selected_regions)] if selected_regions else df_view.copy()

latest_date = df_view['Tanggal'].max()
df_now = df_view[df_view['Tanggal'] == latest_date].copy()

nat_full = df_full.groupby('Tanggal')['Harga'].mean().sort_index()
nat_view = nat_full[(nat_full.index >= d_start) & (nat_full.index <= d_end)]

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([3,1])
with h1:
    n_provs = df_full['Wilayah'].nunique()
    total_days = (df_full['Tanggal'].max() - df_full['Tanggal'].min()).days
    st.markdown(f"""
    <div style='margin-bottom:.5rem;'>
        <div style='font-size:11px;color:#3DD68C;letter-spacing:.15em;text-transform:uppercase; font-weight:700;margin-bottom:4px;'>
            <span class='live-dot'></span>Market Intelligence
        </div>
        <h1 style='font-size:2.2rem;margin:0;line-height:1.1;'>Dashboard Harga Daging Ayam Ras</h1>
        <p style='color:#6B7A8D;font-size:.875rem;margin:6px 0 0;'>
            Data: <strong style='color:#9BAABD;'>{df_full['Tanggal'].min().strftime('%d %b %Y')}</strong>
            → <strong style='color:#9BAABD;'>{latest_date.strftime('%d %b %Y')}</strong>
            &nbsp;·&nbsp; {n_provs} provinsi &nbsp;·&nbsp; {total_days:,} hari &nbsp;·&nbsp; {len(df_full):,} titik data
        </p>
    </div>
    """, unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div style='text-align:right;padding-top:.5rem;'>
        <div style='font-size:10px;color:#6B7A8D;text-transform:uppercase;letter-spacing:.1em;'>Sumber Data</div>
        <div style='font-size:14px;font-weight:700;color:#E6EDF3;margin-top:2px;'>SP2KP Kemendag</div>
        <div style='font-size:11px;color:#6B7A8D;'>Update: {latest_date.strftime('%d %b %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='hdiv'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────────────────────────────────────
if not df_now.empty:
    avg_now  = df_now['Harga'].mean()
    min_row  = df_now.loc[df_now['Harga'].idxmin()]
    max_row  = df_now.loc[df_now['Harga'].idxmax()]
    n_warn   = (df_now['Harga'] > threshold).sum()
    n_total  = len(df_now)
    spread   = df_now['Harga'].max() - df_now['Harga'].min()

    # Hitung WoW (Week on Week)
    prev_date_wow = latest_date - timedelta(days=7)
    df_prev_wow = df_full[df_full['Tanggal'] == df_full['Tanggal'][df_full['Tanggal'] <= prev_date_wow].max()]
    avg_prev_wow = df_prev_wow['Harga'].mean() if not df_prev_wow.empty else avg_now
    wow_pct = (avg_now - avg_prev_wow) / avg_prev_wow * 100 if avg_prev_wow else 0

    cv_nat = coeff_of_variation(nat_view) if not nat_view.empty else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, cls, label, val, sub, pfx in [
        (c1,'acc','Rata-rata Nasional', avg_now, f'<span class="{"delta-pos" if wow_pct>=0 else "delta-neg"}">{"▲" if wow_pct>=0 else "▼"} {abs(wow_pct):.1f}% vs Minggu Lalu</span>','Rp'),
        (c2,'safe','Harga Terendah', min_row['Harga'], f'📍 {min_row["Wilayah"]}','Rp'),
        (c3,'dng','Harga Tertinggi', max_row['Harga'], f'📍 {max_row["Wilayah"]}','Rp'),
        (c4,'pri','Disparitas Nasional', spread, f'{n_warn}/{n_total} prov. waspada','Rp'),
        (c5,'pur','Volatilitas (CV)', cv_nat, f'Koef. Variasi – periode ini','%'),
    ]:
        col.markdown(f"""
        <div class='card-metric {cls}'>
            <div class='label'>{label}</div>
            <div class='value'><span class='prefix'>{pfx}</span>{val:,.0f}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:.75rem;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_trend, tab_disp_corr, tab_map, tab_analysis, tab_season, tab_data = st.tabs([
    "📈 Tren & Proyeksi",
    "📐 Disparitas & Korelasi",
    "🗺️ Peta Sebaran",
    "🔬 Analisis Mendalam",
    "📅 Musim & Siklus",
    "📋 Data & Ringkasan"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TREN HARGA & PROYEKSI
# ══════════════════════════════════════════════════════════════════════════════
with tab_trend:
    c_opt1, c_opt2 = st.columns([3,1])
    with c_opt2:
        compare_mode = st.radio("Mode Tampilan", ["Wilayah Terpilih","Nasional Saja","Semua Wilayah"], index=0, horizontal=True)
        chart_type = st.radio("Gaya Nasional", ["Garis", "Candlestick (Mingguan)"], index=0, horizontal=True)

    with c_opt1:
        if compare_mode == "Wilayah Terpilih": regions_to_plot = selected_regions
        elif compare_mode == "Nasional Saja": regions_to_plot = []
        else: regions_to_plot = all_regions

    fig = go.Figure()

    sma7_full  = sma(nat_full, 7)
    sma20_full = sma(nat_full, 20)
    bb_u, bb_m, bb_l = bollinger(nat_full)
    anom_mask, z_vals = zscore_anomaly(nat_full, w=30, threshold=z_thr)

    nat_v   = nat_full[nat_full.index.isin(nat_view.index)]
    sma7_v  = sma7_full[sma7_full.index.isin(nat_view.index)]
    sma20_v = sma20_full[sma20_full.index.isin(nat_view.index)]
    bb_u_v  = bb_u[bb_u.index.isin(nat_view.index)]
    bb_l_v  = bb_l[bb_l.index.isin(nat_view.index)]
    anom_v  = anom_mask[anom_mask.index.isin(nat_view.index)]
    z_v     = z_vals[z_vals.index.isin(nat_view.index)]

    if show_bb:
        fig.add_trace(go.Scatter(
            x=list(bb_u_v.index)+list(bb_l_v.index[::-1]), y=list(bb_u_v.values)+list(bb_l_v.values[::-1]),
            fill='toself', fillcolor='rgba(240,180,41,0.06)', line=dict(width=0), name='BB Band', hoverinfo='skip', showlegend=True))
        for series, name, dash in [(bb_u_v,'BB Upper','dot'),(bb_l_v,'BB Lower','dot')]:
            fig.add_trace(go.Scatter(x=series.index, y=series.values, name=name, line=dict(color='rgba(240,180,41,0.5)', width=1, dash=dash), hovertemplate=f'{name}: Rp %{{y:,.0f}}<extra></extra>'))

    for i, reg in enumerate(regions_to_plot):
        rd = df_full[df_full['Wilayah']==reg].set_index('Tanggal')['Harga'].sort_index()
        rd_v = rd[(rd.index >= d_start) & (rd.index <= d_end)]
        if rd_v.empty: continue
        fig.add_trace(go.Scatter(
            x=rd_v.index, y=rd_v.values, name=f'📍 {reg}',
            line=dict(color=PALETTE[i % len(PALETTE)], width=1.6), opacity=0.8,
            hovertemplate=f'<b>{reg}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))

    if chart_type == "Garis":
        fig.add_trace(go.Scatter(
            x=nat_v.index, y=nat_v.values, name='🇮 Nasional (Avg)',
            line=dict(color='#FFFFFF', width=2.5), hovertemplate='<b>Nasional</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'))
    else:
        nat_w = nat_full.resample('W').ohlc()
        nat_w_v = nat_w[(nat_w.index >= d_start) & (nat_w.index <= d_end)]
        fig.add_trace(go.Candlestick(
            x=nat_w_v.index, open=nat_w_v['open'], high=nat_w_v['high'], low=nat_w_v['low'], close=nat_w_v['close'],
            name='🇮 Nasional (OHLC)', increasing_line_color='#3DD68C', decreasing_line_color='#F87171',
            increasing_fillcolor='rgba(61,214,140,0.5)', decreasing_fillcolor='rgba(248,113,113,0.5)'))
        fig.update_layout(xaxis_rangeslider_visible=False)

    if show_sma:
        fig.add_trace(go.Scatter(x=sma7_v.index, y=sma7_v.values, name='SMA 7', line=dict(color='#60A5FA', width=1.2, dash='dash'), hovertemplate='SMA 7: Rp %{y:,.0f}<extra></extra>'))
        fig.add_trace(go.Scatter(x=sma20_v.index, y=sma20_v.values, name='SMA 20', line=dict(color='#A78BFA', width=1.2, dash='dot'), hovertemplate='SMA 20: Rp %{y:,.0f}<extra></extra>'))

    # FORECASTING Sederhana (7 Hari)
    if show_forecast and not nat_full.empty:
        last_date = nat_full.index[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
        # Simple EMA Projection
        ema_val = nat_full.ewm(span=7).mean().iloc[-1]
        trend = nat_full.diff().ewm(span=7).mean().iloc[-1]
        future_vals = [ema_val + (trend * i) for i in range(1, 8)]
        
        fig.add_trace(go.Scatter(
            x=future_dates, y=future_vals, name='🔮 Proyeksi Nasional (7H)',
            line=dict(color='#E879F9', width=2, dash='dot'),
            hovertemplate='<b>Proyeksi</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'
        ))

    fig.add_hline(y=threshold, line=dict(color='rgba(248,113,113,0.5)', width=1, dash='dash'), annotation_text=f"⚠️ Threshold Rp {threshold:,.0f}", annotation_font_color='#F87171', annotation_font_size=10)

    if show_anomaly:
        anom_pts, z_anom = nat_v[anom_v[anom_v.index.isin(nat_v.index)]], z_v[anom_v[anom_v.index.isin(nat_v.index)]]
        if not anom_pts.empty:
            fig.add_trace(go.Scatter(
                x=anom_pts.index, y=anom_pts.values, mode='markers', name='⚠️ Anomali',
                marker=dict(color='#F87171', size=9, symbol='x-thin-open', line=dict(width=2, color='#F87171')),
                customdata=z_anom.values, hovertemplate='<b>ANOMALI</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<br>Z=%{customdata:.2f}<extra></extra>'))

    if show_holidays:
        for hdate, hname in holidays_in_range(d_start, d_end):
            fig.add_vline(x=hdate, line=dict(color='rgba(96,165,250,0.25)', width=1, dash='dot'))
            fig.add_annotation(x=hdate, y=0.97, xref='x', yref='paper', text=hname, showarrow=False, font=dict(size=8, color='rgba(96,165,250,0.7)'), textangle=-90, xanchor='right', bgcolor='rgba(96,165,250,0.08)', borderpad=3)

    fig.update_layout(
        height=500, hovermode='x unified', dragmode='zoom',
        paper_bgcolor=PLOTLY_BASE['paper_bgcolor'], plot_bgcolor=PLOTLY_BASE['plot_bgcolor'], font=PLOTLY_BASE['font'], margin=PLOTLY_BASE['margin'], hoverlabel=PLOTLY_BASE['hoverlabel'], legend=PLOTLY_BASE['legend'],
        xaxis=dict(gridcolor='#2A3142', showgrid=False, tickfont=dict(size=9), zeroline=False, rangeslider=dict(visible=True, bgcolor='#161B22', thickness=0.04),
                   rangeselector=dict(bgcolor='#1C232D', bordercolor='#2A3142', font=dict(color='#9BAABD', size=10), buttons=[dict(count=1, label='1B', step='month', stepmode='backward'), dict(count=3, label='3B', step='month', stepmode='backward'), dict(count=6, label='6B', step='month', stepmode='backward'), dict(step='all', label='Semua')])),
        yaxis=dict(gridcolor='#2A3142', showgrid=True, tickfont=dict(size=9), zeroline=False, tickformat=',.0f', title='Harga (Rp)', title_font=dict(size=10, color='#6B7A8D'))
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-head'><h3>Tren & Proyeksi Harga Interaktif</h3><span class='tag'>Scroll = zoom · Drag = pan · Double-click = reset</span></div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom':True,'displayModeBar':True,'modeBarButtonsToAdd':['drawline','eraseshape']})
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DISPARITAS & KORELASI
# ══════════════════════════════════════════════════════════════════════════════
with tab_disp_corr:
    st.markdown("""<div style='font-size:12px;color:#6B7A8D;padding:8px 12px;background:#1C232D; border-left:3px solid #3DD68C;border-radius:4px;margin-bottom:1rem;'>
        <b style='color:#3DD68C;'>Disparitas</b> = selisih harga tertinggi dan terendah antar provinsi.
        <b>Indeks Gini Harga</b> = Rasio ketidakmerataan harga (mendekati 0 berarti harga merata seluruh RI).
    </div>""", unsafe_allow_html=True)

    disp_full = df_full.groupby('Tanggal')['Harga'].agg(lambda x: x.max()-x.min()).sort_index()
    disp_view = disp_full[(disp_full.index >= d_start) & (disp_full.index <= d_end)]
    disp_sma_v = sma(disp_full, 20)[sma(disp_full, 20).index.isin(disp_view.index)]

    def gini(arr):
        a = np.sort(np.abs(arr)); n = len(a)
        if n == 0 or a.mean() == 0: return 0
        return (2*np.sum(np.arange(1, n+1)*a) / (n*np.sum(a))) - (n+1)/n

    gini_view = df_full.groupby('Tanggal')['Harga'].apply(gini).sort_index()
    gini_view = gini_view[(gini_view.index >= d_start) & (gini_view.index <= d_end)]

    dc1, dc2 = st.columns([2,1])
    with dc1:
        fig_disp = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.65,0.35], vertical_spacing=0.04)
        fig_disp.add_trace(go.Scatter(x=disp_view.index, y=disp_view.values, name='Disparitas (Rp)', fill='tozeroy', fillcolor='rgba(61,214,140,0.08)', line=dict(color='#3DD68C', width=1.8), hovertemplate='%{x|%d %b %Y}<br>Disparitas: Rp %{y:,.0f}<extra></extra>'), row=1, col=1)
        fig_disp.add_trace(go.Scatter(x=disp_sma_v.index, y=disp_sma_v.values, name='SMA 20', line=dict(color='#F0B429', width=1.2, dash='dash')), row=1, col=1)
        fig_disp.add_trace(go.Bar(x=gini_view.index, y=gini_view.values, name='Gini Harga', marker_color='rgba(167,139,250,0.6)', hovertemplate='%{x|%d %b %Y}<br>Gini: %{y:.4f}<extra></extra>'), row=2, col=1)
        fig_disp.update_layout(**get_base_layout('yaxis', 'yaxis2', 'legend'), height=380, yaxis=dict(**PLOTLY_BASE['yaxis'], title='Disparitas (Rp)', tickformat=',.0f'), yaxis2=dict(**PLOTLY_BASE['yaxis'], title='Gini Index'), legend=dict(**PLOTLY_BASE['legend']))
        fig_disp.update_xaxes(showgrid=False, tickfont=dict(size=9))

        st.markdown("<div class='card'><div class='section-head'><h3>Disparitas Harga & Indeks Gini</h3></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_disp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with dc2:
        prov_std = df_view.groupby('Wilayah')['Harga'].std().sort_values(ascending=False).head(10)
        fig_std = go.Figure(go.Bar(x=prov_std.values, y=prov_std.index, orientation='h', marker_color=[PALETTE[i % len(PALETTE)] for i in range(len(prov_std))], text=prov_std.values.round(0).astype(int), texttemplate='Rp %{text:,}', textfont=dict(size=9), hovertemplate='%{y}<br>Std Dev: Rp %{x:,.0f}<extra></extra>'))
        fig_std.update_layout(**get_base_layout('xaxis', 'yaxis', 'margin'), height=380, xaxis=dict(**PLOTLY_BASE['xaxis'], tickformat=',.0f'), yaxis=dict(**PLOTLY_BASE['yaxis'], categoryorder='total ascending'), showlegend=False, margin=dict(l=0,r=60,t=10,b=10))

        st.markdown("<div class='card'><div class='section-head'><h3>Top 10 Wilayah Paling Volatil</h3><span class='tag'>Standar Deviasi Tertinggi</span></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_std, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # MATRIKS KORELASI
    st.markdown("<div class='hdiv'></div>", unsafe_allow_html=True)
    pivot = df_full.pivot_table(index='Tanggal', columns='Wilayah', values='Harga', aggfunc='mean')
    pivot_v = pivot[(pivot.index >= d_start) & (pivot.index <= d_end)]

    if pivot_v.shape[1] >= 2 and not pivot_v.empty:
        corr = pivot_v.corr(method='pearson')
        top_provs = pivot_v.notna().sum().sort_values(ascending=False).head(40).index.tolist()
        corr_sub  = corr.loc[top_provs, top_provs]

        corr_col1, corr_col2 = st.columns([2,1])
        with corr_col1:
            fig_corr = go.Figure(go.Heatmap(z=corr_sub.values, x=corr_sub.columns, y=corr_sub.index, colorscale=[[0,'#EF4444'],[0.5,'#1C232D'],[1,'#3DD68C']], zmin=-1, zmax=1, textfont=dict(size=7), colorbar=dict(title='r', tickfont=dict(size=8)), hovertemplate="%{y} ↔ %{x}<br>r = %{z:.3f}<extra></extra>"))
            fig_corr.update_layout(**get_base_layout('xaxis', 'yaxis', 'margin'), height=600, xaxis=dict(tickangle=-45, tickfont=dict(size=8), showgrid=False), yaxis=dict(tickfont=dict(size=8), showgrid=False), margin=dict(l=10,r=10,t=10,b=80))
            st.markdown("<div class='card'><div class='section-head'><h3>Matriks Korelasi Pearson</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with corr_col2:
            pairs_df = pd.DataFrame([(corr_sub.index[i], corr_sub.columns[j], corr_sub.iloc[i,j]) for i in range(len(corr_sub)) for j in range(i+1,len(corr_sub.columns))], columns=['Prov A','Prov B','r'])
            
            st.markdown("<div class='card'><div class='section-head'><h3>5 Korelasi Tertinggi</h3></div>", unsafe_allow_html=True)
            for _,row in pairs_df.nlargest(5,'r').iterrows():
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2A3142;font-size:12px;'><span>{row['Prov A'][:14]} ↔ {row['Prov B'][:14]}</span><span style='color:#3DD68C;font-family:monospace;'>{row['r']:.3f}</span></div>", unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div><div class='section-head'><h3>5 Korelasi Terendah</h3></div>", unsafe_allow_html=True)
            for _,row in pairs_df.nsmallest(5,'r').iterrows():
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2A3142;font-size:12px;'><span>{row['Prov A'][:14]} ↔ {row['Prov B'][:14]}</span><span style='color:#F87171;font-family:monospace;'>{row['r']:.3f}</span></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PETA
# ══════════════════════════════════════════════════════════════════════════════
with tab_map:
    map_col1, map_col2 = st.columns([3,1])
    with map_col2:
        map_metric = st.selectbox("Metrik Peta", ["💰 Harga Terkini", "📐 Disparitas vs Nasional", "📊 Z-Score", "📈 Volatilitas (CV)", "🔺 Tren 30 Hari (%)"], key="mapmetric")
        map_style = st.selectbox("Gaya Peta", ["carto-darkmatter","carto-positron","open-street-map"], key="mapstyle")

    map_data = []
    for prov in df_full['Wilayah'].unique():
        lat, lon = KOORDINAT.get(prov, (None, None))
        if lat is None: continue
        series_v = df_full[df_full['Wilayah']==prov].set_index('Tanggal')['Harga'].sort_index()
        series_v = series_v[(series_v.index >= d_start) & (series_v.index <= d_end)]
        if series_v.empty: continue

        harga_now = series_v.iloc[-1]
        nat_avg   = nat_view.iloc[-1] if not nat_view.empty else np.nan
        map_data.append(dict(
            Wilayah=prov, Lat=lat, Lon=lon, Harga=harga_now, Disparitas=harga_now - nat_avg,
            Z_Score=(harga_now - nat_view.mean()) / nat_view.std() if nat_view.std() != 0 else 0,
            Volatilitas=coeff_of_variation(series_v), Tren30=(harga_now - series_v.iloc[max(0, len(series_v)-31)]) / series_v.iloc[max(0, len(series_v)-31)] * 100 if len(series_v)>=5 else 0
        ))

    df_map = pd.DataFrame(map_data)
    if not df_map.empty:
        col, title, cscale = {"💰 Harga Terkini": ("Harga", "Harga (Rp)", [[0,'#22D3EE'],[0.5,'#F0B429'],[1,'#EF4444']]), "📐 Disparitas vs Nasional": ("Disparitas", "Disparitas (Rp)", [[0,'#60A5FA'],[0.5,'#FFFFFF'],[1,'#F87171']]), "📊 Z-Score": ("Z_Score", "Z-Score", [[0,'#60A5FA'],[0.5,'#1C232D'],[1,'#F87171']]), "📈 Volatilitas (CV)": ("Volatilitas","CV (%)", [[0,'#3DD68C'],[1,'#EF4444']]), "🔺 Tren 30 Hari (%)": ("Tren30", "Tren 30h (%)", [[0,'#60A5FA'],[0.5,'#1C232D'],[1,'#F87171']])}[map_metric]
        
        fig_map = px.scatter_mapbox(df_map, lat="Lat", lon="Lon", color=col, size="Harga", hover_name="Wilayah", hover_data={"Harga":":,.0f", "Lat":False, "Lon":False}, color_continuous_scale=cscale, size_max=28, zoom=3.5, mapbox_style=map_style, color_continuous_midpoint=0 if col in ('Disparitas','Z_Score','Tren30') else None)
        fig_map.update_layout(height=480, margin=dict(l=0,r=0,t=0,b=0), coloraxis_colorbar=dict(title=title, tickfont=dict(size=9)), mapbox=dict(center={"lat":-2.5,"lon":118}), paper_bgcolor='rgba(0,0,0,0)')

        with map_col1:
            st.markdown(f"<div class='card'><div class='section-head'><h3>Peta Sebaran — {map_metric}</h3></div>", unsafe_allow_html=True)
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with map_col2:
            st.markdown("<div class='card' style='margin-top:.5rem;'><div class='section-head'><h3>Ringkasan</h3></div>", unsafe_allow_html=True)
            tbl = df_map[['Wilayah','Harga','Tren30']].sort_values('Harga', ascending=False)
            tbl['Harga'] = tbl['Harga'].apply(lambda x: f"Rp {x:,.0f}")
            tbl['Tren30'] = tbl['Tren30'].apply(lambda x: f"{'▲' if x>=0 else '▼'} {abs(x):.1f}%")
            st.dataframe(tbl, hide_index=True, height=420, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS MENDALAM
# ══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    an1, an2 = st.columns(2)

    with an1:
        st.markdown("<div class='card'><div class='section-head'><h3>Indikator Momentum (RSI & MACD)</h3><span class='tag'>Rata-rata Nasional</span></div>", unsafe_allow_html=True)
        rsi_v = rsi(nat_full, w=14)[rsi(nat_full, w=14).index.isin(nat_view.index)]
        macd_line, sig_line, macd_hist = calc_macd(nat_full)
        
        fig_rsi = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.5, 0.5], vertical_spacing=0.08)
        
        # RSI
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor='rgba(248,113,113,0.08)', line_width=0, row=1, col=1)
        fig_rsi.add_hrect(y0=0,  y1=30,  fillcolor='rgba(52,211,153,0.08)',  line_width=0, row=1, col=1)
        fig_rsi.add_trace(go.Scatter(x=rsi_v.index, y=rsi_v.values, name='RSI', line=dict(color='#60A5FA', width=1.5)), row=1, col=1)
        
        # MACD
        m_idx = macd_line.index.isin(nat_view.index)
        fig_rsi.add_trace(go.Bar(x=macd_hist[m_idx].index, y=macd_hist[m_idx].values, name='Histogram', marker_color=np.where(macd_hist[m_idx]>=0, '#3DD68C', '#F87171')), row=2, col=1)
        fig_rsi.add_trace(go.Scatter(x=macd_line[m_idx].index, y=macd_line[m_idx].values, name='MACD', line=dict(color='#38BDF8', width=1.5)), row=2, col=1)
        fig_rsi.add_trace(go.Scatter(x=sig_line[m_idx].index, y=sig_line[m_idx].values, name='Signal', line=dict(color='#F0B429', width=1.5, dash='dot')), row=2, col=1)

        fig_rsi.update_layout(**get_base_layout('xaxis', 'yaxis'), height=400, showlegend=False, yaxis=dict(**PLOTLY_BASE['yaxis'], range=[0,100], title='RSI', tickvals=[30,70]), yaxis2=dict(**PLOTLY_BASE['yaxis'], title='MACD'))
        st.plotly_chart(fig_rsi, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with an2:
        st.markdown("<div class='card'><div class='section-head'><h3>📦 Distribusi Harga (Boxplot)</h3><span class='tag'>Wilayah Terpilih</span></div>", unsafe_allow_html=True)
        df_box = df_sel if selected_regions else df_view
        fig_box = px.box(df_box, x='Wilayah', y='Harga', color='Wilayah', color_discrete_sequence=PALETTE, points='outliers')
        fig_box.update_layout(**get_base_layout('xaxis', 'yaxis', 'margin'), height=400, showlegend=False, xaxis=dict(**PLOTLY_BASE['xaxis'], title='', tickangle=-45), yaxis=dict(**PLOTLY_BASE['yaxis'], title='Harga (Rp)', tickformat=',.0f'), margin=dict(l=10,r=10,t=10,b=60))
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='hdiv'></div>", unsafe_allow_html=True)
    
    an3, an4 = st.columns([2,1])
    with an3:
        st.markdown("<div class='card'><div class='section-head'><h3>🚨 Deteksi Anomali Z-Score</h3></div>", unsafe_allow_html=True)
        anom_rows = []
        for prov in (selected_regions if selected_regions else all_regions):
            s = df_full[df_full['Wilayah']==prov].set_index('Tanggal')['Harga'].sort_index()
            if len(s) < 10: continue
            mask, zs = zscore_anomaly(s, w=30, threshold=z_thr)
            s_v = s[(s.index >= d_start) & (s.index <= d_end)]
            if s_v.empty: continue
            latest_z = zs.reindex(s_v.index).iloc[-1] if not zs.reindex(s_v.index).empty else 0
            if pd.isna(latest_z): latest_z = 0
            anom_rows.append(dict(Provinsi=prov, Harga=s_v.iloc[-1], Z_Score=latest_z, Anomali=int(mask.reindex(s_v.index).sum()), Status=('🔴 KRITIS' if abs(latest_z)>3 else '🟡 WASPADA' if abs(latest_z)>z_thr else '🟢 Normal')))

        if anom_rows:
            adf = pd.DataFrame(anom_rows).sort_values('Z_Score', key=abs, ascending=False)
            adf['Harga'] = adf['Harga'].apply(lambda x: f"Rp {x:,.0f}"); adf['Z_Score'] = adf['Z_Score'].apply(lambda x: f"{x:+.2f}")
            st.dataframe(adf, hide_index=True, use_container_width=True, height=250)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with an4:
        st.markdown("<div class='card'><div class='section-head'><h3>Pola Hari dalam Seminggu</h3></div>", unsafe_allow_html=True)
        day_map = {0:'Sen', 1:'Sel', 2:'Rab', 3:'Kam', 4:'Jum', 5:'Sab', 6:'Min'}
        df_dow = df_view.copy()
        df_dow['Hari'] = df_dow['Tanggal'].dt.dayofweek.map(day_map)
        dow_avg = df_dow.groupby('Hari')['Harga'].mean().reindex(list(day_map.values()))
        
        fig_dow = go.Figure(go.Bar(x=dow_avg.index, y=dow_avg.values, marker_color='#A78BFA', hovertemplate='%{x}<br>Rp %{y:,.0f}<extra></extra>'))
        fig_dow.update_layout(**get_base_layout('xaxis', 'yaxis'), height=250, margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(**PLOTLY_BASE['yaxis'], range=[dow_avg.min()*0.98, dow_avg.max()*1.02]))
        st.plotly_chart(fig_dow, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MUSIMAN & SIKLUS
# ══════════════════════════════════════════════════════════════════════════════
with tab_season:
    s_c1, s_c2 = st.columns([1,1])
    with s_c1:
        st.markdown("<div class='card'><div class='section-head'><h3>Heatmap Bulanan (Nasional)</h3></div>", unsafe_allow_html=True)
        nat_df = nat_full.reset_index(); nat_df.columns = ['Tanggal','Harga']
        heat_data = nat_df.groupby([nat_df['Tanggal'].dt.year, nat_df['Tanggal'].dt.month])['Harga'].mean().unstack(fill_value=np.nan)
        heat_data.columns = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][:len(heat_data.columns)]
        
        if not heat_data.empty:
            fig_heat = go.Figure(go.Heatmap(z=heat_data.values, x=heat_data.columns, y=heat_data.index.astype(str), colorscale=[[0,'#22D3EE'],[0.5,'#F0B429'],[1,'#EF4444']], text=[[f"Rp{v:,.0f}" if not np.isnan(v) else "-" for v in row] for row in heat_data.values], texttemplate="%{text}", textfont=dict(size=9), hovertemplate="Bulan: %{x}<br>Tahun: %{y}<br>Rp %{z:,.0f}<extra></extra>"))
            fig_heat.update_layout(**get_base_layout('xaxis', 'yaxis', 'margin'), height=350, margin=dict(l=10,r=10,t=5,b=5))
            st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s_c2:
        st.markdown("<div class='card'><div class='section-head'><h3>Tren Year-over-Year (YoY)</h3></div>", unsafe_allow_html=True)
        nat_yoy = nat_full.reset_index(); nat_yoy.columns = ['Tanggal','Harga']; nat_yoy['Tahun'] = nat_yoy['Tanggal'].dt.year.astype(str)
        nat_yoy['DummyDate'] = nat_yoy['Tanggal'].apply(lambda d: pd.Timestamp(year=2000, month=d.month, day=d.day))
        
        fig_yoy = px.line(nat_yoy, x='DummyDate', y='Harga', color='Tahun', color_discrete_sequence=['#3DD68C','#F0B429','#60A5FA','#F472B6','#A78BFA'])
        fig_yoy.update_traces(line=dict(width=2), hovertemplate='%{x|%d %b}<br>Rp %{y:,.0f}<extra></extra>')
        fig_yoy.update_layout(**get_base_layout('xaxis', 'yaxis', 'margin', 'legend'), height=350, xaxis=dict(**PLOTLY_BASE['xaxis'], title='', tickformat='%b'), yaxis=dict(**PLOTLY_BASE['yaxis'], title='Harga (Rp)', tickformat=',.0f'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_yoy, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — DATA & RINGKASAN
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown("### 📊 Ringkasan Statistik Periode Terpilih", unsafe_allow_html=True)
    summary_df = df_view.groupby('Wilayah')['Harga'].agg(['mean', 'min', 'max', 'std']).reset_index()
    summary_df.columns = ['Provinsi', 'Rata-rata', 'Terendah', 'Tertinggi', 'Volatilitas (Std)']
    summary_df['Rata-rata'] = summary_df['Rata-rata'].apply(lambda x: f"Rp {x:,.0f}")
    summary_df['Terendah'] = summary_df['Terendah'].apply(lambda x: f"Rp {x:,.0f}")
    summary_df['Tertinggi'] = summary_df['Tertinggi'].apply(lambda x: f"Rp {x:,.0f}")
    summary_df['Volatilitas (Std)'] = summary_df['Volatilitas (Std)'].apply(lambda x: f"Rp {x:,.0f}" if pd.notnull(x) else "-")
    
    st.dataframe(summary_df, hide_index=True, use_container_width=True)
    
    st.markdown("<div class='hdiv'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Data Mentah", unsafe_allow_html=True)
    
    d_c1, d_c2, d_c3 = st.columns([2,1,1])
    with d_c1: search_term = st.text_input("🔍 Cari provinsi...", placeholder="mis. Jakarta, Jawa...", label_visibility="collapsed")
    with d_c2: sort_col = st.selectbox("Urutkan", ["Harga (tinggi→rendah)","Harga (rendah→tinggi)","Provinsi A-Z","Tanggal Terbaru"], label_visibility="collapsed")
    with d_c3: show_all_dates = st.checkbox("Tampilkan semua tanggal", value=False)

    tbl_data = df_view.copy() if show_all_dates else df_now.copy()
    if search_term: tbl_data = tbl_data[tbl_data['Wilayah'].str.contains(search_term, case=False, na=False)]

    sort_map = {"Harga (tinggi→rendah)": ('Harga', False), "Harga (rendah→tinggi)": ('Harga', True), "Provinsi A-Z": ('Wilayah', True), "Tanggal Terbaru": ('Tanggal', False)}
    tbl_data = tbl_data.sort_values(sort_map[sort_col][0], ascending=sort_map[sort_col][1])

    tbl_disp = tbl_data[['Tanggal','Wilayah','Harga']].copy()
    tbl_disp['Status'] = tbl_data['Harga'].apply(lambda x: '⚠️ Waspada' if x > threshold else '✅ Stabil')
    tbl_disp['Tanggal'] = tbl_disp['Tanggal'].dt.strftime('%d %b %Y')
    tbl_disp['Harga'] = tbl_disp['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    tbl_disp.columns = ['Tanggal','Provinsi','Harga','Status']

    st.dataframe(tbl_disp, hide_index=True, use_container_width=True, height=450)

    ec1, ec2, ec3 = st.columns([2,1,1])
    with ec2: st.download_button("📥 Export CSV", data=tbl_data.to_csv(index=False, encoding='utf-8-sig'), file_name=f"harga_ayam_{latest_date.strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
    with ec3: st.download_button("📥 Export Lengkap", data=df_full.to_csv(index=False, encoding='utf-8-sig'), file_name=f"harga_ayam_FULL_{datetime.today().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""<div class='hdiv'></div><div style='text-align:center;padding:1rem 0 2rem;color:#6B7A8D;font-size:12px;'>
    <span style='font-family:"DM Serif Display",serif;font-size:14px;color:#9BAABD;'>AgriPulse</span> &nbsp;·&nbsp; Data: SP2KP Kemendag<br>
    <span style='opacity:.6;'>Built with Streamlit & Plotly</span>
</div>""", unsafe_allow_html=True)
