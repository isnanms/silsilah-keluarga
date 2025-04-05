import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from graphviz import Digraph

# Setup kredensial dan akses ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Akses ke Google Sheet (gunakan URL Sheet atau ID Sheet)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0'  # Ganti dengan URL spreadsheet kamu
sheet = client.open_by_url(spreadsheet_url).sheet1

# Mengambil data dari sheet (asumsi data ada di kolom ID, Nama, Ayah ID, Ibu ID)
data = sheet.get_all_records()

# Membuat pohon keluarga
dot = Digraph(comment='Pohon Keluarga')

# Menambahkan node anggota keluarga ke pohon
for anggota in data:
    dot.node(str(anggota['ID']), anggota['Nama'])

# Menambahkan hubungan antar anggota keluarga (ayah dan ibu)
for anggota in data:
    if anggota['Ayah ID']:
        dot.edge(str(anggota['Ayah ID']), str(anggota['ID']), label="Ayah")
    if anggota['Ibu ID']:
        dot.edge(str(anggota['Ibu ID']), str(anggota['ID']), label="Ibu")

# Render pohon keluarga
st.title('Pohon Keluarga')
st.write('Menampilkan hubungan keluarga dalam pohon keluarga')
st.graphviz_chart(dot)
