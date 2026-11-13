"""Reverse both Type B endpoints and independently census every admissible mask at every cut."""
import argparse
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

HERE = Path(__file__).resolve().parent
ENGINE = "4e00ed5107d96a005c3b11f98e2585bcf622b33b7ef3f05afcffdd33055c2024"
TOTAL = 4784
CAP = 30
STAGES = 17
Q_EVEN_SIGNS = ((1, "plus"), (-1, "minus"))


def admissible(key):
    parity, exponents = key
    return parity in (0, 1) and 0 < sum(exponents) < STAGES and all(x in (0, 1) for x in exponents)


def encode(key):
    parity, exponents = key
    assert admissible(key)
    return [list(j for j, p in enumerate(exponents, 1) if p), parity]


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def check_sector(entries, source, kit):
    # Exact Gram of each body/parity class and full set, computed from Gaussian rows.
    # Delete a class by subtracting its Gram, not by searching a selected base minor.
    Q, multiply, conjugate, add, subtract, ZERO = (kit[n] for n in (
        "Q", "multiply", "conjugate", "add", "subtract", "ZERO"
    ))
    grams = {}
    total = (ZERO, ZERO, ZERO)
    for (_role, parity, exponents), (a, b) in entries.items():
        term = multiply(conjugate(a), a), multiply(conjugate(a), b), multiply(conjugate(b), b)
        total = tuple(add(x, y) for x, y in zip(total, term, strict=True))
        key = parity, exponents
        if admissible(key):
            prior = grams.get(key, (ZERO, ZERO, ZERO))
            grams[key] = tuple(add(x, y) for x, y in zip(prior, term, strict=True))

    def determinant(x):
        a, b, d = x
        out = subtract(multiply(a, d), multiply(conjugate(b), b))
        assert out[1] == 0 and out[0] >= 0
        return out[0]

    def verify_minor(record, removed=None):
        keys = [(r, p, kit["mask"](m)) for ((m, p), r) in record["keys"]]
        assert len(keys) == len(set(keys)) == 2
        assert removed is None or all(k[1:] != removed for k in keys)
        rows = tuple(entries[k] for k in keys)
        expected = tuple(tuple(tuple(Q(v) for v in pair) for pair in row) for row in record["rows"])
        assert rows == expected
        (a, b), (c, d) = rows
        assert subtract(multiply(a, d), multiply(b, c)) == tuple(Q(v) for v in record["determinant"]) != ZERO

    base = determinant(total)
    assert base > 0
    verify_minor(source["base_minor"])
    survivors = []
    rank_twos = 0
    for key, part in sorted(grams.items()):
        residual = tuple(subtract(x, y) for x, y in zip(total, part, strict=True))
        if determinant(residual):
            rank_twos += 1
        else:
            survivors.append(encode(key))
    assert sorted(survivors) == sorted(key for key, _ in source["survivors"])
    for key, record in source["rejected"]:
        stages, parity = key
        verify_minor(record, (parity, kit["mask"](stages)))
    return {
        "nonzero_admissible_classes": len(grams), "rank_twos_after_deletion": rank_twos,
        "survivors": survivors, "nonzero_coefficient_rows": len(entries),
        "base_gram_determinant": base,
    }


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    parser.add_argument("--cap-seconds", type=int, choices=(30, 120), default=CAP)
    args = parser.parse_args()
    started = perf_counter()
    last = TOTAL

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", last_completed_cut=last if last < TOTAL else None,
             remaining_reverse_cuts=last, cap_seconds=args.cap_seconds, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(args.cap_seconds)
    engine = HERE / "check_type_b_reverse.py"
    assert sha256(engine.read_bytes()).hexdigest() == ENGINE
    kit = run_path(str(engine))
    pins = kit["PINS"]
    inputs = {p: (args.root / p).read_bytes() for p in pins}
    assert {p: sha256(raw).hexdigest() for p, raw in inputs.items()} == pins
    caller = loads(inputs["inputs/7113-CALLER.json"], object_pairs_hook=kit["unique_pairs"])
    app = loads(inputs["inputs/7481-APPLICATION.json"], object_pairs_hook=kit["unique_pairs"])
    assert app["caller_sha256"] == pins["inputs/7113-CALLER.json"] and app["caller_head"] == kit["CALLER"]
    assert app["claim_decimal"] == "0.003647081039689"
    tape = caller["events"]
    kind = caller["types"]["B"]
    assert caller["roles"] == 72 and caller["stages"] == STAGES and len(tape) + 1 == TOTAL
    assert kind["offset"] == 36 and kind["roles"] == 36
    assert kind["ports"] == [15, 17, 27, 34, 35, 42, 47, 55]
    assert kind["diagonal"][:2] == [[-1, 0] + [1] * STAGES] * 2
    kit["controls"](tape)
    lead_raw = args.lead_receipt.read_bytes()
    assert sha256(lead_raw).hexdigest() == args.lead_sha256
    header, *lead_rows, footer = [loads(raw, object_pairs_hook=kit["unique_pairs"]) for raw in lead_raw.splitlines()]
    assert header["status"] == "START" and header["total_cut_cap"] == TOTAL
    assert footer["status"] == "PASS_FIXED_CLASS_CENSUS" and footer["cuts_tested"] == TOTAL
    assert footer["exact_original_endpoints"] and footer["survivors"] == []
    assert [row["cut"] for row in lead_rows] == list(range(TOTAL))
    unit, roots, q = kit["unit"], kit["ROOTS"], kit["Q"]
    columns = {sign: [unit(role, 1, kit["END_MASK"], (q(sign), q(0))) for role in roots]
               for sign, _ in Q_EVEN_SIGNS}
    counts = {label: Counter() for _, label in Q_EVEN_SIGNS}
    transcript = sha256()
    for cut in range(TOTAL - 1, -1, -1):
        summary = {}
        for sign, label in Q_EVEN_SIGNS:
            entries = kit["coefficients"](columns[sign])
            data = check_sector(entries, lead_rows[cut][label], kit)
            assert data["rank_twos_after_deletion"] == data["nonzero_admissible_classes"]
            assert not data["survivors"]
            summary[label] = data
            counts[label].update({k: v for k, v in data.items() if type(v) is int})
            if cut:
                for col in columns[sign]:
                    kit["trans"](col, tape[cut - 1], sign, inverse=True)
        transcript.update((dumps({"cut": cut, **summary}, sort_keys=True, default=str) + "\n").encode())
        last = cut
    for sign, _ in Q_EVEN_SIGNS:
        for role, col in zip(roots, columns[sign], strict=True):
            assert col == unit(role, 0, kit["UNIT_MASK"], kit["ONE"])
    conceptual = TOTAL * 2 * (2**STAGES - 2)
    emit(status="PASS_INDEPENDENT_ALL_CUTS_ALL_MASKS", cuts_tested=TOTAL,
         sector_cut_counts=counts, admissible_classes_per_cut=2 * (2**STAGES - 2),
         conceptual_cases=conceptual, original_endpoints_both_sectors=True,
         survivors=[], unresolved=[], transcript_sha256=transcript.hexdigest(),
         input_pins=pins | {"independent/check_type_b_reverse.py": ENGINE},
         lead_sha256=args.lead_sha256, cap_seconds=args.cap_seconds, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
