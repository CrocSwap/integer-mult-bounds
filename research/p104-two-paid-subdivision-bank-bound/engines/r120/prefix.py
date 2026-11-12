"""Independent second-prime exterior prefix and alias check for the last R99 bank."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "plan/PRICE.json": "b29ff21d96485317003db5d06d3332f71e7158de4fafbbc6b300a45fc5d5e3c6",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/second_prime.py": "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
    "inputs/7334-WORD.json.gz": WORD,
}
MOVERS = [572, 1255]
ANCHORS = {572: 43050, 1255: 42958}
LOW, HIGH = 762, 869
CUTS, PAIRS = (42958, 42959, 42960), (22, 33, 44)
EVENTS, SECONDS, PRIME = 76466, 25, 65537


def checked(root, rel):
    data = (root / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError("changed dependency " + rel)
    return data


def freeze(root, engine):
    load = lambda name: loads(checked(root, name), object_pairs_hook=engine["unique"])
    price = load("plan/PRICE.json")
    cohort_data = load("inputs/R92-PRICE.json")
    cohort = set(cohort_data["endpoint_cohort"])
    assert price["head"] == cohort_data["head"] == HEAD and price["caller"] == CALLER
    assert price["pins"]["inputs/R92-PRICE.json"] == PINS["inputs/R92-PRICE.json"]
    assert price["word_sha256"] == WORD and len(cohort) == 615 and set(MOVERS) <= cohort
    caps = price["caps"]
    assert (caps["events_per_direction"], caps["raw_keys"], caps["support_forms"], caps["runner_seconds"]) == (EVENTS, 9, 1, SECONDS)
    assert price["raw_keys"] == [[t, i] for t in CUTS for i in PAIRS]
    assert price["row"]["bank"]["public"] == price["row"]["bank"]["pivots"] == MOVERS
    assert not price["row"]["bank"]["owned"] and price["row"]["chart"] is None
    assert sorted(price["row"]["anchors"]) == sorted([t, r] for r, t in ANCHORS.items())
    return price, cohort


def geometry(word, price, engine, span):
    frames = word["frames"]
    low, high = span(LOW), span(HIGH)
    assert len(low) == 16 and len(high) == 64 and low < high
    spans = set()
    for interval in price["intervals"]:
        key, basis = interval["pair"], interval["basis"]
        assert key in PAIRS and interval["chart"] is None
        assert [interval["first"], interval["last"]] == [CUTS[0], CUTS[-1]]
        assert len(basis) == 5
        mid = frozenset(engine["span"](basis))
        assert len(mid) == 32 and low < mid < high
        spans.add(mid)
    assert len(spans) == 3
    # A fresh chart has no pre-existing physical occupant or matching old label.
    catalogue = {span(chart) for chart, frame in enumerate(frames) if len(frame) == 5}
    assert spans.isdisjoint(catalogue)
    for r, at in ANCHORS.items():
        assert word["program"][at] == ["MOVE", r, LOW, HIGH, False]
        assert (word["initial"][r], word["final"][r]) == (3, 127)
    return len(catalogue)


def sweep(word, price, cohort, engine, deadline, progress, rows, denoms):
    n, owned, tape = word["public"], word["owned_fields"], word["program"]
    assert (n, owned, len(tape)) == (1501, 68, EVENTS)

    @cache
    def span(chart):
        return frozenset(engine["span"](word["frames"][chart]))

    catalogue = geometry(word, price, engine, span)
    state = word["initial"] + [None] * owned
    vectors = [{j: 1} for j in range(n)] + [None] * owned
    fresh, incidents = set(), {r: [] for r in MOVERS}
    for t in range(EVENTS + 1):
        progress["first_unvisited_cut"] = t
        if (t % 128 == 0 or t in CUTS) and monotonic() >= deadline:
            raise TimeoutError("literal prefix cap")
        if t in CUTS:
            assert [state[r] for r in MOVERS] == [LOW, LOW if t == CUTS[0] else HIGH]
            proof = engine["classify"](MOVERS, vectors, cohort)
            exterior = [{j: a for j, a in sorted(vectors[r].items()) if j not in cohort} for r in MOVERS]
            minor = None
            if proof["rank"] == 2:
                axes = proof["minor_axes"]
                matrix = [[v.get(j, 0) for j in axes] for v in exterior]
                det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % PRIME
                assert det == proof["determinant"] != 0 and set(axes).isdisjoint(cohort)
                minor = {"axes": axes, "matrix": matrix, "determinant": det}
            rows[t] = dict(cut=t, old_charts=[state[r] for r in MOVERS],
                full_rows=[dict(vectors[r]) for r in MOVERS], exterior=exterior,
                rank=proof["rank"], minor=minor)
        if t == EVENTS:
            assert state == word["final"] + [None] * owned and not fresh
            progress["first_unvisited_cut"] = None
            break
        event = tape[t]
        op, d, *args = event
        touched = (d, args[0]) if op in ("ADD", "COPY") else (d,)
        for r in touched:
            if r in incidents:
                incidents[r].append(t)
        if op == "MOVE":
            a, b, is_owned = args
            assert span(a) < span(b) or is_owned and span(b) < span(a)
        engine["apply"](event, state, vectors, fresh, n, denoms, False)
        progress["events"] += 1

    neighbors = {}
    for r, times in incidents.items():
        i = bisect_left(times, ANCHORS[r])
        assert 0 < i < len(times) - 1 and times[i] == ANCHORS[r]
        neighbors[r] = [times[i - 1], times[i], times[i + 1]]
    assert neighbors == {572: [42955, 43050, 43051], 1255: [42957, 42958, 42960]}
    assert [max(row[0] + 1 for row in neighbors.values()), min(row[2] for row in neighbors.values())] == [CUTS[0], CUTS[-1]]
    assert [t for t in range(CUTS[0], CUTS[-1]) if any(t in xs for xs in incidents.values())] == [42958]
    # The only incident event inside the half-open alias corridor is a normalized MOVE.
    assert tape[42958] == ["MOVE", 1255, LOW, HIGH, False]
    assert all(rows[t]["full_rows"] == rows[CUTS[0]]["full_rows"] for t in CUTS)
    return dict(nearest_contacts=neighbors, transition_events=[[t, tape[t]] for t in range(CUTS[0], CUTS[-1])],
                distinct_fresh_rank_five_spaces=3, existing_distinct_rank_five_spaces=catalogue,
                shared_normalized_prefix=True)


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    name = "inputs/second_prime.py"
    checked(args.root, name)
    engine = run_path(str(args.root / name))
    controls = engine["controls"]()
    assert engine["PRIME"] == PRIME
    price, cohort = freeze(args.root, engine)
    if args.controls_only:
        print(dumps(dict(controls=controls, raw_keys=price["raw_keys"]), indent=2))
        return 0

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    progress = {"events": 0, "first_unvisited_cut": 0}
    rows, denoms, alias, timeout = {}, set(), None, None
    try:
        payload = decompress(checked(args.root, "inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=engine["unique"])
        alias = sweep(word, price, cohort, engine, monotonic() + 23, progress, rows, denoms)
    except TimeoutError as exc:
        timeout = str(exc)
    finally:
        alarm(0)
    proven = [key for key in price["raw_keys"] if alias is not None and rows[key[0]]["rank"] == 2]
    unresolved = [key for key in price["raw_keys"] if key not in proven]
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, price_caps=price["caps"], controls=controls,
        prime=PRIME, public=MOVERS, projection_cohort_size=len(cohort), rows=list(rows.values()),
        progress=progress, denominator_units=sorted(denoms), alias=alias, timeout=timeout,
        counts=Counter("full prefix rank" if r["rank"] == 2 else "prefix drop" for r in rows.values()),
        raw_excluded=proven, unresolved=unresolved), indent=2, sort_keys=True))
    return 2 if timeout else 0


if __name__ == "__main__":
    raise SystemExit(main())
