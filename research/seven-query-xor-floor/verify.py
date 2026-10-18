#!/usr/bin/env python3
"""Exact seven-query source-XOR floor; read-only default. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import (  # noqa: E402
    CHAMPION_7,
    PR2455_GRAPH_DIGESTS,
    check_identity,
    invoice,
    meet_census,
    min_even_subset_R,
    path_X,
    path_word,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def check_source_pins():
    sources = load_json_reject_duplicates(SOURCES_PATH)
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def build_certificate():
    census = meet_census(n=5, bound=6)
    for row in census["by_length"]:
        length = row["length"]
        need(row["graphs_sha256"] == PR2455_GRAPH_DIGESTS[length], f"digest drift at X={length}")
        need(row["connected_identity_graphs"] == 0, f"unexpected connected restore at X={length}")

    # Component+census floors: first X with query_floor <= 7 is X=6.
    # String keys so JSON round-trips compare equal.
    floors = {str(row["length"]): row["query_floor_n_plus_c"] for row in census["by_length"]}
    need(floors["0"] == 10, "X=0 floor")
    need(floors["2"] == 9, "X=2 floor")
    need(floors["4"] == 8, "X=4 floor")
    need(floors["5"] == 8, "X=5 floor")
    need(floors["6"] == 7, "X=6 floor")
    need(floors["1"] is None and floors["3"] is None, "odd-length restores should be empty")
    for x in range(6):
        floor = floors[str(x)]
        need(floor is None or floor >= 8, f"X={x} must not admit Q=7")
    need(floors["6"] == 7, "X=6 admits Q=7 via c=2")

    # Attaining path-lowered witness at X=6 (credited 789q champion).
    closed = CHAMPION_7
    need(path_X(closed) == 6, "champion path_X")
    slots = tuple(closed[:-1])
    r_total = min_even_subset_R(slots)
    need(r_total == 82, "champion even-subset R")
    word = path_word(closed)
    counts = check_identity(word)
    need(counts["Q"] == 7 and counts["X"] == 6 and counts["R"] == 82, "champion bill")
    bill = invoice(word)
    need(bill["tariff"] == 442, "champion tariff")

    # Edge-count soft bound: X<=2 simple edges => c>=3 => Q>=8 (independent of census).
    # Census strengthens X=2 to c>=4 / Q>=9 and excludes X<=5 for Q=7.
    edge_bound = {
        "argument": "Any interaction graph with e undirected edges on n=5 labels has c>=n-e components. For e<=2, c>=3 so Q>=n+c>=8. Census tightens X=2 to c>=4.",
        "X_le_2_query_floor_from_edges": 8,
        "X_le_2_query_floor_from_census": 9,
    }

    return {
        "schema_version": 1,
        "status": "PASS_SEVEN_QUERY_XOR_FLOOR",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Restored straight-line words. Exact minimum source-XOR count at Q=7."
        ),
        "claim": {
            "Q": 7,
            "min_X": 6,
            "sharp": True,
            "answers_789q_oq1": "No non-path (or path) schedule at Q=7 can reach X<=2; in fact X<=5 is impossible.",
            "no_new_kappa": True,
        },
        "component_lemma": {
            "statement": "An interaction graph with c components forces at least n+c queries on n sources.",
            "n": 5,
        },
        "edge_bound": edge_bound,
        "census": census,
        "query_floors_by_X": floors,
        "attaining_witness": {
            "kind": "path_lowered_even_subset",
            "closed_path": list(closed),
            "Q": 7,
            "R": 82,
            "X": 6,
            "tariff_at_38_2_2": bill["tariff"],
            "invoice": bill,
            "credit": "Path-lowered champion from mutable-source-789q-invoice lineage; PR1898 alphabet.",
        },
        "pr2455_crosscheck": {
            "matched_graph_digests_0_through_6": True,
            "note": "Open PR2455 proves X>=8 at Q=6; this package reuses the same meet-in-the-middle census through X=6 for the Q=7 floor. Per-length graph digests match that package's RESULT.json.",
        },
        "new_kappa": False,
    }


def compare_cert(fresh, committed):
    need(committed.get("status") == "PASS_SEVEN_QUERY_XOR_FLOOR", "bad certificate status")
    need(fresh["claim"] == committed["claim"], "claim drift")
    need(fresh["query_floors_by_X"] == committed["query_floors_by_X"], "floor drift")
    need(fresh["census"]["by_length"] == committed["census"]["by_length"], "census drift")
    need(
        fresh["census"]["last_layer_sha256"] == committed["census"]["last_layer_sha256"],
        "layer digest drift",
    )
    need(fresh["attaining_witness"]["X"] == committed["attaining_witness"]["X"], "witness X drift")
    need(
        fresh["attaining_witness"]["tariff_at_38_2_2"]
        == committed["attaining_witness"]["tariff_at_38_2_2"],
        "witness tariff drift",
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = ap.parse_args(argv)

    check_source_pins()
    fresh = build_certificate()

    if args.write:
        CERT_PATH.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
    else:
        need(CERT_PATH.is_file(), "missing CERTIFICATE.json; author with --write")
        committed = load_json_reject_duplicates(CERT_PATH)
        compare_cert(fresh, committed)

    print(
        "PASS_SEVEN_QUERY_XOR_FLOOR "
        "Q=7 min_X=6 sharp "
        "X<=5 blocked "
        "answers_789q_oq1 "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
