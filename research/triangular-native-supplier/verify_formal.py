"""Build the arithmetic and composition proofs and replay each new kernel module."""

from pathlib import Path
import re
import subprocess


def main():
    root = Path(__file__).resolve().parent / "lean"
    proofs = sorted(root.glob("*.lean"))
    expected = set()
    for proof in proofs:
        code = re.sub(r"/-.*?-/|--[^\n]*", "", proof.read_text(), flags=re.S)
        if re.search(r"\b(sorry|admit|unsafe|native_decide|axiom)\b", code):
            raise ValueError(f"Proof escape in {proof.name}")
        expected.update(
            (proof.name, name) for name in re.findall(r"^#print axioms (\w+)", code, re.M)
        )
    build = subprocess.run(
        ["lake", "--wfail", "build"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    print(build.stdout, end="", flush=True)
    if "Build completed successfully" not in build.stdout or "sorryAx" in build.stdout:
        raise ValueError("Incomplete or admitted proof")
    result = re.findall(
        r"(?m)^info: ([\w.]+\.lean):\d+:\d+: '([^']+)' "
        r"(?:depends on axioms: \[([^\]]+)\]|does not depend on any axioms)",
        build.stdout,
    )
    got = {(file, name.rsplit(".", 1)[-1]) for file, name, _ in result}
    used = {ax for _, _, axioms in result for ax in axioms.split(", ") if ax}
    if not expected <= got or used != {"propext", "Classical.choice", "Quot.sound"}:
        raise ValueError((sorted(expected - got), used))
    for proof in proofs:
        check = subprocess.run(
            ["lake", "env", "leanchecker", "-v", proof.stem],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        log = check.stdout + check.stderr
        if "replaying " + proof.stem not in log:
            raise ValueError("Missing kernel receipt for " + proof.stem)
        print(log, end="", flush=True)
    print(
        "PASS_TRIANGULAR_KERNEL",
        len(proofs),
        "modules",
        len(expected),
        "axiom reports",
        sorted(used),
    )


if __name__ == "__main__":
    main()
