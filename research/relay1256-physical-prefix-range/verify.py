"""Compute chart-weighted prefix ranges and realize the maximum at address zero."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
NATIVE = (HERE.parents[1] / "research/p104-shared-native-helper-splits/"
          "retained/retained/native/native_verify.py")
PACKED_HASH = "0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc"
GRAPH_HASH = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
NATIVE_HASH = "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38"
GRID = 921600


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_source():
    packed = (HERE / "data/CANDIDATE-GRAPH.json.gz").read_bytes()
    require(sha256(packed).hexdigest() == PACKED_HASH, "source archive hash")
    raw = gzip.decompress(packed)
    require(sha256(raw).hexdigest() == GRAPH_HASH, "source graph hash")
    graph = json.loads(raw)
    forms = {key: [(donor, Fraction(q)) for donor, q in terms]
             for key, terms in graph["forms"]}
    moves = {key: (a, b) for key, a, b in graph["moves"]}
    require(len(graph["schedule"]) == len(forms) and set(graph["schedule"]) == forms.keys(),
            "row order must visit each form exactly once")
    return graph, forms, moves


def span_mask(basis):
    elements = [0]
    for axis in basis:
        require(0 < axis < 512 and axis not in elements, "invalid nine-axis basis")
        elements.extend([axis ^ element for element in elements])
    return sum(1 << element for element in elements)


def chart_weights(graph):
    frames = graph["frames"]
    spans = [span_mask(basis) for basis in frames]
    ingress_charts = set(graph["initial"])
    by_start = {}
    for current, span in enumerate(spans):
        weights = {}
        for ingress in ingress_charts:
            intersection_dim = (span & spans[ingress]).bit_count().bit_length() - 1
            distance = len(frames[current]) + len(frames[ingress]) - 2 * intersection_dim
            weights[ingress] = 1 << ((distance + 1) // 2)
        by_start[current] = [weights[i] for i in graph["initial"]]
    return by_start


def maximum_prefix(graph, forms, moves):
    weights = chart_weights(graph)
    charts = {~i: chart for i, chart in enumerate(graph["initial"])}
    values = {~i: {i: GRID} for i in range(len(charts))}
    peak = 0
    winner = None
    count = 0
    for key in graph["schedule"]:
        current = moves[key][0] if key in moves else graph["final"][key - graph["first_output"]]
        row_weights = weights[current]
        row = {}
        total = 0
        for term, (donor, q) in enumerate(forms[key], 1):
            require(charts[donor] == current, "prefix reads a donor in another chart")
            for i, coefficient in values[donor].items():
                scaled, residue = divmod(q.numerator * coefficient, q.denominator)
                require(residue == 0, "nonintegral normalized coefficient")
                old = row.get(i, 0)
                new = old + scaled
                total += (abs(new) - abs(old)) * row_weights[i]
                if new:
                    row[i] = new
                else:
                    row.pop(i, None)
            count += 1
            if total > peak:
                peak = total
                winner = (key, term, current, row.copy())
        if key in moves:
            values[key] = row
            charts[key] = moves[key][1]
    require(winner is not None, "no nonzero prefix")
    return Fraction(peak, GRID), winner, count


def reverse_coefficients(schedule, forms, key, term):
    """Expand just the winning prefix backward over Q, without a working grid."""
    terms = forms[key][:term]
    pending = dict(terms)
    require(len(pending) == len(terms), "repeated donor in the winning prefix")
    for prior in reversed(schedule[:schedule.index(key)]):
        factor = pending.pop(prior, 0)
        if factor:
            for donor, q in forms[prior]:
                pending[donor] = pending.get(donor, 0) + factor * q
    require(all(donor < 0 for donor in pending), "unfinished reverse expansion")
    return {~donor: q for donor, q in pending.items() if q}


def sign(value):
    return (value > 0) - (value < 0)


def physical_witness(graph, current, coefficients):
    """Use the actual adjoint row to construct and evaluate signed physical inputs."""
    require(sha256(NATIVE.read_bytes()).hexdigest() == NATIVE_HASH, "chart interpreter hash")
    native = runpy.run_path(str(NATIVE))
    charts = graph["frames"]
    undo_current = native["adjoint"](native["frame"](charts[current], 9))
    one_column = {}
    contributions = Counter()
    total = Fraction()
    for role, q in coefficients.items():
        ingress = graph["initial"][role]
        if ingress not in one_column:
            circuit = undo_current + native["frame"](charts[ingress], 9)
            state, exponent = native["state"](circuit, basis=0)
            # The adjoint column stores (a,b); the physical matrix row stores (a,-b).
            real_output = sum(a * sign(a) + b * sign(b) for a, b in state.values())
            one_column[ingress] = Fraction(real_output, 1 << exponent)
        # Multiply the entrance signs by sign(q) for this independent role.
        gain = one_column[ingress]
        contributions[gain] += abs(q)
        total += q * sign(q) * gain
    return total, {str(k): str(v) for k, v in sorted(contributions.items())}


def check():
    graph, forms, moves = read_source()
    maximum, (key, term, current, scaled), count = maximum_prefix(graph, forms, moves)
    coefficients = reverse_coefficients(graph["schedule"], forms, key, term)
    require(coefficients == {i: Fraction(z, GRID) for i, z in scaled.items()},
            "forward and backward winning forms disagree")
    attained, by_gain = physical_witness(graph, current, coefficients)
    require(attained == maximum, "signed physical input fails to attain the upper bound")
    return {"graph_sha256": GRAPH_HASH, "chart_interpreter_sha256": NATIVE_HASH,
            "rows": len(forms), "nonempty_prefixes": count, "maximum": str(maximum),
            "row": key, "term_one_based": term, "last_donor": forms[key][term - 1][0],
            "current_chart": current, "nonzero_entrances": len(coefficients),
            "normalized_abs_mass_by_physical_gain": by_gain,
            "attained_at_address_zero_real": str(attained)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="write the computed receipt to stdout")
    args = parser.parse_args()
    result = check()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_bytes()), "receipt mismatch")
        print(f"PASS_RELAY1256_PHYSICAL_PREFIX {result['nonempty_prefixes']} prefixes; "
              f"maximum {result['maximum']} at row {result['row']}, term {result['term_one_based']}")
