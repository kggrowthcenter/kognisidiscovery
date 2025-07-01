import streamlit as st
import pandas as pd
import pymysql
import gspread
from oauth2client.service_account import ServiceAccountCredentials


@st.cache_resource(ttl=1800)
def get_discovery_connection():
    return pymysql.connect(
        host=st.secrets["discovery"]["host"],
        port=st.secrets["discovery"]["port"],
        user=st.secrets["discovery"]["user"],
        password=st.secrets["discovery"]["password"],
        database=st.secrets["discovery"]["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

@st.cache_data(ttl=1800)
def fetch_data_from_query(query_file):
    try:
        conn = get_discovery_connection()
        with open(query_file, 'r') as sql_file:
            query = sql_file.read()

        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"An error occurred while fetching data from {query_file}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def fetch_data_discovery_al():
    return fetch_data_from_query('query_DiscoveryAL.sql')

@st.cache_data(ttl=1800)
def fetch_data_discovery_au():
    return fetch_data_from_query('query_DiscoveryAU.sql')


# ----------------------------------
# Cached Google Sheets client
# ----------------------------------
@st.cache_resource(ttl=1800)
def get_gspread_client(secret_key: str):
    secret_info = st.secrets[secret_key]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    return gspread.authorize(creds)

# ----------------------------------
# Fetch Capture Sheet (2 worksheets)
# ----------------------------------
@st.cache_data(ttl=1800)
def fetch_data_capture():
    client = get_gspread_client("json_sap")
    spreadsheet = client.open("0. Data Capture - Monthly Updated")

    sheet1 = spreadsheet.get_worksheet(4)
    sheet2 = spreadsheet.get_worksheet(1)

    data1 = sheet1.get_all_records()
    data2 = sheet2.get_all_records()

    df_capture_sheet1 = pd.DataFrame(data1)
    df_capture_sheet2 = pd.DataFrame(data2)

    return df_capture_sheet1, df_capture_sheet2

# ----------------------------------
# Fetch SAP Sheet with selected columns
# ----------------------------------
@st.cache_data(ttl=1800)
def fetch_data_sap(selected_columns):
    client = get_gspread_client("json_sap")
    spreadsheet = client.open("0. Active Employee - Monthly Updated")
    sheet = spreadsheet.sheet1

    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df[selected_columns]

# ----------------------------------
# Fetch Credentials Sheet
# ----------------------------------
@st.cache_data(ttl=1800)
def fetch_data_creds():
    client = get_gspread_client("sheets")
    spreadsheet = client.open("Discovery Test Result - Dashboard Credentials")

    sheet1 = spreadsheet.sheet1
    data1 = sheet1.get_all_records()
    df_creds = pd.DataFrame(data1)

    return df_creds
