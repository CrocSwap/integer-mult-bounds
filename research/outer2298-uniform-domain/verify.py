#!/usr/bin/env python3
"""Exact certificates for the stated PR2298 parameter tail, not its callees."""
import argparse
import ast
import hashlib
import json
from math import isqrt
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CUTOFF = 524288
HEAD = "8507498d363735ced0b0a3f02d5ecf80ed3e3805"
BINDINGS = {
    "p": "6 * b", "d": "floor_root(p, 40)", "K": "floor_root(d, 500)",
    "ell": "(log_T + d - 1) // d", "alpha4": "12 * d * d * b",
    "gamma": "2 * d * alpha * alpha", "G": "4 * p.bit_length() + 6",
    "H": "d * G", "q0": "2642 * 2 * d.bit_length()",
    "Q0": "q0 + (2 * H + K - 1) // K + (H + K - 1) // K",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_bindings(data):
    tree = ast.parse(data)
    function = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "compressed_domains")
    assignments = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                assignments[node.targets[0].id] = ast.dump(node.value)
    for name, expression in BINDINGS.items():
        expected = ast.dump(ast.parse(expression, mode="eval").body)
        need(assignments.get(name) == expected, "source formula: " + name)
    return sorted(BINDINGS)


def digest_check(data, expected):
    need(hashlib.sha256(data).hexdigest() == expected, "source hash")


def authenticate():
    source = json.loads((PACKAGE / "SOURCES.json").read_text())["audited_source"]
    need(source["commit"] == HEAD and source["pr"] == 2298, "audited head")
    need({x["local_path"] for x in source["files"]} ==
         {"source/PR2298-PROOF.md", "source/PR2298-checks.py"}, "source inventory")
    for item in source["files"]:
        data = (PACKAGE / item["local_path"]).read_bytes()
        digest_check(data, item["sha256"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
    data = (PACKAGE / "source/PR2298-checks.py").read_bytes()
    return data, source_bindings(data)


def exponential_tail(start, slope, intercept, label):
    """Certify 2^j > slope*j+intercept for all integers j >= start.

    Doubling the linear bound exceeds its next value by
    slope*j+intercept-slope, a nondecreasing affine expression.
    """
    right = slope * start + intercept
    difference = right - slope
    need(start >= 0 and slope >= 0, label + ": induction domain")
    need((1 << start) > right, label + ": base")
    need(difference >= 0, label + ": induction")
    return {"start": start, "slope": slope, "intercept": intercept,
            "right_at_start": right, "induction_difference_at_start": difference}


def tail_certificate(cutoff=CUTOFF, guard=210000, chunk_factor=16):
    # s=floor(log2(p)); t=floor(s/40); u=floor(s/20000).
    t, u = cutoff // 40, cutoff // 20000
    need(39 * cutoff >= 40 * (guard + 2), "guard tail")
    need(t >= 3, "dimension at least eight")
    need(19 * cutoff >= 20 * 10, "prime room quadratic tail")
    need(19499 * cutoff > 20000 * 6, "chunk below record length")
    need(39 * cutoff >= 40 * 4, "dimension below b")
    need(8**20 > 6 * 7**20, "Gaussian constant")
    need(9 * cutoff >= 140, "Gaussian gamma tail")
    # b^4 <= 2^b for b>=16; 896*b < 2^(3*b/4) for b>=32.
    need(16**4 == 2**16 and 17**4 < 2 * 16**4, "recovery induction")
    need(896 < 2**10 and 32 > 20, "recovery strict margin")
    return {
        "log2_b_cutoff": cutoff, "conservative_s_cutoff": cutoff,
        "guard_margin_integer": 39 * cutoff - 40 * (guard + 2),
        "prime_room_margin_integer": 19 * cutoff - 200,
        "chunk_length_margin_integer": 19499 * cutoff - 120000,
        "chunk": exponential_tail(u, chunk_factor * 80000,
                                  chunk_factor * 80006, "chunk tail"),
        "row": exponential_tail(t, 16 * 5284, 16 * 5284, "row tail"),
        "prime_log": exponential_tail(t, 42, 44, "prime logarithm tail"),
        "reserve_upper_bound": "Q0 < d/4 + 2 < d-1",
        "guard_upper_bound": "2^210000*d < p/2",
        "gamma_upper_bound": "gamma < b/4",
        "recovery_bound": "448*b*2^(-b+gamma) < 1/2",
    }


def root500(n):
    # Independent bisection on a small root; PR2298 uses Newton iteration.
    low, high = 0, 1 << ((n.bit_length() + 499) // 500)
    while high - low > 1:
        mid = (low + high) // 2
        if mid**500 <= n:
            low = mid
        else:
            high = mid
    need(low**500 <= n < (low + 1)**500, "root500 certificate")
    return low


def fixture(t, offset):
    # Never construct n, T, or r. Only their logarithmic descriptions fit.
    exponent = 40 * t
    p = (1 << exponent) + offset
    b = p // 6
    need(6 * b == p and b >= 1 << CUTOFF, "fixture domain")
    d = (1 << t) - int(offset < 0)
    need(d**40 <= p < (d + 1)**40, "dimension root certificate")
    k = root500(d)
    g = 4 * p.bit_length() + 6
    h = d * g
    q0 = 5284 * d.bit_length()
    reserve = q0 + (2 * h + k - 1) // k + (h + k - 1) // k
    alpha4 = 12 * d * d * b
    lower_alpha = isqrt(isqrt(alpha4))
    alpha = lower_alpha + int(lower_alpha**4 != alpha4)
    need((alpha - 1)**4 < alpha4 <= alpha**4, "alpha ceiling certificate")
    gamma = 2 * d * alpha * alpha
    need(k >= 16 * g and 16 * q0 <= d, "chunk and row bounds")
    need(4 * reserve < d + 8 and reserve < d - 1, "reserve bound")
    need(2 * (d << 210000) < p, "guard bound")
    need(4 * gamma < b and alpha * alpha < p and alpha >= 2, "Gaussian bounds")
    low = (b + 1) // 2
    boundary = ((low + d - 1) // d) * d
    lengths = sorted({x for x in (low, b, boundary - 1, boundary, boundary + 1)
                      if low <= x <= b})
    for length in lengths:
        ell = (length + d - 1) // d
        need(0 <= d * ell - length < d, "short-axis count")
        need(p <= 12 * d * ell <= 4 * p, "record bands")
        need(1 <= k <= ell - 1 and k > p.bit_length(), "chunk domain")
        need(ell < p, "ring length exponent")
        need(ell - 1 > 16 * d, "prime room exponential condition")
        need(ell - 1 > 3 + 2 * d.bit_length() + ell.bit_length(),
             "prime room logarithmic condition")
    gap = reserve - q0 - 3 * h // k
    row = {"p": {"power_of_two": exponent, "offset": offset},
           "b_bits": b.bit_length(), "d_bits": d.bit_length(), "K": k,
           "G": g, "alpha_bits": alpha.bit_length(), "gamma_bits": gamma.bit_length(),
           "length_cases": len(lengths), "ceiling_gap_above_floor": gap}
    return row, {"s": p.bit_length() - 1, "d": d, "K": k, "G": g,
                 "reserve": reserve, "q0": q0, "H": h, "ceiling_gap": gap}


def rejected(label, action, message):
    try:
        action()
    except ValueError as exc:
        need(message in str(exc), label + ": unexpected rejection")
        return label
    raise ValueError(label + ": false variant accepted")


def run():
    source, bindings = authenticate()
    certificate = tail_certificate()
    rows, internal = [], []
    for t, offset in ((13108, 2), (13500, -4), (13500, 2)):
        row, values = fixture(t, offset)
        rows.append(row)
        internal.append(values)
    regular, before, after = internal
    need(before["K"] == (1 << 27) - 1 and after["K"] == 1 << 27,
         "simultaneous floor discontinuity")
    need(regular["ceiling_gap"] > 0, "nonzero ceiling control")
    controls = [
        rejected("low cutoff cannot pay guard", lambda: tail_certificate(40), "guard tail"),
        rejected("larger guard is not certified", lambda: tail_certificate(guard=600000), "guard tail"),
        rejected("ceil dimension bin overstates d", lambda: need(
            before["d"] >= 1 << ((before["s"] + 39) // 40), "wrong d lower bound"),
            "wrong d lower bound"),
        rejected("ceil chunk bin overstates K", lambda: need(
            before["K"] >= 1 << ((before["s"] + 19999) // 20000), "wrong K lower bound"),
            "wrong K lower bound"),
        rejected("floor-only reserve omits axes", lambda: need(
            regular["reserve"] <= regular["q0"] + 3 * regular["H"] // regular["K"],
            "underallocated reserve"), "underallocated reserve"),
        rejected("stronger chunk factor has a counterexample", lambda: need(
            regular["K"] >= 64 * regular["G"], "false chunk factor"), "false chunk factor"),
        rejected("stronger chunk factor fails tail certificate",
                 lambda: tail_certificate(chunk_factor=64), "chunk tail: base"),
        rejected("changed dimension exponent breaks source binding", lambda: source_bindings(
            source.replace(b"d = floor_root(p, 40)", b"d = floor_root(p, 39)")), "source formula: d"),
        rejected("source byte corruption", lambda: digest_check(
            source + b"\n", hashlib.sha256(source).hexdigest()), "source hash"),
    ]
    need(2**40 <= 6 * 2**40 < 3**40 and (2 << 210000) > 6 * 2**40,
         "low cutoff guard counterexample")
    return {"schema_version": 1, "source_pr": 2298, "source_head": HEAD,
            "source_formula_bindings": bindings, "tail_certificate": certificate,
            "compressed_boundary_fixtures": rows, "negative_controls": controls,
            "scope": "Written uniform parameter-domain lemma with exact endpoint and induction certificates. No full callee, tape, Gaussian or multiplication proof; no new kappa."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((PACKAGE / "RESULT.json").read_text()), "complete receipt")
        print("PASS_OUTER2298_UNIFORM_DOMAIN cutoff_log2_b=524288 fixtures=3 controls=9 no_new_kappa")
