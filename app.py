import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
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
def clean_pos_label(pos):
    return re.sub(r'\d+$', '', pos)

# Navigation Tabs
tab_stats, tab_matches, tab_news = st.tabs(["📊 Player Stats", "⚽ Matches", "📰 News"])

# ==========================================
# --- PLAYER STATS TAB ---
# ==========================================
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
        col1.metric("🏃 Most Apps", f"{top_apps['Player']}", f"{int(top_apps['Appearances'])} Apps")
        col2.metric("⚽ Top Scorer", f"{top_scorer['Player']}", f"{int(top_scorer['Goals'])} Goals")
        col3.metric("🅰️ Top Assister", f"{top_assister['Player']}", f"{int(top_assister['Assists'])} Assists")
        col4.metric("🔥 Top Contributor", f"{top_involvements['Player']}", f"{int(top_involvements['Goal Involvements'])} G+A")

        st.divider()

        st.subheader("Player Leaderboard")

        # Custom Interactive Controls
        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        with f_col1:
            search_query = st.text_input("🔍 Search Player", "")
        with f_col2:
            sort_by = st.selectbox("Sort By Column", options=df.columns, index=1)
        with f_col3:
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

        # Apply Filtering & Sorting
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["Player"].str.contains(search_query, case=False, na=False)]

        ascending = True if sort_order == "Ascending" else False
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

        # Centered HTML Table Rendering
        table_html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-top: 15px; font-family: sans-serif;'>"
        table_html += "<tr style='background-color: #262730; color: white;'>"
        for col in filtered_df.columns:
            table_html += f"<th style='padding: 12px; border-bottom: 2px solid #555; text-align: center;'>{col}</th>"
        table_html += "</tr>"

        for idx, row in filtered_df.iterrows():
            bg_color = "#1e1e1e" if idx % 2 == 0 else "#0e1117"
            table_html += f"<tr style='background-color: {bg_color}; color: white;'>"
            for col in filtered_df.columns:
                val = row[col]
                formatted_val = f"{int(val)}" if pd.notnull(val) and isinstance(val, (int, float)) and float(val).is_integer() else (f"{val:.1f}" if isinstance(val, float) else str(val))
                table_html += f"<td style='padding: 10px; border-bottom: 1px solid #333; text-align: center;'>{formatted_val}</td>"
            table_html += "</tr>"
        table_html += "</table>"

        st.markdown(table_html, unsafe_allow_html=True)

    except Exception as e:
        st.error("Error loading stats.")
        st.exception(e)

# ==========================================
# --- MATCHES & PITCH TAB ---
# ==========================================
with tab_matches:
    st.header("Match Center & Tactical Lineups")
    try:
        games_df = load_sheet("Socials_Games")

        def create_game_label(row):
            opponent = str(row.get("Opponent", "Unknown")).strip()
            result = str(row.get("Result", "")).strip()
            date = str(row.get("Date", "")).strip()
            
            label = f"vs {opponent}"
            if result and result.lower() != "nan":
                label += f" ({result})"
            if date and date.lower() != "nan":
                label += f" — {date}"
            return label

        game_options = {create_game_label(row): row["GameID"] for _, row in games_df.iterrows()}

        selected_label = st.selectbox(
            "Select Game to View Details & Lineup:",
            options=list(game_options.keys())
        )

        selected_game_id = game_options[selected_label]
        game_data = games_df[games_df["GameID"] == selected_game_id].iloc[0]

        # Clean MOTM lookup logic to prevent "nan"
        raw_motm = str(game_data.get("MOTM", "")).strip()
        motm_val = raw_motm if raw_motm and raw_motm.lower() not in ["nan", "none", "-"] else "-"

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
        m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))
        m_col3.metric("⚽ Score", str(game_data.get("Result", "-")))
        m_col4.metric("🏆 MOTM", motm_val)

        st.divider()

        pitch_col, details_col = st.columns([2, 1])

        with pitch_col:
            formation = str(game_data.get("Formation", "4-3-3")).strip()
            st.subheader(f"🟢 Starting Lineup ({formation})")

            # All position keys
            all_pos_keys = ["GK", "LB", "LWB", "CB", "CB1", "CB2", "CB3", "RB", "RWB", 
                            "CDM", "CM", "CM1", "CM2", "CM3", "CAM", "LM", "RM", 
                            "LW", "ST", "ST1", "ST2", "ST3", "RW"]

            lineup = {}
            for col_name in game_data.index:
                col_clean = str(col_name).strip()
                if col_clean in all_pos_keys:
                    val = game_data.get(col_name)
                    if pd.notnull(val) and str(val).strip().lower() not in ["", "-", "nan", "none"]:
                        lineup[col_clean] = str(val).strip()

            def make_player_card(pos_key, name):
                c_pos = clean_pos_label(pos_key)
                return f"""
                <div style="background: white; color: #1b5e20; border-radius: 6px; padding: 6px 8px; margin: 4px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.4); min-width: 80px; max-width: 120px; flex: 1;">
                    <div style="font-size: 10px; color: #2e7d32; font-weight: bold; text-transform: uppercase;">{c_pos}</div>
                    <div style="font-size: 12px; font-weight: 800; color: #111;">{name}</div>
                </div>
                """

            # Strategic 5-tier vertical division
            gk_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k == "GK"])
            def_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k in ["LB", "LWB", "CB", "CB1", "CB2", "CB3", "RB", "RWB"]])
            cdm_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k in ["CDM"]])
            mid_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k in ["CM", "CM1", "CM2", "CM3", "LM", "RM"]])
            cam_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k in ["CAM"]])
            att_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k in ["LW", "ST", "ST1", "ST2", "ST3", "RW"]])

            # Pure HTML Pitch Graphic Container
            pitch_component = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {{ margin: 0; font-family: sans-serif; }}
            .pitch {{
                background: linear-gradient(180deg, #1e5622 0%, #2e7d32 100%);
                border: 4px solid #ffffff;
                border-radius: 12px;
                padding: 15px 10px;
                position: relative;
                box-sizing: border-box;
                min-height: 520px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                overflow: hidden;
            }}
            .halfway-line {{
                position: absolute; top: 50%; left: 0; right: 0;
                border-top: 2px solid rgba(255,255,255,0.5);
            }}
            .center-circle {{
                position: absolute; top: calc(50% - 40px); left: calc(50% - 40px);
                width: 80px; height: 80px;
                border: 2px solid rgba(255,255,255,0.5);
                border-radius: 50%;
            }}
            .row {{
                display: flex;
                justify-content: space-around;
                align-items: center;
                position: relative;
                z-index: 2;
                width: 100%;
            }}
            </style>
            </head>
            <body>
            <div class="pitch">
                <div class="halfway-line"></div>
                <div class="center-circle"></div>
                {"<div class='row'>" + gk_html + "</div>" if gk_html else ""}
                {"<div class='row'>" + def_html + "</div>" if def_html else ""}
                {"<div class='row'>" + cdm_html + "</div>" if cdm_html else ""}
                {"<div class='row'>" + mid_html + "</div>" if mid_html else ""}
                {"<div class='row'>" + cam_html + "</div>" if cam_html else ""}
                {"<div class='row'>" + att_html + "</div>" if att_html else ""}
            </div>
            </body>
            </html>
            """
            components.html(pitch_component, height=540)

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
                        
                        if pd.notnull(assist) and str(assist).strip().lower() not in ["", "none", "-", "unassisted", "nan"]:
                            st.write(f"• **{scorer}** ⚽ ( {str(assist).strip()} 🅰️ )")
                        else:
                            st.write(f"• **{scorer}** ⚽")
                else:
                    st.info("No goals recorded for this match.")
            except Exception:
                st.info("Goal log loading...")

            st.divider()

            st.subheader("👥 Substitutes")
            subs = [game_data.get(f"SUB{i}") for i in range(1, 7)]
            active_subs = [str(s).strip() for s in subs if pd.notnull(s) and str(s).strip().lower() not in ["", "-", "nan", "none"]]
            
            if active_subs:
                for sub in active_subs:
                    st.write(f"• {sub}")
            else:
                st.write("No substitutes listed.")

    except Exception as e:
        st.error("Error loading match data.")
        st.exception(e)

# ==========================================
# --- NEWS TAB ---
# ==========================================
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
