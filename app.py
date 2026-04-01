import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import datetime

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
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px; padding: 4px; border: 1px solid var(--border); overflow-x: auto; }
.stTabs [data-baseweb="tab"] { color: var(--textsoft) !important; border-radius: 7px !important; font-size: 13px !important; font-weight: 600 !important; white-space: nowrap; }
.stTabs [aria-selected="true"] { background: rgba(61,214,140,.15) !important; color: var(--accent) !important; }
.desc-text { font-size: 13px; color: var(--textsoft); margin-bottom: 1rem; line-height: 1.5; }
.guide-box { background: rgba(96,165,250,0.05); border-left: 4px solid #60A5FA; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 13px; line-height: 1.6;}
.guide-box strong { color: #60A5FA; }
.guide-box ul { margin-top: 4px; margin-bottom: 4px; padding-left: 20px; }
.interpreter-box { background: rgba(61,214,140,0.05); border-left: 4px solid #3DD68C; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 13.5px; line-height: 1.6;}
.interpreter-box strong { color: #3DD68C; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI EVENT TETAP & DINAMIS (HARDCODED EST)
# ─────────────────────────────────────────────────────────────────────────────
EVENT_DATES = {
    'Awal Ramadan': {2023: '2023-03-23', 2024: '2024-03-12', 2025: '2025-03-01', 2026: '2026-02-18', 2027: '2027-02-08'},
    'Idul Fitri': {2023: '2023-04-22', 2024: '2024-04-10', 2025: '2025-03-31', 2026: '2026-03-20', 2027: '2027-03-10'},
    'Idul Adha': {2023: '2023-06-29', 2024: '2024-06-17', 2025: '2025-06-06', 2026: '2026-05-27', 2027: '2027-05-17'},
    'Tahun Baru Imlek': {2023: '2023-01-22', 2024: '2024-02-10', 2025: '2025-01-29', 2026: '2026-02-17', 2027: '2027-02-06'},
    'Hari Raya Nyepi': {2023: '2023-03-22', 2024: '2024-03-11', 2025: '2025-03-29', 2026: '2026-03-19', 2027: '2027-03-09'},
    'Hari Raya Waisak': {2023: '2023-06-04', 2024: '2024-05-23', 2025: '2025-05-12', 2026: '2026-05-31', 2027: '2027-05-20'},
    'Maulid Nabi': {2023: '2023-09-28', 2024: '2024-09-16', 2025: '2025-09-05', 2026: '2026-08-26', 2027: '2027-08-15'},
    'HUT RI': {2023: '2023-08-17', 2024: '2024-08-17', 2025: '2025-08-17', 2026: '2026-08-17', 2027: '2027-08-17'},
    'Hari Buruh': {2023: '2023-05-01', 2024: '2024-05-01', 2025: '2025-05-01', 2026: '2026-05-01', 2027: '2027-05-01'},
    'Natal': {2023: '2023-12-25', 2024: '2024-12-25', 2025: '2025-12-25', 2026: '2026-12-25', 2027: '2027-12-25'},
    'Tahun Baru': {2023: '2023-01-01', 2024: '2024-01-01', 2025: '2025-01-01', 2026: '2026-01-01', 2027: '2027-01-01'}
}

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

# Fungsi Kecepatan Mean Reversion (Half-Life menggunakan AR(1) via regresi linear)
def calc_half_life(series):
    s = series.dropna()
    if len(s) < 10: return np.nan
    y = s.values
    dy = np.diff(y)
    y_lag = y[:-1]
    try:
        slope, _ = np.polyfit(y_lag, dy, 1)
        if slope >= 0: return np.inf 
        hl = -np.log(2) / slope
        return hl if hl < 365 else np.inf
    except:
        return np.nan

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
        <p style='color:#9BAABD; font-size:1rem; margin-top:4px;'>Update Terakhir: {latest_date.strftime('%d %B %Y')} | 38 Provinsi | 10 Model Analisis</p>
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
        selected_regs = st.multiselect("🌏 Pilih Provinsi", all_regions, default=default_regs)
    else:
        all_islands = sorted(df_full['Pulau'].unique())
        all_islands = [i for i in all_islands if i != 'Lainnya']
        selected_regs = st.multiselect("🏝️ Pilih Pulau", all_islands, default=all_islands)

# Persiapan Data Scope Berdasarkan Pilihan
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
tab_utama, tab_disparitas, tab_dekomposisi, tab_volatilitas, tab_klaster, tab_anomali, tab_spasial, tab_entropi, tab_halflife, tab_preevent = st.tabs([
    "📈 Tren & Komparasi",
    "📐 Disparitas",
    "1️⃣ Dekomposisi",
    "4️⃣ Volatilitas",
    "7️⃣ Klasterisasi",
    "🔟 Anomali",
    "12️⃣ Spasial",
    "🧠 Entropi",
    "⏳ Mean Reversion",
    "📅 Efek Event"
])

# =============================================================================
# TAB 0: TREN & KOMPARASI
# =============================================================================
with tab_utama:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Memantau pergerakan harga dasar (<i>baseline</i>), membandingkan tren antar wilayah, dan melihat posisi relatif suatu wilayah terhadap rata-rata Nasional.<br>
        <strong>Metode:</strong> Visualisasi <i>Time-Series</i> komparatif dengan overlay agregat nasional (rata-rata selurus wilayah).<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Garis hijau dengan arsiran adalah rata-rata Nasional.</li>
            <li>Garis warna-warni mewakili entitas (Provinsi/Pulau) yang Anda pilih.</li>
            <li>Jika garis suatu wilayah berada secara konsisten di atas area hijau, wilayah tersebut memiliki struktur biaya/harga yang secara permanen lebih mahal dari kewajaran nasional.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

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
    fig1.update_layout(height=450) 
    fig1.update_yaxes(range=[y_min_total - padding if y_min_total > 0 else 0, y_max_total + padding])
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    if plot_data:
        latest_prices = {k: v.iloc[-1] for k, v in plot_data.items()}
        max_ent = max(latest_prices, key=latest_prices.get)
        min_ent = min(latest_prices, key=latest_prices.get)
        st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> Pada data terakhir ({latest_date.strftime('%d %b %Y')}), tingkat harga tertinggi di antara wilayah terpilih dipegang oleh <b>{max_ent}</b> (Rp {latest_prices[max_ent]:,.0f}), sedangkan harga termurah berada di <b>{min_ent}</b> (Rp {latest_prices[min_ent]:,.0f}).</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 1: DISPARITAS & DISTRIBUSI
# =============================================================================
with tab_disparitas:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Menilai seberapa merata atau timpangnya harga antar lokasi. Ketimpangan tinggi menandakan kendala distribusi logistik atau adanya hambatan isolasi pasar.<br>
        <strong>Metode:</strong> Kalkulasi <i>Price Gap</i> (Nilai Maksimum - Nilai Minimum) harian, dan <i>Gini Ratio</i> (mengukur distribusi ketidakmerataan).<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li><b>Grafik Area Kuning:</b> Selisih harga mutlak (dalam Rupiah). Jika membesar, berarti kesenjangan makin parah.</li>
            <li><b>Grafik Bar Ungu (Gini):</b> Nilai 0 berarti harga sama rata di semua tempat. Mendekati 1 berarti timpang.</li>
            <li>Nilai Gini > 0.3 biasanya menjadi peringatan dini bahwa intervensi operasi pasar lintas batas diperlukan.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

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
            fig_disp.add_trace(go.Scatter(x=disp_daily['Tanggal'], y=disp_daily['Gap'], name='Gap (Max-Min)', fill='tozeroy', fillcolor='rgba(240, 180, 41, 0.1)', line=dict(color='#F0B429', width=2), hovertemplate='Rp %{y:,.0f}<extra></extra>'), row=1, col=1)
            fig_disp.add_trace(go.Bar(x=gini_daily['Tanggal'], y=gini_daily['Harga'], name='Gini', marker_color='rgba(167,139,250,0.6)', hovertemplate='%{y:.4f}<extra></extra>'), row=2, col=1)
            fig_disp = apply_beautiful_layout(fig_disp, f"Tren Disparitas (Wilayah Terpilih)")
            fig_disp.update_layout(height=400, showlegend=False, yaxis=dict(title="Gap (Rp)"), yaxis2=dict(title="Gini"))
            st.plotly_chart(fig_disp, use_container_width=True, config={'displayModeBar': False})
            
        with col_d2:
            st.markdown("#### Peringkat Harga Terbaru")
            df_scope_latest = df_scope[df_scope['Tanggal'] == df_scope['Tanggal'].max()].sort_values('Harga', ascending=True)
            fig_bar = px.bar(df_scope_latest, x='Harga', y=entity_col, orientation='h', color='Harga', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], text='Harga')
            fig_bar.update_traces(texttemplate='Rp %{text:,.0f}', textposition='outside', marker_line_width=0)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=11, color='#9BAABD')), xaxis=dict(showticklabels=False, showgrid=False, title=""), margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            
        latest_gap = disp_daily.iloc[-1]['Gap']
        latest_gini = gini_daily.iloc[-1]['Harga']
        gini_status = "Relatif Merata" if latest_gini < 0.1 else "Moderat" if latest_gini < 0.2 else "Sangat Timpang"
        st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> Kesenjangan (gap) harga hari ini antara wilayah termahal dan termurah mencapai <b>Rp {latest_gap:,.0f}</b>. Indeks Gini sebesar <b>{latest_gini:.3f}</b> menandakan bahwa distribusi harga di pasar-pasar terpilih ini tergolong <b>{gini_status}</b>.</div>""", unsafe_allow_html=True)
    else: st.info(f"Pilih minimal 2 {compare_mode.split(' ')[1].lower()} untuk menghitung disparitas.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 2: DEKOMPOSISI MUSIMAN
# =============================================================================
with tab_dekomposisi:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengungkap struktur dasar atau "anatomi" dari sebuah data deret waktu harga daging ayam.<br>
        <strong>Metode:</strong> <i>Seasonal Decomposition of Time Series</i> menggunakan model <i>Multiplicative</i> pada data rata-rata mingguan.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li><b>Trend (Fundamental):</b> Garis yang menunjukkan arah jangka panjang murni, tanpa gangguan musim atau noise harian.</li>
            <li><b>Musiman (Seasonal):</b> Pola bukit-lembah berulang secara konsisten. Membantu melihat siklus harga mahal/murah rutin.</li>
            <li><b>Residual (Acak):</b> Bar grafik yang menunjukkan faktor 'kejutan' tak terduga yang tidak bisa dijelaskan oleh trend/musim (contoh: panic buying, bencana).</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if HAS_STATSMODELS:
        default_target = selected_regs[0] if selected_regs else "Nasional"
        target_options = ["Nasional"] + list(plot_data.keys())
        target_decomp = st.selectbox("Pilih Target untuk Didekomposisi:", target_options, index=target_options.index(default_target) if default_target in target_options else 0)
        
        series_to_decomp = nat_avg if target_decomp == "Nasional" else plot_data[target_decomp]
        series_weekly = series_to_decomp.resample('W').mean().ffill()
        
        if len(series_weekly) > 10:
            result = seasonal_decompose(series_weekly, model='multiplicative', period=4)
            fig_decomp = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=(f"Harga Aktual", "Trend Fundamental", "Pola Musiman", "Residual (Acak)"), vertical_spacing=0.06)
            fig_decomp.add_trace(go.Scatter(x=result.observed.index, y=result.observed, line=dict(color='#3DD68C')), row=1, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.trend.index, y=result.trend, line=dict(color='#F0B429')), row=2, col=1)
            fig_decomp.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, line=dict(color='#60A5FA')), row=3, col=1)
            fig_decomp.add_trace(go.Bar(x=result.resid.index, y=result.resid, marker_color='#F87171'), row=4, col=1)
            fig_decomp.update_layout(height=650, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9BAABD'))
            fig_decomp.update_xaxes(showgrid=False, gridcolor='#2A3142')
            fig_decomp.update_yaxes(showgrid=True, gridcolor='#2A3142')
            st.plotly_chart(fig_decomp, use_container_width=True, config={'displayModeBar': False})
            
            trend_s = result.trend.dropna()
            trend_dir = "mengalami tren Kenaikan" if trend_s.iloc[-1] > trend_s.iloc[0] else "mengalami tren Penurunan"
            st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> Secara fundamental jangka panjang (mengabaikan noise harian), <b>{target_decomp}</b> saat ini secara keseluruhan <b>{trend_dir}</b>. Jika grafik bar Residual (merah) di bawah tiba-tiba memanjang drastis di periode tertentu, itu menandakan terjadinya <i>market shock</i> (kejutan eksternal).</div>""", unsafe_allow_html=True)
        else: st.warning("Data tidak cukup panjang untuk dekomposisi. Pilih rentang waktu yang lebih lama.")
    else: st.error("Library `statsmodels` tidak terinstal.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 3: VOLATILITAS (GARCH / EWMA PROXY)
# =============================================================================
with tab_volatilitas:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengukur risiko fluktuasi harga harian yang disetahunkan (Annualized Volatility). Penting untuk menilai stabilitas dan kepastian pasar bagi peternak/pedagang.<br>
        <strong>Metode:</strong> Estimasi berbasis <i>Exponentially Weighted Moving Average (EWMA)</i> dari Log Return harga (sebagai proksi untuk varians bersyarat GARCH/RiskMetrics).<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Garis chart (kiri) melacak dinamika kepanikan/ketenangan pasar dari hari ke hari.</li>
            <li>Bar chart (kanan) mengurutkan rata-rata volatilitas secara agregat (<i>Coefficient of Variation</i>).</li>
            <li>Volatilitas yang menanjak naik berarti pasar sangat fluktuatif dan berisiko tinggi. Semakin kecil angkanya, pasar semakin aman dan pasti.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_v1, col_v2 = st.columns([2, 1])
    
    with col_v1:
        fig_vol = go.Figure()
        log_returns_nat = np.log(nat_avg / nat_avg.shift(1)).dropna()
        vol_nat = log_returns_nat.ewm(span=21).std() * np.sqrt(365) * 100
        fig_vol.add_trace(go.Scatter(x=vol_nat.index, y=vol_nat.values, name='Nasional', line=dict(color='#3DD68C', width=2, dash='dot'), hovertemplate='<b>Nasional</b><br>Volatilitas: %{y:.2f}%<extra></extra>'))

        latest_vols = {}
        for i, (name, series) in enumerate(plot_data.items()):
            log_returns = np.log(series / series.shift(1)).dropna()
            vol = log_returns.ewm(span=21).std() * np.sqrt(365) * 100
            latest_vols[name] = vol.iloc[-1]
            fig_vol.add_trace(go.Scatter(x=vol.index, y=vol.values, name=name, line=dict(color=PALETTE[i%len(PALETTE)], width=1.5), hovertemplate=f'<b>{name}</b><br>Volatilitas: %{{y:.2f}}%<extra></extra>'))
        
        fig_vol = apply_beautiful_layout(fig_vol, "Tingkat Volatilitas Dinamis (Annualized %)")
        fig_vol.update_layout(height=400, yaxis=dict(title="Tingkat Gejolak (%)", ticksuffix="%"))
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
        
    with col_v2:
        if not df_scope.empty:
            vol_data = df_scope.groupby(entity_col)['Harga'].apply(lambda x: x.std() / x.mean() * 100).reset_index()
            vol_data.columns = [entity_col, 'CV']
            vol_data = vol_data.sort_values('CV', ascending=True)
            fig_cv = px.bar(vol_data, x='CV', y=entity_col, orientation='h', color='CV', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], text='CV')
            fig_cv.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
            fig_cv.update_layout(title=dict(text="Peringkat Agregat (CV)", font=dict(size=14, color='#E6EDF3')), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=11, color='#9BAABD')), xaxis=dict(showticklabels=False, showgrid=False, title=""), margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig_cv, use_container_width=True, config={'displayModeBar': False})
    
    if latest_vols:
        max_vol_name = max(latest_vols, key=latest_vols.get)
        st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> Secara dinamis pada data teraktual, <b>{max_vol_name}</b> adalah wilayah dengan gejolak risiko tertinggi ({latest_vols[max_vol_name]:.2f}%). Harga di wilayah ini berubah-ubah secara liar sehingga mendatangkan risiko kerugian atau spekulasi yang lebih tinggi dibanding area lain.</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 4: KLASTERISASI PASAR (K-MEANS)
# =============================================================================
with tab_klaster:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengelompokkan daerah berdasarkan kemiripan pola pergerakan harganya. Berguna untuk efisiensi kebijakan operasi pasar dan distribusi logistik.<br>
        <strong>Metode:</strong> Algoritma <i>Machine Learning Unsupervised (K-Means Clustering)</i> pada data yang telah distandardisasi (Z-Score) agar fokus pada "Bentuk Pola", bukan pada nominal harga yang besar/kecil.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Algoritma mencari entitas mana saja yang senasib dan sepola, lalu memecahnya menjadi grup-grup.</li>
            <li>Entitas yang Anda pilih akan disorot <b>tebal</b> di daftar sebelah kanan.</li>
            <li>Jika 2 provinsi masuk di Klaster yang sama, maka jika provinsi A harga naik, kemungkinan besar provinsi B polanya juga merespon hal serupa karena pasokan mereka saling terhubung.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

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
                
                fig_km = apply_beautiful_layout(fig_km, f"Rata-rata Harga Aktual per Klaster (AI K-Means)")
                fig_km.update_layout(height=400)
                st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
            
            with col_k2:
                st.markdown("#### Keanggotaan Klaster")
                for c in range(n_clusters):
                    members = cluster_map[cluster_map['Cluster'] == c]['Entitas'].tolist()
                    st.markdown(f"**<span style='color:{cluster_colors[c]}'>Cluster {c+1}</span>**", unsafe_allow_html=True)
                    formatted_members = [f"<b>{m}</b>" if m in selected_regs else m for m in members]
                    st.markdown(", ".join(formatted_members), unsafe_allow_html=True)
                    st.markdown("<hr style='margin:0.5rem 0; border-color:#2A3142;'>", unsafe_allow_html=True)
            
            c_counts = cluster_map['Cluster'].value_counts()
            largest_c = c_counts.idxmax()
            st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> AI mengelompokkan karakteristik pasar menjadi <b>{n_clusters} Klaster</b> pola perilaku. Mayoritas entitas ({c_counts[largest_c]} entitas) tergabung dalam <b>Cluster {largest_c + 1}</b>, menjadikannya standar perilaku harga dominan di RI saat ini. Entitas yang berbeda klaster berarti memiliki fundamental penggerak harga (struktur rantai pasok) yang terisolasi atau independen satu sama lain.</div>""", unsafe_allow_html=True)
        else: st.warning("Data entitas tidak cukup untuk membentuk klaster.")
    else: st.error("Library `scikit-learn` tidak terinstal.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 5: DETEKSI ANOMALI
# =============================================================================
with tab_anomali:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mendeteksi titik-titik harga harian yang menyimpang di luar kewajaran. Sangat relevan untuk investigasi spekulasi, gangguan distribusi mendadak, atau keberhasilan intervensi OP (Operasi Pasar).<br>
        <strong>Metode:</strong> Statistik <i>Rolling Z-Score</i>. Harga dinyatakan anomali jika deviasinya melebihi 2.5 kali Standar Deviasi dari pergerakan normal 30 hari ke belakang.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Garis menunjukkan pergerakan harga normal. Tanda <b>titik X atau bulatan padat</b> menunjukkan tanggal terjadinya Anomali Harga.</li>
            <li>Jika banyak tanda anomali bertumpuk, ini menunjukkan pasar sedang dilanda kepanikan irasional atau <i>market failure</i> yang kuat.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if not plot_data: st.info("Pilih wilayah/pulau terlebih dahulu.")
    else:
        fig_anom = go.Figure()
        anom_counts = {}
        
        for i, (name, series) in enumerate(plot_data.items()):
            window = 30
            rolling_mean = series.rolling(window=window, min_periods=5).mean()
            rolling_std = series.rolling(window=window, min_periods=5).std()
            z_scores = (series - rolling_mean) / rolling_std
            anomalies = series[z_scores.abs() > 2.5]
            
            line_color = PALETTE[i % len(PALETTE)]
            fig_anom.add_trace(go.Scatter(x=series.index, y=series.values, name=name, line=dict(color=line_color, width=1.5), opacity=0.6))
            
            if not anomalies.empty:
                fig_anom.add_trace(go.Scatter(x=anomalies.index, y=anomalies.values, mode='markers', name=f'Anomali {name}', marker=dict(color='#F87171', size=10, symbol='circle', line=dict(width=2, color=line_color)), hovertemplate=f'<b>ANOMALI: {name}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'))
                anom_counts[name] = len(anomalies)
        
        fig_anom = apply_beautiful_layout(fig_anom, f"Pemantauan Anomali (Spike) Harga")
        fig_anom.update_layout(height=450)
        st.plotly_chart(fig_anom, use_container_width=True, config={'displayModeBar': False})
        
        if anom_counts:
            max_anom = max(anom_counts, key=anom_counts.get)
            st.markdown(f"""<div class='interpreter-box'><strong>💡 Interpretasi Otomatis:</strong> Terdeteksi adanya pergerakan harga di luar akal sehat (anomali) pada data yang diamati. Entitas yang paling sering mencatat kejadian ekstrem atau rentan terhadap <i>shock</i> adalah <b>{max_anom}</b> (dengan total {anom_counts[max_anom]} deteksi tak wajar). Disarankan instansi terkait memfokuskan investigasi logistik pada titik ini.</div>""", unsafe_allow_html=True)
        else: st.success("✅ Seluruh wilayah/pulau terpilih bergerak normal sesuai batas kewajaran statistik selama periode ini (Tidak ada anomali).")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 6: SPASIAL & KORELASI
# =============================================================================
with tab_spasial:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengukur fenomena <i>Spillover Effect</i> atau penularan harga antar lokasi. Mengetahui apakah kenaikan harga di satu daerah mempengaruhi harga daerah sebelahnya.<br>
        <strong>Metode:</strong> Pemetaan Geospasial (Choropleth/Scatter) digabung dengan <i>Pearson Cross-Correlation</i> antar wilayah terpilih.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li><b>Peta (Kiri):</b> Visualisasi wilayah mana yang paling "merah" (mahal) di Indonesia hari ini.</li>
            <li><b>Heatmap (Kanan):</b> Menguji hubungan antar 2 entitas. Angka mendekati 1 (Hijau terang) berarti pergerakan 100% seragam. Angka 0 (Gelap) berarti tak ada hubungan.</li>
            <li>Jika provinsi A dan B punya korelasi 0.95, maka penumpukan stok operasi pasar di provinsi A hampir pasti akan ikut menurunkan harga di provinsi B.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_s1, col_s2 = st.columns([1, 1])
    
    with col_s1:
        st.markdown("#### Peta Geografis Harga Terkini", unsafe_allow_html=True)
        df_latest = df_view[df_view['Tanggal'] == df_view['Tanggal'].max()]
        df_map = df_latest[df_latest['Wilayah'].isin(selected_regs)] if compare_mode == "Per Provinsi" else df_latest[df_latest['Pulau'].isin(selected_regs)]
            
        if not df_map.empty and 'Lat' in df_map.columns:
            fig_map = px.scatter_mapbox(df_map, lat="Lat", lon="Lon", color="Harga", size="Harga", hover_name="Wilayah", hover_data={"Harga":":,.0f", "Pulau":True, "Lat":False, "Lon":False}, color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], size_max=25, zoom=3.5, mapbox_style="carto-darkmatter")
            fig_map.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', coloraxis_colorbar=dict(title="Harga (Rp)", tickfont=dict(size=10)))
            st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
        else: st.info("Data koordinat tidak ditemukan untuk visualisasi peta.")
            
    with col_s2:
        st.markdown(f"#### Matriks Transmisi (Korelasi Harga)", unsafe_allow_html=True)
        if len(plot_data) >= 2:
            corr_df = pd.DataFrame(plot_data)
            corr_matrix = corr_df.corr()
            fig_corr = go.Figure(go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index, colorscale=[[0,'#EF4444'],[0.5,'#1C232D'],[1,'#3DD68C']], zmin=-1, zmax=1, text=np.round(corr_matrix.values, 2), texttemplate="%{text}", textfont=dict(size=11), colorbar=dict(title='r', tickfont=dict(size=10)), hovertemplate="%{y} ↔ %{x}<br>Korelasi: %{z:.2f}<extra></extra>"))
            fig_corr.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=50), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickangle=-45, tickfont=dict(size=11, color='#9BAABD')), yaxis=dict(tickfont=dict(size=11, color='#9BAABD')))
            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})
            
            corr_matrix_masked = corr_matrix.where(~np.eye(corr_matrix.shape[0], dtype=bool))
            if not corr_matrix_masked.isna().all().all():
                max_corr_val = corr_matrix_masked.max().max()
                prov_a, prov_b = corr_matrix_masked.stack().idxmax()
                st.markdown(f"""<div class='interpreter-box' style='margin-top:0;'><strong>💡 Interpretasi Otomatis:</strong> Pasangan dengan transmisi penularan harga paling kuat/identik adalah <b>{prov_a}</b> dan <b>{prov_b}</b> (r = {max_corr_val:.2f}). Kebijakan peredaman harga pada salah satu dari dua entitas ini kemungkinan besar akan ikut berdampak langsung ke entitas pasangannya.</div>""", unsafe_allow_html=True)
        else: st.info(f"Pilih setidaknya 2 entitas untuk menghasilkan matriks korelasi.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 7: KOMPLEKSITAS (ENTROPI)
# =============================================================================
with tab_entropi:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengukur tingkat "Kekacauan" (<i>Randomness</i>) atau seberapa sulit harga diprediksi secara matematis.<br>
        <strong>Metode:</strong> Model Teori Informasi <i>Shannon Entropy</i> pada nilai turunan harga harian (Log Returns).<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Panjang bar menunjukkan nilai entropi dalam satuan <i>bits</i>.</li>
            <li><b>Entropi Tinggi:</b> Harga ayam bergerak sangat acak (menyebar rata), menandakan iklim ketidakpastian tinggi di pasar tersebut (penuh fluktuasi tanpa arah pasti).</li>
            <li><b>Entropi Rendah:</b> Harga bergerak kaku (<i>Price Stickiness</i>) atau sangat mudah diprediksi. Biasanya dikontrol kuat oleh pasokan dominan.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if plot_data:
        entropy_results = [{'Entitas': 'Nasional', 'Entropi (bits)': calc_shannon_entropy(nat_avg), 'Warna': '#3DD68C'}]
        for i, (name, series) in enumerate(plot_data.items()):
            entropy_results.append({'Entitas': name, 'Entropi (bits)': calc_shannon_entropy(series), 'Warna': PALETTE[i % len(PALETTE)]})
            
        df_ent = pd.DataFrame(entropy_results).sort_values('Entropi (bits)', ascending=True)
        col_e1, col_e2 = st.columns([2, 1])
        
        with col_e1:
            fig_ent = px.bar(df_ent, x='Entropi (bits)', y='Entitas', orientation='h', color='Entitas', color_discrete_map=dict(zip(df_ent['Entitas'], df_ent['Warna'])), text='Entropi (bits)')
            fig_ent.update_traces(texttemplate='%{text:.3f} bits', textposition='outside', marker_line_width=0)
            fig_ent = apply_beautiful_layout(fig_ent, f"Tingkat Keacakan Pasar (Shannon Entropy)")
            fig_ent.update_layout(height=400, showlegend=False, xaxis=dict(title="Tingkat Kompleksitas (bits) ➔ Makin Tinggi Makin Acak"), yaxis=dict(title="", tickfont=dict(size=12)))
            st.plotly_chart(fig_ent, use_container_width=True, config={'displayModeBar': False})
            
        with col_e2:
            max_ent = df_ent.iloc[-1]
            min_ent = df_ent[df_ent['Entitas'] != 'Nasional'].iloc[0] if len(df_ent) > 1 else df_ent.iloc[0]
            st.markdown(f"""<div class='interpreter-box' style='height:90%;'><strong>💡 Interpretasi Otomatis:</strong><br><br><b>Pasar Paling Acak:</b> <b>{max_ent['Entitas']}</b> ({max_ent['Entropi (bits)']:.3f} bits). Pasar bertindak dinamis, sangat menyulitkan sistem peramalan (forecasting) presisi harian.<br><br><b>Pasar Paling Kaku/Teratur:</b> <b>{min_ent['Entitas']}</b> ({min_ent['Entropi (bits)']:.3f} bits). Pergerakan harga monoton, menandakan struktur distribusi pasokan yang dominan dan pasti.</div>""", unsafe_allow_html=True)
    else: st.info("Pilih wilayah/pulau terlebih dahulu.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 8: KECEPATAN MEAN REVERSION (HALF-LIFE)
# =============================================================================
with tab_halflife:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Mengukur seberapa efisien pasar memulihkan diri (<i>recovery</i>) setelah terjadi kepanikan atau lonjakan harga (<i>shock</i>).<br>
        <strong>Metode:</strong> Ekstraksi parameter model <i>Auto-Regressive AR(1)</i> untuk menghitung nilai <i>Half-Life</i> (Waktu Paruh) <i>Mean Reversion</i>.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Nilai ditampilkan dalam hitungan <b>Hari</b>.</li>
            <li>Wilayah dengan hari <b>paling pendek</b> berarti pasarnya sangat efisien (jika harga meroket, cepat sekali kembali normal karena suplai cepat diguyur).</li>
            <li>Bar merah <b>"Tak Terhingga"</b> menandakan harga yang telah meroket gagal kembali turun (terjadi inflasi permanen / <i>Random Walk</i>).</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if plot_data:
        hl_results = [{'Entitas': 'Nasional', 'Half-Life (Hari)': calc_half_life(nat_avg), 'Warna': '#3DD68C'}]
        for i, (name, series) in enumerate(plot_data.items()):
            hl_results.append({'Entitas': name, 'Half-Life (Hari)': calc_half_life(series), 'Warna': PALETTE[i % len(PALETTE)]})
            
        df_hl = pd.DataFrame(hl_results).sort_values('Half-Life (Hari)', ascending=True)
        df_hl_plot = df_hl.copy()
        df_hl_plot['Plot_HL'] = df_hl_plot['Half-Life (Hari)'].apply(lambda x: 365 if x == np.inf else x)
        df_hl_plot['Teks_HL'] = df_hl_plot['Half-Life (Hari)'].apply(lambda x: "Tak Terhingga (Eksplosif)" if x == np.inf else f"{x:.1f} Hari")
        df_hl_plot['Plot_Warna'] = df_hl_plot.apply(lambda row: '#F87171' if row['Half-Life (Hari)'] == np.inf else row['Warna'], axis=1)

        col_hl1, col_hl2 = st.columns([2, 1])
        
        with col_hl1:
            fig_hl = px.bar(df_hl_plot, x='Plot_HL', y='Entitas', orientation='h', color='Entitas', color_discrete_map=dict(zip(df_hl_plot['Entitas'], df_hl_plot['Plot_Warna'])), text='Teks_HL')
            fig_hl.update_traces(textposition='outside', marker_line_width=0, hovertemplate='<b>%{y}</b><br>Waktu Pemulihan: %{text}<extra></extra>')
            fig_hl = apply_beautiful_layout(fig_hl, f"Kecepatan Penyerapan Shock Harga (Half-Life)")
            fig_hl.update_layout(height=400, showlegend=False, xaxis=dict(title="Hari (Makin Cepat Makin Baik)"), yaxis=dict(title="", tickfont=dict(size=12)))
            st.plotly_chart(fig_hl, use_container_width=True, config={'displayModeBar': False})
            
        with col_hl2:
            valids = df_hl[df_hl['Half-Life (Hari)'] != np.inf]
            if not valids.empty:
                fastest = valids.iloc[0]
                st.markdown(f"""<div class='interpreter-box' style='height:90%;'><strong>💡 Interpretasi Otomatis:</strong><br><br>Pasar berkinerja terbaik/paling sehat dalam meredam gejolak harga adalah <b>{fastest['Entitas']}</b> (hanya butuh <b>{fastest['Half-Life (Hari)']:.1f} hari</b> untuk meredam separuh kepanikan harga).<br><br>Waspadai entitas merah (Tak Terhingga); ini menandakan pasar yang kaku ke bawah (harganya gampang naik, tapi susah turun lagi).</div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class='interpreter-box' style='height:90%;'><strong>💡 Interpretasi Otomatis:</strong> Seluruh entitas pasar pada rentang waktu terpilih bersifat eksplosif (Tak Terhingga). Lonjakan harga bersifat permanen membentuk level ekuilibrium harga baru yang lebih tinggi.</div>""", unsafe_allow_html=True)
    else: st.info("Pilih wilayah/pulau terlebih dahulu.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 9: PRA & PASCA EVENT (EFEK HARI RAYA/KALENDER)
# =============================================================================
with tab_preevent:
    with st.expander("📖 Panduan Analisis", expanded=False):
        st.markdown("""<div class='guide-box'>
        <strong>Tujuan:</strong> Menginvestigasi perilaku pembentukan harga (Spekulasi/Inflasi Musiman) sebelum dan sesudah <i>event</i> besar atau hari libur nasional.<br>
        <strong>Metode:</strong> <i>Event Study Analysis</i> / Windowing Data berdasarkan kalender. Membandingkan data N-hari sebelum dan N-hari sesudah tanggal event berlangsung.<br>
        <strong>Cara Baca & Interpretasi:</strong>
        <ul>
            <li>Atur Event, Tahun, serta lebar jendela sebelum (H-) dan sesudah (H+) pada slider.</li>
            <li>Garis vertikal merah putus-putus pada grafik menandakan tepat pada hari "H" perayaan.</li>
            <li>Jika harga menanjak agresif di area H- dan runtuh tajam di area H+, ini membuktikan fenomena tarikan permintaan musiman spesifik akibat acara tersebut.</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # UI Control Bar
    row_ev1 = st.columns([1, 1, 1, 1])
    ev_name = row_ev1[0].selectbox("Pilih Perayaan Nasional:", list(EVENT_DATES.keys()))
    ev_years = [y for y, d in EVENT_DATES[ev_name].items() if pd.to_datetime(d) <= df_full['Tanggal'].max() + pd.Timedelta(days=60)] 
    
    if not ev_years:
        st.warning("Data histori tidak mencakup event ini. Pilih event lain.")
    else:
        ev_year = row_ev1[1].selectbox("Tahun Kejadian:", ev_years)
        days_before = row_ev1[2].slider("Fokus Pra-Event (H-)", 0, 60, 14, 1, help="Berapa hari sebelum acara")
        days_after = row_ev1[3].slider("Fokus Pasca-Event (H+)", 0, 60, 14, 1, help="Berapa hari setelah acara")
        
        target_date = pd.to_datetime(EVENT_DATES[ev_name][ev_year])
        start_date = target_date - pd.Timedelta(days=days_before)
        end_date = target_date + pd.Timedelta(days=days_after)
        
        st.markdown(f"<div align='center' style='padding: 8px; background:#1C232D; border-radius:8px; margin-top:10px; font-size:14px;'>🗓️ Tanggal Puncak (Hari H): <b style='color:#F87171'>{target_date.strftime('%d %b %Y')}</b> | Analisis mulai <b>{start_date.strftime('%d %b')}</b> s/d <b>{end_date.strftime('%d %b')}</b></div>", unsafe_allow_html=True)
        
        # Ekstraksi Data Spesifik Jendela Event
        df_event = df_full[(df_full['Tanggal'] >= start_date) & (df_full['Tanggal'] <= end_date)]
        
        if df_event.empty:
            st.warning("Sistem tidak memiliki riwayat data pada jendela waktu ini (data belum terupdate ke sistem pusat).")
        else:
            fig_ev = go.Figure()
            
            # Plot Nasional
            nat_ev = df_event.groupby('Tanggal')['Harga'].mean()
            fig_ev.add_trace(go.Scatter(x=nat_ev.index, y=nat_ev.values, name='Nasional', fill='tozeroy', fillcolor='rgba(61,214,140,0.15)', line=dict(color='#3DD68C', width=3)))
            
            # Plot Entitas
            for i, reg in enumerate(selected_regs):
                filter_col = 'Wilayah' if compare_mode == "Per Provinsi" else 'Pulau'
                s_ev = df_event[df_event[filter_col] == reg].groupby('Tanggal')['Harga'].mean()
                if not s_ev.empty:
                    fig_ev.add_trace(go.Scatter(x=s_ev.index, y=s_ev.values, name=reg, line=dict(color=PALETTE[i % len(PALETTE)], width=1.5)))
            
            # Garis Vertikal Penanda Hari H
            fig_ev.add_vline(x=target_date.timestamp() * 1000, line_width=2, line_dash="dash", line_color="#F87171")
            fig_ev.add_annotation(x=target_date.timestamp() * 1000, y=1, yref="paper", text="Hari 'H'", showarrow=False, bgcolor="#F87171", font=dict(color="white"))
            
            fig_ev = apply_beautiful_layout(fig_ev, f"Dinamika Event H-{days_before} hingga H+{days_after} ({ev_name} {ev_year})")
            fig_ev.update_layout(height=450)
            st.plotly_chart(fig_ev, use_container_width=True, config={'displayModeBar': False})
            
            # KALKULATOR EFEK & INTERPRETER
            if not nat_ev.empty:
                val_start = nat_ev.iloc[0]
                val_peak = nat_ev.loc[:target_date].iloc[-1] if not nat_ev.loc[:target_date].empty else val_start
                val_end = nat_ev.iloc[-1]
                
                inflasi_pra = ((val_peak - val_start) / val_start) * 100 if days_before > 0 else 0
                inflasi_pasca = ((val_end - val_peak) / val_peak) * 100 if days_after > 0 else 0
                
                teks_pra = f"**naik {abs(inflasi_pra):.2f}%**" if inflasi_pra > 0 else f"**turun {abs(inflasi_pra):.2f}%**"
                teks_pasca = f"**naik {abs(inflasi_pasca):.2f}%**" if inflasi_pasca > 0 else f"**mereda/turun {abs(inflasi_pasca):.2f}%**"
                
                st.markdown(f"""<div class='interpreter-box'><strong>💡 Wawasan Efek Kalender (Calendar Effect) Secara Nasional:</strong><br><br>
                1. <b>Fase Eskalasi (Pra-Event):</b> Selama H-{days_before} sebelum acara, harga {teks_pra}. {'Ini wajar terjadi karena *demand pull inflation* musiman.' if inflasi_pra > 0 else 'Fakta menarik, pasokan aman menahan inflasi walau permintaan akan meninggi.'}<br>
                2. <b>Fase Pendinginan (Pasca-Event):</b> Setelah acara berlalu (H+{days_after}), harga tercatat {teks_pasca}. {'Harga mereda normal menyesuaikan titik wajarnya.' if inflasi_pasca <= 0 else 'Awas! Harga justru tetap meroket setelah perayaan usai, ada kemungkinan pasokan logistik terkuras habis di hari raya.'}</div>""", unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
