#!/usr/bin/env python3
"""Exact arithmetic for the conditional body-stock lemma; standard library only.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier is imported or executed.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = 269241600
Q = 15 * 2**78 + 1
CUTOFF = 245773


def require(condition, message):
    if not condition:
        raise ValueError(message)


def depth(n):
    require(type(n) is int and n >= 0, "nonnegative integer width required")
    result = 0
    while n >= 64:
        n = 42 * (n // 64)
        result += 1
    return result


def atom_width(e):
    """ceil(e**(17/10000)) using integer comparisons only."""
    require(type(e) is int and e >= 1, "positive integer original width required")
    target = e**17
    low, high = 1, 1 << ((17 * e.bit_length() + 9999) // 10000)
    while low < high:
        middle = (low + high) // 2
        if middle**10000 >= target:
            high = middle
        else:
            low = middle + 1
    return low


def upper(d, w):
    return 4096 * w * d + (29 * d + 79) // 80


def guard(e, k, w):
    return 0 <= 2 * k < e and k >= upper(depth((e - k) // w), w)


def choose_borrow(e):
    """Least conservative feasible k; the near-half witness only decides fit."""
    w = atom_width(e)
    maximum = (e - 1) // 2
    if not guard(e, maximum, w):
        return None
    low, high = 0, maximum
    while low < high:
        middle = (low + high) // 2
        if guard(e, middle, w):
            high = middle
        else:
            low = middle + 1
    k = low
    require(guard(e, k, w), "borrow witness fails")
    require(k == 0 or not guard(e, k - 1, w), "borrow witness is not least")
    require(k <= upper(depth(e), w), "lost logarithmic borrowing bound")
    return dict(e=e, w=w, k=k, n=(e-k)//w, depth=depth((e-k)//w))


def thresholds(count):
    values = [64]
    for _ in range(count - 1):
        values.append(64 * ((values[-1] + 41) // 42))
    return values


def authenticate(package):
    root = package.parent.parent
    sources = json.loads((package / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            data = (root / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"],
                    "live input SHA256 mismatch: " + item["path"])
    retained = sources["retained_sources"]
    require({x["path"] for x in retained} == {
        "sources/pr2234/PROOF.md", "sources/pr2234/NOTICE.md",
        "sources/pr2324/README.md"}, "retained source inventory mismatch")
    for item in retained:
        data = (package / item["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"],
                "retained source SHA256 mismatch: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["git_blob"], "retained Git blob mismatch")


def prime_certificate(q=Q, base=11):
    require(q == 15 * 2**78 + 1, "prime witness form changed")
    require(q > 2**80, "prime is outside the caller domain")
    require(pow(base, (q - 1)//2, q) == q - 1, "prime order witness failed")
    require((2**78 + 1)**2 > q, "prime-divisor size argument failed")
    return dict(q=q, base=base, power_of_two=78)


def exact_log_cell(d, j, q=Q):
    """Certify j < log_q(M**d * P(q)**d) < j+1, with P=prod(1-q**-i).

    Its dth power exceeds 1/2 when 2d<q-1. These inequalities avoid
    materializing the enormous group order. All callers have w=2.
    """
    require(2*d < q-1, "product lower bound failed")
    require(2*q**j < M**d < q**(j+1), "exact logarithm cell failed")
    return 8192*d + j + 1


def build_receipt():
    require(M < 2**29, "uniform packet bound failed")
    require(2*42**2 < 64**2, "two-level contraction failed")
    b = thresholds(22)
    intervals = []
    for d in range(15, 19):
        start = max(CUTOFF, 4*b[d-1]-2)
        end = min(2**20-1, 4*b[d]-3)
        u = upper(d, 2)
        margin = start - 2*u
        require(start <= end and margin > 0, "staircase interval fails strict fit")
        for e in (start, end):
            maximum = (e-1)//2
            require(atom_width(e) == 2, "wrong atom width in finite interval")
            require(depth((e-maximum)//2) == d, "body depth interval mismatch")
            require(guard(e, maximum, 2), "finite interval endpoint fails")
        intervals.append(dict(first=start, last=end, depth=d, upper=u, margin=margin))
    require(intervals[0]["first"] == CUTOFF and intervals[-1]["last"] == 2**20-1,
            "finite interval coverage incomplete")
    require(all(a["last"]+1 == z["first"] for a,z in zip(intervals, intervals[1:])),
            "finite interval coverage gap")
    # Constants in the written infinite dyadic-tail induction.
    require(2*21*17 < 10000 and 2*17 < 10000, "fractional exponent bound failed")
    require(2*4 < 9, "sqrt(2) < 3/2 failed")
    require(16388*21*3//2+1 == 516223 < 2**19, "tail base failed")
    require(11 < 14 and 14 <= 2*11, "tail contraction failed")

    prime = prime_certificate()
    k15, k16 = exact_log_cell(15, 5), exact_log_cell(16, 5)
    require(k15 == 122886 and k16 == 131078, "boundary stock cells changed")
    e = CUTOFF-1
    maximum = (e-1)//2
    require(atom_width(e) == 2 and depth((e-maximum)//2) == 15, "sharpness domain failed")
    require(maximum == 122885 < k15, "sharpness obstruction failed")
    require(choose_borrow(e) is None, "boundary incorrectly accepted")
    first = choose_borrow(CUTOFF)
    require(first["k"] == 122886, "first fitting witness changed")

    # Equality has no solution here; its least feasible inequality witness
    # borrows one digit more than the log ceiling of its resulting stock.
    jump_e = 273158
    require(depth((jump_e-k15)//2) == 16, "left jump depth changed")
    require(depth((jump_e-(k15+1))//2) == 15, "right jump depth changed")
    require(depth((jump_e-k16)//2) == 15, "two-cycle changed")
    jump = choose_borrow(jump_e)
    require(jump["k"] == k15+1, "least jump witness changed")

    probes = sorted({CUTOFF, jump_e, 300541, 300542, 457981, 457982,
                     698109, 698110, 2**20-1, 2**20, 2**40, 2**128,
                     2**588, 2**589, 3**588, 3**589})
    samples = [choose_borrow(width) for width in probes]
    require(all(x is not None for x in samples), "positive borrow probe failed")
    return dict(schema_version=1, scope="conditional body-stock fit; no new kappa",
                cutoff=CUTOFF, old_prescribed_stock_cutoff=311311,
                prime_certificate=prime, depth_thresholds=b, intervals=intervals,
                infinite_tail=dict(first_index=20, base_upper=516223,
                                   base_limit=524288, contraction=[11,14]),
                sharpness=dict(e=e, maximum_k=maximum, minimum_depth=15,
                               actual_required_k=k15),
                first_witness=first,
                no_fixed_point=dict(e=jump_e, cycle=[k15,k16],
                                    least_feasible_k=jump["k"], resulting_log_ceiling=k15),
                borrow_probes=samples)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=HERE)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    authenticate(package)
    receipt = build_receipt()
    if args.write_receipt:
        require(not args.write_receipt.resolve().is_relative_to(package),
                "use a new external receipt path")
        with args.write_receipt.open("x") as out:
            out.write(json.dumps(receipt, indent=2) + "\n")
    else:
        stored = json.loads((package / "RESULT.json").read_text())
        require(canonical(stored) == canonical(receipt), "stored receipt mismatch")
    print("PASS_BIT2234_BODY_STOCK cutoff=245773 boundary=245772 no_fixed_point=273158 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error))
