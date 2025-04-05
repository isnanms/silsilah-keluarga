import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import json

# Set up Google Sheets connection using Streamlit secrets
def authenticate_google_sheets():
    # Ambil JSON kredensial dari Secrets Streamlit
    creds_json = st.secrets["gcp_service_account"]  # Sesuaikan dengan nama secret kamu

    # Mengonversi JSON string menjadi objek Python (jika perlu)
    creds_dict = json.loads(creds_json) if isinstance(creds_json, str) else creds_json

    # Menyimpan JSON kredensial ke file sementara
    with open("temp_service_account.json", "w") as json_file:
        json.dump(creds_dict, json_file)

    # Gunakan kredensial yang disimpan
    creds = Credentials.from_service_account_file(
        "temp_service_account.json",
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )

    return gspread.authorize(creds)

# Get data from Google Sheets
def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0")
    worksheet = sheet.get_worksheet(0)  # Access the first sheet
    data = pd.DataFrame(worksheet.get_all_records())
    return data

# Main function to run the app
def main():
    st.title("Pohon Keluarga")
    st.write("Aplikasi ini menampilkan pohon keluarga berdasarkan data di Google Sheets.")
    
    data = get_family_data()
    st.write(data)

if __name__ == "__main__":
    main()
