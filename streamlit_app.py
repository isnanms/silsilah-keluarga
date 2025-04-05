from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

def authenticate_google_sheets():
    # Ambil kredensial dari file JSON (disesuaikan dengan path file JSON milikmu)
    creds_json = st.secrets["service_account"]  # Ganti dengan nama secret sesuai di Streamlit
    creds = Credentials.from_service_account_info(creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

    # Refresh kredensial jika sudah kadaluarsa
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Autentikasi dengan Google Sheets
    client = gspread.authorize(creds)
    return client

def get_family_data():
    # Mengambil data dari Google Sheets
    client = authenticate_google_sheets()
    sheet = client.open("Sheet1").sheet1  # Ganti dengan nama sheet sesuai kebutuhan
    data = pd.DataFrame(sheet.get_all_records())  # Mengambil data dalam bentuk DataFrame
    return data

def build_family_tree(data):
    # Membuat pohon keluarga berdasarkan data
    G = nx.DiGraph()  # Membuat directed graph
    
    for index, row in data.iterrows():
        anak = row["Nama Lengkap"]  # Kolom "Nama Lengkap" untuk nama anggota keluarga
        ayah_id = row["Ayah ID"]  # Kolom "Ayah ID" untuk mencari ID ayah
        ibu_id = row["Ibu ID"]  # Kolom "Ibu ID" untuk mencari ID ibu
        
        G.add_node(anak)  # Menambahkan anggota keluarga ke graph

        if pd.notnull(ayah_id):  # Jika ada ID ayah
            ayah = data[data["ID"] == ayah_id]["Nama Lengkap"].values[0]
            G.add_edge(ayah, anak)  # Menambahkan hubungan antara ayah dan anak

        if pd.notnull(ibu_id):  # Jika ada ID ibu
            ibu = data[data["ID"] == ibu_id]["Nama Lengkap"].values[0]
            G.add_edge(ibu, anak)  # Menambahkan hubungan antara ibu dan anak

    return G

def display_family_tree():
    data = get_family_data()  # Mendapatkan data keluarga
    G = build_family_tree(data)  # Membangun pohon keluarga

    # Menampilkan pohon keluarga menggunakan networkx
    st.write("Pohon Keluarga")
    nx.draw(G, with_labels=True, font_size=8, node_size=2000, node_color="lightblue", font_weight="bold")
    
def main():
    display_family_tree()

if __name__ == "__main__":
    main()
