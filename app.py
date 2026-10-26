import base64
import textwrap
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ==========================================
# 1. HELPER: SAFE HTML RENDERING
# ==========================================
def render_html(html_str):
    clean_html = str(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


# ==========================================
# 2. PAGE CONFIG & ASSETS
# ==========================================
# Logo file sits in the same folder as app.py in the repository
LOGO_FILENAME = "6C4E75CF-C4F8-4770-B666-1143DC3BC22D.jpeg"
LOGO_PATH = Path(__file__).parent / LOGO_FILENAME


@st.cache_data
def load_logo_data_uri():
    try:
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return ""


HEADER_LOGO_URL = load_logo_data_uri()

try:
    from PIL import Image
    PAGE_ICON = Image.open(LOGO_PATH)
except Exception:
    PAGE_ICON = "⚽"

st.set_page_config(
    page_title="Derby MvF League App", page_icon=PAGE_ICON, layout="wide"
)

# ==========================================
# 3. SESSION STATE / NAVIGATION STATE
# ==========================================
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Homepage"

if "season_stats_selected" not in st.session_state:
    st.session_state["season_stats_selected"] = None  # set once seasons are loaded

if "draft_period" not in st.session_state:
    st.session_state["draft_period"] = "Overview"

current_page = st.session_state["active_page"]

# ==========================================
# 4. GLOBAL STYLING
# ==========================================
style_html = f"""
<head>
<meta name="apple-mobile-web-app-title" content="Derby MvF League App">
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

/* Force nav grid to stay in a row on all screen sizes */
div[data-testid="stHorizontalBlock"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
}}
div[data-testid="stHorizontalBlock"] > div {{
    flex: 1 1 0px !important;
    min-width: 0 !important;
}}

/* Header logo */
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
    max-height: 65px !important;
    width: auto !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 auto !important;
}}

/* Native Streamlit buttons (nav + subnav) */
div.stButton > button {{
    width: 100% !important;
    padding: 8px 2px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {{
    text-align: center !important;
}}
ul, ol {{
    list-style-position: inside !important;
    padding-left: 0 !important;
}}
li {{
    text-align: center !important;
}}
div.stButton > button p {{
    white-space: normal !important;
    line-height: 1.15 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
}}
div.stButton > button[kind="primary"] {{
    background-color: #22252e !important;
    color: #FFB81C !important;
    border: 1px solid #FFB81C !important;
    box-shadow: 0 0 8px rgba(255, 184, 28, 0.2) !important;
}}
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

/* KPI metric cards */
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
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.75rem !important;
    color: #d1d5db !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}}
[data-testid="stMetricLabel"] > div {{
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}}
[data-testid="stMetricValue"] {{
    color: #FFB81C !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    white-space: normal !important;
    word-break: break-word !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}}
[data-testid="stMetricValue"] > div {{
    text-align: center !important;
    justify-content: center !important;
    width: 100% !important;
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
render_html(style_html)

# ==========================================
# 5. TOP HEADER LOGO
# ==========================================
header_html = f"""
<div class="header-logo-container">
    <img src="{HEADER_LOGO_URL}" class="header-logo" alt="Derby MvF League Logo">
</div>
<h1 style="margin-top: 2px; margin-bottom: 10px; font-size: 1.25rem;">Derby MvF League</h1>
"""
render_html(header_html)

# ==========================================
# 6. SPREADSHEET DATA LOADER
# ==========================================
SPREADSHEET_ID = "1jtBoXRsuQ0L7-uh1iashTCJUKne435qGqXRSBqyZ1eU"


@st.cache_data(ttl=60)
def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df


def normalize_name(val):
    return str(val).strip() if pd.notnull(val) else ""


# ==========================================
# 7. TEAM COLOUR LOOKUP
# ==========================================
@st.cache_data(ttl=60)
def load_colour_map():
    """Expects a 'Team_Colours' sheet with columns: Player, Team, Colour"""
    try:
        df = load_sheet("Team_Colours")
        df["Player"] = df["Player"].apply(normalize_name)
        df["Colour"] = df["Colour"].apply(normalize_name)
        return dict(zip(df["Player"], df["Colour"]))
    except Exception:
        return {}


def team_dot(hex_color):
    if not hex_color:
        return ""
    return (
        f"<span style='display:inline-block; width:9px; height:9px; "
        f"border-radius:50%; background-color:{hex_color}; "
        f"margin-right:5px; vertical-align:middle;'></span>"
    )


def player_cell_html(player_name, colour_map):
    colour = colour_map.get(player_name, "")
    dot = team_dot(colour) if colour else ""
    return f"{dot}{player_name}"


# ==========================================
# 8. STATS DATA: HISTORICAL + CURRENT SEASON
# ==========================================
STATS_COLUMNS = ["Season", "Player", "Goals", "Assists", "Goal Involvements", "Man Of The Match"]


@st.cache_data(ttl=60)
def load_historical_data():
    """Expects a 'Historical_Data' sheet with columns:
    Season, Player, Goals, Assists, Goal Involvements, Man Of The Match"""
    df = load_sheet("Historical_Data")
    df.columns = df.columns.str.strip()
    for col in STATS_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col not in ["Season", "Player"] else ""
    return df[STATS_COLUMNS]


@st.cache_data(ttl=60)
def load_current_season_data(season_label):
    """Expects a 'Current_Season' sheet laid out as four pivot pairs, WITH a
    blank spacer column between each pair (matches the real sheet layout):
    Player, Goals Scored, [blank], Player, Assists, [blank],
    Player, Goal Contributions, [blank], Player, MOTM"""
    raw = load_sheet("Current_Season")
    cols = raw.columns.tolist()

    if len(cols) < 11:
        return pd.DataFrame(columns=STATS_COLUMNS)

    def pair_to_dict(player_col, value_col):
        out = {}
        for p, v in zip(raw[player_col], raw[value_col]):
            p = normalize_name(p)
            if p and p.lower() not in ["nan", "none", "", "-"]:
                out[p] = v if pd.notnull(v) else 0
        return out

    # Positions: (0,1)=Goals, (3,4)=Assists, (6,7)=Goal Contributions, (9,10)=MOTM
    goals_dict = pair_to_dict(cols[0], cols[1])
    assists_dict = pair_to_dict(cols[3], cols[4])
    gi_dict = pair_to_dict(cols[6], cols[7])
    motm_dict = pair_to_dict(cols[9], cols[10])

    all_players = set(goals_dict) | set(assists_dict) | set(gi_dict) | set(motm_dict)

    rows = []
    for p in all_players:
        rows.append({
            "Season": season_label,
            "Player": p,
            "Goals": goals_dict.get(p, 0),
            "Assists": assists_dict.get(p, 0),
            "Goal Involvements": gi_dict.get(p, 0),
            "Man Of The Match": motm_dict.get(p, 0),
        })

    return pd.DataFrame(rows, columns=STATS_COLUMNS)


CURRENT_SEASON_LABEL = "8"  # TODO: update this manually each new season (matches Historical_Data's numeric Season column)


@st.cache_data(ttl=60)
def load_combined_stats():
    historical_df = load_historical_data()
    current_df = load_current_season_data(CURRENT_SEASON_LABEL)
    combined = pd.concat([historical_df, current_df], ignore_index=True)
    for col in ["Goals", "Assists", "Goal Involvements", "Man Of The Match"]:
        combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0)
    return combined


# ==========================================
# 9. STATS TABLE RENDERER (shared by Season + All Time)
# ==========================================
def render_stats_table(df, colour_map, key_prefix):
    st.markdown("")

    search_query = st.text_input("🔍 Search Player", "", key=f"{key_prefix}_search")
    sort_options = ["Goals", "Assists", "Goal Involvements", "Man Of The Match", "Player"]
    sort_by = st.selectbox("Sort By", options=sort_options, index=0, key=f"{key_prefix}_sort")
    sort_order = st.radio(
        "Order", ["Descending", "Ascending"], horizontal=True, key=f"{key_prefix}_order"
    )

    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Player"].str.contains(search_query, case=False, na=False)
        ]

    ascending = sort_order == "Ascending"
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)

    display_cols = ["Player", "Goals", "Assists", "Goal Involvements", "Man Of The Match"]

    table_html = (
        "<div class='mobile-table-container'>"
        "<table style='width:100%; border-collapse: collapse; text-align: center; "
        "font-family: sans-serif; min-width: 550px;'>"
        "<tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
    )
    for col in display_cols:
        th_style = "padding: 8px; border-bottom: 2px solid #333; font-size: 12px;"
        if col == "Player":
            th_style += " white-space: nowrap;"
        table_html += f"<th style='{th_style}'>{col}</th>"
    table_html += "</tr>"

    for idx, row in filtered_df.iterrows():
        bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
        table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
        for col in display_cols:
            val = row[col]
            if col == "Player":
                cell_content = player_cell_html(val, colour_map)
                td_style = "padding: 6px; border-bottom: 1px solid #2A2D35; white-space: nowrap; font-weight: 500;"
            else:
                cell_content = "-" if pd.isnull(val) else str(int(val))
                td_style = "padding: 6px; border-bottom: 1px solid #2A2D35;"
            table_html += f"<td style='{td_style}'>{cell_content}</td>"
        table_html += "</tr>"
    table_html += "</table></div>"

    render_html(table_html)


def render_stats_kpis(df):
    if df.empty:
        row1_col1, row1_col2 = st.columns(2)
        row1_col1.metric("⚽ Top Scorer", "-", "0 Goals")
        row1_col2.metric("🅰️ Top Assister", "-", "0 Assists")
        row2_col1, row2_col2 = st.columns(2)
        row2_col1.metric("🔥 Top Contributor", "-", "0 G+A")
        row2_col2.metric("🏆 Most MOTMs", "-", "0 MOTM")
        return

    top_scorer = df.sort_values(by="Goals", ascending=False).iloc[0]
    top_assister = df.sort_values(by="Assists", ascending=False).iloc[0]
    top_gi = df.sort_values(by="Goal Involvements", ascending=False).iloc[0]
    top_motm = df.sort_values(by="Man Of The Match", ascending=False).iloc[0]

    row1_col1, row1_col2 = st.columns(2)
    row1_col1.metric("⚽ Top Scorer", top_scorer["Player"], f"{int(top_scorer['Goals'])} Goals")
    row1_col2.metric("🅰️ Top Assister", top_assister["Player"], f"{int(top_assister['Assists'])} Assists")

    row2_col1, row2_col2 = st.columns(2)
    row2_col1.metric("🔥 Top Contributor", top_gi["Player"], f"{int(top_gi['Goal Involvements'])} G+A")
    row2_col2.metric("🏆 Most MOTMs", top_motm["Player"], f"{int(top_motm['Man Of The Match'])} MOTM")


# ==========================================
# 10. DRAFT STANDINGS DATA + RENDERER
# ==========================================
# The Draft_Standings sheet is a formula-driven "printed report" layout, not a
# tidy table - four period blocks sit side-by-side (Three Season Table /
# Season One / Two / Three), each containing three stacked league tables
# (Overall / Pitch / Scales). Positions below were verified against the real
# sheet directly. If rows/columns are ever inserted or reordered in that
# sheet, these positions will need re-checking.

DRAFT_BLOCK_START_COLS = {
    "Overview": 1,    # "Three Season Table" block
    "Season 1": 11,   # "Season One" block
    "Season 2": 21,   # "Season Two" block
    "Season 3": 31,   # "Season Three" block
}

# Row ranges (0-indexed, inclusive) for each league's data rows within a block.
DRAFT_LEAGUE_ROW_RANGES = {
    "Overall": (4, 11),
    "Pitch": (15, 22),
    "Scales": (26, 33),
}

# Column offsets relative to a block's start column
DRAFT_COL_OFFSETS = {
    "Team": 0,
    "Played": 1,
    "Won": 2,
    "Drawn": 3,
    "Lost": 4,
    "Goals For": 5,
    "Goals Against": 6,
    "Goal Difference": 7,
    "Points": 8,
}


@st.cache_data(ttl=60)
def load_draft_standings_raw():
    url = (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet=Draft_Standings"
    )
    df = pd.read_csv(url, header=None, dtype=str)
    return df


def parse_draft_league(raw_df, period_key, league_key):
    """Pull one league table (Overall/Pitch/Scales) for one period block out
    of the raw positional sheet."""
    start_col = DRAFT_BLOCK_START_COLS[period_key]
    row_start, row_end = DRAFT_LEAGUE_ROW_RANGES[league_key]

    records = []
    for r in range(row_start, row_end + 1):
        if r >= len(raw_df):
            break

        team_col = start_col + DRAFT_COL_OFFSETS["Team"]
        team_val = raw_df.iat[r, team_col] if team_col < raw_df.shape[1] else None

        if pd.isnull(team_val) or str(team_val).strip() == "":
            continue  # blank slot within this league's allocated rows

        def cell(field_name):
            col = start_col + DRAFT_COL_OFFSETS[field_name]
            if col >= raw_df.shape[1]:
                return None
            return raw_df.iat[r, col]

        records.append({
            "Team": str(team_val).strip(),
            "Played": cell("Played"),
            "Won": cell("Won"),
            "Drawn": cell("Drawn"),
            "Lost": cell("Lost"),
            "Goals For": cell("Goals For"),
            "Goals Against": cell("Goals Against"),
            "Goal Difference": cell("Goal Difference"),
            "Points": cell("Points"),
        })

    result = pd.DataFrame(
        records,
        columns=["Team", "Played", "Won", "Drawn", "Lost",
                 "Goals For", "Goals Against", "Goal Difference", "Points"],
    )
    numeric_cols = ["Played", "Won", "Drawn", "Lost",
                     "Goals For", "Goals Against", "Goal Difference", "Points"]
    for c in numeric_cols:
        result[c] = pd.to_numeric(result[c], errors="coerce").fillna(0)

    return result


def render_standings_table(subset, title):
    subset = subset.sort_values(by=["Points", "Goal Difference"], ascending=False).reset_index(drop=True)

    st.markdown(f"#### {title}")

    cols = ["Team", "Played", "Won", "Drawn", "Lost",
            "Goals For", "Goals Against", "Goal Difference", "Points"]

    table_html = (
        "<div class='mobile-table-container'>"
        "<table style='width:100%; border-collapse: collapse; text-align: center; "
        "font-family: sans-serif; min-width: 600px;'>"
        "<tr style='background-color: #FFB81C; color: #111; font-weight: bold;'>"
    )
    for col in cols:
        table_html += f"<th style='padding: 8px; border-bottom: 2px solid #333; font-size: 12px;'>{col}</th>"
    table_html += "</tr>"

    for idx, row in subset.iterrows():
        bg_color = "#181a20" if idx % 2 == 0 else "#0e1117"
        table_html += f"<tr style='background-color: {bg_color}; color: white; font-size: 12px;'>"
        for col in cols:
            val = row[col]
            if pd.isnull(val):
                formatted_val = "-"
            elif isinstance(val, (int, float)):
                formatted_val = str(int(val)) if float(val) % 1 == 0 else str(val)
            else:
                formatted_val = str(val)

            weight = "font-weight: 700;" if col == "Team" else ""
            gd_colour = ""
            if col == "Goal Difference" and pd.notnull(val):
                try:
                    gd_val = float(val)
                    gd_colour = "color: #4ADE80;" if gd_val > 0 else ("color: #F87171;" if gd_val < 0 else "")
                except ValueError:
                    pass

            table_html += (
                f"<td style='padding: 6px; border-bottom: 1px solid #2A2D35; "
                f"{weight} {gd_colour}'>{formatted_val}</td>"
            )
        table_html += "</tr>"
    table_html += "</table></div>"

    render_html(table_html)


# ==========================================
# 10b. FIXTURES
# ==========================================
import html as html_lib
import re
from datetime import datetime
from zoneinfo import ZoneInfo

FIXTURE_COLUMNS = ["Week", "Date", "Time", "Pitch", "Home Team", "Away Team"]

# Teams are named after their colours, so we can show a matching dot
TEAM_DOT_COLOURS = {
    "white": "#FFFFFF", "black": "#000000", "yellow": "#FACC15",
    "blue": "#3B82F6", "pink": "#EC4899", "red": "#EF4444",
    "orange": "#F97316", "green": "#22C55E", "purple": "#A855F7",
    "grey": "#9CA3AF", "gray": "#9CA3AF",
}


@st.cache_data(ttl=60)
def load_fixtures():
    """Expects a 'Fixtures' sheet with columns:
    Week, Date, Time, Pitch, Home Team, Away Team"""
    df = load_sheet("Fixtures").dropna(how="all")
    missing = [c for c in FIXTURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Fixtures sheet is missing columns: {', '.join(missing)}")
    df = df[FIXTURE_COLUMNS].dropna(subset=["Week"]).copy()
    for col in FIXTURE_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
    df["ParsedDate"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


def week_slug(week_name):
    return re.sub(r"[^a-z0-9]+", "-", str(week_name).lower()).strip("-")


def find_next_week(df):
    """First week whose date is today or later (UK time). If the season is
    over, falls back to the final week."""
    today = datetime.now(ZoneInfo("Europe/London")).date()
    weeks = df["Week"].drop_duplicates().tolist()
    for w in weeks:
        d = df.loc[df["Week"] == w, "ParsedDate"].dropna()
        if not d.empty and d.iloc[0].date() >= today:
            return w
    return weeks[-1] if weeks else None


def team_chip(name, dot_on_right=False):
    colour = TEAM_DOT_COLOURS.get(str(name).strip().lower())
    dot = ""
    if colour:
        margin = "margin-left:5px;" if dot_on_right else "margin-right:5px;"
        dot = (
            f"<span style='display:inline-block; width:10px; height:10px; "
            f"border-radius:50%; background-color:{colour}; "
            f"border:1px solid rgba(255,255,255,0.5); {margin} "
            f"vertical-align:middle;'></span>"
        )
    label = html_lib.escape(str(name))
    return f"{label}{dot}" if dot_on_right else f"{dot}{label}"


def fixtures_cards_html(df, next_week):
    cards = ""
    for week in df["Week"].drop_duplicates().tolist():
        group = df[df["Week"] == week]
        parsed = group["ParsedDate"].dropna()
        date_label = (
            parsed.iloc[0].strftime("%A %d %B %Y")
            if not parsed.empty
            else group["Date"].iloc[0]
        )

        is_next = week == next_week
        border = "2px solid #FFB81C" if is_next else "1px solid #333"
        glow = "box-shadow: 0 0 10px rgba(255,184,28,0.25);" if is_next else ""
        badge = (
            "<div style='display:inline-block; background:#FFB81C; color:#111; "
            "font-size:10px; font-weight:700; padding:2px 8px; border-radius:10px; "
            "margin-bottom:6px;'>NEXT UP</div>"
            if is_next else ""
        )

        cards += (
            f"<div id='{week_slug(week)}' style='background:#181a20; border:{border}; "
            f"{glow} border-radius:12px; padding:14px 12px; margin:0 auto 16px auto; "
            f"max-width:520px; scroll-margin-top:20px;'>"
            f"{badge}"
            f"<div style='font-size:18px; font-weight:800; color:#FFB81C;'>"
            f"{html_lib.escape(str(week))}</div>"
            f"<div style='font-size:13px; color:#d1d5db; margin-bottom:8px;'>"
            f"{html_lib.escape(str(date_label))}</div>"
        )
        for _, row in group.iterrows():
            cards += (
                f"<div style='padding:8px 0; border-top:1px solid #2A2D35;'>"
                f"<div style='font-size:15px; font-weight:700; color:#fff;'>"
                f"{team_chip(row['Home Team'])} <span style='color:#9CA3AF; "
                f"font-weight:500;'>v</span> {team_chip(row['Away Team'], dot_on_right=True)}</div>"
                f"<div style='font-size:12px; color:#FFB81C; margin-top:2px;'>"
                f"KO {html_lib.escape(row['Time'])} &middot; "
                f"{html_lib.escape(row['Pitch'])}</div></div>"
            )
        cards += "</div>"
    return cards


def to_24h_label(t):
    """'8:00pm' -> '20:00'. Falls back to the original text if unparseable."""
    cleaned = str(t).strip().upper().replace(" ", "")
    for fmt in ("%I:%M%p", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return str(t).strip()


PITCH_ORDER = ["Near Pitch", "Far Pitch", "First Free Pitch"]
PITCH_SHORT_LABELS = {"First Free Pitch": "Either"}


def fixture_split_html(df):
    """One row per team: how many games in each KO slot and on each pitch,
    counted across home and away fixtures."""
    long_df = pd.concat([
        df[["Time", "Pitch", "Home Team"]].rename(columns={"Home Team": "Team"}),
        df[["Time", "Pitch", "Away Team"]].rename(columns={"Away Team": "Team"}),
    ], ignore_index=True)
    long_df["Slot"] = long_df["Time"].apply(to_24h_label)

    slots = sorted(long_df["Slot"].unique())
    present = long_df["Pitch"].unique().tolist()
    pitches = [p for p in PITCH_ORDER if p in present] + sorted(
        p for p in present if p not in PITCH_ORDER
    )

    by_slot = pd.crosstab(long_df["Team"], long_df["Slot"]).reindex(columns=slots, fill_value=0)
    by_pitch = pd.crosstab(long_df["Team"], long_df["Pitch"]).reindex(columns=pitches, fill_value=0)

    th = "padding:6px 4px; font-size:11px; border-bottom:1px solid #333;"
    group_th = (
        "padding:6px 4px; font-size:11px; font-weight:700; color:#111; "
        "background:#FFB81C;"
    )
    divider = "border-left:1px solid #333;"

    out = (
        "<div class='mobile-table-container'>"
        "<table style='width:100%; border-collapse:collapse; text-align:center; "
        "font-family:sans-serif; min-width:330px;'>"
        f"<tr><th style='{group_th}'></th>"
        f"<th colspan='{len(slots)}' style='{group_th} {divider}'>KO TIME</th>"
        f"<th colspan='{len(pitches)}' style='{group_th} {divider}'>PITCH</th></tr>"
        f"<tr style='background:#22252e; color:#FFB81C;'>"
        f"<th style='{th}'>Team</th>"
    )
    for i, sl in enumerate(slots):
        out += f"<th style='{th}{divider if i == 0 else ''}'>{html_lib.escape(sl)}</th>"
    for i, p in enumerate(pitches):
        label = html_lib.escape(PITCH_SHORT_LABELS.get(p, p.replace(" Pitch", "")))
        out += f"<th style='{th}{divider if i == 0 else ''}'>{label}</th>"
    out += "</tr>"

    for idx, team in enumerate(sorted(by_slot.index)):
        bg = "#181a20" if idx % 2 == 0 else "#0e1117"
        out += (
            f"<tr style='background:{bg}; color:#fff; font-size:12px;'>"
            f"<td style='padding:6px 4px; text-align:center; font-weight:600; "
            f"white-space:nowrap; border-bottom:1px solid #2A2D35;'>"
            f"<div style='display:flex; justify-content:center; align-items:center; "
            f"text-align:center;'><span>{team_chip(team)}</span></div></td>"
        )
        for i, sl in enumerate(slots):
            out += (
                f"<td style='padding:6px 4px; border-bottom:1px solid #2A2D35;"
                f"{divider if i == 0 else ''}'>{int(by_slot.loc[team, sl])}</td>"
            )
        for i, p in enumerate(pitches):
            out += (
                f"<td style='padding:6px 4px; border-bottom:1px solid #2A2D35;"
                f"{divider if i == 0 else ''}'>{int(by_pitch.loc[team, p])}</td>"
            )
        out += "</tr>"
    out += "</table></div>"
    return out


# ==========================================
# 11. TOP-LEVEL NAVIGATION
# ==========================================
pages_config = [
    ("🏠 Home", "Homepage"),
    ("📅 Fixtures", "Fixtures"),
    ("📊 Season Stats", "Season Stats"),
    ("🏆 All Time Stats", "All Time Stats"),
    ("🔄 Draft Standings", "Draft Standings"),
]


def nav_button(label, key, column):
    is_active = current_page == key
    btn_type = "primary" if is_active else "secondary"
    if column.button(label, key=f"top_nav_{key}", use_container_width=True, type=btn_type):
        st.session_state["active_page"] = key
        st.rerun()


# Row 1: Home + Fixtures, centred over the row below
_, top_col_1, top_col_2, _ = st.columns(4)
nav_button(pages_config[0][0], pages_config[0][1], top_col_1)
nav_button(pages_config[1][0], pages_config[1][1], top_col_2)

# Row 2: the three stats tabs
other_cols = st.columns(len(pages_config) - 2)
for idx, (label, key) in enumerate(pages_config[2:]):
    nav_button(label, key, other_cols[idx])

st.divider()


# ==========================================
# 12. HOMEPAGE
# ==========================================
if current_page == "Homepage":
    st.markdown("### Welcome to the Derby Man v Fat League App")
    st.markdown(
        textwrap.dedent("""
        Man v Fat Football is a weight-loss focused six-a-side league where
        your score isn't just about goals - it's about progress on and off the pitch.

        This app tracks player stats across every season of the Derby league:
        goals, assists, goal involvements, and Man of the Match awards - both
        for the current season and across our full league history.

        Every three seasons, squads are redrafted. Use **Draft Standings** to see
        how each side performed across a full draft cycle before the next reshuffle.

        Use the buttons above to explore:
        - **Season Stats** - this season's leaderboard, plus every past season
        - **All Time Stats** - combined totals across the league's whole history
        - **Draft Standings** - team-by-team standings for each 3-season draft cycle
        """)
    )

# ==========================================
# 13. SEASON STATS
# ==========================================
elif current_page == "Season Stats":
    render_page_header_title = "Season Stats"
    st.markdown(f"## {render_page_header_title}")

    try:
        combined_df = load_combined_stats()
        colour_map = load_colour_map()

        def season_sort_key(s):
            try:
                return (0, int(s))
            except (ValueError, TypeError):
                return (1, str(s))

        all_seasons = sorted(combined_df["Season"].dropna().unique().tolist(), key=season_sort_key)
        if not all_seasons:
            st.info("No season data found yet.")
        else:
            # Default to current season if present, else the most recent season
            default_season = CURRENT_SEASON_LABEL if CURRENT_SEASON_LABEL in all_seasons else all_seasons[-1]

            selected_season = st.selectbox(
                "Select Season",
                options=all_seasons,
                index=all_seasons.index(default_season),
            )

            season_df = combined_df[combined_df["Season"] == selected_season].reset_index(drop=True)

            render_stats_kpis(season_df)
            st.divider()
            st.markdown(f"### Season {selected_season} Player Stats")
            render_stats_table(season_df, colour_map, key_prefix="season")

    except Exception as e:
        st.error(f"Error loading Season Stats: {e}")

# ==========================================
# 14. ALL TIME STATS
# ==========================================
elif current_page == "All Time Stats":
    st.markdown("## All Time Stats")

    try:
        combined_df = load_combined_stats()
        colour_map = load_colour_map()

        all_time_df = (
            combined_df.groupby("Player", as_index=False)[
                ["Goals", "Assists", "Goal Involvements", "Man Of The Match"]
            ]
            .sum()
        )

        render_stats_kpis(all_time_df)
        st.divider()
        st.markdown("### All Time Player Stats")
        render_stats_table(all_time_df, colour_map, key_prefix="alltime")

    except Exception as e:
        st.error(f"Error loading All Time Stats: {e}")

# ==========================================
# 15. DRAFT STANDINGS
# ==========================================
elif current_page == "Draft Standings":
    st.markdown("## Draft Standings")

    try:
        raw_df = load_draft_standings_raw()

        periods = ["Overview", "Season 1", "Season 2", "Season 3"]

        period_cols = st.columns(len(periods))
        for idx, p in enumerate(periods):
            is_active = st.session_state["draft_period"] == p
            if period_cols[idx].button(
                p,
                key=f"draft_period_{p}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state["draft_period"] = p
                st.rerun()

        st.divider()

        selected_period = st.session_state["draft_period"]

        overall_df = parse_draft_league(raw_df, selected_period, "Overall")
        pitch_df = parse_draft_league(raw_df, selected_period, "Pitch")
        scales_df = parse_draft_league(raw_df, selected_period, "Scales")

        render_standings_table(overall_df, "🔥 Combined")
        st.markdown("<br>", unsafe_allow_html=True)
        render_standings_table(scales_df, "⚖️ Scales")
        st.markdown("<br>", unsafe_allow_html=True)
        render_standings_table(pitch_df, "⚽ Pitch")

    except Exception as e:
        st.error(f"Error loading Draft Standings: {e}")

# ==========================================
# 16. FIXTURES
# ==========================================
elif current_page == "Fixtures":
    st.markdown("## Fixtures")

    try:
        fixtures_df = load_fixtures()
        next_week = find_next_week(fixtures_df)

        if next_week:
            render_html(
                f"<div style='text-align:center; margin:6px 0 18px 0;'>"
                f"<a href='#{week_slug(next_week)}' target='_self' "
                f"style='display:inline-block; padding:10px 18px; border-radius:8px; "
                f"background:#22252e; color:#FFB81C; border:1px solid #FFB81C; "
                f"font-weight:600; font-size:14px; text-decoration:none;'>"
                f"See this week's fixtures</a></div>"
            )

        with st.expander("📊 Fixture balance: KO slots & pitches per team", expanded=True):
            render_html(fixture_split_html(fixtures_df))

        render_html(fixtures_cards_html(fixtures_df, next_week))

    except Exception as e:
        st.error(f"Error loading Fixtures: {e}")
