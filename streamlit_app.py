import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image, ImageDraw
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

# --- Kolom pencarian ---
search = st.text_input("🔍 Cari nama anggota keluarga...").lower()
filtered_df = df[df["Nama Lengkap"].str.lower().str.contains(search)]

# --- Tambahkan komponen HTML + CSS untuk pop-up modal gambar ---
st.markdown("""
<style>
.popup-img {
  border-radius: 50%;
  width: 100px;
  cursor: pointer;
}
.modal {
  display: none;
  position: fixed;
  z-index: 999;
  padding-top: 60px;
  left: 0;
  top: 0;
  width: 100%%;
  height: 100%%;
  overflow: auto;
  background-color: rgba(0,0,0,0.8);
}
.modal-content {
  margin: auto;
  display: block;
  max-width: 90%%;
}
.close {
  position: absolute;
  top: 40px;
  right: 60px;
  color: white;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
}
</style>

<script>
function showModal(imgUrl) {
  const modal = document.getElementById("myModal");
  const modalImg = document.getElementById("modalImage");
  modal.style.display = "block";
  modalImg.src = imgUrl;
}

function closeModal() {
  document.getElementById("myModal").style.display = "none";
}
</script>

<div id="myModal" class="modal" onclick="closeModal()">
  <span class="close" onclick="closeModal()">&times;</span>
  <img class="modal-content" id="modalImage">
</div>
""", unsafe_allow_html=True)

# --- Tampilkan Data Anggota Keluarga ---
st.subheader("📜 Daftar Anggota Keluarga")

for index, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([1, 4])
        with cols[0]:
            foto_url = str(row.get("Foto URL", "")).strip()
            if "http" in foto_url:
                try:
                    response = requests.get(foto_url)
                    image = Image.open(BytesIO(response.content))
                    image = image.resize((100, 100))
                    image = bulatkan_foto(image)

                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    st.image(buffer.getvalue(), width=100)

                    # Tambahkan versi clickable untuk modal
                    st.markdown(
                        f"""
                        <img src="{foto_url}" class="popup-img" onclick="showModal('{foto_url}')">
                        """,
                        unsafe_allow_html=True
                    )
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
