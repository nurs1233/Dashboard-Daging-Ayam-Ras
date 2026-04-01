import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & CSS MINIMALIS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AgriPulse | Daging Ayam Ras", page_icon="🐔", layout="wide")

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
.live-dot {
    display: inline-block; width: 8px; height: 8px; background: var(--accent);
    border-radius: 50%; animation: livepulse 2s infinite; margin-right: 8px;
}
@keyframes livepulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(61,214,140,0.4); }
    50% { opacity: 0.5; box-shadow: 0 0 0 6px rgba(61,214,140,0); }
}
</style>
""", unsafe_allow_html=True)

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
    return combined.sort_values(['Wilayah','Tanggal']).reset_index(drop=True)

df_full = load_all_data()
if df_full.empty:
    st.error("Data tidak ditemukan atau kosong."); st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & FILTER
# ─────────────────────────────────────────────────────────────────────────────
latest_date = df_full['Tanggal'].max()
st.markdown(f"""
    <div style='margin-bottom: 2rem;'>
        <div style='font-size:12px; color:#3DD68C; letter-spacing:2px; text-transform:uppercase; font-weight:700;'>
            <span class='live-dot'></span>AgriPulse Market Intelligence
        </div>
        <h1 style='font-size:2.8rem; margin:0;'>Daging Ayam Ras</h1>
        <p style='color:#9BAABD; font-size:1rem; margin-top:4px;'>Update Terakhir: {latest_date.strftime('%d %B %Y')}</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    rentang = st.selectbox("📅 Rentang Waktu", ["6 Bulan Terakhir", "3 Bulan Terakhir", "1 Bulan Terakhir", "Semua Data"])
    days = {"1 Bulan Terakhir": 30, "3 Bulan Terakhir": 90, "6 Bulan Terakhir": 180, "Semua Data": None}[rentang]
    
    d_start = df_full['Tanggal'].min() if days is None else max(latest_date - pd.Timedelta(days=days), df_full['Tanggal'].min())
    df_view = df_full[(df_full['Tanggal'] >= d_start) & (df_full['Tanggal'] <= latest_date)]

with col2:
    all_regions = sorted(df_full['Wilayah'].unique())
    default_regs = [r for r in ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Sumatera Utara'] if r in all_regions]
    selected_regs = st.multiselect("🌏 Bandingkan Wilayah Utama", all_regions, default=default_regs)

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
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(showgrid=False, gridcolor='#2A3142', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2A3142', zeroline=False, tickformat=",.0f")
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: TREN HARGA (AREA & LINE)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)

nat_avg = df_view.groupby('Tanggal')['Harga'].mean()
fig1 = go.Figure()

# Garis Nasional (Area Fill)
fig1.add_trace(go.Scatter(
    x=nat_avg.index, y=nat_avg.values, name='🇮 Nasional (Rata-rata)',
    fill='tozeroy', fillcolor='rgba(61,214,140,0.1)',
    line=dict(color='#3DD68C', width=3),
    hovertemplate='<b>Nasional</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'
))

# Garis Provinsi Terpilih
palette = ['#F0B429', '#60A5FA', '#F472B6', '#A78BFA', '#FB923C']
for i, reg in enumerate(selected_regs):
    df_reg = df_view[df_view['Wilayah'] == reg].sort_values('Tanggal')
    fig1.add_trace(go.Scatter(
        x=df_reg['Tanggal'], y=df_reg['Harga'], name=reg,
        line=dict(color=palette[i % len(palette)], width=1.5),
        hovertemplate=f'<b>{reg}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'
    ))

fig1 = apply_beautiful_layout(fig1, "📈 Pergerakan Harga Sepanjang Waktu")
st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: RANKING HARGA TERKINI (BAR CHART)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)

# Ambil data hari terakhir
df_latest = df_full[df_full['Tanggal'] == latest_date].sort_values('Harga', ascending=True)

fig2 = px.bar(
    df_latest, x='Harga', y='Wilayah', orientation='h',
    color='Harga', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'],
    text='Harga'
)

fig2.update_traces(
    texttemplate='Rp %{text:,.0f}', textposition='outside',
    hovertemplate='<b>%{y}</b><br>Harga: Rp %{x:,.0f}<extra></extra>',
    marker_line_width=0
)

fig2 = apply_beautiful_layout(fig2, f"📊 Peringkat Harga per Wilayah (Update: {latest_date.strftime('%d %b %Y')})")
fig2.update_layout(
    height=max(400, len(df_latest) * 22), # Ketinggian dinamis menyesuaikan jumlah provinsi
    coloraxis_showscale=False, # Sembunyikan colorbar agar lebih bersih
    yaxis=dict(title="", tickfont=dict(size=10)),
    xaxis=dict(title="", showticklabels=False, showgrid=False)
)

st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)
