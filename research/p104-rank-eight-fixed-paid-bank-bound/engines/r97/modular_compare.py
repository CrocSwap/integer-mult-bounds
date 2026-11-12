"""Reconcile all R97 frozen bank labels, modular ranks and dispositions."""
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

PINS = {
    "modular/RESULT.json": "6710e8711907a0c8412660696cf821e69fdc42bebf7fc24689fc3385fe7aabf3",
    "lead/CONTINUATION.json": "1f1b1db497436811c3d18219a2277fff6fedc8ad19b7e3c4a486fdfc53c7907a",
}


def unique(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def main(root):
    documents = {}
    for path, digest in PINS.items():
        raw = (root / path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"changed receipt: {path}")
        documents[path] = loads(raw, object_pairs_hook=unique)
    independent, lead = (documents[k] for k in PINS)
    assert independent["head"] == lead["head"]
    assert independent["complete"] and independent["modulus"] == 65537
    assert independent["previously_frozen_exact_keys"] == lead["existing_exact_pending"]
    assert independent["cap_cases"] == lead["case_cap"] == 310
    assert independent["cap_seconds"] == lead["runner_seconds"] == 25
    assert independent["prefix_progress"]["events"] == lead["visited_prefix_events"] == 76466
    assert independent["suffix_progress"]["events"] == lead["visited_suffix_events"] == 76466
    out = []
    for a,b in zip(independent["results"], lead["rows"], strict=True):
        assert a["key"] == b["key"] and a["status"] == b["status"]
        bank = a["prefix"]["bank"]
        assert all(v == b["prefix"][k] for k,v in bank.items())
        assert a["prefix"]["rank"] == b["prefix"]["exterior_rank"]
        assert bool(a["suffix"]) == bool(b["suffix"])
        if a["suffix"]:
            assert a["suffix"]["rank"] == b["suffix"]["suffix_rank_mod_65521"]
            assert all(v == b["suffix"][k] for k,v in bank.items())
        out.append({"key":a["key"], "bank":bank, "status":a["status"],
                    "prefix_rank":a["prefix"]["rank"],
                    "suffix_rank":a["suffix"]["rank"] if a["suffix"] else None})
    assert len(out) == len({tuple(r["key"]) for r in out}) == 310
    print(dumps(dict(head=lead["head"], input_sha256=PINS, moduli=[65521,65537],
        counts=Counter(r["status"] for r in out), rows=out, matched=310), indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main(Path(sys.argv[1]))
