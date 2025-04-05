import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Autentikasi Google Sheets ---
json_key = st.secrets["gcp_service_account"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(json_key, scopes=scope)
client = gspread.authorize(credentials)

# --- Ambil Data dari Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc"
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Mapping ID ke Nama ---
id_to_nama = dict(zip(df["ID"], df["Nama Lengkap"]))

# --- Tampilkan Data ---
st.subheader("📜 Daftar Anggota Keluarga")

for _, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 3])

        with cols[0]:
            foto_url = row.get("Foto URL", "")
            if isinstance(foto_url, str) and foto_url.startswith("http"):
                st.image(foto_url, width=100)
            else:
                st.write("📷 Foto tidak ditemukan")

        with cols[1]:
            st.markdown(f"### {row['Nama Lengkap']}")

            ayah_id = row.get("Ayah ID")
            ibu_id = row.get("Ibu ID")

            ayah_nama = id_to_nama.get(ayah_id, "Tidak diketahui") if pd.notna(ayah_id) else "Tidak diketahui"
            ibu_nama = id_to_nama.get(ibu_id, "Tidak diketahui") if pd.notna(ibu_id) else "Tidak diketahui"

            if pd.notna(ayah_id) or pd.notna(ibu_id):
                hubungan = f"Anak dari {ayah_nama} dan {ibu_nama}"
            else:
                hubungan = "Tidak ada data orang tua"

            st.markdown(f"**{hubungan}**")
            st.markdown("---")
