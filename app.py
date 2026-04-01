import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from data_loader import load_all_data

# --- SETUP PATH ---
# Mengambil direktori tempat file app.py berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Market Intelligence | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS KUSTOM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    :root { --primary: #012D1D; --accent: #EAB308; --success: #16A34A; --danger: #DC2626; --neutral: #64748B; }
    header, footer { visibility: hidden; }
    .main { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #012D1D !important; border-right: 1px solid rgba(255,255,255,0.1); }
    section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #F1F5F9; }
    .card-label { font-size: 0.75rem; font-weight: 700; color: var(--neutral); text-transform: uppercase; }
    .card-value { font-size: 1.6rem; font-weight: 800; color: var(--primary); margin: 0.25rem 0; }
    .delta-up { color: var(--danger); font-size: 0.75rem; font-weight: 600; }
    .delta-down { color: var(--success); font-size: 0.75rem; font-weight: 600; }
    .chart-container { background: white; padding: 1.5rem; border-radius: 1rem; border: 1px solid #F1F5F9; margin-bottom: 1.5rem; }
    .pulse { width: 10px; height: 10px; background: #16A34A; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); } 100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); } }
</style>
""", unsafe_allow_html=True)

# --- PEMUATAN DATA ---
@st.cache_data
def get_data():
    return load_all_data(BASE_DIR)

df_full = get_data()

if df_full.empty:
    st.error("⚠️ **Data tidak ditemukan atau gagal dimuat.**")
    st.info(f"Pastikan folder `Data` berisi file CSV statistik harian di lokasi: `{os.path.join(BASE_DIR, 'Data')}`")
    # Tampilkan struktur folder untuk debug jika perlu
    if st.checkbox("Lihat Debug Info (Struktur Folder)"):
        st.write("Current Directory Content:", os.listdir(BASE_DIR))
        if os.path.exists(os.path.join(BASE_DIR, 'Data')):
            st.write("Data Directory Content:", os.listdir(os.path.join(BASE_DIR, 'Data')))
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;'>
        <h3 style='margin:0'>🐔 AGRI-INTEL</h3>
        <p style='color: #86AF99; font-size: 10px; margin:0; font-weight:700;'>POULTRY MARKET TRACKER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Filter Analisis")
    
    max_d = df_full['Tanggal'].max().date()
    min_d = df_full['Tanggal'].min().date()
    
    date_range = st.date_input("Rentang Waktu", value=(max_d - timedelta(days=30), max_d), min_value=min_d, max_value=max_d)
    threshold = st.slider("Ambang Batas Waspada (Rp)", 25000, 60000, 40000)
    
    all_regs = sorted(df_full['Wilayah'].unique())
    selected_regions = st.multiselect("Wilayah Fokus", all_regs, default=['DKI Jakarta', 'Jawa Barat', 'Jawa Timur'] if len(all_regs) > 3 else all_regs)
    
    if st.button("🔄 Segarkan Database"):
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

# --- HEADER ---
st.markdown(f"""
<div style='margin-bottom: 25px;'>
    <div style='display:flex; align-items:center; gap:10px;'>
        <div class='pulse'></div>
        <span style='color:var(--neutral); font-weight:700; font-size:11px; letter-spacing:1px;'>MONITORING HARGA NASIONAL</span>
    </div>
    <h1 style='color:var(--primary); font-weight:800; margin:0; font-size:2.2rem;'>Dashboard Daging Ayam Ras</h1>
    <p style='color:var(--neutral); margin-top:5px; font-size: 0.9rem;'>Analisis tren pasar harian berdasarkan data historis SP2KP.</p>
</div>
""", unsafe_allow_html=True)

# --- METRIKS ---
m1, m2, m3, m4 = st.columns(4)
latest_date = df['Tanggal'].max()
df_now = df[df['Tanggal'] == latest_date]
avg_now = df_now['Harga'].mean()
avg_prev = df_now['Prev_Harga'].mean()
delta_pct = ((avg_now - avg_prev) / avg_prev * 100) if (pd.notna(avg_prev) and avg_prev != 0) else 0

with m1:
    st.markdown(f"<div class='metric-card'><div class='card-label'>Rata-rata Nasional</div><div class='card-value'>Rp {avg_now:,.0f}</div><div class='{'delta-up' if delta_pct > 0 else 'delta-down'}'>{'▲' if delta_pct > 0 else '▼'} {abs(delta_pct):.1f}% vs Kemarin</div></div>", unsafe_allow_html=True)

with m2:
    peak = df_now.loc[df_now['Harga'].idxmax()]
    st.markdown(f"<div class='metric-card'><div class='card-label'>Harga Tertinggi</div><div class='card-value'>Rp {peak['Harga']:,.0f}</div><div style='font-size:11px; color:var(--neutral);'>📍 {peak['Wilayah']}</div></div>", unsafe_allow_html=True)

with m3:
    st.markdown(f"<div class='metric-card'><div class='card-label'>Status Waspada</div><div class='card-value' style='color:var(--danger)'>{len(df_now[df_now['Status']=='Waspada'])} Wilayah</div><div style='font-size:11px; color:var(--neutral);'>Batas: Rp {threshold:,.0f}</div></div>", unsafe_allow_html=True)

with m4:
    st.markdown(f"<div class='metric-card'><div class='card-label'>Periode Data</div><div class='card-value' style='font-size:1.2rem'>{min_d.strftime('%b %y')} - {max_d.strftime('%b %y')}</div><div style='font-size:11px; color:var(--neutral);'>{len(df_full):,} Data Poin</div></div>", unsafe_allow_html=True)

# --- VISUALS ---
st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([1.7, 1.3])

with c1:
    st.markdown("<div class='chart-container'><h3>📈 Pergerakan Harga</h3>", unsafe_allow_html=True)
    df_line = df.groupby('Tanggal')['Harga'].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_line['Tanggal'], y=df_line['Harga'], name="Nasional", line=dict(color='#012D1D', width=3)))
    if selected_regions:
        for r in selected_regions:
            rd = df[df['Wilayah']==r]
            fig.add_trace(go.Scatter(x=rd['Tanggal'], y=rd['Harga'], name=r, line=dict(width=1.5), opacity=0.5))
    fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), hovermode='x unified', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-container'><h3>🗺️ Sebaran Harga</h3>", unsafe_allow_html=True)
    df_map = df_now.dropna(subset=['Lat', 'Lon'])
    if not df_map.empty:
        fig_map = px.scatter_mapbox(df_map, lat="Lat", lon="Lon", color="Harga", size="Harga", hover_name="Wilayah", color_continuous_scale="RdYlGn_r", size_max=15, zoom=3.5, mapbox_style="carto-positron")
        fig_map.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Data koordinat tidak lengkap untuk peta.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TABEL ---
st.markdown("### 📋 Detail Harga Per Wilayah (Terbaru)")
st.dataframe(
    df_now[['Wilayah', 'Harga', 'Status']].sort_values('Harga', ascending=False).style
    .format({'Harga': 'Rp {:,.0f}'})
    .apply(lambda x: ['background-color: #FEE2E2; color: #991B1B' if v == 'Waspada' else '' for v in x], subset=['Status']),
    use_container_width=True, hide_index=True
)

st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 11px; margin-top: 30px;'>Dashboard v2.6 • © 2026 Agrarian Intelligence</p>", unsafe_allow_html=True)
