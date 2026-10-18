#!/usr/bin/env python3
"""Replay the pinned R420 local, native, nine-stage, and eleven-stage pipeline."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
R420 = ROOT / "research/e8-bit-r420"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def render(word_path: Path) -> str:
    script = (R420 / "verify.sh").read_text()
    old_here = 'HERE=$(cd "$(dirname "$0")" && pwd); WD='
    new_here = f"HERE={shlex.quote(str(R420))}; WD="
    require(script.count(old_here) == 1, "pinned verify.sh HERE anchor changed")
    script = script.replace(old_here, new_here)
    old_word = "WORD=$D/bitE8mut-r420.json.gz; EXP=$HERE/EXPECTED.json"
    new_word = f"WORD={shlex.quote(str(word_path))}; EXP=$HERE/EXPECTED.json"
    require(script.count(old_word) == 1, "pinned verify.sh WORD anchor changed")
    script = script.replace(old_word, new_word)

    start = script.index('step "1. the word, rebuilt from the frozen plan"')
    end = script.index('step "2. independent exact replay', start)
    replacement = '''step "1. candidate from bounded block-4 search"
$PY -c 'import gzip,json,sys; w=json.load(gzip.open(sys.argv[1],"rt")); assert w["R"]==420 and len(w["B"])==830 and len(w["C"])==2654; print("   candidate R=420, B=830, C=2654")' "$WORD"

'''
    script = script[:start] + replacement + script[end:]
    summary = "$PY $C/summary.py $HERE $WD"
    require(script.count(summary) == 1, "pinned verify.sh summary anchor changed")
    script = script.replace(
        summary,
        'echo "   changed-word summary is recorded in the package VALIDATION.json"',
    )
    return script


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory to retain full intermediate receipts")
    args = parser.parse_args()
    python = shlex.split(os.environ.get("PYTHON", sys.executable))
    if importlib.util.find_spec("numpy") is None or importlib.util.find_spec("scipy") is None:
        raise SystemExit("The R420 hosted pipeline needs NumPy, SymPy, and SciPy; see README.md")
    sympy = subprocess.run(python + ["-c", "import sympy"], capture_output=True)
    if sympy.returncode:
        raise SystemExit("SymPy is unavailable in this Python; see README.md for the isolated environment")

    keep = args.output.resolve() if args.output else None
    if keep is not None:
        require(not keep.exists(), f"refusing to overwrite {keep}")
        require(not keep.is_relative_to(R420) and not keep.is_relative_to(ROOT / "research/e8-bit-carrier-skeleton"),
                "output must be outside the source packages")
        keep.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="r420-block4-hosted-") as scratch:
        temp = Path(scratch)
        word_path = temp / "candidate-word.json.gz"
        shutil.copyfile(HERE / "candidate-word.json.gz", word_path)
        script_path = temp / "verify-candidate.sh"
        script_path.write_text(render(word_path))
        script_path.chmod(0o755)
        if keep is None:
            output = temp / "output"
        else:
            output = keep
        env = os.environ.copy()
        env["PYTHON"] = os.environ.get("PYTHON", sys.executable)
        subprocess.run(["bash", str(script_path), str(output)], cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
