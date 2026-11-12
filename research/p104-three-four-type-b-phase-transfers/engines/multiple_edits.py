"""Exact integer-scaled causal impulse replay on the frozen R84 keys."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from time import monotonic

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "price": "6bf60b702f2d8b879fe0fca3c6c93dc5a580ae264f19eb87d27d0268d29b63bf",
    "keys": "2bb549fc7738efb4a159181094c771218903099be624a85474599683b73acde2",
    "admission": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "caller": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "engine": "140c10fb4365bb5e254df5f9b0a7d89ad54b901ceaf36d528e2ff4baa4bd3c80",
}
CAP, SECONDS, COOPERATIVE = 25350, 35, 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, key):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[key], f"changed input {key}")
    return raw


def stock(caller, offset):
    odd, even = {}, {}
    for clock, e in enumerate(caller["events"]):
        if e[:2] == ["B", "IDLE_ODD"]:
            need(len(e[3]) == 1 and e[4:] == [-1], "invalid signed singleton")
            odd[clock] = [e[2] - offset, e[3]]
        elif e[:2] == ["B", "IDLE_ONE"] and len(e[3]) > 1:
            even[clock] = [e[2] - offset, e[3]]
    return odd, even


def prepared(data, n):
    d, rows, gains, ends = data
    dense = tuple((j + 1) ** 2 for j in range(n))
    observations = {c: sum(x * y for x, y in zip(row, dense, strict=True)) for c, row in rows.items()}
    return dense, observations, tuple(d ** k for k in range(10))


def dense_difference(data, clocks, observations, powers):
    _, _, gains, ends = data
    injections = []
    for j, c in enumerate(clocks):
        arrived = observations[c] * powers[j]
        for i, previous in enumerate(clocks[:j]):
            arrived += injections[i] * gains[previous, c] * powers[j - i - 1]
        injections.append(-2 * arrived)
    if not any(injections):
        return None
    weights = [a * powers[len(clocks) - i - 1] for i, a in enumerate(injections)]
    denominator = powers[len(clocks) + 1]
    for row, endpoint in enumerate(zip(*(ends[c] for c in clocks), strict=True)):
        value = sum(a * b for a, b in zip(weights, endpoint, strict=True))
        if value:
            return row, Q(value, denominator)
    return None


def controls(engine):
    inherited = engine["controls"]()
    for n in (6, 8):
        clocks = tuple(range(n))
        roles = ([0, 1, 0, 1] + [2, 2] * 2)[:n]
        gates = [None] * n
        data = engine["old_trajectories"](gates, dict(enumerate(roles)), 3)
        dense, obs, powers = prepared(data, 3)
        need(dense_difference(data, clocks, obs, powers) is None and
             engine["first_difference"](data, clocks, 3) is None, "extended cancellation rejected")
        bad = roles[:-1] + [1]
        data = engine["old_trajectories"](gates, dict(enumerate(bad)), 3)
        dense, obs, powers = prepared(data, 3)
        got = dense_difference(data, clocks, obs, powers)
        need(got is not None and engine["first_difference"](data, clocks, 3) is not None,
             "corrupt extended cancellation accepted")
        row, value = got
        direct = sum(dense[j] * engine["direct"](gates, dict(enumerate(bad)), clocks, j, 3).get(row, 0)
                     for j in range(3))
        need(direct == value, "dense integer scaling differs from literal recurrence")
    return inherited | {"six_and_eight_clock_simultaneous_cancellation": True,
                        "dense_direct_bad_controls": 2}


def main(args):
    read(HERE / "four_edits.py", "engine")
    engine = run_path(str(HERE / "four_edits.py"))
    tests = controls(engine)
    if args.controls_only:
        return {"controls": tests}
    started = monotonic()
    price = loads(read(args.price, "price"))
    keys = loads(read(args.keys, "keys"))
    admission = loads(read(args.admission, "admission"))
    need(price["head"] == admission["head"] == HEAD and admission["exit"] == 0 and
         price["keys_sha256"] == PINS["keys"] and price["caller_sha256"] == PINS["caller"],
         "wrong price or admission")
    need(price["limits"]["first_keys"] == CAP and price["limits"]["first_runner_seconds"] == SECONDS,
         "wrong frozen scope cap")
    caller = loads(read(args.caller, "caller"))
    block = caller["types"]["B"]
    offset, n = block["offset"], block["roles"]
    need((caller["stages"], offset, n, len(block["ports"])) == (17, 36, 36, 8), "wrong Type B signature")
    odd, even = stock(caller, offset)
    need({str(k): v for k, v in odd.items()} == price["odd_jobs"] and
         {str(k): v for k, v in even.items()} == price["even_jobs"], "literal phase inventory differs")
    reconstructed = [
        {"odd": list(o), "even": list(e), "price": ",".join(map(str, sorted(len(even[c][1]) for c in e)))}
        for m in (3, 4) for o in combinations(sorted(odd), m) for e in combinations(sorted(even), m)
    ]
    need(keys == reconstructed and len(keys) == CAP, "literal keys differ from sealed price")
    site_roles = {t: v[0] for t, v in (odd | even).items()}
    gates = [engine["decode"](event, offset) for event in caller["events"]]
    diagonal = [engine["signed"](row[0]) for row in block["diagonal"]]
    data = engine["old_trajectories"](gates, site_roles, n, diagonal)
    dense, obs, powers = prepared(data, n)
    outcomes = []
    for spec in keys:
        if len(outcomes) >= CAP or monotonic() - started >= COOPERATIVE:
            break
        clocks = tuple(sorted(spec["odd"] + spec["even"]))
        match = dense_difference(data, clocks, obs, powers)
        if match:
            row, value = match
            result = {"status": "excluded", "dense_witness": [row + offset, str(value)]}
        else:
            witness = engine["first_difference"](data, clocks, n)
            if witness is None:
                result = {"status": "specialization_survives", "basis_columns": n}
            else:
                col, row, value = witness
                result = {"status": "excluded", "basis_witness": [col + offset, row + offset, str(value)]}
        outcomes.append({"key": clocks, "price": spec["price"], **result})
    unvisited = keys[len(outcomes):]
    return {"status": "CAPPED" if unvisited else "EXHAUSTED", "head": HEAD, "input_sha256": PINS,
            "case_cap": CAP, "runner_cap_seconds": SECONDS, "cooperative_seconds": COOPERATIVE,
            "controls": tests, "old_endpoint_columns": n, "dense_probe": dense, "common_denominator": data[0],
            "tested": len(outcomes), "outcomes": outcomes, "unvisited": unvisited,
            "survivors": [r["key"] for r in outcomes if r["status"] == "specialization_survives"],
            "counts": dict(Counter(row["status"] for row in outcomes))}


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("--controls-only", action="store_true")
    for name in ("price", "keys", "admission", "caller"):
        p.add_argument("--" + name, type=Path)
    args = p.parse_args()
    need(args.controls_only or all(getattr(args, key) for key in ("price", "keys", "admission", "caller")),
         "all pinned inputs required")
    print(dumps(main(args), sort_keys=True, separators=(",", ":")))
