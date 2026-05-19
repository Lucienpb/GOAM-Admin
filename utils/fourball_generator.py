import random
from itertools import combinations
import pandas as pd


def generate_fourballs(players_list, teams, matrix, strict_mode, shuffle_seed, player_modes):
    """
    players_list: list of normalized player ids
    teams: dict[player] -> team initials
    matrix: pairing history (numeric)
    player_modes: dict[player] -> "Walking 🚶‍♂️" or "Carting 🛺"
    """
    random.seed(shuffle_seed)

    players = players_list[:]

    # ---------------------------------------------------------
    # PENALTY MATRIX
    # ---------------------------------------------------------
    penalty = pd.DataFrame(0, index=players, columns=players, dtype=int)

    def history_penalty(a, b):
        return int(matrix.loc[a, b]) * 2

    def team_penalty(a, b):
        ta = teams.get(a)
        tb = teams.get(b)
        if ta and tb and ta == tb:
            return 3
        return 0

    def cart_penalty(a, b):
        mode_a = player_modes.get(a, "Walking 🚶‍♂️")
        mode_b = player_modes.get(b, "Walking 🚶‍♂️")

        if "Carting" in mode_a and "Carting" in mode_b:
            return -3   # strong preference for carts together
        elif "Walking" in mode_a and "Walking" in mode_b:
            return 0    # neutral
        else:
            return 1    # small penalty for mixing

    for a, b in combinations(players, 2):
        p = 0
        p += history_penalty(a, b)
        p += team_penalty(a, b)
        p += cart_penalty(a, b)
        penalty.loc[a, b] = p
        penalty.loc[b, a] = p

    # ---------------------------------------------------------
    # AUTO-BALANCING: TRY 2 CARTS + 2 WALKERS
    # ---------------------------------------------------------
    carts = [p for p in players if "Carting" in player_modes.get(p, "Walking 🚶‍♂️")]
    walkers = [p for p in players if "Walking" in player_modes.get(p, "Walking 🚶‍♂️")]

    random.shuffle(carts)
    random.shuffle(walkers)

    groups = []

    # ideal groups: 2 carts + 2 walkers
    while len(carts) >= 2 and len(walkers) >= 2:
        g = [carts.pop(), carts.pop(), walkers.pop(), walkers.pop()]
        groups.append(g)

    remaining = carts + walkers
    random.shuffle(remaining)

    current = []
    for p in remaining:
        current.append(p)
        if len(current) == 4:
            groups.append(current)
            current = []
    if current:
        if strict_mode and len(current) < 3 and groups:
            for p in current:
                best_g = None
                best_cost = float("inf")
                for g in groups:
                    if len(g) >= 4:
                        continue
                    cost = 0
                    for x in g:
                        cost += penalty.loc[p, x]
                    if cost < best_cost:
                        best_cost = cost
                        best_g = g
                if best_g is not None:
                    best_g.append(p)
        else:
            groups.append(current)

    # ---------------------------------------------------------
    # LOCAL IMPROVEMENT
    # ---------------------------------------------------------
    def group_cost(g):
        c = 0
        for a, b in combinations(g, 2):
            c += penalty.loc[a, b]
        return c

    improved = True
    iters = 0
    max_iters = 200

    while improved and iters < max_iters:
        improved = False
        iters += 1

        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                g1 = groups[i]
                g2 = groups[j]
                for a in g1:
                    for b in g2:
                        new_g1 = [x for x in g1 if x != a] + [b]
                        new_g2 = [x for x in g2 if x != b] + [a]

                        if strict_mode and (len(new_g1) < 3 or len(new_g2) < 3):
                            continue

                        old_cost = group_cost(g1) + group_cost(g2)
                        new_cost = group_cost(new_g1) + group_cost(new_g2)

                        if new_cost < old_cost:
                            groups[i] = new_g1
                            groups[j] = new_g2
                            improved = True

    final_groups = [list(g) for g in groups]

    return final_groups, penalty
