import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Import library untuk Analisis Lanjutan
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
h1, h2, h3, h4 { font-family: 'DM Serif Display', serif !important; color: var(--text) !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 2rem 3rem !important; }
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
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
.desc-text { font-size: 13px; color: var(--textsoft); margin-bottom: 1rem; line-height: 1.5; }
.guide-box { background: rgba(96,165,250,0.05); border-left: 4px solid #60A5FA; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 13px; line-height: 1.6;}
.guide-box strong { color: #60A5FA; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PEMETAAN PULAU & KOORDINAT
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

# Fungsi untuk menghitung Shannon Entropy dari return harga
def calc_shannon_entropy(series, bins=10):
    returns = series.pct_change().dropna()
    if len(returns) == 0: return 0
    counts, _ = np.histogram(returns, bins=bins)
    probs = counts / sum(counts)
    probs = probs[probs > 0] # hindari log(0)
    return -np.sum(probs * np.log2(probs))

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
# HEADER & FILTER DINAMIS
# ─────────────────────────────────────────────────────────────────────────────
latest_date = df_full['Tanggal'].max()
st.markdown(f"""
    <div style='margin-bottom: 1.5rem;'>
        <div style='font-size:12px; color:#3DD68C; letter-spacing:2px; text-transform:uppercase; font-weight:700;'>
            <span class='live-dot'></span>AgriPulse Advanced Analytics
        </div>
        <h1 style='font-size:2.8rem; margin:0;'>Daging Ayam Ras</h1>
        <p style='color:#9BAABD; font-size:1rem; margin-top:4px;'>Update Terakhir: {latest_date.strftime('%d %B %Y')} | Data Mencakup 38 Provinsi</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    rentang = st.selectbox("📅 Rentang Waktu", ["Semua Data", "1 Tahun Terakhir", "6 Bulan Terakhir", "3 Bulan Terakhir"], index=0)
    days = {"3 Bulan Terakhir": 90, "6 Bulan Terakhir": 180, "1 Tahun Terakhir": 365, "Semua Data": None}[rentang]
    d_start = df_full['Tanggal'].min() if days is None else max(latest_date - pd.Timedelta(days=days), df_full['Tanggal'].min())
    df_view = df_full[(df_full['Tanggal'] >= d_start) & (df_full['Tanggal'] <= latest_date)]

with col2:
    compare_mode = st.radio("🔍 Mode Analisis", ["Per Provinsi", "Per Pulau"], horizontal=True)

with col3:
    if compare_mode == "Per Provinsi":
        all_regions = sorted(df_full['Wilayah'].unique())
        default_regs = [r for r in ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Sumatera Utara'] if r in all_regions]
        selected_regs = st.multiselect("🌏 Pilih Provinsi untuk Dianalisis", all_regions, default=default_regs)
    else:
        all_islands = sorted(df_full['Pulau'].unique())
        all_islands = [i for i in all_islands if i != 'Lainnya']
        default_islands = all_islands
        selected_regs = st.multiselect("🏝️ Pilih Pulau untuk Dianalisis", all_islands, default=default_islands)

# Persiapan Data Scope Berdasarkan Pilihan (Untuk kalkulasi dinamis)
plot_data = {}
if compare_mode == "Per Provinsi":
    df_scope = df_view[df_view['Wilayah'].isin(selected_regs)]
    entity_col = 'Wilayah'
    for reg in selected_regs:
        s = df_scope[df_scope['Wilayah'] == reg].groupby('Tanggal')['Harga'].mean()
        if not s.empty: plot_data[reg] = s
else:
    df_scope = df_view[df_view['Pulau'].isin(selected_regs)].groupby(['Tanggal', 'Pulau'])['Harga'].mean().reset_index()
    entity_col = 'Pulau'
    for pulau in selected_regs:
        s = df_scope[df_scope['Pulau'] == pulau].groupby('Tanggal')['Harga'].mean()
        if not s.empty: plot_data[pulau] = s

# Rata-rata Nasional selalu dihitung sebagai Baseline
nat_avg = df_view.groupby('Tanggal')['Harga'].mean()

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
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
        xaxis=dict(showgrid=False, gridcolor='#2A3142', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2A3142', zeroline=False, tickformat=",.0f")
    )
    return fig

PALETTE = ['#F0B429', '#60A5FA', '#F472B6', '#A78BFA', '#FB923C', '#22D3EE', '#4ADE80', '#FCD34D', '#E879F9', '#94A3B8']

# ─────────────────────────────────────────────────────────────────────────────
# TABS UNTUK SEMUA ANALISIS
# ─────────────────────────────────────────────────────────────────────────────
tab_utama, tab_disparitas, tab_dekomposisi, tab_volatilitas, tab_klaster, tab_anomali, tab_spasial, tab_entropi = st.tabs([
    "📈 Tren & Komparasi",
    "📐 Disparitas & Distribusi",
    "1️⃣ Dekomposisi Musiman",
    "4️⃣ Volatilitas & Risiko",
    "7️⃣ Klasterisasi Pasar",
    "🔟 Deteksi Anomali",
    "12️⃣ Spasial & Korelasi",
    "🧠 Kompleksitas (Entropi)"
])

# =============================================================================
# TAB 0: TREN & KOMPARASI
# =============================================================================
with tab_utama:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Visualisasi garis waktu pergerakan harga aktual daging ayam ras.<br>
            <strong>Tujuan:</strong> Memantau pergerakan, membandingkan tren antar wilayah, dan melihat posisi relatif suatu wilayah terhadap rata-rata Nasional.<br>
            <strong>Cara Baca:</strong> Sumbu horizontal menunjukkan waktu, sumbu vertikal menunjukkan harga dalam Rupiah. Area berwarna hijau muda adalah rata-rata Nasional.<br>
            <strong>Interpretasi:</strong> Jika garis suatu wilayah berada di atas area hijau, berarti wilayah tersebut mengalami harga di atas kewajaran nasional (relatif mahal). Tren menanjak mengindikasikan inflasi atau pengetatan pasokan.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    fig1 = go.Figure()
    y_mins, y_maxs = [nat_avg.min()], [nat_avg.max()]

    fig1.add_trace(go.Scatter(x=nat_avg.index, y=nat_avg.values, name='🇮 Nasional (Rata-rata)', fill='tozeroy', fillcolor='rgba(61,214,140,0.1)', line=dict(color='#3DD68C', width=3), hovertemplate='<b>Nasional</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'))

    for i, (name, series) in enumerate(plot_data.items()):
        y_mins.append(series.min()); y_maxs.append(series.max())
        prefix = "📍" if compare_mode == "Per Provinsi" else "🏝️"
        fig1.add_trace(go.Scatter(x=series.index, y=series.values, name=f"{prefix} {name}", line=dict(color=PALETTE[i % len(PALETTE)], width=1.5), hovertemplate=f'<b>{name}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))

    fig1 = apply_beautiful_layout(fig1, f"Komparasi Pergerakan Harga ({compare_mode})")
    
    y_min_total, y_max_total = min(y_mins), max(y_maxs)
    padding = (y_max_total - y_min_total) * 0.05
    if padding == 0: padding = y_min_total * 0.05
    fig1.update_layout(height=500) 
    fig1.update_yaxes(range=[y_min_total - padding, y_max_total + padding])

    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 1: DISPARITAS & DISTRIBUSI
# =============================================================================
with tab_disparitas:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Pengukuran kesenjangan harga menggunakan nilai "Gap" (selisih Termahal - Termurah) dan "Indeks Gini".<br>
            <strong>Tujuan:</strong> Menilai seberapa merata harga di berbagai wilayah. Ketimpangan tinggi menandakan adanya kendala distribusi atau isolasi pasar.<br>
            <strong>Cara Baca:</strong> Grafik area (kuning) menunjukkan nilai Gap dalam Rupiah. Grafik bar (ungu) adalah Indeks Gini (skala 0 sampai 1).<br>
            <strong>Interpretasi:</strong> Gap yang terus membesar atau Indeks Gini yang tinggi (>0.3) mengindikasikan pasar yang tidak sehat karena perbedaan harga yang sangat ekstrim antar daerah.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if not df_scope.empty and len(selected_regs) >= 2:
        disp_daily = df_scope.groupby('Tanggal')['Harga'].agg(['max', 'min']).reset_index()
        disp_daily['Gap'] = disp_daily['max'] - disp_daily['min']
        
        def gini(arr):
            a = np.sort(np.abs(arr)); n = len(a)
            if n == 0 or a.mean() == 0: return 0
            return (2*np.sum(np.arange(1, n+1)*a) / (n*np.sum(a))) - (n+1)/n
            
        gini_daily = df_scope.groupby('Tanggal')['Harga'].apply(gini).reset_index()

        col_d1, col_d2 = st.columns([2, 1])
        
        with col_d1:
            fig_disp = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.65,0.35], vertical_spacing=0.06)
            fig_disp.add_trace(go.Scatter(x=disp_daily['Tanggal'], y=disp_daily['Gap'], name='Gap Harga (Max-Min)', fill='tozeroy', fillcolor='rgba(240, 180, 41, 0.1)', line=dict(color='#F0B429', width=2), hovertemplate='Gap Harga: Rp %{y:,.0f}<extra></extra>'), row=1, col=1)
            fig_disp.add_trace(go.Bar(x=gini_daily['Tanggal'], y=gini_daily['Harga'], name='Indeks Gini', marker_color='rgba(167,139,250,0.6)', hovertemplate='Gini: %{y:.4f}<extra></extra>'), row=2, col=1)
            
            fig_disp = apply_beautiful_layout(fig_disp, f"Tren Disparitas (Spesifik: {compare_mode.split(' ')[1]} Terpilih)")
            fig_disp.update_layout(height=450, showlegend=False, yaxis=dict(title="Gap Harga (Rp)", tickformat=",.0f"), yaxis2=dict(title="Indeks Gini"))
            st.plotly_chart(fig_disp, use_container_width=True, config={'displayModeBar': False})
            
        with col_d2:
            st.markdown("#### Peringkat Harga Hari Terakhir")
            df_scope_latest = df_scope[df_scope['Tanggal'] == df_scope['Tanggal'].max()].sort_values('Harga', ascending=True)
            
            fig_bar = px.bar(df_scope_latest, x='Harga', y=entity_col, orientation='h', color='Harga', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], text='Harga')
            fig_bar.update_traces(texttemplate='Rp %{text:,.0f}', textposition='outside', hovertemplate='<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>', marker_line_width=0)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=11, color='#9BAABD')), xaxis=dict(showticklabels=False, showgrid=False, title=""), margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info(f"Pilih minimal 2 {compare_mode.split(' ')[1].lower()} untuk menghitung disparitas.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 2: DEKOMPOSISI MUSIMAN
# =============================================================================
with tab_dekomposisi:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Model statistik yang membedah struktur time series menjadi tiga komponen terpisah menggunakan <i>Multiplicative Decomposition</i>.<br>
            <strong>Tujuan:</strong> Mengungkap tren mendasar tanpa gangguan fluktuasi harian, serta mendeteksi adanya siklus (musiman) pada komoditas ayam ras.<br>
            <strong>Cara Baca:</strong><br>
            1. <b>Trend:</b> Garis kuning, menunjukkan arah pergerakan murni jangka panjang.<br>
            2. <b>Musiman (Seasonal):</b> Gelombang biru, menunjukkan pola berulang (misal mingguan/bulanan).<br>
            3. <b>Residual:</b> Bar merah, menunjukkan kejadian acak (anomali) yang tidak bisa dijelaskan oleh tren maupun musim.<br>
            <strong>Interpretasi:</strong> Jika Trend naik tajam, terjadi inflasi sistemik. Jika Residual tiba-tiba menjulang tinggi, berarti terjadi kejutan pasar (misal: panik beli akibat isu tertentu).
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if HAS_STATSMODELS:
        default_target = selected_regs[0] if selected_regs else "Nasional"
        target_options = ["Nasional"] + list(plot_data.keys())
        target_decomp = st.selectbox("Pilih Target untuk Didekomposisi:", target_options, index=target_options.index(default_target) if default_target in target_options else 0)
        
        series_to_decomp = nat_avg if target_decomp == "Nasional" else plot_data[target_decomp]
        series_weekly = series_to_decomp.resample('W').mean().ffill()
        
        if len(series_weekly) > 10:
            result = seasonal_decompose(series_weekly, model='multiplicative', period=4)
            
            fig_decomp = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=(f"Harga Aktual ({target_decomp})", "Trend Fundamental", "Pola Musiman", "Residual (Acak)"), vertical_spacing=0.06)
            
            fig_decomp.add_trace(go.Scatter(x=result.observed.index, y=result.observed, line=dict(color='#3DD68C')), row=1, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.trend.index, y=result.trend, line=dict(color='#F0B429')), row=2, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, line=dict(color='#60A5FA')), row=3, col=1)
            fig_decomp.add_trace(go.Bar(x=result.resid.index, y=result.resid, marker_color='#F87171'), row=4, col=1)
            
            fig_decomp.update_layout(height=700, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9BAABD', family='DM Sans'))
            fig_decomp.update_xaxes(showgrid=False, gridcolor='#2A3142')
            fig_decomp.update_yaxes(showgrid=True, gridcolor='#2A3142')
            st.plotly_chart(fig_decomp, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Data tidak cukup panjang untuk dekomposisi. Silakan pilih 'Semua Data'.")
    else:
        st.error("Library `statsmodels` tidak terinstal.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 3: VOLATILITAS (GARCH / EWMA PROXY)
# =============================================================================
with tab_volatilitas:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Estimasi tingkat gejolak pasar dengan metode <i>Exponentially Weighted Moving Average (EWMA)</i> dari Log Return, yang disetahunkan (Annualized Volatility).<br>
            <strong>Tujuan:</strong> Mengukur risiko (<i>RiskMetrics</i>) akibat fluktuasi harga yang berubah-ubah secara ekstrem.<br>
            <strong>Cara Baca:</strong> Sumbu vertikal adalah persentase Volatilitas. Garis putus-putus hijau adalah <i>baseline</i> volatilitas Nasional.<br>
            <strong>Interpretasi:</strong> Lonjakan volatilitas menunjukkan pasar sedang dalam keadaan "panik" atau sangat tidak stabil. Wilayah dengan volatilitas yang konsisten tinggi berisiko merugikan peternak/konsumen akibat ketidakpastian. Peringkat di sebelah kanan (CV) menyoroti entitas paling berisiko secara keseluruhan.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v1:
        fig_vol = go.Figure()
        log_returns_nat = np.log(nat_avg / nat_avg.shift(1)).dropna()
        vol_nat = log_returns_nat.ewm(span=21).std() * np.sqrt(365) * 100
        fig_vol.add_trace(go.Scatter(x=vol_nat.index, y=vol_nat.values, name='Nasional', line=dict(color='#3DD68C', width=2, dash='dot'), hovertemplate='<b>Nasional</b><br>Volatilitas: %{y:.2f}%<extra></extra>'))

        for i, (name, series) in enumerate(plot_data.items()):
            log_returns = np.log(series / series.shift(1)).dropna()
            vol = log_returns.ewm(span=21).std() * np.sqrt(365) * 100
            fig_vol.add_trace(go.Scatter(x=vol.index, y=vol.values, name=name, line=dict(color=PALETTE[i%len(PALETTE)], width=1.5), hovertemplate=f'<b>{name}</b><br>Volatilitas: %{{y:.2f}}%<extra></extra>'))
        
        fig_vol = apply_beautiful_layout(fig_vol, "Tingkat Volatilitas Harga Dinamis (Annualized %)")
        fig_vol.update_layout(height=450, yaxis=dict(title="Tingkat Gejolak (%)", ticksuffix="%"))
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
        
    with col_v2:
        st.markdown("#### Peringkat Volatilitas (CV)")
        if not df_scope.empty:
            vol_data = df_scope.groupby(entity_col)['Harga'].apply(lambda x: x.std() / x.mean() * 100).reset_index()
            vol_data.columns = [entity_col, 'CV']
            vol_data = vol_data.sort_values('CV', ascending=True)
            
            fig_cv = px.bar(vol_data, x='CV', y=entity_col, orientation='h', color='CV', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], text='CV')
            fig_cv.update_traces(texttemplate='%{text:.1f}%', textposition='outside', hovertemplate='<b>%{y}</b><br>CV: %{x:.2f}%<extra></extra>', marker_line_width=0)
            fig_cv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=11, color='#9BAABD')), xaxis=dict(showticklabels=False, showgrid=False, title=""), margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_cv, use_container_width=True, config={'displayModeBar': False})
            
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 4: KLASTERISASI PASAR (K-MEANS)
# =============================================================================
with tab_klaster:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Model <i>Machine Learning (Unsupervised)</i> yang secara otomatis mengelompokkan wilayah berdasarkan kemiripan <b>POLA</b> fluktuasi harganya, bukan harga nominalnya.<br>
            <strong>Tujuan:</strong> Mencari daerah-daerah yang memiliki karakter pasar serupa atau terhubung erat dalam rantai pasok (meskipun lokasinya berjauhan).<br>
            <strong>Cara Baca:</strong> Grafik menampilkan pergerakan "Pusat Klaster" (centroid). Di sisi kanan, Anda dapat melihat wilayah mana saja yang masuk ke klaster tersebut. Wilayah yang Anda pilih di menu atas akan disorot <b>tebal</b>.<br>
            <strong>Interpretasi:</strong> Wilayah yang berada di klaster yang sama memiliki dinamika permintaan-penawaran yang sinkron. Kebijakan operasi pasar yang diterapkan pada satu anggota klaster biasanya akan berdampak serupa pada anggota lainnya di klaster yang sama.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if HAS_SKLEARN:
        entity_c = 'Wilayah' if compare_mode == "Per Provinsi" else 'Pulau'
        if compare_mode == "Per Pulau": pivot_df = df_view.groupby(['Tanggal', 'Pulau'])['Harga'].mean().reset_index().pivot_table(index='Tanggal', columns='Pulau', values='Harga')
        else: pivot_df = df_view.pivot_table(index='Tanggal', columns='Wilayah', values='Harga')
            
        pivot_df = pivot_df.ffill().bfill().dropna(axis=1)
        
        if pivot_df.shape[1] >= 3:
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(pivot_df.T) 
            n_clusters = max(2, min(3, pivot_df.shape[1] - 1))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_data)
            cluster_map = pd.DataFrame({'Entitas': pivot_df.columns, 'Cluster': clusters})
            
            col_k1, col_k2 = st.columns([5, 2])
            with col_k1:
                fig_km = go.Figure()
                cluster_colors = ['#3DD68C', '#F0B429', '#60A5FA']
                for c in range(n_clusters):
                    members = cluster_map[cluster_map['Cluster'] == c]['Entitas'].tolist()
                    cluster_avg_price = pivot_df[members].mean(axis=1)
                    
                    name_label = f"Cluster {c+1} ({len(members)} Anggota)"
                    fig_km.add_trace(go.Scatter(x=cluster_avg_price.index, y=cluster_avg_price.values, name=name_label, line=dict(color=cluster_colors[c], width=3), hovertemplate=f"<b>{name_label}</b><br>Rp %{{y:,.0f}}<extra></extra>"))
                
                fig_km = apply_beautiful_layout(fig_km, f"Karakteristik Pola Harga per Klaster")
                fig_km.update_layout(height=450)
                st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
            
            with col_k2:
                st.markdown("#### Keanggotaan Klaster")
                for c in range(n_clusters):
                    members = cluster_map[cluster_map['Cluster'] == c]['Entitas'].tolist()
                    st.markdown(f"**<span style='color:{cluster_colors[c]}'>Cluster {c+1}</span>**", unsafe_allow_html=True)
                    formatted_members = [f"<b>{m}</b>" if m in selected_regs else m for m in members]
                    st.markdown(", ".join(formatted_members), unsafe_allow_html=True)
                    st.markdown("<hr style='margin:0.5rem 0; border-color:#2A3142;'>", unsafe_allow_html=True)
        else: st.warning("Data entitas tidak cukup untuk membentuk klaster yang bermakna.")
    else: st.error("Library `scikit-learn` tidak terinstal.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 5: DETEKSI ANOMALI
# =============================================================================
with tab_anomali:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Model peringatan dini (<i>Early Warning System</i>) berbasis statistik Z-Score dengan <i>Rolling Window</i> 30 Hari.<br>
            <strong>Tujuan:</strong> Mendeteksi titik harga harian yang lompatannya (spike) atau anjlokannya tidak masuk akal dan berada di luar kewajaran deviasi standar.<br>
            <strong>Cara Baca:</strong> Garis tipis putus-putus adalah batas rata-rata kewajaran. Simbol <b>X warna merah</b> adalah titik waktu di mana harga dinyatakan sebagai "Anomali".<br>
            <strong>Interpretasi:</strong> Semakin banyak tanda merah di suatu wilayah, semakin rentan wilayah tersebut terhadap *market shock* (seperti gagal panen, kelangkaan stok dadakan, atau aksi spekulan/kartel).
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if not plot_data:
        st.info("Pilih wilayah/pulau terlebih dahulu.")
    else:
        fig_anom = go.Figure()
        anom_reports = []
        
        for i, (name, series) in enumerate(plot_data.items()):
            window = 30
            rolling_mean = series.rolling(window=window, min_periods=5).mean()
            rolling_std = series.rolling(window=window, min_periods=5).std()
            z_scores = (series - rolling_mean) / rolling_std
            
            threshold = 2.5
            anomalies = series[z_scores.abs() > threshold]
            
            line_color = PALETTE[i % len(PALETTE)]
            fig_anom.add_trace(go.Scatter(x=series.index, y=series.values, name=name, line=dict(color=line_color, width=1.5), opacity=0.7))
            
            if not anomalies.empty:
                fig_anom.add_trace(go.Scatter(x=anomalies.index, y=anomalies.values, mode='markers', name=f'Anomali {name}', marker=dict(color='#F87171', size=10, symbol='circle', line=dict(width=2, color=line_color)), hovertemplate=f'<b>ANOMALI: {name}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))
                anom_reports.append(f"**{name}**: {len(anomalies)} kejadian.")
        
        fig_anom = apply_beautiful_layout(fig_anom, f"Visualisasi Serentak Anomali Harga Ekstrem")
        fig_anom.update_layout(height=500)
        st.plotly_chart(fig_anom, use_container_width=True, config={'displayModeBar': False})
        
        if anom_reports: st.error("⚠️ **Ringkasan Temuan Anomali:**\n\n" + "\n".join([f"- {r}" for r in anom_reports]))
        else: st.success("✅ Seluruh wilayah/pulau terpilih bergerak normal sesuai batas kewajaran statistik selama periode ini.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 6: SPASIAL & KORELASI
# =============================================================================
with tab_spasial:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Pemetaan spasial dan perhitungan matriks Korelasi Pearson (r) yang mengukur kekuatan dan arah hubungan harga antar entitas.<br>
            <strong>Tujuan:</strong> Mengetahui apakah kenaikan harga di satu provinsi akan merembet (<i>spillover effect</i>) atau menular ke provinsi lainnya.<br>
            <strong>Cara Baca:</strong> Peta warna: Merah (Mahal) hingga Hijau (Murah). Heatmap: Nilai mendekati 1 (Hijau tua) berarti korelasi positif sempurna. Mendekati -1 (Merah tua) berarti korelasi negatif/berlawanan.<br>
            <strong>Interpretasi:</strong> Dua wilayah dengan korelasi tinggi (>0.8) menandakan kedua pasar sangat terintegrasi. Jika satu wilayah mengalami inflasi daging ayam, dapat diprediksi kuat wilayah pasangannya akan segera menyusul naik.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_s1, col_s2 = st.columns([1, 1])
    
    with col_s1:
        st.markdown("#### Peta Distribusi Geografis", unsafe_allow_html=True)
        df_latest = df_view[df_view['Tanggal'] == df_view['Tanggal'].max()]
        df_map = df_latest[df_latest['Wilayah'].isin(selected_regs)] if compare_mode == "Per Provinsi" else df_latest[df_latest['Pulau'].isin(selected_regs)]
            
        if not df_map.empty and 'Lat' in df_map.columns:
            fig_map = px.scatter_mapbox(df_map, lat="Lat", lon="Lon", color="Harga", size="Harga", hover_name="Wilayah", hover_data={"Harga":":,.0f", "Pulau":True, "Lat":False, "Lon":False}, color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], size_max=25, zoom=3.5, mapbox_style="carto-darkmatter")
            fig_map.update_layout(height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', coloraxis_colorbar=dict(title="Harga (Rp)", tickfont=dict(size=10)))
            st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        else: st.info("Data koordinat tidak ditemukan untuk visualisasi peta.")
            
    with col_s2:
        st.markdown(f"#### Matriks Transmisi (Korelasi Harga)", unsafe_allow_html=True)
        if len(plot_data) >= 2:
            corr_df = pd.DataFrame(plot_data)
            corr_matrix = corr_df.corr()
            
            fig_corr = go.Figure(go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index, colorscale=[[0,'#EF4444'],[0.5,'#1C232D'],[1,'#3DD68C']], zmin=-1, zmax=1, text=np.round(corr_matrix.values, 2), texttemplate="%{text}", textfont=dict(size=11), colorbar=dict(title='r', tickfont=dict(size=10)), hovertemplate="%{y} ↔ %{x}<br>Korelasi: %{z:.2f}<extra></extra>"))
            fig_corr.update_layout(height=450, margin=dict(l=10,r=10,t=10,b=50), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickangle=-45, tickfont=dict(size=11, color='#9BAABD')), yaxis=dict(tickfont=dict(size=11, color='#9BAABD')))
            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
        else: st.info(f"Pilih setidaknya 2 {compare_mode.split(' ')[1].lower()} untuk menghasilkan matriks korelasi.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 7: KOMPLEKSITAS (ENTROPI)
# =============================================================================
with tab_entropi:
    with st.expander("📖 Panduan & Interpretasi Analisis", expanded=False):
        st.markdown("""
        <div class='guide-box'>
            <strong>Apa itu:</strong> Model Teori Informasi (<i>Shannon Entropy</i>) yang diterapkan pada perubahan persentase harga harian (log returns).<br>
            <strong>Tujuan:</strong> Mengukur tingkat "Keacakan", "Kompleksitas", atau seberapa sulit memprediksi pergerakan harga komoditas.<br>
            <strong>Cara Baca:</strong> Nilai ditampilkan dalam satuan <i>bits</i>. Semakin panjang bar (nilai lebih tinggi), semakin tinggi kompleksitasnya.<br>
            <strong>Interpretasi:</strong> 
            <br>• <b>Entropi Tinggi:</b> Harga ayam bergerak sangat acak (menyebar rata), tidak membentuk pola statis, menandakan ketidakpastian (<i>uncertainty</i>) yang tinggi di pasar tersebut.
            <br>• <b>Entropi Rendah:</b> Harga bergerak sangat monoton atau terpusat pada angka perubahan yang itu-itu saja (sangat mudah diprediksi). Pasar lebih pasti atau mungkin mengalami <i>price stickiness</i> (kekakuan harga).
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if plot_data:
        entropy_results = []
        
        # Hitung entropi untuk baseline Nasional
        ent_nat = calc_shannon_entropy(nat_avg)
        entropy_results.append({'Entitas': 'Nasional', 'Entropi (bits)': ent_nat, 'Warna': '#3DD68C'})
        
        # Hitung entropi untuk entitas terpilih
        for i, (name, series) in enumerate(plot_data.items()):
            ent_val = calc_shannon_entropy(series)
            entropy_results.append({'Entitas': name, 'Entropi (bits)': ent_val, 'Warna': PALETTE[i % len(PALETTE)]})
            
        df_ent = pd.DataFrame(entropy_results).sort_values('Entropi (bits)', ascending=True)
        
        col_e1, col_e2 = st.columns([2, 1])
        
        with col_e1:
            fig_ent = px.bar(df_ent, x='Entropi (bits)', y='Entitas', orientation='h', color='Entitas', color_discrete_map=dict(zip(df_ent['Entitas'], df_ent['Warna'])), text='Entropi (bits)')
            fig_ent.update_traces(texttemplate='%{text:.3f} bits', textposition='outside', hovertemplate='<b>%{y}</b><br>Entropi: %{x:.3f} bits<extra></extra>', marker_line_width=0)
            
            fig_ent = apply_beautiful_layout(fig_ent, f"Tingkat Keacakan Pasar (Shannon Entropy)")
            fig_ent.update_layout(height=450, showlegend=False, xaxis=dict(title="Tingkat Kompleksitas (bits) ➔ Makin Tinggi Makin Acak"), yaxis=dict(title="", tickfont=dict(size=12)))
            
            st.plotly_chart(fig_ent, use_container_width=True, config={'displayModeBar': False})
            
        with col_e2:
            st.markdown("#### Wawasan Entropi")
            max_ent = df_ent.iloc[-1]
            min_ent = df_ent[df_ent['Entitas'] != 'Nasional'].iloc[0] if len(df_ent) > 1 else df_ent.iloc[0]
            
            st.info(f"**Paling Acak / Sulit Diprediksi:**\n\nPasar di **{max_ent['Entitas']}** memiliki entropi tertinggi ({max_ent['Entropi (bits)']:.3f} bits), menandakan rentang fluktuasi perubahan harga yang luas dan tidak berpola tetap.")
            st.success(f"**Paling Teratur / Kaku:**\n\nPasar di **{min_ent['Entitas']}** memiliki entropi terendah ({min_ent['Entropi (bits)']:.3f} bits), menandakan harga cenderung diam, kaku, atau bergerak dalam pola yang mudah ditebak.")
            
    else:
        st.info("Pilih wilayah/pulau terlebih dahulu untuk menganalisis entropi pasar.")
    st.markdown("</div>", unsafe_allow_html=True)
