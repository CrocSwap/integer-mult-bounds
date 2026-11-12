"""Check the 2,128 frozen public banks by exact modular suffix minors."""
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "price/KEYS.json": "a131ec5bf96baac89f0f6623cf7d9dff06601b36ea720474311ee7ecb394f6e2",
    "inputs/PRICE.json": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_minor.py": "b25fef5432d8ea9cff9eecc422cf07ccf7473568084de3e8d3d1b5224793504d",
}


def authenticated(root):
    raw = {}
    for path, expected in PINS.items():
        raw[path] = (root / path).read_bytes()
        if sha256(raw[path]).hexdigest() != expected:
            raise ValueError(f"changed dependency: {path}")
    return raw


def reverse_event(event, active, columns, public, scalar, plus, prime):
    op, dst, *args = event
    if op == "MOVE":
        old, new, owned = args
        assert active[dst] == new and owned == (dst >= public)
        active[dst] = old
    elif op == "CLEAR":
        assert dst >= public and active[dst] is None and columns[dst] is None
        active[dst], columns[dst] = args[0], {}
    elif op == "INIT":
        assert dst >= public and active[dst] == args[0]
        active[dst] = columns[dst] = None
    elif op == "SCALE":
        coefficient, chart = args
        assert active[dst] == chart
        factor = scalar(coefficient)
        columns[dst] = {k: factor * v % prime for k, v in columns[dst].items()
                        if factor * v % prime}
    else:
        src, coefficient, chart = args
        assert op in ("ADD", "COPY") and dst != src
        assert active[dst] == active[src] == chart
        # The source contributes to both post-event fields. A guarded COPY
        # replaces the destination, whose required pre-event value is zero.
        plus(columns[src], columns[dst], scalar(coefficient))
        if op == "COPY":
            assert dst >= public
            columns[dst] = {}


def controls(engine):
    scalar, plus, prime = (engine[name] for name in ("scalar", "plus", "P"))
    active = [4, 4, None]
    cols = [{0: 1}, {1: 1}, None]
    tape = [
        ("ADD", 1, 0, "-3/2", 4),
        ("SCALE", 0, "2", 4),
        ("INIT", 2, 4),
        ("COPY", 2, 1, "1", 4),
        ("ADD", 0, 2, "5", 4),
        ("CLEAR", 2, 4),
    ]
    for event in reversed(tape):
        reverse_event(event, active, cols, 2, scalar, plus, prime)
    assert cols == [{0: scalar("-11/2"), 1: scalar("-3/2")}, {0: 5, 1: 1}, None]
    assert active == [4, 4, None]
    minor = engine["exterior_minor"]
    assert minor([0, 1], cols, set())["disposition"] == "excluded"
    assert minor([0, 1], cols, {0})["disposition"] == "rank drop"
    return ["signed two-output impulse with owned COPY and CLEAR",
            "full exterior rank", "planted pure suffix", *engine["controls"]()]


def sweep(word, records, cohort, engine, deadline):
    public = word["public"]
    active = word["final"] + [None] * word["owned_fields"]
    columns = [{i: 1} for i in range(public)] + [None] * word["owned_fields"]
    requests = defaultdict(list)
    for record in records:
        requests[record["key"][0]].append(record)
    scalar, plus, prime, minor = (engine[name] for name in ("scalar", "plus", "P", "exterior_minor"))
    seen, visited = {}, 0
    for cut in range(len(word["program"]), -1, -1):
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        for record in requests.get(cut, ()):
            chart = record["key"][1]
            public_bank = [r for r in range(public) if active[r] == chart]
            owned_bank = [r for r in range(public, len(active)) if active[r] == chart]
            assert public_bank == record["public"] and owned_bank == record["owned"]
            assert sorted(set(public_bank) & cohort) == record["pivots"]
            result = minor(public_bank, columns, cohort)
            seen[tuple(record["key"])] = {
                "key": record["key"], "public": public_bank, "owned": owned_bank,
                "pivots": record["pivots"], "prefix_rank_mod_65521": record["exterior_rank"],
                "suffix_rank_mod_65521": result["exterior_rank"], "output_minor_rows": result["columns"],
                "determinant_mod_65521": result["determinant"], "disposition": result["disposition"],
            }
        if not cut:
            assert active == word["initial"] + [None] * word["owned_fields"]
            break
        reverse_event(word["program"][cut - 1], active, columns, public, scalar, plus, prime)
        visited += 1
    return seen, visited


def main():
    assert __debug__
    deadline = monotonic() + 32
    root = Path(sys.argv[1])
    raw = authenticated(root)
    engine = run_path(str(root / "inputs/exterior_minor.py"))
    unique = engine["unique"]
    frozen = json.loads(raw["price/KEYS.json"], object_pairs_hook=unique)
    price = json.loads(raw["inputs/PRICE.json"], object_pairs_hook=unique)
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]), object_pairs_hook=unique)
    assert frozen["head"] == price["head"] == HEAD
    assert frozen["source_sha256"]["inputs/7334-WORD.json.gz"] == PINS["inputs/7334-WORD.json.gz"]
    assert frozen["source_sha256"]["inputs/PRICE.json"] == PINS["inputs/PRICE.json"]
    records = frozen["keys"]
    keys = [tuple(row["key"]) for row in records]
    assert len(keys) == len(set(keys)) == frozen["reverse_case_cap"] == 2128
    cohort = set(price["endpoint_cohort"])
    assert len(cohort) == 615
    checks = controls(engine)
    found, visited = sweep(word, records, cohort, engine, deadline)
    results = [found[k] for k in keys if k in found]
    pending = [list(k) for k in keys if k not in found]
    print(json.dumps({
        "head": HEAD, "pins": PINS, "scope": "normalized suffix on the frozen public bank only",
        "prime": engine["P"], "cases_cap": 2128, "seconds_cap": 32, "events_processed": visited,
        "status": "CAPPED" if pending or visited != len(word["program"]) else "EXHAUSTED",
        "controls": checks, "counts": Counter(row["disposition"] for row in results),
        "results": results, "unvisited": pending,
        "rank_drops": [row["key"] for row in results if row["disposition"] == "rank drop"],
    }, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
