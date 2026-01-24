from math import floor

# lit une instance dans le fichier texte
def load_instance(path, n_items=None, n_obj=None):
    weights = []
    values = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("c"):
                continue
            if line.startswith("n"):
                # on ignore cette ligne
                continue
            if line.startswith("i"):
                parts = line.split()
                nums = list(map(int, parts[1:]))  # [w, v1, v2, ...]
                if len(nums) < 2:
                    continue
                w = nums[0]
                v_list = nums[1:]

                if n_obj is not None:
                    v_list = v_list[:n_obj]

                weights.append(w)
                values.append(tuple(v_list))

    if n_items is not None:
        weights = weights[:n_items]
        values = values[:n_items]

    if len(weights) == 0:
        raise ValueError("Aucun objet chargé depuis le fichier " + path)

    total_weight = sum(weights)
    capacity = floor(total_weight / 2)

    return weights, values, capacity
