import streamlit as st
import pandas as pd

# Page Configuration for Mobile Optimization
st.set_page_config(
    page_title="Penguins Master Stats",
    page_icon="🐧",
    layout="wide"
)

st.title("🐧 Penguins Club Stats")

# --- SPREADSHEET CONFIGURATION ---
SPREADSHEET_ID = "19wTGruEyetdVNhfjkyVqLDueyV9joVtRsI51RAqurjA"

@st.cache_data(ttl=60) # Refreshes every 60 seconds when you update the Google Sheet
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    
    # Keep strictly the first 8 columns (Columns A to H)
    df = df.iloc[:, :8]
    
    # Drop rows where Player name is empty
    if "Player" in df.columns:
        df = df.dropna(subset=["Player"])
        
    return df

# Helper function to render tables with strictly centered headers and data cells
def display_centered_table(df):
    styled_df = df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center !important')]},
        {'selector': 'td', 'props': [('text-align', 'center !important')]}
    ])
    st.table(styled_df)

# Navigation Tabs
tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# --- PLAYER STATS TAB ---
with tab_stats:
    try:
        df = load_sheet("Socials_Player_Stats")
        
        # Calculate 4 Top KPI Metrics
        top_apps = df.sort_values(by="Appearances", ascending=False).iloc[0]
        top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
        top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
        top_involvements = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]

        # 4 Metric Columns Layout
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏃 Most Appearances", f"{top_apps['Player']}", f"{int(top_apps['Appearances'])} Apps")
        with col2:
            st.metric("⚽ Top Scorer", f"{top_scorer['Player']}", f"{int(top_scorer['Goals'])} Goals")
        with col3:
            st.metric("🅰️ Top Assister", f"{top_assister['Player']}", f"{int(top_assister['Assists'])} Assists")
        with col4:
            st.metric("🔥 Top Contributor", f"{top_involvements['Player']}", f"{int(top_involvements['Goal Involvements'])} G+A")

        st.divider()

        # Search Bar for Players
        search_query = st.text_input("🔍 Search Player Name", "")
        if search_query:
            df = df[df["Player"].str.contains(search_query, case=False, na=False)]

        # Interactive Leaderboard Table (Centrally aligned headers & cells)
        st.subheader("Player Leaderboard")
        display_centered_table(df)

    except Exception as e:
        st.error("Unable to load player stats. Ensure Google Sheet sharing is set to 'Anyone with the link can view'.")
        st.exception(e)

# --- MATCHES TAB ---
with tab_matches:
    st.header("Match Results & Fixtures")
    try:
        matches_df = load_sheet("Socials_Matches")
        display_centered_table(matches_df)
    except Exception:
        st.info("Set up your 'Socials_Matches' tab to display match logs here!")

# --- NEWS TAB ---
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
