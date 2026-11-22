"""Build the inherited price lemma and kernel-check the weighted construction."""

from pathlib import Path
import os
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

package = Path(__file__).resolve().parent
lean_bin = Path(sys.argv[1]).resolve() / "bin"
mathlib = Path(sys.argv[2]).resolve()
with TemporaryDirectory(prefix="tier-lean-") as temp:
    dst = Path(temp)
    paths = [
        dst,
        mathlib / ".lake/build/lib/lean",
        *sorted((mathlib / ".lake/packages").glob("*/.lake/build/lib/lean")),
    ]
    env = os.environ | {
        "LEAN_PATH": os.pathsep.join(map(str, paths)),
        "PATH": str(lean_bin) + os.pathsep + os.environ["PATH"],
    }
    for source in (
        package.parent / "tiered-native-multiplier" / "TierCost.lean",
        package / "WeightedNumerical.lean",
        package / "GaussianFiniteLoss.lean",
    ):
        name = source.stem
        copyfile(source, dst / (name + ".lean"))
        run(
            [lean_bin / "lean", "-o", name + ".olean", name + ".lean"],
            cwd=dst,
            env=env,
            check=True,
        )
        run([lean_bin / "leanchecker", "-v", name], cwd=dst, env=env, check=True)
