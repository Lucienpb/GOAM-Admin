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


def run_scores_app():
    st.header("📘 GOAM Scores & Rounds")

    rounds = _get_rounds_state()

    # -----------------------------
    # 1. Upload full-season workbook
    # -----------------------------
    st.subheader("📂 Load full-season workbook")

    season_file = st.file_uploader(
        "Upload GOAM_Scores_2026.xlsx",
        type=["xlsx"],
        key="season_upload"
    )

    if season_file:
        sheets = GOAMLoader.load_season(season_file)
        season_rounds = GOAMCalculator.build_from_course_sheets(sheets)

        if not season_rounds.empty:
            rounds.rounds = [season_rounds]
            st.success("Season workbook loaded successfully.")

    # -----------------------------
    # 2. Upload single-round scorecard
    # -----------------------------
    st.subheader("📥 Upload scorecard (single round)")

    course_for_upload = st.selectbox(
        "Course:",
        ["Akasia", "PGC", "Kyalami", "Copperleaf", "Services"],
        key="scorecard_course"
    )

    scorecard_file = st.file_uploader(
        "Upload scorecard",
        type=["xlsx"],
        key="scorecard_upload"
    )

    if scorecard_file:
        try:
            df_round = GOAMLoader.load_single_round(scorecard_file)
            rounds.add_round(df_round, course_name=course_for_upload)
            st.success(f"Scorecard added for {course_for_upload}.")
        except Exception as e:
            st.error(f"Error: {e}")

    # -----------------------------
    # 3. Manual entry
    # -----------------------------
    st.subheader("✍️ Manual score entry")

    with st.form("manual_entry"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input("Player Name")
        with col2:
            course_manual = st.selectbox(
                "Course",
                ["Akasia", "PGC", "Kyalami", "Copperleaf", "Services"]
            )
        with col3:
            strokes = st.number_input("Strokes", min_value=40, max_value=140)
        with col4:
            ips = st.number_input("IPS", min_value=0, max_value=60)

        submitted = st.form_submit_button("Add Round")

    if submitted and name:
        df_manual = pd.DataFrame([{
            "Name": name,
            "Strokes": strokes,
            "IPS": ips
        }])
        rounds.add_round(df_manual, course_name=course_manual)
        st.success(f"Round added for {name} at {course_manual}.")

    # -----------------------------
    # 4. Build combined rounds table
    # -----------------------------
    all_rounds_df = rounds.get_all_rounds()

    if all_rounds_df.empty:
        st.info("No rounds loaded yet.")
        return

    # -----------------------------
    # 5. Course selection for leaderboards
    # -----------------------------
    st.subheader("🎯 Select courses to include in leaderboards")

    all_courses = GOAMCalculator.list_courses(all_rounds_df)
    
    # Get active courses (month <= current month) for default selection
    active_courses = GOAMCalculator.get_active_courses(all_rounds_df)

    selected_courses = st.multiselect(
        "Only include these courses:",
        all_courses,
        default=active_courses  # Default to active courses only
    )

    filtered_df = all_rounds_df[all_rounds_df["Course"].isin(selected_courses)]

    # -----------------------------
    # 6. Calculate IPS, Strokes, LIV
    # -----------------------------
    ips_table = GOAMCalculator.build_ips_leaderboard(filtered_df)
    strokes_table = GOAMCalculator.build_strokes_leaderboard(filtered_df)
    liv_table = GOAMCalculator.build_liv_leaderboard(filtered_df)
    course_sheets = GOAMCalculator.split_by_course(filtered_df)

    # -----------------------------
    # 7. Leaderboard Selector
    # -----------------------------
    st.subheader("🏆 Leaderboards")

    leaderboard_choice = st.selectbox(
        "Select leaderboard:",
        ["IPS", "Strokes", "LIV"],
        index=0  # Default to IPS
    )

    # -----------------------------
    # 8. Display selected leaderboard
    # -----------------------------
    if leaderboard_choice == "IPS":
        st.subheader("🏆 IPS Leaderboard (Best 6 + Course Breakdown)")
        st.dataframe(ips_table, use_container_width=True)

    elif leaderboard_choice == "Strokes":
        st.subheader("⛳ Strokes Leaderboard (Best 6 Over Par)")
        st.dataframe(strokes_table, use_container_width=True)

    elif leaderboard_choice == "LIV":
        st.subheader("🏁 LIV Team Leaderboard (Top 3 IPS per Course)")
        st.dataframe(liv_table, use_container_width=True)



    # -----------------------------
    # 8.1 View Score Cards
    # -----------------------------
    st.subheader("📂 View Score Cards")

    options = ["None"] + list(course_sheets.keys())
    choice = st.selectbox("Select Course", options)

    if choice in course_sheets:
        st.dataframe(course_sheets[choice], use_container_width=True)

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
