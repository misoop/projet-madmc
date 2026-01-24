from pathlib import Path
import time
import signal

from .data_loader import load_instance
from .dp_indirect import solve_indirect


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException


# on lance une série de tests pour différents n_items et n_obj
def run_experiments():
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "madmcprojet_DATA.txt"

    # ici on contrôle les valeurs que on veut tester
    n_items_list = [10, 15,20]
    n_obj_list = [6]

    timeout_sec = 90 * 60  # 90 minutes

    header = f"{'n_items':>7} {'n_obj':>6} {'generated':>10} {'pareto':>8} {'lorenz':>8} {'time_sec':>10}"
    print(header)
    print("-" * len(header))

    signal.signal(signal.SIGALRM, timeout_handler)

    for n_obj in n_obj_list:
        for n_items in n_items_list:
            weights, values, capacity = load_instance(str(data_path), n_items=n_items, n_obj=n_obj)

            try:
                signal.alarm(timeout_sec)

                t0 = time.perf_counter()
                pareto_points, lorenz_points, stats = solve_indirect(weights, values, capacity)
                t1 = time.perf_counter()

                signal.alarm(0)

                elapsed = t1 - t0
                generated = stats.get("generated", 0)
                pareto_count = stats.get("pareto_count", len(pareto_points))
                lorenz_count = stats.get("lorenz_count", len(lorenz_points))

                print(f"{n_items:7d} {n_obj:6d} {generated:10d} {pareto_count:8d} {lorenz_count:8d} {elapsed:10.4f}")

            except TimeoutException:
                signal.alarm(0)
                print(f"{n_items:7d} {n_obj:6d} {'TIMEOUT':>10} {'-':>8} {'-':>8} {('>%dmin' % (timeout_sec // 60)):>10}")

            finally:
                signal.alarm(0)


if __name__ == "__main__":
    run_experiments()
