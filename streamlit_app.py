import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Autentikasi Google Sheets ---
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
client = gspread.authorize(credentials)

# --- Ambil Data dari Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc"
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Tampilkan Data ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if "http" in str(row["Foto URL"]):
                st.image(row["Foto URL"], width=100)
            else:
                st.write("📷 Foto tidak ditemukan")
        with cols[1]:
            st.markdown(f"### {row['Nama Lengkap']}")
            st.markdown(f"**ID**: {row['ID']}")
            st.markdown(f"**Ayah ID**: {row['Ayah ID'] or '-'}")
            st.markdown(f"**Ibu ID**: {row['Ibu ID'] or '-'}")
            st.markdown(f"**Gender**: {row['Gender']}")
            st.markdown(f"**Tanggal Lahir**: {row['Tanggal Lahir']}")
            st.markdown("---")
