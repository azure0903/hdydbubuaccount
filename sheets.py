import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)

def open_sheet(sheet_id):
    gc = get_gspread_client()
    return gc.open_by_key(sheet_id)
