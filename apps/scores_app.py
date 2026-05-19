#---------------------------------
# GOAM Scores & Rounds App
#   - Load GOAM scores from JSON
#   - Build IPS, Strokes, LIV leaderboards 
#   - Show position changes with arrows
#   - Export updated workbook with new leaderboards
#---------------------------------  

import os
import streamlit as st
import pandas as pd

from backend.goam_loader import GOAMLoader
from backend.goam_rounds import GOAMRounds
from backend.goam_calculator import GOAMCalculator


def _get_rounds_state():
    if "goam_rounds" not in st.session_state:
        st.session_state.goam_rounds = GOAMRounds()
    return st.session_state.goam_rounds


def _format_pos_change(delta):
    """
    Convert numeric position change into arrow string:
    - delta > 0  → moved up (better position)  → ⬆️ delta
    - delta < 0  → moved down (worse position) → ⬇️ abs(delta)
    - delta == 0 → no change                   → ➡️
    - delta is None / no history               → –
    """
    if delta is None:
        return "–"
    try:
        d = int(delta)
    except (TypeError, ValueError):
        return "–"

    if d > 0:
        return f"⬆️ {d}"
    if d < 0:
        return f"⬇️ {abs(d)}"
    return "➡️"


def run_scores_app():
    st.header("📘 GOAM Scores & Rounds")

    rounds = _get_rounds_state()

    # -----------------------------
    # 1. Load GOAM scores from JSON
    # -----------------------------
    try:
        goam_scores = GOAMLoader.load_json_scores("data/goam_scores.json")
        season_rounds = GOAMCalculator.build_from_json(goam_scores)

        if not season_rounds.empty:
            rounds.rounds = [season_rounds]
            st.success("GOAM scores loaded from JSON.")
        else:
            st.info("No GOAM scores found. Load data via Data Manager.")
            return

    except Exception as e:
        st.error(f"Error loading GOAM scores: {e}")
        return

    # -----------------------------
    # 2. Build combined rounds table
    # -----------------------------
    all_rounds_df = rounds.get_all_rounds()

    if all_rounds_df.empty:
        st.info("No rounds available.")
        return

    # -----------------------------
    # 3. Course selection
    # -----------------------------
    st.subheader("🎯 Select courses to include in leaderboards")

    all_courses = GOAMCalculator.list_courses(all_rounds_df)
    active_courses = GOAMCalculator.get_active_courses(all_rounds_df)

    selected_courses = st.multiselect(
        "Only include these courses:",
        all_courses,
        default=active_courses
    )

    filtered_df = all_rounds_df[all_rounds_df["Course"].isin(selected_courses)]

    # -----------------------------
    # 4. Leaderboard calculations
    # -----------------------------
    ips_table = GOAMCalculator.build_ips_leaderboard(filtered_df)
    strokes_table = GOAMCalculator.build_strokes_leaderboard(filtered_df)
    liv_table = GOAMCalculator.build_liv_leaderboard(filtered_df)
    course_sheets = GOAMCalculator.split_by_course(filtered_df)

    if ips_table.empty:
        st.info("No IPS data available for selected courses.")
        return

    # Normalize column names just in case
    ips_table.rename(columns={c: c.strip() for c in ips_table.columns}, inplace=True)

    # Ensure Position exists (defensive)
    if "Position" not in ips_table.columns:
        if "IPS" in ips_table.columns:
            ips_table["Position"] = (
                ips_table["IPS"]
                .rank(ascending=False, method="min")
                .astype(int)
            )
        else:
            st.error("IPS column missing from IPS leaderboard.")
            return

    # -----------------------------
    # 5. Update position history & Pos Change arrows
    # -----------------------------
    # GOAMRounds is assumed to track numeric positions internally.
    rounds.update_position_history(ips_table)

    ips_table = ips_table.copy()
    if "Name" in ips_table.columns:
        ips_table.insert(2, "Pos Change", ips_table["Name"].apply(
            lambda name: _format_pos_change(rounds.get_position_change(name))
        ))
    else:
        ips_table.insert(2, "Pos Change", "–")

    # -----------------------------
    # 6. Leaderboard Selector
    # -----------------------------
    st.subheader("🏆 Leaderboards")

    leaderboard_choice = st.selectbox(
        "Select leaderboard:",
        ["IPS", "Strokes", "LIV"],
        index=0
    )

    # -----------------------------
    # 7. Display selected leaderboard
    # -----------------------------
    if leaderboard_choice == "IPS":
        st.subheader("🏆 IPS Leaderboard (Best 6 + Course Breakdown)")
        st.dataframe(ips_table, width="stretch")

    elif leaderboard_choice == "Strokes":
        st.subheader("⛳ Strokes Leaderboard (Best 6 Over Par)")
        st.dataframe(strokes_table, width="stretch")

    elif leaderboard_choice == "LIV":
        st.subheader("🏁 LIV Team Leaderboard (Top 3 IPS per Course)")
        st.dataframe(liv_table, width="stretch")

    # -----------------------------
    # 8. View Score Cards
    # -----------------------------
    st.subheader("📂 View Score Cards")

    options = ["None"] + list(course_sheets.keys())
    choice = st.selectbox("Select Course", options)

    if choice in course_sheets:
        st.dataframe(course_sheets[choice], width="stretch")

    # -----------------------------
    # 9. Export updated workbook
    # -----------------------------
    st.subheader("💾 Export updated GOAM workbook")

    output_file = GOAMCalculator.generate_output_filename()
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", output_file)

    with pd.ExcelWriter(output_path) as writer:
        ips_table.to_excel(writer, sheet_name="IPS", index=False)
        strokes_table.to_excel(writer, sheet_name="Strokes", index=False)
        liv_table.to_excel(writer, sheet_name="LIV", index=False)

        for course, df in course_sheets.items():
            df.to_excel(writer, sheet_name=course, index=False)

    with open(output_path, "rb") as f:
        st.download_button(
            label=f"Download {output_file}",
            data=f,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
