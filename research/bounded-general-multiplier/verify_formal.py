"""Build the package, inspect its declared axioms and replay every local module."""

from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent / "lean"
modules = sorted(f.stem for f in root.glob("*.lean"))
for module in modules:
    source = (root/(module+".lean")).read_text()
    code = re.sub(r"/-.*?-/|--[^\n]*","",source,flags=re.S)
    if re.search(r"\b(sorry|admit|native_decide|unsafe|axiom)\b",code):
        raise ValueError("Proof escape in "+module)
build = subprocess.run(["lake","--wfail","build"],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
print(build.stdout,end="",flush=True)
build.check_returncode()
if "Build completed successfully" not in build.stdout or "sorryAx" in build.stdout:
    raise ValueError("Missing build receipt or unproved obligation")
reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]+)\]",build.stdout)
axioms = {name for _,values in reports for name in values.split(", ")}
required = {"ShiftedCarrier.bit_program","ShiftedCarrier.complex_program","CubeFacts.cube_padding",
            "TernaryRouting.full_cube","TernaryRouting.weighted_thin_leaf","CarrierStock.current",
            "PeriodicCover.ordered_actions"}
if axioms != {"propext","Classical.choice","Quot.sound"} or not required <= {name for name,_ in reports}:
    raise ValueError((sorted(axioms),sorted(required-{name for name,_ in reports})))
for module in modules:
    result = subprocess.run(["lake","env","leanchecker","-v",module],cwd=root,capture_output=True,text=True)
    log = result.stdout+result.stderr
    print(log,end="",flush=True)
    result.check_returncode()
    if "replaying "+module not in log:
        raise ValueError("Missing kernel replay for "+module)
print("PASS_GENERAL_KERNEL",len(modules),"modules",len(dict(reports)),"axiom reports",sorted(axioms))
