import streamlit as st

# 1. Page Configuration (Must be the first Streamlit command in your script)
st.set_page_config(
    page_title="App Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Styling (Flash Removal + Unclipped Logo Fix)
st.markdown(
    """
    <style>
    /* PREVENT WHITE FLASH ON PAGE LOAD */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }

    /* FIX LOGO TRUNCATION / CHOPPING AT TOP */
    [data-testid="stHeader"], 
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarNav"] {
        padding-top: 1.5rem !important;
        overflow: visible !important;
        height: auto !important;
    }

    /* TARGET ALL SIDEBAR/HEADER LOGO IMAGES */
    [data-testid="stLogo"], 
    [data-testid="stSidebarHeader"] img,
    [data-testid="stSidebar"] img,
    header img {
        margin-top: 0 !important;
        padding-top: 4px !important;
        max-height: 85px !important;  /* Adjust maximum height as desired */
        width: auto !important;
        object-fit: contain !important;
        overflow: visible !important;
    }
    </style>

    <script>
    /* Force dark background on parent document frame prior to paint */
    const forceDark = () => {
        try {
            if (window.parentElement && window.parentElement.document) {
                window.parentElement.document.body.style.backgroundColor = "#0e1117";
            }
        } catch (e) {}
        document.body.style.backgroundColor = "#0e1117";
    };
    forceDark();
    </script>
    """,
    unsafe_allow_html=True,
)

# 3. Logo Implementation
# Option A: Native st.logo (Streamlit 1.31+)
# st.logo("path/to/logo.png")

# Option B: Standard Sidebar Image
with st.sidebar:
    st.image("logo.png", use_container_width=True) # Replace 'logo.png' with your file path or URL
    st.markdown("---")
    st.title("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")


# 4. Main Application Content
st.title("Dashboard")
st.write("Your content loads cleanly without white flashing or logo edge clipping.")
