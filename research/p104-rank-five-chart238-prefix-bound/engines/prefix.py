"""Check the 18 frozen rank-five 3→238 exterior prefixes at prime 65537."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/GEOMETRY.json": "c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
    "inputs/PRICE.json": "c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/second_prime.py": "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
    "inputs/7334-WORD.json.gz": WORD,
}
GROUP = [3, 238]
COHORT = {325, 1087}
EVENTS, CASES, SECONDS, PRIME = 76466, 18, 25, 65537


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency " + name)
    return raw


def freeze(root):
    price = loads(checked(root, "inputs/PRICE.json"), object_pairs_hook=unique)
    geometry = loads(checked(root, "inputs/GEOMETRY.json"), object_pairs_hook=unique)
    assert price["head"] == geometry["head"] == HEAD and price["caller"] == CALLER
    assert price["word_sha256"] == geometry["pins"]["inputs/7334-WORD.json.gz"] == WORD
    assert geometry["pins"]["lead/PRICE.json"] == PINS["inputs/PRICE.json"]
    assert geometry["status"] == "EXHAUSTED" and geometry["visited_events"] == EVENTS
    assert len(price["groups"]) == 28 and len(geometry["candidate_rows"]) == 68
    assert [set(g["roles"]) for g in price["groups"] if g["endpoints"] == GROUP] == [COHORT]
    chosen = {tuple(r["key"][:2]): r for r in geometry["candidate_rows"] if r["key"][2:] == GROUP}
    assert len(chosen) == CASES
    return chosen


def prefix(word, chosen, engine, deadline, progress, results, denoms):
    n, owned, tape = (word[k] for k in ("public", "owned_fields", "program"))
    assert (n, owned, len(tape)) == (1501, 68, EVENTS)
    assert all([word["initial"][r], word["final"][r]] == GROUP for r in COHORT)
    frames = word["frames"]

    @cache
    def span(label):
        return engine["span"](frames[label])

    low, high = map(span, GROUP)
    assert len(low) == 1 and len(high) == 32 and low < high
    by_cut = defaultdict(list)
    for cut, chart in chosen:
        assert 0 <= cut <= EVENTS and len(frames[chart]) in (2, 3)
        assert low < span(chart) < high
        by_cut[cut].append(chart)

    active = word["initial"] + [None] * owned
    vectors = [{i: 1} for i in range(n)] + [None] * owned
    fresh = set()
    for cut in range(EVENTS + 1):
        progress["first_unvisited_cut"] = cut
        if (cut % 128 == 0 or cut in by_cut) and monotonic() >= deadline:
            raise TimeoutError("bounded literal prefix")
        for chart in by_cut.get(cut, ()):
            key = cut, chart
            public = [r for r in range(n) if active[r] == chart]
            owners = [r for r in range(n, n + owned) if active[r] == chart]
            pivots = sorted(set(public) & COHORT)
            assert public == chosen[key]["public"] and owners == chosen[key]["owned"]
            assert pivots and pivots == chosen[key]["pivots"]
            proof = engine["classify"](public, vectors, COHORT)
            exterior = [{i: v for i, v in vectors[r].items() if i not in COHORT} for r in public]
            results[key] = dict(key=key, chart_rank=len(frames[chart]), public=public,
                owned=owners, pivots=pivots, exterior_rows=exterior, independent_minor=proof,
                disposition="prefix exclusion" if not proof["kernel"] else "modular rank drop")
        if cut == EVENTS:
            assert active == word["final"] + [None] * owned and not fresh
            assert len(results) == CASES
            progress["first_unvisited_cut"] = None
            break
        event = tape[cut]
        if event[0] == "MOVE":
            old, new, is_owned = event[2:]
            assert span(old) < span(new) or is_owned and span(new) < span(old)
        engine["apply"](event, active, vectors, fresh, n, denoms, False)
        progress["events"] += 1


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    name = "inputs/second_prime.py"
    checked(args.root, name)
    engine = run_path(str(args.root / name))
    assert engine["PRIME"] == PRIME
    controls = engine["controls"]()
    chosen = freeze(args.root)
    if args.controls_only:
        print(dumps(dict(controls=controls, frozen_keys=list(chosen)), indent=2))
        return 0

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + 23
    progress = {"events": 0, "first_unvisited_cut": 0}
    output, denoms, timeout = {}, set(), None
    try:
        payload = decompress(checked(args.root, "inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest() == PAYLOAD
        prefix(loads(payload, object_pairs_hook=unique), chosen, engine, deadline, progress, output, denoms)
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)
    rows = [output[key] for key in chosen if key in output]
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, group=GROUP, cohort=sorted(COHORT),
        prime=PRIME, cases=CASES, seconds=SECONDS, controls=controls, timeout=timeout,
        rows=rows, progress=progress, denominator_units=sorted(denoms),
        counts=Counter(r["disposition"] for r in rows),
        unresolved=[key for key in chosen if key not in output or output[key]["disposition"] != "prefix exclusion"]),
        indent=2, sort_keys=True))
    return 2 if timeout else 0


if __name__ == "__main__":
    raise SystemExit(main())
