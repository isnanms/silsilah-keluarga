import streamlit as st
import pandas as pd
import gspread
import requests
from io import BytesIO
from google.oauth2.service_account import Credentials
from PIL import Image

# Set halaman Streamlit
st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Kolom pencarian ---
search_name = st.text_input("🔍 Cari Anggota Keluarga", "")

# --- Autentikasi ke Google Sheets dengan Scopes ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
json_key = st.secrets["gcp_service_account"]

credentials = Credentials.from_service_account_info(json_key, scopes=scope)
client = gspread.authorize(credentials)

# --- URL Google Sheet ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc"

# --- Ambil data ---
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Mapping ID ke Nama ---
id_to_nama = dict(zip(df["ID"], df["Nama Lengkap"]))

# --- Fungsi untuk memperbaiki orientasi foto ---
def perbaiki_orientasi(img):
    try:
        exif = img._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag == 274:  # Orientasi (Orientation)
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return img

# Fungsi untuk menampilkan gambar dengan ukuran yang lebih kecil dan proporsional
def tampilkan_gambar(img, width=150):
    st.image(img, use_container_width=True, width=width)  # Ukuran gambar 150px

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    # Filter pencarian berdasarkan nama
    if search_name.lower() in row['Nama Lengkap'].lower():
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                foto_url = row.get("Foto URL", "")
                if foto_url.startswith("http"):
                    try:
                        response = requests.get(foto_url)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        image = perbaiki_orientasi(image)  # Perbaiki orientasi foto
                        
                        # Menampilkan gambar dengan ukuran proporsional dan tombol fullscreen
                        st.image(image, caption="Klik untuk melihat foto HD", use_container_width=True)
                        
                        # Menambahkan tombol fullscreen
                        if st.button(f"Lihat HD {row['Nama Lengkap']}"):
                            st.image(image, caption=f"{row['Nama Lengkap']} (Foto HD)", use_container_width=True)
                        
                    except requests.exceptions.RequestException as e:
                        st.write("📷 Foto tidak dapat dimuat")
                else:
                    st.write("📷 Foto tidak ditemukan")
            with cols[1]:
                st.markdown(f"### {row['Nama Lengkap']}")

                ayah_nama = id_to_nama.get(row.get("Ayah ID"), "Tidak diketahui")
                ibu_nama = id_to_nama.get(row.get("Ibu ID"), "Tidak diketahui")

                if pd.notna(row.get("Ayah ID")) or pd.notna(row.get("Ibu ID")):
                    hubungan = f"Anak dari {ayah_nama} dan {ibu_nama}"
                else:
                    hubungan = "Tidak ada data orang tua"

                st.markdown(f"**{hubungan}**")
                st.markdown("---")
