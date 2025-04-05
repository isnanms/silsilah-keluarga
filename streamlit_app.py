import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Autentikasi Google Sheets
def authenticate_google_sheets():
    creds_json = st.secrets["service_account"]  # Ganti sesuai dengan nama secret kamu
    creds_dict = json.loads(creds_json)
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope=["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    return client

# Ambil data keluarga dari Google Sheets
def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0")
    worksheet = sheet.get_worksheet(0)  # Akses sheet pertama
    
    records = worksheet.get_all_records()
    if not records:
        st.error("Data tidak ditemukan di Google Sheets.")
        return pd.DataFrame()
    
    data = pd.DataFrame(records)
    
    # Tampilkan nama-nama kolom untuk pengecekan
    st.write("Nama-nama kolom di data:", data.columns)
    
    return data

# Membangun pohon keluarga dengan NetworkX
def build_family_tree(data):
    G = nx.DiGraph()  # Menggunakan directed graph untuk menunjukkan arah (relasi ayah/ibu)
    
    for _, row in data.iterrows():
        anak = row["Nama Lengkap"]
        ayah_id = row.get("Ayah ID")
        ibu_id = row.get("Ibu ID")
        
        # Menambahkan hubungan anak dengan ayah dan ibu (jika ada)
        if pd.notnull(ayah_id):
            ayah = data.loc[data["ID"] == ayah_id, "Nama Lengkap"].values[0]
            G.add_edge(ayah, anak, relationship="father")
        
        if pd.notnull(ibu_id):
            ibu = data.loc[data["ID"] == ibu_id, "Nama Lengkap"].values[0]
            G.add_edge(ibu, anak, relationship="mother")
    
    return G

# Menampilkan pohon keluarga
def display_family_tree():
    data = get_family_data()
    if data.empty:
        return
    
    G = build_family_tree(data)
    
    # Gambar pohon keluarga
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
    plt.title("Pohon Keluarga")
    st.pyplot()

# Main function untuk menjalankan aplikasi
def main():
    st.title("Aplikasi Pohon Keluarga")
    display_family_tree()

if __name__ == "__main__":
    main()
