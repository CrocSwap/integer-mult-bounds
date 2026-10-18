#!/usr/bin/env python3
"""Opt-in PR589 replay with full gzip-payload equality at two rebuild sites.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPT = "research/e8-bit-p111-tuned/tune/verify.sh"
COMPARISONS = ("cmp $WD/base.json.gz $BASE", "cmp $WD/tuned.json.gz $WORD")
OLD_MESSAGE = "rebuilt tuned word is byte-identical to the shipped word"
NEW_MESSAGE = "rebuilt tuned word has identical decompressed bytes to the shipped word"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources(root=ROOT):
    """Bind the original shell, manifests and focused test inputs before use.

    The original replay's step 0 additionally checks both complete package
    manifests, vendored blob IDs, external dependencies and cited receipts.
    """
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = (root / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source drift: " + row["path"])


def compare_payloads(generated, reference):
    """Compare all uncompressed bytes, including metadata and JSON whitespace.

    gzip.decompress validates every member and its CRC/size trailer. No JSON
    field selection, normalization or source-pin substitution is performed.
    """
    actual = gzip.decompress(Path(generated).read_bytes())
    expected = gzip.decompress(Path(reference).read_bytes())
    require(actual == expected, "regenerated gzip payload differs: " + str(generated))
    return hashlib.sha256(actual).hexdigest()


def adapted_script(source, helper=None):
    """Exactly two comparison replacements and one corrected success message."""
    helper = HERE / "replay.py" if helper is None else Path(helper)
    command = '"$PYTHON" -I -B ' + shlex.quote(str(helper)) + " --compare"
    for old in COMPARISONS:
        require(source.count(old + "\n") == 1, "comparison anchor changed: " + old)
        source = source.replace(old + "\n", command + old[len("cmp"):] + "\n")
    require(source.count(OLD_MESSAGE) == 1, "summary message anchor changed")
    return source.replace(OLD_MESSAGE, NEW_MESSAGE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--compare", nargs=2, metavar=("GENERATED", "REFERENCE"))
    mode.add_argument("--work", type=Path, help="fresh external output directory for the full bit replay")
    args = parser.parse_args()
    try:
        if args.compare:
            print("PASS_GZIP_PAYLOAD " + compare_payloads(*args.compare))
            return
        require(not sys.flags.optimize, "full replay requires enabled assertions")
        work = args.work.resolve()
        require(not work.exists() and not work.is_relative_to(ROOT),
                "use a fresh output directory outside the repository")
        check_sources()
        original = ROOT / SCRIPT
        source = adapted_script(original.read_text(encoding="utf-8"))
        env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONOPTIMIZE", None)
        # bash -c sets $0 to the original filename. HERE/PKG, all later commands
        # and the complete manifest checks consequently retain their paths.
        result = subprocess.run(["bash", "-c", source, str(original), str(work)],
                                cwd=ROOT, env=env)
        raise SystemExit(result.returncode)
    except (OSError, EOFError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
