"""Opt-in execution of the frozen PR886 checker; no source files are edited."""
import argparse
import ast
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from closure import make_close, require

CHECKER = "research/bit589-frame-optimum/frameopt.py"
TUNED = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
BASE_WORD = "research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz"
INPUTS = {
    TUNED, BASE_WORD,
    "research/bit589-frame-optimum/verify.sh",
    "research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py",
}
CASES = {
    "pr589": (TUNED, "1733427039589844234749/1000000000000000000000000", False),
    "pr555": (BASE_WORD, "1733052823330162099157/1000000000000000000000000", False),
    "degraded": (TUNED, "1733427039589844234749/1000000000000000000000000", True),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_sources(root=ROOT, pins=None):
    if pins is None:
        pins = json.loads((HERE / "SOURCES.json").read_text())
    records = [row for row in pins["files"] if row["usage"] == "input"]
    require(len(records) == len(INPUTS) and
            {row["path"] for row in records} == INPUTS, "exact input inventory")
    for row in records:
        path = root / row["path"]
        require(path.is_file(), "missing input: " + row["path"])
        require(sha(path.read_bytes()) == row["sha256"],
                "source digest: " + row["path"])


def program(source, filename, engine):
    tree = ast.parse(source, filename=filename)
    if engine == "basis":
        matches = [i for i, node in enumerate(tree.body)
                   if isinstance(node, ast.FunctionDef) and node.name == "close"]
        require(len(matches) == 1, "unique close function")
        i = matches[0]
        replacement = ast.parse("close = _make_close(L, V, _close)").body[0]
        tree.body[i] = ast.copy_location(replacement, tree.body[i])
    else:
        require(engine == "reference", "engine")
    # Explicit optimize=0 retains every inherited assertion, regardless of
    # parent process state. The CLI additionally rejects optimized invocation.
    return compile(ast.fix_missing_locations(tree), filename, "exec", optimize=0)


def execute(case, engine):
    require(not sys.flags.optimize, "inherited checker requires assertions")
    check_sources()
    path, endpoint, degraded = CASES[case]
    filename = ROOT / CHECKER
    code = program(filename.read_text(), str(filename), engine)
    namespace = {"__file__": str(filename), "__name__": "__main__",
                 "_make_close": make_close}
    output = io.StringIO()
    previous = sys.argv
    try:
        sys.argv = [str(filename), str(ROOT / path), endpoint]
        if degraded:
            sys.argv.append("--degrade")
        with redirect_stdout(output):
            exec(code, namespace)
    finally:
        sys.argv = previous
    text = output.getvalue()
    receipt = json.loads(text)
    closures = [[str(mask), str(closed), rank]
                for mask, (closed, rank) in sorted(namespace["_close"].items())]
    report = {
        "case": case, "receipt": receipt, "stdout_sha256": sha(text.encode()),
        "closure_count": len(closures),
        "closure_sha256": sha(canonical(closures).encode()),
    }
    return report, closures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("reference", "basis"), default="basis")
    parser.add_argument("--case", choices=tuple(CASES), default="pr589")
    parser.add_argument("--closure-output", type=Path)
    args = parser.parse_args()
    if args.closure_output:
        destination = args.closure_output.resolve()
        require(not destination.exists() and not destination.is_relative_to(ROOT),
                "use a fresh external closure output")
    report, closures = execute(args.case, args.engine)
    if args.closure_output:
        with destination.open("x") as stream:
            stream.write(canonical(closures) + "\n")
    print(canonical(report))


if __name__ == "__main__":
    main()
