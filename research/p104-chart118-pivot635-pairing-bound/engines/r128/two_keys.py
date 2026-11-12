"""Exact rational necessary pairing for two translated chart-118 banks."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PRICE = "lead/PRICE.json"
WORD = "inputs/7334-WORD.json.gz"
PAIR = "inputs/paired_support.py"
TRACE = "inputs/paired_rank.py"
HISTORY = "inputs/OLD-WITNESS.json"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    PRICE: "8083c540876bbc7c61fc05eaa8e5796cb96d58ea123638931f6cb60ce0507849",
    WORD: "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    PAIR: "38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f",
    TRACE: "d1b7c34e6f8c8a7b810414762015e6e300a8292422af66ff671ae09741141f09",
    HISTORY: "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
}
CAP, SECONDS = 2, 35


def unique(rows):
    obj = dict(rows)
    if len(obj) != len(rows):
        raise ValueError("duplicate JSON key")
    return obj


def read(relative):
    raw = (ROOT / relative).read_bytes()
    if sha256(raw).hexdigest() != PINS[relative]:
        raise ValueError(f"changed dependency {relative}")
    return raw


def check_time(deadline):
    if monotonic() >= deadline:
        raise TimeoutError("cooperative limit")


def span(frame):
    subspace = {0}
    for vector in frame:
        assert vector not in subspace
        subspace |= {vector ^ old for old in subspace}
    return subspace


def geometry(word, keys, deadline):
    n = word["public"]
    assert (n, word["owned_fields"], len(word["program"])) == (1501, 68, 76466)
    assert (word["initial"][635], word["final"][635]) == (3, 127)
    frames = [word["frames"][r] for r in (3, 118, 127)]
    low, middle, high = map(span, frames)
    assert low < middle < high
    sizes = [len(frame) for frame in frames]
    differences = [b - a for a, b in zip(sizes, sizes[1:])]
    assert sorted(differences) == [4, 5]
    current = word["initial"][:] + [None] * word["owned_fields"]
    requested = {row["key"][0]: row["public"] for row in keys}
    banks = {}
    for t, event in enumerate(word["program"]):
        if t % 128 == 0:
            check_time(deadline)
        if t in requested:
            bank = [r for r, c in enumerate(current) if c == 118]
            assert bank == requested[t] and max(bank) < n and 635 in bank
            banks[t] = bank
        if t == max(requested):
            break
        op, d, *args = event
        if op == "MOVE":
            assert current[d] == args[0] and args[2] == (d >= n)
            current[d] = args[1]
        elif op == "INIT":
            assert current[d] is None and d >= n
            current[d] = args[0]
        elif op == "CLEAR":
            assert current[d] == args[0] and d >= n
            current[d] = None
        else:
            assert current[d] == args[-1]
            if op in ("ADD", "COPY"):
                assert current[args[0]] == args[-1] and args[0] != d
                if op == "COPY":
                    assert d >= n
            else:
                assert op == "SCALE"
    return banks, differences


def controls(solve, earlier):
    old = {k: {int(r): Q(v) for r, v in earlier[k].items()} for k in ("a", "b", "c", "d")}
    dot = solve["dot"]
    assert dot(old["a"], old["b"]) == dot(old["c"], old["d"]) == 1
    f, s = [(old["a"], old["c"])], [(old["b"], old["d"])]
    assert solve["paired"](f, s, float("inf"))
    assert solve["paired"](f, [(old["b"], {r: 2 * v for r, v in old["d"].items()})], float("inf")) is None
    return ["known historical chart-118 exact unit pair", "changed boundary pairing rejects"] + solve["controls"]()


def classify(row, forward, reverse, solve, rank, deadline):
    f = forward[row["key"][0]]
    s = reverse[row["key"][0]]
    dot = solve["dot"]
    local = [[dot(a, b) for b, _ in s] for a, _ in f]
    endpoint = [[dot(c, d) for _, d in s] for _, c in f]
    difference = [[x-y for x, y in zip(a, b, strict=True)] for a, b in zip(local, endpoint, strict=True)]
    wedge, difference_rank, stacked_rank = rank["pairing"](endpoint, difference)
    witness = solve["paired"](f, s, deadline)
    assert (witness is not None) == (wedge or difference_rank != stacked_rank)
    if witness:
        assert dot(witness["a"], witness["b"]) == dot(witness["c"], witness["d"]) == 1
    matrix = lambda values: [[str(v) for v in r] for r in values]
    return {
        "key": row["key"], "bank": row["public"], "pivot635_present": True,
        "prefix_dimension": len(f), "suffix_dimension": len(s),
        "nonzero_prefix_images": sum(bool(c) for _, c in f),
        "nonzero_suffix_images": sum(bool(d) for _, d in s),
        "local_pairing_matrix": matrix(local), "endpoint_pairing_matrix": matrix(endpoint),
        "difference_rank": difference_rank, "stacked_rank": stacked_rank, "nonzero_wedge": wedge,
        "status": "provisional relaxed rational support" if witness else "no exact unit pairing",
        "witness": {k: {r: str(v) for r, v in u.items()} for k, u in witness.items()} if witness else None,
    }


def hard_limit(*_):
    raise TimeoutError("35-second hard limit")


def main():
    assert __debug__
    raw = {name: read(name) for name in PINS}
    price = loads(raw[PRICE], object_pairs_hook=unique)
    earlier = loads(raw[HISTORY], object_pairs_hook=unique)
    solve, rank = (run_path(str(ROOT / f)) for f in (PAIR, TRACE))
    tests = controls(solve, earlier)
    assert price["limits"] == {"cases": CAP, "runner_seconds": SECONDS}
    assert Q(price["complete_probe"][0]) > 0 and Q(price["extra_rank_one_at_crossing_lower"][1]) < 0
    keys = price["selected"]
    assert len(keys) == CAP and [r["key"] for r in keys] == [[39701, 118], [40853, 118]]
    result = dict(head=price["head"], caller=price["caller"], pins=PINS, controls=tests,
                  cap=price["limits"], results=[], unselected=price["unvisited"], timeout=None,
                  scope="Arbitrary rational paired support, suffix guard requirements relaxed")
    signal(SIGALRM, hard_limit)
    alarm(SECONDS)
    deadline = monotonic() + 32
    try:
        payload = decompress(raw[WORD])
        if sha256(payload).hexdigest() != PAYLOAD:
            raise ValueError("changed literal payload")
        word = loads(payload, object_pairs_hook=unique)
        cohort, _ = solve["initial_groups"](word)
        assert cohort == set(price["endpoint_cohort"]) and len(cohort) == 615
        banks, result["ranks"] = geometry(word, keys, deadline)
        f = rank["side"](word, banks, cohort, deadline, False)
        s = rank["side"](word, banks, cohort, deadline, True)
        for row in keys:
            check_time(deadline)
            t = row["key"][0]
            if t not in f or t not in s:
                raise TimeoutError("unvisited rational bank")
            result["results"].append(classify(row, f, s, solve, rank, deadline))
    except (TimeoutError, solve["Capped"]) as error:
        result["timeout"] = str(error) or "paired-support cap"
    finally:
        alarm(0)
    result["selected_unvisited"] = [r["key"] for r in keys[len(result["results"]):]]
    print(dumps(result, indent=2, sort_keys=True))
    return 124 if result["timeout"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
