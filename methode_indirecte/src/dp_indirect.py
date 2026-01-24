from .dominance import filter_pareto, filter_lorenz

# DP pour le sac à dos multi-objectifs (vecteurs seulement)
def dp_knapsack_multiobjective(weights, values, capacity, stats=None):
    n = len(weights)
    if n == 0:
        return []

    p = len(values[0])

    if stats is not None:
        stats["generated"] = 0
        stats["all_points"] = []

    # DP[w] = liste de vecteurs non dominés pour un poids total w
    DP = [[] for _ in range(capacity + 1)]
    DP[0] = [tuple(0 for _ in range(p))]

    for j in range(n):
        wj = weights[j]
        vj = values[j]

        new_DP = [list(vecs) for vecs in DP]

        for w in range(capacity + 1):
            if w >= wj:
                for vect in DP[w - wj]:
                    if stats is not None:
                        stats["generated"] += 1
                    candidate = tuple(vect[i] + vj[i] for i in range(p))
                    new_DP[w].append(candidate)

        for w in range(capacity + 1):
            if new_DP[w]:
                new_DP[w] = filter_pareto(new_DP[w])

        DP = new_DP

    all_points = []
    for w in range(capacity + 1):
        all_points.extend(DP[w])

    if stats is not None:
        stats["all_points"] = list(all_points)

    pareto_points = filter_pareto(all_points)
    return pareto_points


# méthode indirecte classique (sans garder les objets)
def solve_indirect(weights, values, capacity):
    stats = {}
    pareto_points = dp_knapsack_multiobjective(weights, values, capacity, stats)
    stats["pareto_count"] = len(pareto_points)

    lorenz_points = filter_lorenz(pareto_points)
    stats["lorenz_count"] = len(lorenz_points)

    return pareto_points, lorenz_points, stats


# DP qui garde les objets utilisés pour chaque solution
def dp_with_items(weights, values, capacity, stats=None):
    n = len(weights)
    if n == 0:
        return []

    p = len(values[0])

    if stats is not None:
        stats["generated"] = 0

    # DP[w] = liste de (vecteur, objets_pris)
    DP = [[] for _ in range(capacity + 1)]
    DP[0] = [(tuple(0 for _ in range(p)), tuple())]

    for j in range(n):
        wj = weights[j]
        vj = values[j]

        new_DP = [list(lst) for lst in DP]

        for w in range(capacity + 1):
            if w >= wj:
                for vect, items in DP[w - wj]:
                    if stats is not None:
                        stats["generated"] += 1
                    new_vect = tuple(vect[i] + vj[i] for i in range(p))
                    new_items = items + (j,)
                    new_DP[w].append((new_vect, new_items))

        for w in range(capacity + 1):
            if new_DP[w]:
                only_vectors = [v for (v, it) in new_DP[w]]
                pareto_vectors = filter_pareto(only_vectors)

                filtered = []
                for v, it in new_DP[w]:
                    if v in pareto_vectors and (v, it) not in filtered:
                        filtered.append((v, it))
                new_DP[w] = filtered

        DP = new_DP

    all_pairs = []
    for w in range(capacity + 1):
        all_pairs.extend(DP[w])

    all_vectors = [v for (v, it) in all_pairs]
    pareto_vectors = filter_pareto(all_vectors)

    pareto_pairs = []
    for v, it in all_pairs:
        if v in pareto_vectors and (v, it) not in pareto_pairs:
            pareto_pairs.append((v, it))

    return pareto_pairs


# méthode indirecte avec items (vecteur + liste d'objets) + stats
def solve_indirect_with_items(weights, values, capacity):
    stats = {}
    pareto_pairs = dp_with_items(weights, values, capacity, stats)

    pareto_vectors = [v for (v, it) in pareto_pairs]
    stats["pareto_count"] = len(pareto_vectors)

    lorenz_vectors = filter_lorenz(pareto_vectors)

    lorenz_pairs = []
    for v, it in pareto_pairs:
        if v in lorenz_vectors and (v, it) not in lorenz_pairs:
            lorenz_pairs.append((v, it))

    stats["lorenz_count"] = len(lorenz_pairs)

    return pareto_pairs, lorenz_pairs, stats
