from gurobipy import *


def _set_gurobi_verbosity(model: Model, verbose: bool) -> None:
    """
    Configure la verbosité Gurobi
    
    """
    # 1 = affiche, 0 = silencieux
    model.Params.OutputFlag = 1 if verbose else 0


def _to_int_list(vals, ndigits: int = 6):
    """
    Convertit une liste de valeurs Gurobi (float) en entiers stables.

    Les valuations étant entières et x binaire, y et L(y) sont entiers.

    """
    return [int(round(float(v), ndigits)) for v in vals]


def build_P1 (w, v, W, omega, name):
    """
    Construit le programme lineaire P1 
    (Pour ne pas avoir a reecrire la fonction objective et les contraintes communes a PL)

    Docstring for solve_P1

    :param w: liste de taille n (objet i de taille w_i)
    :param v: matrice de taille n x p (objet i a un vect de valuations v[i])
    :param W: capacite max
    :param omega: liste de taille p (strict. decroissante et > 0)

    """

    m = Model(name)
    
    n = len(w)
    p = len(omega)
    
    # Definition de lambda
    lamb = [omega[k] - omega[k+1] for k in range(p-1)] + [omega[-1]]

    # Variables de decision
    x = m.addVars(n, vtype=GRB.BINARY, name="x")  # Variables binaires x_i
    r = m.addVars(p, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="r")  # Variables r_k (continues dans R)
    b = m.addVars(p, p, vtype=GRB.CONTINUOUS, lb=0, name="b")  # Variables b_ik (continues, >= 0)
    
    # Contraintes
    for k in range (p):
        for i in range (p):
            m.addConstr(r[k] - b[k, i] <= quicksum(v[j][i]*x[j] for j in range (n)), name=f"rb_{k}_{i}")

    # Capacite
    m.addConstr(quicksum(w[i]*x[i] for i in range(n)) <= W, name="capacite")
     
    # Fonction objective
    obj = quicksum(lamb[k] * ((k+1)*r[k] - quicksum(b[k, i] for i in range(p))) for k in range (p))
    m.setObjective(obj, GRB.MAXIMIZE)

    return m, x, r, b


def solve_P1 (w, v, W, omega, verbose=True):
    """
    Resout P1

    Docstring for solve_P1

    :param w: liste de taille n (objet i de taille w_i)
    :param v: matrice de taille n x p (objet i a un vect de valuations v[i])
    :param W: capacite max
    :param omega: liste de taille p (strict. decroissante et > 0)

    """

    m, x, r, b = build_P1(w, v, W, omega, "P1")
    _set_gurobi_verbosity(m, verbose)
    
    # Resolution
    m.optimize()
    
    
    # Résultats
    if m.status == GRB.OPTIMAL:
        n = len(w)
        p = len(omega)

        # Point objectif y = (sum_j v[j][i]*x[j])
        y = [sum(v[j][i] * x[j].x for j in range(n)) for i in range(p)]

        # Vecteur de Lorenz L(y) (cumul des composantes triées)
        y_sorted = sorted(y)
        L = []
        cum = 0
        for k in range(p):
            cum += y_sorted[k]
            L.append(cum)

        if verbose:
            print("\n=== Solution optimale P1 ===\n")

            # Variables x (objets choisis)
            print("Variables x (objets sélectionnés) :")
            for j in range(n):
                print(f"  x[{j}] = {int(x[j].x)}")
            print("")

            # Variables r
            print("Variables r :")
            for k in range(p):
                print(f"  r[{k}] = {r[k].x:.4f}")
            print("")

            # Variables b
            print("Variables b :")
            for k in range(p):
                for i in range(p):
                    print(f"  b[{k},{i}] = {b[k,i].x:.4f}")
                print("")

            print("Point objectif y :")
            for i in range(p):
                print(f"  y[{i}] = {y[i]:.4f}")
            print("")

            print("Vecteur de Lorenz L(y) :")
            for k in range(p):
                print(f"  L[{k}] = {L[k]:.4f}")
            print("")

            # Poids utilisé
            total_weight = sum(w[j] * x[j].x for j in range(n))
            print(f"Poids total = {total_weight:.2f} / {W}\n")

            # Valeur de l'objectif
            print("Valeur de la fonction objectif OWA :", m.objVal)
            print("")

        # Retourne des entiers stables (utile pour éviter des doublons dus au flottant)
        return _to_int_list(y), _to_int_list(L)

    else:
        # Cas possibles : TIME_LIMIT, SUBOPTIMAL, UNBOUNDED, INF_OR_UNBD...
        print(f"\nPas de solution optimale trouvée (statut Gurobi = {m.status}).")
        return None, None
    



def solve_PL (w, v, W, omega, L, verbose=True):
    """
    Docstring for solve_PL
    
    :param w: liste de taille n (objet i de taille w_i)
    :param v: matrice de taille n x p (objet i a un vect de valuations v[i])
    :param W: capacite max
    :param omega: liste de taille p (strict. decroissante et > 0)
    :param L: liste de taille p des vects de Lorenz deja trouves 

    """

    m, x, r, b = build_P1(w, v, W, omega, "PL")
    _set_gurobi_verbosity(m, verbose)

    n = len(w)
    p = len(omega)
    l = len(L)

    # Cas l = 0 : aucune solution précédente -> PL équivaut à P1
    if l == 0:
        return solve_P1(w, v, W, omega, verbose=verbose)

    # Ajout des variables de decisions z
    z = m.addVars(l, p, vtype=GRB.BINARY, name="z")

    # Ajout des contraintes en plus de celles de P1
    for s in range (l):
        # Au moins une composante du vecteur de Lorenz doit être strictement améliorée
        m.addConstr(quicksum(z[s, k] for k in range(p)) >= 1, name=f"sum_z_{s}")

        for k in range (p):
            m.addConstr((k+1)*r[k] - quicksum(b[k, i] for i in range(p)) >= (L[s][k] + 1)*z[s, k], name=f"s={s},k={k}")


    m.optimize()


    # Affichage des resultats
    if m.status == GRB.INFEASIBLE:
        if verbose:
            print("\nPL infaisable -> fin (tout généré).")
        return None, None

    if m.status in (GRB.INF_OR_UNBD, GRB.UNBOUNDED):
        print(f"\nPL arrêté (statut Gurobi = {m.status}).")
        return None, None

    if m.status == GRB.OPTIMAL:
        n = len(w)
        p = len(omega)

        # Point objectif y = (sum_j v[j][i]*x[j])
        y = [sum(v[j][i] * x[j].x for j in range(n)) for i in range(p)]

        # Vecteur de Lorenz L(y)
        y_sorted = sorted(y)
        L_new = []
        cum = 0
        for k in range(p):
            cum += y_sorted[k]
            L_new.append(cum)

        if verbose:
            print("\n=== Solution optimale PL ===\n")

            # Variables x (objets choisis)
            print("Variables x (objets sélectionnés) :")
            for j in range(n):
                print(f"  x[{j}] = {int(x[j].x)}")
            print("")

            # Variables r
            print("Variables r :")
            for k in range(p):
                print(f"  r[{k}] = {r[k].x:.4f}")
            print("")

            # Variables b
            print("Variables b :")
            for k in range(p):
                for i in range(p):
                    print(f"  b[{k},{i}] = {b[k,i].x:.4f}")
                print("")

            print("Point objectif y :")
            for i in range(p):
                print(f"  y[{i}] = {y[i]:.4f}")
            print("")

            print("Vecteur de Lorenz L(y) :")
            for k in range(p):
                print(f"  L[{k}] = {L_new[k]:.4f}")
            print("")

            # Poids utilisé
            total_weight = sum(w[j] * x[j].x for j in range(n))
            print(f"Poids total = {total_weight:.2f} / {W}\n")

            # Valeur de l'objectif
            print("Valeur de la fonction objectif OWA :", m.objVal)
            print("")

        return _to_int_list(y), _to_int_list(L_new)
    
    else:
        print(f"PL arrêté avec statut {m.status} (pas optimal).")
        return None, None
    

def generate_lorenz (w, v, W, omega, verbose=True):
    Y, Ls = [], []

    y0, L0 = solve_P1 (w, v, W, omega, verbose=verbose)

    if y0 is None:
        return Y, Ls
    
    Y.append(y0)
    Ls.append(L0)

    while True:
        y, L = solve_PL (w, v, W, omega, Ls, verbose=verbose)

        if y is None:
            break

        Y.append(y)
        Ls.append(L)

    print(f"***> Nombre de points de Lorenz non dominés : {len(Ls)}")

    return Y, Ls