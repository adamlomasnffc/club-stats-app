import streamlit as st
import pandas as pd
import re

# Page Configuration for Mobile Optimization
st.set_page_config(
    page_title="Penguins Master Stats",
    page_icon="🐧",
    layout="wide"
)

# Global CSS: Force center alignment on st.dataframe headers & cells
st.markdown("""
    <style>
    /* Force centered headers on st.dataframe */
    [data-testid="stDataFrame"] div[role="columnheader"] div {
        justify-content: center !important;
        text-align: center !important;
    }
    [data-testid="stDataFrame"] div[role="gridcell"] {
        justify-content: center !important;
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐧 Penguins Club Stats")

SPREADSHEET_ID = "19wTGruEyetdVNhfjkyVqLDueyV9joVtRsI51RAqurjA"

@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def clean_pos_label(pos):
    return re.sub(r'\d+$', '', pos)

tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# --- PLAYER STATS TAB ---
with tab_stats:
    try:
        df = load_sheet("Socials_Player_Stats").iloc[:, :8]
        if "Player" in df.columns:
            df = df.dropna(subset=["Player"])

        # Metric Cards
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

        st.subheader("Player Leaderboard")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            search_query = st.text_input("🔍 Search Player Name", "")
        with f_col2:
            min_apps = st.slider("Filter by Minimum Appearances", 0, int(df["Appearances"].max()), 0)

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Player"].str.contains(search_query, case=False, na=False)]
        if min_apps > 0:
            filtered_df = filtered_df[filtered_df["Appearances"] >= min_apps]

        # Centered interactive table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.Column(alignment="center") for col in filtered_df.columns
            }
        )

    except Exception as e:
        st.error("Error loading stats.")
        st.exception(e)

# --- MATCHES & PITCH TAB ---
with tab_matches:
    st.header("Match Center & Tactical Lineups")
    try:
        games_df = load_sheet("Socials_Games")

        selected_game_id = st.selectbox(
            "Select Game to View Details & Lineup:",
            options=games_df["GameID"].unique()
        )

        game_data = games_df[games_df["GameID"] == selected_game_id].iloc[0]

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
        m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))
        m_col3.metric("⚽ Score", str(game_data.get("Result", "-")))
        m_col4.metric("🏆 MOTM", str(game_data.get("MOTM", "-")))

        st.divider()

        pitch_col, details_col = st.columns([2, 1])

        with pitch_col:
            formation = str(game_data.get("Formation", "4-3-3")).strip()
            st.subheader(f"🟢 Starting Lineup ({formation})")

            # Exhaustive position fetcher to never miss players
            all_pos_keys = ["GK", "LB", "LWB", "CB", "CB1", "CB2", "CB3", "RB", "RWB", 
                            "CDM", "CM", "CM1", "CM2", "CM3", "CAM", "LM", "RM", 
                            "LW", "ST", "ST1", "ST2", "ST3", "RW"]

            lineup = {}
            for k in all_pos_keys:
                val = game_data.get(k, None)
                if pd.notnull(val) and str(val).strip() not in ["", "-", "nan"]:
                    lineup[k] = str(val).strip()

            # Dynamic pitch card HTML builder
            def make_player_badge(pos_key, name):
                c_pos = clean_pos_label(pos_key)
                return f"""
                <div style="background: white; color: #1b5e20; border-radius: 6px; padding: 6px 10px; margin: 4px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.4); flex: 1; min-width: 90px; max-width: 140px;">
                    <div style="font-size: 10px; color: #2e7d32; font-weight: bold;">{c_pos}</div>
                    <div style="font-size: 12px; font-weight: 800;">{name}</div>
                </div>
                """

            # Group into tactical rows
            gk_html = "".join([make_player_badge(k, lineup[k]) for k in lineup if k == "GK"])
            def_html = "".join([make_player_badge(k, lineup[k]) for k in lineup if k in ["LB", "LWB", "CB", "CB1", "CB2", "CB3", "RB", "RWB"]])
            mid_html = "".join([make_player_badge(k, lineup[k]) for k in lineup if k in ["CDM", "CM", "CM1", "CM2", "CM3", "CAM", "LM", "RM"]])
            att_html = "".join([make_player_badge(k, lineup[k]) for k in lineup if k in ["LW", "ST", "ST1", "ST2", "ST3", "RW"]])

            # SVG pitch visualizer container
            pitch_html = f"""
            <div style="background: linear-gradient(180deg, #1e5622 0%, #2e7d32 100%); border: 3px solid #ffffff; border-radius: 12px; padding: 20px 10px; position: relative; box-shadow: inset 0 0 15px rgba(0,0,0,0.5);">
                <!-- Pitch lines -->
                <div style="border-top: 2px solid rgba(255,255,255,0.6); position: absolute; top: 50%; left: 0; right: 0;"></div>
                <div style="border: 2px solid rgba(255,255,255,0.6); border-radius: 50%; width: 80px; height: 80px; position: absolute; top: calc(50% - 40px); left: calc(50% - 40px);"></div>
                
                <!-- Goalkeeper -->
                <div style="display: flex; justify-content: center; position: relative; z-index: 2; margin-bottom: 25px;">
                    {gk_html}
                </div>
                <!-- Defenders -->
                <div style="display: flex; justify-content: space-around; position: relative; z-index: 2; margin-bottom: 35px;">
                    {def_html}
                </div>
                <!-- Midfielders -->
                <div style="display: flex; justify-content: space-around; position: relative; z-index: 2; margin-bottom: 35px;">
                    {mid_html}
                </div>
                <!-- Attackers -->
                <div style="display: flex; justify-content: space-around; position: relative; z-index: 2;">
                    {att_html}
                </div>
            </div>
            """
            st.markdown(pitch_html, unsafe_allow_html=True)

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
        st.error("Error loading match data.")
        st.exception(e)

# --- NEWS TAB ---
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
