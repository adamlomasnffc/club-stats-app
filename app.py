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

# Custom Mobile CSS Injection (Centering & Penguin Yellow Theme)
st.markdown("""
<style>
    /* Center align all metric components (Label, Value, Subtext) */
    [data-testid="stMetric"] {
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        background-color: #1a1c23;
        border-radius: 8px;
        padding: 10px !important;
        border: 1px solid #333;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricLabel"] > div {
        justify-content: center !important;
        text-align: center !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
        color: #FFB81C !important; /* Penguin Yellow */
        width: 100% !important;
    }
    [data-testid="stMetricValue"] > div {
        justify-content: center !important;
        text-align: center !important;
    }

    /* Make tables horizontally scrollable on small screens */
    .mobile-table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* Tab label font adjustment & active tab highlight */
    button[data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 14px !important;
    }
    button[aria-selected="true"] {
        color: #FFB81C !important;
    }
</style>
""", unsafe_allow_html=True)

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
tab_stats, tab_results, tab_matches, tab_news = st.tabs([
    "📊 Player Stats", 
    "📅 Results", 
    "⚽ Match Center", 
    "📰 News"
])

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

        # Centered HTML Table Rendering wrapped in mobile scrolling container
        table_html = "<div class='mobile-table-container'>"
        table_html += "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 600px;'>"
        table_html += "<tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
        for col in filtered_df.columns:
            table_html += f"<th style='padding: 10px; border-bottom: 2px solid #333; text-align: center; font-size: 13px;'>{col}</th>"
        table_html += "</tr>"

        for idx, row in filtered_df.iterrows():
            bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
            table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 13px;'>"
            for col in filtered_df.columns:
                val = row[col]
                formatted_val = f"{int(val)}" if pd.notnull(val) and isinstance(val, (int, float)) and float(val).is_integer() else (f"{val:.1f}" if isinstance(val, float) else str(val))
                table_html += f"<td style='padding: 8px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
            table_html += "</tr>"
        table_html += "</table></div>"

        st.markdown(table_html, unsafe_allow_html=True)

    except Exception as e:
        st.error("Error loading stats.")
        st.exception(e)

# ==========================================
# --- RESULTS TAB ---
# ==========================================
with tab_results:
    st.header("📅 Results")
    try:
        games_df = load_sheet("Socials_Games")
        
        target_cols = ["GameID", "Date", "Location", "Opponent", "KO Time", "Result", "Outcome"]
        display_cols = [c for c in target_cols if c in games_df.columns]
        
        if not display_cols:
            display_cols = list(games_df.columns[:7])
            
        fixtures_df = games_df[display_cols].copy().dropna(subset=[display_cols[0]])

        # Responsive HTML Table Display
        f_table_html = "<div class='mobile-table-container'>"
        f_table_html += "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 550px;'>"
        f_table_html += "<tr style='background-color: #FFB81C; color: #111; font-weight: bold; font-size: 13px;'>"
        for col in fixtures_df.columns:
            f_table_html += f"<th style='padding: 10px; border-bottom: 2px solid #333; text-align: center;'>{col}</th>"
        f_table_html += "</tr>"

        for idx, row in fixtures_df.reset_index(drop=True).iterrows():
            bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
            f_table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 13px;'>"
            for col in fixtures_df.columns:
                val = row[col]
                formatted_val = "-" if pd.isnull(val) or str(val).strip().lower() in ["nan", "none", ""] else str(val).strip()
                f_table_html += f"<td style='padding: 8px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
            f_table_html += "</tr>"
        f_table_html += "</table></div>"

        st.markdown(f_table_html, unsafe_allow_html=True)

    except Exception as e:
        st.error("Error loading results data.")
        st.exception(e)

# ==========================================
# --- MATCH CENTER & PITCH TAB ---
# ==========================================
with tab_matches:
    st.markdown("<h2 style='text-align: center;'>Match Center & Lineups</h2>", unsafe_allow_html=True)
    try:
        games_df = load_sheet("Socials_Games")

        def create_game_label(row):
            opponent = str(row.get("Opponent", "Unknown")).strip()
            result = str(row.get("Result", "")).strip()
            date = str(row.get("Date", "")).strip()
            
            venue_val = ""
            for col in row.index:
                col_lower = str(col).strip().lower()
                if "home" in col_lower or "away" in col_lower or col_lower == "venue":
                    venue_val = str(row[col]).strip().lower()
                    break
            
            is_away = venue_val.startswith("a")

            if result and result.lower() != "nan":
                if is_away:
                    scores = [s.strip() for s in result.split("-")]
                    match_title = f"{opponent} {scores[1]}-{scores[0]} Socials" if len(scores) == 2 else f"{opponent} {result} Socials"
                else:
                    match_title = f"Socials {result} {opponent}"
            else:
                match_title = f"{opponent} vs Socials" if is_away else f"Socials vs {opponent}"
            
            return f"{match_title} ({date})" if date and date.lower() != "nan" else match_title

        game_options = {create_game_label(row): row["GameID"] for _, row in games_df.iterrows()}

        selected_label = st.selectbox(
            "Select Game:",
            options=list(game_options.keys())
        )

        selected_game_id = game_options[selected_label]
        game_data = games_df[games_df["GameID"] == selected_game_id].iloc[0]

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
            st.subheader(f"Dynamic Lineup ({formation})")

            goal_counts, assist_counts = {}, {}
            try:
                goals_df = load_sheet("Socials_Goals")
                match_col = "Match ID" if "Match ID" in goals_df.columns else "GameID"
                match_goals = goals_df[goals_df[match_col].astype(str) == str(selected_game_id)]

                if not match_goals.empty:
                    for _, row in match_goals.iterrows():
                        scorer = str(row.get("Goalscorer", row.get("Scorer", ""))).strip()
                        assist = str(row.get("Assist", "")).strip()
                        
                        if scorer and scorer.lower() not in ["unknown", "none", "-", "nan", ""]:
                            goal_counts[scorer] = goal_counts.get(scorer, 0) + 1
                        if assist and assist.lower() not in ["none", "-", "unassisted", "nan", ""]:
                            assist_counts[assist] = assist_counts.get(assist, 0) + 1
            except Exception:
                pass

            # Ordering maps (Left -> Center -> Right)
            def_order = ["LB", "LWB", "CB", "CB1", "CB2", "CB3", "RWB", "RB"]
            cdm_order = ["CDM", "CDM1", "CDM2"]
            mid_order = ["LM", "CM", "CM1", "CM2", "CM3", "RM"]
            cam_order = ["CAM", "CAM1", "CAM2"]
            att_order = ["LW", "ST", "ST1", "ST2", "ST3", "RW"]

            lineup = {}
            for col_name in game_data.index:
                col_clean = str(col_name).strip()
                val = game_data.get(col_name)
                if pd.notnull(val) and str(val).strip().lower() not in ["", "-", "nan", "none"]:
                    lineup[col_clean] = str(val).strip()

            def make_player_card(pos_key, name):
                c_pos = clean_pos_label(pos_key)
                g_count = goal_counts.get(name, 0)
                a_count = assist_counts.get(name, 0)
                
                icons = []
                if g_count > 0:
                    icons.append("⚽" * g_count)
                if a_count > 0:
                    icons.append("🅰️" * a_count)
                
                badge_html = f'<div style="font-size: 9px; margin-top: auto; padding-top: 2px; line-height: 1;">{" ".join(icons)}</div>' if icons else ""

                return f"""
                <div style="background: #111; color: white; border: 1px solid #333; border-radius: 5px; padding: 4px 5px; margin: 2px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.5); min-width: 55px; max-width: 90px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
                    <div>
                        <div style="font-size: 9px; color: #FFB81C; font-weight: bold;">{c_pos}</div>
                        <div style="font-size: 10px; font-weight: 800; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{name}</div>
                    </div>
                    {badge_html}
                </div>
                """

            gk_html = "".join([make_player_card(k, lineup[k]) for k in lineup if k == "GK"])
            def_html = "".join([make_player_card(k, lineup[k]) for k in def_order if k in lineup])
            cdm_html = "".join([make_player_card(k, lineup[k]) for k in cdm_order if k in lineup])
            mid_html = "".join([make_player_card(k, lineup[k]) for k in mid_order if k in lineup])
            cam_html = "".join([make_player_card(k, lineup[k]) for k in cam_order if k in lineup])
            att_html = "".join([make_player_card(k, lineup[k]) for k in att_order if k in lineup])

            pitch_component = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {{ margin: 0; font-family: sans-serif; }}
            .pitch {{
                background: #181a20;
                border: 2px solid #FFB81C;
                border-radius: 10px;
                padding: 10px 5px;
                position: relative;
                box-sizing: border-box;
                min-height: 480px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                overflow: hidden;
            }}
            .halfway-line {{
                position: absolute; top: 50%; left: 0; right: 0;
                border-top: 1px dashed rgba(255, 184, 28, 0.3);
            }}
            .center-circle {{
                position: absolute; top: calc(50% - 35px); left: calc(50% - 35px);
                width: 70px; height: 70px;
                border: 1px dashed rgba(255, 184, 28, 0.3);
                border-radius: 50%;
            }}
            .row {{
                display: flex;
                justify-content: space-around;
                align-items: stretch;
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
            components.html(pitch_component, height=500)

        with details_col:
            st.markdown("<h3 style='text-align: center;'>⚽ Goals & Assists</h3>", unsafe_allow_html=True)
            try:
                goals_df = load_sheet("Socials_Goals")
                match_col = "Match ID" if "Match ID" in goals_df.columns else "GameID"
                match_goals = goals_df[goals_df[match_col].astype(str) == str(selected_game_id)]

                if not match_goals.empty:
                    for _, row in match_goals.iterrows():
                        scorer = row.get("Goalscorer", row.get("Scorer", "Unknown"))
                        assist = row.get("Assist", "")
                        
                        if pd.notnull(assist) and str(assist).strip().lower() not in ["", "none", "-", "unassisted", "nan"]:
                            st.markdown(f"<div style='text-align: center;'>• <b>{scorer}</b> ⚽ ( {str(assist).strip()} 🅰️ )</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: center;'>• <b>{scorer}</b> ⚽</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align: center; color: #aaa;'>No goals recorded.</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("<div style='text-align: center;'>Goal log loading...</div>", unsafe_allow_html=True)

            st.divider()

            st.markdown("<h3 style='text-align: center;'>👥 Substitutes</h3>", unsafe_allow_html=True)
            subs = [game_data.get(f"SUB{i}") for i in range(1, 7)]
            active_subs = [str(s).strip() for s in subs if pd.notnull(s) and str(s).strip().lower() not in ["", "-", "nan", "none"]]
            
            if active_subs:
                for sub in active_subs:
                    st.markdown(f"<div style='text-align: center;'>• {sub}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align: center; color: #aaa;'>No substitutes listed.</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error("Error loading match data.")
        st.exception(e)

# ==========================================
# --- NEWS TAB ---
# ==========================================
with tab_news:
    st.header("Club Announcements")
    st.info("📢 Training details, match locations, and announcements go here.")
