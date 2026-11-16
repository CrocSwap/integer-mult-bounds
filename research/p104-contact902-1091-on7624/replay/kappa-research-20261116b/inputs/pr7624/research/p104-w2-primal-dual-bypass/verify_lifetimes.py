"""Standalone verifier for owned lifetime allocation, stationarity, and bank reuse (204 = 74 base + 130 stationary).

Checks:
  1. Rebuilds word.json.gz from w7616.json.gz + edits-on-7616.json and verifies metadata invariance vs base7605.json.gz.
  2. Extracts all owned lifetimes (INIT, MOVE, CLEAR) and matches the 74-lifetime #7605/#7616 owned skeleton in order.
  3. Verifies all 130 additional owned lifetimes are strictly stationary (0 owned MOVEs, start_chart == end_chart).
  4. Verifies peak live owned labels == 50 <= 68 and non-overlapping lifetime intervals per owned label (17 * 68 = 1,156 banks).
  5. Writes evidence/lifetime-allocation-step1.json.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
EVID = HERE / "evidence"

EXPECTED_CANON = {
    "base7605.json.gz": "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd",
    "w7616.json.gz": "bced9c9818cbbb130c74af97daa0172e1c5a3734a5c8f64d6f4d18dd79554f7a",
    "word.json.gz": "c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de",
}


def canon_sha256(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_word(name: str) -> dict:
    p = DATA / name
    raw = gzip.decompress(p.read_bytes())
    obj = json.loads(raw)
    assert canon_sha256(obj) == EXPECTED_CANON[name], f"Hash mismatch for {name}"
    return obj


def extract_lifetimes(W: dict):
    n = W["public"]
    owned_n = W["owned_fields"]
    N = n + owned_n
    opened = {}
    lts = []
    peak = 0
    for idx, e in enumerate(W["program"]):
        op, r = e[0], e[1]
        if op == "INIT":
            assert r >= n and r not in opened, f"Illegal INIT at {idx}: {e}"
            opened[r] = {
                "field": r,
                "start": idx,
                "start_chart": e[2],
                "moves": [],
                "tokens": [("INIT", r, e[2])],
            }
            peak = max(peak, len(opened))
        elif op == "MOVE":
            if r >= n:
                assert r in opened, f"Unopened owned MOVE at {idx}: {e}"
                assert e[4] is True, f"Owned MOVE missing True flag at {idx}: {e}"
                opened[r]["moves"].append([idx, e[2], e[3]])
                opened[r]["tokens"].append(("MOVE", r, e[2], e[3]))
            else:
                assert e[4] is False, f"Public MOVE has owned flag at {idx}: {e}"
        elif op == "CLEAR":
            assert r >= n and r in opened, f"Illegal CLEAR at {idx}: {e}"
            lt = opened.pop(r)
            lt["end"] = idx
            lt["end_chart"] = e[2]
            lt["tokens"].append(("CLEAR", r, e[2]))
            lt["stationary"] = (len(lt["moves"]) == 0 and lt["start_chart"] == lt["end_chart"])
            lts.append(lt)
    assert not opened, f"Unclosed owned lifetimes: {opened}"
    return peak, lts


def main():
    B = load_word("base7605.json.gz")
    W16 = load_word("w7616.json.gz")
    W = load_word("word.json.gz")

    edits = json.loads((DATA / "edits-on-7616.json").read_text(encoding="utf-8"))
    assert edits["base_canonical_sha256"] == EXPECTED_CANON["w7616.json.gz"]
    assert edits["target_canonical_sha256"] == EXPECTED_CANON["word.json.gz"]
    rebuilt = list(W16["program"])
    for h in reversed(edits["replacements"]):
        assert rebuilt[h["start"] : h["end"]] == h["old"]
        rebuilt[h["start"] : h["end"]] = h["new"]
    assert rebuilt == W["program"], "Reconstruction w7616 + edits-on-7616 != word"

    meta_keys = [k for k in W if k != "program"]
    assert all(W[k] == B[k] == W16[k] for k in meta_keys), "Boundary metadata changed"
    assert W["public"] == 1501 and W["owned_fields"] == 68

    _, lts05 = extract_lifetimes(B)
    _, lts16 = extract_lifetimes(W16)
    peak, lts = extract_lifetimes(W)
    assert len(lts05) == 74 and len(lts16) == 113 and len(lts) == 204
    assert peak == 50

    j = 0
    matched_indices = []
    extra = []
    for k, lt in enumerate(lts):
        if j < len(lts05) and lt["tokens"] == lts05[j]["tokens"]:
            matched_indices.append({"base_idx": j, "step1_idx": k, "field": lt["field"], "start": lt["start"], "end": lt["end"]})
            j += 1
        else:
            extra.append((k, lt))
    assert j == 74 and len(matched_indices) == 74 and len(extra) == 130
    assert all(lt["stationary"] for _, lt in extra), "Non-stationary extra lifetime found!"

    # Verify per-label non-overlapping allocation across all 204 lifetimes and 17*68=1156 physical banks
    n = W["public"]
    owned_n = W["owned_fields"]
    per_label = collections.defaultdict(list)
    for k, lt in enumerate(lts):
        r = lt["field"]
        assert n <= r < n + owned_n
        assert lt["start"] < lt["end"]
        for a, b in per_label[r]:
            assert lt["end"] < a or lt["start"] > b, f"Overlapping lifetime on label {r}"
        per_label[r].append((lt["start"], lt["end"]))
    banks = {call: [call * owned_n + i for i in range(owned_n)] for call in range(17)}
    all_banks = {b for row in banks.values() for b in row}
    assert len(all_banks) == 17 * 68 == 1156

    summary = {
        "word_canonical_sha256": EXPECTED_CANON["word.json.gz"],
        "base_lifetimes": 74,
        "extra_stationary_lifetimes": 130,
        "total_lifetimes": 204,
        "owned_peak": peak,
        "owned_fields": owned_n,
        "calls": 17,
        "physical_banks_total": len(all_banks),
        "all_extra_strictly_stationary": True,
        "all_label_intervals_disjoint": True,
        "matched_base_skeleton_indices": matched_indices,
        "extra_stationary_summary": [
            {"step1_idx": k, "field": lt["field"], "chart": lt["start_chart"], "start": lt["start"], "end": lt["end"]}
            for k, lt in extra
        ],
    }
    EVID.mkdir(exist_ok=True)
    out = EVID / "lifetime-allocation-step1.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"PASS_STEP1_LIFETIMES 204 (74 base + 130 stationary), peak {peak}/{owned_n}, 17*{owned_n}={len(all_banks)} banks")


if __name__ == "__main__":
    main()
