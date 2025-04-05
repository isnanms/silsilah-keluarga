import streamlit as st
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Set up Google Sheets connection
def authenticate_google_sheets():
    # Load credentials from the service account file
    creds = None
    if creds is None or not creds.valid:
        creds = Credentials.from_service_account_file(
            'path-to-your-service-account.json', 
            scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
    return gspread.authorize(creds)

# Get data from Google Sheets
def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1__VDkWvS-FdSHpOhNnLvqej4ggFKU1xqJnobDlTeppc/edit?gid=0#gid=0")
    worksheet = sheet.get_worksheet(0)  # Access the first sheet
    data = pd.DataFrame(worksheet.get_all_records())
    return data

# Create family tree
def create_family_tree(data):
    G = nx.DiGraph()  # Directed graph to show family tree structure

    for index, row in data.iterrows():
        child = row['Nama']
        father = row['Ayah']
        mother = row['Ibu']
        
        # Add nodes and edges
        G.add_node(child)
        if father:
            G.add_edge(father, child)
        if mother:
            G.add_edge(mother, child)

    return G

# Display family tree
def display_family_tree():
    data = get_family_data()
    G = create_family_tree(data)
    
    # Draw the family tree using NetworkX and Matplotlib
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G, seed=42)  # Layout for better visualization
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold")
    
    st.pyplot(plt)  # Display the tree in Streamlit app

# Main function to run the app
def main():
    st.title("Pohon Keluarga")
    st.write("Aplikasi ini menampilkan pohon keluarga berdasarkan data di Google Sheets.")
    
    display_family_tree()

if __name__ == "__main__":
    main()
