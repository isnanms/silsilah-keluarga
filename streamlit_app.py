import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO

st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Autentikasi ke Google Sheets ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
json_key = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(json_key, scopes=scope)
client = gspread.authorize(credentials)

# --- Ambil data dari Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc"
spreadsheet = client.open_by_url(sheet_url)
sheet = spreadsheet.worksheet("Data")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Mapping ID ke Nama ---
id_to_nama = dict(zip(df["ID"], df["Nama Lengkap"]))

# --- Fungsi untuk membuat foto jadi bulat ---
def bulatkan_foto(img):
    img = img.convert("RGBA")
    size = img.size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 4])
        with cols[0]:
            foto_url = str(row.get("Foto URL", "")).strip()
            if "http" in foto_url:
                try:
                    response = requests.get(foto_url)
                    image = Image.open(BytesIO(response.content))
                    image = ImageOps.exif_transpose(image)  # Koreksi orientasi
                    image = image.resize((130, 130), Image.Resampling.LANCZOS)  # Ukuran kecil & tajam
                    image = bulatkan_foto(image)
                    
                    # Simpan sementara di buffer
                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    st.markdown(
                        f'<a href="{foto_url}" target="_blank">'
                        f'<img src="data:image/png;base64,{buffer.getvalue().hex()}" '
                        f'style="border-radius: 50%; width: 130px; height: 130px;" /></a>',
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.write("❌ Gagal memuat gambar")
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
