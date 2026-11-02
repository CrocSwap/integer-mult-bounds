#!/usr/bin/env python3
"""Publication integrity wrapper; executes only the frozen NEW v2 static reader.
Clear1nsight, with substantial OpenAI Codex/Sol Max assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import json
import stat
import sys

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if ok is not True:
        raise ValueError(message)

def main():
    manifest = json.loads((ROOT / "MANIFEST.json").read_bytes())
    rows = manifest["files"]
    expected = {row["path"] for row in rows}
    require(len(expected) == len(rows), "duplicate manifest path")
    actual = set()
    for path in ROOT.rglob("*"):
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), "symlink in package")
        if stat.S_ISREG(info.st_mode):
            actual.add(path.relative_to(ROOT).as_posix())
            require(info.st_nlink == 1, "multilink in package")
            require((info.st_mode & 0o111) == 0, "executable package member")
    require(actual == expected | {"MANIFEST.json"}, "package member set differs")
    for row in rows:
        name = row["path"]
        require(type(name) is str and not name.startswith("/") and ".." not in Path(name).parts, "bad manifest path")
        raw = (ROOT / name).read_bytes()
        require(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"], "package bytes differ: " + name)
    fixed = {"at_random_producer_v2.py": "49023291b40f424b56e6fe7f3fd63dd99cbdbab69bb7bd697a1bb3fd9c121ed0", "package_reader_v2.py": "98cc037da70cc5f562c9bf2aa5c9ad61b096ac18bf9bc08430d8722da70fb6bf"}
    for name, digest in fixed.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "frozen NEW source differs")
    sys.path.insert(0, str(ROOT))
    import package_reader_v2 as reader
    bundle = reader.read_package(str(ROOT))
    raw = reader.make_witness(bundle)
    reader.check_witness(bundle, raw)
    require(raw == (ROOT / "WITNESS-v1.json").read_bytes(), "frozen witness differs")
    require(len(raw) == 2617 and hashlib.sha256(raw).hexdigest() == "3bc1e7dd7d6cf17e5dd11129defe1baa05c73c90e617a0b7205af7df114e6f70", "witness identity differs")
    print(json.dumps({"status": "PASS_AT_RANDOM_EXACT_SOURCE_EVENT_PACKAGE_ONLY", "files": len(actual), "literal_inputs": len(bundle), "witness_bytes": len(raw), "witness_sha256": hashlib.sha256(raw).hexdigest(), "retained_40_case_suite_rerun": False, "full_C05": False, "full_V03": False, "outside_costs": "OPEN_NOT_ZERO"}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
