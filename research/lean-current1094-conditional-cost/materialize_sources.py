#!/usr/bin/env python3
"""Reconstruct exact sources from included files and one existing public Git snapshot.

No fetch, installation, compiler invocation, source rewriting or object reuse.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public-repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / "SOURCE_MANIFEST.json").read_text())
    commit = manifest["public_prerequisite"]["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    output = args.output.absolute()
    if output.exists() or output.is_symlink():
        raise SystemExit("Refusing existing output; choose a fresh directory")
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    records = []
    names = set()
    for row in manifest["modules"]:
        name = row["filename"]
        assert re.fullmatch(r"[A-Za-z0-9_]+\.lean", name) and name not in names
        names.add(name)
        path = Path(row["provider_path"])
        assert not path.is_absolute() and ".." not in path.parts
        if row["provider"] == "included":
            data = (package / path).read_bytes()
        elif row["provider"] == "public_git":
            data = subprocess.check_output(
                ["git", "--no-optional-locks", "-C", str(args.public_repo),
                 "show", commit + ":" + path.as_posix()],
                env=env, timeout=15)
        else:
            raise ValueError("Unknown source provider")
        assert len(data) == row["bytes"], name
        assert hashlib.sha256(data).hexdigest() == row["sha256"], name
        assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"], name
        records.append((row, data))
    assert len(records) == manifest["counts"]["complete_research_modules"]
    assert sum(len(data) for _, data in records) == manifest["counts"]["complete_source_bytes"]
    # Validate all inputs first; never overwrite any prior stage on failure.
    output.mkdir()
    for row, data in records:
        with (output / row["filename"]).open("xb") as stream:
            stream.write(data)
    result = {"status": "EXACT_SOURCES_RECONSTRUCTED_NO_COMPILER",
              "modules": [{"module": row["module"], "bytes": len(data),
                           "sha256": hashlib.sha256(data).hexdigest()}
                          for row, data in records],
              "total_bytes": sum(len(data) for _, data in records),
              "import_changes": 0, "compiler": False}
    (output / "SOURCE_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "modules": len(records),
                      "total_bytes": result["total_bytes"]}))


if __name__ == "__main__":
    main()
