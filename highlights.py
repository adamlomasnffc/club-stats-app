import re

import pandas as pd
import streamlit as st

# Shown until the 'Highlights' tab in your Google Sheet has rows in it.
FALLBACK_HIGHLIGHTS = [
    {
        "Date": "",
        "Title": "Game Highlights",
        "Match": "",
        "Video Link": "https://youtu.be/q3vPOsYrlrs",
    }
]


def video_url(link):
    """YouTube links (youtu.be, watch?v=, shorts) -> a clean watch URL.
    Any other link (e.g. a Cloudinary .mp4) is used as it is."""
    link = str(link).strip()
    match = re.search(r"(?:youtu\.be/|v=|/shorts/|/embed/)([A-Za-z0-9_-]{11})", link)
    return f"https://www.youtube.com/watch?v={match.group(1)}" if match else link


def prepare_highlights(df):
    """Cleans the sheet data and sorts newest first. Falls back to the
    built-in list if the tab is missing, empty or has the wrong columns."""
    fallback = pd.DataFrame(FALLBACK_HIGHLIGHTS)
    if df is None or "Video Link" not in df.columns or "Title" not in df.columns:
        return fallback

    df = df.dropna(subset=["Video Link"]).copy()
    for col in ["Date", "Title", "Match"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    df["Video Link"] = df["Video Link"].astype(str).str.strip()
    df = df[df["Video Link"] != ""]
    if df.empty:
        return fallback

    df["_row"] = range(len(df))
    df["_date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    # Newest dated first; undated ones keep "last row in the sheet = newest"
    df = df.sort_values(["_date", "_row"], ascending=[False, False], na_position="last")
    return df.reset_index(drop=True)


def render_highlights(load_sheet):
    st.markdown("### 🎬 Match Highlights")

    try:
        raw = load_sheet("Highlights")
    except Exception:
        raw = None
    items = prepare_highlights(raw)

    labels = []
    for _, row in items.iterrows():
        label = row["Title"] or "Highlight"
        if row["Date"]:
            label += f" ({row['Date']})"
        labels.append(label)

    chosen = 0
    if len(items) > 1:
        chosen = st.selectbox(
            "Choose a highlight",
            options=list(range(len(items))),
            format_func=lambda i: labels[i],
        )

    row = items.iloc[chosen]
    st.markdown(f"#### {row['Title'] or 'Highlight'}")
    details = " · ".join(x for x in [row["Match"], row["Date"]] if x)
    if details:
        st.caption(details)
    st.video(video_url(row["Video Link"]))
