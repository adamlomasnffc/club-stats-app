import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Club Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Global Custom CSS Fixes
st.markdown(
    """
    <style>
    /* Prevent overall horizontal page overflow */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }

    /* 1. Compact Grid for Cards (Tight, visible without side scrolling) */
    .card-container {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)) !important;
        gap: 6px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 15px;
    }

    .card {
        padding: 6px 8px !important;
        font-size: 0.8rem !important;
        text-align: center;
        border-radius: 6px;
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #333333;
        box-sizing: border-box !important;
    }

    .card-title {
        font-size: 0.75rem;
        color: #aaaaaa;
        margin-bottom: 2px;
        text-transform: uppercase;
    }

    .card-value {
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* 2. Newsfeed Right-Edge Clipping Fix */
    .newsfeed-container {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    .newsfeed-container iframe {
        width: 100% !important;
        max-width: 100% !important;
        border: none !important;
        box-sizing: border-box !important;
    }

    /* 3. Social Stats Vertical Stacking Layout */
    .social-stat-box {
        background-color: #1a1a1a;
        padding: 10px 12px;
        border-radius: 6px;
        margin-bottom: 8px;
        border-left: 3px solid #ff4b4b;
    }

    .social-label {
        font-size: 0.8rem;
        color: #cccccc;
    }

    .social-val {
        font-size: 1rem;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- APP LAYOUT ---

st.title("Derby Penguins Dashboard")

# Main Page Split (Main Content vs Sidebar Newsfeed/Socials)
col_main, col_side = st.columns([2, 1], gap="medium")

with col_main:
    st.subheader("Player Statistics")

    # Filter Controls Stacked Vertically
    name_search = st.text_input("Search Name", key="search_input")
    sort_by = st.selectbox(
        "Sort By", ["Goals", "Assists", "Rating", "Name"], key="sort_select"
    )

    st.markdown("---")

    # Compact Cards Section (Auto-adjusts to fit on-screen)
    st.markdown(
        """
        <div class="card-container">
            <div class="card">
                <div class="card-title">Top Scorer</div>
                <div class="card-value">12</div>
            </div>
            <div class="card">
                <div class="card-title">Top Assists</div>
                <div class="card-value">8</div>
            </div>
            <div class="card">
                <div class="card-title">Matches</div>
                <div class="card-value">15</div>
            </div>
            <div class="card">
                <div class="card-title">Clean Sheets</div>
                <div class="card-value">5</div>
            </div>
            <div class="card">
                <div class="card-title">Win Rate</div>
                <div class="card-value">68%</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Main Data Display / Pitch Visualizer Area
    st.info("Filtered list and pitch visualization render here.")

with col_side:
    st.subheader("Social Stats")

    # Vertical Metric Stack (No wide horizontal scrolling)
    st.markdown(
        """
        <div class="social-stat-box">
            <div class="social-label">Facebook Followers</div>
            <div class="social-val">1,240 <span style="color:#4CAF50; font-size:0.8rem;">+12</span></div>
        </div>
        <div class="social-stat-box">
            <div class="social-label">Weekly Engagement</div>
            <div class="social-val">3,850</div>
        </div>
        <div class="social-stat-box">
            <div class="social-label">Post Reach</div>
            <div class="social-val">8.4K</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("Newsfeed")

    # Embedded Newsfeed with containment to prevent right-side clipping
    st.markdown(
        """
        <div class="newsfeed-container">
            <iframe 
                src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Ffacebook&tabs=timeline&width=340&height=500&small_header=true&adapt_container_width=true&hide_cover=true&show_facepile=false" 
                height="500" 
                style="border:none;overflow:hidden" 
                scrolling="no" 
                frameborder="0" 
                allowfullscreen="true" 
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share">
            </iframe>
        </div>
    """,
        unsafe_allow_html=True,
    )
