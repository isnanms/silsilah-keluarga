import streamlit as st
import graphviz
from graphviz import Digraph

# Data keluarga yang sudah diolah
data = [
    {'ID': 1, 'Nama': 'Bapak A', 'Ayah ID': None, 'Ibu ID': None},
    {'ID': 2, 'Nama': 'Ibu A', 'Ayah ID': None, 'Ibu ID': None},
    {'ID': 3, 'Nama': 'Anak A1', 'Ayah ID': 1, 'Ibu ID': 2},
    {'ID': 4, 'Nama': 'Anak A2', 'Ayah ID': 1, 'Ibu ID': 2},
    {'ID': 5, 'Nama': 'Cucu A1', 'Ayah ID': 3, 'Ibu ID': None},
]

# Membuat pohon keluarga
dot = Digraph(comment='Pohon Keluarga')

# Menambahkan node anggota keluarga
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
