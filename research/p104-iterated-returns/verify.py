"""Replay one independent part of the 36-call and 48-call research checkpoint."""
import argparse
import gzip
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


def canonical_hash(path):
    with gzip.open(path, "rt", encoding="utf-8") as reader:
        value = json.load(reader)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def same_word(path, archive, pin):
    if canonical_hash(path) != pin or canonical_hash(archive) != pin:
        raise ValueError(f"constructed and published word must both have digest {pin}")


def operator_receipt(path):
    report = json.loads(path.read_bytes())
    # Different zlib versions may encode the generated comparator and control
    # archives differently. Their canonical graph and layout digests are checked.
    for generated in (report["base"], report["incremental_comparison"]["source"]):
        del generated["word_file_sha256"], generated["layout_file_sha256"]
    return report


def main(args):
    cache, out = args.cache.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources(cache)
    claim = json.loads((HERE / "CLAIM.json").read_bytes())
    c, b = HERE / "complex", HERE / "binary"
    if args.part == "binary-construction":
        run(b / "construction.py", "--cache", cache, "--out", out)
        same_word(out / "WORD.json.gz", b / "WORD.json.gz", claim["binary_word"])
        return
    if args.part == "binary-finite":
        output = out / "finite.json"
        run(b / "finite.py", "--package", cache / "parent", "--source-root", cache / "source",
            "--word", b / "WORD.json.gz", "--word-sha", claim["binary_word"], "--out", output)
        if json.loads(output.read_bytes()) != json.loads((b / "FINITE.json").read_bytes()):
            raise ValueError("published finite binary receipt differs from replay")
        independent = out / "second-finite.json"
        run(b / "verify_target.py", "--word", b / "WORD.json.gz", "--source-root", cache / "source",
            "--independent", cache / "parent/binary/independent", "--out", independent)
        if json.loads(independent.read_bytes()) != json.loads((b / "INDEPENDENT.json").read_bytes()):
            raise ValueError("the second finite binary certificate differs from replay")
        run(b / "physical.py", "--cache", cache, "--out", out / "physical.json")
        return
    if args.part in ("construction", "operator"):
        parent = out / "comparator"
        run(cache / "parent/verify.py", "--cache", cache, "--out", parent, "--part", "construction")
        word, layout = parent / "free/WORD.json.gz", parent / "free/LAYOUT.json.gz"
        stages = out / "stages"
        run(c / "construction.py", "--cache", cache, "--word", word, "--layout", layout,
            "--out", stages, *(["--first-only"] if args.part == "operator" else []))
        if args.part == "construction":
            same_word(stages / "WORD.json.gz", c / "WORD.json.gz", claim["complex_word"])
            same_word(stages / "LAYOUT.json.gz", c / "LAYOUT.json.gz", claim["layout"])
            return
        fault_args = [arg for item in claim["controls"] for arg in ("--fault", item)]
        run(c / "independent.py", "--cache", cache, "--base-graph", word, "--base-layout", layout,
            "--control-word", stages / "first/WORD.json.gz", "--control-layout", stages / "first/LAYOUT.json.gz",
            "--control-sha", claim["control_word"], "--control-layout-sha", claim["control_layout"],
            "--candidate", c / "WORD.json.gz", "--layout", c / "LAYOUT.json.gz", "--sha", claim["complex_word"],
            "--layout-sha", claim["layout"], "--binary-finite", b / "FINITE.json",
            "--binary-finite-sha", hashlib.sha256((b / "FINITE.json").read_bytes()).hexdigest(),
            "--binary-word", claim["binary_word"], "--ordinary", "--charts", "--scoped-faults",
            *fault_args, "--out", out / "operator.json")
        if operator_receipt(out / "operator.json") != operator_receipt(HERE / "evidence/operator.json"):
            raise ValueError("independent operator, negative controls or finite compiler changed")
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
