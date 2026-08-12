import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re
from urllib.parse import quote_plus

# REPOSITORY LOGO URLS
CLUB_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/ClubLogo.jpeg"
SOCIALS_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/SocialsLogo.jpeg"
COMMUNITY_LOGO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/BlackCommunityLogo.jpeg"
VIDEO_URL = "https://raw.githubusercontent.com/adamlomasnffc/club-stats-app/main/a6e86bfe-69d7-4146-add8-2ba2d49c942b.MP4"

st.set_page_config(
    page_title="Derby Penguins App",
    page_icon=CLUB_LOGO_URL,
    layout="wide"
)

# TRUE HEAD INJECTOR FIX FOR IOS/SAFARI ICONS & ANTI-FLASH BACKGROUND LOCK
icon_injector = f"""
<script>
    const docHead = window.parent.document.querySelector('head');
    if (docHead) {{
        const existingIcons = docHead.querySelectorAll('link[rel*="icon"], link[rel*="apple-touch-icon"]');
        existingIcons.forEach(el => el.remove());

        const rels = ['apple-touch-icon', 'apple-touch-icon-precomposed', 'icon', 'shortcut icon'];
        rels.forEach(rel => {{
            let link = window.parent.document.createElement('link');
            link.rel = rel;
            link.href = "{CLUB_LOGO_URL}";
            if(rel.includes('icon')) {{
                link.type = 'image/jpeg';
                link.sizes = '192x192';
            }}
            docHead.appendChild(link);
        }});
        
        let meta = window.parent.document.createElement('meta');
        meta.name = "apple-mobile-web-app-capable";
        meta.content = "yes";
        docHead.appendChild(meta);
    }}
</script>
"""
components.html(icon_injector, height=0, width=0)

# Initialize Session State
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Homepage"

DEFAULT_SUBTABS = {
    "Penguins": "Player Stats",
    "Socials": "Player Stats",
    "Community": "Player Stats",
    "Club": "Combined Stats",
}
for team_key, default_tab in DEFAULT_SUBTABS.items():
    if f"{team_key}_subtag" not in st.session_state:
        st.session_state[f"{team_key}_subtag"] = default_tab

query_params = st.query_params
if "nav" in query_params:
    st.session_state["active_page"] = query_params["nav"]
if "team" in query_params and "tab" in query_params:
    st.session_state[f"{query_params['team']}_subtab"] = query_params["tab"]

# 2. GLOBAL STYLING (Forced dark background variables to prevent white flash)
st.markdown("""
    <style>
        /* Force dark background instantly on Streamlit framework layers */
        [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
            background-color: #0e1117 !important;
        }
        html, body, [class*="css"] {
            text-align: center !important;
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        .block-container, div[class*="stMainBlockContainer"], .stAppViewBlockContainer {
            padding-top: 3rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 1000px !important;
            margin: 0 auto !important;
        }
        h1, h2, h3, h4, h5, h6, p, label, div {
            text-align: center !important;
        }
        .header-logo-container {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin-bottom: 5px !important;
        }
        .header-logo {
            filter: invert(1);
            max-height: 60px !important;
            width: auto !important;
            object-fit: contain;
            display: block !important;
        }
        .dash-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            width: 100%;
            margin: 6px auto 14px auto;
        }
        .dash-grid.sub-grid {
            grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
        }
        .dash-tile {
            background-color: #1a1c23 !important;
            color: #ffffff !important;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 10px 2px;
            text-decoration: none !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            transition: all 0.15s ease-in-out;
            min-width: 0;
        }
        .dash-tile:hover {
            border-color: #FFB81C;
            color: #FFB81C !important;
            background-color: #22252e !important;
        }
        .dash-tile.active {
            background-color: #FFB81C !important;
            color: #111111 !important;
            border-color: #FFB81C;
        }
        .dash-tile.active .dash-img-icon {
            filter: invert(1);
        }
        .dash-icon {
            font-size: 1.25rem;
            line-height: 1.1;
            margin-bottom: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 24px;
        }
        .dash-img-icon {
            max-height: 22px;
            width: auto;
            object-fit: contain;
            display: block;
            filter: invert(1);
        }
        .page-heading-icon {
            max-height: 32px;
            width: auto;
            object-fit: contain;
            vertical-align: middle;
            margin-right: 8px;
            filter: invert(1);
        }
        .dash-label {
            font-size: 0.68rem;
            line-height: 1.15;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }
        .sub-grid .dash-tile {
            padding: 8px 2px;
        }
        .sub-grid .dash-icon {
            font-size: 1.05rem;
        }
        .sub-grid .dash-label {
            font-size: 0.6rem;
        }
        .video-container {
            max-width: 480px;
            margin: 0 auto;
            width: 100%;
        }
        .video-container video {
            width: 100% !important;
            max-height: 480px;
            border-radius: 8px;
            object-fit: contain;
        }
        [data-testid="stMetric"] {
            background-color: #1a1c23 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            border: 1px solid #333 !important;
            text-align: center !important;
        }
        [data-testid="stMetricValue"] {
            color: #FFB81C !important;
        }
        .mobile-table-container {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-top: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown(f"""
    <div class="header-logo-container">
        <img src="{CLUB_LOGO_URL}" class="header-logo" alt="Derby Penguins Logo">
    </div>
    <h1 style="margin-top: 2px; margin-bottom: 10px; font-size: 1.25rem;">Derby Penguins FC</h1>
""", unsafe_allow_html=True)

SPREADSHEET_ID = "19wTGruEyetdVNhfjkyVqLDueyV9joVtRsI51RAqurjA"

@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def clean_pos_label(pos):
    return re.sub(r'\d+$', '', pos)

pages_config = [
    ("🏠", "Home", "Homepage", False),
    (CLUB_LOGO_URL, "Penguins", "Penguins", True),
    (SOCIALS_LOGO_URL, "Socials", "Socials", True),
    (COMMUNITY_LOGO_URL, "Community", "Community", True),
    ("📊", "Club", "Club", False),
    ("ℹ️", "About", "About Us", False),
]

def render_nav_dashboard(active_page):
    tiles = ""
    for icon_item, label, key, is_img in pages_config:
        active_cls = " active" if active_page == key else ""
        if is_img:
            icon_html = f'<img src="{icon_item}" class="dash-img-icon" alt="{label}">'
        else:
            icon_html = icon_item
        
        tiles += f"""<a href="?nav={quote_plus(key)}" class="dash-tile{active_cls}">
            <div class="dash-icon">{icon_html}</div>
            <div class="dash-label">{label}</div>
        </a>"""
    st.markdown(f'<div class="dash-grid">{tiles}</div>', unsafe_allow_html=True)

render_nav_dashboard(st.session_state["active_page"])
st.divider()
current_page = st.session_state["active_page"]

def render_subtab_dashboard(team_key, has_match_center=True):
    if has_match_center:
        tabs = [("📊", "Player Stats"), ("📅", "Results"), ("⚽", "Match Center"), ("📰", "News")]
    else:
        tabs = [("📊", "Combined Stats"), ("📅", "Club Schedule"), ("📰", "Club News")]

    current_subtab = st.session_state.get(f"{team_key}_subtab", tabs[0][1])

    tiles = ""
    for icon, tab_name in tabs:
        active_cls = " active" if current_subtab == tab_name else ""
        href = f"?nav={quote_plus(team_key)}&team={quote_plus(team_key)}&tab={quote_plus(tab_name)}"
        tiles += f"""<a href="{href}" class="dash-tile{active_cls}">
            <div class="dash-icon">{icon}</div>
            <div class="dash-label">{tab_name}</div>
        </a>"""
    st.markdown(f'<div class="dash-grid sub-grid">{tiles}</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    return current_subtab

if current_page == "Homepage":
    st.markdown("### 🎥 Feature Video")
    st.markdown("<div class='video-container'>", unsafe_allow_html=True)
    st.video(VIDEO_URL)
    st.markdown("</div>", unsafe_allow_html=True)
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

elif current_page == "Penguins":
    st.markdown(f"## <img src='{CLUB_LOGO_URL}' class='page-heading-icon'> Derby Penguins", unsafe_allow_html=True)
    subtab = render_subtab_dashboard("Penguins")
    if subtab == "Player Stats": st.info("First team player stats will be populated here.")
    elif subtab == "Results": st.info("First team results and fixtures coming soon.")
    elif subtab == "Match Center": st.info("First team lineup pitch and goal logs coming soon.")
    elif subtab == "News": st.info("First team announcements.")

elif current_page == "Socials":
    st.markdown(f"## <img src='{SOCIALS_LOGO_URL}' class='page-heading-icon'> Derby Penguins Socials", unsafe_allow_html=True)
    subtab = render_subtab_dashboard("Socials")
    if subtab == "Player Stats":
        try:
            df = load_sheet("Socials_Player_Stats").iloc[:, :8]
            if "Player" in df.columns: df = df.dropna(subset=["Player"])
            top_apps = df.sort_values(by="Appearances", ascending=False).iloc[0]
            top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
            top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
            top_involvements = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]

            row1_col1, row1_col2 = st.columns(2)
            row1_col1.metric("🏃 Apps Leader", f"{top_apps['Player']}", f"{int(top_apps['Appearances'])} Apps")
            row1_col2.metric("⚽ Top Scorer", f"{top_scorer['Player']}", f"{int(top_scorer['Goals'])} Goals")
            row2_col1, row2_col2 = st.columns(2)
            row2_col1.metric("🅰️ Top Assister", f"{top_assister['Player']}", f"{int(top_assister['Assists'])} Assists")
            row2_col2.metric("🔥 Top Contributor", f"{top_involvements['Player']}", f"{int(top_involvements['Goal Involvements'])} G+A")

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
            st.exception(e)

elif current_page == "Community":
    st.markdown(f"## <img src='{COMMUNITY_LOGO_URL}' class='page-heading-icon'> Derby Penguins Community", unsafe_allow_html=True)
    subtab = render_subtab_dashboard("Community")
    st.info("Community stats coming soon.")

elif current_page == "Club":
    st.markdown("## 📊 Derby Penguins Club Overview")
    subtab = render_subtab_dashboard("Club", has_match_center=False)
    st.info("Combined stats across all squads will be displayed here.")

elif current_page == "About Us":
    st.markdown("## ℹ️ About Derby Penguins")
    st.markdown("""
        <div style="background-color: #1a1c23; border: 1px solid #333; border-radius: 10px; padding: 20px; max-width: 600px; margin: 0 auto; text-align: center;">
            <p style="color: #FFB81C; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;">Our Ethos</p>
            <p style="margin-bottom: 15px; font-size: 0.9rem;">At Derby Penguins, we are dedicated to grassroots football, sportsmanship, and building a supportive team community on and off the pitch.</p>
        </div>
    """, unsafe_allow_html=True)
