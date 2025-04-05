import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ExifTags
import requests
from io import BytesIO
import graphviz

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

# --- Fungsi untuk memperbaiki orientasi foto ---
def perbaiki_orientasi(img):
    try:
        exif = img._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag == 274:  # EXIF orientation tag
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
        return img
    except (AttributeError, KeyError, IndexError):
        # Jika tidak ada EXIF data, return gambar asli
        return img

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
                    image = perbaiki_orientasi(image)  # Memperbaiki rotasi gambar
                    image = image.resize((120, 120))  # Ukuran tetap
                    image = bulatkan_foto(image)  # Membuat foto bulat
                    st.image(image, use_container_width=True)  # Foto ditampilkan dengan ukuran yang sesuai
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

# --- Membuat Pohon Keluarga ---
st.subheader("🌳 Pohon Keluarga")

dot = graphviz.Digraph(comment='Pohon Keluarga')

# Membuat relasi ayah, ibu, dan anak (misalnya 3 generasi)
for index, row in df.iterrows():
    nama = row['Nama Lengkap']
    ayah_id = row.get("Ayah ID")
    ibu_id = row.get("Ibu ID")

    # Menambahkan node untuk setiap individu
    dot.node(nama, nama)

    # Membuat hubungan dengan orang tua
    if pd.notna(ayah_id) and ayah_id in id_to_nama:
        dot.edge(id_to_nama[ayah_id], nama)
    if pd.notna(ibu_id) and ibu_id in id_to_nama:
        dot.edge(id_to_nama[ibu_id], nama)

# Menampilkan pohon keluarga
st.graphviz_chart(dot)
