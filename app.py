import streamlit as st
import pandas as pd

# URL Google Sheets dalam format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/export?format=csv"

# Membaca data
df = pd.read_csv(sheet_url)

st.title("🌳 Silsilah Keluarga Digital")

# Input: Pilih nama
nama_dicari = st.selectbox("Pilih nama anggota keluarga:", df['Nama Lengkap'])

# Data anggota terpilih
orang = df[df['Nama Lengkap'] == nama_dicari].iloc[0]
st.subheader(f"👤 {orang['Nama Lengkap']} (ID: {orang['ID']})")

# Cek Ayah dan Ibu
ayah = df[df['ID'] == orang['Ayah ID']].iloc[0]['Nama Lengkap'] if orang['Ayah ID'] in df['ID'].values else "Tidak diketahui"
ibu = df[df['ID'] == orang['Ibu ID']].iloc[0]['Nama Lengkap'] if orang['Ibu ID'] in df['ID'].values else "Tidak diketahui"

st.write(f"👨 Ayah: {ayah}")
st.write(f"👩 Ibu: {ibu}")

# Cek Anak-anak
anak = df[(df['Ayah ID'] == orang['ID']) | (df['Ibu ID'] == orang['ID'])]

if not anak.empty:
    st.write("🧒 Anak-anak:")
    for i, row in anak.iterrows():
        st.write(f"• {row['Nama Lengkap']} (ID: {row['ID']})")
else:
    st.write("🧒 Tidak ada anak yang terdaftar")
