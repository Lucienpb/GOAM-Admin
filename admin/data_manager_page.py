#######################################
# Data Manager Page (Admin Only)
#######################################
# Allows admins to upload Excel files to update:    
# - Course information (course_data.json)
# - Player information (players.json)
# - Pairings information (pairings.json)    
# - GOAM Scores (goam_scores.json) with derived fields
#--------------
import streamlit as st
import pandas as pd
from utils.json_utils import load_json, save_json

def convert_course_excel_to_json(df):
    courses = {}

    for _, row in df.iterrows():
        course = safe_str(row.get("Course Name"))
        tee = "" if pd.isna(row.get("Tee Name")) else str(row["Tee Name"]).strip()

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
    
    def safe_str(value):
        if value is None:
            return ""
        if isinstance(value, float):  # catches NaN
            return ""
        return str(value).strip()
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
# -------------------------------------------------------------------
# GOAM SCORES SECTION (with derived fields)
# -------------------------------------------------------------------
    st.subheader("📘 GOAM Scores 2026 (with derived fields)")

    uploaded_scores = st.file_uploader(
        "Upload GOAM_Scores_2026_upload.xlsx",
        type=["xlsx"],
        key="goam_scores_upload"
    )
    mode_scores = st.radio("Load Mode (GOAM Scores)", ["FULL", "DELTA"], key="goam_scores_mode")

    SHEET_MONTH_MAP = {
        "Akasia": "Feb'26",
        "PGC": "Mar'26",
        "Kyalami": "Apr'26",
        "CopperLeaf": "May'26",
        "Services": "Jun'26",
        "July": "Jul'26",
        "August": "Aug'26",
        "September": "Sep'26",
        "October": "Oct'26",
    }


    def compute_derived_fields(players):
        """Compute Best Gross, Best Nett, OX Nau, Placements, LIV totals, Pool, Fines."""
        # Best Gross
        best_gross_player = min(players, key=lambda p: p.get("strokes", 999))
        best_gross = best_gross_player["name"]

        # Best Nett (only if handicap exists)
        for p in players:
            if "handicap" in p and p["handicap"] not in [None, "", 0]:
                p["nett"] = p["strokes"] - int(p["handicap"])
            else:
                p["nett"] = None

        nett_players = [p for p in players if p["nett"] is not None]
        best_nett = min(nett_players, key=lambda p: p["nett"])["name"] if nett_players else None

        # OX Nau = lowest IPS
        ox_nau = min(players, key=lambda p: p.get("ips", 999))["name"]

        # Placements (sorted by IPS desc)
        placements = sorted(players, key=lambda p: p.get("ips", 0), reverse=True)
        placements = [
            {"position": i + 1, "name": p["name"], "ips": p["ips"]}
            for i, p in enumerate(placements)
        ]

        # LIV totals = top 3 IPS per team
        team_map = {}
        for p in players:
            team = p.get("team", "")
            team_map.setdefault(team, []).append(p.get("ips", 0))

        liv_totals = {
            team: sum(sorted(ips_list, reverse=True)[:3])
            for team, ips_list in team_map.items()
        }

        # Pool winner (highest payout)
        pool_players = [p for p in players if p.get("pool_payouts")]
        pool_winner = max(pool_players, key=lambda p: p["pool_payouts"])["name"] if pool_players else None

        # Fines total
        fines_total = sum([p.get("fines", 0) or 0 for p in players])

        return {
            "best_gross": best_gross,
            "best_nett": best_nett,
            "ox_nau": ox_nau,
            "placements": placements,
            "liv_totals": liv_totals,
            "pool_winner": pool_winner,
            "fines_total": fines_total
        }


    def convert_goam_scores_workbook_to_json(xls):
        result = {}

        for sheet_name, df in xls.items():
            if sheet_name not in SHEET_MONTH_MAP:
                continue

            month_key = SHEET_MONTH_MAP[sheet_name]
            course_name = sheet_name

            df.columns = [str(c).strip() for c in df.columns]

            players = []
            for _, row in df.iterrows():
                name = str(row.get("Name", "")).strip()
                if not name:
                    continue

                player = {
                    "name": name,
                    "strokes": int(row.get("Strokes", 0)),
                    "ips": int(row.get("IPS", 0)),
                    "team": str(row.get("LIV", "")).strip()
                }

                # Optional extended fields
                for col in ["Handicap", "NP1", "NP2", "LD1", "LD2", "BG", "BN", "Pool Bet", "Pool Payouts", "Fines"]:
                    if col in df.columns:
                        key = col.lower().replace(" ", "_")
                        player[key] = row.get(col)

                players.append(player)

            # Compute derived fields
            derived = compute_derived_fields(players)

            result[month_key] = {
                "course": course_name,
                "players": players,
                **derived
            }

        return result


    def full_load_goam_scores(xls):
        data = convert_goam_scores_workbook_to_json(xls)
        save_json("data/goam_scores.json", data)


    def delta_load_goam_scores(xls):
        existing = load_json("data/goam_scores.json")
        incoming = convert_goam_scores_workbook_to_json(xls)

        for month, data in incoming.items():
            existing[month] = data

        save_json("data/goam_scores.json", existing)


    if st.button("Process GOAM Scores 2026"):
        if uploaded_scores:
            xls = pd.read_excel(uploaded_scores, sheet_name=None)

            if mode_scores == "FULL":
                full_load_goam_scores(xls)
                st.success("GOAM scores fully replaced for 2026.")
            else:
                delta_load_goam_scores(xls)
                st.success("GOAM scores merged (delta load).")
        else:
            st.error("Please upload the GOAM_Scores_2026_upload.xlsx workbook.")
