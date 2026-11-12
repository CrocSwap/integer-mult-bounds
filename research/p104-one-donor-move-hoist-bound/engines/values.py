"""Independently reject changed-donor equalities on pinned exact rational inputs."""
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "GEOMETRY.json": "d1319c5df9f1f9227c8d364447834a8d54d60ff25bbb1890f9754672bbfb22c0",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-LEAD.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CUTS, PAIRS, SECONDS = 8, 13, 25


def unique(items):
    data = dict(items)
    assert len(data) == len(items), "duplicate JSON key"
    return data


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    if path.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def stop(*_):
    raise TimeoutError("25-second exact rational cap")


@cache
def scalar(text):
    return Fraction(text)


def witness(values, owner, donor, sign, preferred):
    indices = [preferred] + [i for i in range(len(values[owner])) if i != preferred]
    for i in indices:
        a, b = values[owner][i], values[donor][i]
        if a != sign * b:
            return {"probe": i, "owner_value": str(a), "donor_value": str(b)}
    return None


def main():
    assert __debug__
    geometry = read("GEOMETRY.json")
    old = read("inputs/R137-LEAD.json")
    word = read("inputs/7334-WORD.json.gz")
    assert (geometry["head"], geometry["caller"]) == (old["head"], old["caller"])
    old_cuts = {r["move_clock"]: r for r in old["records"]}
    chosen = {r["clock"]: r for r in geometry["records"] if r["candidates"]}
    assert len(chosen) == CUTS
    probes = {clock: {int(j): scalar(v) for j, v in old_cuts[clock]["separator"].items()}
              for clock in chosen}
    probe_index = {clock: i for i, clock in enumerate(probes)}
    zero = Fraction(0)
    all_zero = (zero,) * CUTS
    assert witness([(Fraction(2),), (Fraction(2),)], 0, 1, 1, 0) is None
    assert witness([(Fraction(2),), (Fraction(2),)], 0, 1, -1, 0) == {
        "probe": 0, "owner_value": "2", "donor_value": "2"}
    n, m, tape = (word[k] for k in ("public", "owned_fields", "program"))
    assert (n, m, len(tape)) == (1501, 68, 76466)
    states = word["initial"] + [None] * m
    values = [tuple(p.get(j, zero) for p in probes.values()) for j in range(n)] + [all_zero] * m
    fresh, results, visited, capped = set(), [], 0, False
    signal(SIGALRM, stop)
    alarm(SECONDS)
    try:
        for clock, (op, dst, *args) in enumerate(tape[:max(chosen) + 1]):
            visited = clock + 1
            if clock in chosen:
                item, p = chosen[clock], probe_index[clock]
                assert dst == item["owner"] and [op, *args] == [
                    "MOVE", item["from_chart"], item["to_chart"], True]
                assert values[dst][p] == scalar(old_cuts[clock]["separator_value"]) != 0
                for donor, next_clock, source, target, is_owned in item["candidates"]:
                    assert states[donor] == source and is_owned == (donor >= n)
                    assert tape[next_clock] == ["MOVE", donor, source, target, is_owned]
                    checks = {str(sign): witness(values, dst, donor, sign, p) for sign in (1, -1)}
                    results.append({"clock": clock, "owner": dst, "donor": donor,
                                    "donor_move_clock": next_clock, "checks": checks})
            if op == "MOVE":
                a, b, owned = args
                assert states[dst] == a and owned == (dst >= n)
                states[dst] = b
            elif op == "INIT":
                assert dst >= n and states[dst] is None
                states[dst], values[dst] = args[0], all_zero
                fresh.add(dst)
                continue
            elif op == "CLEAR":
                assert dst >= n and states[dst] == args[0]
                states[dst], values[dst] = None, all_zero
            elif op == "SCALE":
                q, chart = args
                assert states[dst] == chart
                values[dst] = tuple(scalar(q) * v for v in values[dst])
            else:
                source, q, chart = args
                assert op in ("ADD", "COPY") and dst != source and states[dst] == states[source] == chart
                assert op != "COPY" or (dst >= n and dst in fresh and values[dst] == all_zero)
                values[dst] = tuple(a + scalar(q) * b for a, b in zip(values[dst], values[source], strict=True))
            fresh.discard(dst)
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    expected = {(k, r["owner"], d[0]) for k, r in chosen.items() for d in r["candidates"]}
    assert len(expected) == PAIRS
    resolved = {(r["clock"], r["owner"], r["donor"]) for r in results if all(r["checks"].values())}
    assert resolved <= expected
    print(dumps({"pins": PINS, "head": geometry["head"], "caller": geometry["caller"],
                 "probe_vectors": list(probes.values()), "checks": results, "cut_cap": CUTS,
                 "pair_cap": PAIRS, "seconds_cap": SECONDS, "capped": capped,
                 "visited": visited, "tested_pairs": len(results), "excluded_pairs": len(resolved),
                 "unresolved_pairs": sorted(expected - resolved)},
                indent=2, sort_keys=True, default=str))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
