import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from data_loader import load_all_data

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Market Intelligence | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS KUSTOM (TEMA PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    :root {
        --primary: #012D1D;
        --accent: #EAB308;
        --success: #16A34A;
        --danger: #DC2626;
        --neutral: #64748B;
    }
    header, footer { visibility: hidden; }
    .main { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] {
        background-color: #012D1D !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #F1F5F9;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-4px); }
    .card-label { font-size: 0.75rem; font-weight: 700; color: var(--neutral); text-transform: uppercase; }
    .card-value { font-size: 1.5rem; font-weight: 800; color: var(--primary); margin: 0.25rem 0; }
    .delta-up { color: var(--danger); font-size: 0.75rem; font-weight: 600; }
    .delta-down { color: var(--success); font-size: 0.75rem; font-weight: 600; }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #F1F5F9;
        margin-bottom: 1.5rem;
    }
    .status-pill {
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
    }
    .pulse {
        width: 10px;
        height: 10px;
        background: #16A34A;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); }
        100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- PEMUATAN DATA ---
@st.cache_data
def get_data():
    # Mengambil data asli dari folder Data
    df = load_all_data('nurs1233/dashboard-daging-ayam-ras/Dashboard-Daging-Ayam-Ras-fe9d74e5fbb14b4d0b5b5339506d5774df9a0dd3/Data')
    return df

df_full = get_data()

if df_full.empty:
    st.error("Data tidak ditemukan! Pastikan file CSV tersedia di folder Data.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;'>
        <h3 style='margin:0'>🐔 AGRI-INTEL</h3>
        <p style='color: #86AF99; font-size: 10px; margin:0; font-weight:700;'>POULTRY MARKET TRACKER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Pengaturan Analisis")
    
    # Rentang Tanggal
    min_date = df_full['Tanggal'].min().date()
    max_date = df_full['Tanggal'].max().date()
    
    date_range = st.date_input(
        "Rentang Waktu",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Ambang Batas Waspada
    threshold = st.slider("Ambang Batas Waspada (Rp)", 25000, 65000, 40000)
    
    # Filter Wilayah
    all_regions = sorted(df_full['Wilayah'].unique())
    selected_regions = st.multiselect("Filter Wilayah", all_regions, default=['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Sumatera Utara', 'Bali'])
    
    st.markdown("---")
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()

# --- PEMROSESAN DATA FILTERED ---
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    mask = (df_full['Tanggal'] >= start) & (df_full['Tanggal'] <= end)
    df = df_full[mask].copy()
else:
    df = df_full.copy()

if selected_regions:
    df_filtered = df[df['Wilayah'].isin(selected_regions)]
else:
    df_filtered = df

# Status Dinamis
df['Status'] = df['Harga'].apply(lambda x: 'Waspada' if x > threshold else 'Stabil')

# --- HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div class='pulse'></div>
            <span style='color:var(--neutral); font-weight:700; font-size:12px; letter-spacing:1px;'>SISTEM INFORMASI PASAR</span>
        </div>
        <h1 style='color:var(--primary); font-weight:800; margin:0; font-size:2.2rem;'>Daging Ayam Ras</h1>
        <p style='color:var(--neutral); margin-top:5px;'>Laporan tren harga harian berbasis data SP2KP Kementerian Perdagangan.</p>
    </div>
    """, unsafe_allow_html=True)

# --- KARTU METRIK ---
m1, m2, m3, m4 = st.columns(4)

latest_date = df['Tanggal'].max()
df_latest = df[df['Tanggal'] == latest_date]
avg_now = df_latest['Harga'].mean()
avg_prev = df_latest['Prev_Harga'].mean()
delta = avg_now - avg_prev if pd.notna(avg_prev) else 0
delta_pct = (delta / avg_prev) * 100 if delta != 0 else 0

with m1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Rata-rata Terkini</div>
        <div class='card-value'>Rp {avg_now:,.0f}</div>
        <div class='{'delta-up' if delta > 0 else 'delta-down'}'>
            {'▲' if delta > 0 else '▼'} {abs(delta_pct):.1f}% vs Hari Sebelumnya
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    peak_row = df_latest.loc[df_latest['Harga'].idxmax()]
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Harga Tertinggi</div>
        <div class='card-value'>Rp {peak_row['Harga']:,.0f}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>📍 {peak_row['Wilayah']}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    count_waspada = len(df_latest[df_latest['Status'] == 'Waspada'])
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Wilayah Status Waspada</div>
        <div class='card-value' style='color:var(--danger);'>{count_waspada}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>Threshold: Rp {threshold:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    total_data = len(df)
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Total Data Poin</div>
        <div class='card-value'>{total_data:,}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>Sinkronisasi: {datetime.now().strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- VISUALISASI UTAMA ---
c1, c2 = st.columns([1.8, 1.2])

with c1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 📈 Grafik Tren Harga & Moving Average")
    
    df_trend = df.groupby('Tanggal')['Harga'].mean().reset_index()
    df_trend['MA7'] = df_trend['Harga'].rolling(window=7).mean()
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_trend['Tanggal'], y=df_trend['Harga'], name="Rerata Nasional", line=dict(color='#012D1D', width=3)))
    fig_line.add_trace(go.Scatter(x=df_trend['Tanggal'], y=df_trend['MA7'], name="Tren 7-Hari", line=dict(color='#EAB308', width=2, dash='dot')))
    
    # Tambahkan garis wilayah terpilih
    for reg in selected_regions:
        reg_data = df[df['Wilayah'] == reg]
        fig_line.add_trace(go.Scatter(x=reg_data['Tanggal'], y=reg_data['Harga'], name=reg, opacity=0.4, line=dict(width=1.5), visible='legendonly'))

    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), height=380,
        hovermode='x unified', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Sebaran Harga Nasional")
    
    fig_map = px.scatter_mapbox(
        df_latest, lat="Lat", lon="Lon", color="Harga", size="Harga",
        hover_name="Wilayah", color_continuous_scale="RdYlGn_r",
        size_max=15, zoom=3.8, mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=380)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- ANALISIS TAMBAHAN ---
c3, c4 = st.columns(2)

with c3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 📊 Perbandingan Harga Rata-rata per Wilayah")
    avg_reg = df_filtered.groupby('Wilayah')['Harga'].mean().sort_values(ascending=True).reset_index()
    fig_bar = px.bar(avg_reg, x='Harga', y='Wilayah', orientation='h', color='Harga', color_continuous_scale="Greens")
    fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 🌡️ Heatmap Intensitas Harga")
    # Batasi jumlah wilayah agar heatmap terbaca
    top_regs = df_filtered.groupby('Wilayah')['Harga'].mean().nlargest(15).index
    df_heat = df_filtered[df_filtered['Wilayah'].isin(top_regs)]
    pivot = df_heat.pivot_table(index='Wilayah', columns=df_heat['Tanggal'].dt.strftime('%d/%m'), values='Harga')
    fig_heat = px.imshow(pivot, color_continuous_scale="YlOrRd")
    fig_heat.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- TABEL RINCIAN ---
st.markdown("### 📋 Rincian Data Harian")

table_df = df_filtered.sort_values(['Tanggal', 'Harga'], ascending=[False, False]).head(50)
table_df['Tanggal_Str'] = table_df['Tanggal'].dt.strftime('%d %B %Y')

def style_status(val):
    if val == 'Waspada': return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
    return 'background-color: #DCFCE7; color: #166534; font-weight: bold;'

st.dataframe(
    table_df[['Tanggal_Str', 'Wilayah', 'Harga', 'Status']].style
    .applymap(style_status, subset=['Status'])
    .format({'Harga': 'Rp {:,.0f}'}),
    use_container_width=True,
    hide_index=True
)

# --- EKSPOR DATA ---
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Unduh Laporan Lengkap (CSV)",
    csv,
    f"laporan_harga_ayam_{datetime.now().strftime('%Y%m%d')}.csv",
    "text/csv",
    use_container_width=True
)

st.markdown("""
<div style='text-align: center; color: #94A3B8; font-size: 11px; margin-top: 50px; padding: 20px;'>
    Market Intelligence Dashboard v2.5 Pro • Diperbarui Secara Otomatis • © 2026 Agrarian Intelligence Corp.
</div>
""", unsafe_allow_html=True)
