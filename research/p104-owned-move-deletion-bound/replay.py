"""Authenticate and exhaust direct deletion eligibility on the #7277 word."""
from argparse import ArgumentParser
from collections import Counter
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import time

HERE = Path(__file__).resolve().parent
WORD = "inputs/WORD.json.gz"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
SHA256 = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
BLOB = "077bf48c35db0ddafae81f1bfa0ffacc30894b2b"


def unique(items):
    value = dict(items)
    assert len(value) == len(items), "duplicate JSON key"
    return value


def read_json(data):
    return json.loads(data, object_pairs_hook=unique)


def owned_followups(word):
    public = word["public"]
    active = set()
    pending = {}
    followups = []
    for i, (op, dst, *args) in enumerate(word["program"]):
        if op == "INIT":
            assert dst >= public and dst not in active and dst not in pending
            active.add(dst)
            continue
        contacts = [(dst, "destination"), (args[0], "source")] if op in ("ADD", "COPY") else [(dst, "role")]
        for role, side in contacts:
            if role < public:
                continue
            assert role in active
            if role in pending:
                record = pending.pop(role)
                if op == "CLEAR":
                    assert args == [record["to_chart"]]
                followups.append({**record, "next": i, "next_op": op, "contact": side})
        if op == "CLEAR":
            active.remove(dst)
        elif op == "MOVE":
            src, target, owned = args
            assert owned == (dst in active)
            if owned:
                rank = abs(len(word["frames"][src]) - len(word["frames"][target]))
                assert rank > 0
                pending[dst] = {
                    "move": i, "role": dst, "from_chart": src,
                    "to_chart": target, "rank": rank,
                }
    assert not pending and not active
    return sorted(followups, key=lambda row: row["move"])


def contact_controls():
    word = {"public": 1, "frames": [[], [1]], "program": [
        ["INIT", 1, 0], ["ADD", 1, 0, "1", 0], ["MOVE", 1, 0, 1, True],
        ["CLEAR", 1, 1], ["INIT", 1, 0], ["ADD", 1, 0, "1", 0],
        ["MOVE", 1, 0, 1, True], ["ADD", 0, 1, "1", 1], ["CLEAR", 1, 1],
        ["INIT", 1, 0], ["MOVE", 1, 0, 1, True], ["INIT", 2, 1],
        ["COPY", 2, 1, "1", 1], ["CLEAR", 2, 1], ["CLEAR", 1, 1],
    ]}
    trace = owned_followups(word)
    assert [(r["move"], r["next_op"], r["contact"]) for r in trace] == [
        (2, "CLEAR", "role"), (6, "ADD", "source"), (10, "COPY", "source")]
    return ["direct_clear_detected", "intervening_add_read_excluded",
            "intervening_copy_read_excluded", "owned_reuse_separate"]


def run():
    pin = read_json((HERE / "PROVENANCE.json").read_bytes())["files"][WORD]
    assert (pin["commit"], pin["sha256"], pin["git_blob"]) == (HEAD, SHA256, BLOB)
    raw = (HERE / WORD).read_bytes()
    assert sha256(raw).hexdigest() == SHA256, "changed exact source word"
    assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == BLOB
    word = read_json(gzip.decompress(raw))
    verifier = runpy.run_path(str(HERE / "verify_zero.py"))
    result = {
        "scientific_head": HEAD, "compressed_word_sha256": SHA256,
        **verifier["audit"](word, time.monotonic(), 18),
        "control": verifier["control"](),
    }
    assert read_json(json.dumps(result)) == read_json((HERE / "RESULT.json").read_bytes())
    assert result["scope_exhausted"] and not result["exact_zero_moves"]
    assert result["fresh_zero_moves"] == 0
    contacts = owned_followups(word)
    counts = Counter(row["rank"] for row in contacts)
    assert counts == result["paid_owned_histogram"]
    assert len(contacts) == result["paid_owned_moves"] == 47
    clear = [row for row in contacts if row["next_op"] == "CLEAR"]
    assert not clear
    return {
        "head": HEAD, "word_sha256": SHA256,
        "paid_owned_moves": len(contacts), "direct_zero": result["exact_zero_moves"],
        "direct_clear": clear, "next_contact_counts": Counter(row["next_op"] for row in contacts),
        "stock_upper": "0", "kappa_change": "0", "unresolved": 0,
        "controls": contact_controls(), "owned_followups": contacts,
    }


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    parser = ArgumentParser(description=__doc__)
    parser.parse_args()
    actual = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    assert actual == (HERE / "CONTACTS.json").read_text()
    print("PASS_OWNED_MOVE_DIRECT_DELETION moves=47 exact_zero=0 direct_clear=0 unresolved=0 stock_upper=0 kappa_change=0")
