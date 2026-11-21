"""Check local proof sources, their reported axioms and the compiled modules."""

from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent / "lean"
names = sorted(path.stem for path in root.glob("*.lean"))
receipt = set()
for name in names:
    src = (root / (name + ".lean")).read_text()
    code = re.sub(r"/-.*?-/|--[^\n]*", "", src, flags=re.S)
    if re.search(r"\b(sorry|admit|unsafe|native_decide|axiom)\b", code):
        raise ValueError("Proof escape in " + name)
    receipt.update(re.findall(r"^#print axioms (\w+)", code, re.M))
step = subprocess.run(
    ["lake", "--wfail", "build"],
    cwd=root,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
print(step.stdout, end="", flush=True)
step.check_returncode()
if "Build completed successfully" not in step.stdout or "sorryAx" in step.stdout:
    raise ValueError("The Lean build has no complete receipt")
reports = re.findall(
    r"'([^']+)' (?:depends on axioms: \[([^\]]+)\]|does not depend on any axioms)", step.stdout
)
seen = {name.rsplit(".", 1)[-1] for name, _ in reports}
used = {ax for _, axioms in reports for ax in axioms.split(", ") if ax}
if seen != receipt or used != {"propext", "Classical.choice", "Quot.sound"}:
    raise ValueError((seen ^ receipt, used))
for name in names:
    check = subprocess.run(
        ["lake", "env", "leanchecker", "-v", name], cwd=root, capture_output=True, text=True
    )
    log = check.stdout + check.stderr
    print(log, end="", flush=True)
    check.check_returncode()
    if "replaying " + name not in log:
        raise ValueError("No kernel receipt for " + name)
print(
    "PASS_NATIVE_STOCK_KERNEL", len(names), "modules", len(receipt), "axiom reports", sorted(used)
)
