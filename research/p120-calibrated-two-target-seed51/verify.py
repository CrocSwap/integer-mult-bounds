#!/usr/bin/env python3
"""Exact finite replay for the seed-51 calibrated two-target E8 decoder audit."""
from fractions import Fraction
from pathlib import Path


def require(ok, message):
    if not ok:
        raise AssertionError(message)


ROOT = Path(__file__).resolve().parent
CERT_LINES = (ROOT / "certificate.tsv").read_text().splitlines()
require(CERT_LINES[:3] == ["# schema=1",
                            "#! seed=51 track=structural-decoder ports=P120 e_index=51 d0_index=1",
                            "#! columns=index root8_csv label9_bits"], "certificate header changed")
L, U = [], []
for expected, line in enumerate(CERT_LINES[3:]):
    index, root, label = line.split("\t")
    require(int(index) == expected and len(label) == 9 and set(label) <= {"0", "1"},
            "malformed root/label certificate row")
    L.append([int(x) for x in root.split(",")])
    U.append(int(label, 2))
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def dot2(a, b):
    return (a & b).bit_count() & 1


require(len(L) == len(U) == 120 and all(len(row) == 8 for row in L), "bad E8 dimensions")
require(all(0 <= u < 512 for u in U), "label outside F_2^9")
G = [[dot(a, b) // 2 for b in L] for a in L]
require(all(dot(a, a) == 4 for a in L), "root-line norm changed")
require(all(dot(a, b) % 2 == 0 for a in L for b in L), "nonintegral half-Gram entry")
require(all(G[i][i] == 2 for i in range(120)), "bad Gram diagonal")
require(all(G[i][j] in (-1, 0, 1) for i in range(120) for j in range(120) if i != j),
        "bad E8 off-diagonal Gram entry")
require(all(dot2(U[i], U[j]) == ((1 + G[i][j]) & 1)
            for i in range(120) for j in range(120)), "labels do not factor (J+G) mod 2")


def enumerate_calibrated_nodes(ports, e_index, d_index):
    e, d = L[e_index], L[d_index]
    pe, pd = {s: dot(L[s], e) for s in ports}, {s: dot(L[s], d) for s in ports}
    nodes = []
    counts = {"sink_label_rows": 0, "consistent_calibration_rows": 0,
              "calibrated_rows": 0, "nonzero_diagonal_rows": 0}
    for t in ports:
        for w in range(1, 512):
            Z = {s for s in ports if dot2(w, U[s])}
            if t not in Z or w == U[t]:
                continue
            counts["sink_label_rows"] += 1
            mu_values = {
                Fraction(-pd[s], pe[s])
                for s in ports if s != t and s in Z and pe[s] != 0
            }
            if len(mu_values) > 1:
                continue
            counts["consistent_calibration_rows"] += 1
            if not mu_values:
                continue
            counts["calibrated_rows"] += 1
            mu = next(iter(mu_values))
            if pd[t] + mu * pe[t] == 0:
                continue
            counts["nonzero_diagonal_rows"] += 1
            E = {
                s for s in ports
                if s != t and s in Z and pe[s] == 0 and pd[s] != 0
            }
            nodes.append({"t": t, "w": w, "mu": mu, "E": E, "Z": Z})
    return nodes, counts, pe, pd


def relaxed_row_exact(t, mu, E_total, Z, ports, pe, pd):
    """Check the exact rational row against the sink's bit support."""
    for s in ports:
        n = Fraction(pd[s]) + mu * pe[s] - (pd[s] if s in E_total else 0)
        if s == t:
            if s not in Z or n == 0:
                return False
        elif n != 0 and s in Z:
            return False
    return True


def first_exact_pair(ports, e_index, d_index):
    nodes, _, pe, pd = enumerate_calibrated_nodes(ports, e_index, d_index)
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if a["t"] == b["t"]:
                continue
            total = a["E"] | b["E"]
            if not a["E"] <= b["Z"] or not b["E"] <= a["Z"]:
                continue
            if a["t"] in b["E"] or b["t"] in a["E"]:
                continue
            if not relaxed_row_exact(a["t"], a["mu"], total, a["Z"], ports, pe, pd):
                continue
            if not relaxed_row_exact(b["t"], b["mu"], total, b["Z"], ports, pe, pd):
                continue
            return a, b, total, nodes, pe, pd
    return None, None, None, nodes, pe, pd


def full_unit_exact(ports, a, b, total):
    """Check every entry of the P112/P120 unit, including untouched baseline rows."""
    e, d = L[0], L[76]
    pe, pd = {s: dot(L[s], e) for s in ports}, {s: dot(L[s], d) for s in ports}
    sinks = {s: U[s] for s in ports}
    sinks[a["t"]], sinks[b["t"]] = a["w"], b["w"]
    for t in ports:
        for s in ports:
            if t == a["t"]:
                n = Fraction(pd[s]) + a["mu"] * pe[s] - (pd[s] if s in total else 0)
            elif t == b["t"]:
                n = Fraction(pd[s]) + b["mu"] * pe[s] - (pd[s] if s in total else 0)
            else:
                n = Fraction(G[t][s], 2)
            pairing = dot2(sinks[t], U[s])
            if t == s:
                if not pairing or n == 0:
                    return False
            elif n != 0 and pairing:
                return False
    return True


e_index, d_index = 51, 1
odd_partners = [s for s in range(120) if s != e_index and G[e_index][s] != 0]
require(len(odd_partners) == 56 and odd_partners[0] == d_index,
        "seed-selected first odd partner is not reproduced")

all_ports = list(range(120))
nodes, row_counts, pe, pd = enumerate_calibrated_nodes(all_ports, e_index, d_index)
raw_pairs = available_pairs = target_contaminated = exact_pairs = 0
one_cross, two_cross = 0, 0
for i, a in enumerate(nodes):
    for b in nodes[i + 1:]:
        if a["t"] == b["t"]:
            continue
        raw_pairs += 1
        if not a["E"] <= b["Z"] or not b["E"] <= a["Z"]:
            continue
        available_pairs += 1
        a_cross, b_cross = a["t"] in b["E"], b["t"] in a["E"]
        require(a_cross or b_cross, "found a shared-total pair without target contamination")
        target_contaminated += 1
        one_cross += (a_cross != b_cross)
        two_cross += (a_cross and b_cross)
        if a_cross:
            require(pe[a["t"]] == 0 and pd[a["t"]] != 0,
                    "cross-target source does not force a zero diagonal")
            diagonal_a = Fraction(pd[a["t"]]) + a["mu"] * pe[a["t"]] - pd[a["t"]]
            require(diagonal_a == 0, "cross-target diagonal obstruction failed")
        if b_cross:
            require(pe[b["t"]] == 0 and pd[b["t"]] != 0,
                    "cross-target source does not force a zero diagonal")
            diagonal_b = Fraction(pd[b["t"]]) + b["mu"] * pe[b["t"]] - pd[b["t"]]
            require(diagonal_b == 0, "cross-target diagonal obstruction failed")
        exact_a = relaxed_row_exact(a["t"], a["mu"], a["E"] | b["E"], a["Z"], all_ports, pe, pd)
        exact_b = relaxed_row_exact(b["t"], b["mu"], a["E"] | b["E"], b["Z"], all_ports, pe, pd)
        exact_pairs += bool(exact_a and exact_b)

require(row_counts == {"sink_label_rows": 30600, "consistent_calibration_rows": 63,
                       "calibrated_rows": 63, "nonzero_diagonal_rows": 27},
        f"P120 row census changed: {row_counts}")
require(len(nodes) == 27 and raw_pairs == available_pairs == target_contaminated == 351,
        "P120 candidate-pair census changed")
require(one_cross + two_cross == 351 and exact_pairs == 0,
        "P120 shared-total diagonal obstruction count changed")

# Positive control: replay the published P112 C.6 two-target witness through the
# same calibrated-node and pair predicates.
p112 = list(range(8, 120))
a, b, total, p112_nodes, pe112, pd112 = first_exact_pair(p112, 0, 76)
require(a is not None and b is not None, "P112 C.6 positive control was not found")
got = (a["t"], a["w"], b["t"], b["w"], len(total))
require(got == (75, 329, 76, 438, 24), f"P112 C.6 positive control changed: {got}")
require(relaxed_row_exact(a["t"], a["mu"], total, a["Z"], p112, pe112, pd112)
        and relaxed_row_exact(b["t"], b["mu"], total, b["Z"], p112, pe112, pd112),
        "P112 positive-control relaxed rows failed exact replay")
require(full_unit_exact(p112, a, b, total), "P112 positive control failed full 112x112 replay")

# Negative controls for certificate integrity: changing a root or a label must
# break the independent Gram/label checks above.
bad_root = [row[:] for row in L]
bad_root[51][0] += 1
require(dot(bad_root[51], bad_root[51]) != 4, "root mutation negative control did not detect corruption")
bad_label = U[:]
bad_label[0] ^= 1
require(any(dot2(bad_label[0], U[j]) != ((1 + G[0][j]) & 1) for j in range(120)),
        "label mutation negative control did not detect corruption")

print("PASS_P120_CALIBRATED_TWO_TARGET_SEED51")
print("P120 ports=120 targets=120 nonzero_sink_words=511 tested=61320")
print("P120 label_valid_rows=30600 calibrated_rows=63 nonzero_diagonal_nodes=27")
print(f"P120 distinct_target_pairs={raw_pairs} shared_total_available={available_pairs} "
      f"cross_target_diagonal_obstructions={target_contaminated} one_cross={one_cross} both_cross={two_cross}")
print(f"P120 exact_pairs={exact_pairs}; no candidate in this calibrated shared-total ansatz")
print(f"P112 positive_control=targets({a['t']},{b['t']}) sinks({a['w']},{b['w']}) "
      f"shared_sources={len(total)} exact_matrix=112x112")
print("negative_controls=root_mutation,label_mutation detected")
