import streamlit as st

# Combined Flash Removal & Logo Fix
st.markdown(
    """
    <style>
    /* 1. PREVENT WHITE FLASH ON LOAD */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }

    /* 2. FIX LOGO CHOPPING AT THE TOP */
    /* Add top clearance and prevent container clipping */
    [data-testid="stHeader"], 
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarNav"] {
        padding-top: 1.2rem !important;
        overflow: visible !important;
        height: auto !important;
    }

    /* Target Streamlit logo (st.logo) or custom logo images */
    [data-testid="stLogo"], 
    [data-testid="stSidebarHeader"] img,
    header img,
    .logo-container img {
        margin-top: 0 !important;
        padding-top: 6px !important;
        max-height: 80px !important;  /* Adjust max height as needed */
        width: auto !important;
        object-fit: contain !important;
        overflow: visible !important;
    }
    </style>

    <script>
    /* Force immediate dark background on parent frame before CSS fully renders */
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
