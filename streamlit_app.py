import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO
import base64
import uuid

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

# CSS dan JS Modal Pop-up
st.markdown("""
<style>
.modal {
  display: none;
  position: fixed;
  z-index: 9999;
  padding-top: 60px;
  left: 0; top: 0;
  width: 100%; height: 100%;
  overflow: auto; background-color: rgba(0,0,0,0.8);
}
.modal-content {
  margin: auto;
  display: block;
  max-width: 80%;
  border-radius: 12px;
}
.close {
  position: absolute;
  top: 20px; right: 35px;
  color: #fff;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
}
</style>
<script>
function openModal(id, url) {
    var modal = document.getElementById("modal-" + id);
    var img = document.getElementById("img-" + id);
    img.src = url;
    modal.style.display = "block";
}
function closeModal(id) {
    var modal = document.getElementById("modal-" + id);
    modal.style.display = "none";
}
</script>
""", unsafe_allow_html=True)

# Tampilkan anggota keluarga
for index, row in df.iterrows():
    with st.container():
        cols = st.columns([1, 4])
        with cols[0]:
            foto_url = str(row.get("Foto URL", "")).strip()
            if "http" in foto_url:
                try:
                    response = requests.get(foto_url)
                    image = Image.open(BytesIO(response.content))
                    image = ImageOps.exif_transpose(image)
                    image = image.resize((110, 110), Image.Resampling.LANCZOS)
                    image = bulatkan_foto(image)

                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    encoded = base64.b64encode(buffered.getvalue()).decode()

                    unique_id = str(uuid.uuid4())

                    st.markdown(f"""
                    <img src="data:image/png;base64,{encoded}" style="border-radius: 50%; cursor: pointer;" width="110" height="110"
                         onclick="openModal('{unique_id}', '{foto_url}')">
                    <div id="modal-{unique_id}" class="modal" onclick="closeModal('{unique_id}')">
                        <span class="close" onclick="closeModal('{unique_id}')">&times;</span>
                        <img class="modal-content" id="img-{unique_id}">
                    </div>
                    """, unsafe_allow_html=True)
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
