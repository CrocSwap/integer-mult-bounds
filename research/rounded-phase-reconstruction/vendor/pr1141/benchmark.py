"""Measure the two phase interfaces on the same dyadic input."""
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('phase_benchmark_checks', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)


def run(length, bits, fast):
    before = v.data(length, bits, 3)
    data = list(before)
    module = v.s if fast else v.s.old
    meter = module.Meter()
    meter.layout = {id(data): (0, 0)}
    started = time.perf_counter()
    if fast:
        plan = module.Phase.prepare(-3, 2*length+1, bits, meter, length)
    else:
        plan = module.Phase.prepare(-3, 2*length+1, bits, meter)
    prepared = time.perf_counter()
    for inverse in (False, True):
        module.phase_pass(data, plan, inverse)
    streamed = time.perf_counter()
    if fast:
        plan.clear()
    finished = time.perf_counter()
    v.need(data == before, 'benchmark exact restoration')
    return dict(prepare_seconds=prepared-started, stream_seconds=streamed-prepared,
                erase_seconds=finished-streamed, total_seconds=finished-started,
                phase_products=meter.phase_products, phase_divisions=meter.phase_divisions,
                seed_products=getattr(meter, 'seed_products', 0),
                seed_divisions=getattr(meter, 'seed_divisions', 0),
                seed_peak_bits=getattr(meter, 'seed_peak_bits', None),
                tape_moves=meter.tape_moves)


def main():
    rows = []
    for length, bits in ((32, 16), (257, 48), (2048, 96)):
        trials = {'pr1038': [], 'stream': []}
        for trial in range(3):
            order = (False, True) if trial % 2 == 0 else (True, False)
            for fast in order:
                trials['stream' if fast else 'pr1038'].append(run(length, bits, fast))
        rows.append(dict(length=length, bits=bits, trials=trials,
                         median_seconds={key: statistics.median(r['total_seconds'] for r in values)
                                         for key, values in trials.items()}))
    print(json.dumps(dict(python=platform.python_version(), platform=platform.platform(),
                          scope='Two opposite phase passes; new seed erasure included; old API has no explicit seed erasure. PR1038 puts all product and division counts in the phase counters. The new seed counters are separate.',
                          rows=rows), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
