"""Reverse chronology for the closed chart-3 helper entrance gate."""
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
import sys

PIN = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
START = 3


def stop(*_):
    raise TimeoutError("10-second chronology cap")


def span(frame):
    out = {0}
    for x in frame:
        assert x not in out
        out |= {x ^ y for y in out}
    return out


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(10)
    raw = Path(sys.argv[1]).read_bytes()
    assert sha256(raw).hexdigest() == PIN
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == PAYLOAD
    w = loads(payload)
    n, tape, frames = w["public"], w["program"], w["frames"]
    assert (n, len(tape), frames[START]) == (1501, 76466, [])
    main = set(w["live"]) | {r + 112 for r in w["live"]}
    main.update(w["hosted"]["X2"])
    main.update(w["hosted"]["Y2"])
    helpers = set(range(n)) - main
    cohort = {i for i in helpers if w["initial"][i] == START}
    assert (len(main), len(helpers)) == (400, 1101)
    first_moves = {}
    for t in range(len(tape) - 1, -1, -1):
        e = tape[t]
        if e[0] == "MOVE" and e[1] in cohort:
            first_moves[e[1]] = t
    assert set(first_moves) == cohort
    proper = {}
    for r, t in first_moves.items():
        op, role, low, mid, owned = tape[t]
        end = w["final"][r]
        assert (op, role, low, owned) == ("MOVE", r, START, False)
        assert {0} < span(frames[mid]) <= span(frames[end])
        if len(frames[mid]) < len(frames[end]):
            proper[r] = (t, mid)
    edges = defaultdict(set)
    blockers = defaultdict(list)
    prelude = Counter()
    for t in range(len(tape) - 1, -1, -1):
        e = tape[t]
        op, dst, *tail = e
        if op not in ("ADD", "COPY", "SCALE"):
            assert op in ("MOVE", "INIT", "CLEAR")
            continue
        pairs = ((dst, None),) if op == "SCALE" else ((dst, tail[0]), (tail[0], dst))
        for role, peer in pairs:
            if role not in proper or t >= proper[role][0]:
                continue
            assert e[-1] == START
            prelude[role] += 1
            if op == "SCALE":
                continue
            if op == "ADD" and peer in proper and t < proper[peer][0] and proper[role][1] == proper[peer][1]:
                edges[role].add(peer)
            else:
                blockers[role].append([t, role, peer, op])

    assert all(prelude[r] for r in proper), "quiet proper case conflicts with prior gate"
    remaining = set(proper)
    groups = []
    while remaining:
        root = min(remaining)
        component = {root}
        work = [root]
        while work:
            extra = edges[work.pop()] - component
            component.update(extra)
            work.extend(extra)
        remaining.difference_update(component)
        blocked = [x for r in component for x in blockers[r]]
        roles = sorted(component)
        assert {proper[r][1] for r in roles} == {proper[root][1]}
        groups.append({"roles": roles, "upper": proper[root][1],
                       "first_move_clocks": [proper[r][0] for r in roles],
                       "boundary_contacts": len(blocked), "earliest_blocker": min(blocked) if blocked else None})
    assert sum(len(x["roles"]) for x in groups) == len(proper)
    survivors = [x for x in groups if not x["boundary_contacts"]]
    alarm(0)
    print(dumps({
        "pins": {"benchmark_native_WORD.json.gz": PIN, "word_payload": PAYLOAD},
        "head": "aaeec8c0acf01e99a5f331ef363a698d9c084ace",
        "caller": "07a76c5e2738882c0cb322278e56f6cae3c9885d",
        "caps": {"words": 1, "events": len(tape), "seconds": 10, "start_chart": START},
        "productive_helpers": len(helpers), "chart_3_helpers": len(cohort),
        "zero_residual": len(cohort) - len(proper), "proper_nonempty": len(proper),
        "components": groups, "sizes": Counter(len(x["roles"]) for x in groups),
        "survivors": survivors, "exhausted": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
