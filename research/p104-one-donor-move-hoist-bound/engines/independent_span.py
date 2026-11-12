"""Independent full-source symbolic forward check of 13 changed-donor spans."""
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import gcd, lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/GEOMETRY.json": "d1319c5df9f1f9227c8d364447834a8d54d60ff25bbb1890f9754672bbfb22c0",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-LEAD.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CUTS, PAIRS, SECONDS = 8, 13, 35
EMPTY = ({}, 1)


def unique(items):
    data = dict(items)
    assert len(data) == len(items), "duplicate key"
    return data


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    if path.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def stop(*_):
    raise TimeoutError("35-second full-source cap")


@cache
def coefficient(text):
    q = Fraction(text)
    assert q
    return q.numerator, q.denominator


def add_scaled(old, source, factor):
    a, da = old
    b, db = source
    if not b:
        return old
    num, den = factor
    d = lcm(da, db * den)
    a_factor, b_factor = d // da, num * (d // (db * den))
    out = a.copy() if a_factor == 1 else {j: v * a_factor for j, v in a.items()}
    for j, b_j in b.items():
        val = out.get(j, 0) + b_factor * b_j
        if val:
            out[j] = val
        else:
            out.pop(j, None)
    g = gcd(d, *out.values()) if d != 1 else 1
    if g != 1:
        out = {j: v // g for j, v in out.items()}
    return out, d // g


def eliminate(row, basis):
    residual = row.copy()
    for pivot, body in sorted(basis.items()):
        scale = residual.get(pivot, 0)
        if scale:
            for j, v in body.items():
                val = residual.get(j, 0) - scale * v
                if val:
                    residual[j] = val
                else:
                    residual.pop(j, None)
    return residual


def dot(row, vector):
    integers, denom = row
    return sum((v * integers.get(j, 0) for j, v in vector.items()), Fraction(0)) / denom


def separate(owner, donors):
    basis = {}
    for integers, _ in donors:
        residual = eliminate(integers, basis)
        if residual:
            pivot = min(residual)
            val = residual[pivot]
            basis[pivot] = {j: Fraction(v) / val for j, v in residual.items()}
    residual = eliminate(owner[0], basis)
    if not residual:
        return len(basis), None, None
    vector = {min(residual): Fraction(1)}
    for pivot, row in sorted(basis.items(), reverse=True):
        v = -sum((x * vector.get(j, 0) for j, x in row.items()), Fraction(0))
        if v:
            vector[pivot] = v
    separation = dot(owner, vector)
    assert separation and all(dot(r, vector) == 0 for r in donors)
    return len(basis), vector, separation


def controls():
    unit = ({0: 1}, 1)
    assert add_scaled(unit, unit, (-1, 1)) == EMPTY
    assert add_scaled(unit, ({1: 2}, 3), (1, 2)) == ({0: 3, 1: 1}, 3)
    donated = (({0: 2, 1: 1}, 3), ({1: 2, 2: 1}, 4))
    matching = add_scaled(donated[0], donated[1], (-2, 3))
    assert separate(matching, donated) == (2, None, None)
    rank, vector, value = separate(unit, donated)
    assert rank == 2 and value and not dot(donated[0], vector) and not dot(donated[1], vector)
    assert dot(unit, vector)
    return ["mixed denominator update", "known member stays viable", "augmented separator rejects",
            "owner substituted for donor breaks the separator"]


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    chosen, results, expected, visited, capped = {}, [], set(), 0, False
    geometry = {}
    try:
        geometry = read("inputs/GEOMETRY.json")
        chosen = {r["clock"]: r for r in geometry["records"] if r["candidates"]}
        expected = {(k, r["owner"], d[0]) for k, r in chosen.items() for d in r["candidates"]}
        assert len(chosen) == CUTS and len(expected) == PAIRS
        old, word = read("inputs/R137-LEAD.json"), read("inputs/7334-WORD.json.gz")
        assert (geometry["head"], geometry["caller"]) == (old["head"], old["caller"])
        old_cuts = {r["move_clock"]: r for r in old["records"]}
        n, m, tape = (word[k] for k in ("public", "owned_fields", "program"))
        assert (n, m, len(tape)) == (1501, 68, 76466)
        states = word["initial"] + [None] * m
        rows = [({j: 1}, 1) for j in range(n)] + [EMPTY] * m
        fresh = set()
        for clock, (op, dst, *args) in enumerate(tape[:max(chosen) + 1]):
            visited = clock + 1
            if clock in chosen:
                r, prior = chosen[clock], old_cuts[clock]
                assert dst == r["owner"] and [op, *args] == ["MOVE", r["from_chart"], r["to_chart"], True]
                bank = [j for j, chart in enumerate(states) if j != dst and chart == r["to_chart"]]
                assert bank == r["unchanged_target_bank"]
                own, den = rows[dst]
                assert {str(j): Fraction(v, den) for j, v in own.items()} == {
                    j: Fraction(v) for j, v in prior["row"].items()}
                old_probe = {int(j): Fraction(v) for j, v in prior["separator"].items()}
                assert dot(rows[dst], old_probe) == Fraction(prior["separator_value"]) != 0
                assert all(dot(rows[j], old_probe) == 0 for j in bank)
                for donor, next_clock, source, target, owned in r["candidates"]:
                    assert states[donor] == source and donor not in bank
                    assert tape[next_clock] == ["MOVE", donor, source, target, owned]
                    augmented = bank + [donor]
                    rank, probe, value = separate(rows[dst], [rows[j] for j in augmented])
                    results.append({"clock": clock, "owner": dst, "donor": donor, "bank": bank,
                                    "next_donor_move": next_clock, "augmented_rank": rank,
                                    "prior_probe_donor_value": str(dot(rows[donor], old_probe)),
                                    "disposition": "outside span" if probe else "span member",
                                    "separator": probe, "owner_value": str(value) if probe else None})
            if op == "MOVE":
                a, b, owned = args
                assert states[dst] == a and owned == (dst >= n)
                states[dst] = b
            elif op == "INIT":
                assert dst >= n and states[dst] is None
                states[dst], rows[dst] = args[0], EMPTY
                fresh.add(dst)
                continue
            elif op == "CLEAR":
                assert dst >= n and states[dst] == args[0]
                states[dst], rows[dst] = None, EMPTY
            elif op == "SCALE":
                q, chart = args
                assert states[dst] == chart
                rows[dst] = add_scaled(EMPTY, rows[dst], coefficient(q))
            else:
                source, q, chart = args
                assert op in ("ADD", "COPY") and dst != source and states[dst] == states[source] == chart
                assert op != "COPY" or (dst >= n and dst in fresh and rows[dst] == EMPTY)
                rows[dst] = add_scaled(rows[dst], rows[source], coefficient(q))
            fresh.discard(dst)
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    done = {(r["clock"], r["owner"], r["donor"]) for r in results if r["disposition"] == "outside span"}
    assert done <= expected
    print(dumps({"pins": PINS, "head": geometry.get("head"), "caller": geometry.get("caller"),
                 "controls": controls(), "results": results, "cut_cap": CUTS, "pair_cap": PAIRS,
                 "seconds_cap": SECONDS, "capped": capped, "visited": visited,
                 "tested_pairs": len(results), "excluded_pairs": len(done),
                 "unresolved_pairs": sorted(expected - done)}, indent=2, sort_keys=True, default=str))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
