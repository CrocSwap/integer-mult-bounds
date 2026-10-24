"""Export the pinned PR5017 audit inputs without changing a checkout.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output must be a new directory")
    sources = json.loads(Path(__file__).with_name("SOURCES.json").read_bytes())
    files = []
    for row in sources["files"]:
        raw = subprocess.check_output([
            "git", "-c", "maintenance.auto=false", "-c", "gc.auto=0", "show",
            row["commit"] + ":" + row["path"]], cwd=args.repo)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if blob != row["git_blob"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("source identity mismatch: " + row["path"])
        files.append((row["path"], raw))
    args.output.mkdir(parents=True)
    for name, raw in files:
        target = args.output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    print("PASS_PINNED_WINDOWS_WORKER_EXPORT files=" + str(len(files)))


if __name__ == "__main__":
    main()
