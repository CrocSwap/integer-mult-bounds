"""Verify only the 16 frozen R102 prefix keys at a second exact prime."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/PRICE.json": "4e0d6436eb4fc6a9dfa34c05ba98aacc63e3a8bf7214145dd9f9254763c5a13e",
    "inputs/GEOMETRY.json": "2d0dee60998d168d2eff4c16794176c5ec3b4d18ffa8bde247602035f1b68129",
    "inputs/PREFIX.json": "65c11b0a42092557fe1c64b4feb2f61e2d16c636cfcaddf7f95ec09dbdd27452",
    "inputs/7334-WORD.json.gz": WORD,
    "inputs/second_prime.py": "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
}
PRIME, CAP, SECONDS, EVENTS = 65537, 16, 25, 76466


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def pinned(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency: {name}")
    return raw


def freeze(raw):
    price, geom, primary = [loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)
                            for name in ("PRICE", "GEOMETRY", "PREFIX")]
    assert price["head"] == geom["head"] == primary["head"] == HEAD
    assert price["caller"] == CALLER and price["word_sha256"] == geom["word_sha256"] == WORD
    assert geom["price_sha256"] == primary["pins"]["lead/PRICE.json"] == PINS["inputs/PRICE.json"]
    assert primary["pins"]["lead/GEOMETRY.json"] == PINS["inputs/GEOMETRY.json"]
    assert primary["pins"]["inputs/7334-WORD.json.gz"] == WORD
    assert geom["status"] == "EXHAUSTED" and geom["visited_events"] == primary["event_count"] == EVENTS
    assert geom["bank_cap"] == price["support_cap"] == primary["case_cap"] == CAP
    assert primary["runner_seconds"] == price["support_runner_seconds"] == SECONDS
    assert geom["ranks"] == price["cut_ranks"] == [5, 6] and price["endpoint_charts"] == [602, 127]
    assert primary["counts"] == {"excluded": CAP} and not primary["unvisited"]
    cohort = set(price["cohort"])
    assert cohort == {1457, 1458, 1474, 1475, 1476}
    selected = {tuple(row["key"]): row for row in geom["selected"]}
    assert len(selected) == len(geom["selected"]) == CAP
    earlier = {tuple(row["key"]): row for row in primary["rows"]}
    assert list(selected) == list(earlier)
    unselected = list(map(tuple, geom["unvisited_keys"]))
    assert list(map(tuple, primary["unselected"])) == unselected and len(set(unselected)) == 49
    assert set(unselected).isdisjoint(selected) and len(geom["all_representative_keys"]) == 65
    assert set(unselected) | selected.keys() == set(map(tuple, geom["all_representative_keys"]))
    for key in selected:
        a, b = selected[key], earlier[key]
        assert all(a[field] == b[field] for field in ("public", "owned", "pivots"))
        assert b["exterior_rank"] == len(a["public"]) and b["determinant"]
    return cohort, selected, earlier, unselected


def sweep(word, cohort, selected, earlier, engine, deadline, progress, results):
    n, owned, tape = (word[k] for k in ("public", "owned_fields", "program"))
    assert (n, owned, len(tape)) == (1501, 68, EVENTS)
    assert all((word["initial"][r], word["final"][r]) == (602, 127) for r in cohort)
    frames = word["frames"]
    span = engine["span"]
    low, high = span(frames[602]), span(frames[127])
    assert len(low) == 4 and len(high) == 512 and low < high
    requests = defaultdict(list)
    for cut, chart in selected:
        assert 0 <= cut <= EVENTS and len(frames[chart]) in (5, 6) and low < span(frames[chart]) < high
        requests[cut].append(chart)

    active = word["initial"] + [None] * owned
    vectors = [{r: 1} for r in range(n)] + [None] * owned
    fresh, denoms = set(), set()
    progress.update(events=0, first_unvisited_cut=0)
    for cut in range(EVENTS + 1):
        progress["first_unvisited_cut"] = cut
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        for chart in requests.get(cut, ()):
            key = cut, chart
            bank = [r for r in range(n) if active[r] == chart]
            owners = [r for r in range(n, n + owned) if active[r] == chart]
            pivots = sorted(set(bank) & cohort)
            assert pivots and bank == selected[key]["public"] and owners == selected[key]["owned"]
            assert pivots == selected[key]["pivots"]
            if cut:
                last = tape[cut - 1]
                assert chart in (last[2:4] if last[0] == "MOVE" else last[-1:])
            proof = engine["classify"](bank, vectors, cohort)
            primary_columns = earlier[key]["columns"]
            assert len(primary_columns) == len(set(primary_columns)) == len(bank)
            assert cohort.isdisjoint(primary_columns)
            determinant = engine["verify_minor"]([vectors[r] for r in bank], primary_columns)
            results[key] = dict(key=key, chart_rank=len(frames[chart]), public=bank, owned=owners, pivots=pivots,
                independent_minor=proof, primary_minor_axes=primary_columns,
                primary_minor_det_mod_65537=determinant,
                disposition="excluded" if not proof["kernel"] else "modular_rank_drop")
        if cut == EVENTS:
            assert active == word["final"] + [None] * owned and not fresh
            assert len(results) == CAP
            progress["first_unvisited_cut"] = None
            break
        engine["apply"](tape[cut], active, vectors, fresh, n, denoms, False)
        progress["events"] += 1
    progress["denominator_units"] = sorted(denoms)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    assert __debug__ and sys.version_info[:2] == (3, 12)

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 2
    selected, unselected, result, progress, checks = {}, [], {}, {}, []
    timeout = None
    try:
        raw = {rel: pinned(args.root, rel) for rel in PINS}
        cohort, selected, earlier, unselected = freeze(raw)
        engine = run_path(str(args.root / "inputs/second_prime.py"))
        assert engine["PRIME"] == PRIME
        checks = engine["controls"]()
        payload = decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=unique)
        sweep(word, cohort, selected, earlier, engine, deadline, progress, result)
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)

    rows = [result[k] for k in selected if k in result]
    visited_all = timeout is None and progress.get("first_unvisited_cut", 0) is None
    agreement = visited_all and all(row["disposition"] == "excluded" for row in rows)
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, modulus=PRIME, cap_cases=CAP, cap_seconds=SECONDS,
        progress=progress, controls=checks, complete=visited_all, primary_agreement=agreement, timeout=timeout,
        counts=Counter(row["disposition"] for row in rows), rows=rows,
        unvisited_selected=[k for k in selected if k not in result], unselected=unselected), indent=2, sort_keys=True))
    if not agreement:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
