"""Review the unpaired spectral bound without producer imports."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import product
from math import comb, isqrt
from pathlib import Path
import gzip
import json
import subprocess
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LANES = HERE.parent
PRODUCER = LANES / "schur-selection"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_PIN = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
PINS = {
    "SPECTRAL-BOUND.md": "6dd2afed08d8873a2277ccfef4edd1bc212e831b8495bb659809f76d77802af1",
    "check_spectral_bound.py": "ecc031e20c309c4e1d04443b60a58fe03d32ce73a5a3b43078e9cb673341c61c",
    "SPECTRAL-BOUND.json": "d1124af128b6e526461c7587c2a7331dc4d19c9d90433d8d08bf9676c33a8a84",
    "PAIR-BOUND.json": "77e6d0e69dacc72a8bf110d13bd5708283ebcae8155d1b6666613806ee1be5a0",
}
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": (
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
        "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"),
    "slots/local/LOCAL-PROGRAMS.json.gz": (
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
        "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3"),
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, "Changed input: " + str(path))
    return raw


def source_matrix():
    raw = subprocess.check_output(["git", "show", BASE + ":" + ARCHIVE],
                                  cwd=ROOT / "worktrees/k5-centre-sharing")
    need(sha256(raw).hexdigest() == ARCHIVE_PIN, "Archive pin differs")
    inputs = {}
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        for name, (compressed_pin, payload_pin) in MEMBERS.items():
            matches = [x for x in archive.getmembers() if x.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "Invalid archive member")
            compressed = archive.extractfile(matches[0]).read()
            need(sha256(compressed).hexdigest() == compressed_pin, "Member pin differs")
            payload = gzip.decompress(compressed)
            need(sha256(payload).hexdigest() == payload_pin, "Payload pin differs")
            inputs[name.rsplit("/", 1)[-1]] = json.loads(payload)
    word = inputs["CANONICAL-WORD.json.gz"]
    events = inputs["LOCAL-PROGRAMS.json.gz"]["forward"]
    cut = events.index(["phase", "centers"])
    gradient = [{} for _ in range(712)]
    for k, center in enumerate(word["centers"]):
        gradient[center][k] = Q(1)

    def register(token):
        need(token[0] in ("L", "C"), "Unknown field namespace")
        value = token[1] + 704 * (token[0] == "C")
        need(0 <= value < 712, "Invalid field")
        return value

    for event in reversed(events[:cut]):
        if event[0] != "scalar":
            continue
        op = event[1]
        target = register(op[1])
        if op[0] == "clear":
            gradient[target] = {}
        elif op[0] == "scale":
            scale = Q(op[2], op[3])
            gradient[target] = {k: x * scale for k, x in gradient[target].items()}
        else:
            need(op[0] in ("add", "copy"), "Unknown scalar operation")
            source = register(op[2])
            need(source != target, "Unexpected aliased scalar operation")
            scale = Q(1) if op[0] == "copy" else Q(op[3], op[4])
            for k, x in gradient[target].items():
                gradient[source][k] = gradient[source].get(k, 0) + scale*x
            if op[0] == "copy":
                gradient[target] = {}
    R = [[gradient[p].get(k, Q(0)) for p in range(112)] for k in range(8)]
    interface = json.loads(pinned(LANES / "circuit-interface/INTERFACE.json", INTERFACE_PIN))
    need(R == [[Q(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]],
         "Reverse source reconstruction differs from R")
    need(all(x.denominator == 1 for row in R for x in row), "R is not integral")
    R = [[int(x) for x in row] for row in R]
    gram = lambda ports: [[sum(R[i][p]*R[j][p] for p in ports)
                           for j in range(8)] for i in range(8)]
    need(gram(range(112)) == [[56*(i == j) for j in range(8)] for i in range(8)],
         "Full source Gram differs")
    need(not set(A) & set(T), "Fixed minors overlap")
    for ports in (A, T):
        need(gram(ports) == [[4*(i == j) for j in range(8)] for i in range(8)],
             "A fixed minor differs")
    columns = list(zip(*R))
    need(all(sum(x*x for x in col) == 4 for col in columns), "A root norm differs")
    dots = Counter(sum(x*y for x, y in zip(columns[i], columns[j]))
                   for i in range(112) for j in range(i))
    need(dots == {0: 3304, 2: 1960, -2: 952}, "Root products differ")
    return {"archive_sha256": ARCHIVE_PIN, "members": MEMBERS,
            "reverse_output_forms": 8, "source_columns": 112, "source_cut": cut,
            "pair_products": dict(sorted(dots.items())), "full_gram": "56 I8",
            "fixed_minor_grams": "4 I8"}


def graph_cases(producer):
    for n in (7, 8):
        G = [[Q(2*(i == j)+2) for j in range(n)] for i in range(n)]
        H = [[(Q(i == j)-Q(1, n+1))/2 for j in range(n)] for i in range(n)]
        need(all(sum(G[i][k]*H[k][j] for k in range(n)) == (i == j)
                 for i in range(n) for j in range(n)), "Clique inverse differs")
    clique8 = [[h, s] for h in range(9) for s in range(-h, h+1, 2)
               if 9*h-s*s == 18]
    need(clique8 == producer["clique_eight_projection_cases_h_s"], "Eight-clique cases differ")
    need(28+7*max(x[0] for x in clique8)+21 == 91, "Eight-clique edge bound differs")
    high = [[s, str(Q(s*s-32, 4))] for s in range(-6, 7, 2) if s*s >= 32]
    need(high == [[-6, "1"], [6, "1"]], "High-root cases differ")
    expected = {(0, 0, "4"): 7, (1, 1, "9/4"): 6, (2, 0, "0"): 2,
                (2, 2, "1"): 7, (3, 3, "1/4"): 4,
                (4, 4, "0"): 3, (5, 5, "1/4"): 2}
    cases = Counter()
    comparisons = 0
    for epsilon in product((-1, 0, 1), repeat=7):
        h, s = sum(x != 0 for x in epsilon), sum(epsilon)
        residual4 = s*s-8*h+16
        if h > 5 or residual4 < 0:
            continue
        a2 = isqrt(residual4)
        need(a2*a2 == residual4, "A low-root residual needs another case")
        key = (h, abs(s), str(Q(residual4, 4)))
        need(key in expected, "Unlisted low-root case")
        allowed = []
        for index in range(7):
            dots2 = {s-4*epsilon[index]+sign*a2 for sign in (-1, 1)}
            allowed.append(dots2 & {-4, 0, 4})
        possible_edges = sum(bool(values & {-4, 4}) for values in allowed)
        need(possible_edges == expected[key], "The low-root table differs")
        for t in range(8):
            if t <= sum(bool(values) for values in allowed):
                need(h+min(t, possible_edges) <= max(7, t+2), "Combined degree bound fails")
                comparisons += 1
        cases[key] += 1
    need(sum(cases.values()) == 281 and set(cases) == set(expected), "Low cases are incomplete")
    bounds = [21+6*t+5*(8-t)+28 if t < 2 else
              21+6*t+comb(t, 2)+(8-t)*max(7, t+2)+comb(8-t, 2)
              for t in range(8)]
    need(bounds == [89, 90, 91, 87, 85, 85, 89, 93], "Seven-clique total differs")
    need(bounds == producer["clique_seven_bounds_for_t_zero_through_seven"], "Receipt cases differ")
    need((Q(1)-Q(1, 6))*225/2 < 94, "Small-clique bound fails")
    return {"epsilon_patterns": sum(cases.values()), "degree_checks": comparisons,
            "low_table": [[*key, expected[key], cases[key]] for key in sorted(cases)],
            "seven_clique_bounds": bounds, "eight_clique_bound": 91,
            "fifteen_root_edge_bound": 93}


def log_bounds(argument, terms=64):
    """Use direct rational powers and an explicit positive tail bound."""
    x = Q(argument)
    need(x > 0, "Nonpositive logarithm")
    if x < 1:
        lo, hi = log_bounds(1/x, terms)
        return -hi, -lo
    exponent = 0
    while x > 2:
        x /= 2
        exponent += 1
    z = (x-1)/(x+1)
    lower = sum((2*z**j/Q(j) for j in range(1, 2*terms, 2)), Q(0))
    upper = lower + 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    if exponent:
        lo2, hi2 = log_bounds(Q(2), terms)
        lower, upper = lower+exponent*lo2, upper+exponent*hi2
    return lower, upper


def rational_floor(x, scale=10**9):
    return str(Q((x*scale).numerator//(x*scale).denominator, scale))


def spectral_cases(receipt):
    lo44, _ = log_bounds(44)
    lo2, hi2 = log_bounds(2)
    log44_32, _ = log_bounds(44, 32)
    _, log2_32 = log_bounds(2, 32)
    rows = []
    for row in receipt["rows"]:
        v = row["additional_columns"]
        trace = 4*v
        edge = min(comb(v, 2), 7*v*v//16)
        if v >= 15:
            edge = min(edge, 93*comb(v, 2)//comb(15, 2))
        moment = 16*v+8*edge
        discr = 7*(8*moment-trace*trace)
        root_upper = isqrt(discr*256**2)
        root_upper += (root_upper**2 != discr*256**2)
        cap = min(Q(2*v+2), Q(4)+Q(7*v, 4), (trace+Q(root_upper, 256))/8)
        need(0 < cap < 44 and Q(row["largest_eigenvalue_bound"]) == cap, "Eigenvalue cap differs")
        need((row["trace"], row["nonorthogonal_edge_bound"], row["square_trace_bound"])
             == (trace, edge, moment), "Moment ledger differs")
        count = int(trace//cap)
        leftover = trace-count*cap
        need(0 <= count < 8 and 0 <= leftover < cap, "Invalid extreme spectrum")
        crude = (44-cap)**count*(44-leftover)*44**(7-count)
        upper = (44-Q(v, 2))**8
        ratio = Q(44)/(44-cap)
        _, log_ratio_hi = log_bounds(ratio)
        lower = 8*lo44-Q(trace, 44)-Q(moment)/cap**2*(log_ratio_hi-cap/44)
        lower_power = max(k for k in range(60) if crude > 2**k or lower > k*hi2)
        upper_power = min(k for k in range(60) if upper < 2**k)
        remaining = list(range(lower_power+1, upper_power))
        need(Q(row["crude_determinant_lower"]) == crude and Q(row["determinant_upper"]) == upper,
             "Determinant bounds differ")
        need((lower_power, upper_power, remaining) ==
             (row["strict_lower_power"], row["strict_upper_power"], row["remaining_power_exponents"]),
             "Power-of-two interval differs")
        if not remaining:
            _, lr32 = log_bounds(ratio, 32)
            l32 = 8*log44_32-Q(trace, 44)-Q(moment)/cap**2*(lr32-cap/44)
            margins = row["exact_exclusion_margins"]
            need(Q(margins["log_lower_minus_previous_power"]) == l32-lower_power*log2_32,
                 "Saved logarithm margin differs")
            need(Q(margins["crude_lower_minus_previous_power"]) == crude-2**lower_power,
                 "Saved crude margin differs")
            need(Q(margins["next_power_minus_upper"]) == 2**upper_power-upper,
                 "Saved upper margin differs")
        margin = lower-lower_power*hi2
        if v == 15:
            need(moment == 984 and cap == Q(29815, 1024), "Critical v15 data differ")
            need(margin > Q(1, 1250), "The exact v15 gap is not above 1/1250")
        rows.append({"selected_size": v+16, "edge_bound": edge,
                     "largest_eigenvalue_bound": str(cap),
                     "strict_powers": [lower_power, upper_power],
                     "remaining_exponents": remaining,
                     "log_margin_lower_bound": rational_floor(margin)})
    need([r["selected_size"] for r in rows] == list(range(24, 40)), "Size range is incomplete")
    excluded = [r["selected_size"] for r in rows if not r["remaining_exponents"]]
    need(excluded == [24, 25, 26, 28, 29, 30, 31] == receipt["excluded_selected_sizes"],
         "Exclusion list differs")
    return rows


def main():
    blobs = {name: pinned(PRODUCER/name, pin) for name, pin in PINS.items()}
    receipt = json.loads(blobs["SPECTRAL-BOUND.json"])
    need(receipt["status"] == "PASS_UNPAIRED_SPECTRAL_EXCLUSIONS", "Wrong source status")
    result = {"status": "PASS_INDEPENDENT_UNPAIRED_SPECTRAL_BOUND",
              "reviewed_pins": PINS, "interface_sha256": INTERFACE_PIN,
              "source_reconstruction": source_matrix(),
              "graph_cases": graph_cases(receipt["fifteen_root_edge_proof"]),
              "logarithm_terms": 64, "rows": spectral_cases(receipt),
              "critical_v15_log_margin_strictly_above": "1/1250",
              "general_selected_lower_bound": 27,
              "scope": "S contains the fixed A and T, and the selected baselines are retained.",
              "not_repeated": ["The million-vector split-pair enumeration"],
              "not_claimed": ["Existence at size 27", "A general centre-information lower bound",
                              "A native controller", "A supplier or kappa improvement"]}
    (HERE/"SPECTRAL-BOUND-REVIEW.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "general_selected_lower_bound": 27,
                      "critical_v15_gap": "> 1/1250"}))


if __name__ == "__main__":
    main()
