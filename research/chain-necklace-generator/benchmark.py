"""Five alternating fresh-process comparisons; JSON output, no file writes."""

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import representatives
from verify import literal_classes, need


def emit_method(method: str) -> None:
    if method == "generator":
        words, work = representatives(5, 1)
    else:
        words, work = literal_classes(5, 1)
    print(json.dumps(dict(words=sorted(words), work=work), sort_keys=True))


def main() -> None:
    samples = []
    for trial in range(5):
        order = ("generator", "literal") if trial % 2 == 0 else ("literal", "generator")
        results = {}
        elapsed = {}
        for method in order:
            begin = perf_counter()
            run = subprocess.run([sys.executable, "-I", "-W", "error", "-B",
                                  str(Path(__file__).resolve()), "--method", method],
                                 capture_output=True, text=True, timeout=30, check=True)
            elapsed[method] = perf_counter() - begin
            need(not run.stderr, "timed child emitted diagnostics")
            results[method] = json.loads(run.stdout)
        words, work = results["generator"]["words"], results["generator"]["work"]
        baseline = results["literal"]["words"]
        baseline_work = results["literal"]["work"]
        need(len(words) == 356 and words == baseline, "timed outputs differ")
        samples.append(dict(order=order, seconds=elapsed, generator_work=work,
                            literal_work=baseline_work))
    medians = {method: statistics.median(s["seconds"][method] for s in samples)
               for method in ("generator", "literal")}
    paths = ("generate.py", "verify.py", "benchmark.py")
    hashes = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
              for name in paths}
    print(json.dumps(dict(python=sys.version, platform=platform.platform(),
                          samples=samples, medians=medians, code_sha256=hashes,
                          errors=0, complete_output_comparisons=5),
                     sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("generator", "literal"))
    arguments = parser.parse_args()
    if arguments.method:
        emit_method(arguments.method)
    else:
        main()
