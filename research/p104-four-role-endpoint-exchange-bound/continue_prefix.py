"""Resume exactly the seven capped, unvisited R151 native exchange cuts."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
BASIS = "3ff8748c0bcbcceea120265f87d92263cccd17343ef504efbe3b401ca05e4f0b"
PREFIX = "6525f616502fe23c155e5c96138e85142401c8fdfddc266c6aa1ced64299da8d"
OLD_KEYS = (
    (996, 1481, 1454, 1251, 245, 45688),
    (438, 1481, 1454, 1251, 245, 45222),
    (996, 1481, 1454, 1251, 245, 45222),
    (1195, 1481, 1454, 1251, 245, 45222),
    (438, 1481, 1454, 1251, 245, 45219),
    (996, 1481, 1454, 1251, 245, 45219),
    (1195, 1481, 1454, 1251, 245, 45219),
)
SECONDS = 25


def stop(*_):
    raise TimeoutError("25-second continuation cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 1
    assert sha256((ROOT / "lead/basis.py").read_bytes()).hexdigest() == BASIS
    basis = run_path(str(ROOT / "lead/basis.py"))
    checked = basis["checked"]
    checked(ROOT, "inputs/reverse_span.py")
    engine = run_path(str(ROOT / "inputs/reverse_span.py"))
    controls = basis["controls"](engine)
    prior = loads(checked(ROOT, "lead/PREFIX.json", PREFIX), object_pairs_hook=engine["unique"])
    assert prior["counts"] == {"exact_rank_exclusion": 8}
    assert prior["pins"] == basis["PINS"]
    keys = prior["unvisited"]
    assert tuple(map(tuple, keys)) == OLD_KEYS
    geometry = loads(checked(ROOT, "lead/GEOMETRY.json"), object_pairs_hook=engine["unique"])
    assert basis["selection"](geometry) == prior["selected"] + keys
    price = loads(checked(ROOT, "lead/PRICE.json"), object_pairs_hook=engine["unique"])
    assert price["compatible_edit_cap"] == 1 and price["extra_paid"] == 0
    assert (price["paid"], price["productive"], price["surplus"]) == (110519, 22461, 1424)
    raw = decompress(checked(ROOT, "inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == basis["PAYLOAD"]
    word = loads(raw, object_pairs_hook=engine["unique"])
    assert len(word["program"]) == basis["EVENTS"]

    results, unresolved, timeout = [], [], None
    try:
        results = [{"key": r, "proof": p} for r, p in basis["prefix"](word, keys, engine, deadline)]
    except TimeoutError as err:
        timeout = str(err)
        unresolved = keys[len(results):]
    alarm(0)
    print(dumps({
        "head": price["head"], "caller": price["caller"], "controls": controls,
        "inherited_pins": basis["PINS"], "basis_sha256": BASIS, "prior_prefix_sha256": PREFIX,
        "original_prefix_exclusions": 8, "selected": keys, "cap_seconds": SECONDS,
        "counts": Counter(row["proof"]["status"] for row in results), "results": results,
        "still_unvisited": unresolved, "timeout": timeout,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
