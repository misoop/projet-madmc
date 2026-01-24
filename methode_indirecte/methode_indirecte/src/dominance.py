# fonctions liées à la dominance Pareto et Lorenz

def pareto_dominates(u, v):
    # renvoie True si u Pareto-domine v (maximisation)
    ge_all = True
    gt_one = False
    for i in range(len(u)):
        if u[i] < v[i]:
            ge_all = False
            break
        if u[i] > v[i]:
            gt_one = True
    return ge_all and gt_one


def filter_pareto(points):
    # enlève les points Pareto-dominés d'une liste
    pts = list(points)
    nondominated = []

    for p in pts:
        dominated = False
        for q in pts:
            if q is p:
                continue
            if pareto_dominates(q, p):
                dominated = True
                break
        if not dominated:
            nondominated.append(p)

    # enlever les doublons
    unique = []
    seen = set()
    for p in nondominated:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


def lorenz_vector(y):
    # calcule le vecteur de Lorenz L(y)
    sorted_y = sorted(y)  # ordre croissant
    cumul = []
    s = 0
    for val in sorted_y:
        s += val
        cumul.append(s)
    return tuple(cumul)


def lorenz_dominates(u, v):
    # renvoie True si u Lorenz-domine v
    Lu = lorenz_vector(u)
    Lv = lorenz_vector(v)
    return pareto_dominates(Lu, Lv)


def filter_lorenz(points):
    # enlève les points Lorenz-dominés d'une liste
    pts = list(points)
    lorenz_map = {p: lorenz_vector(p) for p in pts}
    nondominated = []

    for p in pts:
        Lp = lorenz_map[p]
        dominated = False
        for q in pts:
            if q is p:
                continue
            Lq = lorenz_map[q]
            if pareto_dominates(Lq, Lp):
                dominated = True
                break
        if not dominated:
            nondominated.append(p)

    # enlever les doublons
    unique = []
    seen = set()
    for p in nondominated:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique
