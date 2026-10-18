"""Exact low-shell census of the 23 rooted Niemeier lattices.

The classification and theta identity are cited in SOURCES.txt. Root-lattice
norm-four counts are elementary coordinate counts; exceptional counts are
independently enumerated inside E8 here. This is a census, not a cost certificate.
"""
from itertools import combinations, product
from math import comb, isqrt, prod
from pathlib import Path
import json

ROOT_SYSTEMS = [
    ("D24", [("D", 24, 1)]),
    ("D16 E8", [("D", 16, 1), ("E", 8, 1)]),
    ("E8^3", [("E", 8, 3)]),
    ("A24", [("A", 24, 1)]),
    ("D12^2", [("D", 12, 2)]),
    ("A17 E7", [("A", 17, 1), ("E", 7, 1)]),
    ("D10 E7^2", [("D", 10, 1), ("E", 7, 2)]),
    ("A15 D9", [("A", 15, 1), ("D", 9, 1)]),
    ("D8^3", [("D", 8, 3)]),
    ("A12^2", [("A", 12, 2)]),
    ("A11 D7 E6", [("A", 11, 1), ("D", 7, 1), ("E", 6, 1)]),
    ("E6^4", [("E", 6, 4)]),
    ("A9^2 D6", [("A", 9, 2), ("D", 6, 1)]),
    ("D6^4", [("D", 6, 4)]),
    ("A8^3", [("A", 8, 3)]),
    ("A7^2 D5^2", [("A", 7, 2), ("D", 5, 2)]),
    ("A6^4", [("A", 6, 4)]),
    ("A5^4 D4", [("A", 5, 4), ("D", 4, 1)]),
    ("D4^6", [("D", 4, 6)]),
    ("A4^6", [("A", 4, 6)]),
    ("A3^8", [("A", 3, 8)]),
    ("A2^12", [("A", 2, 12)]),
    ("A1^24", [("A", 1, 24)]),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exceptional_shell_counts():
    """Enumerate x=2v in the E8 norm-two and norm-four shells."""
    shells = {2: set(), 4: set()}
    for support in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            x = [0] * 8
            for i, a in zip(support, signs):
                x[i] = a
            shells[2].add(tuple(x))
    for x in product((-1, 1), repeat=8):
        if sum(x) % 4 == 0:
            shells[2].add(x)
    for i in range(8):
        for a in (-4, 4):
            x = [0] * 8
            x[i] = a
            shells[4].add(tuple(x))
    for support in combinations(range(8), 4):
        for signs in product((-2, 2), repeat=4):
            x = [0] * 8
            for i, a in zip(support, signs):
                x[i] = a
            shells[4].add(tuple(x))
    for i in range(8):
        for signs in product((-1, 1), repeat=8):
            x = list(signs)
            x[i] *= 3
            if sum(x) % 4 == 0:
                shells[4].add(tuple(x))
    answer = {}
    for n in (6, 7, 8):
        answer[n] = {}
        for norm, shell in shells.items():
            selected = [x for x in shell if (n == 8 or sum(x) == 0)
                        and (n != 6 or x[0] + x[7] == 0)]
            require(all(sum(a * a for a in x) == 4 * norm for x in selected),
                    f"E{n} shell {norm}: every vector has the required norm")
            require(all(tuple(-a for a in x) in shell for x in selected),
                    f"E{n} shell {norm}: every antipode is present")
            answer[n][norm] = len(selected)
    require(answer == {6: {2: 72, 4: 270}, 7: {2: 126, 4: 756},
                       8: {2: 240, 4: 2160}},
            "Exact exceptional root and norm-four shell counts")
    return answer


def component_data(kind, n, exceptional):
    if kind == "A":
        h, determinant, roots = n + 1, n + 1, n * (n + 1)
        norm4 = 6 * comb(n + 1, 4)
        natural_binary_rank = n + 1 if n % 2 == 0 else n
    elif kind == "D":
        h, determinant, roots = 2 * n - 2, 4, 2 * n * (n - 1)
        norm4 = 2 * n + 16 * comb(n, 4)
        natural_binary_rank = n - 1 if n % 2 == 0 else n
    else:
        h = {6: 12, 7: 18, 8: 30}[n]
        determinant = {6: 3, 7: 2, 8: 1}[n]
        roots, norm4 = exceptional[n][2], exceptional[n][4]
        natural_binary_rank = {6: 7, 7: 7, 8: 9}[n]
    return {"type": kind, "rank": n, "coxeter_number": h,
            "determinant": determinant, "root_vectors": roots,
            "norm4_vectors": norm4,
            "natural_root_fitting_rank": natural_binary_rank}


def census():
    exceptional = exceptional_shell_counts()
    rows = []
    for name, factors in ROOT_SYSTEMS:
        components = [component_data(kind, n, exceptional)
                      for kind, n, count in factors for _ in range(count)]
        require(sum(c["rank"] for c in components) == 24,
                f"{name}: component ranks sum to 24")
        hs = {c["coxeter_number"] for c in components}
        require(len(hs) == 1, f"{name}: components share a Coxeter number")
        h = hs.pop()
        roots = sum(c["root_vectors"] for c in components)
        require(roots == 24 * h, f"{name}: root count equals 24H")
        determinant = prod(c["determinant"] for c in components)
        glue_order = isqrt(determinant)
        require(glue_order * glue_order == determinant,
                f"{name}: root determinant is a perfect square")
        root_norm4_vectors = sum(c["norm4_vectors"] for c in components)
        root_norm4_vectors += sum(a["root_vectors"] * b["root_vectors"]
                                  for a, b in combinations(components, 2))
        require(root_norm4_vectors % 2 == 0,
                f"{name}: norm-four vectors form antipodal pairs")
        shell4_lines = 98280 - 288 * h
        root_norm4_lines = root_norm4_vectors // 2
        require(0 <= root_norm4_lines <= shell4_lines,
                f"{name}: root norm-four shell is contained in the full shell")
        rows.append({"root_system": name, "coxeter_number": h,
                     "root_lines": roots // 2, "norm4_lines": shell4_lines,
                     "root_sublattice_norm4_lines": root_norm4_lines,
                     "glue_only_norm4_lines": shell4_lines - root_norm4_lines,
                     "glue_group_order": glue_order, "components": components})
    require(len(rows) == 23, "The census contains all 23 rooted systems")
    return {"scope": "Exact shell counts, not a supplier or exponent certificate",
            "norm_convention": "Squared Euclidean norm; antipodal pairs count once",
            "theta_convention": "q exponent is squared norm / 2",
            "theta_identity": "theta_L = E4^3 + (24H-720) Delta",
            "norm4_line_formula": "98280 - 288H",
            "exceptional_shell_vector_counts": exceptional, "lattices": rows}


if __name__ == "__main__":
    result = census()
    destination = Path(__file__).resolve().parents[1] / "catalog.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    for row in result["lattices"]:
        print(f'{row["root_system"]:14} H={row["coxeter_number"]:2}'
              f' roots={row["root_lines"]:3} N4={row["norm4_lines"]:5}'
              f' root-part={row["root_sublattice_norm4_lines"]:5}'
              f' glue-part={row["glue_only_norm4_lines"]:5}'
              f' glue-order={row["glue_group_order"]}')
