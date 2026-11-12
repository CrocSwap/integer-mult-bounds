"""Independent reverse exact rows for the eight frozen fixed-clock donor banks."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import lcm
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "97df4e628a30f516862ef8acc1862ddfabfee1806fe046446c473edc8b0de009",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "independent/reused/reverse_span.py": "f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
EVENTS, BANKS, SECONDS = 76466, 8, 20


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed input " + name)
    return raw


def legal_scalar(q):
    d = q.denominator
    return bool(q and not d & (d - 1) and d <= 2**25 and
                abs(q.numerator).bit_length() <= 24 and abs(q) + 1 < 2**16)


def backward(word, price, engine, deadline, progress):
    tape, n, owned = word["program"], word["public"], word["owned_fields"]
    assert (len(tape), n, owned) == (EVENTS, 1501, 68)
    chart = word["final"] + [None] * owned
    empty = ({}, 1)
    adjoint = [empty] * len(chart)
    sum_scaled, coefficient = engine["sum_scaled"], engine["coefficient"]
    demands = defaultdict(list)
    anchors = defaultdict(list)
    for spec in price["banks"]:
        demands[spec["key"][-1]].append(spec)
    for window in price["windows"]:
        f, g, h = window["key"]
        a, b, c = window["charts"]
        assert tape[f] == ["MOVE", h, a, b, False] and tape[g] == ["MOVE", h, b, c, False]
        anchors[h].append((f, g, {clock for clock, _ in window["original_pair"]}))
    captures, fresh_copy = {}, set()
    row_count = 0

    @cache
    def span(label):
        space = {0}
        for vector in word["frames"][label]:
            assert vector not in space
            space |= {v ^ vector for v in space}
        return space

    for window in price["windows"]:
        a, b, c = window["charts"]
        assert span(a) < span(b) < span(c)

    for t in range(len(tape) - 1, -1, -1):
        progress["last_unvisited"] = t
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse literal walk")
        op, d, *args = tape[t]
        assert 0 <= d < len(chart) and (d not in fresh_copy or op == "INIT")
        roles = (d, args[0]) if op in ("ADD", "COPY") else (d,)
        for role in roles:
            for f, g, allowed in anchors.get(role, ()):
                assert not f < t < g or t in allowed
        if op == "MOVE":
            old, new, is_owned = args
            assert chart[d] == new and is_owned == (d >= n)
            assert span(old) < span(new) or is_owned and span(new) < span(old)
            chart[d] = old
        elif op == "INIT":
            assert d >= n and chart[d] == args[0]
            chart[d] = None
            fresh_copy.discard(d)
            adjoint[d] = empty
        elif op == "CLEAR":
            assert d >= n and chart[d] is None
            chart[d] = args[0]
            adjoint[d] = empty
        else:
            assert op in ("ADD", "COPY", "SCALE") and chart[d] == args[-1]
            q = coefficient(args[-2])
            if op == "SCALE":
                adjoint[d] = sum_scaled(empty, adjoint[d], q)
            else:
                src = args[0]
                assert src != d and chart[src] == chart[d]
                adjoint[src] = sum_scaled(adjoint[src], adjoint[d], q)
                if op == "COPY":
                    assert d >= n
                    fresh_copy.add(d)
                    adjoint[d] = empty
        for spec in demands.get(t, ()):
            d0, s0 = spec["destination"], spec["source"]
            old, new = spec["old_coframe"], spec["new_coframe"]
            assert tape[t] == ["ADD", d0, s0, spec["coefficient"], old]
            assert 0 <= d0 < n and 0 <= s0 < n and chart[d0] == chart[s0] == old
            others = [r for r, f in enumerate(chart[:n]) if f == new and r not in (d0, s0)]
            omitted = [r for r in range(n, len(chart)) if chart[r] == new]
            ids = {}
            for role in (s0, d0, *others):
                ids[role] = row_count
                adjoint[role] = sum_scaled(adjoint[role], ({row_count: 1}, 1), (1, 1))
                row_count += 1
            captures[tuple(spec["key"])] = ids, others, omitted
        progress["events_checked"] += 1

    assert chart == word["initial"] + [None] * owned and not fresh_copy
    assert not any(vector for vector, _ in adjoint[n:])
    progress["last_unvisited"] = None
    by_row = [[] for _ in range(row_count)]
    for j, (weights, den) in enumerate(adjoint[:n]):
        for row_id, num in weights.items():
            by_row[row_id].append((j, num, den))
    rows = []
    for terms in by_row:
        den = lcm(*(d for _, _, d in terms))
        rows.append(engine["normalized"]({j: num * (den // d) for j, num, d in terms}, den))
    return captures, rows


def classify(spec, capture, rows, engine):
    ids, others, omitted = capture
    d, s = spec["destination"], spec["source"]
    bank = [(r, rows[ids[r]]) for r in (d, *others)]
    target = rows[ids[s]]
    proof = engine["exact_span"](bank, target)
    if proof["status"] == "absent_exterior_coordinate":
        proof["separating_covector"] = {proof["coordinate"]: "1"}
    status = "outside relaxed span"
    replacement = None
    if proof["status"] == "exact_span":
        alpha = Q(spec["coefficient"])
        weights = {r: alpha * Q(v) for r, v in proof["coefficients"].items()}
        lam = 1 + weights.pop(d, Q(0))
        status = "exact span, sparse format unresolved"
        if len(weights) <= 2 and legal_scalar(lam) and all(map(legal_scalar, weights.values())):
            status = "sparse dyadic witness"
            replacement = {"scale": str(lam), "add": {r: str(q) for r, q in weights.items()}}
            reconstruct = engine["sum_scaled"]
            actual = reconstruct(({}, 1), rows[ids[d]], (lam.numerator, lam.denominator))
            for role, weight in weights.items():
                actual = reconstruct(actual, rows[ids[role]], (weight.numerator, weight.denominator))
            expected = reconstruct(rows[ids[d]], target, (alpha.numerator, alpha.denominator))
            assert actual == expected
    return dict(key=spec["key"], chart=spec["new_coframe"], destination=d, source=s,
                public_donors=others, diagonal=d, omitted_owned=omitted,
                status=status, replacement=replacement, proof=proof)


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    root = args.root
    engine_name = "independent/reused/reverse_span.py"
    checked(root, engine_name)
    engine = run_path(str(root / engine_name))
    controls = engine["controls"]()
    assert legal_scalar(Q(-1, 2)) and not legal_scalar(Q(0)) and not legal_scalar(Q(1, 3))
    controls += ["nonzero retained dyadic scalar"]
    if args.controls_only:
        print(dumps({"controls": controls}, sort_keys=True))
        return 0
    price = loads(checked(root, "plan/PRICE.json"), object_pairs_hook=unique)
    assert price["limits"] == {"banks": BANKS, "events": EVENTS, "seconds": SECONDS, "windows": 4}
    assert len(price["banks"]) == BANKS
    keys = [p["key"] for p in price["banks"]]
    results, rows = [], []
    progress = {"events_checked": 0, "last_unvisited": EVENTS - 1}
    error = None

    def stop(*_):
        raise TimeoutError("20-second hard cap")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 2
    try:
        raw = decompress(checked(root, "inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest() == price["payload_sha256"]
        word = loads(raw, object_pairs_hook=unique)
        captures, rows = backward(word, price, engine, deadline, progress)
        for spec in price["banks"]:
            if monotonic() >= deadline:
                raise TimeoutError("bank support cap")
            results.append(classify(spec, captures[tuple(spec["key"])], rows, engine))
    except TimeoutError as exc:
        error = str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=price["head"], caller=price["caller"], pins=PINS,
        counts=dict(Counter(r["status"] for r in results)), results=results,
        limits=price["limits"], controls=controls, timeout=error, progress=progress,
        unvisited=keys[len(results):]), indent=2, sort_keys=True))
    return 2 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
