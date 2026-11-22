"""Build the algebraic phase identities and replay the generated environment."""

from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
import os
import subprocess
import sys

here = Path(__file__).resolve().parent
lean, mathlib = [Path(v).resolve() for v in sys.argv[1:3]]
with TemporaryDirectory(prefix="phase-lean-") as tmp:
    copyfile(here / "PhaseSum.lean", Path(tmp) / "PhaseSum.lean")
    libs = [
        Path(tmp),
        mathlib / ".lake/build/lib/lean",
        *sorted((mathlib / ".lake/packages").glob("*/.lake/build/lib/lean")),
    ]
    env = dict(
        os.environ,
        LEAN_PATH=os.pathsep.join(map(str, libs)),
        PATH=str(lean / "bin") + os.pathsep + os.environ["PATH"],
    )
    for cmd in (
        (lean / "bin/lean", "-o", "PhaseSum.olean", "PhaseSum.lean"),
        (lean / "bin/leanchecker", "-v", "PhaseSum"),
    ):
        result = subprocess.run(cmd, cwd=tmp, env=env, text=True, capture_output=True)
        print(result.stdout + result.stderr, end="", flush=True)
        result.check_returncode()
        if "sorryAx" in result.stdout + result.stderr:
            raise ValueError("The phase proof has an incomplete dependency")
