#!/usr/bin/env python3
"""Replay the portable, compressed R5 certificate without modifying files."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "R5-OPTIMUM.json.gz"
RAW_SHA256 = "b1fe3d866d2184227f46ec73ec2021c546bba056e98077e657e9205d9db5ad8b"
PACKED_SHA256 = "d26f615aacff4b082c316e491aa1730aabc9cb6ceb377d33fb9a279b2d7f5f16"


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def replay() -> bytes:
    packed = CERTIFICATE.read_bytes()
    require(hashlib.sha256(packed).hexdigest() == PACKED_SHA256,
            "compressed certificate SHA-256 mismatch")
    raw = gzip.decompress(packed)
    require(hashlib.sha256(raw).hexdigest() == RAW_SHA256,
            "expanded certificate SHA-256 mismatch")
    # Parse it too: this confirms the recovered bytes are a usable certificate.
    document = json.loads(raw)
    require(document.get("radius") == 5 and document.get("inputs") == 3121,
            "expanded certificate has an unexpected domain")
    return raw


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", metavar="PATH",
                        help="write the exact expanded JSON bytes to PATH")
    args = parser.parse_args()
    raw = replay()
    if args.write_certificate:
        Path(args.write_certificate).write_bytes(raw)
    print(json.dumps({
        "status": "PASS",
        "expanded_certificate_sha256": RAW_SHA256,
        "expanded_bytes": len(raw),
        "certificate_output": args.write_certificate,
        "default_run_writes_nothing": args.write_certificate is None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
