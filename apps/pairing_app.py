"""
Pairing Matrix & Fourball App (JSON Version) — TABBED VERSION
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

from utils.json_utils import load_json
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
# BUILD PAIRING MATRIX
# ---------------------------------------------------------
def build_pairing_matrix(pairings_json, players_df, alias_map):
    official_players = set(players_df["name"].apply(lambda x: normalize_name(x, alias_map)))

    pairing_players = set()
    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            for p in fb["players"]:
                pairing_players.add(normalize_name(p, alias_map))

    all_players = sorted(official_players.union(pairing_players))

    matrix = pd.DataFrame(0, index=all_players, columns=all_players, dtype=int)

    for month, data in pairings_json.items():
        for fb in data["fourballs"]:
            players = [normalize_name(p, alias_map) for p in fb["players"]]
            for a, b in combinations(players, 2):
                matrix.loc[a, b] += 1
                matrix.loc[b, a] += 1

    for p in all_players:
        matrix.loc[p, p] = 0

    return matrix


# ---------------------------------------------------------
# FORMAT PLAYER DISPLAY
# ---------------------------------------------------------
def format_player(p, display_map, teams, player_modes):
    nick = display_map.get(p, p)
    team = teams.get(p, "")
    mode = player_modes.get(p, "Walking 🚶‍♂️")
    icon = "🛺" if "Carting" in mode else "🚶‍♂️"
    team_part = f" ({team})" if team else ""
    return f"{nick}{team_part} {icon}"


# ---------------------------------------------------------
# MAIN APP (TABS)
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

    alias_map = build_alias_map(players_df)
    display_map = build_display_name_map(players_df)

    pairings_json, warnings = validate_and_map_names(players_df, raw_pairings, alias_map)

    if warnings:
        with st.expander("⚠️ Name Mismatches Found", expanded=False):
            for w in warnings:
                st.write(w)

    tab_matrix, tab_fourball = st.tabs(["📊 Matrix", "🏌️ Gen. 4 Ball"])

    # ---------------------------------------------------------
    # TAB 1 — PAIRING MATRIX
    # ---------------------------------------------------------
    with tab_matrix:
        st.subheader("📊 Pairing Matrix (from JSON history)")

        matrix = build_pairing_matrix(pairings_json, players_df, alias_map)

        official_set = set(players_df["name"].apply(lambda x: normalize_name(x, alias_map)))
        for p in matrix.index:
            if p not in official_set:
                display_map[p] = f"{p}*"
            else:
                if p not in display_map:
                    display_map[p] = p

        matrix_display = matrix.copy().astype(object)
        for p in matrix_display.index:
            matrix_display.loc[p, p] = "-"

        matrix_display.index = [display_map[p] for p in matrix.index]
        matrix_display.columns = [display_map[p] for p in matrix.columns]

        with st.expander("View Matrix", expanded=False):
            st.dataframe(matrix_display)

        show_heatmap = st.checkbox("Show pairing heatmap")

        if show_heatmap:
            st.subheader("🔥 Pairing Heatmap")

            numeric_matrix = matrix.astype(int)

            fig, ax = plt.subplots()
            im = ax.imshow(numeric_matrix.values, cmap="YlOrRd")

            ax.set_xticks(range(len(matrix.columns)))
            ax.set_yticks(range(len(matrix.index)))
            ax.set_xticklabels([display_map[p] for p in matrix.columns], rotation=90)
            ax.set_yticklabels([display_map[p] for p in matrix.index])

            plt.colorbar(im, ax=ax, label="Times paired")
            st.pyplot(fig)

        st.subheader("🔍 Player Pairing Lookup")

        players_list = [p.strip() for p in matrix.index]

        lookup_player = st.selectbox(
            "Select a player",
            players_list,
            format_func=lambda p: display_map[p.strip()]
        )

        if lookup_player:
            lookup_player = lookup_player.strip()

            played_with = []
            not_played_with = []

            for p in players_list:
                if p == lookup_player:
                    continue

                val = matrix.loc[lookup_player, p]

                if isinstance(val, int) and val > 0:
                    played_with.append(p)
                else:
                    not_played_with.append(p)

            st.markdown(f"### ✅ {display_map[lookup_player]} HAS played with")
            st.table(pd.DataFrame({"Player": [display_map[p] for p in played_with]}))

            st.markdown(f"### ❌ {display_map[lookup_player]} has NOT played with")
            st.table(pd.DataFrame({"Player": [display_map[p] for p in not_played_with]}))

    # ---------------------------------------------------------
    # TAB 2 — FOURBALL GENERATOR
    # ---------------------------------------------------------
    with tab_fourball:
        st.subheader("3️⃣ Fourball Generator")

        matrix = build_pairing_matrix(pairings_json, players_df, alias_map)
        all_players = list(matrix.index)

        st.subheader("📝 Select Players Playing This Month")
        selected_players = st.multiselect(
            "Choose players for this month",
            all_players,
            default=all_players,
            format_func=lambda p: display_map[p]
        )

        st.subheader("➕ Add Guest Players")
        guest_name = st.text_input("Guest name")
        guest_cart = st.checkbox("Guest is carting 🛺", value=False)

        if st.button("Add Guest"):
            if guest_name.strip():
                np = normalize_name(guest_name.strip(), alias_map)
                if np not in selected_players:
                    selected_players.append(np)
                display_map[np] = guest_name.strip()
                st.success(f"Guest added: {guest_name}")

        # ---------------------------------------------------------
        # WALKING / CARTING TABLE LAYOUT (NAME LEFT, ONE BIG CHECKBOX RIGHT)
        # ---------------------------------------------------------
        st.subheader("🚶‍♂️ / 🛺 Walking or Carting")

        header_cols = st.columns([2.5, 1])
        with header_cols[0]:
            st.markdown("### Player")
        with header_cols[1]:
            st.markdown("### Carting")

        # Make Streamlit checkboxes bigger using CSS
        st.markdown("""
            <style>
                .big-checkbox .stCheckbox > label > div:first-child {
                    transform: scale(1.5);
                    margin-left: -8px;
                    margin-top: 2px;
                }
            </style>
        """, unsafe_allow_html=True)

        player_modes = {}

        for p in selected_players:
            c1, c2 = st.columns([2.5, 1])

            with c1:
                st.markdown(
                    f"<div style='font-size:1.1rem; font-weight:600; margin-top:6px;'>{display_map[p]}</div>",
                    unsafe_allow_html=True
                )

            with c2:
                st.markdown("<div class='big-checkbox'>", unsafe_allow_html=True)
                is_cart = st.checkbox("", key=f"cart_{p}", label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)

            player_modes[p] = "Carting 🛺" if is_cart else "Walking 🚶‍♂️"

        strict_mode = st.checkbox("Strict mode (never allow 1- or 2-balls)", value=True)

        shuffle_seed = st.number_input(
            "Shuffle seed",
            min_value=0,
            value=0,
            step=1
        )

        if st.button("Generate Fourballs"):
            if len(selected_players) < 3:
                st.error("Need at least 3 players to generate fourballs.")
                return

            teams = dict(
                zip(
                    players_df["name"].apply(lambda x: normalize_name(x, alias_map)),
                    players_df["team"]
                )
            )

            final_groups, penalty = generate_fourballs(
                selected_players,
                teams,
                matrix,
                strict_mode,
                shuffle_seed,
                player_modes
            )

            st.subheader("🏌️ Fourballs for Next Month")

            rows = []
            for i, g in enumerate(final_groups, 1):
                row = {
                    "Fourball": i,
                    "Player 1": format_player(g[0], display_map, teams, player_modes) if len(g) > 0 else "",
                    "Player 2": format_player(g[1], display_map, teams, player_modes) if len(g) > 1 else "",
                    "Player 3": format_player(g[2], display_map, teams, player_modes) if len(g) > 2 else "",
                    "Player 4": format_player(g[3], display_map, teams, player_modes) if len(g) > 3 else "",
                }
                rows.append(row)

            df = pd.DataFrame(rows)

            def color_mode(val):
                if isinstance(val, str) and "🛺" in val:
                    return "color: #0b3d91; font-weight: 600;"
                if isinstance(val, str) and "🚶‍♂️" in val:
                    return "color: #1b7f3b; font-weight: 600;"
                return ""

            styled = df.style.applymap(color_mode, subset=["Player 1", "Player 2", "Player 3", "Player 4"])
            st.dataframe(styled, use_container_width=True)

            whatsapp_lines = []
            for i, g in enumerate(final_groups, 1):
                line = f"Fourball {i}: " + ", ".join(
                    format_player(p, display_map, teams, player_modes) for p in g
                )
                whatsapp_lines.append(line)

            st.subheader("📲 WhatsApp Text")
            st.text_area("Copy & paste to WhatsApp:", "\n".join(whatsapp_lines), height=150)
