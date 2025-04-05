import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def authenticate_google_sheets():
    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0")
    worksheet = sheet.get_worksheet(0)  # Akses sheet pertama
    
    records = worksheet.get_all_records()
    if not records:
        st.error("Data tidak ditemukan di Google Sheets.")
        return pd.DataFrame()
    
    data = pd.DataFrame(records)
    return data

def build_family_tree(data):
    G = nx.DiGraph()  # Directed graph, karena kita ingin memetakan hubungan orang tua-anak
    
    for _, row in data.iterrows():
        anak = row["Nama"]  # Asumsi kolom "Nama" untuk nama anggota
        ayah = row.get("Ayah ID")
        ibu = row.get("Ibu ID")
        
        if ayah:
            G.add_edge(ayah, anak)  # Hubungkan Ayah -> Anak
        if ibu:
            G.add_edge(ibu, anak)  # Hubungkan Ibu -> Anak
    
    return G

def display_family_tree():
    data = get_family_data()
    if not data.empty:
        G = build_family_tree(data)
        
        # Visualisasi pohon keluarga
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(G, seed=42)  # Layout untuk penataan node secara rapi
        nx.draw(G, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray")
        st.pyplot(plt)  # Tampilkan gambar dengan Streamlit

def main():
    st.title("Pohon Keluarga")
    st.write("Aplikasi ini menampilkan pohon keluarga berdasarkan data di Google Sheets.")
    
    display_family_tree()

if __name__ == "__main__":
    main()
