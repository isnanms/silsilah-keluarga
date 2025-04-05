import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Autentikasi ke Google Sheets menggunakan Streamlit Secrets ---
json_key = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(json_key)
client = gspread.authorize(credentials)

# --- Ambil Data dari Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc"
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Mapping ID ke Nama untuk lookup ayah/ibu ---
id_to_nama = dict(zip(df["ID"], df["Nama Lengkap"]))

# --- Fungsi konversi link Google Drive agar bisa ditampilkan ---
def convert_drive_link(url):
    if "drive.google.com" in url:
        if "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        elif "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        else:
            return url
        return f"https://drive.google.com/uc?id={file_id}"
    return url

# --- Tampilkan Data Anggota ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            foto_url = convert_drive_link(row.get("Foto URL", ""))
            if "http" in foto_url:
                st.image(foto_url, width=100)
            else:
                st.write("📷 Foto tidak ditemukan")
        with cols[1]:
            st.markdown(f"### {row['Nama Lengkap']}")

            ayah_nama = id_to_nama.get(row["Ayah ID"], "Tidak diketahui")
            ibu_nama = id_to_nama.get(row["Ibu ID"], "Tidak diketahui")

            if pd.notna(row["Ayah ID"]) or pd.notna(row["Ibu ID"]):
                hubungan = f"Anak dari {ayah_nama} dan {ibu_nama}"
            else:
                hubungan = "Tidak ada data orang tua"

            st.markdown(f"**{hubungan}**")
            st.markdown("---")
