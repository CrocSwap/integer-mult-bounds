#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the copied input bytes and their selected replay bindings."""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build


def verify():
    if not __debug__:
        raise RuntimeError("verification requires assertions; do not use -O")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    records = (sources["dependencies"] + sources["generated_inputs"]
               + sources["selected_archive"]["members"])
    checked = 0
    for record in records:
        if "local_path" not in record:
            continue
        data = (HERE / record["local_path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == record["sha256"], record["local_path"]
        if "content_sha256" in record:
            assert hashlib.sha256(gzip.decompress(data)).hexdigest() == record["content_sha256"]
        checked += 1
    selected = json.loads((HERE / "evidence/selected1094-SCALAR-FRAME-AUDIT.json").read_text())
    assert selected["input_content_sha256"] == build.SOURCE_HASH
    assert selected["canonical_content_sha256"] == "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"
    original, zero = build.source(), build.construct(0)
    for key in original:
        if key != "refactored_cleanup":
            assert original[key] == zero[key], key
    assert selected["local_profile"] == original["report"]["local_profile"]
    assert selected["local_rank_mass"] == 5586
    changed = json.loads((HERE / "evidence/all-eight-SCALAR-FRAME-AUDIT.json").read_text())
    encoded = json.dumps(build.construct(255), sort_keys=True, separators=(",", ":")).encode()
    assert changed["input_content_sha256"] == hashlib.sha256(encoded).hexdigest()
    assert changed["canonical_content_sha256"] == "0d5d90211bf938b59c1897589e379dfa16eadb0aa3e832f2b01b01a9ea40e50e"
    return {"status": "PASS_SELECTED_REPLAY_AND_COPIED_SOURCE_BINDINGS", "copied_files": checked,
            "scope": "Byte pins and recorded selected/native bindings; no native replay is run by this command."}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
