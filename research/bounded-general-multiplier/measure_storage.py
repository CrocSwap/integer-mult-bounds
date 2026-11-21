"""Measure one complete packed product in a fresh process; report its high-water RSS."""

import argparse
import json
from pathlib import Path
from random import Random
import resource
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from multiply import fourier, multiply
from short_product import native_product


def rss():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak if sys.platform == "darwin" else peak * 1024


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bits",type=int)
    parser.add_argument("--library",type=Path)
    args = parser.parse_args()
    engine = native_product(args.library) if args.library else None
    incumbent = fourier().multiply_uniform
    rng = Random(728)
    a,b = (rng.getrandbits(args.bits-1) | 1 << (args.bits-1) for _ in range(2))
    initial = rss()
    clock = time.perf_counter()
    result = multiply(a,b,engine) if engine else incumbent(a,b)
    elapsed = time.perf_counter()-clock
    peak = rss()
    if result != a*b:
        raise ArithmeticError("Incorrect full product")
    print(json.dumps(dict(bits=args.bits,library=args.library.name if engine else "pinned",
             peak_before=initial,peak_after=peak,seconds=elapsed)))
