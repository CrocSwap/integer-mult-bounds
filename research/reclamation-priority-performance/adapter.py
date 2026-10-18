"""Source-pinned, opt-in exact eligibility and ordering adapter."""

from hashlib import sha256
from pathlib import Path
import importlib
import json
import sys

from priority import RankedSlots

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPERIMENTS = ROOT / "scripts/experiments"
COMPILER = "scripts/experiments/joint_dual_reclaim_compiler.py"
REPLACEMENTS = (
    ("retired=set();", "retired=RankedSlots(h, lambda s: (blocks[frames[s]]['rank'], blocks[frames[s]]['frame']));"),
    ("frames[s]=g;events.append((s,old,g))",
     "retired.move(s,blocks[g]['rank'],blocks[g]['frame']);"
     "frames[s]=g;events.append((s,old,g))"),
    ("sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s))", "retired.ordered(blocks[g]['frame'])"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_sources(root=ROOT):
    require(not sys.flags.optimize, "Assertions must remain enabled")
    pins = json.loads((HERE / "SOURCE.json").read_text())
    for name, digest in pins["files"].items():
        require(sha256((root / name).read_bytes()).hexdigest() == digest,
                "Changed pinned source: " + name)
    # The pinned local manifest binds the original compiler, finite inputs and
    # inherited manifests. Check every listed byte before loading the compiler.
    manifest = json.loads((root / "research/joint-dual/SOURCE.json").read_text())
    for name, digest in manifest["files"].items():
        require(sha256((root / name).read_bytes()).hexdigest() == digest,
                "Changed joint-dual source: " + name)
    return pins


def transformed_source(source):
    for before, after in REPLACEMENTS:
        require(source.count(before) == 1, "Adapter source shape changed: " + before)
        source = source.replace(before, after)
    return source


def load(mode):
    require(mode in ("reference", "buckets", "indexed"), "Unknown engine")
    verify_sources()
    require("joint_dual_compiler" not in sys.modules,
            "Run each engine in a fresh Python process")
    sys.path.insert(0, str(EXPERIMENTS))
    compiler = importlib.import_module("joint_dual_compiler")
    composition = importlib.import_module("joint_dual_compose")
    composition.check_sources()
    if mode != "reference":
        source = (HERE / "reference-pr175.py").read_text() if mode == "buckets" else transformed_source((ROOT / COMPILER).read_text())
        namespace = vars(compiler.compiler)
        namespace["RankedSlots"] = RankedSlots
        exec(compile(source, str(ROOT / COMPILER), "exec"), namespace)
    return compiler
