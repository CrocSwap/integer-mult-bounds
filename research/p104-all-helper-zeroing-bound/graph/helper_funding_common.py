"""Shared pins and validators for the portable, read-only review engines."""
from __future__ import annotations

from hashlib import sha256
import json

WORD_SHA256 = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
AUTHOR_ROWS_SHA256 = "15de6d0e53a846efdd5d3f9b34beb8d57fc51534967cc464b12c305ed2cf1834"
AUTHOR_MATROID_SHA256 = "32a0f298f0ace5f0ff1a91b5a9b4e0f32984abd75f56f6f9259ca5c6b4dae74b"
AUTHOR_POWER_SHA256 = "2eb198d365cf6d4d3d689559e0fccf4a0b866d4fc949110475e5aec5cb0dfb5e"
EXPECTED_RECORDS_SHA256 = "72dac0430ce655b17d49699939485e87b580308ac69f5fe2d871b2b89099d6c2"
EXPECTED_TARGETS_SHA256 = "68c2462fe8e7f76d56c77f733e98ffa5d46e13a6fe801e043c1ec748704011f1"
EXPECTED_STRUCTURE_DOC_SHA256 = "593a8956cf115ba06ca52fd2ffb4d76f1b84f3973a6fe137f9cf0656cc158084"


class ValidationError(ValueError):
    """Raised for a source, inventory, or certificate validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def digest_bytes(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def digest_json(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return digest_bytes(raw)


def read_json(path):
    from pathlib import Path
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_rebuilt_doc(doc):
    """Validate the exact source-bound row inventory used by later stages."""
    require(isinstance(doc, dict), "rebuilt document is not an object")
    require(doc.get("schema") == "helper-funding-rebuilt-v1", "rebuilt schema mismatch")
    require(doc.get("source_sha256") == WORD_SHA256, "rebuilt source hash mismatch")
    require(doc.get("author_rows_sha256") == AUTHOR_ROWS_SHA256, "rebuilt author-row pin mismatch")
    require(doc.get("public_inputs") == 1501 and doc.get("main_coordinates") == 400 and
            doc.get("helper_coordinates") == 1101, "rebuilt input partition mismatch")
    require(doc.get("instruction_count") == 76475 and doc.get("move_count") == 6279,
            "rebuilt source event counts mismatch")
    require(doc.get("frame_basis_check") is True, "frame basis validation missing")
    require(doc.get("main_free_move_rows") == 468 and
            doc.get("nonzero_main_move_rows") == 5811, "rebuilt MOVE partition mismatch")
    require(doc.get("used_helper_columns") == 806, "used helper-column count mismatch")
    records = doc.get("records")
    targets = doc.get("helper_target_ranks")
    require(isinstance(records, list) and len(records) == 468, "missing or extra MOVE rows")
    events = [r.get("event") for r in records if isinstance(r, dict)]
    require(len(events) == 468 and all(type(e) is int for e in events), "malformed row event IDs")
    require(len(set(events)) == 468, "duplicate MOVE row event ID")
    require(events == sorted(events), "MOVE row events are not ordered")
    require(digest_json(records) == EXPECTED_RECORDS_SHA256, "MOVE row content hash mismatch")
    require(doc.get("records_sha256") == EXPECTED_RECORDS_SHA256, "MOVE row digest field mismatch")
    require(isinstance(targets, dict) and len(targets) == 1101, "missing or extra helper target weights")
    require(all(type(v) is int and 1 <= v <= 9 for v in targets.values()), "invalid helper target rank")
    require(digest_json(targets) == EXPECTED_TARGETS_SHA256, "helper target weights are forged or incomplete")
    require(doc.get("target_ranks_sha256") == EXPECTED_TARGETS_SHA256, "target digest field mismatch")
    target_ints = {int(h): v for h, v in targets.items()}
    seen_columns = set()
    for rec in records:
        require(set(rec) == {"event", "owner", "owned", "rank", "row"}, "row schema mismatch")
        require(type(rec["owner"]) is int and type(rec["owned"]) is bool and
                type(rec["rank"]) is int and 1 <= rec["rank"] <= 9, "row metadata malformed")
        row = rec["row"]
        require(isinstance(row, dict) and row, "empty helper MOVE row")
        for key, value in row.items():
            require(key.isdecimal() and int(key) in target_ints, "row contains non-helper coordinate")
            from fractions import Fraction
            q = Fraction(value)
            require(q != 0, "row stores a zero coefficient")
            seen_columns.add(int(key))
            require(rec["rank"] <= target_ints[int(key)], "support target rank below paid rank")
    require(len(seen_columns) == 806, "helper support union width mismatch")
    return records, target_ints


def validate_structure_doc(doc, rebuilt_doc):
    """Reject altered component partitions and certificates before subset use."""
    require(isinstance(doc, dict), "structure document is not an object")
    require(doc.get("schema") == "helper-funding-structure-v1", "structure schema mismatch")
    require(doc.get("source_sha256") == WORD_SHA256 == rebuilt_doc.get("source_sha256"),
            "structure source binding mismatch")
    require(doc.get("records_sha256") == EXPECTED_RECORDS_SHA256 == rebuilt_doc.get("records_sha256"),
            "structure row binding mismatch")
    require(doc.get("target_ranks_sha256") == EXPECTED_TARGETS_SHA256 == rebuilt_doc.get("target_ranks_sha256"),
            "structure target binding mismatch")
    payload = {k: v for k, v in doc.items() if k != "structure_sha256"}
    require(digest_json(payload) == EXPECTED_STRUCTURE_DOC_SHA256,
            "structure component/certificate digest mismatch")
    require(doc.get("global_rank_Q") == 463 and doc.get("giant_rank_Q") == 342 and
            doc.get("giant_rows") == 347 and doc.get("giant_nullity") == 5,
            "structure rank summary mismatch")
    blocks = doc.get("dependent_blocks")
    require(isinstance(blocks, list) and sorted((len(x.get("events", [])) for x in blocks), reverse=True)
            == [11, 5, 5, 5], "false dependent component structure")
    flat = [e for block in blocks for e in block["events"]]
    require(len(flat) == 26 and len(set(flat)) == 26, "dependent components overlap or omit rows")
    row_events = {r["event"] for r in rebuilt_doc["records"]}
    require(set(flat) <= row_events, "dependent component contains an unknown row")
    return blocks
