"""Check exact spectral exclusions for unpaired selected port sets."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import isqrt
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "circuit-interface" / "INTERFACE.json"
PAIR_RECEIPT_PIN = "77e6d0e69dacc72a8bf110d13bd5708283ebcae8155d1b6666613806ee1be5a0"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]


def log_series(x, terms=32):
    """Return rational bounds for log(x), with 1 <= x <= 2."""
    assert 1 <= x <= 2
    z = (x-1)/(x+1)
    power = z
    total = Q(0)
    for k in range(terms):
        total += 2*power/(2*k+1)
        power *= z*z
    error = 2*power/((2*terms+1)*(1-z*z))
    return total, total+error


def log_interval(x):
    assert x > 0
    if x < 1:
        lo, hi = log_interval(1/x)
        return -hi, -lo
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    lo, hi = log_series(x)
    two_lo, two_hi = log_series(Q(2))
    return lo+power*two_lo, hi+power*two_hi


def ceil_sqrt(x, denominator=256):
    numerator = isqrt(x*denominator*denominator)
    if numerator*numerator < x*denominator*denominator:
        numerator += 1
    result = Q(numerator, denominator)
    assert result*result >= x
    assert result == 0 or (result-Q(1,denominator))**2 < x
    return result


def check_fifteen_root_bound():
    """Check the finite cases in the fifteen-root edge proof."""
    eight_clique_cases = []
    for h in range(9):
        for total in range(-h, h+1, 2):
            if 9*h-total*total == 18:
                eight_clique_cases.append([h, total])
    assert eight_clique_cases == [[2, 0], [3, -3], [3, 3], [6, -6], [6, 6]]

    high_cases = [(total, Q(total*total-32, 4)) for total in range(-6,7,2)
                  if total*total >= 32]
    assert high_cases == [(-6, Q(1)), (6, Q(1))]
    low_cases = set()
    patterns = 0
    for epsilon in product([-1,0,1], repeat=7):
        h = sum(x != 0 for x in epsilon)
        if h > 5:
            continue
        total = sum(epsilon)
        residual_four = total*total-8*h+16
        if residual_four < 0:
            continue
        root = isqrt(residual_four)
        assert root*root == residual_four
        residual = Q(root, 2)
        low_cases.add((h, abs(total), str(residual*residual)))
        legal = 0
        nonorthogonal = 0
        for value in epsilon:
            inner_products = {Q(total,2)-2*value+sign*residual for sign in [-1,1]}
            legal += bool(inner_products & {-2,0,2})
            nonorthogonal += bool(inner_products & {-2,2})
        for t in range(min(7,legal)+1):
            assert h+min(t,nonorthogonal) <= max(7,t+2)
        patterns += 1
    assert sorted(low_cases) == [(0,0,"4"), (1,1,"9/4"), (2,0,"0"),
                                (2,2,"1"), (3,3,"1/4"), (4,4,"0"), (5,5,"1/4")]
    seven_clique_bounds = []
    for t in range(8):
        low = 8-t
        if t <= 1:
            bound = 21+6*t+5*low+28
        else:
            bound = 21+6*t+t*(t-1)//2+low*max(7,t+2)+low*(low-1)//2
        seven_clique_bounds.append(bound)
    assert seven_clique_bounds == [89,90,91,87,85,85,89,93]
    return {
        "edge_bound": 93,
        "clique_at_most_six_bound": 93,
        "clique_eight_projection_cases_h_s": eight_clique_cases,
        "clique_eight_edge_bound": 91,
        "clique_seven_high_residual_cases_s_a_squared": [[s,str(a)] for s,a in high_cases],
        "clique_seven_low_residual_cases_h_abs_s_a_squared": sorted(low_cases),
        "clique_seven_checked_low_patterns": patterns,
        "clique_seven_bounds_for_t_zero_through_seven": seven_clique_bounds,
    }


def main():
    pair_bytes = (HERE / "PAIR-BOUND.json").read_bytes()
    assert sha256(pair_bytes).hexdigest() == PAIR_RECEIPT_PIN
    pair = json.loads(pair_bytes)
    assert sha256(SOURCE.read_bytes()).hexdigest() == pair["interface_sha256"]
    data = json.loads(SOURCE.read_text())
    R = [[int(row.get(str(j), 0)) for j in range(112)] for row in data["R"]]
    columns = list(zip(*R))
    dot = lambda a,b: sum(x*y for x,y in zip(a,b))
    assert all(dot(v,v) == 4 for v in columns)
    products = Counter(dot(columns[i],columns[j]) for i in range(112) for j in range(i))
    assert products == {0:3304, 2:1960, -2:952}
    for selected in [A,T]:
        assert [[sum(R[i][j]*R[k][j] for j in selected) for k in range(8)]
                for i in range(8)] == [[4*(i == k) for k in range(8)] for i in range(8)]
    assert not set(A) & set(T)
    fifteen_root_bound = check_fifteen_root_bound()
    log44_lo, log44_hi = log_interval(Q(44))
    log2_lo, log2_hi = log_interval(Q(2))
    rows = []
    for v in range(8,24):
        trace = 4*v
        edges = min(v*(v-1)//2, 7*v*v//16)
        if v >= 15:
            edges = min(edges, 31*v*(v-1)//70)
        square_trace = 16*v+8*edges
        discriminant = 7*(8*square_trace-trace*trace)
        rank_cap = (trace+ceil_sqrt(discriminant))/8
        cap = min(Q(2*v+2), Q(4)+Q(7*v,4), rank_cap)
        assert 0 < cap < 44
        quotient = trace//cap
        remainder = trace-quotient*cap
        crude = (44-cap)**quotient * (44-remainder) * 44**(7-quotient)
        assert quotient < 8 and 0 <= remainder < cap
        log_ratio_lo, log_ratio_hi = log_interval(44/(44-cap))
        logarithmic_lower = (8*log44_lo-Q(trace,44)
                             - Q(square_trace)/(cap*cap)*(log_ratio_hi-cap/44))
        lower_power = max(k for k in range(60) if logarithmic_lower > k*log2_hi
                          or crude > 2**k)
        upper = (Q(44)-Q(v,2))**8
        upper_power = min(k for k in range(60) if upper < 2**k)
        possible = list(range(lower_power+1, upper_power))
        margins = {}
        if not possible:
            margins = {
                "log_lower_minus_previous_power": str(logarithmic_lower-lower_power*log2_hi),
                "crude_lower_minus_previous_power": str(crude-2**lower_power),
                "next_power_minus_upper": str(2**upper_power-upper),
            }
        rows.append({
            "selected_size": v+16, "additional_columns": v,
            "trace": trace, "nonorthogonal_edge_bound": edges,
            "square_trace_bound": square_trace,
            "largest_eigenvalue_bound": str(cap),
            "crude_determinant_lower": str(crude),
            "determinant_upper": str(upper),
            "strict_lower_power": lower_power,
            "strict_upper_power": upper_power,
            "remaining_power_exponents": possible,
            "exact_exclusion_margins": margins,
        })
    result = {
        "status": "PASS_UNPAIRED_SPECTRAL_EXCLUSIONS",
        "base": pair["base"],
        "interface_sha256": pair["interface_sha256"],
        "source_reconstruction_receipt_sha256": PAIR_RECEIPT_PIN,
        "column_norm_squared": 4,
        "pair_inner_products": dict(sorted(products.items())),
        "logarithm_series_terms": 32,
        "fifteen_root_edge_proof": fifteen_root_bound,
        "rows": rows,
        "excluded_selected_sizes": [r["selected_size"] for r in rows if not r["remaining_power_exponents"]],
        "unresolved_selected_sizes": [r["selected_size"] for r in rows if r["remaining_power_exponents"]],
        "not_claimed": ["An admissible selected set of an unresolved size", "A supplier or kappa improvement"],
    }
    (HERE / "SPECTRAL-BOUND.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"],
                      "excluded_selected_sizes": result["excluded_selected_sizes"],
                      "remaining": {r["selected_size"]:r["remaining_power_exponents"] for r in rows if r["remaining_power_exponents"]}}), flush=True)


if __name__ == "__main__":
    main()
