"""Independent Fraction/column-action distance checker; no project imports.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Checks the exact two-register census, not physical/native supplier admission.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
I = (F(1), F(0), F(0), F(1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def right_action(matrix, instruction):
    """Multiply on the RIGHT, by elementary column operations."""
    kind, column, value = instruction
    out = list(matrix)
    if kind == "mix":
        for row in (0, 1):
            out[2 * row + column] += value * matrix[2 * row + 1 - column]
    else:
        for row in (0, 1):
            out[2 * row + column] *= value
    return tuple(out)


ALPHABET = tuple(
    [("mix", c, F(sign)) for c in (0, 1) for sign in (-1, 1)]
    + [("scale", c, factor) for c in (0, 1) for factor in (F(-1), F(1, 2), F(2))]
)


def rational_ball(radius=6):
    distances = {I: 0}
    frontier = [I]
    layers = [1]
    for depth in range(radius):
        next_layer = []
        for matrix in frontier:
            for gate in ALPHABET:
                other = right_action(matrix, gate)
                if other not in distances:
                    distances[other] = depth + 1
                    next_layer.append(other)
        frontier = next_layer
        layers.append(len(frontier))
    return distances, layers


def normalized_row(matrix, distance):
    denominator = max(value.denominator for value in matrix)
    require(denominator & (denominator - 1) == 0, "non-dyadic matrix")
    coefficients = [value.numerator * (denominator // value.denominator) for value in matrix]
    return (*coefficients, denominator.bit_length() - 1, distance)


def inverse(matrix):
    a, b, c, d = matrix
    determinant = a * d - b * c
    require(determinant != 0, "singular matrix")
    return d / determinant, -b / determinant, -c / determinant, a / determinant


def shortest(q, distances, inverses):
    best = None
    for (a, b, c, d), suffix_distance in inverses:
        # A = B^(-1) G(q), whereas the constructor solves B = G(q) A^(-1).
        prefix = (a, a * q + b, c, c * q + d)
        first = distances.get(prefix)
        if first is not None and (best is None or first + suffix_distance < best):
            best = first + suffix_distance
    return best


def word_matrix(names, sign=1):
    rows = [[F(1), F(0)], [F(0), F(1)]]
    for name in names:
        if name in ("t+s", "t-s", "s+t", "s-t"):
            dest = 0 if name[0] == "t" else 1
            value = sign * (1 if name[1] == "+" else -1)
            rows[dest] = [rows[dest][i] + value * rows[1 - dest][i] for i in (0, 1)]
        else:
            dest = 0 if "t" in name else 1
            factor = F(2) if name.startswith("2") else F(-1) if name.startswith("-") else F(1, 2)
            require(name in ("2t", "t/2", "2s", "s/2", "-t", "-s"), "unknown witness gate")
            rows[dest] = [factor * x for x in rows[dest]]
    return tuple(rows[0] + rows[1])


def validate_entry(entry, minimum):
    require(type(entry["best_comparator_cost"]) is int, "noninteger comparator cost")
    require(entry["two_register_minimum"] is None or type(entry["two_register_minimum"]) is int,
            "noninteger minimum")
    require(entry["two_register_minimum"] == minimum, "wrong shortest distance")
    lower = 13 if minimum is None else minimum
    require(type(entry["two_register_lower_bound"]) is int and entry["two_register_lower_bound"] == lower,
            "wrong lower bound")
    require(entry["complete_cost_lower_bound"] == lower + 1, "unpaid private clear")
    require(entry["best_comparator_cost"] <= 14, "cutoff does not exclude all improvements")
    improvement = minimum is not None and minimum + 1 < entry["best_comparator_cost"]
    require(type(entry["strict_improvement"]) is bool and entry["strict_improvement"] == improvement,
            "incorrect strict comparison")
    if minimum is not None:
        q = F(entry["coefficient"])
        require(len(entry["word"]) == minimum, "witness cost mismatch")
        require(word_matrix(entry["word"]) == (1, q, 0, 1), "positive witness endpoint")
        require(word_matrix(entry["word"], -1) == (1, -q, 0, 1), "negative witness endpoint")
    else:
        require(entry["word"] is None, "unreached target has a witness")


def independent_controls(entries, minima, distances):
    import copy
    examples = {entry["coefficient"]: entry for entry in entries}
    mutants = []
    for label, q, field, value in (
        ("optimistic_distance", "3", "two_register_minimum", 2),
        ("boolean_distance", "1", "two_register_minimum", True),
        ("unpaid_clear", "3", "complete_cost_lower_bound", 3),
        ("unproved_long_target", "1/64", "two_register_lower_bound", 14),
        ("false_improvement", "5/2", "strict_improvement", True),
    ):
        mutant = copy.deepcopy(examples[q])
        mutant[field] = value
        mutants.append((label, q, mutant))
    mutant = copy.deepcopy(examples["3"])
    mutant["word"][0] = "t-s"
    mutants.append(("wrong_witness_sign", "3", mutant))
    rejected = []
    for label, q, mutant in mutants:
        try:
            validate_entry(mutant, minima[q])
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted mutant: " + label)
    # A reduced ball actually loses a reachable frontier state.
    radius_five = {m: d for m, d in distances.items() if d <= 5}
    require(len(radius_five) == 8408 and len(radius_five) != len(distances), "radius deletion undetected")
    rejected.append("missing_depth_six_frontier")
    return rejected


def run(certificate):
    receipt = json.loads(certificate.read_text(encoding="utf-8"))
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    path = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz"
    raw = gzip.decompress((ROOT / path).read_bytes())
    require(sha256(raw).hexdigest() == pins["files"][path]["sha256"], "CK source pin")
    programs = json.loads(raw)
    domains = {}
    for orientation in ("forward", "backward"):
        domains[orientation] = Counter(abs(F(e[1][3], e[1][4])) for e in programs[orientation]
                                       if e[0] == "scalar" and e[1][0] == "add")
    entries = receipt["coefficients"]
    require([F(e["coefficient"]) for e in entries] == sorted(domains["forward"]), "incomplete coefficient domain")
    require(set(domains["forward"]) == set(domains["backward"]), "orientation domain differs")
    distances, layers = rational_ball()
    require(layers == receipt["layer_sizes"] == [1, 10, 69, 370, 1646, 6312, 22168], "BFS layer census")
    rows = sorted(normalized_row(m, d) for m, d in distances.items())
    digest = sha256()
    for row in rows:
        digest.update((",".join(map(str, row)) + "\n").encode("ascii"))
    require(digest.hexdigest() == receipt["distance_sha256"], "full group-ball distance digest")
    require(len(distances) == receipt["ball_states"] == 30576, "group-ball coverage")
    inverses = [(inverse(m), d) for m, d in distances.items()]
    minima = {}
    for entry in entries:
        q = F(entry["coefficient"])
        for orientation, domain in domains.items():
            require(entry["occurrences"][orientation] == domain[q], "occurrence count")
        minimum = shortest(q, distances, inverses)
        validate_entry(entry, minimum)
        minima[str(q)] = minimum
    require(sum(d is not None for d in minima.values()) == 77, "minimum census")
    require([e["coefficient"] for e in entries if e["strict_improvement"]] == ["2", "3"], "improvement census")
    controls = independent_controls(entries, minima, distances)
    return {"status": "PASS_RESTORED_SOURCE_INDEPENDENT", "states": len(distances),
            "coefficients": len(entries), "exact_minima": 77,
            "distance_sha256": digest.hexdigest(), "controls": controls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=HERE / "EXPECTED.json")
    args = parser.parse_args()
    print(json.dumps(run(args.certificate), sort_keys=True))
