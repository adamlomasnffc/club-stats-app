import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re

# 1. PAGE CONFIGURATION & LOGO URLS
APP_ICON_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/PenguinsLogo.png"
HEADER_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/ClubLogo.jpeg"
VIDEO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/a6e86bfe-69d7-4146-add8-2ba2d49c942b.MP4"

SOCIALS_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/SocialsLogo.jpeg"
WHITE_COMMUNITY_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/WhiteCommunityLogo.jpeg"

st.set_page_config(
    page_title="Derby Penguins App",
    page_icon=APP_ICON_URL,
    layout="wide"
)

# Handle Query Params safely for main navigation
query_params = st.query_params

if "nav" in query_params:
    st.session_state["active_page"] = query_params["nav"]

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Homepage"

current_page = st.session_state["active_page"]

# Handle Query Params safely for team subtabs
for team_key in ["Penguins", "Socials", "Community", "Club"]:
    param_name = f"sub_{team_key}"
    if param_name in query_params:
        st.session_state[f"{team_key}_subtab"] = query_params[param_name]
    elif f"{team_key}_subtab" not in st.session_state:
        st.session_state[f"{team_key}_subtab"] = "Player Stats"

# 2. GLOBAL STYLING
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" sizes="180x180" href="{APP_ICON_URL}">
        <link rel="apple-touch-icon-precomposed" href="{APP_ICON_URL}">
        <link rel="icon" type="image/png" sizes="192x192" href="{APP_ICON_URL}">
        <link rel="shortcut icon" href="{APP_ICON_URL}">
        <meta name="apple-mobile-web-app-title" content="Derby Penguins App">
        <meta name="apple-mobile-web-app-capable" content="yes">
    </head>
    <style>
        /* Global Reset & Base Alignments */
        html, body, [class*="css"], .stApp {{
            text-align: center !important;
            background-color: #0e1117 !important;
        }}
        
        .block-container, div[class*="stMainBlockContainer"], .stAppViewBlockContainer {{
            padding-top: 2.5rem !important; 
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
        }}

        h1, h2, h3, h4, h5, h6, p, label, div {{
            text-align: center !important;
        }}

        /* Header Logo Container */
        .header-logo-container {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin-bottom: 5px !important;
        }}
        .header-logo {{
            filter: invert(1);
            max-height: 60px !important;
            width: auto !important;
            object-fit: contain;
            display: block !important;
        }}

        /* DASHBOARD GRID CONTAINER FOR LINKS */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            width: 100%;
            margin-bottom: 10px;
        }}
        @media (max-width: 600px) {{
            .dashboard-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        .dashboard-btn {{
            background-color: #1a1c23 !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            padding: 10px 6px !important;
            font-weight: 600 !important;
            font-size: 0.75rem !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            cursor: pointer;
            text-align: center !important;
            text-decoration: none !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            transition: all 0.2s ease-in-out !important;
            width: 100%;
            box-sizing: border-box;
        }}
        .dashboard-btn:hover {{
            border-color: #FFB81C !important;
            color: #FFB81C !important;
            background-color: #22252e !important;
        }}
        .dashboard-btn img {{
            width: 24px;
            height: 24px;
            object-fit: contain;
        }}
        .dashboard-btn.inverted img {{
            filter: invert(1);
        }}

        /* SUB-TAB DASHBOARD CONTAINER */
        .subtab-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4px;
            width: 100%;
            margin-bottom: 12px;
        }}
        @media (max-width: 600px) {{
            .subtab-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        /* Clean Streamlit Video Styling */
        [data-testid="stVideo"] {{
            max-width: 480px !important;
            margin: 0 auto !important;
            width: 100% !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }}

        /* Metrics Styling */
        [data-testid="stMetric"] {{
            background-color: #1a1c23 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            border: 1px solid #333 !important;
            text-align: center !important;
        }}
        [data-testid="stMetricValue"] {{
            color: #FFB81C !important;
        }}

        /* Mobile Scrollable Table Wrapper */
        .mobile-table-container {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-top: 10px;
            margin-bottom: 20px;
        }}
    </style>
""", unsafe_allow_html=True)

# 3. TOP HEADER LOGO
st.markdown(f"""
    <div class="header-logo-container">
        <img src="{HEADER_LOGO_URL}" class="header-logo" alt="Derby Penguins Logo">
    </div>
    <h1 style="margin-top: 2px; margin-bottom: 10px; font-size: 1.25rem;">Derby Penguins FC</h1>
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
    if pd.isnull(pos):
        return ""
    return re.sub(r'\d+$', '', str(pos))

# Page Title Renderer replacing Emojis with Logos
def render_page_header(title, img_url=None, invert=False):
    if img_url:
        invert_style = "filter: invert(1);" if invert else ""
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 12px; margin-top: 5px;">
                <img src="{img_url}" style="height: 32px; width: auto; object-fit: contain; {invert_style}">
                <h2 style="margin: 0; padding: 0; font-size: 1.4rem; font-weight: 700; color: #ffffff;">{title}</h2>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='text-align: center; margin-bottom: 12px;'>{title}</h2>", unsafe_allow_html=True)

# 5. TOP INTERACTIVE NAVIGATION (Native Streamlit Markdown - Direct DOM)
pages_config = [
    ("🏠 Home", "Homepage", None, False),
    ("Penguins", "Penguins", HEADER_LOGO_URL, True),
    ("Socials", "Socials", SOCIALS_LOGO_URL, True),
    ("Community", "Community", WHITE_COMMUNITY_LOGO_URL, False),
    ("Club", "Club", HEADER_LOGO_URL, True),
    ("ℹ️ About", "About Us", None, False)
]

nav_html = '<div class="dashboard-grid">'
for label, key, img_url, invert in pages_config:
    active_style = "border-color: #FFB81C; color: #FFB81C; background-color: #22252e;" if current_page == key else ""
    invert_class = "inverted" if invert else ""
    img_tag = f'<img src="{img_url}" class="{invert_class}">' if img_url else ''
    
    nav_html += f'''
    <a href="?nav={key}" target="_self" class="dashboard-btn" style="{active_style}">
        {img_tag}
        <span>{label}</span>
    </a>
    '''
nav_html += '</div>'

# Render directly into parent page DOM (No iframe)
st.markdown(nav_html, unsafe_allow_html=True)

st.divider()

# Sub-tab Navigation Helper Function
def render_subtab_cards(team_key, has_match_center=True):
    tabs = ["Player Stats", "Results", "Match Center", "News"] if has_match_center else ["Combined Stats", "Club Schedule", "Club News"]
    current_subtab = st.session_state.get(f"{team_key}_subtab", tabs[0])

    subtab_html = '<div class="subtab-grid">'
    for idx, tab_name in enumerate(tabs):
        btn_label = f"📊 Stats" if "Stats" in tab_name else f"📅 Results" if "Results" in tab_name else f"📅 Schedule" if "Schedule" in tab_name else f"⚽ Lineups" if "Match" in tab_name else f"📰 News"
        active_style = "border-color: #FFB81C; color: #FFB81C; background-color: #22252e;" if current_subtab == tab_name else ""
        
        subtab_html += f'''
        <a href="?nav={current_page}&sub_{team_key}={tab_name}" target="_self" class="dashboard-btn" style="{active_style}">
            <span>{btn_label}</span>
        </a>
        '''
    subtab_html += '</div>'

    # Render directly into parent page DOM (No iframe)
    st.markdown(subtab_html, unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    return current_subtab


# ==========================================
# --- 1. HOMEPAGE ---
# ==========================================
if current_page == "Homepage":
    
    st.markdown("### 🎥 Feature Video")
    st.video(VIDEO_URL)

    st.divider()

    st.markdown("### 📲 Latest Club Updates")
    fb_page_url = "https://www.facebook.com/p/Derby-Penguins-FC-61568730025829/" 
    
    fb_iframe = f"""
    <div style="display: flex; justify-content: center; width: 100%; overflow: hidden;">
        <div style="width: 100%; max-width: 500px; overflow: hidden; border-radius: 8px; background: #111;">
            <iframe 
                src="https://www.facebook.com/plugins/page.php?href={fb_page_url}&tabs=timeline&width=340&height=650&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true" 
                width="100%" 
                height="650" 
                style="border:none; overflow:hidden; max-width: 100vw;" 
                scrolling="no" 
                frameborder="0" 
                allowfullscreen="true" 
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share">
            </iframe>
        </div>
    </div>
    """
    components.html(fb_iframe, height=660, scrolling=False)


# ==========================================
# --- 2. DERBY PENGUINS ---
# ==========================================
elif current_page == "Penguins":
    render_page_header("Derby Penguins", HEADER_LOGO_URL, invert=True)
    subtab = render_subtab_cards("Penguins")

    if subtab == "Player Stats":
        st.info("First team player stats will be populated here.")
    elif subtab == "Results":
        st.info("First team results and fixtures coming soon.")
    elif subtab == "Match Center":
        st.info("First team lineup pitch and goal logs coming soon.")
    elif subtab == "News":
        st.info("First team announcements.")


# ==========================================
# --- 3. DERBY PENGUINS SOCIALS ---
# ==========================================
elif current_page == "Socials":
    render_page_header("Derby Penguins Socials", SOCIALS_LOGO_URL, invert=True)
    subtab = render_subtab_cards("Socials")

    if subtab == "Player Stats":
        try:
            df = load_sheet("Socials_Player_Stats").iloc[:, :8]
            if "Player" in df.columns:
                df = df.dropna(subset=["Player"])

            top_apps = df.sort_values(by="Appearances", ascending=False).iloc[0]
            top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
            top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
            top_involvements = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]

            def safe_val(val):
                try:
                    return str(int(float(val))) if pd.notnull(val) else "0"
                except Exception:
                    return str(val)

            row1_col1, row1_col2 = st.columns(2)
            row1_col1.metric("🏃 Apps Leader", f"{top_apps['Player']}", f"{safe_val(top_apps['Appearances'])} Apps")
            row1_col2.metric("⚽ Top Scorer", f"{top_scorer['Player']}", f"{safe_val(top_scorer['Goals'])} Goals")
            
            row2_col1, row2_col2 = st.columns(2)
            row2_col1.metric("🅰️ Top Assister", f"{top_assister['Player']}", f"{safe_val(top_assister['Assists'])} Assists")
            row2_col2.metric("🔥 Top Contributor", f"{top_involvements['Player']}", f"{safe_val(top_involvements['Goal Involvements'])} G+A")

            st.divider()

            st.markdown("### Socials Player Stats")

            search_query = st.text_input("🔍 Search Player", "")
            sort_by = st.selectbox("Sort By Column", options=df.columns, index=1)
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[filtered_df["Player"].str.contains(search_query, case=False, na=False)]

            ascending = True if sort_order == "Ascending" else False
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

            table_html = "<div class='mobile-table-container'>"
            table_html += "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 500px;'>"
            table_html += "<tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
            for col in filtered_df.columns:
                table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center; font-size: 12px;'>{col}</th>"
            table_html += "</tr>"

            for idx, row in filtered_df.iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in filtered_df.columns:
                    val = row[col]
                    formatted_val = f"{int(val)}" if pd.notnull(val) and isinstance(val, (int, float)) and float(val).is_integer() else (f"{val:.1f}" if isinstance(val, float) else str(val))
                    table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                table_html += "</tr>"
            table_html += "</table></div>"

            st.markdown(table_html, unsafe_allow_html=True)

        except Exception as e:
            st.error("Error loading stats.")

    elif subtab == "Results":
        try:
            games_df = load_sheet("Socials_Games")
            target_cols = ["GameID", "Date", "Location", "Opponent", "KO Time", "Result", "Outcome"]
            display_cols = [c for c in target_cols if c in games_df.columns]
            if not display_cols:
                display_cols = list(games_df.columns[:7])
                
            fixtures_df = games_df[display_cols].copy().dropna(subset=[display_cols[0]])

            f_table_html = "<div class='mobile-table-container'>"
            f_table_html += "<table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 500px;'>"
            f_table_html += "<tr style='background-color: #FFB81C; color: #111; font-weight: bold; font-size: 12px;'>"
            for col in fixtures_df.columns:
                f_table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center;'>{col}</th>"
            f_table_html += "</tr>"

            for idx, row in fixtures_df.reset_index(drop=True).iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                f_table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in fixtures_df.columns:
                    val = row[col]
                    formatted_val = "-" if pd.isnull(val) or str(val).strip().lower() in ["nan", "none", ""] else str(val).strip()
                    f_table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                f_table_html += "</tr>"
            f_table_html += "</table></div>"

            st.markdown(f_table_html, unsafe_allow_html=True)

        except Exception as e:
            st.error("Error loading results data.")

    elif subtab == "Match Center":
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

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
            m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))
            
            m_col3, m_col4 = st.columns(2)
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
                    if g_count > 0: icons.append("⚽" * g_count)
                    if a_count > 0: icons.append("🅰️" * a_count)
                    badge_html = f'<div style="font-size: 7px; margin-top: 1px; line-height: 1;">{" ".join(icons)}</div>' if icons else ""

                    return f"""
                    <div style="background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 2px 2px; margin: 1px; text-align: center; flex: 1 1 0px; min-width: 0; box-sizing: border-box; overflow: hidden;">
                        <div style="font-size: 7px; color: #FFB81C; font-weight: bold; line-height: 1;">{c_pos}</div>
                        <div style="font-size: 8.5px; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.1;">{name}</div>
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
                body {{ margin: 0; font-family: sans-serif; background-color: transparent; }}
                .pitch {{
                    background: #181a20;
                    border: 2px solid #FFB81C;
                    border-radius: 8px;
                    padding: 6px 2px;
                    position: relative;
                    box-sizing: border-box;
                    min-height: 420px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    overflow: hidden;
                    width: 100%;
                }}
                .halfway-line {{
                    position: absolute; top: 50%; left: 0; right: 0;
                    border-top: 1px dashed rgba(255, 184, 28, 0.3);
                }}
                .center-circle {{
                    position: absolute; top: calc(50% - 25px); left: calc(50% - 25px);
                    width: 50px; height: 50px;
                    border: 1px dashed rgba(255, 184, 28, 0.3);
                    border-radius: 50%;
                }}
                .row {{
                    display: flex;
                    justify-content: space-around;
                    align-items: center;
                    position: relative;
                    z-index: 2;
                    width: 100%;
                    gap: 1px;
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
                components.html(pitch_component, height=440)

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

    elif subtab == "News":
        st.info("📢 Training details, match locations, and team announcements go here.")


# ==========================================
# --- 4. DERBY PENGUINS COMMUNITY ---
# ==========================================
elif current_page == "Community":
    render_page_header("Derby Penguins Community", WHITE_COMMUNITY_LOGO_URL, invert=False)
    subtab = render_subtab_cards("Community")

    if subtab == "Player Stats":
        st.info("Community stats coming soon.")
    elif subtab == "Results":
        st.info("Community results coming soon.")
    elif subtab == "Match Center":
        st.info("Community match center coming soon.")
    elif subtab == "News":
        st.info("Community announcements.")


# ==========================================
# --- 5. DERBY PENGUINS CLUB ---
# ==========================================
elif current_page == "Club":
    render_page_header("Derby Penguins Club Overview", HEADER_LOGO_URL, invert=True)
    subtab = render_subtab_cards("Club", has_match_center=False)

    if subtab == "Combined Stats":
        st.info("Combined stats across all squads will be displayed here.")
    elif subtab == "Club Schedule":
        st.info("Combined fixture list for all teams.")
    elif subtab == "Club News":
        st.info("Overall club announcements.")


# ==========================================
# --- 6. ABOUT DERBY PENGUINS ---
# ==========================================
elif current_page == "About Us":
    render_page_header("About Derby Penguins")
    st.markdown("""
        <div style="background-color: #1a1c23; border: 1px solid #333; border-radius: 10px; padding: 20px; max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #FFB81C; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;">Our Ethos</p>
            <p style="margin-bottom: 15px; font-size: 0.9rem;">At Derby Penguins, we are dedicated to grassroots football, sportsmanship, and building a supportive team community on and off the pitch.</p>
            <p style="color: #FFB81C; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;">Club Lore</p>
            <p style="margin-bottom: 0; font-size: 0.9rem;">Founded to bring together passionate players, Derby Penguins provides a competitive, welcoming environment to train, play, and win together across all our squad levels.</p>
        </div>
    """, unsafe_allow_html=True)
