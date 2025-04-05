import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

def authenticate_google_sheets():
    try:
        creds = st.secrets["service_account"]
        credentials = Credentials.from_service_account_info(creds)

        # Try refreshing the token to make sure it's valid
        credentials.refresh(Request())

        # Use credentials to authenticate
        client = build('sheets', 'v4', credentials=credentials)
        return client

    except RefreshError as e:
        st.error(f"Authentication failed: {str(e)}")
        return None

def get_family_data():
    client = authenticate_google_sheets()
    if not client:
        return []

    # Try to open the sheet and fetch data
    try:
        sheet = client.spreadsheets().values().get(spreadsheetId='your-spreadsheet-id', range="Sheet1").execute()
        return sheet['values']
    except Exception as e:
        st.error(f"Failed to retrieve sheet data: {str(e)}")
        return []

def main():
    data = get_family_data()
    if data:
        st.write(data)  # Display the sheet data for testing
    else:
        st.error("No data available due to authentication or access issues.")

if __name__ == "__main__":
    main()
