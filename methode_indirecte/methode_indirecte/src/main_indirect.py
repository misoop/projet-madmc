from pathlib import Path

from .data_loader import load_instance
from .dp_indirect import solve_indirect_with_items


# lance la méthode indirecte sur une instance de données
def main():
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "madmcprojet_DATA.txt"

    n_items = 30
    n_obj = 3

    print("Chargement de l'instance...")
    weights, values, capacity = load_instance(str(data_path), n_items=n_items, n_obj=n_obj)

    print("Nombre d'objets :", len(weights))
    print("Nombre d'objectifs :", len(values[0]))
    print("Capacité W :", capacity)

    print("\nMéthode indirecte (DP + filtrage Lorenz)...")
    pareto_pairs, lorenz_pairs, stats = solve_indirect_with_items(weights, values, capacity)

    print("\nSolutions Pareto non dominées (vecteur, objets) :")
    for v, it in pareto_pairs:
        print(v, "objets :", it)

    print("\nSolutions Lorenz non dominées (vecteur, objets) :")
    for v, it in lorenz_pairs:
        print(v, "objets :", it)

    print("\nStatistiques de génération :")
    print("Nombre total généré pendant DP :", stats.get("generated", "N/A"))
    print("Après filtrage Pareto :", stats.get("pareto_count", "N/A"))
    print("Après filtrage Lorenz :", stats.get("lorenz_count", "N/A"))


if __name__ == "__main__":
    main()

