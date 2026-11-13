"""Build and verify the normalized chart-115 two-ADD cancellation."""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm
from sys import version_info

ROOT = Path(__file__).resolve().parent.parent
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "next-chart115/retained_independent.py": "21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874",
}
FIRST, LAST = 36448, 38004
ROLES = {751, 1276}
CONTACTS = {
    FIRST: ["ADD", 1276, 751, "-1", 3],
    38002: ["MOVE", 1276, 3, 115, False],
    38003: ["MOVE", 751, 3, 115, False],
    LAST: ["ADD", 1276, 751, "1", 115],
}


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-word", type=Path)
    args = parser.parse_args()
    alarm(30)
    for path, digest in PINS.items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest
    source = gzip.decompress((ROOT / "inputs/7481-WORD.json.gz").read_bytes())
    assert sha256(source).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(source)
    program = word["program"]
    assert len(program) == 76475
    found = {i: e for i, e in enumerate(program)
             if e[1] in ROLES or e[0] in ("ADD", "COPY") and e[2] in ROLES}
    assert found == CONTACTS
    h = word["hosted"]
    protected = set(word["live"]) | {r + 112 for r in word["live"]} | set(h["X2"]) | set(h["Y2"])
    assert len(protected) == 400 and not (protected & ROLES)
    assert all(word["initial"][r] == 3 and word["final"][r] == 115 for r in ROLES)
    assert not word["frames"][3] and len(word["frames"][115]) == 5
    native = run_path(str(ROOT / "next-chart115/retained_independent.py"))["native"]
    edit = dict(word, program=[e for i, e in enumerate(program) if i not in (FIRST, LAST)])
    mutant = dict(word, program=program[:FIRST] + program[FIRST + 1:])
    old = native(word)
    new = native(edit)
    bad = native(mutant)
    assert not old["bad_inputs"] and not new["bad_inputs"]
    assert bad["bad_inputs"] == [751]
    assert new["events"] == old["events"] - 2
    assert {k: v for k, v in new.items() if k != "events"} == {k: v for k, v in old.items() if k != "events"}
    operations = Counter(e[0] for e in program)
    operations.subtract(e[0] for e in edit["program"])
    assert +operations == Counter({"ADD": 2}) and not -operations
    payload = dumps(edit, sort_keys=True, separators=(",", ":")).encode()
    if args.write_word:
        with args.write_word.open("xb") as out:
            out.write(gzip.compress(payload, mtime=0))
    print(dumps({"status": "PASS_NORMALIZED_CHART115_CANCELLATION", "pins": PINS,
                 "word_sha256": sha256(payload).hexdigest(), "old": old, "new": new,
                 "omitted_one_add_bad_inputs": bad["bad_inputs"]}, sort_keys=True))
    alarm(0)


if __name__ == "__main__":
    main()
