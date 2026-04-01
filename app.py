import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Market Intelligence | Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (PREMIUM THEME) ---
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

    /* Hide Streamlit Header/Footer */
    header, footer { visibility: hidden; }
    
    .main { background-color: #F8FAFC; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #012D1D !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 { color: white !important; }

    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #F1F5F9;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-4px); }
    
    .card-label { font-size: 0.75rem; font-weight: 700; color: var(--neutral); text-transform: uppercase; letter-spacing: 0.05em; }
    .card-value { font-size: 1.75rem; font-weight: 800; color: var(--primary); margin: 0.25rem 0; }
    .card-delta { font-size: 0.75rem; font-weight: 600; }
    .delta-up { color: var(--danger); }
    .delta-down { color: var(--success); }

    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #F1F5F9;
        margin-bottom: 1.5rem;
    }

    /* Status Badges */
    .status-pill {
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .status-waspada { background: #FEE2E2; color: #991B1B; }
    .status-stabil { background: #DCFCE7; color: #166534; }

    /* Custom Button */
    .stButton>button {
        background: #1B4332;
        color: white;
        border-radius: 0.75rem;
        border: none;
        padding: 0.5rem 1rem;
        width: 100%;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover { background: #2D6A4F; border: none; color: white; }

    /* Live Pulse */
    .pulse {
        width: 10px;
        height: 10px;
        background: #16A34A;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 rgba(22, 163, 74, 0.4);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(22, 163, 74, 0); }
        100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- DATA GENERATION (MOCK SP2KP DATA) ---
@st.cache_data
def load_market_data():
    regions = {
        'DKI Jakarta': [-6.2088, 106.8456, 38000],
        'Jawa Barat': [-6.9175, 107.6191, 33000],
        'Jawa Timur': [-7.2575, 112.7521, 31000],
        'Banten': [-6.1200, 106.1503, 34000],
        'Papua': [-4.2699, 138.0804, 45000],
        'Sumatera Utara': [3.5952, 98.6722, 32000],
        'Sulawesi Selatan': [-5.1476, 119.4327, 29000],
        'Bali': [-8.4095, 115.1889, 36000]
    }
    
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=45, freq='D')
    
    rows = []
    for date in dates:
        for region, info in regions.items():
            base_price = info[2]
            # Simulate trend + randomness
            day_effect = np.sin(date.dayofyear / 5) * 1000
            price = base_price + day_effect + np.random.randint(-1500, 1500)
            
            rows.append({
                'Tanggal': date,
                'Wilayah': region,
                'Lat': info[0],
                'Lon': info[1],
                'Harga': round(price, -2)
            })
    
    df = pd.DataFrame(rows)
    # Calculate previous price for delta
    df = df.sort_values(['Wilayah', 'Tanggal'])
    df['Prev_Harga'] = df.groupby('Wilayah')['Harga'].shift(1)
    return df

df_full = load_market_data()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;'>
        <h3 style='margin:0'>🐔 AGRI-INTEL</h3>
        <p style='color: #86AF99; font-size: 10px; margin:0; font-weight:700;'>INDONESIA POULTRY TRACKER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Konfigurasi Analisis")
    
    # Date Range
    date_range = st.date_input(
        "Rentang Waktu",
        value=(df_full['Tanggal'].min().date(), df_full['Tanggal'].max().date()),
        min_value=df_full['Tanggal'].min().date(),
        max_value=df_full['Tanggal'].max().date()
    )
    
    # Threshold Slider
    threshold = st.slider("Ambang Batas Waspada (Rp)", 30000, 45000, 38000)
    
    # Region Filter
    all_regions = sorted(df_full['Wilayah'].unique())
    selected_regions = st.multiselect("Filter Wilayah", all_regions, default=all_regions[:5])
    
    st.markdown("---")
    if st.button("🔄 Perbarui Data"):
        st.cache_data.clear()
        st.rerun()

# --- DATA PROCESSING ---
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    mask = (df_full['Tanggal'] >= start) & (df_full['Tanggal'] <= end)
    df = df_full[mask].copy()
else:
    df = df_full.copy()

if selected_regions:
    df = df[df['Wilayah'].isin(selected_regions)]

# Add dynamic status
df['Status'] = df['Harga'].apply(lambda x: 'Waspada' if x > threshold else 'Stabil')

# --- HEADER SECTION ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div>
        <div style='display:flex; align-items:center; gap:10px;'>
            <div class='pulse'></div>
            <span style='color:var(--neutral); font-weight:700; font-size:12px; letter-spacing:1px;'>LIVE MARKET DATA</span>
        </div>
        <h1 style='color:var(--primary); font-weight:800; margin:0; font-size:2.5rem;'>Harga Daging Ayam Ras</h1>
        <p style='color:var(--neutral); margin-top:5px;'>Analisis real-time komoditas pangan nasional berbasis data SP2KP.</p>
    </div>
    """, unsafe_allow_html=True)

# --- METRIC CARDS ---
m1, m2, m3, m4 = st.columns(4)

# Calculations
avg_now = df[df['Tanggal'] == df['Tanggal'].max()]['Harga'].mean()
avg_prev = df[df['Tanggal'] == df['Tanggal'].max()]['Prev_Harga'].mean()
delta_pct = ((avg_now - avg_prev) / avg_prev) * 100

with m1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Rata-rata Nasional</div>
        <div class='card-value'>Rp {avg_now:,.0f}</div>
        <div class='card-delta {'delta-up' if delta_pct > 0 else 'delta-down'}'>
            {'▲' if delta_pct > 0 else '▼'} {abs(delta_pct):.1f}% (Daily)
        </div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    peak_region = df.loc[df['Harga'].idxmax()]
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Harga Tertinggi</div>
        <div class='card-value'>Rp {peak_region['Harga']:,.0f}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>📍 {peak_region['Wilayah']}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    count_waspada = len(df[(df['Tanggal'] == df['Tanggal'].max()) & (df['Status'] == 'Waspada')])
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Wilayah Status Waspada</div>
        <div class='card-value' style='color:var(--danger);'>{count_waspada}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>Ambang Batas: Rp {threshold:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    volatility = df.groupby('Tanggal')['Harga'].std().mean()
    st.markdown(f"""
    <div class='metric-card'>
        <div class='card-label'>Indeks Volatilitas</div>
        <div class='card-value'>{volatility/1000:.2f}</div>
        <div style='font-size:11px; color:var(--neutral); font-weight:600;'>Tingkat Fluktuasi Harga</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN VISUALS ---
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 📈 Tren Harga & Moving Average")
    
    fig_line = go.Figure()
    
    # Group by date for national average
    df_trend = df.groupby('Tanggal')['Harga'].mean().reset_index()
    df_trend['MA7'] = df_trend['Harga'].rolling(window=7).mean()
    
    fig_line.add_trace(go.Scatter(
        x=df_trend['Tanggal'], y=df_trend['Harga'],
        name="Rerata Nasional", line=dict(color='#012D1D', width=3)
    ))
    
    fig_line.add_trace(go.Scatter(
        x=df_trend['Tanggal'], y=df_trend['MA7'],
        name="Trend (7-Day MA)", line=dict(color='#EAB308', width=2, dash='dot')
    ))
    
    # Add individual regions as faint lines
    for region in selected_regions:
        reg_data = df[df['Wilayah'] == region]
        fig_line.add_trace(go.Scatter(
            x=reg_data['Tanggal'], y=reg_data['Harga'],
            name=region, opacity=0.3, line=dict(width=1),
            visible='legendonly'
        ))

    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0), height=400,
        hovermode='x unified', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_line.update_yaxes(gridcolor='#F1F5F9')
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 🗺️ Sebaran Spasial")
    
    # Latest data for map
    df_map = df[df['Tanggal'] == df['Tanggal'].max()]
    
    fig_map = px.scatter_mapbox(
        df_map, lat="Lat", lon="Lon", color="Harga", size="Harga",
        hover_name="Wilayah", color_continuous_scale="RdYlGn_r",
        size_max=15, zoom=3.5, mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=400, showlegend=False)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- SECONDARY VISUALS ---
c3, c4 = st.columns(2)

with c3:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 📊 Perbandingan Harga per Wilayah")
    avg_reg = df.groupby('Wilayah')['Harga'].mean().sort_values(ascending=True).reset_index()
    fig_bar = px.bar(
        avg_reg, x='Harga', y='Wilayah', orientation='h',
        color='Harga', color_continuous_scale="Greens"
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0), height=300, showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### 🌡️ Heatmap Intensitas Harga")
    pivot = df.pivot_table(index='Wilayah', columns=df['Tanggal'].dt.strftime('%d %b'), values='Harga')
    fig_heat = px.imshow(pivot, color_continuous_scale="YlOrRd")
    fig_heat.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=300
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- DATA TABLE WITH CONDITIONAL FORMATTING ---
st.markdown("### 📋 Rincian Data Harian")

# Formatting for display
display_df = df.sort_values(['Tanggal', 'Harga'], ascending=[False, False]).head(20)

def style_status(val):
    if val == 'Waspada':
        return 'color: #991B1B; background-color: #FEE2E2; font-weight: bold;'
    return 'color: #166534; background-color: #DCFCE7; font-weight: bold;'

# Final processing for table
table_df = display_df[['Tanggal', 'Wilayah', 'Harga', 'Status']].copy()
table_df['Tanggal'] = table_df['Tanggal'].dt.strftime('%Y-%m-%d')

st.dataframe(
    table_df.style.applymap(style_status, subset=['Status'])
    .format({'Harga': 'Rp {:,.0f}'}),
    use_container_width=True,
    hide_index=True
)

# --- EXPORT ---
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Download Laporan Lengkap (CSV)",
    csv,
    "laporan_harga_ayam.csv",
    "text/csv",
    use_container_width=True
)

st.markdown("""
<div style='text-align: center; color: #94A3B8; font-size: 12px; margin-top: 50px; padding: 20px;'>
    Market Intelligence Dashboard v2.0 • Data diperbarui setiap 24 jam • © 2024 Agrarian Intelligence Corp.
</div>
""", unsafe_allow_html=True)
