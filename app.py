import streamlit as st
import pandas as pd
from graphviz import Digraph

# URL Google Sheets CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/export?format=csv"
df = pd.read_csv(sheet_url)

st.title("🌳 Silsilah Keluarga Digital")

# Pilih root (pusat pohon)
root = st.selectbox("Pilih anggota keluarga untuk ditampilkan sebagai akar pohon:", df['Nama Lengkap'])

# Ambil ID root
root_row = df[df['Nama Lengkap'] == root].iloc[0]
root_id = root_row['ID']

# Buat graph
dot = Digraph()
dot.node(str(root_id), root_row['Nama Lengkap'])

# Tambahkan anak-anak secara rekursif
def tambah_anak(node_id):
    anak_df = df[(df['Ayah ID'] == node_id) | (df['Ibu ID'] == node_id)]
    for _, anak in anak_df.iterrows():
        dot.node(str(anak['ID']), anak['Nama Lengkap'])
        dot.edge(str(node_id), str(anak['ID']))
        tambah_anak(anak['ID'])  # rekursif ke cucu dst.

# Mulai membangun pohon dari root
tambah_anak(root_id)

# Tampilkan hasil visualisasi
st.graphviz_chart(dot)
