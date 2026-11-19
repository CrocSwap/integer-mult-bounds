"""Replay one independent part of the 36-call and 48-call research checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prepare_sources import sources


def run(script, *args):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)], check=True)


def main(args):
    cache, out = args.cache.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources(cache)
    claim = json.loads((HERE / "CLAIM.json").read_bytes())
    c, b = HERE / "complex", HERE / "binary"
    if args.part == "binary-construction":
        run(b / "replay.py", "--source-root", cache / "source", "--parent-word", cache / "parent/binary/WORD.json.gz",
            "--journal", b / "BIRTHS.json", "--out", out)
        return
    if args.part == "binary-finite":
        output = out / "finite.json"
        run(b / "finite.py", "--package", cache / "parent", "--source-root", cache / "source",
            "--word", b / "WORD.json.gz", "--word-sha", claim["binary_word"], "--out", output)
        if json.loads(output.read_bytes()) != json.loads((b / "FINITE.json").read_bytes()):
            raise ValueError("published finite binary receipt differs from replay")
        return
    if args.part in ("construction", "operator"):
        parent = out / "comparator"
        run(cache / "parent/verify.py", "--cache", cache, "--out", parent, "--part", "construction")
        word, layout = parent / "free/WORD.json.gz", parent / "free/LAYOUT.json.gz"
        if args.part == "construction":
            projected = out / "projected"
            run(c / "paid_projection.py", "--source-root", cache / "source", "--word", word, "--layout", layout,
                "--journal", c / "PROJECTIONS.json", "--word-sha", claim["comparator_complex"],
                "--layout-sha", claim["comparator_layout"], "--expected", claim["projected"], "--out", projected)
            run(c / "births.py", "--cache", cache, "--word", projected / "WORD.json.gz", "--layout", projected / "LAYOUT.json.gz",
                "--journal", c / "BIRTHS.json", "--parent-layout", claim["comparator_layout"],
                "--child-layout", claim["layout"], "--out", out / "candidate")
            return
        fault_args = [arg for item in claim["controls"] for arg in ("--fault", item)]
        run(c / "independent.py", "--cache", cache, "--base-graph", word, "--base-layout", layout,
            "--candidate", c / "WORD.json.gz", "--layout", c / "LAYOUT.json.gz", "--sha", claim["complex_word"],
            "--layout-sha", claim["layout"], "--binary-finite", b / "FINITE.json",
            "--binary-finite-sha", hashlib.sha256((b / "FINITE.json").read_bytes()).hexdigest(),
            "--binary-word", claim["binary_word"], "--ordinary", "--charts", *fault_args, "--out", out / "operator.json")
        return
    output = out / "application.json"
    extra = ["--shard", args.part[-1]] if args.part.startswith("charts-") else []
    run(HERE / "application.py", "--cache", cache, "--word", c / "WORD.json.gz", "--layout", c / "LAYOUT.json.gz",
        "--binary-finite", b / "FINITE.json", "--word-sha", claim["complex_word"],
        "--layout-sha", claim["layout"], "--binary-sha", claim["binary_word"], "--out", output, *extra)
    report = json.loads(output.read_bytes())
    expected = json.loads((HERE / "evidence" / (args.part + ".json")).read_bytes())
    if expected != report:
        raise ValueError("published physical or application receipt differs from replay")
    if args.part == "application":
        for name in ("finite_lower", "complex_raw", "gain_above_upper", "target", "remaining_to_target", "ordinary_binary"):
            if report[name] != claim[name]:
                raise ValueError("claim differs from application at " + name)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--part", choices=("construction", "operator", "binary-construction", "binary-finite",
                                     "charts-0", "charts-1", "charts-2", "application"), required=True)
    main(p.parse_args())
