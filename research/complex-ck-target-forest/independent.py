import gzip
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def primitive_price(a, b):
    if a == 0:
        return 0
    common = math.gcd(abs(a), b)
    a, b = abs(a) // common, b // common
    price = 3
    while a:
        price += a % 2
        a //= 2
        if a:
            price += 1
    while b > 1:
        require(b % 2 == 0, "non-dyadic coefficient")
        b //= 2
        price += 1
    return price


def prim(weights):
    reached = {0}
    best = weights[0].copy()
    cost = 0
    while len(reached) < len(weights):
        vertex = min((v for v in range(len(weights)) if v not in reached), key=lambda v: (best[v], v))
        cost += best[vertex]
        reached.add(vertex)
        for v in range(len(weights)):
            if v not in reached:
                best[v] = min(best[v], weights[vertex][v])
    return cost


def panel_column(gates, column, backward):
    state = [0] * 716
    state[column] = 4
    for op, t, s, a, b, frame in gates:
        require(op == "add" and frame == 0 and t != s, "panel syntax")
        if backward:
            t, s, a = s, t, -a
        value, remainder = divmod(a * state[s], b)
        require(remainder == 0, "nonintegral quarter-grid prefix")
        state[t] += value
    return state


def main():
    manifest = read(HERE / "SOURCES.json")
    for name, pin in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        if pin["encoding"] == "gzip-payload":
            data = gzip.decompress(data)
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin mismatch")
    word = read(ROOT / PROVIDER / "CANONICAL-WORD.json.gz")
    recipe = read(HERE / "RECIPE.json")
    expected = read(HERE / "EXPECTED.json")
    encoded = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    require(hashlib.sha256(encoded).hexdigest() == expected["recipe_sha256"], "recipe digest")
    sources = sorted({g[2] for g in word["compensation"]})
    source_index = {r: i for i, r in enumerate(sources)}
    matrix = [[0] * len(sources) for _ in range(112)]
    for op, target, source, a, b, frame in word["compensation"]:
        require(op == "add" and 112 <= target < 224 and frame == 0 and 4 * a % b == 0, "input matrix")
        matrix[target - 112][source_index[source]] += 4 * a // b
    require(not set(sources) & set(range(112, 224)), "source/target overlap")
    weights = [[0] * 113 for _ in range(113)]
    signed_prices = {}
    for i, row in enumerate(matrix, 1):
        weights[0][i] = weights[i][0] = sum(primitive_price(x, 4) for x in row)
        for j in range(1, i):
            prices = {}
            for sign in (-1, 1):
                prices[sign] = 8 + sum(primitive_price(x - sign * y, 4) for x, y in zip(row, matrix[j - 1]))
                signed_prices[j + 111, i + 111, sign] = prices[sign]
            weights[i][j] = weights[j][i] = min(prices.values())
    floor = prim(weights)
    require(floor == expected["forest_class_complex_primitive_floor"], "independent Prim floor")
    chosen_cost = 0
    adjacency = {v: [] for v in [-1, *range(112, 224)]}
    require(len(recipe["tree_edges"]) == 112, "tree edge count")
    for cost, a, b, sign in recipe["tree_edges"]:
        require(a in adjacency and b in adjacency and a < b, "tree vertex/order")
        require(sign == 0 if a == -1 else sign in (-1, 1), "tree edge sign")
        price = weights[0][b - 111] if a == -1 else signed_prices[a, b, sign]
        require(price == cost, "selected edge weight")
        chosen_cost += price
        adjacency[a].append(b)
        adjacency[b].append(a)
    reached = {-1}
    stack = [-1]
    while stack:
        for child in adjacency[stack.pop()]:
            if child not in reached:
                reached.add(child)
                stack.append(child)
    require(reached == set(adjacency), "tree disconnected")
    require(chosen_cost == floor, "chosen forest cost")
    panel = recipe["compensation"]
    require(sum(primitive_price(g[3], g[4]) for g in panel) == floor, "independent literal circuit bill")
    active = sorted(set(sources) | set(range(112, 224)))
    require(all(g[1] in active and g[2] in active for g in panel), "changed inactive register")
    for backward in (False, True):
        for column in active:
            wanted = [0] * 716
            wanted[column] = 4
            if backward and 112 <= column < 224:
                for source, value in zip(sources, matrix[column - 112]):
                    wanted[source] -= value
            elif not backward and column in source_index:
                for t, row in enumerate(matrix, 112):
                    wanted[t] += row[source_index[column]]
            require(panel_column(panel, column, backward) == wanted, f"column mismatch: {backward}, {column}")
    require(expected["compensation_after"] == len(panel), "recipe length")
    for name, table in expected["scalar_bills"].items():
        original = sum(primitive_price(g[3], g[4]) for g in word["compensation"])
        require(table["real_saved"] == 2 * (original - floor), f"independent saving: {name}")
    toy = [[0, 5, 6, 10], [5, 0, 1, 9], [6, 1, 0, 2], [10, 9, 2, 0]]
    require(prim(toy) == 8, "Prim positive control")
    changed = [row.copy() for row in toy]
    changed[2][3] = changed[3][2] = 20
    require(prim(changed) == 15, "Prim edge-price control")
    print(f"PASS_CK_FOREST_INDEPENDENT floor={floor} active_columns={len(active)} "
          f"untouched_columns={716 - len(active)} orientations=2")


if __name__ == "__main__":
    main()
