import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re

# 1. PAGE CONFIGURATION & MOBILE APP ICON
LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/unnamed.png"
VIDEO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/a6e86bfe-69d7-4146-add8-2ba2d49c942b.MP4"

st.set_page_config(
    page_title="Derby Penguins App",
    page_icon=LOGO_URL,
    layout="wide"
)

# Initialize Session State
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Homepage"

for team_key in ["Penguins", "Socials", "Community", "Club"]:
    if f"{team_key}_subtab" not in st.session_state:
        st.session_state[f"{team_key}_subtab"] = "Player Stats"

# Handle Query Params
query_params = st.query_params
if "nav" in query_params:
    st.session_state["active_page"] = query_params["nav"]

# 2. GLOBAL STYLING & RESPONSIVE GRID CSS
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" sizes="180x180" href="{LOGO_URL}">
        <link rel="apple-touch-icon-precomposed" href="{LOGO_URL}">
        <link rel="icon" type="image/png" sizes="192x192" href="{LOGO_URL}">
        <link rel="shortcut icon" href="{LOGO_URL}">
        <meta name="apple-mobile-web-app-title" content="Derby Penguins">
        <meta name="apple-mobile-web-app-capable" content="yes">
    </head>
    <style>
        /* Global Center Alignment */
        html, body, [class*="css"], .stApp, .block-container {{
            text-align: center !important;
        }}
        
        .block-container, div[class*="stMainBlockContainer"], .stAppViewBlockContainer {{
            padding-top: 1.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}

        h1, h2, h3, h4, h5, h6, p, label, div {{
            text-align: center !important;
        }}

        /* Header Logo Fix */
        .header-logo-container {{
            padding-top: 10px;
            margin-bottom: 5px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .header-logo {{
            filter: invert(1);
            max-height: 80px;
            object-fit: contain;
            display: block;
            margin: 0 auto !important;
        }}

        /* Responsive Custom Button Grids */
        div[data-testid="column"] {{
            padding: 0 2px !important;
        }}

        div.stButton > button {{
            width: 100% !important;
            background-color: #1a1c23 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            padding: 8px 2px !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease-in-out !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        
        div.stButton > button:hover {{
            border-color: #FFB81C !important;
            color: #FFB81C !important;
            background-color: #22252e !important;
        }}
        
        div.stButton > button:active {{
            background-color: #FFB81C !important;
            color: #111111 !important;
        }}

        /* Media queries for narrow mobile screens */
        @media (max-width: 640px) {{
            div.stButton > button {{
                font-size: 0.72rem !important;
                padding: 6px 1px !important;
                border-radius: 6px !important;
            }}
        }}

        /* Video Wrapper */
        .video-container {{
            max-width: 480px;
            margin: 0 auto;
            width: 100%;
        }}
        .video-container video {{
            width: 100% !important;
            max-height: 500px;
            border-radius: 10px;
            object-fit: contain;
        }}

        /* Facebook Centered Responsive Wrapper */
        .fb-center-wrapper {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin: 0 auto;
        }}
        .fb-container {{
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            overflow: hidden;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        .fb-container iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        /* Center metrics styling */
        [data-testid="stMetric"] {{
            text-align: center !important;
            justify-content: center !important;
            align-items: center !important;
            background-color: #1a1c23;
            border-radius: 8px;
            padding: 8px !important;
            border: 1px solid #333;
        }}
        [data-testid="stMetric"] > div {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 0.8rem !important;
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.1rem !important;
            display: flex !important;
            justify-content: center !important;
            text-align: center !important;
            color: #FFB81C !important;
            width: 100% !important;
        }}

        /* Mobile table container */
        .mobile-table-container {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-top: 10px;
            margin-bottom: 20px;
        }}
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown(f"""
    <div class="header-logo-container">
        <img src="{LOGO_URL}" class="header-logo" alt="Derby Penguins Logo">
    </div>
    <h1 style="margin-top: 5px; margin-bottom: 15px; font-size: 1.6rem;">Derby Penguins App</h1>
""", unsafe_allow_html=True)

# 4. SPREADSHEET DATA LOADER
SPREADSHEET_ID = "19wTGruEyetdVNhfjkyVqLDueyV9joVtRsI51RAqurjA"

@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def clean_pos_label(pos):
    return re.sub(r'\d+$', '', pos)

# 5. TOP INTERACTIVE NAVIGATION CARDS (6 Uniform Columns)
nav_cols = st.columns(6)
pages_config = [
    ("🏠 Home", "Homepage"),
    ("🐧 Penguins", "Penguins"),
    ("📱 Socials", "Socials"),
    ("🤝 Community", "Community"),
    ("📊 Club", "Club"),
    ("ℹ️ About", "About Us")
]

for idx, (label, key) in enumerate(pages_config):
    with nav_cols[idx]:
        if st.button(label, key=f"nav_btn_{key}"):
            st.session_state["active_page"] = key
            st.rerun()

st.divider()

current_page = st.session_state["active_page"]

# Helper function for rendering sub-tab interactive cards in horizontal single-row grids
def render_subtab_cards(team_key, has_match_center=True):
    tabs = ["Player Stats", "Results", "Match Center", "News"] if has_match_center else ["Combined Stats", "Club Schedule", "Club News"]
    cols = st.columns(len(tabs))
    for idx, tab_name in enumerate(tabs):
        with cols[idx]:
            btn_label = f"📊 Stats" if "Stats" in tab_name else f"📅 Results" if "Results" in tab_name else f"📅 Schedule" if "Schedule" in tab_name else f"⚽ Lineups" if "Match" in tab_name else f"📰 News"
            if st.button(btn_label, key=f"sub_btn_{team_key}_{idx}"):
                st.session_state[f"{team_key}_subtab"] = tab_name
                st.rerun()
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    return st.session_state.get(f"{team_key}_subtab", tabs[0])


# ==========================================
# --- 1. HOMEPAGE ---
# ==========================================
if current_page == "Homepage":
    
    st.markdown("### 🎥 Feature Video")
    st.markdown("<div class='video-container'>", unsafe_allow_html=True)
    st.video(VIDEO_URL)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📲 Latest Club Updates")
    fb_page_url = "https://www.facebook.com/p/Derby-Penguins-FC-61568730025829/" 
    fb_iframe = f"""
    <div class="fb-center-wrapper">
        <div class="fb-container">
            <iframe 
                src="https://www.facebook.com/plugins/page.php?href={fb_page_url}&tabs=timeline&width=500&height=600&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true" 
                height="600" 
                style="border:none;overflow:hidden;width:100%;" 
                scrolling="no" 
                frameborder="0" 
                allowfullscreen="true" 
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share">
            </iframe>
        </div>
    </div>
    """
    components.html(fb_iframe, height=620, scrolling=True)


# ==========================================
# --- 2. DERBY PENGUINS ---
# ==========================================
elif current_page == "Penguins":
    st.markdown("## 🐧 Derby Penguins")
    subtab = render_subtab_cards("Penguins")

    if subtab == "Player Stats":
        st.markdown("### 📊 Player Stats")
        st.info("First team player stats will be populated here.")

    elif subtab == "Results":
        st.markdown("### 📅 Results")
        st.info("First team results and fixtures coming soon.")

    elif subtab == "Match Center":
        st.markdown("### ⚽ Match Center")
        st.info("First team lineup pitch and goal logs coming soon.")

    elif subtab == "News":
        st.markdown("### 📰 News")
        st.info("First team announcements.")


# ==========================================
# --- 3. DERBY PENGUINS SOCIALS (POPULATED DATA) ---
# ==========================================
elif current_page == "Socials":
    st.markdown("## 📱 Derby Penguins Socials")
    subtab = render_subtab_cards("Socials")

    # --- SOCIALS STATS TAB ---
    if subtab == "Player Stats":
        try:
            df = load_sheet("Socials_Player_Stats").iloc[:, :8]
            if "Player" in df.columns:
                df = df.dropna(subset=["Player"])

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

            st.markdown("### Socials Player Stats")

            f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
            with f_col1:
                search_query = st.text_input("🔍 Search Player", "")
            with f_col2:
                sort_by = st.selectbox("Sort By Column", options=df.columns, index=1)
            with f_col3:
                sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[filtered_df["Player"].str.contains(search_query, case=False, na=False)]

            ascending = True if sort_order == "Ascending" else False
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

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

    # --- SOCIALS RESULTS TAB ---
    elif subtab == "Results":
        st.markdown("## 📅 Socials Results")
        try:
            games_df = load_sheet("Socials_Games")
            target_cols = ["GameID", "Date", "Location", "Opponent", "KO Time", "Result", "Outcome"]
            display_cols = [c for c in target_cols if c in games_df.columns]
            if not display_cols:
                display_cols = list(games_df.columns[:7])
                
            fixtures_df = games_df[display_cols].copy().dropna(subset=[display_cols[0]])

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

    # --- SOCIALS MATCH CENTER TAB ---
    elif subtab == "Match Center":
        st.markdown("## Socials Match Center & Lineups")
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
            options_list = list(game_options.keys())
            default_idx = len(options_list) - 1 if options_list else 0

            selected_label = st.selectbox("Select Game:", options=options_list, index=default_idx)
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
                st.subheader(f"Starting 11 ({formation})")

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
                st.markdown("### ⚽ Goals & Assists")
                try:
                    goals_df = load_sheet("Socials_Goals")
                    match_col = "Match ID" if "Match ID" in goals_df.columns else "GameID"
                    match_goals = goals_df[goals_df[match_col].astype(str) == str(selected_game_id)]

                    if not match_goals.empty:
                        for _, row in match_goals.iterrows():
                            scorer = row.get("Goalscorer", row.get("Scorer", "Unknown"))
                            assist = row.get("Assist", "")
                            if pd.notnull(assist) and str(assist).strip().lower() not in ["", "none", "-", "unassisted", "nan"]:
                                st.markdown(f"• <b>{scorer}</b> ⚽ ( {str(assist).strip()} 🅰️ )", unsafe_allow_html=True)
                            else:
                                st.markdown(f"• <b>{scorer}</b> ⚽", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #aaa;'>No goals recorded.</p>", unsafe_allow_html=True)
                except Exception:
                    st.markdown("Goal log loading...")

                st.divider()

                st.markdown("### 👥 Substitutes")
                subs = [game_data.get(f"SUB{i}") for i in range(1, 7)]
                active_subs = [str(s).strip() for s in subs if pd.notnull(s) and str(s).strip().lower() not in ["", "-", "nan", "none"]]
                
                if active_subs:
                    for sub in active_subs:
                        st.markdown(f"• {sub}")
                else:
                    st.markdown("<p style='color: #aaa;'>No substitutes listed.</p>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Error loading match data.")
            st.exception(e)

    # --- SOCIALS NEWS TAB ---
    elif subtab == "News":
        st.markdown("## 📰 Socials Announcements")
        st.info("📢 Training details, match locations, and team announcements go here.")


# ==========================================
# --- 4. DERBY PENGUINS COMMUNITY ---
# ==========================================
elif current_page == "Community":
    st.markdown("## 🤝 Derby Penguins Community")
    subtab = render_subtab_cards("Community")

    if subtab == "Player Stats":
        st.markdown("### 📊 Player Stats")
        st.info("Community stats coming soon.")

    elif subtab == "Results":
        st.markdown("### 📅 Results")
        st.info("Community results coming soon.")

    elif subtab == "Match Center":
        st.markdown("### ⚽ Match Center")
        st.info("Community match center coming soon.")

    elif subtab == "News":
        st.markdown("### 📰 News")
        st.info("Community announcements.")


# ==========================================
# --- 5. DERBY PENGUINS CLUB ---
# ==========================================
elif current_page == "Club":
    st.markdown("## 📊 Derby Penguins Club Overview")
    subtab = render_subtab_cards("Club", has_match_center=False)

    if subtab == "Combined Stats":
        st.markdown("### 📊 Club Leaderboards")
        st.info("Combined stats across all squads will be displayed here.")

    elif subtab == "Club Schedule":
        st.markdown("### 📅 Master Schedule")
        st.info("Combined fixture list for all teams.")

    elif subtab == "Club News":
        st.markdown("### 📰 Club News")
        st.info("Overall club announcements.")


# ==========================================
# --- 6. ABOUT DERBY PENGUINS ---
# ==========================================
elif current_page == "About Us":
    st.markdown("## ℹ️ About Derby Penguins")
    st.markdown("""
        <div style="background-color: #1a1c23; border: 1px solid #333; border-radius: 10px; padding: 25px; max-width: 750px; margin: 0 auto; text-align: center;">
            <p style="color: #FFB81C; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;">Our Ethos</p>
            <p style="margin-bottom: 20px;">At Derby Penguins, we are dedicated to grassroots football, sportsmanship, and building a supportive team community on and off the pitch.</p>
            <p style="color: #FFB81C; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;">Club Lore</p>
            <p style="margin-bottom: 0;">Founded to bring together passionate players, Derby Penguins provides a competitive, welcoming environment to train, play, and win together across all our squad levels.</p>
        </div>
    """, unsafe_allow_html=True)
