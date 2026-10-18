"""Prepared for Thiago with OpenAI GPT-6 Astra and Codex assistance. Apache-2.0.

Stdlib-only exact verifier for the known Petersen broadcast/rank bound 5.

No optimization package, floating-point arithmetic, assert statements, or
import of the discovery program is used.  See Blasiak--Kleinberg--Lubetzky,
"Index coding via linear programming", Fact 5.6 (1), for prior art.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def graph():
    vertices = [list(e) for e in combinations(range(5), 2)]
    adjacency = []
    for a in vertices:
        mask = 0
        for j, b in enumerate(vertices):
            if len(set(a + b)) == 4:
                mask |= 1 << j
        adjacency.append(mask)
    require(all(m.bit_count() == 3 for m in adjacency), "Petersen degrees")
    require(all(((adjacency[i] >> j) & 1) == ((adjacency[j] >> i) & 1)
                for i in range(10) for j in range(10)), "graph symmetry")
    return vertices, adjacency


def expression(entry, adjacency):
    """Reconstruct a genuine Shannon/rank constraint, never trust stored rows."""
    require(isinstance(entry, dict), "constraint must be a mapping")
    kind = entry.get("kind")
    require(kind in ("monotone", "slope", "submodular", "decode", "normalize"),
            "unknown constraint kind")
    expected_keys = {"kind", "multiplier"}
    if kind != "normalize":
        expected_keys |= {"S", "i"}
    if kind == "submodular":
        expected_keys.add("j")
    require(set(entry) == expected_keys, "constraint keys")
    if kind == "normalize":
        return {1023: 1}, -10, False
    s, i = entry["S"], entry["i"]
    require(type(s) is int and 0 <= s < 1024, "subset outside ten vertices")
    require(type(i) is int and 0 <= i < 10 and not s & (1 << i),
            "added vertex must be absent")
    si = s | (1 << i)
    if kind == "monotone":
        return {si: 1, s: -1}, 0, True
    if kind == "slope":
        return {s: 1, si: -1}, 1, True
    if kind == "decode":
        require(adjacency[i] & s == adjacency[i], "decode missing known neighbor")
        return {si: 1, s: -1}, 0, False
    j = entry["j"]
    require(type(j) is int and i < j < 10 and not s & (1 << j),
            "submodular vertices must be distinct and absent")
    sj, sij = s | (1 << j), si | (1 << j)
    return {si: 1, sj: 1, s: -1, sij: -1}, 0, True


def verify(certificate):
    vertices, adjacency = graph()
    require(certificate.get("schema") == "petersen-shannon-rank-lp-dual-v1", "schema")
    require(certificate.get("vertices") == vertices, "vertex numbering changed")
    constraints = certificate.get("constraints")
    require(isinstance(constraints, list) and constraints, "no certificate terms")
    total = [Fraction(0) for _ in range(1024)]
    constant = Fraction(0)
    kinds = Counter()
    seen = set()
    for entry in constraints:
        coefficients, offset, inequality = expression(entry, adjacency)
        require(isinstance(entry["multiplier"], str), "multiplier must be exact text")
        multiplier = Fraction(entry["multiplier"])
        require(multiplier != 0, "zero certificate term")
        require(not inequality or multiplier > 0, "inequality multiplier must be positive")
        signature = tuple(sorted((k, v) for k, v in entry.items() if k != "multiplier"))
        require(signature not in seen, "duplicate constraint term")
        seen.add(signature)
        kinds[entry["kind"]] += 1
        for index, value in coefficients.items():
            total[index] += multiplier * value
        constant += multiplier * offset
    require(total[0] == 1, "wrong coefficient of F(empty)")
    require(all(value == 0 for value in total[1:]), "uncancelled subset coefficient")
    require(constant == -5, "wrong constant term")
    return {"terms": len(constraints), "kinds": dict(sorted(kinds.items())),
            "exact_identity": "F(empty) - 5", "subset_coefficients_checked": len(total)}


def matching_witness(certificate):
    """A five-pair scalar code attains the lower bound over every field."""
    _, adjacency = graph()

    def search(remaining):
        if remaining == 0:
            return []
        i = (remaining & -remaining).bit_length() - 1
        for j in range(i + 1, 10):
            if remaining & adjacency[i] & (1 << j):
                rest = search(remaining ^ (1 << i) ^ (1 << j))
                if rest is not None:
                    return [(i, j)] + rest
        return None

    pairs = search(1023)
    require(pairs is not None and len(pairs) == 5, "no perfect matching")
    pair_masks = [(1 << i) | (1 << j) for i, j in pairs]
    require(sum(pair_masks) == 1023, "matching does not partition vertices")
    # Broadcast x_i + x_j on each edge.  Adding the coordinates in S to its
    # five independent rows increases rank once for every pair touched by S.
    f = [5 + sum(bool(s & p) for p in pair_masks) for s in range(1024)]
    require(f[0] == 5 and f[1023] == 10, "matching endpoint values")
    checked_inequalities = 0
    checked_decodes = 0
    for s in range(1024):
        absent = [i for i in range(10) if not s & (1 << i)]
        for i in absent:
            si = s | (1 << i)
            require(0 <= f[si] - f[s] <= 1, "matching monotonicity/slope")
            checked_inequalities += 2
            if adjacency[i] & s == adjacency[i]:
                require(f[si] == f[s], "matching decoding")
                checked_decodes += 1
        for i, j in combinations(absent, 2):
            require(f[s | (1 << i)] + f[s | (1 << j)] >=
                    f[s] + f[s | (1 << i) | (1 << j)], "matching submodularity")
            checked_inequalities += 1
    for entry in certificate["constraints"]:
        coefficients, offset, _ = expression(entry, adjacency)
        value = offset + sum(coefficient * f[s] for s, coefficient in coefficients.items())
        require(value == 0, "non-tight term on matching code")
    return {"pairs": pairs, "exact_rate": 5,
            "all_elementary_inequalities_checked": checked_inequalities,
            "all_decoding_equalities_checked": checked_decodes}


def negative_controls(certificate):
    passed = []

    def reject(name, candidate):
        try:
            verify(candidate)
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            passed.append(name)
            return
        raise ValueError("negative control accepted: " + name)

    changed = deepcopy(certificate)
    term = changed["constraints"][0]
    term["multiplier"] = str(Fraction(term["multiplier"]) + Fraction(1, 8))
    reject("changed_multiplier", changed)

    changed = deepcopy(certificate)
    term = next(t for t in changed["constraints"]
                if t["kind"] in ("monotone", "slope", "submodular"))
    term["multiplier"] = str(-abs(Fraction(term["multiplier"])))
    reject("negative_inequality_multiplier", changed)

    changed = deepcopy(certificate)
    term = next(t for t in changed["constraints"] if t["kind"] == "decode")
    _, adjacency = graph()
    term["S"] &= ~(adjacency[term["i"]] & -adjacency[term["i"]])
    reject("missing_decode_neighbor", changed)

    changed = deepcopy(certificate)
    changed["constraints"] = [t for t in changed["constraints"] if t["kind"] != "normalize"]
    reject("omitted_normalization", changed)

    changed = deepcopy(certificate)
    changed["vertices"][0] = changed["vertices"][1]
    reject("changed_graph_numbering", changed)
    return passed


def main():
    path = (Path(sys.argv[1]) if len(sys.argv) > 1 else
            Path(__file__).with_name("PETERSEN-LP-DUAL.json"))
    raw = path.read_bytes()
    certificate = json.loads(raw)
    result = verify(certificate)
    result["matching_upper_bound"] = matching_witness(certificate)
    result["negative_controls_rejected"] = negative_controls(certificate)
    result["certificate_sha256"] = sha256(raw).hexdigest()
    result = dict(PASS=True, **result)
    Path(__file__).with_name("PETERSEN-VERIFIED.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
