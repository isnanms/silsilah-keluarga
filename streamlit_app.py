import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ExifTags
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

# --- Fungsi untuk membulatkan gambar ---
def bulatkan_foto(img):
    img = img.convert("RGBA")
    size = img.size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

# --- Fungsi untuk memperbaiki rotasi gambar jika perlu ---
def perbaiki_rotasi(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except:
        pass
    return image

# --- Kolom pencarian ---
search_query = st.text_input("🔎 Cari nama anggota keluarga")

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

filtered_df = df[df["Nama Lengkap"].str.contains(search_query, case=False, na=False)]

for index, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([1, 4])
        with cols[0]:
            foto_url = str(row.get("Foto URL", "")).strip()
            if "http" in foto_url:
                try:
                    response = requests.get(foto_url)
                    image = Image.open(BytesIO(response.content))
                    image = perbaiki_rotasi(image)
                    image = image.resize((100, 100))
                    image = bulatkan_foto(image)
                    st.image(image)
                    
                    # Tombol Lihat HD di bawah gambar
                    hd_url = foto_url
                    st.markdown(f"<div style='text-align: right; margin-top: -10px;'><a href='{hd_url}' target='_blank'>🔍 Lihat HD</a></div>", unsafe_allow_html=True)
                except:
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
