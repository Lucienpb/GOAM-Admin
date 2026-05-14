"""
Fourball Generator Module - Generates optimal fourballs
"""
import random
from itertools import combinations

# ================================================================================
# FOURBALL GENERATION
# ================================================================================
def attempt_grouping(players, teams, penalty, seed):
    """Attempt to create fourballs with given seed"""
    random.seed(seed)
    shuffled = players[:]
    random.shuffle(shuffled)

    sorted_players = sorted(shuffled, key=lambda p: sum(penalty[p].values()), reverse=True)

    groups = []
    used = set()

    for p in sorted_players:
        if p in used:
            continue

        group = [p]
        used.add(p)

        for q in sorted_players:
            if q in used:
                continue
            if teams[q] in [teams[x] for x in group]:
                continue
            if any(penalty[q][x] > 0 for x in group):
                continue

            group.append(q)
            used.add(q)
            if len(group) == 4:
                break

        groups.append(group)

    return groups

def generate_fourballs(players, teams, matrix, strict_mode=True, shuffle_seed=0):
    """Generate optimal fourballs from player list and matrix"""
    # Build pairing penalty from matrix
    penalty = {}
    for a in players:
        penalty[a] = {}
        for b in players:
            if a == b:
                penalty[a][b] = 999
            else:
                if (a in matrix.index) and (b in matrix.columns):
                    val = matrix.loc[a, b]
                else:
                    val = ""
                penalty[a][b] = int(val) if val not in ["", "-", None] else 0

    # Try up to 50 attempts if strict mode is ON
    attempts = 50 if strict_mode else 1
    final_groups = None

    for i in range(attempts):
        groups = attempt_grouping(players, teams, penalty, shuffle_seed + i)

        # Check if any group is < 3
        if strict_mode:
            if all(len(g) >= 3 for g in groups):
                final_groups = groups
                break
        else:
            final_groups = groups
            break

    # If strict mode failed, force merge
    if final_groups is None:
        groups = attempt_grouping(players, teams, penalty, shuffle_seed)
        flat = [p for g in groups for p in g]
        final_groups = [flat[i:i+4] for i in range(0, len(flat), 4)]
        if len(final_groups[-1]) == 1:
            final_groups[-2].append(final_groups[-1][0])
            final_groups = final_groups[:-1]
        if len(final_groups[-1]) == 2:
            final_groups[-2].extend(final_groups[-1])
            final_groups = final_groups[:-1]

    return final_groups, penalty

def get_initials(team_name):
    """Extract initials from team name (e.g., 'Fairway Fighters' -> 'FF')"""
    return ''.join([word[0].upper() for word in team_name.split()])

def format_player(name, teams):
    """Format player name with team initials"""
    return f"{name} ({get_initials(teams[name])})"
