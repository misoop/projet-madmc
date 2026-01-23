from __future__ import annotations

import argparse
import csv
import time
import signal
from pathlib import Path
from typing import List, Dict

from fonctions import generate_lorenz
from methode_directe.codes.experiments_direct_omega import load_dat, sub_instance, compute_W


TIMEOUT_SECONDS = 20 * 60  # 20 minutes


class TimeoutException(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException


signal.signal(signal.SIGALRM, _timeout_handler)


# Omega linéaire
def omega_linear(p: int) -> List[int]:
    if p <= 0:
        raise ValueError("p doit être > 0")
    
    return list(range(p, 0, -1))


# Tests sur en fixant p, et faisant varier n
def run_scalability(data_path, p, verbose):
    inst_full = load_dat(data_path)

    n_values = [20, 40, 60] # PEUT ETRE MODIFIE
    if max(n_values) > len(inst_full.w):
        raise ValueError(
            f"Le fichier ne contient que {len(inst_full.w)} objets, impossible d'aller jusqu'à n=100."
        )

    omega = omega_linear(p)
    rows: List[Dict] = []

    for n in n_values:
        inst = sub_instance(inst_full, n, p)
        W = compute_W(inst.w)

        print(f"\n=== Scalabilité | n={n}, p={p} | W={W} | omega=linéaire ===")

        signal.alarm(TIMEOUT_SECONDS)
        t0 = time.perf_counter()

        try:
            Y, Ls = generate_lorenz(inst.w, inst.v, W, omega, verbose=verbose)
            elapsed = time.perf_counter() - t0
            nb_lorenz = -1 if Ls is None else len(Ls)

            print(f"time = {elapsed:.2f} s | nb_lorenz = {nb_lorenz}")

            rows.append(
                {
                    "n": n,
                    "p": p,
                    "nb_lorenz": nb_lorenz,
                    "time": f"{elapsed:.6f}",
                }
            )

        except TimeoutException:
            elapsed = time.perf_counter() - t0
            print(f"TIMEOUT atteint ({TIMEOUT_SECONDS}s) pour n={n}")

            rows.append(
                {
                    "n": n,
                    "p": p,
                    "nb_lorenz": "timeout",
                    "time": f">{TIMEOUT_SECONDS}",
                }
            )

        finally:
            signal.alarm(0)  # désactive l’alarme

    return rows


# CSV
def write_csv(rows: List[Dict], out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["n", "p", "nb_lorenz", "time"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV écrit : {out_path.resolve()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Chemin vers le fichier .dat")
    ap.add_argument("--p", type=int, required=True, help="Nombre d'objectifs (p)")
    ap.add_argument("--verbose", action="store_true", help="Affiche les logs Gurobi")
    ap.add_argument("--out", default=None, help="Chemin CSV de sortie")
    args = ap.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(data_path)

    rows = run_scalability(data_path=data_path, p=args.p, verbose=args.verbose)

    out_path = Path(args.out) if args.out else Path(f"results/scalability_linear_p{args.p}.csv")
    write_csv(rows, out_path)


if __name__ == "__main__":
    main()
