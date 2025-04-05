import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import json

def authenticate_google_sheets():
    # Ambil kredensial dari Streamlit Secrets
    creds_dict = st.secrets["google_service_account"]

    # Gunakan kredensial langsung dari dictionary
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )

    return gspread.authorize(creds)

def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0")
    worksheet = sheet.get_worksheet(0)  # Akses sheet pertama
    data = pd.DataFrame(worksheet.get_all_records())
    return data

def main():
    st.title("Pohon Keluarga")
    st.write("Aplikasi ini menampilkan pohon keluarga berdasarkan data di Google Sheets.")
    
    data = get_family_data()
    st.write(data)

if __name__ == "__main__":
    main()
