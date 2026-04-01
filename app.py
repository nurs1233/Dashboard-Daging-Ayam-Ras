import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Agrarian Intelligence | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS KUSTOM YANG DIPERBAIKI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');
    
    /* Reset & Base */
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif !important; 
        background-color: #F8FAF9 !important;
    }
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Manrope', sans-serif !important; 
        color: #012D1D !important;
    }
    
    /* Hide Default Header */
    header[data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    
    /* Top Navigation */
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
    .top-nav-brand::before {
        content: "🐔";
        font-size: 1.2rem;
    }
    .top-nav-links { 
        color: #5B6B63; 
        font-size: 13px; 
        font-weight: 600;
        display: flex;
        gap: 24px;
    }
    .top-nav-links span {
        cursor: pointer;
        transition: color 0.2s;
        padding: 4px 0;
    }
    .top-nav-links span:hover {
        color: #16A34A;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #012D1D 0%, #0A3D2E 100%) !important; 
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #D8F3DC !important; }
    section[data-testid="stSidebar"] .stSelectbox label, 
    section[data-testid="stSidebar"] .stSlider label, 
    section[data-testid="stSidebar"] .stDateInput label { 
        color: #A7C4B5 !important; 
        font-size: 11px !important; 
        text-transform: uppercase; 
        letter-spacing: 0.08em; 
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSlider > div,
    section[data-testid="stSidebar"] .stDateInput > div {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
    }
    
    /* Header Section */
    .header-container { 
        display: flex; 
        justify-content: space-between; 
        align-items: flex-start; 
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .header-left { flex: 1; min-width: 300px; }
    .live-badge { 
        display: inline-flex; 
        align-items: center; 
        gap: 8px; 
        padding: 6px 12px;
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        border-radius: 20px;
        margin-bottom: 12px;
        border: 1px solid #86EFAC;
    }
    .pulse { 
        width: 8px; 
        height: 8px; 
        background: #16A34A; 
        border-radius: 50%; 
        animation: pulse 2s infinite; 
        box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4);
    }
    @keyframes pulse { 
        0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 
        70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); } 
        100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } 
    }
    .page-title { 
        font-size: 2rem; 
        font-weight: 800; 
        color: #012D1D; 
        margin: 0; 
        line-height: 1.3;
    }
    .page-subtitle { 
        color: #5B6B63; 
        font-size: 0.95rem; 
        margin-top: 8px;
        line-height: 1.5;
    }
    
    /* Bento Cards */
    .bento-card { 
        background: linear-gradient(145deg, #ffffff 0%, #FAFBFA 100%); 
        border-radius: 16px; 
        padding: 1.5rem; 
        box-shadow: 0 4px 20px rgba(1, 45, 29, 0.08); 
        height: 100%; 
        border: 1px solid #E8EDEA;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .bento-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(1, 45, 29, 0.12);
    }
    
    /* Metric Cards */
    .metric-card { 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        min-height: 130px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
    }
    .border-secondary::before { background: linear-gradient(180deg, #8E4E14, #C47A2E); }
    .border-success::before { background: linear-gradient(180deg, #16A34A, #22C55E); }
    .border-error::before { background: linear-gradient(180deg, #BA1A1A, #EF4444); }
    .border-primary::before { background: linear-gradient(180deg, #012D1D, #0A3D2E); }
    
    .metric-title { 
        font-size: 11px; 
        font-weight: 700; 
        color: #6B7A72; 
        text-transform: uppercase; 
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .metric-value-row { 
        display: flex; 
        align-items: baseline; 
        gap: 6px; 
        margin-top: 4px;
    }
    .metric-currency { 
        font-size: 1rem; 
        font-weight: 700; 
        color: #8A9A92;
    }
    .metric-value { 
        font-size: 2rem; 
        font-weight: 800; 
        color: #012D1D; 
        line-height: 1;
    }
    .metric-sub { 
        font-size: 0.8rem; 
        color: #6B7A72; 
        margin-top: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .metric-sub span {
        color: #012D1D;
        font-weight: 600;
    }
    
    /* Chart Containers */
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E8EDEA;
    }
    .chart-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #012D1D;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-subtitle {
        color: #6B7A72;
        font-size: 0.85rem;
        margin: 4px 0 0 0;
    }
    
    /* Table Styling */
    .table-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid #E8EDEA;
        background: linear-gradient(135deg, #F8FAF9 0%, #ffffff 100%);
        border-radius: 16px 16px 0 0;
    }
    .table-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #012D1D;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .table-subtitle {
        color: #6B7A72;
        font-size: 0.85rem;
        margin: 4px 0 0 0;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-waspada {
        background: #FEF2F2;
        color: #93000A;
        border: 1px solid #FECACA;
    }
    .status-stabil {
        background: #F0FDF4;
        color: #002114;
        border: 1px solid #BBF7D0;
    }
    
    /* Footer */
    .footer {
        text-align: center; 
        margin-top: 3rem; 
        padding: 2rem;
        border-top: 1px solid #E8EDEA;
        color: #6B7A72;
        font-size: 0.85rem;
    }
    .footer-title {
        color: #012D1D;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .top-nav { padding: 0.75rem 1rem; margin: -2rem -1rem 1.5rem -1rem; }
        .page-title { font-size: 1.5rem; }
        .metric-value { font-size: 1.5rem; }
        .header-container { flex-direction: column; align-items: flex-start; }
    }
    
    /* Streamlit Component Overrides */
    .stButton > button {
        background: linear-gradient(135deg, #16A34A 0%, #0A3D2E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: transform 0.1s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 0 0 16px 16px !important;
        overflow: hidden !important;
    }
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

# --- FUNGSI PEMUATAN DATA (Tetap sama) ---
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
        raise FileNotFoundError("TIDAK ADA file .xlsx atau .csv ditemukan di direktori aplikasi!")

    all_data = []
    file_errors = []
    
    for file in files:
        df = None
        err = None
        try:
            if file.endswith('.csv'):
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                header_idx = -1
                for i, line in enumerate(lines[:30]):
                    if 'wilayah' in line.lower():
                        header_idx = i
                        break
                        
                if header_idx != -1:
                    df = pd.read_csv(file, skiprows=header_idx, dtype=str)
                    cols_to_drop = [c for c in df.columns if 'unnamed' in str(c).lower() or pd.isna(c)]
                    df = df.drop(columns=cols_to_drop)
                else:
                    err = "Kata 'Wilayah' tidak ditemukan di 30 baris pertama (CSV)."
                    
            elif file.endswith('.xlsx'):
                xls = pd.ExcelFile(file)
                found = False
                for sheet_name in xls.sheet_names:
                    df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None, dtype=str)
                    header_idx = -1
                    for i in range(min(30, len(df_raw))): 
                        row_str = " ".join([str(val).lower() for val in df_raw.iloc[i].values])
                        if 'wilayah' in row_str:
                            header_idx = i
                            break
                    if header_idx != -1:
                        df_raw.columns = df_raw.iloc[header_idx].astype(str).tolist()
                        df = df_raw.iloc[header_idx + 1:].copy()
                        cols_to_drop = [c for c in df.columns if 'nan' in str(c).lower() or str(c).strip() == '']
                        df = df.drop(columns=cols_to_drop)
                        found = True
                        break
                if not found:
                    err = "Kata 'Wilayah' tidak ditemukan di seluruh sheet (XLSX)."
                    
        except Exception as e:
            err = f"ERROR PYTHON -> {str(e)}"
            
        if df is not None and not df.empty:
            try:
                wilayah_col = [c for c in df.columns if 'wilayah' in str(c).lower()][0]
                df = df.rename(columns={wilayah_col: 'Wilayah'})
                df = df.dropna(subset=['Wilayah'])
                df = df[~df['Wilayah'].astype(str).str.contains('Sumber Data|Laporan|Periode', case=False, na=False)]
                
                date_columns = [c for c in df.columns if c != 'Wilayah']
                df_melted = pd.melt(
                    df, id_vars=['Wilayah'], value_vars=date_columns, 
                    var_name='Tanggal', value_name='Harga'
                )

                df_melted['Tanggal'] = pd.to_datetime(df_melted['Tanggal'], errors='coerce')
                df_melted['Harga'] = df_melted['Harga'].astype(str).str.replace(r'[^\d]', '', regex=True)
                df_melted['Harga'] = pd.to_numeric(df_melted['Harga'], errors='coerce')
                df_melted['Wilayah'] = df_melted['Wilayah'].astype(str).str.strip()

                df_melted = df_melted.dropna(subset=['Tanggal', 'Harga'])
                df_melted = df_melted[df_melted['Harga'] > 0]
                
                if not df_melted.empty:
                    all_data.append(df_melted)
                else:
                    file_errors.append(f"{os.path.basename(file)}: Tersaring habis.")
            except Exception as e:
                file_errors.append(f"{os.path.basename(file)}: Gagal parsing -> {str(e)}")
        else:
            if err:
                file_errors.append(f"{os.path.basename(file)}: {err}")

    if not all_data:
        error_msg = "Gagal memproses data valid. Detail error:\n"
        for err in file_errors:
            error_msg += f"• {err}\n"
        raise ValueError(error_msg)

    combined_df = pd.concat(all_data, ignore_index=True)
    
    if 'Lat' not in combined_df.columns:
        combined_df['Lat'] = None
    if 'Lon' not in combined_df.columns:
        combined_df['Lon'] = None
        
    return combined_df

# --- EKSEKUSI PEMUATAN DATA ---
try:
    df_full = load_all_data()
except Exception as e:
    st.error(f"❌ **Error Memuat Data:** {str(e)}")
    st.info("💡 Pastikan file CSV/Excel Anda memiliki kolom 'Wilayah' dan format tanggal yang valid.")
    st.stop()

if df_full.empty:
    st.error("⚠️ Data berhasil dibaca tetapi hasilnya kosong setelah pemrosesan.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style='display:flex; align-items:center; gap:12px; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.2);'>
        <div style='width:48px; height:48px; background:linear-gradient(135deg, #1B4332, #2D5A45); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>🐔</div>
        <div>
            <h1 style='color:white; margin:0; font-size:17px; font-weight:700;'>Daging Ayam Ras</h1>
            <p style='color:#A7C4B5; font-size:10px; margin:4px 0 0 0; letter-spacing:1.5px; text-transform:uppercase;'>Market Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    max_d = df_full['Tanggal'].max().date()
    min_d = df_full['Tanggal'].min().date()
    
    if max_d == min_d:
        default_start = min_d
    else:
        default_start = max_d - timedelta(days=30)
        if default_start < min_d:
            default_start = min_d
            
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin:1.5rem 0 0.5rem 0;'>📅 Timeframe</p>", unsafe_allow_html=True)
    date_range = st.date_input("", value=(default_start, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin:1.5rem 0 0.5rem 0;'>⚠️ Threshold Harga</p>", unsafe_allow_html=True)
    threshold = st.slider("", 25000, 60000, 40000, label_visibility="collapsed")
    st.caption(f"Nilai: **Rp {threshold:,.0f}**")
    
    st.markdown("<p style='color:#A7C4B5; font-size:11px; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin:1.5rem 0 0.5rem 0;'>📍 Filter Wilayah</p>", unsafe_allow_html=True)
    all_regs = sorted(df_full['Wilayah'].unique())
    default_selection = ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur'] if all(r in all_regs for r in ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur']) else all_regs[:3]
    selected_regions = st.multiselect("", all_regs, default=default_selection, label_visibility="collapsed", placeholder="Pilih wilayah...")
    
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.2);'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("""
    <div style='margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 12px; font-size: 11px; color: #A7C4B5;'>
        <strong style='color: #D8F3DC;'>💡 Tips:</strong><br>
        • Gunakan filter untuk fokus pada wilayah tertentu<br>
        • Adjust threshold untuk alert harga<br>
        • Export data dari tabel di bawah
    </div>
    """, unsafe_allow_html=True)

# --- FILTERING DATA ---
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df_full[(df_full['Tanggal'] >= start) & (df_full['Tanggal'] <= end)].copy()
else:
    df = df_full.copy()

df['Status'] = df['Harga'].apply(lambda x: 'Waspada' if x > threshold else 'Stabil')
df_filtered = df[df['Wilayah'].isin(selected_regions)] if selected_regions else df

latest_date = df['Tanggal'].max()
df_now = df[df['Tanggal'] == latest_date]

# --- HEADER SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"""
    <div class='header-left'>
        <div class='live-badge'>
            <div class='pulse'></div>
            <span style='font-size: 11px; font-weight: 700; color: #166534; text-transform: uppercase; letter-spacing: 0.8px;'>● Market Live</span>
        </div>
        <h1 class='page-title'>Dashboard Harga Daging Ayam Ras</h1>
        <p class='page-subtitle'>Monitor pergerakan harga komoditas harian seluruh Indonesia • Update terakhir: <strong>{latest_date.strftime('%d %B %Y')}</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.markdown("""
    <div style='text-align: right;'>
        <div style='background: #F0FDF4; padding: 12px 16px; border-radius: 12px; border: 1px solid #BBF7D0;'>
            <p style='margin: 0; font-size: 11px; color: #6B7A72; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;'>Data Source</p>
            <p style='margin: 4px 0 0 0; font-size: 13px; font-weight: 600; color: #012D1D;'>SP2KP Kemendag</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1px; background: linear-gradient(90deg, transparent, #E8EDEA, transparent); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

# --- METRIC CARDS ---
if not df_now.empty:
    avg_now = df_now['Harga'].mean()
    min_row = df_now.loc[df_now['Harga'].idxmin()]
    max_row = df_now.loc[df_now['Harga'].idxmax()]
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class='bento-card metric-card border-secondary'>
            <div>
                <span class='metric-title'>📊 Rata-rata Nasional</span>
                <div class='metric-value-row'>
                    <span class='metric-currency'>Rp</span>
                    <span class='metric-value'>{avg_now:,.0f}</span>
                </div>
            </div>
            <span class='metric-sub'>Per {latest_date.strftime('%d/%m')}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class='bento-card metric-card border-success'>
            <div>
                <span class='metric-title'>📉 Harga Terendah</span>
                <div class='metric-value-row'>
                    <span class='metric-currency'>Rp</span>
                    <span class='metric-value'>{min_row['Harga']:,.0f}</span>
                </div>
            </div>
            <span class='metric-sub'>📍 <span>{min_row['Wilayah']}</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
        <div class='bento-card metric-card border-error'>
            <div>
                <span class='metric-title'>📈 Harga Tertinggi</span>
                <div class='metric-value-row'>
                    <span class='metric-currency'>Rp</span>
                    <span class='metric-value'>{max_row['Harga']:,.0f}</span>
                </div>
            </div>
            <span class='metric-sub'>📍 <span>{max_row['Wilayah']}</span></span>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class='bento-card metric-card border-primary'>
            <div>
                <span class='metric-title'>🗄️ Total Data</span>
                <div class='metric-value-row'>
                    <span class='metric-value'>{len(df_full):,}</span>
                </div>
            </div>
            <span class='metric-sub'>✅ Synced & Validated</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- CHARTS GRID ---
# Row 1: Line Chart + Bar Chart
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("""
    <div class='bento-card'>
        <div class='chart-header'>
            <div>
                <h3 class='chart-title'>📈 Tren Harga Over Time</h3>
                <p class='chart-subtitle'>Pergerakan harga harian berdasarkan wilayah terpilih</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    df_line = df.groupby('Tanggal')['Harga'].mean().reset_index()
    fig1 = go.Figure()
    
    # National average line
    fig1.add_trace(go.Scatter(
        x=df_line['Tanggal'], 
        y=df_line['Harga'], 
        name="🇮🇩 Nasional (Avg)", 
        line=dict(color='#8E4E14', width=3, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Rata-rata: Rp %{y:,.0f}<extra></extra>'
    ))
    
    # Regional lines
    colors = ['#012D1D', '#16A34A', '#BA1A1A', '#EA9147', '#7C3AED', '#0891B2']
    if selected_regions:
        for i, r in enumerate(selected_regions[:5]):
            rd = df[df['Wilayah']==r]
            if not rd.empty:
                fig1.add_trace(go.Scatter(
                    x=rd['Tanggal'], 
                    y=rd['Harga'], 
                    name=f"📍 {r}", 
                    line=dict(color=colors[i%len(colors)], width=2),
                    hovertemplate='<b>%{x}</b><br>{name}: Rp %{y:,.0f}<extra></extra>'
                ))
    
    fig1.update_layout(
        height=320, 
        margin=dict(l=20,r=20,t=10,b=20), 
        hovermode='x unified', 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.3, 
            xanchor="center", 
            x=0.5,
            font=dict(size=10)
        ),
        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(
            gridcolor='#E8EDEA', 
            tickfont=dict(size=9),
            tickformat=',.0f',
            title='Harga (Rp)'
        )
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='bento-card'>
        <div class='chart-header'>
            <h3 class='chart-title'>📊 Ranking Wilayah</h3>
        </div>
    """, unsafe_allow_html=True)
    
    top_regions = df_now.sort_values('Harga', ascending=True).head(8)
    fig2 = px.bar(
        top_regions, 
        x='Harga', 
        y='Wilayah', 
        orientation='h', 
        color='Harga', 
        color_continuous_scale=['#16A34A', '#EAB308', '#BA1A1A'],
        hover_data={'Harga': ':,.0f', 'Wilayah': False}
    )
    fig2.update_layout(
        height=340, 
        margin=dict(l=0,r=10,t=0,b=10), 
        coloraxis_showscale=False, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder':'total ascending', 'tickfont': dict(size=9)},
        xaxis=dict(visible=False),
        hoverlabel=dict(bgcolor="white", font_size=11)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Row 2: Map + Box Plot
st.markdown("<br>", unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    st.markdown("""
    <div class='bento-card'>
        <div class='chart-header'>
            <h3 class='chart-title'>🗺️ Peta Sebaran Harga</h3>
        </div>
    """, unsafe_allow_html=True)
    
    df_map = df_now.dropna(subset=['Lat', 'Lon'])
    if not df_map.empty and df_map['Lat'].notna().any():
        fig_map = px.scatter_mapbox(
            df_map, 
            lat="Lat", 
            lon="Lon", 
            color="Harga", 
            size="Harga", 
            hover_name="Wilayah", 
            color_continuous_scale=['#16A34A', '#EAB308', '#BA1A1A'], 
            size_max=25, 
            zoom=3.5, 
            mapbox_style="carto-positron",
            hover_data={'Harga': ':,.0f', 'Lat': False, 'Lon': False}
        )
        fig_map.update_layout(
            height=320, 
            margin=dict(l=0,r=0,t=0,b=0), 
            coloraxis_showscale=False,
            mapbox=dict(
                style="carto-positron",
                zoom=3.5,
                center={"lat": -2.5, "lon": 118}
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("""
        **📍 Data Koordinat Tidak Tersedia**
        
        Untuk menampilkan peta interaktif, tambahkan kolom `Lat` dan `Lon` pada data Anda dengan koordinat masing-masing wilayah.
        
        *Contoh format:*
        ```
        Wilayah, Lat, Lon
        DKI Jakarta, -6.2088, 106.8456
        Jawa Barat, -6.9175, 107.6191
        ```
        """)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class='bento-card'>
        <div class='chart-header'>
            <h3 class='chart-title'>📦 Distribusi Harga</h3>
        </div>
    """, unsafe_allow_html=True)
    
    plot_df = df_filtered if selected_regions else df[df['Wilayah'].isin(df['Wilayah'].unique()[:6])]
    if not plot_df.empty:
        fig_box = px.box(
            plot_df, 
            x="Harga", 
            y="Wilayah", 
            color="Wilayah", 
            color_discrete_sequence=['#012D1D', '#8E4E14', '#16A34A', '#EA9147', '#BA1A1A', '#7C3AED'],
            hover_data={'Harga': ':,.0f'}
        )
        fig_box.update_layout(
            height=320, 
            margin=dict(l=0,r=10,t=0,b=10), 
            showlegend=False, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            yaxis={'categoryorder':'median ascending', 'tickfont': dict(size=9)},
            xaxis=dict(
                title="Harga (Rp)", 
                gridcolor='#E8EDEA',
                tickfont=dict(size=9),
                tickformat=',.0f'
            ),
            hoverlabel=dict(bgcolor="white", font_size=10)
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("⚠️ Tidak ada data untuk ditampilkan pada filter saat ini.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- DATA TABLE SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class='bento-card' style='padding: 0; overflow: hidden;'>
    <div class='table-header'>
        <h3 class='table-title'>📋 Rincian Data Harga Harian</h3>
        <p class='table-subtitle'>Data terbaru per provinsi • Klik header kolom untuk sort</p>
    </div>
""", unsafe_allow_html=True)

if not df_now.empty:
    styled_df = df_now[['Tanggal', 'Wilayah', 'Harga', 'Status']].sort_values('Harga', ascending=False).copy()
    styled_df['Tanggal'] = styled_df['Tanggal'].dt.strftime('%d %b %Y')
    styled_df['Harga_Formatted'] = styled_df['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    
    # Custom status badge function
    def status_badge(status):
        if status == 'Waspada':
            return '<span class="status-badge status-waspada">⚠️ Waspada</span>'
        return '<span class="status-badge status-stabil">✅ Stabil</span>'
    
    styled_df['Status_Badge'] = styled_df['Status'].apply(status_badge)
    
    # Display with custom formatting
    display_df = styled_df[['Tanggal', 'Wilayah', 'Harga_Formatted', 'Status_Badge']].copy()
    display_df.columns = ['📅 Tanggal', '📍 Wilayah', '💰 Harga', '🔔 Status']
    
    st.dataframe(
        display_df,
        use_container_width=True, 
        hide_index=True, 
        height=350,
        column_config={
            "📅 Tanggal": st.column_config.TextColumn(width="small"),
            "📍 Wilayah": st.column_config.TextColumn(width="medium"),
            "💰 Harga": st.column_config.TextColumn(width="small"),
            "🔔 Status": st.column_config.TextColumn(width="small")
        }
    )
    
    # Export button
    col_exp1, col_exp2 = st.columns([4,1])
    with col_exp2:
        csv = styled_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"harga_ayam_{latest_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.warning("⚠️ Tidak ada data untuk tanggal terpilih.")

st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class='footer'>
    <p class='footer-title'>🐔 Agrarian Intelligence Dashboard</p>
    <p style='margin: 0;'>Data sourced from <strong>Sistem Pemantauan Pasar dan Kebutuhan Pokok (SP2KP)</strong> • Kementerian Perdagangan RI</p>
    <p style='margin: 8px 0 0 0; opacity: 0.8;'>© 2026 Agrarian Intelligence • Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)

# --- TOOLTIP HELPER (Optional) ---
st.markdown("""
<script>
// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
</script>
""", unsafe_allow_html=True)
