"""Build the project, inspect its declared axioms, and replay each kernel object."""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent / "lean"


def replay():
    expected = set()
    for file in ROOT.glob("*.lean"):
        source = re.sub(r"/-.*?-/|--[^\n]*", "", file.read_text(), flags=re.S)
        if re.search(r"\b(sorry|admit|axiom|unsafe|native_decide)\b", source):
            raise ValueError(f"The proof contains an unchecked declaration in {file.name}")
        expected.update(
            (file.name, n.split(".")[-1])
            for n in re.findall(r"^#print axioms ([\w.]+)", source, re.M)
        )
    build = subprocess.run(
        ["lake", "--wfail", "build"], cwd=ROOT, capture_output=True, text=True
    )
    report = build.stdout + build.stderr
    print(report, end="")
    build.check_returncode()
    if "Build completed successfully" not in report or "sorryAx" in report:
        raise ValueError("The formal build or axiom audit failed")
    rows = re.findall(
        r"info: ([\w.]+\.lean):\d+:\d+: '([^']+)' (?:depends on axioms: \[([^\]]+)\]|does not depend on any axioms)",
        report,
    )
    assert {(file, name.split(".")[-1]) for file, name, _ in rows} == expected
    axioms = {a for _, _, items in rows for a in items.split(", ") if a}
    assert axioms == {"propext", "Classical.choice", "Quot.sound"}
    for name in sorted({Path(f).stem for f, _ in expected}):
        run = subprocess.run(
            ["lake", "env", "leanchecker", "-v", name],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        if "replaying " + name not in run.stdout + run.stderr:
            raise ValueError("Missing kernel replay of " + name)
        print(run.stdout + run.stderr, end="")
    print("PASS_NATIVE_SCALE_KERNEL", len(expected), "axiom reports", sorted(axioms))


if __name__ == "__main__":
    replay()
