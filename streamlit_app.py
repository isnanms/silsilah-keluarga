import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ExifTags
import requests
from io import BytesIO
import graphviz
import os

# Set halaman Streamlit
st.set_page_config(page_title="Silsilah Keluarga", layout="wide")
st.title("🌳 Silsilah Keluarga Besar")

# --- Kolom pencarian ---
search_name = st.text_input("🔍 Cari Anggota Keluarga", "")

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
        # Mengambil metadata EXIF
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
        # Jika tidak ada EXIF
        pass
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

# --- Fungsi untuk membuat pohon keluarga dengan Graphviz ---
def create_family_tree():
    dot = graphviz.Digraph(comment='Pohon Keluarga', format='png')
    
    # Menambahkan node untuk keluarga
    dot.node('A', 'Bapak')
    dot.node('B', 'Ibu')
    dot.node('C', 'Anak')

    # Menambahkan hubungan antara node
    dot.edge('A', 'C')
    dot.edge('B', 'C')

    return dot

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in df.iterrows():
    # Filter berdasarkan pencarian nama
    if search_name.lower() in row['Nama Lengkap'].lower():
        with st.container():
            cols = st.columns([1, 4])
            with cols[0]:
                foto_url = str(row.get("Foto URL", "")).strip()
                if "http" in foto_url:
                    try:
                        response = requests.get(foto_url)
                        image = Image.open(BytesIO(response.content))
                        image = perbaiki_orientasi(image)  # Perbaiki orientasi foto
                        image = image.resize((100, 100))  # Ukuran foto lebih kecil
                        image = bulatkan_foto(image)
                        st.image(image, use_container_width=True)  # Menampilkan foto dengan ukuran yang pas
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

# --- Tampilkan Pohon Keluarga ---
st.subheader("🌳 Pohon Keluarga")

# Tentukan folder untuk menyimpan pohon keluarga
output_path = '/mnt/data/family_tree.png'

# Periksa jika folder belum ada, buat folder terlebih dahulu
if not os.path.exists('/mnt/data'):
    os.makedirs('/mnt/data')

# Buat pohon keluarga dan render
family_tree = create_family_tree()
family_tree.render(filename=output_path, view=False)  # Rendering ke file PNG
st.image(output_path, use_container_width=True)  # Menampilkan pohon keluarga
