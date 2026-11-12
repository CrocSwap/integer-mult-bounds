"""Reconstruct the five frozen source windows by reverse literal occupancy."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/PRICE.json": "8fbd560cf7708b99609614a0b96d02b55efc55304225ddffa5dd223ed49d4073",
    "inputs/R101-PRICE.json": "ac5ecb17f0e9f3c068423998b350a78c1a4769b6f61b50838be5f3e0d0b1a00c",
    "inputs/7334-WORD.json.gz": WORD,
    "inputs/RETIMING.json": "331d26d99d45d24796253cd0bf86fdbd8b755ba164ca7765edc8304cc3365f6f",
}
EVENTS, WINDOWS, CUTS, SECONDS = 76466, 5, 18864, 20


def unique(items):
    data = dict(items)
    if len(data) != len(items):
        raise ValueError("duplicate JSON key")
    return data


def read(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency: {name}")
    return raw


def backwards(word, sources, destinations, deadline, progress):
    tape = word["program"]
    n, owned = word["public"], word["owned_fields"]
    assert (n, owned) == (1501, 68) and len(tape) == EVENTS
    active = word["final"] + [None] * owned
    source_chart_intervals = defaultdict(list)
    source_moves, source_writes, dest_incidents = (defaultdict(list) for _ in range(3))
    upper = dict.fromkeys(sources, len(tape))
    for t in range(len(tape) - 1, -1, -1):
        progress["first_unvisited_event"] = t
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse incidence time cap")
        op, d, *args = e = tape[t]
        current = active[d]
        operands = [d]
        if op == "MOVE":
            old, new, flag = args
            assert current == new and flag == (d >= n)
            if d in sources:
                source_chart_intervals[d].append((t + 1, upper[d], new))
                source_moves[d].append((t, e))
                upper[d] = t
            active[d] = old
        elif op == "CLEAR":
            assert d >= n and current is None
            active[d] = args[0]
        elif op == "INIT":
            assert d >= n and current == args[0]
            active[d] = None
        else:
            assert op in ("ADD", "COPY", "SCALE") and current == args[-1]
            if op in ("ADD", "COPY"):
                assert args[0] != d and active[args[0]] == current
                assert op != "COPY" or d >= n
                operands.append(args[0])
            if d in sources:
                source_writes[d].append((t, e))
        for r in operands:
            if r in destinations:
                dest_incidents[r].append((t, e))
        progress["events_replayed"] += 1
    assert active == word["initial"] + [None] * owned
    progress["first_unvisited_event"] = None
    for r in sources:
        source_chart_intervals[r].append((0, upper[r], active[r]))
        source_chart_intervals[r].reverse()
        assert all(x[1] + 1 == y[0] for x, y in zip(source_chart_intervals[r], source_chart_intervals[r][1:]))
        source_moves[r].reverse()
        source_writes[r].reverse()
    for r in destinations:
        dest_incidents[r].reverse()
    return source_chart_intervals, source_moves, source_writes, dest_incidents


def split(lo, hi, old):
    return [(a, b) for a, b in ((lo, min(hi, old - 1)), (max(lo, old + 1), hi)) if a <= b]


def row_stability(writes, old, end):
    earlier = next((r for r in reversed(writes) if r[0] < old), None)
    later = next((r for r in writes if r[0] > old), None)
    assert not any(t == old for t, _ in writes)
    return (0 if earlier is None else earlier[0] + 1, end if later is None else later[0]), earlier, later


def typed_intervals(chart_spans, left, right, old, expected, stable):
    result = []
    for a, b, chart in chart_spans:
        for lo, hi in split(max(a, left), min(b, right), old):
            ranges = [(lo, hi, "different chart", chart)]
            if chart == expected:
                s, t = stable
                ranges = [(lo, min(hi, s - 1), "source write", chart),
                          (max(lo, s), min(hi, t), "exact unchanged source", chart),
                          (max(lo, t + 1), hi, "source write", chart)]
            for first, last, status, actual in ranges:
                if first > last:
                    continue
                if result and result[-1][1] + 1 == first and result[-1][2:] == [status, actual]:
                    result[-1][1] = last
                else:
                    result.append([first, last, status, actual])
    return result


def controls():
    assert split(1, 6, 4) == [(1, 3), (5, 6)] and split(4, 4, 4) == []
    stable, before, after = row_stability([(2, "WRITE1"), (6, "WRITE2")], 4, 8)
    assert (stable, before, after) == ((3, 6), (2, "WRITE1"), (6, "WRITE2"))
    actual = typed_intervals([(0, 3, 5), (4, 8, 7)], 1, 7, 4, 7, stable)
    assert actual == [[1, 3, "different chart", 5], [5, 6, "exact unchanged source", 7], [7, 7, "source write", 7]]
    return ["remove only old pre-event cut", "source write exact endpoints",
            "signed chart and source-write distinction", "chart applies after its MOVE event"]


def candidate_results(word, price, candidates, histories, deadline, progress, result):
    spans, moves, writes, incidents = histories
    for row in candidates:
        f, g, dst = row["key"]
        a, b, c = row["charts"]
        old, add = row["add"]
        src = add[2]
        assert f < old < g and dst == add[1] and 0 <= src < word["public"] and src != dst
        contacts = incidents[dst]
        expected = [(f, ["MOVE",dst,a,b,False]), (old,add), (g,["MOVE",dst,b,c,False])]
        assert [r for r in contacts if f <= r[0] <= g] == expected
        dst_before = next((r for r in reversed(contacts) if r[0] < f), None)
        dst_after = next((r for r in contacts if r[0] > g), None)
        assert len([1 for l,u,h in spans[src] if l <= old <= u and h == b]) == 1
        stable, prev_write, next_write = row_stability(writes[src], old, EVENTS)
        item = dict(move_pair=row["key"], original_add=row["add"], source=src,
                    original_charts=row["charts"], unchanged_row_window=stable,
                    source_moves=[r for r in moves[src] if f <= r[0] <= g],
                    source_writes=[r for r in writes[src] if f <= r[0] <= g],
                    previous_source_write=prev_write, next_source_write=next_write,
                    destination_contacts=expected, previous_destination_contact=dst_before,
                    next_destination_contact=dst_after, cuts=[], counts=Counter())
        result.append(item)
        for side, target in (("entrance", a), ("exit", c)):
            progress["first_unvisited_typed_window"] = [f, g, dst, side]
            if monotonic() >= deadline:
                raise TimeoutError("typed window time cap")
            ranges = typed_intervals(spans[src], f + 1, g, old, target, stable)
            tested = sum(hi - lo + 1 for lo, hi, _, _ in ranges)
            assert tested == g - f - 1
            if progress["typed_cuts_replayed"] + tested > price["limits"]["typed_cuts"]:
                raise TimeoutError("typed cut count cap")
            progress["typed_cuts_replayed"] += tested
            for lo, hi, status, _ in ranges:
                item["counts"][status] += hi - lo + 1
            item["cuts"].append(dict(side=side, chart=target, intervals=ranges))
    progress["first_unvisited_typed_window"] = None


def compare(result, primary):
    assert primary["head"] == HEAD and primary["timeout"] is None
    assert primary["first_unvisited_cut"] is None and primary["first_unvisited_event"] is None
    assert len(result) == len(primary["rows"]) == WINDOWS
    for a, b in zip(result, primary["rows"], strict=True):
        for k in ("move_pair", "original_add", "source", "unchanged_row_window", "source_moves", "source_writes", "cuts", "counts"):
            assert dumps(a[k], sort_keys=True) == dumps(b[k], sort_keys=True), (a["move_pair"], k)
    counts = Counter()
    for row in result:
        counts.update(row["counts"])
    assert counts == primary["counts"] and sum(counts.values()) == CUTS
    return counts


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--controls-only", action="store_true")
    args = p.parse_args()
    assert __debug__ and sys.version_info[:2] == (3, 12)
    checks = controls()
    if args.controls_only:
        print(dumps(checks))
        return

    def stop(*_):
        raise TimeoutError("hard 20-second cap")

    alarm(0)
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + 18
    progress = dict(events_replayed=0, typed_cuts_replayed=0, first_unvisited_event=EVENTS-1,
                    first_unvisited_typed_window=None)
    result, timeout, counts = [], None, None
    try:
        raw = {name: read(args.root, name) for name in PINS}
        price, parent, primary = [loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)
                                  for name in ("PRICE","R101-PRICE","RETIMING")]
        assert price["head"] == parent["head"] == primary["head"] == HEAD
        assert price["caller_head"] == parent["caller_head"] == CALLER
        assert price["parent_price_sha256"] == PINS["inputs/R101-PRICE.json"]
        assert price["word_sha256"] == parent["word_sha256"] == WORD
        assert price["payload_sha256"] == parent["payload_sha256"] == PAYLOAD
        assert primary["pins"]["lead/PRICE.json"] == PINS["inputs/PRICE.json"]
        limits = price["limits"]
        assert (limits["events"], limits["pair_windows"], limits["typed_cuts"], limits["runner_seconds"]) == (
            EVENTS, WINDOWS, CUTS, SECONDS)
        payload = decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=unique)
        candidates = price["candidates"]
        n = word["public"]
        assert len(parent["candidates"]) == WINDOWS + 1
        assert [r for r in parent["candidates"] if r["add"][1][2] < n] == candidates
        assert [r["add"][1][2] for r in parent["candidates"] if r["add"][1][2] >= n] == [1555]
        sources = {r["add"][1][2] for r in candidates}
        destinations = {r["key"][2] for r in candidates}
        assert len(candidates) == len({tuple(r["key"]) for r in candidates}) == WINDOWS
        histories = backwards(word, sources, destinations, deadline, progress)
        candidate_results(word, price, candidates, histories, deadline, progress, result)
        counts = compare(result, primary)
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)

    complete = timeout is None and counts is not None
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, controls=checks, complete=complete,
        agreement=complete, limits=dict(events=EVENTS, windows=WINDOWS, typed_cuts=CUTS, seconds=SECONDS),
        counts=counts, rows=result, progress=progress, timeout=timeout), indent=2, sort_keys=True))
    if not complete:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
