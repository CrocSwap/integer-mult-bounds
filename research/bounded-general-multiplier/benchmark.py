"""Time complete signed products on the same generated operand pairs."""

import argparse
import cProfile
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import pstats
import random
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiply import fourier, multiply
from short_product import native_product, reference_product


def run(library, sizes, rounds, python_limit, gmp_library=None, profile=True):
    rng = random.Random(2185007)
    compiled = native_product(library)
    incumbent = fourier().multiply_uniform
    gmp = native_product(gmp_library) if gmp_library else None
    rows = []
    for n in sizes:
        inputs = [(rng.getrandbits(n-1) | 1 << (n-1),
                   -(rng.getrandbits(n-1) | 1 << (n-1))) for _ in range(rounds)]
        expected = [a*b for a,b in inputs]
        work = {"pinned_python":incumbent, "compiled_ntt":lambda a,b:multiply(a,b,compiled),
                "cpython_builtin":lambda a,b:a*b}
        if n <= python_limit:
            work["portable_ntt"] = lambda a,b:multiply(a,b,reference_product)
        if gmp:
            work["gmp_packed"] = lambda a,b:multiply(a,b,gmp)
        times = {name:[] for name in work}
        for trial,(a,b) in enumerate(inputs):
            names = list(work)
            if trial % 2:
                names.reverse()
            for name in names:
                start = time.perf_counter_ns()
                got = work[name](a,b)
                ns = time.perf_counter_ns()-start
                if got != expected[trial]:
                    raise RuntimeError((n,trial,name))
                times[name].append(ns)
        magnitude = abs(expected[-1])
        rows.append({"operand_bits":n,"sha256_last_magnitude_le":sha256(
            magnitude.to_bytes((magnitude.bit_length()+7)//8,"little")).hexdigest(),
            "timings_ns":{name:{"median":statistics.median(ns),"min":min(ns),"max":max(ns),
                                "samples":ns} for name,ns in times.items()}})
    # Keep profiling out of every reported timing.
    leaves = []
    if profile:
        profiler = cProfile.Profile()
        profiler.runcall(incumbent, *inputs[0])
        stats = pstats.Stats(profiler).stats
        leaves = [(key[2],v[0],v[1],v[2]) for key,v in stats.items() if key[2]=="word_product"]
    return {"python":platform.python_version(),"system":platform.platform(),
            "processor":platform.machine(),"logical_cpu_count":os.cpu_count(),
            "load_at_exit":list(os.getloadavg()),"rounds":rounds,
            "timer":"perf_counter_ns","incumbent_profile":leaves,"rows":rows}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("library",type=Path)
    cli.add_argument("--sizes",type=int,nargs="+",default=[4096,65536,262144,1048576])
    cli.add_argument("--rounds",type=int,default=5)
    cli.add_argument("--python-limit",type=int,default=65536)
    cli.add_argument("--gmp-library",type=Path)
    cli.add_argument("--skip-profile",action="store_true")
    args=cli.parse_args()
    print(json.dumps(run(args.library,args.sizes,args.rounds,args.python_limit,args.gmp_library,
                         not args.skip_profile),indent=2))
