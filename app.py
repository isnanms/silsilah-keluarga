import streamlit as st
import pandas as pd
from graphviz import Digraph

# URL Google Sheets dalam format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/export?format=csv"

# Membaca data dari Google Sheets
df = pd.read_csv(sheet_url)

st.title("🌳 Silsilah Keluarga Digital")

# Input: Pilih nama anggota keluarga
nama_dicari = st.selectbox("Pilih nama anggota keluarga:", df['Nama Lengkap'])

# Data anggota terpilih
orang = df[df['Nama Lengkap'] == nama_dicari].iloc[0]
st.subheader(f"👤 {orang['Nama Lengkap']} (ID: {orang['ID']})")

# Menampilkan foto jika tersedia
if pd.notna(orang['Foto URL']) and orang['Foto URL'].startswith('http'):
    st.image(orang['Foto URL'], caption=orang['Nama Lengkap'], use_column_width=True)
else:
    st.write("Foto tidak tersedia.")

# Menampilkan informasi lainnya (Ayah, Ibu, Anak-anak) seperti sebelumnya
