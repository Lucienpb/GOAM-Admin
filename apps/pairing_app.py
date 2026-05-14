"""
Pairing Matrix & Fourball App
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from utils.pairing_matrix import parse_pairings, build_matrix
from utils.fourball_generator import generate_fourballs, format_player

def run():
    st.header("⛳ Pairing Matrix & Fourball Generator")

    # --------- Section 1: Upload Pairings File ---------
    st.subheader("1️⃣ Upload Pairings File")

    uploaded_file = st.file_uploader("Upload pairings CSV", type=["csv"], key="pairings")

    matrix = None
    rounds = None

    if uploaded_file:
        rounds = parse_pairings(uploaded_file)
        matrix = build_matrix(rounds)

        st.subheader("📊 Pairing Matrix")
        with st.expander("View Matrix", expanded=False):
            st.dataframe(matrix)

        # Heatmap
        show_heatmap = st.checkbox("Show pairing heatmap")

        if show_heatmap:
            st.subheader("🔥 Pairing Heatmap")

            numeric_matrix = matrix.replace({"": 0, "-": 0}).astype(int)

            fig, ax = plt.subplots()
            im = ax.imshow(numeric_matrix.values, cmap="YlOrRd")

            ax.set_xticks(range(len(matrix.columns)))
            ax.set_yticks(range(len(matrix.index)))
            ax.set_xticklabels(matrix.columns, rotation=90)
            ax.set_yticklabels(matrix.index)

            plt.colorbar(im, ax=ax, label="Times paired")
            st.pyplot(fig)
        else:
            numeric_matrix = matrix.replace({"": 0, "-": 0}).astype(int)

        # Player pairing lookup
        st.subheader("🔍 Player Pairing Lookup")

        players_list = list(matrix.index)
        lookup_player = st.selectbox("Select a player for detailed view", players_list, key="lookup_player")
        show_played = st.checkbox("Show who I HAVE played with")
        show_not_played = st.checkbox("Show who I have NOT played with")

        if lookup_player:
            played_with = [
                p for p in players_list
                if matrix.loc[lookup_player, p] not in ["", "0", "-", None]
            ]
            not_played_with = [
                p for p in players_list
                if matrix.loc[lookup_player, p] in ["", "0", None]
            ]

            if show_played:
                st.markdown(f"### ✅ {lookup_player} HAS played with")
                st.write(played_with)

            if show_not_played:
                st.markdown(f"### ❌ {lookup_player} has NOT played with")
                st.write(not_played_with)

        # Download matrix
        csv = matrix.to_csv(sep=";").encode("utf-8")
        st.download_button(
            label="⬇️ Download Matrix as CSV",
            data=csv,
            file_name="pair_matrix.csv",
            mime="text/csv"
        )

    # --------- Section 2: Player List ---------
    st.subheader("2️⃣ Player List (Name + Team)")

    player_file = st.file_uploader("Upload player list CSV (Name,Team)", type=["csv"], key="players")

    if player_file:
        players_df = pd.read_csv(player_file)

        if "Name" not in players_df.columns or "Team" not in players_df.columns:
            st.error("CSV must contain columns: Name, Team")
        else:
            st.subheader("Current Players")
            with st.expander("View Players", expanded=False):
                st.dataframe(players_df)

            st.markdown("### ➕ Add New Player")
            new_name = st.text_input("Player Name")
            new_team = st.selectbox("Team", ["FF", "TT", "HB", "BB", "TS"])

            if st.button("Add Player"):
                if new_name.strip():
                    players_df.loc[len(players_df)] = [new_name.strip(), new_team]
                    st.success(f"Added {new_name} ({new_team})")
                else:
                    st.error("Name cannot be empty")

            st.session_state["players_df"] = players_df

    # --------- Section 3: Fourball Generator ---------
    st.subheader("3️⃣ Fourball Generator")

    if matrix is None:
        st.info("Upload a pairings file first to build the matrix.")
    elif "players_df" not in st.session_state or st.session_state["players_df"] is None:
        st.info("Upload a player list (Name, Team) to generate fourballs.")
    else:
        players_df = st.session_state["players_df"]

        strict_mode = st.checkbox("Strict mode (never allow 1- or 2-balls)", value=True)

        shuffle_seed = st.number_input(
            "Shuffle seed (change this number to reshuffle fourballs)",
            min_value=0,
            value=0,
            step=1
        )

        if st.button("Generate Fourballs"):
            players = list(players_df["Name"])
            teams = dict(zip(players_df["Name"], players_df["Team"]))

            final_groups, penalty = generate_fourballs(players, teams, matrix, strict_mode, shuffle_seed)

            st.subheader("🏌️ Fourballs for Next Month")

            whatsapp_lines = []

            for i, g in enumerate(final_groups, 1):
                team_set = {teams[p] for p in g}
                balance_score = len(team_set)

                conflicts = []
                for a, b in combinations(g, 2):
                    if penalty[a][b] > 0:
                        conflicts.append(f"{a}–{b} ({penalty[a][b]})")

                st.markdown("```\n" +
                            f"───────────────\n"
                            f" FOURBALL {i}\n"
                            f"───────────────\n" +
                            "\n".join(format_player(p, teams) for p in g) +
                            f"\n───────────────\n"
                            f"Team balance: {balance_score}\n"
                            f"Conflicts: {'None' if not conflicts else ', '.join(conflicts)}\n"
                            "```")

                whatsapp_lines.append(f"Fourball {i}: " + ", ".join(format_player(p, teams) for p in g))

            st.subheader("📲 WhatsApp Text")
            st.text_area("Copy & paste to WhatsApp:", "\n".join(whatsapp_lines), height=150)
