"""Compare the same exact count with a feasible simplex reference."""
import json
import platform
from pathlib import Path
from statistics import median
import sys
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import source, direct
from count import joint_count, require

old = source()
q, n, a = 7, 12, (0,) * 7
samples = {"simplex": [], "convolution": []}
answers = {}
for repetition in range(5):
    order = ("simplex", "convolution") if repetition % 2 == 0 else ("convolution", "simplex")
    for method in order:
        start = perf_counter()
        answer = direct(q, n, a, old) if method == "simplex" else joint_count(q, n, a)
        samples[method].append(perf_counter() - start)
        answers[method] = answer
require(answers["simplex"] == answers["convolution"], "benchmark count mismatch")
print(json.dumps({"python": platform.python_version(), "platform": platform.platform(),
                  "q": q, "n": n, "nullities": a, "count": str(answers["simplex"]),
                  "seconds": samples, "median_speedup": median(samples["simplex"]) /
                  median(samples["convolution"]), "timing_is_not_an_acceptance_test": True}, indent=2))
