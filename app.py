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

# --- CSS KUSTOM (Meniru Tailwind Design) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');
    
    /* Global Typography & Background */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Manrope', sans-serif !important; }
    .stApp { background-color: #F3F4F5; }
    
    /* Top Navigation Simulation */
    .top-nav {
        background-color: #ffffff;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #E1E3E4;
        margin: -4rem -4rem 2rem -4rem;
        z-index: 999;
    }
    .top-nav-brand { font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.25rem; color: #012D1D; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { 
        background-color: #012D1D !important; 
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: #D8F3DC; }
    section[data-testid="stSidebar"] .stSelectbox label, 
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: #86AF99 !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Header Section */
    .header-container { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 2rem; }
    .live-badge { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
    .pulse { width: 8px; height: 8px; background: #16A34A; border-radius: 50%; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 70% { box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); } 100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } }
    .page-title { font-size: 2.25rem; font-weight: 800; color: #012D1D; margin: 0; line-height: 1.2; }
    .page-subtitle { color: #414844; font-size: 0.9rem; margin-top: 4px; }
    
    /* Bento Grid Cards */
    .bento-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
        border: 1px solid #E1E3E4;
    }
    
    /* Metric Cards */
    .metric-wrapper { display: flex; flex-direction: column; justify-content: space-between; height: 120px; }
    .metric-title { font-size: 10px; font-weight: 700; color: #717973; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value-container { display: flex; align-items: baseline; gap: 4px; margin-top: 1rem; }
    .metric-currency { font-size: 0.875rem; font-weight: 700; color: #717973; }
    .metric-value { font-size: 1.875rem; font-weight: 800; color: #012D1D; }
    .metric-sub { font-size: 0.75rem; color: #717973; margin-top: 4px; font-weight: 500;}
    
    .border-secondary { border-left: 4px solid #8E4E14; }
    .border-success { border-left: 4px solid #16A34A; }
    .border-error { border-left: 4px solid #BA1A1A; }
    .border-primary { border-left: 4px solid #012D1D; }
    
    /* Hide Streamlit elements */
    header[data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 4rem; }
</style>
""", unsafe_allow_html=True)

# --- FAKE TOP NAV ---
st.markdown("""
<div class="top-nav">
    <div class="top-nav-brand">Agrarian Intelligence</div>
    <div style="color: #717973; font-size: 14px; font-weight: 600;">Dashboard &nbsp; • &nbsp; Analysis &nbsp; • &nbsp; Reports</div>
</div>
""", unsafe_allow_html=True)

# --- FUNGSI PEMUATAN DATA (MENGGANTIKAN DATA_LOADER.PY) ---
@st.cache_data
def load_all_data():
    """
    Mencari seluruh file CSV/XLSX di dalam root aplikasi dan sub-foldernya.
    Logika unpivoting (melt) dan pembersihan disertakan di sini.
    """
    base_search_path = "."
    
    # 1. Cari semua file CSV dan XLSX
    files = []
    for root, dirs, filenames in os.walk(base_search_path):
        # Abaikan folder sistem untuk mempercepat proses
        if '/.' in root or '\\.' in root or 'venv' in root or '__pycache__' in root:
            continue
        for f in filenames:
            if f.endswith('.csv') or f.endswith('.xlsx'):
                files.append(os.path.join(root, f))
    
    if not files:
        raise FileNotFoundError(f"TIDAK ADA file .xlsx atau .csv ditemukan di direktori aplikasi!")

    all_data = []
    for file in files:
        try:
            # Skip 3 baris metadata
            if file.endswith('.csv'):
                df = pd.read_csv(file, skiprows=3)
            else:
                df = pd.read_excel(file, skiprows=3)
        except Exception:
            continue

        if df.empty:
            continue

        # Deteksi kolom 'Wilayah'
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

    if not all_data:
        raise ValueError("File ditemukan, tapi tidak ada data yang valid untuk dibaca (Mungkin format kolom berbeda).")

    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Injeksi kolom Lat/Lon kosong untuk mencegah error Peta di bawah
    if 'Lat' not in combined_df.columns:
        combined_df['Lat'] = None
    if 'Lon' not in combined_df.columns:
        combined_df['Lon'] = None
        
    return combined_df

# --- EKSEKUSI PEMUATAN DATA ---
try:
    df_full = load_all_data()
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")
    st.stop()

if df_full.empty:
    st.error("Data berhasil dibaca tetapi hasilnya kosong.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom: 2rem;'><div style='width:40px; height:40px; background:#1B4332; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:20px;'>🐔</div><div><h1 style='color:white; margin:0; font-size:16px;'>Daging Ayam Ras</h1><p style='color:#86AF99; font-size:10px; margin:0; letter-spacing:1px;'>MARKET INTELLIGENCE</p></div></div>", unsafe_allow_html=True)
    
    max_d = df_full['Tanggal'].max().date()
    min_d = df_full['Tanggal'].min().date()
    
    # Pencegahan jika min dan max date sama
    if max_d == min_d:
        default_start = min_d
    else:
        default_start = max_d - timedelta(days=30)
        if default_start < min_d:
            default_start = min_d
            
    date_range = st.date_input("Timeframe", value=(default_start, max_d), min_value=min_d, max_value=max_d)
    threshold = st.slider("Batas Waspada (Rp)", 25000, 60000, 40000)
    
    all_regs = sorted(df_full['Wilayah'].unique())
    selected_regions = st.multiselect("Filter Regions", all_regs, default=['DKI Jakarta', 'Jawa Barat', 'Jawa Timur'] if 'DKI Jakarta' in all_regs else all_regs[:3])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Live Data", use_container_width=True):
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

# --- HEADER SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"""
    <div>
        <div class='live-badge'>
            <div class='pulse'></div>
            <span style='font-size: 10px; font-weight: 700; color: #717973; text-transform: uppercase; letter-spacing: 1px;'>Market Live</span>
        </div>
        <h1 class='page-title'>Dashboard Harga Daging Ayam Ras</h1>
        <p class='page-subtitle'>Laporan analisis harga komoditas harian seluruh wilayah Indonesia. Update: {latest_date.strftime('%d %b %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- METRIC CARDS ---
if not df_now.empty:
    avg_now = df_now['Harga'].mean()
    min_row = df_now.loc[df_now['Harga'].idxmin()]
    max_row = df_now.loc[df_now['Harga'].idxmax()]
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class='bento-card border-secondary metric-wrapper'>
            <span class='metric-title'>Rata-rata Harga Nasional</span>
            <div>
                <div class='metric-value-container'><span class='metric-currency'>Rp</span><span class='metric-value'>{avg_now:,.0f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='bento-card border-success metric-wrapper'>
            <span class='metric-title'>Harga Terendah</span>
            <div>
                <div class='metric-value-container'><span class='metric-currency'>Rp</span><span class='metric-value'>{min_row['Harga']:,.0f}</span></div>
                <div class='metric-sub'>Wilayah: {min_row['Wilayah']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class='bento-card border-error metric-wrapper'>
            <span class='metric-title'>Harga Tertinggi</span>
            <div>
                <div class='metric-value-container'><span class='metric-currency'>Rp</span><span class='metric-value'>{max_row['Harga']:,.0f}</span></div>
                <div class='metric-sub'>Wilayah: {max_row['Wilayah']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class='bento-card border-primary metric-wrapper'>
            <span class='metric-title'>Total Record Data</span>
            <div>
                <div class='metric-value-container'><span class='metric-value'>{len(df_full):,}</span><span class='metric-currency'>Entries</span></div>
                <div class='metric-sub'>Syncing up to date</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- CHARTS BENTO GRID ---
# Row 1: Line Chart (8) & Bar Chart (4)
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("<div class='bento-card'><h3 style='color: #012D1D; font-size: 1.25rem; margin-bottom: 0;'>📈 Tren Harga Over Time</h3><p style='color: #717973; font-size: 0.85rem; margin-bottom: 1rem;'>Pergerakan harga harian berdasarkan wilayah</p>", unsafe_allow_html=True)
    
    df_line = df.groupby('Tanggal')['Harga'].mean().reset_index()
    fig1 = go.Figure()
    # Nasional
    fig1.add_trace(go.Scatter(x=df_line['Tanggal'], y=df_line['Harga'], name="Nasional", line=dict(color='#8E4E14', width=3, dash='dash')))
    
    # Wilayah Terpilih
    colors = ['#012D1D', '#16A34A', '#BA1A1A', '#EA9147']
    if selected_regions:
        for i, r in enumerate(selected_regions[:4]):
            rd = df[df['Wilayah']==r]
            fig1.add_trace(go.Scatter(x=rd['Tanggal'], y=rd['Harga'], name=r, line=dict(color=colors[i%len(colors)], width=2.5)))
            
    fig1.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0), hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    fig1.update_xaxes(showgrid=False)
    fig1.update_yaxes(gridcolor='#E1E3E4')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='bento-card'><h3 style='color: #012D1D; font-size: 1.25rem; margin-bottom: 1rem;'>📊 Rata-rata per Wilayah</h3>", unsafe_allow_html=True)
    
    # Top 5 Regions Data
    top_regions = df_now.sort_values('Harga', ascending=False).head(7)
    fig2 = px.bar(top_regions, x='Harga', y='Wilayah', orientation='h', color='Harga', color_continuous_scale=['#16A34A', '#EAB308', '#BA1A1A'])
    fig2.update_layout(height=320, margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
    fig2.update_xaxes(visible=False)
    fig2.update_yaxes(title="")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Map/Heatmap (6) & Box Plot (6)
c3, c4 = st.columns(2)

with c3:
    st.markdown("<div class='bento-card'><h3 style='color: #012D1D; font-size: 1.25rem; margin-bottom: 1rem;'>🗺️ Peta Distribusi Harga</h3>", unsafe_allow_html=True)
    df_map = df_now.dropna(subset=['Lat', 'Lon'])
    if not df_map.empty:
        fig_map = px.scatter_mapbox(df_map, lat="Lat", lon="Lon", color="Harga", size="Harga", hover_name="Wilayah", color_continuous_scale=['#16A34A', '#EAB308', '#BA1A1A'], size_max=15, zoom=3.5, mapbox_style="carto-positron")
        fig_map.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Data koordinat (Lat/Lon) belum tersedia di dalam data Anda untuk menampilkan peta.")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='bento-card'><h3 style='color: #012D1D; font-size: 1.25rem; margin-bottom: 1rem;'>🕯️ Distribusi Harga (Box Plot)</h3>", unsafe_allow_html=True)
    
    # Box plot untuk region yang difilter (atau 5 region random jika tidak ada filter)
    plot_df = df_filtered if selected_regions else df[df['Wilayah'].isin(df['Wilayah'].unique()[:5])]
    fig_box = px.box(plot_df, x="Harga", y="Wilayah", color="Wilayah", color_discrete_sequence=['#012D1D', '#8E4E14', '#16A34A', '#EA9147', '#BA1A1A'])
    fig_box.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'median ascending'})
    fig_box.update_xaxes(title="Harga (Rp)", gridcolor='#E1E3E4')
    fig_box.update_yaxes(title="")
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DATA TABLE ---
st.markdown("<div class='bento-card' style='padding: 0;'><div style='padding: 1.5rem; border-bottom: 1px solid #E1E3E4;'><h3 style='color: #012D1D; font-size: 1.25rem; margin:0;'>📋 Rincian Data Harga Harian</h3><p style='color: #717973; font-size: 0.85rem; margin:0;'>Update terbaru dari Provinsi di Indonesia</p></div>", unsafe_allow_html=True)

# Tampilkan tabel menggunakan styling
styled_df = df_now[['Tanggal', 'Wilayah', 'Harga', 'Status']].sort_values('Harga', ascending=False)
styled_df['Tanggal'] = styled_df['Tanggal'].dt.strftime('%d %b %Y')

st.dataframe(
    styled_df.style
    .format({'Harga': 'Rp {:,.0f}'})
    .apply(lambda x: ['background-color: #FFDAD6; color: #93000A; font-weight: bold' if v == 'Waspada' else 'background-color: #C1ECD4; color: #002114; font-weight: bold' for v in x], subset=['Status']),
    use_container_width=True, hide_index=True, height=400
)
st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding-bottom: 2rem;'>
    <h4 style='color: #012D1D; font-weight: 800; font-size: 14px; margin:0;'>Dashboard Harga Daging Ayam Ras</h4>
    <p style='color: #717973; font-size: 12px; margin-top: 4px;'>Data sourced from Sistem Pemantauan Pasar dan Kebutuhan Pokok (SP2KP). © 2026 Agrarian Intelligence.</p>
</div>
""", unsafe_allow_html=True)
