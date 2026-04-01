import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Import library untuk Analisis Lanjutan (Pastikan sudah di-install)
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & CSS MINIMALIS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AgriPulse | Analisis Lanjutan Ayam Ras", page_icon="🐔", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #0D1117; --surface: #161B22; --border: #2A3142;
    --accent: #3DD68C; --text: #E6EDF3; --textsoft: #9BAABD;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; color: var(--text) !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 2rem 3rem !important; }
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
.metric-box {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.25rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.metric-title { font-size: 11px; color: var(--textsoft); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; font-weight: 600; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: var(--text); font-family: 'DM Sans', sans-serif; line-height: 1.2; display: flex; align-items: baseline; gap: 8px;}
.metric-sub { font-size: 12px; color: var(--accent); margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.metric-sub.danger { color: #F87171; }
.metric-delta { font-size: 14px; font-weight: 600; padding: 2px 8px; border-radius: 12px; }
.delta-up { background: rgba(248,113,113,0.15); color: #F87171; }
.delta-down { background: rgba(61,214,140,0.15); color: #3DD68C; }
.live-dot {
    display: inline-block; width: 8px; height: 8px; background: var(--accent);
    border-radius: 50%; animation: livepulse 2s infinite; margin-right: 8px;
}
@keyframes livepulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(61,214,140,0.4); }
    50% { opacity: 0.5; box-shadow: 0 0 0 6px rgba(61,214,140,0); }
}
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px; padding: 4px; border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { color: var(--textsoft) !important; border-radius: 7px !important; font-size: 13px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: rgba(61,214,140,.15) !important; color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PEMETAAN PULAU LENGKAP (38 PROVINSI)
# ─────────────────────────────────────────────────────────────────────────────
PULAU_MAP = {
    'Sumatera': ['Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Kepulauan Riau', 'Jambi', 'Sumatera Selatan', 'Bangka Belitung', 'Bengkulu', 'Lampung'],
    'Jawa': ['Banten', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur'],
    'Bali & Nusa Tenggara': ['Bali', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur'],
    'Kalimantan': ['Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara'],
    'Sulawesi': ['Sulawesi Utara', 'Gorontalo', 'Sulawesi Tengah', 'Sulawesi Barat', 'Sulawesi Selatan', 'Sulawesi Tenggara'],
    'Maluku & Papua': ['Maluku Utara', 'Maluku', 'Papua Barat Daya', 'Papua Barat', 'Papua Tengah', 'Papua', 'Papua Pegunungan', 'Papua Selatan']
}

KOORDINAT = {
    'DKI Jakarta':(-6.2088,106.8456),'Jawa Barat':(-6.9175,107.6191),'Jawa Tengah':(-7.1506,110.1403),'Jawa Timur':(-7.2575,112.7521),'Banten':(-6.4058,106.064),'DI Yogyakarta':(-7.7956,110.3695),
    'Bali':(-8.4095,115.1889),'Sumatera Utara':(3.5952,98.6722),'Sumatera Barat':(-0.9471,100.4172),'Sumatera Selatan':(-3.3194,103.914),'Riau':(0.2933,101.7068),'Kepulauan Riau':(3.9456,108.1429),'Jambi':(-1.6101,103.6131),'Bengkulu':(-3.7928,102.2608),'Lampung':(-5.4292,105.2619),'Bangka Belitung':(-2.7411,106.4406),'Aceh':(4.6951,96.7494),
    'Kalimantan Barat':(-0.2788,111.4752),'Kalimantan Tengah':(-1.6815,113.3824),'Kalimantan Selatan':(-3.0926,115.2838),'Kalimantan Timur':(-0.5022,116.4194),'Kalimantan Utara':(3.0731,116.0419),
    'Sulawesi Utara':(1.4748,124.8421),'Sulawesi Tengah':(-1.43,121.4456),'Sulawesi Selatan':(-5.1477,119.4327),'Sulawesi Tenggara':(-4.1449,122.1746),'Gorontalo':(0.6999,122.4467),'Sulawesi Barat':(-2.8441,119.232),
    'Maluku':(-3.2384,130.1453),'Maluku Utara':(1.5709,127.8087),'Papua':(-4.2699,138.0804),'Papua Barat':(-1.3361,133.1747),'Papua Pegunungan':(-4.0817,138.5167),'Papua Selatan':(-5.7096,140.3889),'Papua Tengah':(-3.5,136.0),'Papua Barat Daya':(-1.8,132.0),
    'Nusa Tenggara Barat':(-8.6529,117.3616),'Nusa Tenggara Timur':(-8.6573,121.0794),
}

def get_pulau(prov):
    for pulau, provs in PULAU_MAP.items():
        if prov in provs: return pulau
    return 'Lainnya'

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    base = "."
    files = [os.path.join(r, f) for r, d, fs in os.walk(base) for f in fs if f.endswith(('.csv', '.xlsx')) and not f.startswith('~$') and 'node_modules' not in r]
    all_data = []

    for fpath in files:
        try:
            if fpath.endswith('.csv'):
                with open(fpath,'r', encoding='utf-8', errors='ignore') as fh: lines = fh.readlines()
                hidx = next((i for i,l in enumerate(lines[:30]) if 'wilayah' in l.lower()), -1)
                df = pd.read_csv(fpath, skiprows=hidx, dtype=str)
            else:
                xls = pd.ExcelFile(fpath)
                for sheet in xls.sheet_names:
                    raw = pd.read_excel(fpath, sheet_name=sheet, header=None, dtype=str)
                    hidx = next((i for i in range(min(30,len(raw))) if 'wilayah' in ' '.join(str(v) for v in raw.iloc[i].values).lower()), -1)
                    if hidx != -1:
                        raw.columns = raw.iloc[hidx].astype(str).tolist()
                        df = raw.iloc[hidx+1:].copy()
                        break

            wcol = next((c for c in df.columns if 'wilayah' in str(c).lower()), None)
            df = df.rename(columns={wcol:'Wilayah'}).dropna(subset=['Wilayah'])
            df = df[~df['Wilayah'].astype(str).str.contains(r'Sumber|Laporan|Periode|Catatan|nan', case=False, na=False)]
            
            date_cols = [c for c in df.columns if c != 'Wilayah']
            melted = pd.melt(df, id_vars=['Wilayah'], value_vars=date_cols, var_name='Tanggal', value_name='Harga')
            melted['Tanggal'] = pd.to_datetime(melted['Tanggal'], errors='coerce')
            melted['Harga'] = pd.to_numeric(melted['Harga'].astype(str).str.replace(r'[^\d.]','',regex=True), errors='coerce')
            melted = melted.dropna(subset=['Tanggal','Harga'])
            if not melted.empty: all_data.append(melted[melted['Harga'] > 1000])
        except: continue

    if not all_data: return pd.DataFrame()
    combined = pd.concat(all_data, ignore_index=True).drop_duplicates(subset=['Wilayah','Tanggal'])
    combined = combined.sort_values(['Wilayah','Tanggal']).reset_index(drop=True)
    combined['Pulau'] = combined['Wilayah'].apply(get_pulau)
    combined['Lat'] = combined['Wilayah'].map(lambda w: KOORDINAT.get(w, (None, None))[0])
    combined['Lon'] = combined['Wilayah'].map(lambda w: KOORDINAT.get(w, (None, None))[1])
    return combined

df_full = load_all_data()
if df_full.empty:
    st.error("Data tidak ditemukan atau kosong."); st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & FILTER
# ─────────────────────────────────────────────────────────────────────────────
latest_date = df_full['Tanggal'].max()
st.markdown(f"""
    <div style='margin-bottom: 1.5rem;'>
        <div style='font-size:12px; color:#3DD68C; letter-spacing:2px; text-transform:uppercase; font-weight:700;'>
            <span class='live-dot'></span>AgriPulse Market Intelligence
        </div>
        <h1 style='font-size:2.8rem; margin:0;'>Analisis Lanjutan: Daging Ayam Ras</h1>
        <p style='color:#9BAABD; font-size:1rem; margin-top:4px;'>Update Terakhir: {latest_date.strftime('%d %B %Y')} | Data Mencakup 38 Provinsi di Indonesia</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    rentang = st.selectbox("📅 Rentang Waktu", ["Semua Data", "1 Tahun Terakhir", "6 Bulan Terakhir", "3 Bulan Terakhir"])
    days = {"3 Bulan Terakhir": 90, "6 Bulan Terakhir": 180, "1 Tahun Terakhir": 365, "Semua Data": None}[rentang]
    d_start = df_full['Tanggal'].min() if days is None else max(latest_date - pd.Timedelta(days=days), df_full['Tanggal'].min())
    df_view = df_full[(df_full['Tanggal'] >= d_start) & (df_full['Tanggal'] <= latest_date)]

with col2:
    compare_mode = st.radio("🔍 Mode Analisis", ["Per Provinsi", "Per Pulau"], horizontal=True)

with col3:
    if compare_mode == "Per Provinsi":
        all_regions = sorted(df_full['Wilayah'].unique())
        default_regs = [r for r in ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Sumatera Utara'] if r in all_regions]
        selected_regs = st.multiselect("🌏 Bandingkan Provinsi", all_regions, default=default_regs)
    else:
        all_islands = sorted(df_full['Pulau'].unique())
        all_islands = [i for i in all_islands if i != 'Lainnya']
        default_islands = [i for i in ['Jawa', 'Sumatera', 'Kalimantan'] if i in all_islands]
        selected_regs = st.multiselect("🏝️ Bandingkan Pulau", all_islands, default=default_islands)

# ─────────────────────────────────────────────────────────────────────────────
# TEMA PLOTLY KUSTOM
# ─────────────────────────────────────────────────────────────────────────────
def apply_beautiful_layout(fig, title):
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#E6EDF3')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#9BAABD'),
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode='x unified',
        # Orientasi Legend di kanan agar grafik TIDAK JOMPLANG/tertekan ke bawah
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
        xaxis=dict(showgrid=False, gridcolor='#2A3142', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2A3142', zeroline=False, tickformat=",.0f")
    )
    return fig

PALETTE = ['#F0B429', '#60A5FA', '#F472B6', '#A78BFA', '#FB923C', '#22D3EE', '#4ADE80', '#FCD34D']

# ─────────────────────────────────────────────────────────────────────────────
# TABS UNTUK 5 ANALISIS LANJUTAN
# ─────────────────────────────────────────────────────────────────────────────
tab_utama, tab_dekomposisi, tab_volatilitas, tab_klaster, tab_anomali, tab_spasial = st.tabs([
    "📊 Ringkasan Utama",
    "1️⃣ Dekomposisi Musiman",
    "4️⃣ Volatilitas & GARCH",
    "7️⃣ Klasterisasi Pasar",
    "🔟 Deteksi Anomali",
    "12️⃣ Spasial & Korelasi"
])

# =============================================================================
# TAB 0: RINGKASAN UTAMA
# =============================================================================
with tab_utama:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    nat_avg = df_view.groupby('Tanggal')['Harga'].mean()
    fig1 = go.Figure()
    y_mins, y_maxs = [nat_avg.min()], [nat_avg.max()]

    fig1.add_trace(go.Scatter(x=nat_avg.index, y=nat_avg.values, name='🇮 Nasional (Rata-rata)', fill='tozeroy', fillcolor='rgba(61,214,140,0.1)', line=dict(color='#3DD68C', width=3), hovertemplate='<b>Nasional</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'))

    if compare_mode == "Per Provinsi":
        for i, reg in enumerate(selected_regs):
            df_plot = df_view[df_view['Wilayah'] == reg].sort_values('Tanggal')
            if not df_plot.empty:
                y_mins.append(df_plot['Harga'].min()); y_maxs.append(df_plot['Harga'].max())
                fig1.add_trace(go.Scatter(x=df_plot['Tanggal'], y=df_plot['Harga'], name=reg, line=dict(color=PALETTE[i % len(PALETTE)], width=1.5), hovertemplate=f'<b>{reg}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))
    else:
        for i, pulau in enumerate(selected_regs):
            df_plot = df_view[df_view['Pulau'] == pulau].groupby('Tanggal')['Harga'].mean().reset_index()
            if not df_plot.empty:
                y_mins.append(df_plot['Harga'].min()); y_maxs.append(df_plot['Harga'].max())
                fig1.add_trace(go.Scatter(x=df_plot['Tanggal'], y=df_plot['Harga'], name=f"🏝️ {pulau}", line=dict(color=PALETTE[i % len(PALETTE)], width=2), hovertemplate=f'<b>Pulau {pulau}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))

    fig1 = apply_beautiful_layout(fig1, f"📈 Pergerakan Harga Sepanjang Waktu ({compare_mode})")
    
    # Fokus zoom Y-axis
    y_min_total, y_max_total = min(y_mins), max(y_maxs)
    padding = (y_max_total - y_min_total) * 0.05
    if padding == 0: padding = y_min_total * 0.05
    fig1.update_layout(height=500) 
    fig1.update_yaxes(range=[y_min_total - padding, y_max_total + padding])

    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 1: DEKOMPOSISI MUSIMAN
# =============================================================================
with tab_dekomposisi:
    st.markdown("### 1. Analisis Dekomposisi Musiman (Seasonal Decomposition)")
    st.write("**Tujuan:** Memisahkan data time series harga menjadi tiga komponen: Trend (pergerakan jangka panjang), Seasonal (pola berulang), dan Residual (komponen acak).")
    
    if HAS_STATSMODELS:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        # Resample ke mingguan untuk dekomposisi yang lebih mulus
        df_nat_weekly = df_view.groupby('Tanggal')['Harga'].mean().resample('W').mean().fillna(method='ffill')
        
        if len(df_nat_weekly) > 10:
            # Menggunakan periode 4 (sekitar 1 bulan) karena data mingguan
            result = seasonal_decompose(df_nat_weekly, model='multiplicative', period=4)
            
            fig_decomp = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                                       subplot_titles=("Harga Asli (Mingguan)", "Trend (Fundamental)", "Musiman (Seasonal)", "Residual (Acak)"),
                                       vertical_spacing=0.05)
            
            fig_decomp.add_trace(go.Scatter(x=result.observed.index, y=result.observed, line=dict(color='#3DD68C')), row=1, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.trend.index, y=result.trend, line=dict(color='#F0B429')), row=2, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, line=dict(color='#60A5FA')), row=3, col=1)
            fig_decomp.add_trace(go.Bar(x=result.resid.index, y=result.resid, marker_color='#F87171'), row=4, col=1)
            
            fig_decomp.update_layout(height=700, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9BAABD'))
            fig_decomp.update_xaxes(showgrid=False, gridcolor='#2A3142')
            fig_decomp.update_yaxes(showgrid=True, gridcolor='#2A3142')
            st.plotly_chart(fig_decomp, use_container_width=True)
        else:
            st.warning("Data tidak cukup panjang untuk melakukan dekomposisi musiman. Perlebar rentang waktu.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Library `statsmodels` tidak terinstal di environment ini.")

# =============================================================================
# TAB 2: VOLATILITAS (PROXY GARCH)
# =============================================================================
with tab_volatilitas:
    st.markdown("### 4. Analisis Volatilitas (GARCH / EWMA Proxy)")
    st.write("**Tujuan:** Memodelkan varians yang berubah-ubah seiring waktu. Di sini kita menggunakan *Exponentially Weighted Moving Average* (EWMA) volatilitas harian (pendekatan *RiskMetrics* yang setara dengan model IGARCH) untuk mengukur risiko fluktuasi harga secara dinamis.")
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    nat_daily = df_view.groupby('Tanggal')['Harga'].mean()
    
    # Menghitung Return Harian (Log Return)
    log_returns = np.log(nat_daily / nat_daily.shift(1)).dropna()
    
    # Menghitung Volatilitas bersyarat menggunakan EWMA (span=21 hari kerja)
    # Dikalikan sqrt(365) untuk annualized volatility, dikali 100 untuk persentase
    conditional_volatility = log_returns.ewm(span=21).std() * np.sqrt(365) * 100
    
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=conditional_volatility.index, y=conditional_volatility.values,
        fill='tozeroy', fillcolor='rgba(248, 113, 113, 0.1)',
        line=dict(color='#F87171', width=2),
        name='Volatilitas Bersyarat (%)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Volatilitas: %{y:.2f}%<extra></extra>'
    ))
    
    fig_vol = apply_beautiful_layout(fig_vol, "🌪️ Tingkat Volatilitas Harga Berjalan (Annualized %)")
    fig_vol.update_layout(height=450, yaxis=dict(title="Volatilitas (%)", ticksuffix="%"))
    st.plotly_chart(fig_vol, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 3: KLASTERISASI PASAR (K-MEANS)
# =============================================================================
with tab_klaster:
    st.markdown("### 7. Klasterisasi Pola Harga Antar Wilayah (Clustering)")
    st.write("**Tujuan:** Mengelompokkan daerah/kota berdasarkan kemiripan pola pergerakan harga untuk memahami integrasi pasar.")
    
    if HAS_SKLEARN:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Pivot Data: Baris = Tanggal, Kolom = Wilayah
        pivot_df = df_view.pivot_table(index='Tanggal', columns='Wilayah', values='Harga')
        pivot_df = pivot_df.fillna(method='ffill').fillna(method='bfill') # Isi data kosong
        
        # Hapus provinsi yang masih punya NaN murni
        pivot_df = pivot_df.dropna(axis=1)
        
        if pivot_df.shape[1] >= 3:
            # Standarisasi data agar fokus pada POLA BENTUK (DTW-like effect), bukan skala harga
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(pivot_df.T) 
            
            # KMeans Clustering
            n_clusters = 3
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_data)
            
            cluster_map = pd.DataFrame({'Wilayah': pivot_df.columns, 'Cluster': clusters})
            
            col_k1, col_k2 = st.columns([2, 1])
            
            with col_k1:
                # Plot rata-rata pergerakan harga asli per klaster
                fig_km = go.Figure()
                cluster_colors = ['#3DD68C', '#F0B429', '#60A5FA']
                for c in range(n_clusters):
                    provinces_in_cluster = cluster_map[cluster_map['Cluster'] == c]['Wilayah'].tolist()
                    cluster_avg_price = pivot_df[provinces_in_cluster].mean(axis=1)
                    
                    fig_km.add_trace(go.Scatter(
                        x=cluster_avg_price.index, y=cluster_avg_price.values,
                        name=f'Cluster {c+1} ({len(provinces_in_cluster)} Prov)',
                        line=dict(color=cluster_colors[c], width=2)
                    ))
                
                fig_km = apply_beautiful_layout(fig_km, "Rata-rata Harga Aktual per Klaster")
                fig_km.update_layout(height=450)
                st.plotly_chart(fig_km, use_container_width=True)
            
            with col_k2:
                st.markdown("#### Anggota Klaster")
                for c in range(n_clusters):
                    provs = cluster_map[cluster_map['Cluster'] == c]['Wilayah'].tolist()
                    st.markdown(f"**<span style='color:{cluster_colors[c]}'>Cluster {c+1}</span>**", unsafe_allow_html=True)
                    st.caption(", ".join(provs))
                    st.markdown("---")
        else:
            st.warning("Data tidak cukup untuk klasterisasi.")
            
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Library `scikit-learn` tidak terinstal di environment ini.")

# =============================================================================
# TAB 4: DETEKSI ANOMALI
# =============================================================================
with tab_anomali:
    st.markdown("### 10. Deteksi Anomali (Anomaly Detection)")
    st.write("**Tujuan:** Menemukan titik-titik harga yang menyimpang signifikan dari pola normal akibat spekulasi, wabah, atau kebijakan mendadak menggunakan *Rolling Z-Score*.")
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    nat_avg = df_view.groupby('Tanggal')['Harga'].mean()
    
    # Hitung Z-Score Dinamis
    window = 30
    rolling_mean = nat_avg.rolling(window=window, min_periods=5).mean()
    rolling_std = nat_avg.rolling(window=window, min_periods=5).std()
    z_scores = (nat_avg - rolling_mean) / rolling_std
    
    # Tentukan Threshold Anomali
    threshold = 2.5
    anomalies = nat_avg[z_scores.abs() > threshold]
    
    fig_anom = go.Figure()
    fig_anom.add_trace(go.Scatter(x=nat_avg.index, y=nat_avg.values, name='Harga Normal', line=dict(color='#60A5FA', width=2)))
    fig_anom.add_trace(go.Scatter(x=rolling_mean.index, y=rolling_mean.values, name='Moving Avg (30 Hari)', line=dict(color='#9BAABD', width=1, dash='dash')))
    
    # Plot Titik Anomali
    fig_anom.add_trace(go.Scatter(
        x=anomalies.index, y=anomalies.values, mode='markers', name='Titik Anomali',
        marker=dict(color='#F87171', size=10, symbol='x-open', line=dict(width=2, color='#F87171')),
        hovertemplate='<b>ANOMALI</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'
    ))
    
    fig_anom = apply_beautiful_layout(fig_anom, "Titik Anomali Harga Nasional")
    fig_anom.update_layout(height=450)
    st.plotly_chart(fig_anom, use_container_width=True)
    
    if not anomalies.empty:
        st.error(f"⚠️ Terdeteksi {len(anomalies)} kejadian anomali (lonjakan/penurunan ekstrem) selama periode ini.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 5: SPASIAL & KORELASI ANTAR WILAYAH
# =============================================================================
with tab_spasial:
    st.markdown("### 12. Analisis Spasial dan Korelasi Antar Wilayah")
    st.write("**Tujuan:** Memahami hubungan harga antar lokasi secara geografis dan melihat sejauh mana pergerakan harga di satu wilayah memengaruhi wilayah lainnya (*spillover*).")
    
    col_s1, col_s2 = st.columns([1, 1])
    
    with col_s1:
        st.markdown("<div class='card' style='height:100%;'>", unsafe_allow_html=True)
        # Peta Spasial
        df_latest = df_view[df_view['Tanggal'] == df_view['Tanggal'].max()]
        if not df_latest.empty and 'Lat' in df_latest.columns:
            fig_map = px.scatter_mapbox(
                df_latest, lat="Lat", lon="Lon", color="Harga", size="Harga",
                hover_name="Wilayah", hover_data={"Harga":":,.0f", "Lat":False, "Lon":False},
                color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'],
                size_max=25, zoom=3.5, mapbox_style="carto-darkmatter"
            )
            fig_map.update_layout(height=450, margin=dict(l=0,r=0,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)', title=dict(text="Peta Sebaran Harga Terkini", font=dict(color='#E6EDF3')))
            st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("<div class='card' style='height:100%;'>", unsafe_allow_html=True)
        # Matriks Korelasi (Cross-Correlation Top 15 Regions)
        pivot = df_view.pivot_table(index='Tanggal', columns='Wilayah', values='Harga')
        top_provs = pivot.notna().sum().sort_values(ascending=False).head(15).index.tolist()
        corr_matrix = pivot[top_provs].corr()
        
        fig_corr = go.Figure(go.Heatmap(
            z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index,
            colorscale=[[0,'#EF4444'],[0.5,'#1C232D'],[1,'#3DD68C']], zmin=-1, zmax=1,
            colorbar=dict(title='Korelasi (r)', tickfont=dict(size=10))
        ))
        
        fig_corr.update_layout(
            title=dict(text="Heatmap Transmisi Harga (Top 15 Prov)", font=dict(size=18, color='#E6EDF3')),
            height=450, margin=dict(l=10,r=10,t=50,b=80),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#9BAABD')),
            yaxis=dict(tickfont=dict(size=10, color='#9BAABD'))
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
