import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Silsilah Keluarga", layout="wide")

st.title("🌳 Silsilah Keluarga Besar")

# --- Autentikasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- Ambil Data dari Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit#gid=0"
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Tampilkan Data ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if "http" in row["Foto URL"]:
                st.image(row["Foto URL"], width=100, use_column_width=False)
            else:
                st.write("📷 Foto tidak ditemukan")
        with cols[1]:
            st.markdown(f"### {row['Nama Lengkap']}")
            st.markdown(f"**Hubungan**: {row['Hubungan']}")
            st.markdown("---")
