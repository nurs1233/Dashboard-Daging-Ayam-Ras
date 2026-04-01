import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Dashboard Harga Daging Ayam Ras",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling yang mirip dengan HTML
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #012D1D;
        --primary-container: #1B4332;
        --secondary: #8E4E14;
        --background: #F8F9FA;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #012D1D !important;
    }
    
    .sidebar-content {
        background-color: #012D1D;
        color: white;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card-average { border-left-color: #8E4E14; }
    .metric-card-low { border-left-color: #16A34A; }
    .metric-card-high { border-left-color: #DC2626; }
    .metric-card-total { border-left-color: #012D1D; }
    
    .metric-label {
        font-size: 0.625rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #414844;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #012D1D;
        line-height: 1;
    }
    
    .metric-subtitle {
        font-size: 0.75rem;
        color: #414844;
        margin-top: 0.5rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Title styling */
    .main-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #012D1D;
        margin-bottom: 0.5rem;
        font-family: 'Manrope', sans-serif;
    }
    
    .subtitle {
        color: #414844;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }
    
    /* Status badges */
    .badge-stabil {
        background: #86AF99;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.625rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .badge-waspada {
        background: #FFDAD6;
        color: #93000A;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.625rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    /* Table styling */
    div[data-testid="stDataFrame"] {
        border-radius: 0.75rem;
        overflow: hidden;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #012D1D;
        color: white;
        border-radius: 9999px;
        font-weight: 700;
        padding: 0.5rem 1.5rem;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #1B4332;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate sample data
@st.cache_data
def generate_sample_data():
    """Generate sample data for demonstration"""
    regions = ['DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Banten', 'Papua', 
               'Sumatera Utara', 'Sulawesi Selatan', 'Bali']
    
    # Generate dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for date in dates:
        for region in regions:
            # Base price varies by region
            base_price = {
                'DKI Jakarta': 38000,
                'Jawa Barat': 33000,
                'Jawa Timur': 31000,
                'Banten': 34000,
                'Papua': 42000,
                'Sumatera Utara': 31000,
                'Sulawesi Selatan': 28000,
                'Bali': 37000
            }
            
            # Add some randomness
            price = base_price[region] + np.random.randint(-2000, 2000)
            
            # Determine status
            if price > 40000:
                status = 'Waspada'
            else:
                status = 'Stabil'
            
            data.append({
                'Tanggal': date,
                'Wilayah': region,
                'Harga': price,
                'Status': status
            })
    
    return pd.DataFrame(data)

# Load data
df = generate_sample_data()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <div style='display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem;'>
            <div style='width: 2.5rem; height: 2.5rem; background: #1B4332; border-radius: 0.5rem; 
                       display: flex; align-items: center; justify-content: center; font-size: 1.5rem;'>🐔</div>
            <div>
                <h3 style='color: white; margin: 0; font-size: 1.125rem;'>Daging Ayam Ras</h3>
                <p style='color: #86AF99; margin: 0; font-size: 0.625rem; text-transform: uppercase; 
                         letter-spacing: 0.1em; font-weight: 700;'>Market Intelligence</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #9CA3AF; font-size: 0.625rem; text-transform: uppercase; "
                "letter-spacing: 0.05em; font-weight: 700; margin: 1rem 0 0.5rem 0;'>TIMEFRAME</p>", 
                unsafe_allow_html=True)
    
    min_date = df['Tanggal'].min()
    max_date = df['Tanggal'].max()
    
    date_range = st.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        label_visibility="collapsed"
    )
    
    st.markdown("<p style='color: #9CA3AF; font-size: 0.625rem; text-transform: uppercase; "
                "letter-spacing: 0.05em; font-weight: 700; margin: 1.5rem 0 0.5rem 0;'>FILTER REGIONS</p>", 
                unsafe_allow_html=True)
    
    all_regions = sorted(df['Wilayah'].unique())
    selected_regions = st.multiselect(
        "Pilih Wilayah",
        options=all_regions,
        default=all_regions[:4],
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Live Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Apply filters
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Tanggal'] >= pd.Timestamp(start_date)) & 
                    (df['Tanggal'] <= pd.Timestamp(end_date))]
else:
    filtered_df = df

if selected_regions:
    filtered_df = filtered_df[filtered_df['Wilayah'].isin(selected_regions)]

# Main content
st.markdown("""
<div style='margin-bottom: 2rem;'>
    <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
        <div style='width: 0.5rem; height: 0.5rem; background: #16A34A; border-radius: 50%; 
                   animation: pulse 2s infinite;'></div>
        <span style='font-size: 0.75rem; font-weight: 700; color: #414844; text-transform: uppercase; 
                    letter-spacing: 0.05em;'>Market Live</span>
    </div>
    <h1 class='main-title'>Dashboard Harga Daging Ayam Ras</h1>
    <p class='subtitle'>Laporan analisis harga komoditas harian seluruh wilayah Indonesia.</p>
</div>
""", unsafe_allow_html=True)

# Metric cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_price = filtered_df['Harga'].mean()
    st.markdown(f"""
    <div class='metric-card metric-card-average'>
        <div class='metric-label'>Rata-rata Harga Nasional</div>
        <div class='metric-value'>Rp {avg_price:,.0f}</div>
        <div style='display: flex; align-items: center; gap: 0.25rem; margin-top: 0.5rem; 
                    color: #16A34A; font-size: 0.75rem; font-weight: 700;'>
            <span>↑</span><span>+2.4% MoM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    min_price = filtered_df['Harga'].min()
    min_region = filtered_df.loc[filtered_df['Harga'].idxmin(), 'Wilayah']
    st.markdown(f"""
    <div class='metric-card metric-card-low'>
        <div class='metric-label'>Harga Terendah</div>
        <div class='metric-value'>Rp {min_price:,.0f}</div>
        <div class='metric-subtitle'>Wilayah: {min_region}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    max_price = filtered_df['Harga'].max()
    max_region = filtered_df.loc[filtered_df['Harga'].idxmax(), 'Wilayah']
    st.markdown(f"""
    <div class='metric-card metric-card-high'>
        <div class='metric-label'>Harga Tertinggi</div>
        <div class='metric-value'>Rp {max_price:,.0f}</div>
        <div class='metric-subtitle'>Wilayah: {max_region}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_records = len(filtered_df)
    st.markdown(f"""
    <div class='metric-card metric-card-total'>
        <div class='metric-label'>Total Record Data</div>
        <div class='metric-value'>{total_records:,}</div>
        <div class='metric-subtitle'>Syncing 2 minutes ago</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

# Charts section
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.markdown("""
    <div class='chart-container'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;'>
            <div>
                <h3 style='color: #012D1D; font-size: 1.25rem; font-weight: 700; margin: 0; 
                           display: flex; align-items: center; gap: 0.5rem;'>
                    <span>📈</span> Tren Harga Over Time
                </h3>
                <p style='color: #414844; font-size: 0.875rem; margin: 0.25rem 0 0 0;'>
                    Perbandingan harga harian 4 wilayah utama
                </p>
            </div>
            <div style='display: flex; gap: 0.5rem;'>
                <span style='padding: 0.25rem 0.75rem; background: #F3F4F5; border-radius: 9999px; 
                            font-size: 0.625rem; font-weight: 700;'>7D</span>
                <span style='padding: 0.25rem 0.75rem; background: #012D1D; color: white; 
                            border-radius: 9999px; font-size: 0.625rem; font-weight: 700;'>1M</span>
                <span style='padding: 0.25rem 0.75rem; background: #F3F4F5; border-radius: 9999px; 
                            font-size: 0.625rem; font-weight: 700;'>3M</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_df.empty:
        fig_line = px.line(
            filtered_df,
            x='Tanggal',
            y='Harga',
            color='Wilayah',
            labels={'Harga': 'Harga (Rp)', 'Tanggal': 'Tanggal'},
            height=400,
            color_discrete_sequence=['#8E4E14', '#012D1D', '#1B4332', '#16A34A']
        )
        fig_line.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            xaxis_title='',
            yaxis_title='Harga (Rp)',
            legend_title='Wilayah',
            hovermode='x unified',
            showlegend=True,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
        )
        st.plotly_chart(fig_line, use_container_width=True)

with col_chart2:
    st.markdown("""
    <div class='chart-container'>
        <h3 style='color: #012D1D; font-size: 1.25rem; font-weight: 700; margin: 0 0 1.5rem 0; 
                   display: flex; align-items: center; gap: 0.5rem;'>
            <span>📊</span> Rata-rata per Wilayah
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_df.empty:
        avg_by_region = filtered_df.groupby('Wilayah')['Harga'].mean().reset_index()
        avg_by_region = avg_by_region.sort_values('Harga', ascending=True)
        
        fig_bar = px.bar(
            avg_by_region,
            x='Harga',
            y='Wilayah',
            orientation='h',
            labels={'Harga': '', 'Wilayah': ''},
            color='Harga',
            color_continuous_scale=['#16A34A', '#EAB308', '#DC2626'],
            height=350
        )
        fig_bar.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            xaxis_title='Rata-rata Harga (Rp)',
            yaxis_title='',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap and Distribution
col_heatmap, col_dist = st.columns(2)

with col_heatmap:
    st.markdown("""
    <div class='chart-container'>
        <h3 style='color: #012D1D; font-size: 1.25rem; font-weight: 700; margin: 0 0 1.5rem 0; 
                   display: flex; align-items: center; gap: 0.5rem;'>
            <span>🔥</span> Harga per Wilayah & Tanggal
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_df.empty:
        pivot_df = filtered_df.pivot_table(
            index='Wilayah',
            columns='Tanggal',
            values='Harga',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            pivot_df,
            labels=dict(x="Tanggal", y="Wilayah", color="Harga (Rp)"),
            color_continuous_scale='RdYlGn_r',
            aspect='auto',
            height=300
        )
        fig_heatmap.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            margin=dict(l=20, r=20, t=20, b=60),
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

with col_dist:
    st.markdown("""
    <div class='chart-container'>
        <h3 style='color: #012D1D; font-size: 1.25rem; font-weight: 700; margin: 0 0 1.5rem 0; 
                   display: flex; align-items: center; gap: 0.5rem;'>
            <span>📦</span> Distribusi Harga per Wilayah
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not filtered_df.empty:
        fig_box = px.box(
            filtered_df,
            x='Wilayah',
            y='Harga',
            labels={'Harga': 'Harga (Rp)', 'Wilayah': 'Wilayah'},
            color='Wilayah',
            height=300
        )
        fig_box.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            xaxis_title='',
            yaxis_title='Harga (Rp)',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=60),
            xaxis=dict(tickangle=-45, showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
        )
        st.plotly_chart(fig_box, use_container_width=True)

# Data table
st.markdown("""
<div class='chart-container'>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;'>
        <div>
            <h3 style='color: #012D1D; font-size: 1.25rem; font-weight: 700; margin: 0;'>
                Rincian Data Harga Harian
            </h3>
            <p style='color: #414844; font-size: 0.875rem; margin: 0.25rem 0 0 0;'>
                Update terbaru dari 34 Provinsi di Indonesia
            </p>
        </div>
        <div style='display: flex; gap: 0.5rem;'>
            <button style='padding: 0.5rem; border: 1px solid #E5E7EB; border-radius: 0.5rem; 
                          background: white; cursor: pointer;'>⚙️</button>
            <button style='padding: 0.5rem; border: 1px solid #E5E7EB; border-radius: 0.5rem; 
                          background: white; cursor: pointer;'>⋮</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Display data table
if not filtered_df.empty:
    display_df = filtered_df.sort_values('Tanggal', ascending=False).head(100)
    
    # Format the dataframe for display
    display_df['Harga'] = display_df['Harga'].apply(lambda x: f"Rp {x:,.0f}")
    display_df['Tanggal'] = display_df['Tanggal'].dt.strftime('%d %B %Y')
    
    st.dataframe(
        display_df[['Tanggal', 'Wilayah', 'Harga', 'Status']],
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data sebagai CSV",
        data=csv,
        file_name='data_harga_ayam.csv',
        mime='text/csv',
        use_container_width=True
    )

# Footer
st.markdown("""
<div style='margin-top: 3rem; text-align: center; padding: 2rem; color: #414844; font-size: 0.875rem;'>
    <h4 style='color: #012D1D; font-weight: 800; margin: 0 0 0.5rem 0;'>Dashboard Harga Daging Ayam Ras</h4>
    <p style='margin: 0; font-size: 0.75rem;'>
        Data sourced from Sistem Pemantauan Pasar dan Kebutuhan Pokok (SP2KP). 
        © 2024 Agrarian Intelligence.
    </p>
</div>
""", unsafe_allow_html=True)
