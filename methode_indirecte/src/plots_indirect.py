from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # nécessaire pour le scatter 3D

from .data_loader import load_instance
from .dp_indirect import dp_knapsack_multiobjective
from .dominance import filter_lorenz


# affiche un nuage de points selon le nombre d'objectifs
def plot_points(points, title_prefix):
    if not points:
        print("Aucun point pour", title_prefix)
        return

    p = len(points[0])

    # Cas 2 objectifs : simple graphe 2D
    if p == 2:
        xs = [v[0] for v in points]
        ys = [v[1] for v in points]

        plt.figure()
        plt.scatter(xs, ys)
        plt.xlabel("Objectif 1")
        plt.ylabel("Objectif 2")
        plt.title(title_prefix)
        plt.grid(True)
        plt.show()

    # Cas 3 objectifs : graphe 3D
    elif p == 3:
        xs = [v[0] for v in points]
        ys = [v[1] for v in points]
        zs = [v[2] for v in points]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(xs, ys, zs)
        ax.set_xlabel("Objectif 1")
        ax.set_ylabel("Objectif 2")
        ax.set_zlabel("Objectif 3")
        ax.set_title(title_prefix)
        plt.show()

    # Cas 4, 5, 6 objectifs : toutes les projections 2D
    else:
        p = len(points[0])
        for i in range(p):
            for j in range(i + 1, p):
                xs = [v[i] for v in points]
                ys = [v[j] for v in points]

                plt.figure()
                plt.scatter(xs, ys)
                plt.xlabel(f"Objectif {i+1}")
                plt.ylabel(f"Objectif {j+1}")
                plt.title(f"{title_prefix} (obj {i+1} vs obj {j+1})")
                plt.grid(True)
                plt.show()


# génère les graphes pour : toutes les solutions, Pareto, Lorenz
def main():
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "madmcprojet_DATA.txt"

    # paramètres de l'instance (modifiable)
    n_items = 20
    n_obj = 3   

    print("Chargement de l'instance pour les graphes...")
    weights, values, capacity = load_instance(str(data_path), n_items=n_items, n_obj=n_obj)
    print("Nombre d'objets :", len(weights))
    print("Nombre d'objectifs :", len(values[0]))
    print("Capacité W :", capacity)

    # DP pour récupérer tous les points
    stats = {}
    pareto_points = dp_knapsack_multiobjective(weights, values, capacity, stats)
    all_points = stats.get("all_points", [])

    # filtrage Lorenz
    lorenz_points = filter_lorenz(pareto_points)

    print("Nombre total de points candidats :", len(all_points))
    print("Pareto-non dominés :", len(pareto_points))
    print("Lorenz-non dominés :", len(lorenz_points))

    # Graphes
    plot_points(all_points, "Toutes les solutions candidates (DP)")
    plot_points(pareto_points, "Points Pareto non dominés")
    plot_points(lorenz_points, "Points Lorenz non dominés")


if __name__ == "__main__":
    main()
