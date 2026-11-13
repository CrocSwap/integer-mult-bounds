"""Portable exact native-word row rebuild; reads inputs and returns a document."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path

from helper_funding_common import (
    AUTHOR_ROWS_SHA256,
    EXPECTED_RECORDS_SHA256,
    EXPECTED_TARGETS_SHA256,
    WORD_SHA256,
    ValidationError,
    digest_bytes,
    digest_json,
    read_json,
    require,
    validate_rebuilt_doc,
)


def _gf2_rank(vectors):
    basis = {}
    for raw in vectors:
        x = int(raw)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def _add(dst, src, q):
    for h, v in src.items():
        z = dst.get(h, Q(0)) + q * v
        if z:
            dst[h] = z
        else:
            dst.pop(h, None)


def _rebuild_bytes(raw: bytes, author_rows: dict, author_rows_sha: str):
    """Internal byte entry point, also exercised with a mutated word in controls."""
    source_sha = digest_bytes(raw)
    require(source_sha == WORD_SHA256, "native source hash mismatch")
    require(author_rows_sha == AUTHOR_ROWS_SHA256, "author row file hash mismatch")
    require(author_rows.get("source_sha256") == WORD_SHA256, "author rows point to another source")
    w = json.loads(gzip.decompress(raw))
    n = w["public"]
    require(n == 1501 and w["owned_fields"] == 68, "native word shape mismatch")
    require(all(_gf2_rank(frame) == len(frame) for frame in w["frames"]),
            "native frame vector list is not an independent GF(2) basis")
    mains = (set(w["live"]) | {i + 112 for i in w["live"]} |
             set(w["hosted"]["X2"]) | set(w["hosted"]["Y2"]))
    require(len(mains) == 400 and max(mains) < n, "native main input partition mismatch")
    helpers = set(range(n)) - mains
    require(len(helpers) == 1101, "native helper input partition mismatch")
    targets = {h: len(w["frames"][w["final"][h]]) -
               len(w["frames"][w["initial"][h]]) for h in helpers}
    require(all(1 <= r <= 9 for r in targets.values()), "native helper target rank domain")

    rows = [{i: Q(1)} for i in range(n)] + [None] * w["owned_fields"]
    charts = w["initial"].copy() + [None] * w["owned_fields"]
    fresh = set()
    records = []
    nonzero_main_moves = 0
    counts = Counter()
    for event, e in enumerate(w["program"]):
        op, a = e[:2]
        counts[op] += 1
        if op == "MOVE":
            old, new = e[2:4]
            require(rows[a] is not None and charts[a] == old, f"invalid MOVE source at {event}")
            require(bool(e[4]) == (a >= n), f"MOVE owner flag mismatch at {event}")
            require(bool(rows[a]), f"unconditional zero MOVE at {event}")
            if not (set(rows[a]) & mains):
                require(set(rows[a]) <= helpers, f"main-free MOVE has non-helper support at {event}")
                records.append({
                    "event": event,
                    "owner": a,
                    "owned": bool(e[4]),
                    "rank": abs(len(w["frames"][old]) - len(w["frames"][new])),
                    "row": {str(h): str(v) for h, v in sorted(rows[a].items())},
                })
            else:
                require(any(h in mains and q for h, q in rows[a].items()),
                        f"excluded MOVE lacks a nonzero main coefficient at {event}")
                nonzero_main_moves += 1
            charts[a] = new
            fresh.discard(a)
        elif op == "INIT":
            require(a >= n and charts[a] is None and rows[a] is None,
                    f"invalid owned INIT at {event}")
            charts[a], rows[a] = e[2], {}
            fresh.add(a)
        elif op == "CLEAR":
            require(a >= n and charts[a] == e[2] and rows[a] is not None,
                    f"invalid owned CLEAR at {event}")
            charts[a], rows[a] = None, None
            fresh.discard(a)
        elif op == "SCALE":
            require(rows[a] is not None and charts[a] == e[-1], f"invalid SCALE at {event}")
            q = Q(e[2])
            require(q != 0, f"zero SCALE at {event}")
            rows[a] = {h: q * v for h, v in rows[a].items() if q * v}
            fresh.discard(a)
        elif op in ("ADD", "COPY"):
            b = e[2]
            require(a != b and rows[a] is not None and rows[b] is not None and
                    charts[a] == charts[b] == e[-1], f"invalid coframed {op} at {event}")
            if op == "COPY":
                require(a >= n and a in fresh and not rows[a],
                        f"COPY not into fresh zero at {event}")
            _add(rows[a], rows[b], Q(e[3]))
            fresh.discard(a)
        else:
            raise ValidationError(f"unknown native operation {op}")

    require(charts == w["final"] + [None] * w["owned_fields"], "native final chart/lifetime mismatch")
    require(all(rows[h] == {h: Q(1)} for h in helpers), "native helper endpoint changed")
    require(all(not (set(rows[m]) & helpers) for m in mains), "native main endpoint uses helper")
    require(len(records) == 468 and nonzero_main_moves == 5811, "native MOVE partition mismatch")
    used = {int(h) for rec in records for h in rec["row"]}
    require(len(used) == 806, "native used-helper support width mismatch")
    record_hash = digest_json(records)
    target_map = {str(h): targets[h] for h in sorted(helpers)}
    target_hash = digest_json(target_map)
    require(record_hash == EXPECTED_RECORDS_SHA256, "reconstructed row inventory differs from pinned native inventory")
    require(target_hash == EXPECTED_TARGETS_SHA256, "reconstructed target weights differ from pinned native inventory")
    require(author_rows.get("records") == records, "author rows disagree with fresh source replay")
    require(author_rows.get("targets") == target_map, "author target weights disagree with fresh source replay")

    doc = {
        "schema": "helper-funding-rebuilt-v1",
        "source_sha256": source_sha,
        "author_rows_sha256": author_rows_sha,
        "public_inputs": n,
        "main_coordinates": len(mains),
        "helper_coordinates": len(helpers),
        "instruction_count": len(w["program"]),
        "move_count": counts["MOVE"],
        "main_free_move_rows": len(records),
        "nonzero_main_move_rows": nonzero_main_moves,
        "used_helper_columns": len(used),
        "frame_basis_check": True,
        "records_sha256": record_hash,
        "target_ranks_sha256": target_hash,
        "helper_target_ranks": target_map,
        "records": records,
    }
    validate_rebuilt_doc(doc)
    return doc


def rebuild(word_path, author_rows_path):
    """Return source-bound exact row data. This function does not write files."""
    raw = Path(word_path).read_bytes()
    author_raw = Path(author_rows_path).read_bytes()
    author_sha = digest_bytes(author_raw)
    require(author_sha == AUTHOR_ROWS_SHA256, "author ROWS file hash mismatch")
    author_rows = json.loads(author_raw)
    return _rebuild_bytes(raw, author_rows, author_sha)
