import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import base64
import streamlit.components.v1 as components

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

# --- Kolom Pencarian ---
search_query = st.text_input("🔍 Cari Nama Anggota Keluarga").lower()
filtered_df = df[df["Nama Lengkap"].str.lower().str.contains(search_query)]

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

# CSS + JS untuk modal pop-up
modal_code = """
<style>
.modal {
  display: none;
  position: fixed;
  z-index: 9999;
  padding-top: 5%;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.9);
}
.modal-content {
  margin: auto;
  display: block;
  max-width: 90%;
  max-height: 90%;
  border-radius: 10px;
}
.close {
  position: absolute;
  top: 30px;
  right: 50px;
  color: #fff;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
}
</style>
<script>
function showModal(src) {
  var modal = document.getElementById("imgModal");
  var modalImg = document.getElementById("modalImg");
  modal.style.display = "block";
  modalImg.src = src;
}
function closeModal() {
  var modal = document.getElementById("imgModal");
  modal.style.display = "none";
}
</script>
<div id="imgModal" class="modal">
  <span class="close" onclick="closeModal()">&times;</span>
  <img class="modal-content" id="modalImg">
</div>
"""

components.html(modal_code, height=0)

for index, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([1, 4])
        with cols[0]:
            foto_url = str(row.get("Foto URL", "")).strip()
            if "http" in foto_url:
                try:
                    response = requests.get(foto_url)
                    image = Image.open(BytesIO(response.content)).convert("RGB")
                    image = image.resize((110, 110))
                    image = bulatkan_foto(image)
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    img_html = f'''
                    <img src="data:image/png;base64,{img_str}" width="100" height="100"
                         style="border-radius: 50%; cursor: pointer;" 
                         onclick="showModal('{foto_url}')"/>
                    '''
                    components.html(img_html, height=110)
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
