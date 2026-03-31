import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_all_data

# Page configuration
st.set_page_config(
    page_title="Dashboard Harga Daging Ayam Ras",
    page_icon="🐔",
    layout="wide"
)

# Title
st.title("🐔 Dashboard Interaktif Harga Daging Ayam Ras")
st.markdown("---")

# Load data
@st.cache_data
def get_data():
    return load_all_data('Data')

with st.spinner('Memuat data...'):
    df = get_data()

if df.empty:
    st.error("Tidak ada data yang ditemukan!")
else:
    # Sidebar filters
    st.sidebar.header("Filter")
    
    # Date range filter
    min_date = df['Tanggal'].min()
    max_date = df['Tanggal'].max()
    
    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Region filter
    all_regions = sorted(df['Wilayah'].unique())
    selected_regions = st.sidebar.multiselect(
        "Pilih Wilayah",
        options=all_regions,
        default=all_regions[:5]  # Default first 5 regions
    )
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df['Tanggal'] >= pd.Timestamp(start_date)) & 
                        (df['Tanggal'] <= pd.Timestamp(end_date))]
    else:
        filtered_df = df
    
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Wilayah'].isin(selected_regions)]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = filtered_df['Harga'].mean()
        st.metric("Rata-rata Harga Nasional", f"Rp {avg_price:,.0f}")
    
    with col2:
        min_price = filtered_df['Harga'].min()
        st.metric("Harga Terendah", f"Rp {min_price:,.0f}")
    
    with col3:
        max_price = filtered_df['Harga'].max()
        st.metric("Harga Tertinggi", f"Rp {max_price:,.0f}")
    
    with col4:
        total_records = len(filtered_df)
        st.metric("Total Record Data", f"{total_records:,}")
    
    st.markdown("---")
    
    # Chart 1: Line chart - Price trend over time
    st.subheader("📈 Tren Harga Over Time")
    if not filtered_df.empty:
        fig_line = px.line(
            filtered_df,
            x='Tanggal',
            y='Harga',
            color='Wilayah',
            title='Perkembangan Harga Daging Ayam Ras per Wilayah',
            labels={'Harga': 'Harga (Rp)', 'Tanggal': 'Tanggal'},
            hover_data=['Wilayah', 'Harga'],
            height=600
        )
        fig_line.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp)",
            legend_title="Wilayah",
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")
    
    # Chart 2: Bar chart - Average price by region
    st.subheader("📊 Rata-rata Harga per Wilayah")
    if not filtered_df.empty:
        avg_by_region = filtered_df.groupby('Wilayah')['Harga'].mean().reset_index()
        avg_by_region = avg_by_region.sort_values('Harga', ascending=True)
        
        fig_bar = px.bar(
            avg_by_region,
            x='Harga',
            y='Wilayah',
            orientation='h',
            title='Rata-rata Harga Daging Ayam Ras per Wilayah',
            labels={'Harga': 'Rata-rata Harga (Rp)', 'Wilayah': 'Wilayah'},
            color='Harga',
            color_continuous_scale='RdYlGn_r',
            height=600
        )
        fig_bar.update_layout(
            xaxis_title="Rata-rata Harga (Rp)",
            yaxis_title="Wilayah",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Chart 3: Heatmap - Price by region and date
    st.subheader("🔥 Heatmap Harga per Wilayah dan Tanggal")
    if not filtered_df.empty:
        # Create pivot table for heatmap
        pivot_df = filtered_df.pivot_table(
            index='Wilayah',
            columns='Tanggal',
            values='Harga',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            pivot_df,
            labels=dict(x="Tanggal", y="Wilayah", color="Harga (Rp)"),
            x=pivot_df.columns.strftime('%Y-%m-%d'),
            y=pivot_df.index,
            color_continuous_scale='RdYlGn_r',
            aspect='auto',
            height=600
        )
        fig_heatmap.update_layout(
            xaxis_title="Tanggal",
            yaxis_title="Wilayah",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Chart 4: Box plot - Price distribution by region
    st.subheader("📦 Distribusi Harga per Wilayah")
    if not filtered_df.empty:
        fig_box = px.box(
            filtered_df,
            x='Wilayah',
            y='Harga',
            title='Distribusi Harga Daging Ayam Ras per Wilayah',
            labels={'Harga': 'Harga (Rp)', 'Wilayah': 'Wilayah'},
            color='Wilayah',
            height=600
        )
        fig_box.update_layout(
            xaxis_title="Wilayah",
            yaxis_title="Harga (Rp)",
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Data table
    st.subheader("📋 Tabel Data")
    with st.expander("Lihat Data Lengkap"):
        st.dataframe(
            filtered_df.sort_values('Tanggal', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data sebagai CSV",
            data=csv,
            file_name='data_harga_ayam.csv',
            mime='text/csv'
        )
    
    # Statistics summary
    st.subheader("📝 Ringkasan Statistik")
    stats_df = filtered_df.groupby('Wilayah')['Harga'].agg([
        ('Min', 'min'),
        ('Max', 'max'),
        ('Mean', 'mean'),
        ('Median', 'median'),
        ('Std Dev', 'std')
    ]).round(0)
    
    st.dataframe(stats_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Dashboard Harga Daging Ayam Ras** | Data diperbarui otomatis dari folder Data/")
