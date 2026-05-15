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

    # =========================
    # 1. Upload full-season file
    # =========================
    st.subheader("📂 Load full-season workbook")

    season_file = st.file_uploader(
        "Upload GOAM_Scores_2026.xlsx",
        type=["xlsx"],
        key="season_upload"
    )

    all_rounds_df = pd.DataFrame(columns=["Name", "Course", "Strokes", "IPS", "Team"])

    if season_file:
        sheets = GOAMLoader.load_season(season_file)
        season_rounds = GOAMCalculator.build_from_course_sheets(sheets)
        if not season_rounds.empty:
            rounds.add_round(season_rounds, course_name="")  # course already in df
        all_rounds_df = rounds.get_all_rounds()

    # =========================
    # 2. Upload single-round scorecard
    # =========================
    st.subheader("📥 Upload scorecard (single round)")

    course_for_upload = st.selectbox(
        "Course for this scorecard:",
        ["Akasia", "PGC", "Kyalami", "Copperleaf", "Services"],
        key="scorecard_course"
    )

    scorecard_file = st.file_uploader(
        "Upload scorecard file",
        type=["xlsx"],
        key="scorecard_upload"
    )

    if scorecard_file is not None:
        try:
            df_round = GOAMLoader.load_single_round(scorecard_file)
            rounds.add_round(df_round, course_name=course_for_upload)
            st.success(f"Scorecard for {course_for_upload} added.")
        except Exception as e:
            st.error(f"Error reading scorecard: {e}")

    # =========================
    # 3. Manual entry
    # =========================
    st.subheader("✍️ Manual score entry")

    with st.form("manual_entry_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input("Player Name")
        with col2:
            course_manual = st.selectbox(
                "Course",
                ["Akasia", "PGC", "Kyalami", "Copperleaf", "Services"],
                key="manual_course"
            )
        with col3:
            strokes = st.number_input("Strokes", min_value=40, max_value=140, step=1)
        with col4:
            ips = st.number_input("IPS", min_value=0, max_value=60, step=1)

        submitted = st.form_submit_button("Add Round")

    if submitted and name:
        df_manual = pd.DataFrame([{
            "Name": name,
            "Strokes": strokes,
            "IPS": ips
        }])
        rounds.add_round(df_manual, course_name=course_manual)
        st.success(f"Round added for {name} at {course_manual}.")

    # =========================
    # 4. Build combined rounds table
    # =========================
    all_rounds_df = rounds.get_all_rounds()

    if all_rounds_df.empty:
        st.info("No rounds loaded yet. Upload a season file, a scorecard, or add a manual round.")
        return

    # =========================
    # 5. Calculate IPS, Strokes, LIV
    # =========================
    ips_table = GOAMCalculator.calculate_best_six_ips(all_rounds_df)
    strokes_table = GOAMCalculator.calculate_strokes(all_rounds_df)
    liv_table = GOAMCalculator.calculate_liv(all_rounds_df)
    course_sheets = GOAMCalculator.split_by_course(all_rounds_df)

    # =========================
    # 6. Display IPS always
    # =========================
    st.subheader("🏆 IPS Leaderboard (Best 6) — Always Visible")
    st.dataframe(ips_table, use_container_width=True)

    # =========================
    # 7. Optionally display other sheets
    # =========================
    st.subheader("📂 View other tables")

    options = ["None", "Strokes", "LIV"] + list(course_sheets.keys())
    choice = st.selectbox("Select table to view:", options)

    if choice == "Strokes":
        st.dataframe(strokes_table, use_container_width=True)
    elif choice == "LIV":
        st.dataframe(liv_table, use_container_width=True)
    elif choice in course_sheets:
        st.dataframe(course_sheets[choice], use_container_width=True)

    # =========================
    # 8. Save back into Excel with month in filename
    # =========================
    st.subheader("💾 Export updated GOAM workbook")

    output_file = GOAMCalculator.generate_output_filename()
    output_path = os.path.join("data", output_file)

    os.makedirs("data", exist_ok=True)

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
