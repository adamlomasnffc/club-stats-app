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
    
    # Keep strictly the first 8 columns (Columns A to H) to remove extra empty columns
    df = df.iloc[:, :8]
    
    # Drop rows where Player name is empty
    if "Player" in df.columns:
        df = df.dropna(subset=["Player"])
        
    return df

# Navigation Tabs
tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# --- PLAYER STATS TAB ---
with tab_stats:
    try:
        df = load_sheet("Socials_Player_Stats")
        
        # Top KPI Metrics Cards at the top
        top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
        top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
        top_involvements = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚽ Top Scorer", f"{top_scorer['Player']}", f"{int(top_scorer['Goals'])} Goals")
        with col2:
            st.metric("🅰️ Top Assister", f"{top_assister['Player']}", f"{int(top_assister['Assists'])} Assists")
        with col3:
            st.metric("🔥 Top Contributor", f"{top_involvements['Player']}", f"{int(top_involvements['Goal Involvements'])} G+A")

        st.divider()

        # Search Bar for Players
        search_query = st.text_input("🔍 Search Player Name", "")
        if search_query:
            df = df[df["Player"].str.contains(search_query, case=False, na=False)]

        # Interactive Leaderboard Table (Exact sheet headers, no blank columns)
        st.subheader("Player Leaderboard")
        {col: st.column_config.Column(alignment="center") for col in df.columns}

    except Exception as e:
        st.error("Unable to load player stats. Ensure Google Sheet sharing is set to 'Anyone with the link can view'.")
        st.exception(e)

# --- MATCHES TAB ---
with tab_matches:
    st.header("Match Results & Fixtures")
    try:
        matches_df = load_sheet("Socials_Matches")
        st.dataframe(matches_df, use_container_width=True, hide_index=True)
    except Exception:
        st.info("Set up your 'Socials_Matches' tab to display match logs here!")

# --- NEWS TAB ---
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
