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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PEMETAAN PULAU
# ─────────────────────────────────────────────────────────────────────────────
PULAU_MAP = {
    'Sumatera': ['Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Kepulauan Riau', 'Jambi', 'Sumatera Selatan', 'Bangka Belitung', 'Bengkulu', 'Lampung'],
    'Jawa': ['Banten', 'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur'],
    'Bali & Nusa Tenggara': ['Bali', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur'],
    'Kalimantan': ['Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara'],
    'Sulawesi': ['Sulawesi Utara', 'Gorontalo', 'Sulawesi Tengah', 'Sulawesi Barat', 'Sulawesi Selatan', 'Sulawesi Tenggara'],
    'Maluku & Papua': ['Maluku Utara', 'Maluku', 'Papua Barat Daya', 'Papua Barat', 'Papua Tengah', 'Papua', 'Papua Pegunungan', 'Papua Selatan']
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
        <h1 style='font-size:2.8rem; margin:0;'>Daging Ayam Ras</h1>
        <p style='color:#9BAABD; font-size:1rem; margin-top:4px;'>Update Terakhir: {latest_date.strftime('%d %B %Y')}</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    rentang = st.selectbox("📅 Rentang Waktu", ["6 Bulan Terakhir", "3 Bulan Terakhir", "1 Bulan Terakhir", "Semua Data"])
    days = {"1 Bulan Terakhir": 30, "3 Bulan Terakhir": 90, "6 Bulan Terakhir": 180, "Semua Data": None}[rentang]
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
# METRIC CARDS (KOMPARASI INSTAN & VOLATILITAS)
# ─────────────────────────────────────────────────────────────────────────────
df_latest = df_full[df_full['Tanggal'] == latest_date]
if not df_latest.empty:
    avg_price = df_latest['Harga'].mean()
    min_row = df_latest.loc[df_latest['Harga'].idxmin()]
    max_row = df_latest.loc[df_latest['Harga'].idxmax()]
    disparitas = max_row['Harga'] - min_row['Harga']
    
    # Hitung Komparasi Waktu (vs 30 Hari Lalu)
    prev_date = latest_date - pd.Timedelta(days=30)
    df_prev = df_full[df_full['Tanggal'] <= prev_date]
    if not df_prev.empty:
        prev_date_actual = df_prev['Tanggal'].max()
        prev_avg = df_full[df_full['Tanggal'] == prev_date_actual]['Harga'].mean()
        delta_pct = ((avg_price - prev_avg) / prev_avg) * 100
    else:
        delta_pct = 0
        
    delta_class = "delta-up" if delta_pct > 0 else "delta-down" if delta_pct < 0 else ""
    delta_icon = "▲" if delta_pct > 0 else "▼" if delta_pct < 0 else "-"
    delta_html = f"<span class='metric-delta {delta_class}'>{delta_icon} {abs(delta_pct):.1f}%</span>" if delta_pct != 0 else ""

    # Hitung Volatilitas Nasional (Coefficient of Variation)
    nat_avg_series = df_view.groupby('Tanggal')['Harga'].mean()
    cv_nasional = (nat_avg_series.std() / nat_avg_series.mean() * 100) if nat_avg_series.mean() != 0 else 0

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    
    mc1.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Rata-rata Nasional</div>
            <div class='metric-value'>Rp {avg_price:,.0f} {delta_html}</div>
            <div class='metric-sub'>vs 30 Hari Lalu</div>
        </div>
    """, unsafe_allow_html=True)
    
    mc2.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Harga Termurah</div>
            <div class='metric-value'>Rp {min_row['Harga']:,.0f}</div>
            <div class='metric-sub'>📍 {min_row['Wilayah']}</div>
        </div>
    """, unsafe_allow_html=True)

    mc3.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Harga Termahal</div>
            <div class='metric-value'>Rp {max_row['Harga']:,.0f}</div>
            <div class='metric-sub danger'>📍 {max_row['Wilayah']}</div>
        </div>
    """, unsafe_allow_html=True)

    mc4.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Disparitas (Gap)</div>
            <div class='metric-value'>Rp {disparitas:,.0f}</div>
            <div class='metric-sub'>Selisih Termahal & Termurah</div>
        </div>
    """, unsafe_allow_html=True)
    
    mc5.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Volatilitas Pasar</div>
            <div class='metric-value'>{cv_nasional:.1f}%</div>
            <div class='metric-sub'>Koefisien Variasi (CV)</div>
        </div>
    """, unsafe_allow_html=True)
    
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

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

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: TREN HARGA (PROVINSI ATAU PULAU)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)

nat_avg = df_view.groupby('Tanggal')['Harga'].mean()
fig1 = go.Figure()

y_mins, y_maxs = [nat_avg.min()], [nat_avg.max()]

# Garis Nasional (Area Fill)
fig1.add_trace(go.Scatter(
    x=nat_avg.index, y=nat_avg.values, name='🇮 Nasional (Rata-rata)',
    fill='tozeroy', fillcolor='rgba(61,214,140,0.1)',
    line=dict(color='#3DD68C', width=3),
    hovertemplate='<b>Nasional</b><br>%{x|%d %b %Y}<br>Rp %{y:,.0f}<extra></extra>'
))

palette = ['#F0B429', '#60A5FA', '#F472B6', '#A78BFA', '#FB923C', '#22D3EE']

if compare_mode == "Per Provinsi":
    for i, reg in enumerate(selected_regs):
        df_plot = df_view[df_view['Wilayah'] == reg].sort_values('Tanggal')
        if not df_plot.empty:
            y_mins.append(df_plot['Harga'].min()); y_maxs.append(df_plot['Harga'].max())
            fig1.add_trace(go.Scatter(
                x=df_plot['Tanggal'], y=df_plot['Harga'], name=reg,
                line=dict(color=palette[i % len(palette)], width=1.5),
                hovertemplate=f'<b>{reg}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'
            ))
else:
    # Mode Pulau
    for i, pulau in enumerate(selected_regs):
        df_plot = df_view[df_view['Pulau'] == pulau].groupby('Tanggal')['Harga'].mean().reset_index()
        if not df_plot.empty:
            y_mins.append(df_plot['Harga'].min()); y_maxs.append(df_plot['Harga'].max())
            fig1.add_trace(go.Scatter(
                x=df_plot['Tanggal'], y=df_plot['Harga'], name=f"🏝️ {pulau}",
                line=dict(color=palette[i % len(palette)], width=2),
                hovertemplate=f'<b>Pulau {pulau}</b><br>%{{x|%d %b %Y}}<br>Rp %{{y:,.0f}}<extra></extra>'
            ))

fig1 = apply_beautiful_layout(fig1, f"📈 Pergerakan Harga Sepanjang Waktu ({compare_mode})")

y_min_total, y_max_total = min(y_mins), max(y_maxs)
padding = (y_max_total - y_min_total) * 0.05
if padding == 0: padding = y_min_total * 0.05

fig1.update_layout(height=450) 
fig1.update_yaxes(range=[y_min_total - padding, y_max_total + padding])

st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3 KOLOM BAWAH: DISPARITAS | RANKING | VOLATILITAS
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_mid, col_right = st.columns([1, 1, 1])

# ---> KIRI: TREN DISPARITAS
with col_left:
    st.markdown("<div class='card' style='height: 100%;'>", unsafe_allow_html=True)
    daily_stats = df_view.groupby('Tanggal')['Harga'].agg(['max', 'min']).reset_index()
    daily_stats['Disparitas'] = daily_stats['max'] - daily_stats['min']
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=daily_stats['Tanggal'], y=daily_stats['Disparitas'],
        fill='tozeroy', fillcolor='rgba(240, 180, 41, 0.1)', line=dict(color='#F0B429', width=2),
        name='Gap Harga', hovertemplate='<b>%{x|%d %b %Y}</b><br>Disparitas: Rp %{y:,.0f}<extra></extra>'
    ))
    fig2 = apply_beautiful_layout(fig2, "📐 Tren Disparitas Nasional")
    fig2.update_layout(height=380, showlegend=False, yaxis=dict(title="Selisih (Rp)", tickfont=dict(size=10)))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ---> TENGAH: RANKING EXTREME
with col_mid:
    st.markdown("<div class='card' style='height: 100%;'>", unsafe_allow_html=True)
    df_latest_sorted = df_latest.sort_values('Harga', ascending=True)
    df_top_bottom = pd.concat([df_latest_sorted.head(4), df_latest_sorted.tail(4)]) if len(df_latest_sorted) > 8 else df_latest_sorted

    fig3 = px.bar(
        df_top_bottom, x='Harga', y='Wilayah', orientation='h',
        color='Harga', color_continuous_scale=['#3DD68C', '#F0B429', '#F87171'], text='Harga'
    )
    fig3.update_traces(texttemplate='Rp %{text:,.0f}', textposition='outside', hovertemplate='<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>', marker_line_width=0)
    fig3 = apply_beautiful_layout(fig3, "📊 4 Termurah & Termahal")
    fig3.update_layout(height=380, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=10)), xaxis=dict(title="", showticklabels=False, showgrid=False))
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ---> KANAN: TOP VOLATILITAS (BAR CHART)
with col_right:
    st.markdown("<div class='card' style='height: 100%;'>", unsafe_allow_html=True)
    # Hitung CV per wilayah selama rentang waktu
    vol_data = df_view.groupby('Wilayah')['Harga'].apply(lambda x: x.std() / x.mean() * 100).reset_index()
    vol_data.columns = ['Wilayah', 'CV']
    vol_data = vol_data.sort_values('CV', ascending=False).head(8) # Ambil 8 Paling Volatil
    
    fig4 = px.bar(
        vol_data.sort_values('CV', ascending=True), # Sort ascending for Plotly horizontal bar display
        x='CV', y='Wilayah', orientation='h',
        color='CV', color_continuous_scale=['#F0B429', '#F87171'], text='CV'
    )
    fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside', hovertemplate='<b>%{y}</b><br>CV: %{x:.2f}%<extra></extra>', marker_line_width=0)
    fig4 = apply_beautiful_layout(fig4, "🌪️ Top 8 Wilayah Paling Volatil")
    fig4.update_layout(height=380, coloraxis_showscale=False, yaxis=dict(title="", tickfont=dict(size=10)), xaxis=dict(title="", showticklabels=False, showgrid=False))
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
