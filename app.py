import streamlit as st
import pandas as pd
import re

# Page Configuration for Mobile Optimization
st.set_page_config(
    page_title="Penguins Master Stats",
    page_icon="🐧",
    layout="wide"
)

st.title("🐧 Penguins Club Stats")

# --- SPREADSHEET CONFIGURATION ---
SPREADSHEET_ID = "19wTGruEyetdVNhfjkyVqLDueyV9joVtRsI51RAqurjA"

@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# Helper to clean position titles (e.g., 'CB1' -> 'CB', 'ST2' -> 'ST')
def clean_position_label(pos_key):
    return re.sub(r'\d+$', '', pos_key)

# Navigation Tabs
tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# --- PLAYER STATS TAB ---
with tab_stats:
    try:
        df = load_sheet("Socials_Player_Stats").iloc[:, :8]
        if "Player" in df.columns:
            df = df.dropna(subset=["Player"])

        # Top KPI Metric Cards
        top_apps = df.sort_values(by="Appearances", ascending=False).iloc[0]
        top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
        top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
        top_involvements = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]

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

        # Custom Filters & Interactive Leaderboard
        st.subheader("Player Leaderboard")
        st.caption("💡 Click any column header to sort. Use the controls below to filter.")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            search_query = st.text_input("🔍 Search Player Name", "")
        with f_col2:
            min_apps = st.slider("Filter by Minimum Appearances", 0, int(df["Appearances"].max()), 0)

        # Apply Filters
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Player"].str.contains(search_query, case=False, na=False)]
        if min_apps > 0:
            filtered_df = filtered_df[filtered_df["Appearances"] >= min_apps]

        # Fully interactive, sortable, and filterable table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.Column(alignment="center") for col in filtered_df.columns
            }
        )

    except Exception as e:
        st.error("Unable to load player stats sheet.")
        st.exception(e)

# --- MATCHES & PITCH VISUALISER TAB ---
with tab_matches:
    st.header("Match Center & Tactical Lineups")
    try:
        games_df = load_sheet("Socials_Games")

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

        pitch_col, details_col = st.columns([2, 1])

        with pitch_col:
            formation = str(game_data.get("Formation", "4-4-2")).strip()
            st.subheader(f"🟢 Starting Lineup ({formation})")

            # Custom pitch CSS with white pitch markings and grass gradient
            st.markdown("""
                <style>
                .football-pitch {
                    background: #2e7d32;
                    background-image: 
                        linear-gradient(to bottom, rgba(255,255,255,0.3) 2px, transparent 2px),
                        radial-gradient(circle, transparent 40%, rgba(0,0,0,0.1) 100%);
                    border: 4px solid #ffffff;
                    border-radius: 12px;
                    padding: 25px 15px;
                    position: relative;
                    box-shadow: inset 0 0 20px rgba(0,0,0,0.4);
                }
                .pitch-line-halfway {
                    border-top: 2px solid rgba(255, 255, 255, 0.7);
                    margin: 15px 0;
                }
                .player-card {
                    background-color: #ffffff;
                    color: #1b5e20;
                    font-weight: 800;
                    border-radius: 6px;
                    padding: 8px 4px;
                    margin: 4px;
                    text-align: center;
                    font-size: 13px;
                    box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                    border: 1px solid #c8e6c9;
                }
                .pos-label {
                    color: #2e7d32;
                    font-size: 11px;
                    display: block;
                    text-transform: uppercase;
                }
                </style>
            """, unsafe_allow_html=True)

            def get_player(pos):
                val = game_data.get(pos, None)
                if pd.notnull(val) and str(val).strip() not in ["", "-", "nan"]:
                    return str(val).strip()
                return None

            # Group positions into tactical bands
            def_keys = ["LWB", "LB", "CB1", "CB2", "CB3", "RB", "RWB"]
            mid_keys = ["LM", "CDM", "CM", "CM1", "CM2", "CM3", "CAM", "RM"]
            att_keys = ["LW", "ST1", "ST2", "ST3", "RW"]

            gk = get_player("GK")
            defenders = [(k, get_player(k)) for k in def_keys if get_player(k)]
            midfielders = [(k, get_player(k)) for k in mid_keys if get_player(k)]
            attackers = [(k, get_player(k)) for k in att_keys if get_player(k)]

            with st.container():
                st.markdown('<div class="football-pitch">', unsafe_allow_html=True)

                # --- GOALKEEPER ---
                if gk:
                    st.markdown(f'<div class="player-card"><span class="pos-label">GK</span>🧤 {gk}</div>', unsafe_allow_html=True)
                    st.write("")

                # --- DEFENDERS ---
                if defenders:
                    d_cols = st.columns(len(defenders))
                    for idx, (pos_key, p_name) in enumerate(defenders):
                        clean_pos = clean_position_label(pos_key)
                        d_cols[idx].markdown(f'<div class="player-card"><span class="pos-label">{clean_pos}</span>{p_name}</div>', unsafe_allow_html=True)
                    st.write("")

                st.markdown('<div class="pitch-line-halfway"></div>', unsafe_allow_html=True)

                # --- MIDFIELDERS ---
                if midfielders:
                    m_cols = st.columns(len(midfielders))
                    for idx, (pos_key, p_name) in enumerate(midfielders):
                        clean_pos = clean_position_label(pos_key)
                        m_cols[idx].markdown(f'<div class="player-card"><span class="pos-label">{clean_pos}</span>{p_name}</div>', unsafe_allow_html=True)
                    st.write("")

                # --- ATTACKERS ---
                if attackers:
                    a_cols = st.columns(len(attackers))
                    for idx, (pos_key, p_name) in enumerate(attackers):
                        clean_pos = clean_position_label(pos_key)
                        a_cols[idx].markdown(f'<div class="player-card"><span class="pos-label">{clean_pos}</span>{p_name}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

        with details_col:
            st.subheader("⚽ Goals & Assists")
            try:
                goals_df = load_sheet("Socials_Goals")
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

            except Exception:
                st.info("Goal log loading...")

            st.divider()

            st.subheader("👥 Substitutes")
            subs = [game_data.get(f"SUB{i}") for i in range(1, 7)]
            active_subs = [str(s).strip() for s in subs if pd.notnull(s) and str(s).strip() not in ["", "-", "nan"]]
            
            if active_subs:
                for sub in active_subs:
                    st.write(f"• {sub}")
            else:
                st.write("No substitutes listed.")

    except Exception as e:
        st.error("Error loading match data from 'Socials_Games'.")
        st.exception(e)

# --- NEWS TAB ---
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
