import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def authenticate_google_sheets():
    # Accessing the secrets
    creds = st.secrets["service_account"]
    credentials = Credentials.from_service_account_info(creds)

    # Use credentials to authenticate and access Google Sheets
    gc = gspread.authorize(credentials)
    return gc

# Example: Retrieve sheet data
def get_family_data():
    client = authenticate_google_sheets()
    sheet = client.open("FamilyData").sheet1
    data = sheet.get_all_records()
    return data

def main():
    data = get_family_data()
    st.write(data)  # Display the sheet data for testing

if __name__ == "__main__":
    main()
