import pandas as pd
import glob
import os
import re
from datetime import datetime


def extract_date_from_filename(filename):
    """Extract date range from filename like Statistik_Harian_20250101__20250131_Daging_Ayam_Ras.xlsx"""
    match = re.search(r'(\d{8})__(\d{8})', filename)
    if match:
        start_date = match.group(1)
        end_date = match.group(2)
        return start_date, end_date
    return None, None


def load_excel_file(filepath):
    """Load a single Excel file and return cleaned dataframe"""
    try:
        # Read the 'Average Prices' sheet with header at row 2 (0-indexed)
        df = pd.read_excel(filepath, sheet_name='Average Prices', header=2)
        
        # Rename first column to 'Wilayah'
        df = df.rename(columns={df.columns[0]: 'Wilayah'})
        
        # Get the actual dates from the header row (they're in the first data row after header)
        # The dates are stored as column names but prefixed with 'Unnamed:'
        date_columns = []
        for col in df.columns[1:]:  # Skip 'Wilayah' column
            # Get the value from the first row to find the actual date
            val = df.iloc[0][col]
            if pd.notna(val) and isinstance(val, (datetime, pd.Timestamp)):
                date_columns.append(val.strftime('%Y-%m-%d'))
            elif pd.notna(val) and isinstance(val, str) and re.match(r'\d{4}-\d{2}-\d{2}', str(val)):
                date_columns.append(str(val))
            else:
                date_columns.append(col)
        
        # Create new column names
        new_columns = ['Wilayah'] + date_columns
        df.columns = new_columns
        
        # Melt the dataframe to long format
        melted = df.melt(id_vars=['Wilayah'], var_name='Tanggal', value_name='Harga')
        
        # Convert Harga to numeric, coerce errors to NaN
        melted['Harga'] = pd.to_numeric(melted['Harga'], errors='coerce')
        
        # Filter out rows where Harga is 0 or NaN
        melted = melted[melted['Harga'] > 0]
        
        # Convert Tanggal to datetime
        melted['Tanggal'] = pd.to_datetime(melted['Tanggal'], errors='coerce')
        
        # Drop rows with invalid dates
        melted = melted.dropna(subset=['Tanggal'])
        
        return melted
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return pd.DataFrame()


def load_all_data(data_folder='Data'):
    """Load all Excel files from the data folder automatically"""
    # Find all Excel files
    pattern = os.path.join(data_folder, '*.xlsx')
    excel_files = glob.glob(pattern)
    
    if not excel_files:
        print(f"No Excel files found in {data_folder}")
        return pd.DataFrame()
    
    # Sort files by name to ensure chronological order
    excel_files.sort()
    
    all_data = []
    
    for filepath in excel_files:
        filename = os.path.basename(filepath)
        print(f"Loading: {filename}")
        
        df = load_excel_file(filepath)
        
        if not df.empty:
            # Add source file info
            df['SourceFile'] = filename
            all_data.append(df)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates based on Wilayah and Tanggal
        combined_df = combined_df.drop_duplicates(subset=['Wilayah', 'Tanggal'], keep='last')
        
        # Sort by Tanggal and Wilayah
        combined_df = combined_df.sort_values(['Tanggal', 'Wilayah']).reset_index(drop=True)
        
        print(f"\nTotal records loaded: {len(combined_df)}")
        print(f"Date range: {combined_df['Tanggal'].min()} to {combined_df['Tanggal'].max()}")
        print(f"Number of regions: {combined_df['Wilayah'].nunique()}")
        
        return combined_df
    
    return pd.DataFrame()


if __name__ == "__main__":
    # Test the loader
    df = load_all_data('Data')
    if not df.empty:
        print("\nFirst 10 rows:")
        print(df.head(10))
        print("\nColumn types:")
        print(df.dtypes)
