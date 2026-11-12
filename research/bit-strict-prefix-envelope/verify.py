"""Check retained strict-prefix separation on the literal eight-port BIT retag."""
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT / "research/paired-query-only-bit"
PINS = {
    "retained/inputs/BIT-NATIVE-WORD.json.gz": "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
    "EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "independent/interval_gate.py": "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
}
TRIAL = Fraction("0.004008162992724")


def checked(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return raw


def load(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def eliminate(rows):
    pivots = {}
    for vector in rows:
        row = list(map(Fraction, vector))
        for pivot, previous in sorted(pivots.items()):
            factor = row[pivot]
            row = [a - factor * b for a, b in zip(row, previous, strict=True)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            pivots[pivot] = tuple(x / row[pivot] for x in row)
    for pivot, row in sorted(pivots.items(), reverse=True):
        for earlier in (i for i in pivots if i < pivot):
            previous = pivots[earlier]
            pivots[earlier] = tuple(a - previous[pivot] * b for a, b in zip(previous, row, strict=True))
    return tuple(row for _, row in sorted(pivots.items()))


def geometry(word):
    frames = {}
    ranks = {}
    canonical = {}
    names = {}
    for f, entry in sorted((int(k), v) for k, v in word["frames"].items()):
        head = eliminate(entry["B"])
        tail = eliminate(entry["A"])
        rank = entry["dim"]
        assert len(head) == rank and len(tail) == 8 - rank
        assert all(len(x) == 8 for x in head + tail)
        assert all(sum(a * b for a, b in zip(x, y, strict=True)) == 0 for x in head for y in tail)
        ranks[f], frames[f] = rank, (head, tail)
        canonical[f] = names.setdefault(head, f)
    return frames, ranks, canonical


def trace(word, origin, adjusted, frames, ranks, canonical):
    public, owned = word["public"], word["owned_fields"]
    charts = [*word["start"], *([None] * owned)]
    rows = [*(1 << i for i in range(public)), *([0] * owned)]
    cache = defaultdict(dict)
    sites, pending = [], {}
    paid, nesting = Counter(), {}
    active = peak = erasures = 0

    def observe(role, cut):
        chart, row = charts[role], rows[role]
        if chart is not None and row:
            cache[canonical[chart]].setdefault(row, cut)

    for role in range(len(rows)):
        observe(role, 0)
    for cut, (old_event, event) in enumerate(zip(origin, word["program"], strict=True)):
        op, role, *args = event
        touched = event[1:3] if op in ("ADD", "SWAP") else event[1:2]
        for owner in touched:
            if owner in pending:
                pending.pop(owner)["due"] = cut
        if op == "ADD":
            donor, chart = args
            assert charts[role] == charts[donor] == chart
            rows[role] ^= rows[donor]
        elif op == "SWAP":
            other, = args
            charts[role], charts[other] = charts[other], charts[role]
            rows[role], rows[other] = rows[other], rows[role]
            observe(other, cut + 1)
        elif op == "INIT":
            assert role >= public and charts[role] is None and not rows[role]
            charts[role] = args[0]
            active += 1
            peak = max(peak, active)
        elif op == "CLEAR":
            assert role >= public and charts[role] == args[0]
            charts[role], rows[role] = None, 0
            active -= 1
            erasures += 1
        else:
            source, target = args
            assert op == "MOVE" and charts[role] == source
            smaller, larger = sorted(args, key=ranks.__getitem__)
            if (smaller, larger) not in nesting:
                nesting[smaller, larger] = all(
                    sum(a * b for a, b in zip(x, y, strict=True)) == 0
                    for x in frames[smaller][0] for y in frames[larger][1])
            delta = ranks[larger] - ranks[smaller]
            assert delta > 0 and nesting[smaller, larger]
            paid[delta] += 1
            if old_event in adjusted:
                assert source == 0 and rows[role]
                site = {"event": old_event, "target_chart": canonical[target],
                        "target_row": rows[role], "due": len(origin)}
                sites.append(site)
                pending[role] = site
            charts[role] = target
        observe(role, cut + 1)
    assert charts == [*word["final"], *([None] * owned)] and active == 0
    assert rows[:public] == [(1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0) for i in range(public)]
    assert (peak, erasures) == (237, 237)
    return paid, sites, cache


def decode_duals(entries):
    result = {}
    for *ids, coordinates in entries:
        key = tuple(ids)
        assert key not in result
        assert coordinates == sorted(set(coordinates)) and all(0 <= j < 659 for j in coordinates)
        result[key] = sum(1 << j for j in coordinates)
    return result


def separates(dual, target, rows):
    return (dual & target).bit_count() % 2 == 1 and all((dual & row).bit_count() % 2 == 0 for row in rows)


def support_check(sites, cache, frames, ranks, canonical, certificate):
    explicit = decode_duals(certificate["explicit"])
    aggregate = decode_duals(certificate["aggregate"])
    checked = Counter()
    for site in sites:
        event, target, due, target_row = (site[k] for k in ("event", "target_chart", "due", "target_row"))
        for chart, rep in canonical.items():
            if chart != rep or not 0 < ranks[chart] < ranks[target]:
                continue
            if not all(sum(a * b for a, b in zip(x, y, strict=True)) == 0
                       for x in frames[chart][0] for y in frames[target][1]):
                continue
            rows = [row for row, cut in cache[chart].items() if cut <= due]
            if not rows:
                checked["empty"] += 1
                continue
            key = (event, chart)
            if key in explicit:
                dual = explicit.pop(key)
                checked["explicit"] += 1
            else:
                dual = aggregate[event,]
                checked["aggregate_cases"] += 1
                checked[event] += 1
            if not separates(dual, target_row, rows):
                raise ValueError(f"Invalid separator for event {event}, chart {chart}")
    assert not explicit and set(aggregate) == {(event,) for event in checked if isinstance(event, int)}
    assert {k: checked[k] for k in ("empty", "explicit", "aggregate_cases")} == {
        "empty": 79, "explicit": 512, "aggregate_cases": 382}
    assert len(aggregate) == 24
    return {"empty": 79, "explicit": 512, "aggregate_cases": 382, "aggregate_recipients": 24}


def price(gate, invoice, old, new):
    assert old == {int(r): n for r, n in invoice["native_paid"].items()}
    delta = {r: new[r] - old[r] for r in new.keys() | old.keys() if new[r] != old[r]}
    assert delta == {1: -48, 2: 21, 3: -6, 4: 6, 6: -8, 7: 8}
    paid = {int(r): n for r, n in invoice["paid"].items()}
    targets = {int(r): n for r, n in invoice["targets"].items()}
    raw_allowance = gate.add(gate.exact(111), gate.sub(gate.moment(targets, TRIAL), gate.moment(paid, TRIAL)))
    cost = gate.moment(delta, TRIAL)
    allowance = gate.div(raw_allowance, gate.exact(18))
    excess = gate.sub(cost, allowance)
    assert excess[0] > 0
    return {"trial": str(TRIAL), "delta": delta, "cost": gate.show(cost),
            "conditional_allowance": gate.show(allowance), "excess": gate.show(excess)}


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    assert separates(4, 5, [1, 2]) and not separates(4, 5, [1, 2, 4])
    assert not separates(1, 2, [4])
    data = {k: checked(BIT / k, digest) for k, digest in PINS.items()}
    word = json.loads(gzip.decompress(data["retained/inputs/BIT-NATIVE-WORD.json.gz"]))
    invoice = json.loads(data["EFREE-RESULT.json"])
    gate = load(BIT / "independent/interval_gate.py")
    rewrite = load(HERE / "retag.py")
    certificate = json.loads((HERE / "CERT.json").read_text(encoding="utf-8"))
    frames, ranks, canonical = geometry(word)
    changed, origin, adjusted, _ = rewrite.retag(word, rewrite.modules(word))
    old_paid, _, _ = trace(word, range(len(word["program"])), {}, frames, ranks, canonical)
    new_paid, sites, cache = trace(changed, origin, adjusted, frames, ranks, canonical)
    assert len(sites) == len(adjusted) == 35
    assert next(row for row in sites if row["event"] == 19234)["target_row"] == (1 << 5) | (1 << 235)
    support = support_check(sites, cache, frames, ranks, canonical, certificate)
    receipt = {"support": support, "sites": 35, "available_strict_donor_credit": [0, 0],
               "price": price(gate, invoice, old_paid, new_paid)}
    expected = HERE / "RESULT.json"
    assert json.loads(expected.read_text(encoding="utf-8")) == json.loads(json.dumps(receipt))
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print("PASS_BIT_STRICT_PREFIX_ENVELOPE sites=35 explicit=512 aggregate=382 no_new_kappa")


if __name__ == "__main__":
    main()
