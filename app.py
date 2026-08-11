import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Derby Penguins - Match Center",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Comprehensive CSS Rules
st.markdown(
    """
    <style>
    /* Global Container Overflow Prevention */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }

    /* 1. TIGHT & COMPACT CARDS (Prevents wide scrolling) */
    .compact-card-grid {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 12px;
    }

    .compact-card {
        flex: 1 1 calc(20% - 6px);
        min-width: 85px !important;
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 6px 4px !important;
        text-align: center;
        box-sizing: border-box !important;
    }

    .compact-card-label {
        font-size: 0.70rem !important;
        color: #aaaaaa;
        text-transform: uppercase;
        margin-bottom: 2px;
        white-space: nowrap;
    }

    .compact-card-value {
        font-size: 1.0rem !important;
        font-weight: bold;
        color: #ffd700; /* Gold Accent */
    }

    /* 2. Tactical Pitch Styling */
    .pitch-container {
        background-color: #2e7d32;
        border: 2px solid #ffffff;
        border-radius: 10px;
        padding: 15px;
        position: relative;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .pitch-line {
        border-top: 2px dashed rgba(255, 255, 255, 0.4);
        margin: 15px 0;
    }

    .player-node {
        background-color: rgba(0, 0, 0, 0.75);
        border: 1px solid #ffd700;
        border-radius: 6px;
        color: white;
        padding: 4px 6px;
        text-align: center;
        font-size: 0.8rem;
        margin: 2px;
    }

    /* 3. NEWSFEED RIGHT-EDGE FIX */
    .newsfeed-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    .newsfeed-wrapper iframe {
        width: 100% !important;
        max-width: 100% !important;
        border: none !important;
        box-sizing: border-box !important;
    }

    /* 4. VERTICAL SOCIAL STATS STACK */
    .social-card-vertical {
        background-color: #181818;
        border-left: 4px solid #ffd700;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 4px;
    }

    .social-card-label {
        font-size: 0.75rem;
        color: #bbbbbb;
    }

    .social-card-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- HEADER SECTION ---
st.title("🐧 Derby Penguins Match Center")

# --- MAIN PAGE LAYOUT ---
col_main, col_side = st.columns([2.2, 1], gap="medium")

with col_main:
    # --- SEARCH & SORT CONTROLS (Stacked Vertically) ---
    st.subheader("Player Search & Controls")
    name_search = st.text_input(
        "Search Name", placeholder="Type player name...", key="search_input"
    )
    sort_by = st.selectbox(
        "Sort By",
        ["Goals", "Assists", "Rating", "Name", "Appearances"],
        key="sort_select",
    )

    st.markdown("---")

    # --- COMPACT CARDS (Tight grid, no side scrolling) ---
    st.markdown(
        """
        <div class="compact-card-grid">
            <div class="compact-card">
                <div class="compact-card-label">Top Scorer</div>
                <div class="compact-card-value">⚽ 12</div>
            </div>
            <div class="compact-card">
                <div class="compact-card-label">Top Assists</div>
                <div class="compact-card-value">🅰️ 8</div>
            </div>
            <div class="compact-card">
                <div class="compact-card-label">Matches</div>
                <div class="compact-card-value">15</div>
            </div>
            <div class="compact-card">
                <div class="compact-card-label">Clean Sheets</div>
                <div class="compact-card-value">5</div>
            </div>
            <div class="compact-card">
                <div class="compact-card-label">Win Rate</div>
                <div class="compact-card-value">68%</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- TACTICAL PITCH VISUALIZER ---
    st.subheader("Tactical Pitch Lineup")

    # Sample player pitch arrangement (5-tier grid representation)
    st.markdown(
        """
        <div class="pitch-container">
            <!-- Attackers -->
            <div style="display: flex; justify-content: space-around;">
                <div class="player-node">ST: J. Smith ⚽⚽</div>
                <div class="player-node">CF: A. Taylor ⚽🅰️</div>
            </div>
            <div class="pitch-line"></div>
            <!-- Midfielders -->
            <div style="display: flex; justify-content: space-around;">
                <div class="player-node">LM: M. Jones</div>
                <div class="player-node">CM: D. Davies 🅰️</div>
                <div class="player-node">RM: C. Wilson</div>
            </div>
            <div class="pitch-line"></div>
            <!-- Defenders -->
            <div style="display: flex; justify-content: space-around;">
                <div class="player-node">LB: R. Brown</div>
                <div class="player-node">CB: T. Evans</div>
                <div class="player-node">CB: K. Thomas</div>
                <div class="player-node">RB: S. Roberts</div>
            </div>
            <div class="pitch-line"></div>
            <!-- Goalkeeper -->
            <div style="display: flex; justify-content: center;">
                <div class="player-node" style="border-color: #00e676;">GK: P. Walker</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # --- SUBSTITUTES SECTION ---
    with st.expander("🔄 Substitutes & Bench", expanded=True):
        st.markdown(
            "- **SUB 1:** B. Johnson (65' ⚽)\n- **SUB 2:** H. White\n- **SUB 3:** L. Harris"
        )

    # --- FEATURE VIDEO PLAYER ---
    st.subheader("🎬 Match Highlights & Media")
    # Replace the sample URL with your GitHub raw video link or local video file path
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")

with col_side:
    # --- SOCIAL STATS (Stacked Vertically) ---
    st.subheader("📊 Social Stats")

    st.markdown(
        """
        <div class="social-card-vertical">
            <div class="social-card-label">Facebook Page Likes</div>
            <div class="social-card-value">1,240</div>
        </div>
        <div class="social-card-vertical">
            <div class="social-card-label">Weekly Reach</div>
            <div class="social-card-value">8.4K</div>
        </div>
        <div class="social-card-vertical">
            <div class="social-card-label">Post Engagement</div>
            <div class="social-card-value">3,850</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # --- EMBEDDED FACEBOOK NEWSFEED (No right clipping) ---
    st.subheader("📰 Facebook Feed")
    st.markdown(
        """
        <div class="newsfeed-wrapper">
            <iframe 
                src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Ffacebook&tabs=timeline&width=340&height=600&small_header=true&adapt_container_width=true&hide_cover=true&show_facepile=false" 
                height="600" 
                style="border:none;overflow:hidden;" 
                scrolling="no" 
                frameborder="0" 
                allowfullscreen="true" 
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share">
            </iframe>
        </div>
    """,
        unsafe_allow_html=True,
    )
