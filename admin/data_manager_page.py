import streamlit as st
import pandas as pd
from utils.json_utils import load_json, save_json

def convert_course_excel_to_json(df):
    courses = {}

    for _, row in df.iterrows():
        course = row["Course Name"].strip()
        tee = row["Tee Name"].strip()

        if course not in courses:
            courses[course] = {"tees": {}}

        courses[course]["tees"][tee] = {
            "slope": float(row["Slope Rating"]),
            "rating": float(row["Course Rating"]),
            "par": int(row["Par"])
        }

    return courses


def full_load_course_data(df):
    data = convert_course_excel_to_json(df)
    save_json("data/course_data.json", data)


def delta_load_course_data(df):
    existing = load_json("data/course_data.json")
    incoming = convert_course_excel_to_json(df)

    for course, data in incoming.items():
        if course not in existing:
            existing[course] = data
        else:
            existing[course]["tees"].update(data["tees"])

    save_json("data/course_data.json", existing)


def show_data_manager_page():
    st.title("📂 Data Manager (Admin Only)")

    st.subheader("📘 Course Information")

    uploaded = st.file_uploader("Upload Course_Information.xlsx", type=["xlsx"])
    mode = st.radio("Load Mode", ["FULL", "DELTA"])

    if st.button("Process Course Data"):
        if uploaded:
            df = pd.read_excel(uploaded)

            if mode == "FULL":
                full_load_course_data(df)
                st.success("Course data fully replaced.")
            else:
                delta_load_course_data(df)
                st.success("Course data merged (delta load).")
        else:
            st.error("Please upload a file.")
# -------------------------------------------------------------------
# PLAYERS SECTION
# -------------------------------------------------------------------
st.subheader("👥 Players")

uploaded_players = st.file_uploader("Upload Players.xlsx", type=["xlsx"], key="players_upload")
mode_players = st.radio("Load Mode (Players)", ["FULL", "DELTA"], key="players_mode")

def convert_players_excel_to_json(df):
    players = []

    for _, row in df.iterrows():
        players.append({
            "name": row["Name"].strip(),
            "membership": str(row["Membership"]).strip(),
            "handicap_index": float(row["Handicap Index"]),
            "team": row["Team"].strip() if "Team" in df.columns else None
        })

    return players


def full_load_players(df):
    data = convert_players_excel_to_json(df)
    save_json("data/players.json", data)


def delta_load_players(df):
    existing = load_json("data/players.json")
    incoming = convert_players_excel_to_json(df)

    # Convert existing to map by membership number
    existing_map = {p["membership"]: p for p in existing}

    # Merge incoming
    for p in incoming:
        existing_map[p["membership"]] = p

    merged = list(existing_map.values())
    save_json("data/players.json", merged)


if st.button("Process Player Data"):
    if uploaded_players:
        df = pd.read_excel(uploaded_players)

        if mode_players == "FULL":
            full_load_players(df)
            st.success("Players fully replaced.")
        else:
            delta_load_players(df)
            st.success("Players merged (delta load).")
    else:
        st.error("Please upload a file.")
# -------------------------------------------------------------------
# PAIRINGS SECTION (GOAM 4-Ball Format with Month + Course)
# -------------------------------------------------------------------
st.subheader("⛳ Pairings (GOAM 4-Ball)")

uploaded_pairings = st.file_uploader("Upload Pairings.xlsx", type=["xlsx"], key="pairings_upload")
mode_pairings = st.radio("Load Mode (Pairings)", ["FULL", "DELTA"], key="pairings_mode")

def extract_month_and_course(df):
    """
    Reads the first cell of the sheet to extract:
    - Month key (e.g., "Feb'26")
    - Course name (e.g., "Akasia GC")
    """
    header_text = str(df.columns[0])

    # Example: "Feb'26: 4 Ball Pairings - Akasia GC"
    if ":" in header_text:
        month_part, rest = header_text.split(":", 1)
        month_key = month_part.strip()
    else:
        month_key = "Unknown"

    if "-" in header_text:
        course = header_text.split("-")[-1].strip()
    else:
        course = "Unknown Course"

    return month_key, course


def convert_pairings_excel_to_json(df):
    month_key, course = extract_month_and_course(df)

    # The actual data starts after the header row
    # Ensure correct column names
    df.columns = ["Fourball", "Player 1", "Player 2", "Player 3", "Player 4"]

    fourballs = []

    for _, row in df.iterrows():
        if str(row["Fourball"]).strip().isdigit():
            fb_no = int(row["Fourball"])
        else:
            continue

        players = []
        for col in ["Player 1", "Player 2", "Player 3", "Player 4"]:
            if isinstance(row[col], str) and row[col].strip():
                players.append(row[col].strip())

        fourballs.append({
            "fourball": fb_no,
            "players": players
        })

    return month_key, {
        "course": course,
        "fourballs": fourballs
    }


def full_load_pairings(df):
    month_key, data = convert_pairings_excel_to_json(df)
    save_json("data/pairings.json", {month_key: data})


def delta_load_pairings(df):
    existing = load_json("data/pairings.json")
    month_key, data = convert_pairings_excel_to_json(df)

    existing[month_key] = data  # overwrite or add
    save_json("data/pairings.json", existing)


if st.button("Process Pairing Data"):
    if uploaded_pairings:
        df = pd.read_excel(uploaded_pairings, header=0)

        if mode_pairings == "FULL":
            full_load_pairings(df)
            st.success("Pairings fully replaced.")
        else:
            delta_load_pairings(df)
            st.success("Pairings merged (delta load).")
    else:
        st.error("Please upload a file.")
