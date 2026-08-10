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

@st.cache_data(ttl=60) # Refreshes every 60 seconds when Google Sheet updates
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# Helper function to render centered stats tables
def display_centered_table(df):
    formatted_df = df.copy()

    # Format numbers: integers as "0", decimals as "0.3"
    for col in formatted_df.columns:
        if col != "Player":
            formatted_df[col] = formatted_df[col].apply(
                lambda x: f"{int(x)}" if pd.notnull(x) and float(x).is_integer() 
                else (f"{x:.1f}" if pd.notnull(x) else "")
            )

    num_cols = len(formatted_df.columns)
    col_width = f"{100 / num_cols:.2f}%"

    styled_df = formatted_df.style.set_table_styles([
        {'selector': 'th', 'props': [('text-align', 'center !important'), ('width', col_width), ('max-width', col_width)]},
        {'selector': 'td', 'props': [('text-align', 'center !important'), ('width', col_width), ('max-width', col_width)]},
        {'selector': 'table', 'props': [('table-layout', 'fixed'), ('width', '100%')]}
    ])
    
    st.table(styled_df)

# Navigation Tabs
tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# --- PLAYER STATS TAB ---
with tab_stats:
    try:
        df = load_sheet("Socials_Player_Stats").iloc[:, :8]
        if "Player" in df.columns:
            df = df.dropna(subset=["Player"])

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

        # Interactive Leaderboard Table
        st.subheader("Player Leaderboard")
        display_centered_table(df)

    except Exception as e:
        st.error("Unable to load player stats. Ensure Google Sheet sharing is set to 'Anyone with the link can view'.")
        st.exception(e)

# --- MATCHES & PITCH VISUALISER TAB ---
with tab_matches:
    st.header("Match Center & Tactical Lineups")
    try:
        games_df = load_sheet("Socials_Games")

        # Match Selection Dropdown
        selected_game_id = st.selectbox(
            "Select Game to View Details & Lineup:",
            options=games_df["GameID"].unique()
        )

        game_data = games_df[games_df["GameID"] == selected_game_id].iloc[0]

        # Top Match Summary Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
        m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))
        m_col3.metric("⚽ Score", str(game_data.get("Result", "-")))
        m_col4.metric("🏆 MOTM", str(game_data.get("MOTM", "-")))

        st.divider()

        # Side-by-Side Pitch and Details
        pitch_col, details_col = st.columns([2, 1])

        with pitch_col:
            formation = str(game_data.get("Formation", "4-4-2")).strip()
            st.subheader(f"🟢 Starting Lineup ({formation})")

            # Custom styling for football pitch layout
            st.markdown("""
                <style>
                .pitch-container {
                    background-color: #2e7d32;
                    border: 4px solid #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                    color: white;
                    text-align: center;
                    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
                }
                .player-card {
                    background-color: rgba(255, 255, 255, 0.95);
                    color: #1b5e20;
                    font-weight: bold;
                    border-radius: 5px;
                    padding: 6px;
                    margin: 4px;
                    text-align: center;
                    font-size: 13px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }
                </style>
            """, unsafe_allow_html=True)

            # Helper function to get player name safely
            def get_p(pos_key):
                val = game_data.get(pos_key, None)
                if pd.notnull(val) and str(val).strip() not in ["", "-", "nan"]:
                    return str(val).strip()
                return None

            with st.container():
                st.markdown('<div class="pitch-container">', unsafe_allow_html=True)

                # --- GK (Always present) ---
                if get_p("GK"):
                    st.markdown(f'<div class="player-card">🧤 GK: {get_p("GK")}</div>', unsafe_allow_html=True)
                    st.write("")

                # --- DEFENCE LINE ---
                def_players = [("LB", get_p("LB")), ("CB1", get_p("CB1")), ("CB2", get_p("CB2")), ("RB", get_p("RB"))]
                active_def = [p for p in def_players if p[1]]
                if active_def:
                    d_cols = st.columns(len(active_def))
                    for idx, (label, name) in enumerate(active_def):
                        d_cols[idx].markdown(f'<div class="player-card">{label}: {name}</div>', unsafe_allow_html=True)
                    st.write("")

                # --- MIDFIELD LINE ---
                mid_players = [("CDM", get_p("CDM")), ("CM", get_p("CM")), ("CM1", get_p("CM1")), ("CM2", get_p("CM2")), ("CM3", get_p("CM3")), ("CAM", get_p("CAM"))]
                active_mid = [p for p in mid_players if p[1]]
                if active_mid:
                    m_cols = st.columns(len(active_mid))
                    for idx, (label, name) in enumerate(active_mid):
                        m_cols[idx].markdown(f'<div class="player-card">{label}: {name}</div>', unsafe_allow_html=True)
                    st.write("")

                # --- ATTACK LINE ---
                att_players = [("LW", get_p("LW")), ("ST1", get_p("ST1")), ("ST2", get_p("ST2")), ("RW", get_p("RW"))]
                active_att = [p for p in att_players if p[1]]
                if active_att:
                    a_cols = st.columns(len(active_att))
                    for idx, (label, name) in enumerate(active_att):
                        a_cols[idx].markdown(f'<div class="player-card">{label}: {name}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        with details_col:
            st.subheader("⚽ Goals & Assists")
            try:
                goals_df = load_sheet("Socials_Goals")
                # Support "Match ID" or "GameID" header name flexibly
                match_col = "Match ID" if "Match ID" in goals_df.columns else "GameID"
                match_goals = goals_df[goals_df[match_col].astype(str) == str(selected_game_id)]

                if not match_goals.empty:
                    for _, row in match_goals.iterrows():
                        scorer = row.get("Goalscorer", row.get("Scorer", "Unknown"))
                        assist = row.get("Assist", "")
                        
                        if pd.notnull(assist) and str(assist).strip() not in ["", "None", "-", "Unassisted", "nan"]:
                            st.write(f"• **{scorer}** ⚽ (🅰️ {assist})")
                        else:
                            st.write(f"• **{scorer}** ⚽")
                else:
                    st.info("No goals recorded for this match.")

            except Exception as e:
                st.info("Goal log loading...")

            st.divider()

            # Substitutes Breakdown
            st.subheader("👥 Substitutes")
            subs = [game_data.get(f"SUB{i}") for i in range(1, 7)]
            active_subs = [str(s).strip() for s in subs if pd.notnull(s) and str(s).strip() not in ["", "-", "nan"]]
            
            if active_subs:
                for sub in active_subs:
                    st.write(f"• {sub}")
            else:
                st.write("No substitutes listed.")

    except Exception as e:
        st.error("Error loading match data. Check sheet tab name 'Socials_Games'.")
        st.exception(e)

# --- NEWS TAB ---
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
