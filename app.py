import os
import pandas as pd
import streamlit as st
from st_gsheets_connection import GSheetsConnection

# ==========================================
# 1. PAGE CONFIGURATION & LOGO PATHS
# ==========================================
st.set_page_config(
    page_title="Derby Penguins App",
    page_icon="⚽",
    layout="wide"
)

# Update these relative paths to match your image files in your repository
LOGOS = {
    "Club": "logos/club_logo.jpg",
    "Socials": "logos/socials_logo.jpg",
    "Community": "logos/community_logo.jpg",
    "Penguins": "logos/penguins_logo.jpg"
}


# Helper function to display title with JPEG logo side-by-side cleanly
def render_page_header(title: str, logo_key: str):
    logo_path = LOGOS.get(logo_key)
    
    # Render with logo if the JPEG exists at path
    if logo_path and os.path.exists(logo_path):
        col1, col2 = st.columns([1, 10])
        with col1:
            st.image(logo_path, width=65)
        with col2:
            st.title(title)
    else:
        st.title(title)


# ==========================================
# 2. CACHED GSHEETS DATA LOADING (6 SHEETS)
# ==========================================
@st.cache_data(ttl=600)  # Caches for 10 mins for lightning-fast navigation
def load_all_team_data():
    """
    Fetches raw game and goal events for all 3 team divisions.
    """
    # Use GSheetsConnection class instead of string
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Load Socials
    socials_games = conn.read(worksheet="Socials_Games")
    socials_goals = conn.read(worksheet="Socials_Goals")
    
    # Load Community
    community_games = conn.read(worksheet="Community_Games")
    community_goals = conn.read(worksheet="Community_Goals")
    
    # Load Penguins
    penguins_games = conn.read(worksheet="Penguins_Games")
    penguins_goals = conn.read(worksheet="Penguins_Goals")
    
    # Tag each DataFrame with its division origin
    socials_games['Team'] = 'Socials'
    socials_goals['Team'] = 'Socials'
    
    community_games['Team'] = 'Community'
    community_goals['Team'] = 'Community'
    
    penguins_games['Team'] = 'Penguins'
    penguins_goals['Team'] = 'Penguins'

    return {
        "Socials": {"games": socials_games, "goals": socials_goals},
        "Community": {"games": community_games, "goals": community_goals},
        "Penguins": {"games": penguins_games, "goals": penguins_goals},
    }


# ==========================================
# 3. STATS & CONCATENATION LOGIC
# ==========================================
def get_club_combined_data(all_data):
    """
    Combines all three division datasets dynamically into master DataFrames.
    """
    club_games = pd.concat(
        [all_data["Socials"]["games"], all_data["Community"]["games"], all_data["Penguins"]["games"]],
        ignore_index=True
    )
    
    club_goals = pd.concat(
        [all_data["Socials"]["goals"], all_data["Community"]["goals"], all_data["Penguins"]["goals"]],
        ignore_index=True
    )
    
    return club_games, club_goals


def calculate_player_stats(games_df, goals_df):
    """
    Calculates Apps, Goals, Assists, and Total Contributions in memory.
    """
    # 1. Calculate Appearances
    if not games_df.empty and 'Player' in games_df.columns:
        apps = games_df.groupby('Player')['Game_ID'].nunique().reset_index(name='Apps')
    else:
        apps = pd.DataFrame(columns=['Player', 'Apps'])

    # 2. Calculate Goals
    if not goals_df.empty and 'Scorer' in goals_df.columns:
        goals = goals_df.groupby('Scorer').size().reset_index(name='Goals')
    else:
        goals = pd.DataFrame(columns=['Scorer', 'Goals'])

    # 3. Calculate Assists
    if not goals_df.empty and 'Assister' in goals_df.columns:
        valid_assists = goals_df[goals_df['Assister'].notna() & (goals_df['Assister'] != '')]
        assists = valid_assists.groupby('Assister').size().reset_index(name='Assists')
    else:
        assists = pd.DataFrame(columns=['Assister', 'Assists'])

    # Merge into a single master summary dataframe
    stats = pd.merge(apps, goals, left_on='Player', right_on='Scorer', how='outer')
    stats = pd.merge(stats, assists, left_on='Player', right_on='Assister', how='outer')

    # Consolidate player names and fill missing values with 0
    stats['Player'] = stats['Player'].fillna(stats['Scorer']).fillna(stats['Assister'])
    stats = stats[['Player', 'Apps', 'Goals', 'Assists']].fillna(0)

    # Cast metrics to integer
    stats['Apps'] = stats['Apps'].astype(int)
    stats['Goals'] = stats['Goals'].astype(int)
    stats['Assists'] = stats['Assists'].astype(int)

    # Total Goal Contributions (G + A)
    stats['Contributions'] = stats['Goals'] + stats['Assists']

    # Sort high-to-low by Contributions, then Goals, then Apps
    return stats.sort_values(by=['Contributions', 'Goals', 'Apps'], ascending=[False, False, True]).reset_index(drop=True)


# ==========================================
# 4. APP NAVIGATION & ROUTING
# ==========================================

# Fetch cached GSheet data
raw_data = load_all_team_data()

# Sidebar Navigation with Logo Header
st.sidebar.title("Navigation")
page_selection = st.sidebar.radio(
    "Select Division / View:",
    options=["Club Overview", "Socials", "Community", "Penguins"]
)

# ------------------------------------------
# PAGE 1: CLUB OVERVIEW (CONCATENATED)
# ------------------------------------------
if page_selection == "Club Overview":
    render_page_header("Derby Penguins - Club Overview", "Club")
    
    # Concatenate all division data on the fly
    club_games, club_goals = get_club_combined_data(raw_data)
    club_stats = calculate_player_stats(club_games, club_goals)
    
    # Metrics Bar
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches Played", club_games['Game_ID'].nunique() if not club_games.empty else 0)
    col2.metric("Total Club Goals", len(club_goals) if not club_goals.empty else 0)
    col3.metric("Active Players", len(club_stats))

    st.markdown("---")
    st.subheader("Master Club Leaderboard")
    st.dataframe(club_stats, use_container_width=True)

# ------------------------------------------
# PAGE 2: SOCIALS
# ------------------------------------------
elif page_selection == "Socials":
    render_page_header("Socials Division", "Socials")
    
    games = raw_data["Socials"]["games"]
    goals = raw_data["Socials"]["goals"]
    stats = calculate_player_stats(games, goals)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Matches Played", games['Game_ID'].nunique() if not games.empty else 0)
    col2.metric("Goals Scored", len(goals) if not goals.empty else 0)
    col3.metric("Squad Players", len(stats))

    st.markdown("---")
    st.subheader("Socials Player Stats")
    st.dataframe(stats, use_container_width=True)

# ------------------------------------------
# PAGE 3: COMMUNITY
# ------------------------------------------
elif page_selection == "Community":
    render_page_header("Community Division", "Community")
    
    games = raw_data["Community"]["games"]
    goals = raw_data["Community"]["goals"]
    stats = calculate_player_stats(games, goals)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Matches Played", games['Game_ID'].nunique() if not games.empty else 0)
    col2.metric("Goals Scored", len(goals) if not goals.empty else 0)
    col3.metric("Squad Players", len(stats))

    st.markdown("---")
    st.subheader("Community Player Stats")
    st.dataframe(stats, use_container_width=True)

# ------------------------------------------
# PAGE 4: PENGUINS
# ------------------------------------------
elif page_selection == "Penguins":
    render_page_header("Penguins Division", "Penguins")
    
    games = raw_data["Penguins"]["games"]
    goals = raw_data["Penguins"]["goals"]
    stats = calculate_player_stats(games, goals)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Matches Played", games['Game_ID'].nunique() if not games.empty else 0)
    col2.metric("Goals Scored", len(goals) if not goals.empty else 0)
    col3.metric("Squad Players", len(stats))

    st.markdown("---")
    st.subheader("Penguins Player Stats")
    st.dataframe(stats, use_container_width=True)
