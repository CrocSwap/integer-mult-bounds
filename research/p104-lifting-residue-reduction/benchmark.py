"""Same-input, alternating-order benchmark; timings are observations, not tests."""
import argparse
import json
from pathlib import Path
import platform
import random
import statistics
import time
import types

HERE = Path(__file__).resolve().parent
v = types.ModuleType('source_verifier')
v.__file__ = str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),v.__file__,'exec'),v.__dict__)


def run(repeats):
    lift,split,plans = v.inputs()
    left,right = plans[0]
    rng = random.Random(53)
    rows = []
    for width in (64,512,4096,32768,65536):
        data = [(rng.getrandbits(width)-rng.getrandbits(width),
                 rng.getrandbits(width)-rng.getrandbits(width)) for _ in range(512)]
        timings = [[],[]]
        for rep in range(repeats):
            outputs = {}
            for method in (rep%2,1-rep%2):
                value = list(data)  # identical input and copying boundary
                start = time.perf_counter_ns()
                if method:
                    split.kernel(value,7,left,right,lift)
                else:
                    lift.kernel(value,7,left,right)
                timings[method].append(time.perf_counter_ns()-start)
                outputs[method] = value
            v.need(outputs[0] == outputs[1], 'benchmark exact output equality')
        medians = [statistics.median(a) for a in timings]
        rows.append(dict(width=width,direct_ns=timings[0],split_ns=timings[1],
                         median_speedup=medians[0]/medians[1]))
    return dict(python=platform.python_version(),platform=platform.platform(),
                processor=platform.processor(),seed=53,rank=7,n=512,
                repetitions=repeats,method='alternating order, same signed input, full forward transport; no warmup',
                rows=rows)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--repeats',type=int,default=7)
    args = ap.parse_args()
    v.need(args.repeats >= 3, 'at least three repetitions')
    print(json.dumps(run(args.repeats),indent=2))
