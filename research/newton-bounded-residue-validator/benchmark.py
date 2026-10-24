"""Time equal membership decisions. Run explicitly; timing is not acceptance."""
import json
from pathlib import Path
import platform
from statistics import median
import sys
from time import perf_counter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import load_source, need
from membership import member


def run(repeats=100, trials=5):
    old = load_source()
    rows = []
    for width in (8, 128, 1024, 8064):
        coefficients = [((-1 if i & 1 else 1) * ((1 << width) + i * 17),
                         (-1 if i & 2 else 1) * ((1 << width) + i * 13)) for i in range(512)]
        values = old.encode(coefficients)
        need(member(values) == old.member(values) == True, "benchmark positive endpoint")
        samples = {"source": [], "bounded": []}
        for trial in range(trials):
            order = (("source", old.member), ("bounded", member))
            if trial % 2: order = tuple(reversed(order))
            for name, function in order:
                start = perf_counter()
                for _ in range(repeats): need(function(values), "timed endpoint")
                samples[name].append(perf_counter() - start)
        rows.append({"coefficient_bits": max(abs(c).bit_length() for z in coefficients for c in z), "samples_seconds": samples,
                     "median_speedup": median(samples["source"]) / median(samples["bounded"])})
    return {"python": platform.python_version(), "platform": platform.platform(),
            "repeats_per_sample": repeats, "alternating_trials": trials,
            "arrays_per_call": 1, "rank": 9, "results": rows,
            "scope": "Membership only; no whole collector, physical tape or kappa speedup."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
