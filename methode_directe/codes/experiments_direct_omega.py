from __future__ import annotations
import argparse
import csv
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import matplotlib.pyplot as plt

from fonctions import generate_lorenz


@dataclass
class Instance:
    w: List[int]
    v: List[List[int]]  # n * p


def load_dat(path):
    """Parse le format 'c/n/i' de 2KP200-TA-0.dat.

    Retour :
      - w : liste des poids (taille n_items)
      - v : liste de lignes [v1..vp] (taille n_items)
    """

    w = []
    v = []
    p_total: int | None = None

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # commentaires
            if line.startswith("c"):
                continue

            parts = line.split()
            tag = parts[0]

            if tag == "n":
                # 'n 1' -> identifiant, pas le nombre d'objets
                continue

            if tag != "i":
                # inconnu : on ignore
                continue

            # format attendu : i weight v1 v2 ... vp
            try:
                nums = list(map(int, parts[1:]))
            except ValueError:
                continue

            if len(nums) < 2:
                continue

            wi = nums[0]
            vals = nums[1:]

            if p_total is None:
                p_total = len(vals)
            else:
                if len(vals) != p_total:
                    raise ValueError(
                        f"Nombre d'objectifs incohérent : attendu {p_total}, obtenu {len(vals)} sur la ligne: {line}"
                    )

            w.append(wi)
            v.append(vals)

    if not w or not v:
        raise ValueError(f"Aucune donnée 'i ...' parsée dans {path}")

    return Instance(w=w, v=v)


def sub_instance(inst, n, p):

    if n <= 0:
        raise ValueError("n doit être > 0")
    
    if p <= 0:
        raise ValueError("p doit être > 0")
    
    if n > len(inst.w):
        raise ValueError(f"n demandé ({n}) > n disponible ({len(inst.w)})")
    
    if p > len(inst.v[0]):
        raise ValueError(f"p demandé ({p}) > p disponible ({len(inst.v[0])})")

    w = inst.w[:n]
    v = [row[:p] for row in inst.v[:n]]

    return Instance(w=w, v=v)


def compute_W(w):

    return int(math.floor(sum(w) / 2))


def omega_families(p):
    """Familles d'omegas valides : strictement décroissantes et >0."""

    # Linéaire : p, p-1, ..., 1
    lin = list(range(p, 0, -1))

    # Géométrique : 2^(p-1), ..., 1
    geo = [2 ** (p - 1 - k) for k in range(p)]

    # Normalisé
    den = p * (p + 1) / 2
    norm = [round((p - k) / den, 3) for k in range(p)]

    if p == 2: # car lin = geo
        return [("linear", lin), ("normalized", norm)]

    return [("linear", lin), ("geometric", geo), ("normalized", norm)]


def random_omega(p, rng):
    """Omega strictement décroissant, entiers uniformes dans [1, 1000]."""
    
    return sorted(rng.sample(range(1, 1001), p), reverse=True)


def run_direct(inst, omega, verbose):

    W = compute_W(inst.w)
    t0 = time.perf_counter()
    Y, Ls = generate_lorenz(inst.w, inst.v, W, omega, verbose=verbose)
    t1 = time.perf_counter()

    # print("* * * Lorenz non dom :", Ls)

    """
    # --- Plot obj1 vs obj2 ---
    if len(Y) > 0 and len(Y[0])==2:
        obj1 = [y[0] for y in Y]
        obj2 = [y[1] for y in Y]

        plt.figure()
        plt.scatter(obj1, obj2)
        plt.xlabel("Objectif 1")
        plt.ylabel("Objectif 2")
        plt.title(f"Méthode directe avec omega = {omega}")
        plt.grid(True)
        plt.show()
    """

    return {
        "W": W,
        "omega": omega,
        "nb_points_lorenz": len(Ls),
        "time_s": (t1 - t0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Chemin vers le fichier .dat")
    ap.add_argument("--n", type=int, required=True, help="Nombre d'objets (prendre les n premiers)")
    ap.add_argument("--p", type=int, required=True, help="Nombre d'objectifs (prendre les p premiers)")
    ap.add_argument("--seed", type=int, default=0, help="Seed RNG pour omegas aléatoires")
    ap.add_argument(
        "--random-omega",
        type=int,
        default=0,
        help="Nombre d'omegas aléatoires en plus des familles de base",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche le detail des solutions.",
    )

    args = ap.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(data_path)

    inst_full = load_dat(data_path)
    inst = sub_instance(inst_full, args.n, args.p)

    W = compute_W(inst.w)
    print(f"Instance: file={data_path.name} | n={args.n}, p={args.p} | W=floor(sum(w)/2)={W}")

    omegas = omega_families(args.p)
    rng = random.Random(args.seed)
    for i in range(args.random_omega):
        omegas.append((f"random_{i+1}", random_omega(args.p, rng)))

    rows = []
    for tag, omega in omegas:
        print(f"\n--- Méthode directe | omega={tag}: {omega} ---")
        res = run_direct(inst, omega, verbose=args.verbose)
        print(f"nb vecteurs Lorenz = {res['nb_points_lorenz']} | time = {res['time_s']:.4f} s")

        rows.append(
            {
                "data": str(data_path),
                "n": args.n,
                "p": args.p,
                "W": res["W"],
                "omega_tag": tag,
                "omega": " ".join(map(str, res["omega"])),
                "nb_points_lorenz": res["nb_points_lorenz"],
                "time_s": f"{res['time_s']:.6f}",
            }
        )

    out_path = Path(f"results/results_direct_n{args.n}p{args.p}.csv")
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "data",
                "n",
                "p",
                "W",
                "omega_tag",
                "omega",
                "nb_points_lorenz",
                "time_s",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV écrit: {out_path.resolve()}")


if __name__ == "__main__":
    main()
