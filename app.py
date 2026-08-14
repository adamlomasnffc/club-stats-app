import re
import textwrap
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# 1. HELPER FUNCTION TO RRENDER HTML SAFELY
def render_html(html_str):
    clean_html = textwrap.dedent(str(html_str)).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


# 2. PAGE CONFIGURATION & LOGO URLS
APP_ICON_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/PenguinsLogo.png"
HEADER_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/ClubLogo.jpeg"
VIDEO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/a6e86bfe-69d7-4146-add8-2ba2d49c942b.MP4"

SOCIALS_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/SocialsLogo.jpeg"
WHITE_COMMUNITY_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/WhiteCommunityLogo.jpeg"
BLACK_COMMUNITY_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/BlackCommunityLogo.jpeg"

st.set_page_config(
    page_title="Derby Penguins App", page_icon=APP_ICON_URL, layout="wide"
)

# 3. INTERNAL SESSION STATE NAVIGATION
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Homepage"

for team_key in ["Penguins", "Socials", "Community", "Club"]:
    if f"{team_key}_subtab" not in st.session_state:
        st.session_state[f"{team_key}_subtab"] = (
            "Player Stats" if team_key != "Club" else "Combined Stats"
        )

current_page = st.session_state["active_page"]

# 4. GLOBAL STYLING (FIXES: UNIFORM BUTTONS & STRICT METRIC CENTERING)
style_html = f"""
<head>
<link rel="apple-touch-icon" sizes="180x180" href="{APP_ICON_URL}">
<link rel="apple-touch-icon-precomposed" href="{APP_ICON_URL}">
<link rel="icon" type="image/png" sizes="192x192" href="{APP_ICON_URL}">
<link rel="shortcut icon" href="{APP_ICON_URL}">
<meta name="apple-mobile-web-app-title" content="Derby Penguins App">
<meta name="apple-mobile-web-app-capable" content="yes">
</head>
<style>
html, body, [class*="css"], .stApp {{
    text-align: center !important;
    background-color: #0e1117 !important;
}}
.block-container, div[class*="stMainBlockContainer"], .stAppViewBlockContainer {{
    padding-top: 2rem !important; 
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    max-width: 1000px !important;
    margin: 0 auto !important;
    overflow: visible !important;
}}
h1, h2, h3, h4, h5, h6, p, label, div {{
    text-align: center !important;
}}

/* FORCE EVEN GRID & SIDE-BY-SIDE KPI CARDS */
div[data-testid="stHorizontalBlock"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    align-items: stretch !important;
}}
div[data-testid="stHorizontalBlock"] > div {{
    flex: 1 1 0px !important;
    min-width: 0 !important;
}}

/* HEADER LOGO UNCLIPPING FIX */
.header-logo-container {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    margin-top: 10px !important;
    margin-bottom: 5px !important;
    padding-top: 5px !important;
    overflow: visible !important;
}}
.header-logo {{
    filter: invert(1);
    max-height: 65px !important;
    width: auto !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 auto !important;
}}

/* UNIFORM BUTTON SIZING FOR ALL NAV & SUBTAB BUTTONS */
div.stButton > button {{
    width: 100% !important;
    height: 40px !important;
    min-height: 40px !important;
    max-height: 40px !important;
    padding: 2px 2px !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

div.stButton > button p {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    font-size: 0.75rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

/* Active Page Button Style */
div.stButton > button[kind="primary"] {{
    background-color: #22252e !important;
    color: #FFB81C !important;
    border: 1px solid #FFB81C !important;
    box-shadow: 0 0 8px rgba(255, 184, 28, 0.2) !important;
}}

/* Inactive Page Button Style */
div.stButton > button[kind="secondary"] {{
    background-color: #1a1c23 !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
}}

div.stButton > button[kind="secondary"]:hover {{
    border-color: #FFB81C !important;
    color: #FFB81C !important;
    background-color: #22252e !important;
}}

/* STRICT CENTER ALIGNMENT FOR METRIC CARDS / KPI */
[data-testid="stMetric"] {{
    background-color: #1a1c23 !important;
    border-radius: 8px !important;
    padding: 8px 4px !important;
    border: 1px solid #333 !important;
    text-align: center !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 65px !important;
}}

[data-testid="stMetric"] > div {{
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.75rem !important;
    color: #d1d5db !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
    display: flex !important;
}}

[data-testid="stMetricLabel"] * {{
    text-align: center !important;
    justify-content: center !important;
}}

[data-testid="stMetricValue"] {{
    color: #FFB81C !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    white-space: normal !important;
    word-break: break-word !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
}}

[data-testid="stMetricValue"] * {{
    text-align: center !important;
    justify-content: center !important;
    margin: 0 auto !important;
}}

[data-testid="stMetricDelta"] {{
    font-size: 0.75rem !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
    display: flex !important;
}}

[data-testid="stVideo"] {{
    max-width: 480px !important;
    margin: 0 auto !important;
    width: 100% !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}}

.mobile-table-container {{
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin-top: 10px;
    margin-bottom: 20px;
}}
</style>
"""

# 5. TOP HEADER LOGO
header_html = f"""
<div class="header-logo-container">
    <img src="{HEADER_LOGO_URL}" class="header-logo" alt="Derby Penguins Logo">
</div>
<h1 style="margin-top: 2px; margin-bottom: 10px; font-size: 1.25rem;">Derby Penguins FC</h1>
"""
render_html(header_html)

# 6. SPREADSHEET DATA LOADER
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
    return re.sub(r"\d+$", "", str(pos))


def render_page_header(title, img_url=None, invert=False):
    if img_url:
        invert_style = "filter: invert(1);" if invert else ""
        render_html(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 12px; margin-top: 5px;">
            <img src="{img_url}" style="height: 32px; width: auto; object-fit: contain; {invert_style}">
            <h2 style="margin: 0; padding: 0; font-size: 1.4rem; font-weight: 700; color: #ffffff;">{title}</h2>
        </div>
        """)
    else:
        render_html(
            f"<h2 style='text-align: center; margin-bottom: 12px;'>{title}</h2>"
        )


pages_config = [
    ("🏠 Home", "Homepage", None),
    ("🐧 Penguins 🐧", "Penguins", None),
    ("🐧 Socials 🐧", "Socials", None),
    ("🐧 Community 🐧", "Community", None),
    ("🐧 Club 🐧", "Club", None),
    ("ℹ️ About", "About Us", None),
]


def nav_button(label, key, logo_url, column):
    is_active = current_page == key
    btn_type = "primary" if is_active else "secondary"

    if logo_url:
        button_label = f"![logo]({logo_url}) {label}"
    else:
        button_label = label

    if column.button(
        button_label,
        key=f"top_nav_{key}",
        use_container_width=True,
        type=btn_type,
    ):
        st.session_state["active_page"] = key
        st.rerun()


# Row 1
row1_cols = st.columns(3)

for idx, (label, key, logo_url) in enumerate(pages_config[:3]):
    nav_button(label, key, logo_url, row1_cols[idx])


# Row 2
row2_cols = st.columns(3)

for idx, (label, key, logo_url) in enumerate(pages_config[3:]):
    nav_button(label, key, logo_url, row2_cols[idx])

st.divider()


# Sub-tab Navigation Helper Function using Native Buttons
def render_subtab_cards(team_key, has_match_center=True):
    tabs = (
        ["Player Stats", "Results", "Match Center", "News"]
        if has_match_center
        else ["Combined Stats", "Club Schedule", "Club News"]
    )
    current_subtab = st.session_state.get(f"{team_key}_subtab", tabs[0])

    sub_cols = st.columns(len(tabs))
    for idx, tab_name in enumerate(tabs):
        btn_label = (
            f"📊 Stats"
            if "Stats" in tab_name
            else (
                f"📅 Results"
                if "Results" in tab_name
                else (
                    f"📅 Schedule"
                    if "Schedule" in tab_name
                    else f"⚽ Match Centre" if "Match" in tab_name else f"📰 News"
                )
            )
        )
        is_active = current_subtab == tab_name
        btn_type = "primary" if is_active else "secondary"

        if sub_cols[idx].button(
            btn_label,
            key=f"sub_nav_{team_key}_{tab_name}",
            use_container_width=True,
            type=btn_type,
        ):
            st.session_state[f"{team_key}_subtab"] = tab_name
            st.rerun()

    return st.session_state.get(f"{team_key}_subtab", tabs[0])


# ==========================================
# --- 1. HOMEPAGE ---
# ==========================================
if current_page == "Homepage":

    st.markdown("### 🎥 Feature Video")
    st.video(VIDEO_URL)

    st.divider()

    st.markdown("### 📲 Latest Club Updates")
    fb_page_url = (
        "https://www.facebook.com/p/Derby-Penguins-FC-61568730025829/"
    )

    fb_iframe = f"""<div style="display: flex; justify-content: center; width: 100%; overflow: hidden;"><div style="width: 100%; max-width: 500px; overflow: hidden; border-radius: 8px; background: #111;"><iframe src="https://www.facebook.com/plugins/page.php?href={fb_page_url}&tabs=timeline&width=340&height=650&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true" width="100%" height="650" style="border:none; overflow:hidden; max-width: 100vw;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe></div></div>"""
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
            games_df = load_sheet("Socials_Games")
            goals_df = load_sheet("Socials_Goals")

            # Non-player metadata columns in Games sheet
            meta_cols = {
                "gameid",
                "date",
                "location",
                "opponent",
                "ko time",
                "result",
                "outcome",
                "formation",
                "motm",
                "venue",
                "home/away",
            }

            player_apps = {}
            player_goals = {}
            player_assists = {}

            # Calculate Appearances from Socials_Games
            if not games_df.empty:
                player_cols = [
                    c for c in games_df.columns if c.strip().lower() not in meta_cols
                ]
                for _, row in games_df.iterrows():
                    game_players = set()
                    for col in player_cols:
                        val = str(row[col]).strip() if pd.notnull(row[col]) else ""
                        if val and val.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unknown",
                        ]:
                            game_players.add(val)
                    for p in game_players:
                        player_apps[p] = player_apps.get(p, 0) + 1

            # Calculate Goals and Assists from Socials_Goals
            if not goals_df.empty:
                scorer_col = (
                    "Goalscorer"
                    if "Goalscorer" in goals_df.columns
                    else ("Scorer" if "Scorer" in goals_df.columns else None)
                )
                assist_col = "Assist" if "Assist" in goals_df.columns else None

                if scorer_col:
                    for val in goals_df[scorer_col]:
                        p = str(val).strip() if pd.notnull(val) else ""
                        if p and p.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unknown",
                            "own goal",
                            "og",
                        ]:
                            player_goals[p] = player_goals.get(p, 0) + 1

                if assist_col:
                    for val in goals_df[assist_col]:
                        p = str(val).strip() if pd.notnull(val) else ""
                        if p and p.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unassisted",
                            "unknown",
                        ]:
                            player_assists[p] = player_assists.get(p, 0) + 1

            all_players = (
                set(player_apps.keys())
                .union(player_goals.keys())
                .union(player_assists.keys())
            )

            stats_list = []
            for p in all_players:
                apps = player_apps.get(p, 0)
                g = player_goals.get(p, 0)
                a = player_assists.get(p, 0)
                gi = g + a
                gpg = round(g / apps, 2) if apps > 0 else 0.0
                apg = round(a / apps, 2) if apps > 0 else 0.0
                gipg = round(gi / apps, 2) if apps > 0 else 0.0

                stats_list.append(
                    {
                        "Player": p,
                        "Appearances": apps,
                        "Goals": g,
                        "Assists": a,
                        "Goal Involvements": gi,
                        "Goals Per Game": gpg,
                        "Assists Per Game": apg,
                        "Goal Involvements Per Game": gipg,
                    }
                )

            df = pd.DataFrame(stats_list)
            if df.empty:
                df = pd.DataFrame(
                    columns=[
                        "Player",
                        "Appearances",
                        "Goals",
                        "Assists",
                        "Goal Involvements",
                        "Goals Per Game",
                        "Assists Per Game",
                        "Goal Involvements Per Game",
                    ]
                )

            top_apps = (
                df.sort_values(by="Appearances", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_scorer = (
                df.sort_values(by="Goals", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_assister = (
                df.sort_values(by="Assists", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_involvements = (
                df.sort_values(by="Goal Involvements", ascending=False).iloc[0]
                if not df.empty
                else None
            )

            row1_col1, row1_col2 = st.columns(2)
            row1_col1.metric(
                "🏃 Apps Leader",
                f"{top_apps['Player']}" if top_apps is not None else "-",
                f"{top_apps['Appearances']} Apps" if top_apps is not None else "0 Apps",
            )
            row1_col2.metric(
                "⚽ Top Scorer",
                f"{top_scorer['Player']}" if top_scorer is not None else "-",
                f"{top_scorer['Goals']} Goals" if top_scorer is not None else "0 Goals",
            )

            row2_col1, row2_col2 = st.columns(2)
            row2_col1.metric(
                "🅰️ Top Assister",
                f"{top_assister['Player']}" if top_assister is not None else "-",
                f"{top_assister['Assists']} Assists"
                if top_assister is not None
                else "0 Assists",
            )
            row2_col2.metric(
                "🔥 Top Contributor",
                f"{top_involvements['Player']}" if top_involvements is not None else "-",
                f"{top_involvements['Goal Involvements']} G+A"
                if top_involvements is not None
                else "0 G+A",
            )

            st.divider()

            st.markdown("### Socials Player Stats")

            search_query = st.text_input("🔍 Search Player", "")
            sort_by = st.selectbox(
                "Sort By Column", options=df.columns, index=1
            )
            sort_order = st.radio(
                "Order", ["Descending", "Ascending"], horizontal=True
            )

            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df["Player"].str.contains(
                        search_query, case=False, na=False
                    )
                ]

            ascending = True if sort_order == "Ascending" else False
            filtered_df = filtered_df.sort_values(
                by=sort_by, ascending=ascending
            ).reset_index(drop=True)

            table_html = "<div class='mobile-table-container'><table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 650px;'><tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
            for col in filtered_df.columns:
                table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center; font-size: 12px;'>{col}</th>"
            table_html += "</tr>"

            for idx, row in filtered_df.iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in filtered_df.columns:
                    val = row[col]
                    if pd.isnull(val):
                        formatted_val = "-"
                    elif isinstance(val, (int, float)):
                        if val % 1 == 0:
                            formatted_val = f"{int(val)}"
                        else:
                            formatted_val = f"{val:.2f}"
                    else:
                        formatted_val = str(val)
                    table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                table_html += "</tr>"
            table_html += "</table></div>"

            render_html(table_html)

        except Exception as e:
            st.error(f"Error loading stats: {e}")

    elif subtab == "Results":
        try:
            games_df = load_sheet("Socials_Games")
            target_cols = [
                "GameID",
                "Date",
                "Location",
                "Opponent",
                "KO Time",
                "Result",
                "Outcome",
            ]
            display_cols = [c for c in target_cols if c in games_df.columns]
            if not display_cols:
                display_cols = list(games_df.columns[:7])

            fixtures_df = (
                games_df[display_cols].copy().dropna(subset=[display_cols[0]])
            )

            f_table_html = "<div class='mobile-table-container'><table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 500px;'><tr style='background-color: #FFB81C; color: #111; font-weight: bold; font-size: 12px;'>"
            for col in fixtures_df.columns:
                f_table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center;'>{col}</th>"
            f_table_html += "</tr>"

            for idx, row in fixtures_df.reset_index(drop=True).iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                f_table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in fixtures_df.columns:
                    val = row[col]
                    formatted_val = (
                        "-"
                        if pd.isnull(val)
                        or str(val).strip().lower() in ["nan", "none", ""]
                        else str(val).strip()
                    )
                    f_table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                f_table_html += "</tr>"
            f_table_html += "</table></div>"

            render_html(f_table_html)

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
                    if (
                        "home" in col_lower
                        or "away" in col_lower
                        or col_lower == "venue"
                    ):
                        venue_val = str(row[col]).strip().lower()
                        break
                is_away = venue_val.startswith("a")

                if result and result.lower() != "nan":
                    if is_away:
                        scores = [s.strip() for s in result.split("-")]
                        match_title = (
                            f"{opponent} {scores[1]}-{scores[0]} Socials"
                            if len(scores) == 2
                            else f"{opponent} {result} Socials"
                        )
                    else:
                        match_title = f"Socials {result} {opponent}"
                else:
                    match_title = (
                        f"{opponent} vs Socials"
                        if is_away
                        else f"Socials vs {opponent}"
                    )
                return (
                    f"{match_title} ({date})"
                    if date and date.lower() != "nan"
                    else match_title
                )

            game_options = {
                create_game_label(row): row["GameID"]
                for _, row in games_df.iterrows()
            }
            options_list = list(game_options.keys())
            default_idx = len(options_list) - 1 if options_list else 0

            selected_label = st.selectbox(
                "Select Game:", options=options_list, index=default_idx
            )
            selected_game_id = game_options[selected_label]
            game_data = games_df[
                games_df["GameID"] == selected_game_id
            ].iloc[0]

            raw_motm = str(game_data.get("MOTM", "")).strip()
            motm_val = (
                raw_motm
                if raw_motm and raw_motm.lower() not in ["nan", "none", "-"]
                else "-"
            )

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
            m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))

            m_col3, m_col4 = st.columns(2)
            m_col3.metric("⚽ Score", str(game_data.get("Result", "-")))
            m_col4.metric("🏆 MOTM", motm_val)

            st.divider()

            # LINEUP PITCH VIEW
            formation = str(game_data.get("Formation", "4-3-3")).strip()
            st.subheader(f"Match Lineup ({formation})")

            goal_counts, assist_counts = {}, {}
            try:
                goals_df = load_sheet("Socials_Goals")
                match_col = (
                    "Match ID" if "Match ID" in goals_df.columns else "GameID"
                )
                match_goals = goals_df[
                    goals_df[match_col].astype(str) == str(selected_game_id)
                ]

                if not match_goals.empty:
                    for _, row in match_goals.iterrows():
                        scorer = str(
                            row.get("Goalscorer", row.get("Scorer", ""))
                        ).strip()
                        assist = str(row.get("Assist", "")).strip()
                        if scorer and scorer.lower() not in [
                            "unknown",
                            "none",
                            "-",
                            "nan",
                            "",
                        ]:
                            goal_counts[scorer] = goal_counts.get(scorer, 0) + 1
                        if assist and assist.lower() not in [
                            "none",
                            "-",
                            "unassisted",
                            "nan",
                            "",
                        ]:
                            assist_counts[assist] = (
                                assist_counts.get(assist, 0) + 1
                            )
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
                if (
                    pd.notnull(val)
                    and str(val).strip().lower() not in ["", "-", "nan", "none"]
                ):
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
                badge_html = (
                    f'<div style="font-size: 7px; margin-top: 1px; line-height: 1;">{" ".join(icons)}</div>'
                    if icons
                    else ""
                )

                return f"""<div style="background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 2px 2px; margin: 1px; text-align: center; flex: 1 1 0px; min-width: 0; box-sizing: border-box; overflow: hidden;"><div style="font-size: 7px; color: #FFB81C; font-weight: bold; line-height: 1;">{c_pos}</div><div style="font-size: 8.5px; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.1;">{name}</div>{badge_html}</div>"""

            gk_html = "".join(
                [make_player_card(k, lineup[k]) for k in lineup if k == "GK"]
            )
            def_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in def_order
                    if k in lineup
                ]
            )
            cdm_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in cdm_order
                    if k in lineup
                ]
            )
            mid_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in mid_order
                    if k in lineup
                ]
            )
            cam_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in cam_order
                    if k in lineup
                ]
            )
            att_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in att_order
                    if k in lineup
                ]
            )

            subs_raw = [game_data.get(f"SUB{i}") for i in range(1, 10)]
            active_subs = [
                str(s).strip()
                for s in subs_raw
                if pd.notnull(s)
                and str(s).strip().lower() not in ["", "-", "nan", "none"]
            ]
            subs_html = (
                "".join(
                    [
                        make_player_card("SUB", sub_name)
                        for sub_name in active_subs
                    ]
                )
                if active_subs
                else "<div style='font-size: 8px; color: #666;'>No substitutes listed</div>"
            )

            pitch_component = f"""<!DOCTYPE html><html><head><style>
            body {{ margin: 0; font-family: sans-serif; background-color: transparent; }}
            .pitch-frame {{ background: #181a20; border: 2px solid #FFB81C; border-radius: 8px; box-sizing: border-box; width: 100%; overflow: hidden; }}
            .pitch {{ padding: 8px 2px 10px 2px; position: relative; box-sizing: border-box; min-height: 400px; display: flex; flex-direction: column; justify-content: space-between; }}
            .halfway-line {{ position: absolute; top: 50%; left: 0; right: 0; border-top: 1px dashed rgba(255, 184, 28, 0.3); }}
            .pitch-row {{ display: flex; justify-content: space-around; align-items: center; width: 100%; z-index: 2; margin: 2px 0; }}
            .subs-section {{ background: #111; padding: 6px; border-top: 1px solid #333; width: 100%; box-sizing: border-box; }}
            </style></head>
            <body>
            <div class="pitch-frame">
                <div class="pitch">
                    <div class="halfway-line"></div>
                    <div class="pitch-row">{att_html}</div>
                    <div class="pitch-row">{cam_html}</div>
                    <div class="pitch-row">{mid_html}</div>
                    <div class="pitch-row">{cdm_html}</div>
                    <div class="pitch-row">{def_html}</div>
                    <div class="pitch-row">{gk_html}</div>
                </div>
                <div class="subs-section">
                    <div style="font-size: 9px; color: #FFB81C; font-weight: bold; margin-bottom: 4px; text-align: center;">SUBSTITUTES</div>
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2px;">{subs_html}</div>
                </div>
            </div>
            </body></html>"""

            components.html(pitch_component, height=520, scrolling=False)

        except Exception as e:
            st.error(f"Error loading Match Center data: {e}")

    elif subtab == "News":
        st.info("Socials team announcements coming soon.")


# ==========================================
# --- 4. DERBY PENGUINS COMMUNITY ---
# ==========================================
elif current_page == "Community":
    render_page_header("Derby Penguins Community", WHITE_COMMUNITY_LOGO_URL, invert=False)
    subtab = render_subtab_cards("Community")

    if subtab == "Player Stats":
        try:
            games_df = load_sheet("Community_Games")
            goals_df = load_sheet("Community_Goals")

            # Non-player metadata columns in Games sheet
            meta_cols = {
                "gameid",
                "date",
                "location",
                "opponent",
                "ko time",
                "result",
                "outcome",
                "formation",
                "motm",
                "venue",
                "home/away",
            }

            player_apps = {}
            player_goals = {}
            player_assists = {}

            # Calculate Appearances from Community_Games
            if not games_df.empty:
                player_cols = [
                    c for c in games_df.columns if c.strip().lower() not in meta_cols
                ]
                for _, row in games_df.iterrows():
                    game_players = set()
                    for col in player_cols:
                        val = str(row[col]).strip() if pd.notnull(row[col]) else ""
                        if val and val.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unknown",
                        ]:
                            game_players.add(val)
                    for p in game_players:
                        player_apps[p] = player_apps.get(p, 0) + 1

            # Calculate Goals and Assists from Community_Goals
            if not goals_df.empty:
                scorer_col = (
                    "Goalscorer"
                    if "Goalscorer" in goals_df.columns
                    else ("Scorer" if "Scorer" in goals_df.columns else None)
                )
                assist_col = "Assist" if "Assist" in goals_df.columns else None

                if scorer_col:
                    for val in goals_df[scorer_col]:
                        p = str(val).strip() if pd.notnull(val) else ""
                        if p and p.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unknown",
                            "own goal",
                            "og",
                        ]:
                            player_goals[p] = player_goals.get(p, 0) + 1

                if assist_col:
                    for val in goals_df[assist_col]:
                        p = str(val).strip() if pd.notnull(val) else ""
                        if p and p.lower() not in [
                            "nan",
                            "none",
                            "",
                            "-",
                            "unassisted",
                            "unknown",
                        ]:
                            player_assists[p] = player_assists.get(p, 0) + 1

            all_players = (
                set(player_apps.keys())
                .union(player_goals.keys())
                .union(player_assists.keys())
            )

            stats_list = []
            for p in all_players:
                apps = player_apps.get(p, 0)
                g = player_goals.get(p, 0)
                a = player_assists.get(p, 0)
                gi = g + a
                gpg = round(g / apps, 2) if apps > 0 else 0.0
                apg = round(a / apps, 2) if apps > 0 else 0.0
                gipg = round(gi / apps, 2) if apps > 0 else 0.0

                stats_list.append(
                    {
                        "Player": p,
                        "Appearances": apps,
                        "Goals": g,
                        "Assists": a,
                        "Goal Involvements": gi,
                        "Goals Per Game": gpg,
                        "Assists Per Game": apg,
                        "Goal Involvements Per Game": gipg,
                    }
                )

            df = pd.DataFrame(stats_list)
            if df.empty:
                df = pd.DataFrame(
                    columns=[
                        "Player",
                        "Appearances",
                        "Goals",
                        "Assists",
                        "Goal Involvements",
                        "Goals Per Game",
                        "Assists Per Game",
                        "Goal Involvements Per Game",
                    ]
                )

            top_apps = (
                df.sort_values(by="Appearances", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_scorer = (
                df.sort_values(by="Goals", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_assister = (
                df.sort_values(by="Assists", ascending=False).iloc[0]
                if not df.empty
                else None
            )
            top_involvements = (
                df.sort_values(by="Goal Involvements", ascending=False).iloc[0]
                if not df.empty
                else None
            )

            row1_col1, row1_col2 = st.columns(2)
            row1_col1.metric(
                "🏃 Apps Leader",
                f"{top_apps['Player']}" if top_apps is not None else "-",
                f"{top_apps['Appearances']} Apps" if top_apps is not None else "0 Apps",
            )
            row1_col2.metric(
                "⚽ Top Scorer",
                f"{top_scorer['Player']}" if top_scorer is not None else "-",
                f"{top_scorer['Goals']} Goals" if top_scorer is not None else "0 Goals",
            )

            row2_col1, row2_col2 = st.columns(2)
            row2_col1.metric(
                "🅰️ Top Assister",
                f"{top_assister['Player']}" if top_assister is not None else "-",
                f"{top_assister['Assists']} Assists"
                if top_assister is not None
                else "0 Assists",
            )
            row2_col2.metric(
                "🔥 Top Contributor",
                f"{top_involvements['Player']}" if top_involvements is not None else "-",
                f"{top_involvements['Goal Involvements']} G+A"
                if top_involvements is not None
                else "0 G+A",
            )

            st.divider()

            st.markdown("### Community Player Stats")

            search_query = st.text_input("🔍 Search Player", "")
            sort_by = st.selectbox(
                "Sort By Column", options=df.columns, index=1
            )
            sort_order = st.radio(
                "Order", ["Descending", "Ascending"], horizontal=True
            )

            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df["Player"].str.contains(
                        search_query, case=False, na=False
                    )
                ]

            ascending = True if sort_order == "Ascending" else False
            filtered_df = filtered_df.sort_values(
                by=sort_by, ascending=ascending
            ).reset_index(drop=True)

            table_html = "<div class='mobile-table-container'><table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 650px;'><tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
            for col in filtered_df.columns:
                table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center; font-size: 12px;'>{col}</th>"
            table_html += "</tr>"

            for idx, row in filtered_df.iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in filtered_df.columns:
                    val = row[col]
                    if pd.isnull(val):
                        formatted_val = "-"
                    elif isinstance(val, (int, float)):
                        if val % 1 == 0:
                            formatted_val = f"{int(val)}"
                        else:
                            formatted_val = f"{val:.2f}"
                    else:
                        formatted_val = str(val)
                    table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                table_html += "</tr>"
            table_html += "</table></div>"

            render_html(table_html)

        except Exception as e:
            st.error(f"Error loading stats: {e}")

    elif subtab == "Results":
        try:
            games_df = load_sheet("Community_Games")
            target_cols = [
                "GameID",
                "Date",
                "Location",
                "Opponent",
                "KO Time",
                "Result",
                "Outcome",
            ]
            display_cols = [c for c in target_cols if c in games_df.columns]
            if not display_cols:
                display_cols = list(games_df.columns[:7])

            fixtures_df = (
                games_df[display_cols].copy().dropna(subset=[display_cols[0]])
            )

            f_table_html = "<div class='mobile-table-container'><table style='width:100%; border-collapse: collapse; text-align: center; font-family: sans-serif; min-width: 500px;'><tr style='background-color: #FFB81C; color: #111; font-weight: bold; font-size: 12px;'>"
            for col in fixtures_df.columns:
                f_table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; text-align: center;'>{col}</th>"
            f_table_html += "</tr>"

            for idx, row in fixtures_df.reset_index(drop=True).iterrows():
                bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
                f_table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
                for col in fixtures_df.columns:
                    val = row[col]
                    formatted_val = (
                        "-"
                        if pd.isnull(val)
                        or str(val).strip().lower() in ["nan", "none", ""]
                        else str(val).strip()
                    )
                    f_table_html += f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; text-align: center;'>{formatted_val}</td>"
                f_table_html += "</tr>"
            f_table_html += "</table></div>"

            render_html(f_table_html)

        except Exception as e:
            st.error("Error loading results data.")

    elif subtab == "Match Center":
        try:
            games_df = load_sheet("Community_Games")

            def create_game_label(row):
                opponent = str(row.get("Opponent", "Unknown")).strip()
                result = str(row.get("Result", "")).strip()
                date = str(row.get("Date", "")).strip()
                venue_val = ""
                for col in row.index:
                    col_lower = str(col).strip().lower()
                    if (
                        "home" in col_lower
                        or "away" in col_lower
                        or col_lower == "venue"
                    ):
                        venue_val = str(row[col]).strip().lower()
                        break
                is_away = venue_val.startswith("a")

                if result and result.lower() != "nan":
                    if is_away:
                        scores = [s.strip() for s in result.split("-")]
                        match_title = (
                            f"{opponent} {scores[1]}-{scores[0]} Community"
                            if len(scores) == 2
                            else f"{opponent} {result} Community"
                        )
                    else:
                        match_title = f"Community {result} {opponent}"
                else:
                    match_title = (
                        f"{opponent} vs Community"
                        if is_away
                        else f"Community vs {opponent}"
                    )
                return (
                    f"{match_title} ({date})"
                    if date and date.lower() != "nan"
                    else match_title
                )

            game_options = {
                create_game_label(row): row["GameID"]
                for _, row in games_df.iterrows()
            }
            options_list = list(game_options.keys())
            default_idx = len(options_list) - 1 if options_list else 0

            selected_label = st.selectbox(
                "Select Game:", options=options_list, index=default_idx
            )
            selected_game_id = game_options[selected_label]
            game_data = games_df[
                games_df["GameID"] == selected_game_id
            ].iloc[0]

            raw_motm = str(game_data.get("MOTM", "")).strip()
            motm_val = (
                raw_motm
                if raw_motm and raw_motm.lower() not in ["nan", "none", "-"]
                else "-"
            )

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("🗓️ Date", str(game_data.get("Date", "-")))
            m_col2.metric("🛡️ Opponent", str(game_data.get("Opponent", "-")))

            m_col3, m_col4 = st.columns(2)
            m_col3.metric("⚽ Score", str(game_data.get("Result", "-")))
            m_col4.metric("🏆 MOTM", motm_val)

            st.divider()

            # LINEUP PITCH VIEW
            formation = str(game_data.get("Formation", "4-3-3")).strip()
            st.subheader(f"Match Lineup ({formation})")

            goal_counts, assist_counts = {}, {}
            try:
                goals_df = load_sheet("Community_Goals")
                match_col = (
                    "Match ID" if "Match ID" in goals_df.columns else "GameID"
                )
                match_goals = goals_df[
                    goals_df[match_col].astype(str) == str(selected_game_id)
                ]

                if not match_goals.empty:
                    for _, row in match_goals.iterrows():
                        scorer = str(
                            row.get("Goalscorer", row.get("Scorer", ""))
                        ).strip()
                        assist = str(row.get("Assist", "")).strip()
                        if scorer and scorer.lower() not in [
                            "unknown",
                            "none",
                            "-",
                            "nan",
                            "",
                        ]:
                            goal_counts[scorer] = goal_counts.get(scorer, 0) + 1
                        if assist and assist.lower() not in [
                            "none",
                            "-",
                            "unassisted",
                            "nan",
                            "",
                        ]:
                            assist_counts[assist] = (
                                assist_counts.get(assist, 0) + 1
                            )
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
                if (
                    pd.notnull(val)
                    and str(val).strip().lower() not in ["", "-", "nan", "none"]
                ):
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
                badge_html = (
                    f'<div style="font-size: 7px; margin-top: 1px; line-height: 1;">{" ".join(icons)}</div>'
                    if icons
                    else ""
                )

                return f"""<div style="background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 2px 2px; margin: 1px; text-align: center; flex: 1 1 0px; min-width: 0; box-sizing: border-box; overflow: hidden;"><div style="font-size: 7px; color: #FFB81C; font-weight: bold; line-height: 1;">{c_pos}</div><div style="font-size: 8.5px; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; line-height: 1.1;">{name}</div>{badge_html}</div>"""

            gk_html = "".join(
                [make_player_card(k, lineup[k]) for k in lineup if k == "GK"]
            )
            def_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in def_order
                    if k in lineup
                ]
            )
            cdm_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in cdm_order
                    if k in lineup
                ]
            )
            mid_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in mid_order
                    if k in lineup
                ]
            )
            cam_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in cam_order
                    if k in lineup
                ]
            )
            att_html = "".join(
                [
                    make_player_card(k, lineup[k])
                    for k in att_order
                    if k in lineup
                ]
            )

            subs_raw = [game_data.get(f"SUB{i}") for i in range(1, 10)]
            active_subs = [
                str(s).strip()
                for s in subs_raw
                if pd.notnull(s)
                and str(s).strip().lower() not in ["", "-", "nan", "none"]
            ]
            subs_html = (
                "".join(
                    [
                        make_player_card("SUB", sub_name)
                        for sub_name in active_subs
                    ]
                )
                if active_subs
                else "<div style='font-size: 8px; color: #666;'>No substitutes listed</div>"
            )

            pitch_component = f"""<!DOCTYPE html><html><head><style>
            body {{ margin: 0; font-family: sans-serif; background-color: transparent; }}
            .pitch-frame {{ background: #181a20; border: 2px solid #FFB81C; border-radius: 8px; box-sizing: border-box; width: 100%; overflow: hidden; }}
            .pitch {{ padding: 8px 2px 10px 2px; position: relative; box-sizing: border-box; min-height: 400px; display: flex; flex-direction: column; justify-content: space-between; }}
            .halfway-line {{ position: absolute; top: 50%; left: 0; right: 0; border-top: 1px dashed rgba(255, 184, 28, 0.3); }}
            .pitch-row {{ display: flex; justify-content: space-around; align-items: center; width: 100%; z-index: 2; margin: 2px 0; }}
            .subs-section {{ background: #111; padding: 6px; border-top: 1px solid #333; width: 100%; box-sizing: border-box; }}
            </style></head>
            <body>
            <div class="pitch-frame">
                <div class="pitch">
                    <div class="halfway-line"></div>
                    <div class="pitch-row">{att_html}</div>
                    <div class="pitch-row">{cam_html}</div>
                    <div class="pitch-row">{mid_html}</div>
                    <div class="pitch-row">{cdm_html}</div>
                    <div class="pitch-row">{def_html}</div>
                    <div class="pitch-row">{gk_html}</div>
                </div>
                <div class="subs-section">
                    <div style="font-size: 9px; color: #FFB81C; font-weight: bold; margin-bottom: 4px; text-align: center;">SUBSTITUTES</div>
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2px;">{subs_html}</div>
                </div>
            </div>
            </body></html>"""

            components.html(pitch_component, height=520, scrolling=False)

        except Exception as e:
            st.error(f"Error loading Match Center data: {e}")

    elif subtab == "News":
        st.info("Community team announcements coming soon.")


# ==========================================
# --- 5. DERBY PENGUINS CLUB ---
# ==========================================
elif current_page == "Club":
    render_page_header("Derby Penguins FC", HEADER_LOGO_URL, invert=True)
    subtab = render_subtab_cards("Club", has_match_center=False)

    if subtab == "Combined Stats":
        st.info("Combined overall club statistics coming soon.")
    elif subtab == "Club Schedule":
        st.info("Full club schedule and event calendar coming soon.")
    elif subtab == "Club News":
        st.info("Latest announcements across all club teams.")


# ==========================================
# --- 6. ABOUT US ---
# ==========================================
elif current_page == "About Us":
    render_page_header("About Derby Penguins FC")
    st.markdown("""
    Welcome to the official app for **Derby Penguins FC**! 
    
    Track player statistics, view detailed match center lineups, stay up-to-date with club results, and catch our latest videos and Facebook updates all in one place.
    """)
