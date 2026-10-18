#!/usr/bin/env python3
"""Exact seven-query even-subset R floor among X=6; read-only default.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
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
    check_identity,
    enumerate_distinct6_R_spectrum,
    invoice,
    min_even_subset_R,
    path_X,
    path_word,
    repeat_layer_basis_census,
    span_obstruction_samples,
    tariff_qrx,
    valid_walk_slots,
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
    # Layer A: distinct 6-nonzero slot sets (Hamiltonian connector walks).
    distinct = enumerate_distinct6_R_spectrum()
    need(distinct["min_R"] == 82, "unexpected distinct-6 min R")
    need(distinct["attainable_R"] == [82, 88], f"unexpected spectrum {distinct['attainable_R']}")
    need(
        distinct["histogram"] == {"82": 97216, "88": 486080},
        f"unexpected histogram {distinct['histogram']}",
    )
    need(distinct["covering_sets"] == 583296, "unexpected covering count")

    # Layer B: one-repeat walks on a spanning 5-set (GL-reduced to the basis).
    repeats = repeat_layer_basis_census()
    need(repeats["min_R"] == 96, "unexpected one-repeat min R")
    need(repeats["attainable_R"] == [96], f"unexpected repeat spectrum {repeats['attainable_R']}")
    need(repeats["covering_walks"] == 1680, f"unexpected repeat covering {repeats['covering_walks']}")
    need(valid_walk_slots(tuple(repeats["first_witness"])), "repeat witness not a valid walk")

    # Layer C: fewer than five independent nonzero labels cannot span F2^5.
    samples = span_obstruction_samples()
    for row in samples:
        need(row["rank"] < 5, f"sample {row['note']} should be dependent")
        need(not row["covers_all_31"], f"sample {row['note']} should not cover")
        need(row["best_even_subset_image_size"] <= 16, f"sample {row['note']} image too large")

    # Classification: every covering Q=7 even-subset slot list has either
    # six distinct nonzero labels (R in {82,88}) or a one-repeat spanning
    # five-set (R=96). Hence global min R is 82.
    min_R = 82
    need(min(distinct["min_R"], repeats["min_R"]) == min_R, "global min R")

    # Sharpness at X=6: credited champion attains R=82 with path-local X=6.
    # Combined with the #2643 restored XOR floor X>=6 at Q=7 (cited; not reopened),
    # every restored seven-query word with X=6 has R>=82, and 82 is attained.
    closed = CHAMPION_7
    need(path_X(closed) == 6, "champion path_X")
    slots = tuple(closed[:-1])
    need(valid_walk_slots(slots), "champion slots")
    need(min_even_subset_R(slots) == 82, "champion R")
    word = path_word(closed)
    counts = check_identity(word)
    need(dict(counts) == {"Q": 7, "R": 82, "X": 6}, f"champion counts {counts}")
    bill = invoice(word)
    need(bill["tariff"] == 442, f"champion tariff {bill}")
    need(tariff_qrx(7, 82, 6) == 442, "tariff arithmetic")
    need(tariff_qrx(7, 78, 6) == 434, "undercut threshold arithmetic")
    need(434 < 436 < 442, "R<=78 would undercut 436; R=82 cannot")

    return {
        "schema_version": 1,
        "status": "PASS_SEVEN_QUERY_R_FLOOR",
        "scope": (
            "Five-source common-B mutable-source Q/R/X alphabet (PR1898). "
            "Even-subset readout on connector states of restored straight-line "
            "words with exactly seven queries. Exact minimum R among words with X=6."
        ),
        "claim": {
            "Q": 7,
            "min_R_among_X_eq_6": 82,
            "min_R_even_subset_all_walks": 82,
            "sharp": True,
            "answers_7qxor_oq1": (
                "Minimum even-subset R among restored seven-query words with X=6 "
                "is exactly 82; R<=78 is impossible in this readout class, so the "
                "abstract tariff cannot undercut 436 via lower R at X=6."
            ),
            "no_new_kappa": True,
        },
        "classification": {
            "distinct_six_nonzero": distinct,
            "one_repeat_spanning_five": repeats,
            "span_obstruction_samples": samples,
            "argument": (
                "A covering even-subset slot list of length 7 must span F2^5, so it "
                "uses at least five linearly independent nonzero labels. With six "
                "intermediate slots after the leading 0, the covering cases are: "
                "(i) six distinct nonzero labels (Hamilton walks; R in {82,88}); "
                "(ii) five spanning nonzero labels with exactly one repeated vertex "
                "(R=96 on the GL(5) basis census). Fewer independent labels cannot "
                "cover. Therefore min R = 82."
            ),
        },
        "xor_floor_citation": {
            "object": "research/seven-query-xor-floor (CrocSwap #2643)",
            "statement": "Every restored seven-query word needs X>=6; sharp via the same champion.",
            "use_here": "Together with min even-subset R=82, every X=6 word has R>=82.",
            "not_reopened": True,
        },
        "attaining_witness": {
            "kind": "path_lowered_even_subset",
            "closed_path": list(closed),
            "Q": 7,
            "R": 82,
            "X": 6,
            "tariff_at_38_2_2": bill["tariff"],
            "invoice": bill,
            "credit": (
                "Path-lowered champion from mutable-source-789q-invoice / "
                "seven-query-xor-floor lineage; PR1898 alphabet."
            ),
        },
        "tariff": {
            "complete_prices": {"b": 38, "a": 2, "x": 2},
            "six_query_endpoint": 436,
            "beat_436_at_Q7_X6_requires_R_le": 78,
            "min_tariff_at_Q7_X6": 442,
            "undercuts_436": False,
        },
        "new_kappa": False,
    }


def compare_cert(fresh, committed):
    need(committed.get("status") == "PASS_SEVEN_QUERY_R_FLOOR", "bad certificate status")
    need(fresh["claim"] == committed["claim"], "claim drift")
    need(
        fresh["classification"]["distinct_six_nonzero"]["histogram"]
        == committed["classification"]["distinct_six_nonzero"]["histogram"],
        "distinct histogram drift",
    )
    need(
        fresh["classification"]["one_repeat_spanning_five"]["histogram"]
        == committed["classification"]["one_repeat_spanning_five"]["histogram"],
        "repeat histogram drift",
    )
    need(
        fresh["attaining_witness"]["R"] == committed["attaining_witness"]["R"],
        "witness R drift",
    )
    need(
        fresh["attaining_witness"]["tariff_at_38_2_2"]
        == committed["attaining_witness"]["tariff_at_38_2_2"],
        "witness tariff drift",
    )
    need(fresh["tariff"] == committed["tariff"], "tariff block drift")


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
        "PASS_SEVEN_QUERY_R_FLOOR "
        "Q=7 min_R_among_X=6 is 82 sharp "
        "repeat_layer_R=96 "
        "answers_7qxor_oq1 "
        "tariff_floor=442 "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
