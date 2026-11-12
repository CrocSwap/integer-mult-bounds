"""Test the two fixed public endpoint banks for the literal role-532 aggregate."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R130-PRICE.json": "d9074aad58d3ffdad995ba68b2ffa541ae2b7df833b757d8e1a9767118140f39",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}
ROLE = 532
BANKS = ((44611, 3, ROLE), (44612, 207, ROLE))
SOURCES = ((41177, 363, Q(1), 744), (41179, 452, Q(-2), 746))


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def invoice():
    old = loads(read("inputs/R130-PRICE.json"), object_pairs_hook=unique)
    assert old["head"] == HEAD and old["caller"] == CALLER
    assert old["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
    by_role = {p["role"]: p for p in old["candidates"] if all(e[1] == p["role"] for _, e in p["contacts"])}
    assert set(by_role) == {198, ROLE}
    lead = by_role[ROLE]
    assert lead["clocks"] == [41176, 41178, 44611] and lead["charts"] == [3, 744, 746, 207]
    assert lead["contacts"] == [[t, ["ADD", ROLE, s, str(q), c]] for t, s, q, c in SOURCES]
    assert lead["paid_delta"] == {"2": -17, "3": -34, "8": 17}
    assert 0 < Q(lead["probe_lower"]) <= Q(lead["raw_upper"]) < 1
    return dict(head=HEAD, caller=CALLER, pins=PINS, candidate=lead,
                compatible_cap=2, gross_upper=str(sum(Q(p["raw_upper"]) for p in by_role.values())),
                paid=old["after_paid_one"], productive=old["productive"], surplus=old["surplus"],
                selected_banks=[list(k) for k in BANKS], unresolved_role198=[42533,42599,44596])


def exact_span(target, bank, deadline, helpers):
    absent = set(target).difference(*(row.keys() for row in bank.values()))
    if absent:
        i = min(absent)
        return dict(decision="outside donor span", separator={i: "1"}, separator_value=str(target[i]),
                    absent_coordinates=sorted(absent))
    # Row elimination, then transpose the reduction onto one nonzero residual coordinate.
    axpy = helpers["axpy"]
    basis = {}
    for role, vector in sorted(bank.items()):
        if monotonic() >= deadline:
            return None
        row, weights = vector.copy(), {role: Q(1)}
        helpers["reduce_row"](row, basis, weights, -1)
        if row:
            i = min(row)
            factor = row[i]
            basis[i] = ({j: a / factor for j, a in row.items()}, {j: a / factor for j, a in weights.items()})
    row, weights = target.copy(), {}
    helpers["reduce_row"](row, basis, weights, 1)
    if not row:
        check = {}
        for role, q in weights.items():
            axpy(check, bank[role], q)
        assert check == target
        return dict(decision="exact span survivor", rank=len(basis),
                    coefficients={i: str(q) for i, q in weights.items()})
    i = min(row)
    dual = {i: Q(1)}
    for pivot, (vector, _) in sorted(basis.items(), reverse=True):
        value = sum(q * dual.get(j, 0) for j, q in vector.items())
        if value:
            dual[pivot] = dual.get(pivot, 0) - value
            if not dual[pivot]:
                del dual[pivot]
    def dot(vector):
        return sum(q * vector.get(j, 0) for j, q in dual.items())
    assert all(dot(v) == 0 for v in bank.values()) and dot(target) == row[i]
    return dict(decision="outside donor span", rank=len(basis),
                separator={j: str(q) for j, q in dual.items()}, separator_value=str(dot(target)))


def controls(helpers):
    d = monotonic() + 1
    bank = {7: {0: Q(1), 1: Q(1)}, 8: {1: Q(2)}}
    assert exact_span({0: Q(3)}, bank, d, helpers)["coefficients"] == {7: "3", 8: "-3/2"}
    assert exact_span({0: Q(3), 2: Q(1)}, bank, d, helpers)["separator"] == {2: "1"}
    covector = exact_span({0: Q(1)}, {7: bank[7]}, d, helpers)
    assert covector["separator"] == {0: "-1", 1: "1"} and covector["separator_value"] == "-1"
    return ["two donor exact aggregate", "exterior-coordinate perturbation", "same-support covector separation"]


def main():
    assert __debug__
    price = invoice()
    if sys.argv[1:] == ["--price-only"]:
        print(dumps(price, sort_keys=True, indent=2))
        return
    assert not sys.argv[1:]
    deadline = monotonic() + 18
    read("inputs/donor_span.py")
    helpers = run_path(str(ROOT / "inputs/donor_span.py"))
    control = controls(helpers)
    raw = decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    program = word["program"]
    assert len(program) == 76466
    paid = price["candidate"]
    a, b, c = paid["clocks"]
    charts = paid["charts"]
    assert [program[t] for t in (a, b, c)] == [
        ["MOVE", ROLE, x, y, False] for x, y in zip(charts[:-1], charts[1:], strict=True)
    ]
    selected = set()
    for t in range(a + 1, c):
        if t == b:
            continue
        e = program[t]
        if ROLE in (e[1:3] if e[0] in {"ADD", "COPY"} else e[1:2]):
            selected.add(t)
    assert selected == {t for t, *_ in SOURCES}
    assert all(program[t] == ["ADD", ROLE, s, str(q), chart] for t, s, q, chart in SOURCES)
    req = {cut: {(chart, role)} for cut, chart, role in BANKS}
    refs = {t: {s} for t, s, *_ in SOURCES}
    banks, values = helpers["snapshot"](word, req, refs, deadline)
    rows, aggregate = [], {}
    if all((t, s) in values for t, s, *_ in SOURCES):
        for t, s, q, _ in SOURCES:
            helpers["axpy"](aggregate, values[t, s], q)
        for key in BANKS:
            if key not in banks or monotonic() >= deadline:
                break
            bank = {i: row for i, row in banks[key].items() if i < word["public"]}
            result = exact_span(aggregate, bank, deadline, helpers)
            if result is None:
                break
            rows.append(dict(key=list(key), bank_roles=sorted(bank), **result))
    unvisited = [list(k) for k in BANKS[len(rows):]]
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, price=price,
                    aggregate={i: str(a) for i, a in aggregate.items()},
                    controls=control, rows=rows, unvisited=unvisited,
                    role198_status="outside this two-bank scope"), sort_keys=True, indent=2))
    if unvisited:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
