import html as html_lib
import re
from collections import Counter
from urllib.parse import quote

import pandas as pd
import streamlit as st

SKIP_NAMES = {"nan", "none", "", "-", "unknown"}


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _clean(v):
    return str(v).strip() if pd.notnull(v) else ""


def normalize_id(val):
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val).strip()


def _venue(row):
    """'H' / 'A' / '' - same column detection the Match Center uses."""
    for col in row.index:
        c = str(col).strip().lower()
        if "home" in c or "away" in c or c == "venue":
            v = _clean(row[col]).lower()
            if v.startswith("a"):
                return "A"
            if v.startswith("h"):
                return "H"
            return ""
    return ""


def longest_streak(flags):
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def _pct(wins, games):
    return f"{wins / games * 100:.0f}%" if games else "-"


def _html(markup):
    if hasattr(st, "html"):
        st.html(markup)
    else:
        st.markdown(markup, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Turn the two sheets into one record per game (in sheet order)
# ------------------------------------------------------------------
def build_records(games_df, goals_df):
    goals_by_game = {}
    if goals_df is not None and not goals_df.empty:
        match_col = "Match ID" if "Match ID" in goals_df.columns else "GameID"
        scorer_col = (
            "Goalscorer" if "Goalscorer" in goals_df.columns
            else ("Scorer" if "Scorer" in goals_df.columns else None)
        )
        assist_col = "Assist" if "Assist" in goals_df.columns else None
        if match_col in goals_df.columns:
            for _, r in goals_df.iterrows():
                entry = goals_by_game.setdefault(
                    normalize_id(r[match_col]), {"goals": Counter(), "assists": Counter()}
                )
                if scorer_col:
                    s = _clean(r[scorer_col])
                    if s and s.lower() not in SKIP_NAMES | {"own goal", "og"}:
                        entry["goals"][s] += 1
                if assist_col:
                    a = _clean(r[assist_col])
                    if a and a.lower() not in SKIP_NAMES | {"unassisted"}:
                        entry["assists"][a] += 1

    records = []
    if games_df is None or games_df.empty:
        return records

    player_cols = games_df.columns[10:37]
    for _, row in games_df.iterrows():
        players = set()
        for col in player_cols:
            v = _clean(row[col])
            if v and v.lower() not in SKIP_NAMES:
                players.add(v)

        outcome_raw = _clean(row.get("Outcome", "")).upper()
        outcome = outcome_raw[:1] if outcome_raw[:1] in ("W", "D", "L") else ""
        if not players and not outcome:
            continue

        # Result is read as "our score - their score"
        m = re.search(r"(\d+)\s*[-\u2013]\s*(\d+)", _clean(row.get("Result", "")))
        gf, ga = (int(m.group(1)), int(m.group(2))) if m else (None, None)

        g = goals_by_game.get(normalize_id(row.get("GameID", "")), {})
        records.append({
            "players": players,
            "outcome": outcome,
            "venue": _venue(row),
            "gf": gf,
            "ga": ga,
            "motm": _clean(row.get("MOTM", "")),
            "goals": g.get("goals", Counter()),
            "assists": g.get("assists", Counter()),
        })
    return records


# ------------------------------------------------------------------
# The numbers
# ------------------------------------------------------------------
def player_summary(records, name):
    mine = [r for r in records if name in r["players"]]          # appearances (matches the stats table)
    played = [r for r in mine if r["outcome"]]                   # games with a result, for streaks/venues
    wins = sum(r["outcome"] == "W" for r in mine)
    draws = sum(r["outcome"] == "D" for r in mine)
    losses = sum(r["outcome"] == "L" for r in mine)
    home = [r for r in played if r["venue"] == "H"]
    away = [r for r in played if r["venue"] == "A"]
    return {
        "apps": len(mine),
        "wins": wins, "draws": draws, "losses": losses,
        "goals": sum(r["goals"][name] for r in mine),
        "assists": sum(r["assists"][name] for r in mine),
        "motm": sum(r["motm"] == name for r in mine),
        "hat_tricks": sum(r["goals"][name] >= 3 for r in mine),
        "braces": sum(r["goals"][name] == 2 for r in mine),
        "home_goals": sum(r["goals"][name] for r in mine if r["venue"] == "H"),
        "away_goals": sum(r["goals"][name] for r in mine if r["venue"] == "A"),
        "home_assists": sum(r["assists"][name] for r in mine if r["venue"] == "H"),
        "away_assists": sum(r["assists"][name] for r in mine if r["venue"] == "A"),
        "streak_wins": longest_streak(r["outcome"] == "W" for r in played),
        "streak_scored": longest_streak(r["goals"][name] > 0 for r in played),
        "streak_assisted": longest_streak(r["assists"][name] > 0 for r in played),
        "streak_either": longest_streak(
            (r["goals"][name] > 0 or r["assists"][name] > 0) for r in played
        ),
        "home_games": len(home), "home_wins": sum(r["outcome"] == "W" for r in home),
        "away_games": len(away), "away_wins": sum(r["outcome"] == "W" for r in away),
    }


def team_summary(records):
    played = [r for r in records if r["outcome"]]

    def wdl(rs):
        return (sum(r["outcome"] == "W" for r in rs),
                sum(r["outcome"] == "D" for r in rs),
                sum(r["outcome"] == "L" for r in rs))

    home = [r for r in played if r["venue"] == "H"]
    away = [r for r in played if r["venue"] == "A"]
    scored = [r for r in played if r["gf"] is not None]
    home_scored = [r for r in scored if r["venue"] == "H"]
    away_scored = [r for r in scored if r["venue"] == "A"]
    wins, draws, losses = wdl(played)
    gf = sum(r["gf"] for r in scored)
    ga = sum(r["ga"] for r in scored)
    return {
        "played": len(played),
        "wins": wins, "draws": draws, "losses": losses,
        "streak_wins": longest_streak(r["outcome"] == "W" for r in played),
        "streak_losses": longest_streak(r["outcome"] == "L" for r in played),
        "home": wdl(home), "away": wdl(away),
        "gf": gf, "ga": ga, "scored_games": len(scored),
        "home_gf": sum(r["gf"] for r in home_scored), "home_ga": sum(r["ga"] for r in home_scored),
        "home_scored_games": len(home_scored),
        "away_gf": sum(r["gf"] for r in away_scored), "away_ga": sum(r["ga"] for r in away_scored),
        "away_scored_games": len(away_scored),
        "clean_sheets": sum(r["ga"] == 0 for r in scored),
    }


# ------------------------------------------------------------------
# Streamlit pieces
# ------------------------------------------------------------------
def player_link_html(team, name):
    href = f"?page={quote(team)}&player={quote(str(name), safe='')}"
    return (
        f"<a href='{href}' target='_self' style='color: inherit; "
        f"text-decoration: underline dotted; text-underline-offset: 3px;'>"
        f"{html_lib.escape(str(name))}</a>"
    )


def render_stats_view_toggle(team):
    key = f"{team}_stats_view"
    if key not in st.session_state:
        st.session_state[key] = "Players"

    cols = st.columns(2)
    for i, (val, label) in enumerate([("Players", "👤 Players"), ("Team", "🛡️ Team")]):
        if cols[i].button(
            label,
            key=f"stats_view_{team}_{val}",
            use_container_width=True,
            type="primary" if st.session_state[key] == val else "secondary",
        ):
            st.session_state[key] = val
            if val == "Players":
                st.session_state.pop(f"{team}_selected_player", None)
            st.rerun()
    return st.session_state[key]


def _metric_pair(a, b):
    c1, c2 = st.columns(2)
    for col, (label, value, delta) in zip((c1, c2), (a, b)):
        if delta:
            col.metric(label, value, delta)
        else:
            col.metric(label, value)


def render_player_profile(load_sheet, team, name):
    records = build_records(load_sheet(f"{team}_Games"), load_sheet(f"{team}_Goals"))
    s = player_summary(records, name)

    if st.button("← All players", key=f"back_to_players_{team}"):
        st.session_state.pop(f"{team}_selected_player", None)
        st.rerun()

    st.markdown(f"## {name}")
    if s["apps"] == 0:
        st.info("No appearances found for this player.")
        return

    _metric_pair(
        ("🏃 Appearances", str(s["apps"]), f"W{s['wins']} D{s['draws']} L{s['losses']}"),
        ("🏆 Win %", _pct(s["wins"], s["apps"]), f"{s['wins']} of {s['apps']} games"),
    )
    _metric_pair(
        ("⚽ Goals", str(s["goals"]), None),
        ("🅰️ Assists", str(s["assists"]), None),
    )
    _metric_pair(
        ("⭐ MOTM", str(s["motm"]), None),
        ("🔥 Goal Involvements", str(s["goals"] + s["assists"]), None),
    )

    _metric_pair(
        ("🎩 Hat Tricks", str(s["hat_tricks"]), None),
        ("✌️ Braces", str(s["braces"]), None),
    )

    st.markdown("### Best runs")
    st.caption("Counted across the games this player appeared in.")
    _metric_pair(
        ("✅ Most wins in a row", str(s["streak_wins"]), None),
        ("⚽ Most games scored in a row", str(s["streak_scored"]), None),
    )
    _metric_pair(
        ("🅰️ Most games assisted in a row", str(s["streak_assisted"]), None),
        ("🔥 Most games scored or assisted in a row", str(s["streak_either"]), None),
    )

    st.markdown("### Home v Away")
    _metric_pair(
        ("🏠 Win % at home", _pct(s["home_wins"], s["home_games"]),
         f"{s['home_wins']} of {s['home_games']} games" if s["home_games"] else None),
        ("🚌 Win % away", _pct(s["away_wins"], s["away_games"]),
         f"{s['away_wins']} of {s['away_games']} games" if s["away_games"] else None),
    )

    def per_game(total, games):
        return f"{total / games:.1f} per game" if games else None

    _metric_pair(
        ("🏠 Home goals", str(s["home_goals"]), per_game(s["home_goals"], s["home_games"])),
        ("🚌 Away goals", str(s["away_goals"]), per_game(s["away_goals"], s["away_games"])),
    )
    _metric_pair(
        ("🏠 Home assists", str(s["home_assists"]), per_game(s["home_assists"], s["home_games"])),
        ("🚌 Away assists", str(s["away_assists"]), per_game(s["away_assists"], s["away_games"])),
    )


def render_team_stats(load_sheet, team):
    records = build_records(load_sheet(f"{team}_Games"), load_sheet(f"{team}_Goals"))
    t = team_summary(records)

    st.markdown(f"### {team} Team Stats")
    if t["played"] == 0:
        st.info("No results recorded yet.")
        return

    _metric_pair(
        ("📅 Games Played", str(t["played"]), None),
        ("🏆 Win %", _pct(t["wins"], t["played"]), None),
    )

    # Wins v draws v defeats bar
    segments = [("Wins", t["wins"], "#22C55E"), ("Draws", t["draws"], "#9CA3AF"),
                ("Defeats", t["losses"], "#EF4444")]
    bar = "".join(
        f"<div style='flex:{n}; background:{colour};'></div>"
        for _, n, colour in segments if n
    )
    legend = " &middot; ".join(f"{n} {label}" for label, n, _ in segments)
    _html(
        "<div style='max-width:520px; margin:10px auto 4px auto;'>"
        f"<div style='display:flex; height:22px; border-radius:6px; overflow:hidden;'>{bar}</div>"
        f"<div style='font-size:12px; color:#d1d5db; margin-top:4px;'>{legend}</div></div>"
    )

    _metric_pair(
        ("✅ Most wins in a row", str(t["streak_wins"]), None),
        ("❌ Most defeats in a row", str(t["streak_losses"]), None),
    )

    hw, hd, hl = t["home"]
    aw, ad, al = t["away"]
    _metric_pair(
        ("🏠 Home record", f"W{hw} D{hd} L{hl}", None),
        ("🚌 Away record", f"W{aw} D{ad} L{al}", None),
    )

    if t["scored_games"]:
        per_game = t["scored_games"]
        _metric_pair(
            ("⚽ Goals scored", str(t["gf"]), f"{t['gf'] / per_game:.1f} per game"),
            ("🥅 Goals conceded", str(t["ga"]), f"{t['ga'] / per_game:.1f} per game"),
        )

        def avg(total, games):
            return f"{total / games:.1f} per game" if games else None

        hg, ag = t["home_scored_games"], t["away_scored_games"]
        _metric_pair(
            ("🏠 Home goals scored", str(t["home_gf"]), avg(t["home_gf"], hg)),
            ("🏠 Home goals conceded", str(t["home_ga"]), avg(t["home_ga"], hg)),
        )
        _metric_pair(
            ("🚌 Away goals scored", str(t["away_gf"]), avg(t["away_gf"], ag)),
            ("🚌 Away goals conceded", str(t["away_ga"]), avg(t["away_ga"], ag)),
        )

        diff = t["gf"] - t["ga"]
        _metric_pair(
            ("➕ Goal difference", f"{diff:+d}", None),
            ("🧤 Clean sheets", str(t["clean_sheets"]), None),
        )
