"""
Pairing Matrix & Fourball App (JSON Version)
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

from utils.json_utils import load_json, save_json
from utils.fourball_generator import generate_fourballs
from utils.name_utils import (
    normalize_name,
    build_alias_map,
    build_display_name_map
)


# ---------------------------------------------------------
# NAME VALIDATION & MAPPING LAYER
# ---------------------------------------------------------
def validate_and_map_names(players_df, pairings_json, alias_map):
    warnings = []

    valid_players = {normalize_name(p, alias_map): p for p in players_df["name"]}

    cleaned_pairings = {}

    for month, data in pairings_json.items():
        cleaned_fourballs = []

        for fb in data["fourballs"]:
            cleaned_players = []
            for p in fb["players"]:
                np = normalize_name(p, alias_map)

                if np not in valid_players:
                    warnings.append(f"⚠️ '{p}' in {month} not found in players.json")

                cleaned_players.append(np)

            cleaned_fourballs.append({
                "fourball": fb["fourball"],
                "players": cleaned_players
            })

        cleaned_pairings[month] = {
            "course": data["course"],
            "fourballs": cleaned_fourballs
        }

    return cleaned_pairings, warnings


# ---------------------------------------------------------
# BUILD PAIRING MATRIX (NOW SUPPORTS MISSING PLAYERS)
# ---------------------------------------------------------
def build_pairing_matrix(pairings_json, players_df, alias_map):
    """
    Build a pairing count matrix from all months in pairings.json.
    Ensures ALL players appear in the matrix, even if missing from players.json.
    """

    # 1️⃣ Start with official players
    official_players = set(players_df["name"].apply(lambda x: normalize_name(x, alias_map)))

    # 2️⃣ Collect all players from pairings.json
    pairing_players = set()
    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            for p in fb["players"]:
                pairing_players.add(normalize_name(p, alias_map))

    # 3️⃣ Combine both sets
    all_players = sorted(official_players.union(pairing_players))

    # 4️⃣ Build matrix
    matrix = pd.DataFrame(0, index=all_players, columns=all_players, dtype=int)

    # 5️⃣ Count pairings
    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            players = [normalize_name(p, alias_map) for p in fb["players"]]
            for a, b in combinations(players, 2):
                if a in matrix.index and b in matrix.columns:
                    matrix.loc[a, b] += 1
                    matrix.loc[b, a] += 1

    # 6️⃣ Diagonal
    for p in all_players:
        matrix.loc[p, p] = -1

    return matrix.replace(-1, "-")


# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
def run():
    st.header("⛳ Pairing Matrix & Fourball Generator (JSON Mode)")

    players = load_json("data/players.json")
    raw_pairings = load_json("data/pairings.json")

    if not players:
        st.error("No players found.")
        return

    if not raw_pairings:
        st.error("No pairings found.")
        return

    players_df = pd.DataFrame(players)

    # Build alias + display maps
    alias_map = build_alias_map(players_df)
    display_map = build_display_name_map(players_df)

    # Validate & map names
    pairings_json, warnings = validate_and_map_names(players_df, raw_pairings, alias_map)

    if warnings:
        with st.expander("⚠️ Name Mismatches Found", expanded=False):
            for w in warnings:
                st.write(w)

    # Build pairing matrix
    st.subheader("📊 Pairing Matrix (from JSON history)")
    matrix = build_pairing_matrix(pairings_json, players_df, alias_map)

    # ---------------------------------------------------------
    # EXTEND DISPLAY MAP WITH MISSING PLAYERS
    # ---------------------------------------------------------
    official_set = set(players_df["name"].apply(lambda x: normalize_name(x, alias_map)))

    for p in matrix.index:
        if p not in official_set:
            # Missing from players.json → mark with *
            display_map[p] = f"{p}*"
        else:
            # Ensure official players always have a display name
            if p not in display_map:
                display_map[p] = p


    # ---------------------------------------------------------
    # DISPLAY MATRIX USING DISPLAY NAMES
    # ---------------------------------------------------------
    matrix_display = matrix.copy()
    matrix_display.index = [display_map[p] for p in matrix.index]
    matrix_display.columns = [display_map[p] for p in matrix.columns]

    with st.expander("View Matrix", expanded=False):
        st.dataframe(matrix_display)

    # Heatmap
    show_heatmap = st.checkbox("Show pairing heatmap")

    numeric_matrix = matrix.replace({"-": 0}).astype(int)

    if show_heatmap:
        st.subheader("🔥 Pairing Heatmap")

        fig, ax = plt.subplots()
        im = ax.imshow(numeric_matrix.values, cmap="YlOrRd")

        ax.set_xticks(range(len(matrix.columns)))
        ax.set_yticks(range(len(matrix.index)))
        ax.set_xticklabels([display_map[p] for p in matrix.columns], rotation=90)
        ax.set_yticklabels([display_map[p] for p in matrix.index])

        plt.colorbar(im, ax=ax, label="Times paired")
        st.pyplot(fig)

    # ---------------------------------------------------------
    # PLAYER LOOKUP
    # ---------------------------------------------------------
    st.subheader("🔍 Player Pairing Lookup")

    # Clean player list (strip spaces)
    players_list = [p.strip() for p in matrix.index]

    lookup_player = st.selectbox(
        "Select a player",
        players_list,
        format_func=lambda p: display_map[p.strip()]
    )

    if lookup_player:
        lookup_player = lookup_player.strip()  # ensure clean key

        played_with = []
        not_played_with = []

        for p in players_list:
            p_clean = p.strip()

            if p_clean == lookup_player:
                continue

            val = matrix.loc[lookup_player, p_clean]

            if isinstance(val, int) and val > 0:
                played_with.append(p_clean)
            else:
                not_played_with.append(p_clean)

        st.markdown(f"### ✅ {display_map[lookup_player]} HAS played with")
        st.table(pd.DataFrame({"Player": [display_map[p] for p in played_with]}))

        st.markdown(f"### ❌ {display_map[lookup_player]} has NOT played with")
        st.table(pd.DataFrame({"Player": [display_map[p] for p in not_played_with]}))


    # ---------------------------------------------------------
    # FOURBALL GENERATOR
    # ---------------------------------------------------------
    st.subheader("3️⃣ Fourball Generator")

    strict_mode = st.checkbox("Strict mode (never allow 1- or 2-balls)", value=True)

    shuffle_seed = st.number_input(
        "Shuffle seed",
        min_value=0,
        value=0,
        step=1
    )

    if st.button("Generate Fourballs"):
        players_list = list(matrix.index)
        teams = dict(zip(players_df["name"].apply(lambda x: normalize_name(x, alias_map)), players_df["team"]))

        final_groups, penalty = generate_fourballs(players_list, teams, matrix, strict_mode, shuffle_seed)

        st.subheader("🏌️ Fourballs for Next Month")

        whatsapp_lines = []

        for i, g in enumerate(final_groups, 1):
            conflicts = []
            for a, b in combinations(g, 2):
                if penalty[a][b] > 0:
                    conflicts.append(f"{display_map[a]}–{display_map[b]} ({penalty[a][b]})")

            st.markdown("```\n" +
                        f"───────────────\n"
                        f" FOURBALL {i}\n"
                        f"───────────────\n" +
                        "\n".join(display_map[p] for p in g) +
                        f"\n───────────────\n"
                        f"Conflicts: {'None' if not conflicts else ', '.join(conflicts)}\n"
                        "```")

            whatsapp_lines.append(f"Fourball {i}: " + ", ".join(display_map[p] for p in g))

        st.subheader("📲 WhatsApp Text")
        st.text_area("Copy & paste to WhatsApp:", "\n".join(whatsapp_lines), height=150)
