"""Fresh-process complete-caller timing, produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import platform
import runpy
import statistics
import subprocess
import sys
import time
from types import SimpleNamespace

adapter = SimpleNamespace(**runpy.run_path(str(Path(__file__).with_name("adapter.py"))))


def main():
    rows = []
    expected = adapter.canonical(adapter.scientific(baseline=True)) + b"\n"
    for index in range(5):
        row = {"pair": index + 1}
        for name in ("baseline", "candidate"):
            argv = [sys.executable, "-I", "-B", str(adapter.HERE / "adapter.py")]
            if name == "baseline":
                argv.append("--baseline")
            start = time.perf_counter_ns()
            process = subprocess.run(argv, capture_output=True, timeout=30)
            elapsed = time.perf_counter_ns() - start
            adapter.require(process.returncode == 0, process.stderr.decode(errors="replace"))
            adapter.require(process.stdout == expected, "timed scientific output differs")
            row[name + "_ns"] = elapsed
        rows.append(row)
    result = {"pairs": rows, "failures": 0,
              "python": sys.version, "platform": platform.platform(),
              "scientific_stdout_sha256": hashlib.sha256(expected).hexdigest(),
              "source_sha256": {name: hashlib.sha256(raw).hexdigest()
                                for name, raw in adapter.source_bytes().items()},
              "program_sha256": {name: hashlib.sha256(adapter.bounded_read(adapter.HERE / name)).hexdigest()
                                 for name in ("adapter.py", "benchmark.py")}}
    for name in ("baseline", "candidate"):
        samples = [row[name + "_ns"] for row in rows]
        result[name] = {"median_ns": statistics.median(samples),
                        "min_ns": min(samples), "max_ns": max(samples)}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
