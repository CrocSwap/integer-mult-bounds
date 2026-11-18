"""Check the sharp prefix envelope for every active tensor repetition.

The coefficient scan adapts Nick Petalas's PR7725 and Ali Romman's PR7709.
Retained files remain unchanged. See CREDITS.md for the full source credit.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import comb
from pathlib import Path
import json
import runpy

HERE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(HERE / "retained/pr7725/verify.py"))
NATIVE = runpy.run_path(str(HERE / "retained/native_verify.py"))
Q = SOURCE["GRID"]
WINNER = (156140, 11, 127)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def provenance():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for pin in pins:
        raw = (HERE / pin["path"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"]
             and sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == pin["git_blob"],
             "retained bytes: " + pin["path"])
    return len(pins)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def distances(graph):
    frames = graph["frames"]
    need(all(rank(row) == len(row) and all(0 < v < 512 for v in row) for row in frames),
         "nine-axis independent chart bases")
    result = {}
    for current, frame in enumerate(frames):
        ds = {ingress: 2*rank(frame+frames[ingress])-len(frame)-len(frames[ingress])
              for ingress in set(graph["initial"])}
        need(all(0 <= d <= 9 for d in ds.values()), "transition rank range")
        result[current] = [ds[ingress] for ingress in graph["initial"]]
    return result


def scan(graph, forms, moves, ranks):
    charts = {~i: chart for i, chart in enumerate(graph["initial"])}
    values = {~i: {i: Q} for i in range(len(charts))}
    polynomials, winning = {}, None
    count, products = 0, 0
    trace = sha256()
    for key in graph["schedule"]:
        current = moves[key][0] if key in moves else graph["final"][key-graph["first_output"]]
        ds, row, mass = ranks[current], {}, [0]*10
        for term, (donor, factor) in enumerate(forms[key], 1):
            need(charts[donor] == current, "same-chart donor")
            for owner, value in values[donor].items():
                part, remainder = divmod(factor.numerator*value, factor.denominator)
                need(remainder == 0, "exact normalized coefficient product")
                old = row.get(owner, 0)
                new = old + part
                mass[ds[owner]] += abs(new) - abs(old)
                if new:
                    row[owner] = new
                else:
                    row.pop(owner, None)
                products += 1
            need(min(mass) >= 0, "nonnegative mass in each rank")
            location = (key, term, current)
            poly = tuple(mass)
            polynomials.setdefault(poly, location)
            trace.update(encoded([location, poly]) + b"\n")
            if location == WINNER:
                winning = row.copy()
            count += 1
        if key in moves:
            values[key] = row
            charts[key] = moves[key][1]
    need(count == sum(map(len, forms.values())) == 172414 and winning is not None,
         "every ordered nonempty prefix")
    return polynomials, winning, dict(prefixes=count, coefficient_products=products,
                                     distinct_rank_mass_vectors=len(polynomials),
                                     prefix_trace_sha256=trace.hexdigest())


def shift_at_one(poly):
    return tuple(sum(poly[d]*comb(d, k) for d in range(k, 10)) for k in range(10))


def weights(poly, parity):
    return tuple(value*(1 << ((d+1)//2) if parity else 1) for d, value in enumerate(poly))


def dominate(candidate, polynomials, parity):
    upper = shift_at_one(weights(candidate, parity))
    minimum, equal, trace = [None]*10, 0, sha256()
    for poly in sorted(polynomials):
        lower = shift_at_one(weights(poly, parity))
        difference = tuple(a-b for a, b in zip(upper, lower, strict=True))
        need(min(difference) >= 0, "negative shifted dominance coefficient")
        equal += not any(difference)
        minimum = [d if old is None else min(old, d)
                   for old, d in zip(minimum, difference, strict=True)]
        trace.update(encoded([poly, difference]) + b"\n")
    return dict(parity=parity, continuous_parameter_lower_bound=1,
                shifted_candidate_coefficients=list(upper),
                polynomials_checked=len(polynomials), coefficients_checked=10*len(polynomials),
                equal_polynomials=equal, minimum_difference_coefficients=minimum,
                dominance_sha256=trace.hexdigest())


def multiply_histograms(left, right):
    result = Counter()
    for (a, b), count_a in left.items():
        for (c, d), count_b in right.items():
            result[a*c-b*d, a*d+b*c] += count_a*count_b
    return result


def physical_rows(graph, coefficients, ranks):
    frames = graph["frames"]
    inverse = NATIVE["adjoint"](NATIVE["frame"](frames[WINNER[2]], 9))
    rows, gains = {}, {}
    for ingress in sorted({graph["initial"][i] for i in coefficients}):
        circuit = inverse + NATIVE["frame"](frames[ingress], 9)
        column, bits = NATIVE["state"](circuit, basis=0)
        histogram = Counter(column.values())
        role = next(i for i in coefficients if graph["initial"][i] == ingress)
        d = ranks[WINNER[2]][role]
        need(len(column) == 2**d and
             all((a*a+b*b)*2**d == 2**(2*bits) for a, b in column.values()),
             "exact row support and component magnitudes")
        need(all((a == 0 or b == 0) if d % 2 == 0 else abs(a) == abs(b)
                 for a, b in column.values()), "Gaussian phase parity")
        tensor, checks = Counter({(1, 0): 1}), []
        for m in range(1, 5):
            tensor = multiply_histograms(tensor, histogram)
            gain = F(sum(count*(abs(a)+abs(b)) for (a, b), count in tensor.items()), 2**(m*bits))
            need(gain == 2**((m*d+1)//2) and sum(tensor.values()) == 2**(m*d),
                 "actual tensor row gain")
            checks.append(dict(repetitions=m, exact_gain=str(gain), nonzero_entries=sum(tensor.values())))
            gains[ingress, m] = gain
        rows[str(ingress)] = dict(rank=d, dyadic_bits=bits, nonzero_entries=len(column),
                                  exact_column_sha256=sha256(encoded(sorted(column.items()))).hexdigest(),
                                  tensor_checks=checks)
    attained = {str(m): str(sum(abs(q)*gains[graph["initial"][i], m] for i, q in coefficients.items()))
                for m in range(1, 5)}
    return rows, attained


def calculate():
    pins = provenance()
    graph, forms, moves = SOURCE["read_source"]()
    ranks = distances(graph)
    polynomials, winning, census = scan(graph, forms, moves, ranks)
    coefficients = SOURCE["reverse_coefficients"](graph["schedule"], forms, WINNER[0], WINNER[1])
    need(coefficients == {i: F(value, Q) for i, value in winning.items()},
         "separate backward rational expansion")
    mass = [0]*10
    for i, value in winning.items():
        mass[ranks[WINNER[2]][i]] += abs(value)
    expected = [F(0)]*10
    expected[4], expected[8], expected[9] = F(12927, 2), F(36549, 8), F(51071533, 256)
    need([F(x, Q) for x in mass] == expected, "winning rank coefficients")
    dominance = [dominate(mass, polynomials, parity) for parity in (0, 1)]
    rows, attained = physical_rows(graph, coefficients, ranks)
    for m, value in attained.items():
        predicted = sum(q*2**((int(m)*d+1)//2) for d, q in enumerate(expected))
        need(F(value) == predicted, "attaining physical tensor signs")
    source = json.loads((HERE / "retained/pr7725/RESULT.json").read_text())
    need(attained["1"] == source["maximum"] and len(coefficients) == source["nonzero_entrances"] == 448,
         "one-tile source anchor")
    damaged = mass.copy()
    damaged[9] -= 1
    rejected = []
    for parity in (0, 1):
        try:
            dominate(damaged, [tuple(mass)], parity)
        except ValueError as error:
            need(str(error) == "negative shifted dominance coefficient", "bound control reason")
            rejected.append(parity)
        else:
            raise ValueError("a bound below the actual witness passed")
    need(2**((2*9+1)//2) == 512 < 32**2, "real-box gain is not multiplicative")
    need(2**((9+1)//2) == 32 != 2**(9//2), "odd-rank ceiling is required")
    return dict(status="PASS_RELAY1256_ALL_TENSOR_PREFIXES", source_pins=pins,
                graph_sha256=SOURCE["GRAPH_HASH"], census=census, winner=list(WINNER),
                last_donor=forms[WINNER[0]][WINNER[1]-1][0], nonzero_entrances=len(coefficients),
                rank_mass={str(d): str(q) for d, q in enumerate(expected) if q},
                dominance=dominance, physical_rows=rows, finite_attainment=attained,
                controls=dict(understated_bound_rejected_for_both_parities=rejected,
                              incorrect_multiplicative_gain=[1024, 512],
                              incorrect_odd_rank_floor=[16, 32]),
                contract="All positive integer repetitions; independent real and imaginary entrance components in [-1,1]; exact row prefixes only.")


if __name__ == "__main__":
    result = calculate()
    need(result == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    print(result["status"], result["census"]["prefixes"], "prefixes; all m >= 1")
