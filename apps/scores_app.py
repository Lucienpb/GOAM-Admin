import streamlit as st
import pandas as pd
from backend.goam_loader import GOAMLoader
from backend.goam_rounds import GOAMRounds
from backend.goam_calculator import GOAMCalculator

def run_scores_app():

    st.header("📘 GOAM Scores & Rounds")

    # Initialise storage
    if "goam_rounds" not in st.session_state:
        st.session_state.goam_rounds = GOAMRounds()

    rounds = st.session_state.goam_rounds

    # -------------------------
    # Upload Season Spreadsheet
    # -------------------------
    st.subheader("📤 Upload Season Spreadsheet")
    season_file = st.file_uploader("Upload GOAM_Scores_2026.xlsx", type=["xlsx"])

    if season_file:
        season_data = GOAMLoader.load_season(season_file)
        rounds.load_season(season_data)
        st.success("Season data loaded successfully!")

    st.write("---")

    # -------------------------
    # Upload Single Round
    # -------------------------
    st.subheader("📥 Upload Single Round")
    round_file = st.file_uploader("Upload a single round file", type=["xlsx"], key="single_round")

    if round_file:
        df = GOAMLoader.load_single_round(round_file)
        rounds.add_round(df)
        st.success("Round added!")

    st.write("---")

    # -------------------------
    # Manual Entry
    # -------------------------
    st.subheader("✍️ Enter New Round Manually")

    course = st.selectbox("Course", ["Akasia", "PGC", "Kyalami", "Copperleaf", "Services"])
    num_players = st.number_input("Number of players", min_value=1, max_value=40, value=20)

    if st.button("Create Entry Table"):
        st.session_state.entry_df = pd.DataFrame({
            "Name": ["" for _ in range(num_players)],
            "Strokes": [0 for _ in range(num_players)],
            "IPS": [0 for _ in range(num_players)],
        })

    if "entry_df" in st.session_state:
        edited = st.data_editor(st.session_state.entry_df, num_rows="dynamic")

        if st.button("Save Round"):
            rounds.add_round(edited, course_name=course)
            st.success("Round saved!")

    st.write("---")

    # -------------------------
    # Display Stats
    # -------------------------
    st.subheader("📊 Player Stats")

    all_rounds = rounds.get_all_rounds()

    if not all_rounds.empty:
        stats = GOAMCalculator.calculate_player_stats(all_rounds)
        st.dataframe(stats, use_container_width=True)
    else:
        st.info("No rounds loaded yet.")
