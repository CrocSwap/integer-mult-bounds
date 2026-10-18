#!/usr/bin/env python3
"""Opt-in PR626 owner check bound to exact decompressed native bytes.

All mathematics runs in the unchanged source-pinned predecessor. Only its four
regenerated-native-container comparisons are replaced. Apache-2.0; see README.
"""
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research/complex-k492-owner-repair"
SOURCE = PACKAGE / "extras/check_owner_map.py"

# Immutable executable sources and historical container receipt. Data pins
# enforced by the predecessor remain untouched.
SOURCE_HASHES = {
    "extras/check_owner_map.py": "d240458ad39a08c242d136c0f1edbda0cb0b93977897f6543c9f430576c9c7dd",
    "extras/exact_intervals.py": "aa3c2327c5d3742248b720a87b2de0bbe2e34ed2af89a578e3c8d5bd2656a9cf",
    "comparison/PR622-NATIVE-HASHES.json": "28479a183387bcb608bd9ee0572f617c17f316b79ce4a6fa1277ed8689fb3431",
}
# Derived from the historical containers named above and bound to their exact
# Git blobs and SHA-256 values in SOURCES.json. verify.py checks that derivation.
PAYLOAD_HASHES = {
    "ck/CANONICAL-WORD.json.gz": "9bbc75dede090cfd7a0a0252424ea9d9f6211e2350d2a801d4e4f2f0784167c7",
    "ck/LOCAL-PROGRAMS.json.gz": "854f17274092263dc25e60367f4cd0d29f60a8446becd17cc1883ebed7a97900",
    "jp8/CANONICAL-WORD.json.gz": "fb4a8d14ed2a8048698bea6ae16f86163a1aa6c80f2eb622222eee5cdbce9b3b",
    "jp8/LOCAL-PROGRAMS.json.gz": "efe45ce7fb025a6f53cc9eb54e951ac2211a5ed927e689a049e4f68ca680654b",
}
OLD_CHECK = (
    "need(hashlib.sha256((directory/filename).read_bytes()).hexdigest()=="
    "load(P/'comparison/PR622-NATIVE-HASHES.json')[pid+'/'+filename],"
    "'unchanged PR622 native word and program')"
)
NEW_CHECK = (
    "need(native_payload_matches(directory/filename,pid,filename),"
    "'unchanged PR622 native word and program (decompressed bytes)')"
)


def native_payload_matches(path, pid, filename):
    """Bind every uncompressed byte, not selected fields or aggregate counts."""
    expected = PAYLOAD_HASHES[pid + "/" + filename]
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest() == expected


def main():
    # Read code once and execute those exact verified bytes. No hash monkeypatch,
    # changed data file, persistent cache, or weakened downstream condition.
    sources = {}
    for relative, expected in SOURCE_HASHES.items():
        raw = (PACKAGE / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise SystemExit("Source pin mismatch: " + relative)
        sources[relative] = raw
    code = sources["extras/check_owner_map.py"].decode("utf-8")
    if code.count(OLD_CHECK) != 1:
        raise SystemExit("Expected exactly one native-container comparison site")
    code = code.replace(OLD_CHECK, NEW_CHECK, 1)
    namespace = {
        "__name__": "__main__",
        "__file__": str(SOURCE),
        "native_payload_matches": native_payload_matches,
    }
    exec(compile(code, str(SOURCE), "exec"), namespace)


if __name__ == "__main__":
    main()
