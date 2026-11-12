"""Independent interval census for the frozen R92 rank-two ascent anchors."""
from argparse import ArgumentParser
from bisect import bisect_left, bisect_right
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
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/GEOMETRY.json": "e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-WORD.json.gz": WORD,
}
EVENTS, PLACEMENTS, RAW_CAP, SECONDS = 76466, 285, 40000, 20
PROTECTED = {319, 863, 1355, 1568}


def unique(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def pinned(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"changed dependency: {path.name}")
    return data


def span(basis):
    result = {0}
    for v in basis:
        assert isinstance(v, int) and 0 < v < 512 and v not in result
        result |= {v ^ w for w in result}
    return frozenset(result)


def contacts(event):
    op, role, *args = event
    if op == "MOVE":
        return (role,), tuple(args[:2])
    if op in ("INIT", "CLEAR", "SCALE"):
        return (role,), (args[-1],)
    assert op in ("ADD", "COPY") and role != args[0]
    return (role, args[0]), (args[-1],)


def quiet_window(incidents, move, event_count):
    i = bisect_left(incidents, move)
    assert incidents[i] == move
    previous = incidents[i - 1] if i else None
    following = incidents[i + 1] if i + 1 < len(incidents) else None
    return (0 if previous is None else previous + 1,
            event_count if following is None else following), previous, following


def segments(low, high, move, post_event_boundaries):
    assert low <= high
    bounds = {low, high + 1}
    a, b = bisect_right(post_event_boundaries, low), bisect_right(post_event_boundaries, high)
    bounds.update(post_event_boundaries[a:b])
    if low <= move < high:
        bounds.add(move + 1)
    ordered = sorted(bounds)
    return [(a, b - 1) for a, b in zip(ordered, ordered[1:])]


def classify(bank, mover, cohort, public):
    assert mover not in bank
    public_roles = sorted(r for r in bank if r < public)
    owned_roles = sorted(r for r in bank if r >= public)
    pivots = sorted(set(public_roles) & cohort)
    status = "owned" if owned_roles else "eligible" if pivots else "missing_pivot"
    return dict(public=public_roles, owned=owned_roles, pivots=pivots, status=status)


def controls():
    tape = [("ADD", 1, 0, "-1", 8), ("MOVE", 0, 8, 10, False),
            ("ADD", 7, 9, "2", 9), ("COPY", 7, 0, "1", 10)]
    hits = [t for t, event in enumerate(tape) if 0 in contacts(event)[0]]
    assert quiet_window(hits, 1, len(tape)) == ((1, 3), 0, 3)
    assert segments(0, 7, 3, [1, 3, 6]) == [(0, 0), (1, 2), (3, 3), (4, 5), (6, 7)]
    assert segments(2, 4, 3, [2, 5]) == [(2, 3), (4, 4)]
    assert classify({2}, 1, {1, 2}, 10)["status"] == "eligible"
    assert classify({2, 11}, 1, {1, 2}, 10)["status"] == "owned"
    assert classify({3}, 1, {1, 2}, 10)["status"] == "missing_pivot"
    return ["mover ADD/COPY source contacts bound its window", "B contacts and removed MOVE separate blocks",
            "distinct pre-existing pivot", "owned guard and missing-pivot guard"]


def frozen_placements(word, geometry, cohort):
    assert geometry["events_replayed"] == EVENTS and geometry["geometry_timeout"] is None
    assert len(geometry["raw_placements"]) == PLACEMENTS
    assert not geometry["eligible"] and not geometry["unvisited_support_keys"]
    spans = [span(basis) for basis in word["frames"]]
    by_span = defaultdict(list)
    for c, s in enumerate(spans):
        by_span[s].append(c)
    quotient_by_anchor, labelled = defaultdict(set), []
    for placement in geometry["raw_placements"]:
        clock, mover, rep = (placement[k] for k in ("move_clock", "mover", "quotient_representative"))
        op, r, lo, hi, owned = word["program"][clock]
        assert op == "MOVE" and r == mover and not owned and r in cohort
        a, c = spans[lo], spans[hi]
        assert a < c and len(c) == 4 * len(a) and rep in c - a
        target = a | {v ^ rep for v in a}
        assert a < target < c and len(target) == (1 << placement["rank"]) and placement["rank"] in (4, 5)
        assert target not in quotient_by_anchor[clock]
        quotient_by_anchor[clock].add(target)
        labels = [row["chart"] for row in placement["labels"]]
        assert labels == by_span.get(target, [])
        assert not any(row["eligible"] for row in placement["labels"])
        labelled.extend(dict(anchor=clock, mover=mover, chart=chart, quotient_representative=rep,
                             source=lo, destination=hi, rank=placement["rank"]) for chart in labels)
    assert len(quotient_by_anchor) == 95 and all(len(s) == 3 for s in quotient_by_anchor.values())
    assert len(labelled) == 31
    assert len({(r["anchor"],r["chart"],r["mover"]) for r in labelled}) == len(labelled)
    return labelled


def index_contacts(tape, labels, deadline, state):
    movers = {r["mover"] for r in labels}
    charts = {r["chart"] for r in labels}
    roles, chart_boundaries = defaultdict(list), defaultdict(list)
    for clock, event in enumerate(tape):
        if clock % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("first-pass chronological contact cap")
        rs, cs = contacts(event)
        for r in rs:
            if r in movers:
                roles[r].append(clock)
        for c in cs:
            if c in charts:
                chart_boundaries[c].append(clock + 1)
        state["forward_events"] = clock + 1
    return roles, chart_boundaries


def build_requests(labels, role_contacts, chart_boundaries, deadline, state):
    requests = defaultdict(set)
    blocks, remaining = state["blocks"], state["raw_unvisited_intervals"]
    for label in labels:
        if monotonic() >= deadline:
            raise TimeoutError("interval construction cap")
        clock, chart, mover = (label[k] for k in ("anchor", "chart", "mover"))
        (low, high), previous, following = quiet_window(role_contacts[mover], clock, EVENTS)
        assert low <= clock < high
        label.update(window=[low, high], previous_contact=previous, next_contact=following)
        count = high - low + 1
        state["raw_candidate_cuts"] += count
        end = min(high, low + RAW_CAP - state["raw_scheduled_cuts"] - 1)
        if end < high:
            remaining.append(dict(anchor=clock, chart=chart, mover=mover, interval=[max(low, end + 1), high]))
        if end < low:
            continue
        for first, last in segments(low, end, clock, chart_boundaries[chart]):
            blocks.append(dict(label, first=first, last=last))
            requests[first].add(chart)
        state["raw_scheduled_cuts"] += end - low + 1
    return requests


def reverse_snapshots(word, requests, deadline, state):
    n = word["public"]
    owned = word["owned_fields"]
    tape = word["program"]
    active = word["final"] + [None] * owned
    banks = defaultdict(set)
    for r, c in enumerate(active[:n]):
        banks[c].add(r)
    result = {}
    state["snapshots"] = result

    def transition(r, old, new):
        assert active[r] == new
        if new is not None:
            banks[new].remove(r)
        if old is not None:
            banks[old].add(r)
        active[r] = old

    for cut in range(EVENTS, -1, -1):
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            raise TimeoutError("second-pass occupancy cap")
        for chart in requests.get(cut, ()):
            result[cut, chart] = banks[chart].copy()
        if not cut:
            assert active == word["initial"] + [None] * owned
            break
        op, r, *args = tape[cut - 1]
        if op == "MOVE":
            old, new, is_owned = args
            assert is_owned == (r >= n)
            transition(r, old, new)
        elif op == "INIT":
            assert r >= n
            transition(r, None, args[0])
        elif op == "CLEAR":
            assert r >= n
            transition(r, args[0], None)
        else:
            assert active[r] == args[-1] and op in ("SCALE", "ADD", "COPY")
            if op in ("ADD", "COPY"):
                assert active[args[0]] == active[r]
        state["reverse_events"] = EVENTS - cut + 1


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--price", type=Path)
    parser.add_argument("--price-sha256")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__ and sys.version_info[:2] == (3, 12)
    checks = controls()
    if args.controls_only:
        print(dumps(checks))
        return
    if args.price is None or args.price_sha256 is None:
        parser.error("the frozen R98 price file and its SHA-256 are required")

    def stop(*_):
        raise TimeoutError("hard 20-second cap")

    deadline = monotonic() + 18
    signal(SIGALRM, stop)
    alarm(SECONDS)
    state = dict(forward_events=0, reverse_events=0, raw_candidate_cuts=0, raw_scheduled_cuts=0,
                 raw_unvisited_intervals=[], blocks=[])
    labels, cohort, n = [], set(), None
    timeout = None
    try:
        price_raw = pinned(args.price, args.price_sha256)
        price = loads(price_raw, object_pairs_hook=unique)
        assert price["head"] == HEAD and price["word_sha256"] == WORD
        assert price["pins"]["inputs/R92-GEOMETRY.json"] == PINS["inputs/GEOMETRY.json"]
        assert price["pins"]["inputs/R92-PRICE.json"] == PINS["inputs/R92-PRICE.json"]
        limits = price["limits"]
        assert (limits["event_passes"], limits["events_each"], limits["quotient_lines"],
                limits["raw_label_cuts"], limits["geometry_seconds"]) == (2, EVENTS, PLACEMENTS, RAW_CAP, SECONDS)
        raw = {k: pinned(ROOT / k, digest) for k, digest in PINS.items()}
        geometry, old_price = [loads(raw[f"inputs/{k}.json"], object_pairs_hook=unique)
                               for k in ("GEOMETRY", "R92-PRICE")]
        assert geometry["price_sha256"] == PINS["inputs/R92-PRICE.json"]
        assert old_price["head"] == geometry["head"] == HEAD and old_price["word_sha256"] == geometry["word_sha256"] == WORD
        word_raw = decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(word_raw).hexdigest() == PAYLOAD
        word = loads(word_raw, object_pairs_hook=unique)
        assert len(word["program"]) == EVENTS and word["public"] == 1501 and word["owned_fields"] == 68
        n = word["public"]
        protected = PROTECTED | set(word["live"]) | {r + 112 for r in word["live"]}
        protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
        cohort = set(old_price["endpoint_cohort"])
        assert cohort == {r for r,(a,z) in enumerate(zip(word["initial"],word["final"],strict=True))
                          if (a,z) == (3,127) and r not in protected}
        labels = frozen_placements(word, geometry, cohort)
        assert [[r[k] for k in ("anchor","mover","chart","rank","quotient_representative")]
                for r in labels] == price["labelled"]
        role_contacts, chart_boundaries = index_contacts(word["program"], labels, deadline, state)
        requests = build_requests(labels, role_contacts, chart_boundaries, deadline, state)
        reverse_snapshots(word, requests, deadline, state)
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)

    snapshots = state.pop("snapshots", {})
    results, counts, raw_counts, unvisited = [], Counter(), Counter(), state["raw_unvisited_intervals"]
    for block in state.pop("blocks"):
        cut, chart, mover = (block[k] for k in ("first", "chart", "mover"))
        key = cut, chart, mover, block["anchor"]
        if (cut, chart) not in snapshots:
            unvisited.append(dict(anchor=block["anchor"], chart=chart, mover=mover, interval=[cut, block["last"]]))
            continue
        status = classify(snapshots[cut, chart], mover, cohort, n)
        counts[status["status"]] += 1
        raw_counts[status["status"]] += block["last"] - cut + 1
        results.append(dict(block, key=key, **status))
    if not timeout:
        assert state["forward_events"] == state["reverse_events"] == EVENTS
        assert sum(raw_counts.values()) + sum(r["interval"][1] - r["interval"][0] + 1 for r in unvisited) == state["raw_candidate_cuts"]
        assert len({tuple(r["key"]) for r in results}) == len(results)
    exhausted = not timeout and not unvisited
    print(dumps(dict(head=HEAD, pins=PINS, r98_price_sha256=args.price_sha256,
        complete=exhausted, cap_events_per_pass=EVENTS, cap_passes=2, cap_placements=PLACEMENTS,
        cap_raw_cuts=RAW_CAP, cap_seconds=SECONDS, timeout=timeout, controls=checks,
        labelled_anchors=labels, counts=counts, raw_counts=raw_counts,
        selected=[r for r in results if r["status"] == "eligible"], results=results,
        **state), indent=2, sort_keys=True))
    if not exhausted:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
