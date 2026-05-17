"""
Pairing Matrix & Fourball App (JSON Version)
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

from utils.json_utils import load_json, save_json
from utils.fourball_generator import generate_fourballs, format_player


def build_pairing_matrix(pairings_json):
    """
    Build a pairing count matrix from all months in pairings.json
    """
    # Collect all players
    all_players = set()
    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            for p in fb["players"]:
                all_players.add(p)

    all_players = sorted(all_players)

    # Initialize matrix
    matrix = pd.DataFrame("", index=all_players, columns=all_players)

    # Count pairings
    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            players = fb["players"]
            for a, b in combinations(players, 2):
                if matrix.loc[a, b] in ["", "-", None]:
                    matrix.loc[a, b] = 1
                    matrix.loc[b, a] = 1
                else:
                    matrix.loc[a, b] += 1
                    matrix.loc[b, a] += 1

    # Diagonal
    for p in all_players:
        matrix.loc[p, p] = "-"

    return matrix


def run():
    st.header("⛳ Pairing Matrix & Fourball Generator (JSON Mode)")

    # Load JSON data
    players = load_json("data/players.json")
    pairings_json = load_json("data/pairings.json")

    if not players:
        st.error("No players found. Please upload Players.xlsx in the Data Manager.")
        return

    if not pairings_json:
        st.error("No pairings found. Please upload Pairings.xlsx in the Data Manager.")
        return

    # Convert players JSON to DataFrame
    players_df = pd.DataFrame(players)

    # Build pairing matrix
    st.subheader("📊 Pairing Matrix (from JSON history)")
    matrix = build_pairing_matrix(pairings_json)

    with st.expander("View Matrix", expanded=False):
        st.dataframe(matrix)

    # Heatmap
    show_heatmap = st.checkbox("Show pairing heatmap")

    numeric_matrix = matrix.replace({"": 0, "-": 0}).astype(int)

    if show_heatmap:
        st.subheader("🔥 Pairing Heatmap")

        fig, ax = plt.subplots()
        im = ax.imshow(numeric_matrix.values, cmap="YlOrRd")

        ax.set_xticks(range(len(matrix.columns)))
        ax.set_yticks(range(len(matrix.index)))
        ax.set_xticklabels(matrix.columns, rotation=90)
        ax.set_yticklabels(matrix.index)

        plt.colorbar(im, ax=ax, label="Times paired")
        st.pyplot(fig)

    # Player lookup
    st.subheader("🔍 Player Pairing Lookup")

    players_list = list(matrix.index)
    lookup_player = st.selectbox("Select a player", players_list)

    if lookup_player:
        played_with = [
            p for p in players_list
            if matrix.loc[lookup_player, p] not in ["", "0", "-", None]
        ]
        not_played_with = [
            p for p in players_list
            if matrix.loc[lookup_player, p] in ["", "0", None]
        ]

        st.markdown(f"### ✅ {lookup_player} HAS played with")
        st.write(played_with)

        st.markdown(f"### ❌ {lookup_player} has NOT played with")
        st.write(not_played_with)

    # Fourball generator
    st.subheader("3️⃣ Fourball Generator")

    strict_mode = st.checkbox("Strict mode (never allow 1- or 2-balls)", value=True)

    shuffle_seed = st.number_input(
        "Shuffle seed (change this number to reshuffle fourballs)",
        min_value=0,
        value=0,
        step=1
    )

    if st.button("Generate Fourballs"):
        players_list = list(players_df["name"])
        teams = dict(zip(players_df["name"], players_df["team"]))

        final_groups, penalty = generate_fourballs(players_list, teams, matrix, strict_mode, shuffle_seed)

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
    # -------------------------------------------------------------------
    # ADMIN-ONLY: SAVE GENERATED FOURBALLS BACK INTO JSON HISTORY
    # -------------------------------------------------------------------
    if st.session_state.get("authenticated") and st.session_state.get("role") == "admin":

        st.subheader("💾 Save Fourballs to GOAM History")

        month_key = st.text_input("Month Key (e.g., Jun'26)")
        course_name = st.text_input("Course Name (e.g., Copperleaf)")

        if st.button("Save Fourballs to History"):
            if not month_key.strip():
                st.error("Month key is required.")
            elif not course_name.strip():
                st.error("Course name is required.")
            else:
                pairings_json = load_json("data/pairings.json")

                new_month_data = {
                    "course": course_name.strip(),
                    "fourballs": [
                        {
                            "fourball": i + 1,
                            "players": g
                        }
                        for i, g in enumerate(final_groups)
                    ]
                }

                pairings_json[month_key.strip()] = new_month_data
                save_json("data/pairings.json", pairings_json)

                st.success(f"Fourballs saved under {month_key}!")
