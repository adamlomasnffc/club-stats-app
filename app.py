import streamlit as st
import pandas as pd

# Page setup for mobile optimization
st.set_page_config(page_title="Club Stats Hub", page_icon="⚽", layout="wide")

st.title("⚽ Club Stats Hub")

# --- CONFIGURATION ---
# Replace this string with your actual Google Sheet ID
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"

# Helper function to read a specific tab from Google Sheets as CSV
@st.cache_data(ttl=300) # Caches data for 5 minutes so it loads instantly
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)

# Navigation Tabs
tab_news, tab_club, tab_t1, tab_t2, tab_t3 = st.tabs([
    "📰 News", "🏆 Club", "🥇 Team 1", "🥈 Team 2", "🥉 Team 3"
])

# --- NEWS TAB ---
with tab_news:
    st.header("Latest Club News")
    try:
        news_df = load_sheet("News")
        for idx, row in news_df.iterrows():
            st.subheader(row.get("Title", "Announcement"))
            st.write(row.get("Content", ""))
            st.divider()
    except Exception:
        st.info("Add a 'News' tab in Google Sheets with columns: Title, Content")

# --- CLUB OVERVIEW TAB ---
with tab_club:
    st.header("Club Overview & Leaders")
    try:
        club_df = load_sheet("Club_Overview")
        st.dataframe(club_df, use_container_width=True)
    except Exception:
        st.info("Add a 'Club_Overview' tab in Google Sheets to display overall stats.")

# --- TEAM 1 TAB ---
with tab_t1:
    st.header("Team 1 Squad Stats")
    try:
        t1_df = load_sheet("Team_1")
        st.dataframe(t1_df, use_container_width=True)
    except Exception:
        st.info("Add a 'Team_1' tab in Google Sheets.")

# --- TEAM 2 TAB ---
with tab_t2:
    st.header("Team 2 Squad Stats")
    try:
        t2_df = load_sheet("Team_2")
        st.dataframe(t2_df, use_container_width=True)
    except Exception:
        st.info("Add a 'Team_2' tab in Google Sheets.")

# --- TEAM 3 TAB ---
with tab_t3:
    st.header("Team 3 Squad Stats")
    try:
        t3_df = load_sheet("Team_3")
        st.dataframe(t3_df, use_container_width=True)
    except Exception:
        st.info("Add a 'Team_3' tab in Google Sheets.")
