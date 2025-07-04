import streamlit as st
import pandas as pd
from fetch_data import fetch_data_discovery_al, fetch_data_discovery_au, fetch_data_sap, fetch_data_capture, fetch_data_creds

@st.cache_data(ttl=1800)
def fill_empty_with_na(df, value='N/A'):
    """Fill empty or None values in the DataFrame with the specified value."""
    return df.replace(['', None, '#VALUE!'], value).fillna(value)

@st.cache_data(ttl=1800)
def fetch_discovery_al_data():
    df_discovery_al = fetch_data_discovery_al()
    df_discovery_al['email'] = df_discovery_al['email'].str.strip().str.lower()
    return fill_empty_with_na(df_discovery_al)

@st.cache_data(ttl=1800)
def fetch_discovery_au_data():
    df_discovery_au = fetch_data_discovery_au()
    df_discovery_au['email'] = df_discovery_au['email'].str.strip().str.lower()
    return fill_empty_with_na(df_discovery_au)

@st.cache_data(ttl=1800)
def fetch_sap_data():
    selected_columns = ['name_sap', 'email', 'nik', 'unit', 'subunit', 'admin_hr', 'layer', 'generation', 'gender', 'division', 'department', 'tenure']
    df_sap = fetch_data_sap(selected_columns)
    df_sap['email'] = df_sap['email'].str.strip().str.lower()
    df_sap['nik'] = df_sap['nik'].astype(str).str.zfill(6)
    return fill_empty_with_na(df_sap)

@st.cache_data(ttl=1800)
def fetch_capture_data():
    df_capture_sheet1, df_capture_sheet2 = fetch_data_capture()
    df_capture_sheet1['email'] = df_capture_sheet1['email'].str.strip().str.lower()
    df_capture_sheet2['email'] = df_capture_sheet2['email'].str.strip().str.lower()
    df_capture_sheet1 = fill_empty_with_na(df_capture_sheet1)
    df_capture_sheet2 = fill_empty_with_na(df_capture_sheet2)
    return df_capture_sheet1, df_capture_sheet2

@st.cache_data(ttl=1800)
def finalize_data():
    df_discovery_al = fetch_discovery_al_data()
    df_discovery_au = fetch_discovery_au_data()
    df_sap = fetch_sap_data()
    df_capture_sheet1, df_capture_sheet2 = fetch_capture_data()
    df_creds = fetch_data_creds()

    # Pastikan 'gender' tetap ada saat menggabungkan df_discovery_al dan df_capture_sheet1
    df_capture_sheet1['gender'] = None  # Menambahkan kolom gender ke df_capture_sheet1 dengan nilai default None
    df_combined_al_capture = pd.concat([df_discovery_al, df_capture_sheet1], ignore_index=True)

    # Drop 'nik' column if it exists
    if 'nik' in df_combined_al_capture.columns:
        df_combined_al_capture = df_combined_al_capture.drop(columns=['nik'])

    # Merge with SAP to determine status_learner
    df_merged = pd.merge(df_combined_al_capture, df_sap, on='email', how='left', indicator=True)
    df_merged['status_learner'] = df_merged['_merge'].apply(lambda x: 'Internal' if x == 'both' else 'External')
    df_merged.drop(columns=['_merge'], inplace=True)

    # Convert 'last_updated' to date
    if 'last_updated' in df_merged.columns:
        df_merged['last_updated'] = pd.to_datetime(df_merged['last_updated'], errors='coerce').dt.date

    # Pastikan tidak ada duplikasi kolom gender
    if 'gender_x' in df_merged.columns and 'gender_y' in df_merged.columns:
        df_merged['gender'] = df_merged['gender_x'].combine_first(df_merged['gender_y'])
        df_merged = df_merged.drop(columns=['gender_x', 'gender_y'])

    # Normalisasi nilai gender menjadi 'female', 'male', atau 'n/a'
    def normalize_gender(value):
        value = str(value).strip().lower()  # Pastikan nilai diubah menjadi string lowercase
        if value in ['male', 'laki-laki', 'laki - laki', 'pria', 'm']:
            return 'Male'
        elif value in ['female', 'perempuan', 'wanita', 'f']:
            return 'Female'
        else:
            return 'n/a'

    df_merged['gender'] = df_merged['gender'].apply(normalize_gender)

    # Konversi tipe data 'Customer ID' ke string
    df_merged['Customer ID'] = df_merged['Customer ID'].astype(str)
    df_merged = fill_empty_with_na(df_merged)

    # Concatenate Discovery AU and Capture Sheet2 vertically
    df_combined_au_capture = pd.concat([df_discovery_au, df_capture_sheet2], ignore_index=True)

    # Convert 'created_at' to date
    if 'created_at' in df_combined_au_capture.columns:
        df_combined_au_capture['created_at'] = pd.to_datetime(df_combined_au_capture['created_at'], errors='coerce').dt.date

    df_combined_au_capture = fill_empty_with_na(df_combined_au_capture)

    df_merged['subunit'] = df_merged['subunit'].replace(['#N/A', '-'], 'N/A')
    df_merged['layer'] = df_merged['layer'].replace({
        'Group 5 Str Layer 1': 'Layer 1',
        'Group 4 Str Layer 2': 'Layer 2',
        'Group 3 Str Layer 3B': 'Layer 3',
        'Group 3 Str Layer 3A': 'Layer 3',
        'Group 2 Str Layer 4': 'Layer 4',
        'Group 1 Str Layer 5': 'Layer 5',
        'Group 1': 'Non Struktural',
        'Group 2': 'Non Struktural',
        'Group 3': 'Non Struktural',
        'Group 4': 'Non Struktural',
        'Group 5': 'Non Struktural',
        0: 'N/A'
    })


    return df_sap, df_merged, df_combined_au_capture, df_creds
