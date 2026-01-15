from gurobipy import *


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
    
    # Resolution
    m.optimize()
    
    
    # Affichage des resultats
    if m.status == GRB.OPTIMAL:
        if verbose:
            print("\n=== Solution optimale P1 ===\n")

            n = len(w)
            p = len(omega)

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
            
            # Point objectif y = (sum_j v[j][i]*x[j])
            y = []
            print("Point objectif y :")
            for i in range(p):
                yi = sum(v[j][i] * x[j].x for j in range(n))
                y.append(yi)
                print(f"  y[{i}] = {yi:.4f}")
            print("")

            # Vecteur de Lorenz
            y_sorted = sorted(y)
            L = []
            cum = 0
            print("Vecteur de Lorenz L(y) :")
            for k in range(p):
                cum += y_sorted[k]
                L.append(cum)
                print(f"  L[{k}] = {cum:.4f}")
            print("")

            # Poids utilise
            total_weight = sum(w[j] * x[j].x for j in range(n))
            print(f"Poids total = {total_weight:.2f} / {W}\n")

            # Valeur de l'objectif
            print("Valeur de la fonction objectif OWA :", m.objVal)
            print("")

        return y, L

    else:
        print("\nPas de solution optimale trouvée.")
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

    n = len(w)
    p = len(omega)
    l = len(L)


    # Ajout des variables de decisions z 
    z = m.addVars(l, p, vtype=GRB.BINARY, name="z")
    """
    Traiter le cas où l = 0 ? (pas de solutions opt trouvées)
    """

    # Ajout des contraintes en plus de celles de P1
    for s in range (l):
        m.addConstr(quicksum(z[s, k] for k in range(p)) >= 1, name=f"sum_z^{s}")

        for k in range (p):
            m.addConstr((k+1)*r[k] - quicksum(b[k, i] for i in range(p)) >= (L[s][k] + 1)*z[s, k], name=f"s={s},k={k}")


    m.optimize()


    # Affichage des resultats
    if m.status == GRB.INFEASIBLE:
        print("\n PL infaisable -> fin (tout généré).")

        return None, None

    if m.status == GRB.OPTIMAL:
        if verbose:
            print("\n=== Solution optimale P1 ===\n")

            n = len(w)
            p = len(omega)

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
            
            # Point objectif y = (sum_j v[j][i]*x[j])
            y = []
            print("Point objectif y :")
            for i in range(p):
                yi = sum(v[j][i] * x[j].x for j in range(n))
                y.append(yi)
                print(f"  y[{i}] = {yi:.4f}")
            print("")

            # Vecteur de Lorenz
            y_sorted = sorted(y)
            L_new = []
            cum = 0
            print("Vecteur de Lorenz L(y) :")
            for k in range(p):
                cum += y_sorted[k]
                L_new.append(cum)
                print(f"  L[{k}] = {cum:.4f}")
            print("")

            # Poids utilise
            total_weight = sum(w[j] * x[j].x for j in range(n))
            print(f"Poids total = {total_weight:.2f} / {W}\n")

            # Valeur de l'objectif
            print("Valeur de la fonction objectif OWA :", m.objVal)
            print("")

        return y, L_new
    
    else:
        print(f"PL arrêté avec statut {m.status} (pas optimal).")
        return None, None
    

def generate_lorenz (w, v, W, omega):
    Y, Ls = [], []

    y0, L0 = solve_P1 (w, v, W, omega)

    if y0 is None:
        return Y, Ls
    
    Y.append(y0)
    Ls.append(L0)

    while True:
        y, L = solve_PL (w, v, W, omega, Ls)

        if y is None:
            break

        Y.append(y)
        Ls.append(L)

    print(f"***> Nombre de points de Lorenz non dominés : {len(Ls)}")

    return Y, Ls