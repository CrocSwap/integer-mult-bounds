#!/usr/bin/env python3
"""Same-input exact enumeration versus compiler+checker; timing is descriptive."""
import gc
import json
import platform
from statistics import median
from time import perf_counter
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
v = types.ModuleType('benchmark_verifier')
v.__file__ = str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),v.__file__,'exec'),v.__dict__)
v.sources()
mu,add = v.hierarchical_prices(6)
times = {'enumeration':[],'compiler_and_checker':[]}
answers = set()
for repeat in range(3):
    for name in (list(times) if repeat % 2 == 0 else list(reversed(times))):
        gc.collect()
        start = perf_counter()
        if name == 'enumeration':
            optimum,forests = v.forest_min(mu,add)
        else:
            certificate = v.solver.synthesize(mu,add)
            optimum = v.Fraction(v.checker.check(mu,add,certificate)['cost'])
        times[name].append(perf_counter()-start)
        answers.add(str(optimum))
v.need(len(answers) == 1,'same exact optimum')
print(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),
                     rows=6,seed=19,tariffs_sha256=v.digest([mu,add]),
                     optimum=next(iter(answers)),enumerated_forests=forests,
                     seconds=times,median_seconds={k:median(t) for k,t in times.items()},
                     scope='New exhaustive forest baseline versus new compiler plus full certificate checker; not physical runtime.'),indent=2,sort_keys=True))
