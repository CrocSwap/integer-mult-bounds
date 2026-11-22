"""Build the fixed machines and inspect what exists before any operand arrives."""

import gzip
import inspect
import tarfile
from fractions import Fraction
from io import BytesIO
from pathlib import Path
import resource
import sys
from time import perf_counter
from band_product import prepare_native
from installations import PROFILES
from raw_binary_stage import binary_word
from upstream import HERE
from transport import Plan
from strong_binary import fixed_binary_charts


def expanded(name, data):
    if not name.endswith(".gz"):
        return len(data)
    raw = gzip.decompress(data)
    if not name.endswith(".tar.gz"):
        return len(raw)
    with tarfile.open(fileobj=BytesIO(raw), mode="r:") as archive:
        return len(raw) + sum(expanded(f.name, archive.extractfile(f).read())
                              for f in archive if f.isfile())


def measure(build):
    meter = sys.monitoring
    key = meter.COVERAGE_ID
    meter.use_tool_id(key, "raw installation")
    count = largest = calendars = 0

    def fraction(code, offset, value):
        nonlocal count, largest
        if isinstance(value, Fraction):
            count += 1
            largest = max(largest, value.numerator.bit_length(), value.denominator.bit_length())

    def calendar(code, offset):
        nonlocal calendars
        calendars += 1

    meter.register_callback(key, meter.events.PY_RETURN, fraction)
    meter.register_callback(key, meter.events.PY_START, calendar)
    for method in vars(Fraction).values():
        method = getattr(method, "__func__", method)
        if inspect.isfunction(method):
            meter.set_local_events(key, method.__code__, meter.events.PY_RETURN)
    meter.set_local_events(key, Plan.__init__.__code__, meter.events.PY_START)
    try:
        build()
    finally:
        meter.free_tool_id(key)
    assert 0 < count < 2**40 and largest < 4096 and calendars == 0
    print("rational results and maximum reduced width", count, largest)
    print("operand-dependent calendars created during fixed setup", calendars)


def build():
    for name, profile in PROFILES.items():
        recipes = prepare_native(profile)
        assert tuple(r.rank_log for r in recipes) == (*profile.rank_logs, profile.complex_log)
        for plan in recipes:
            assert plan.width_log == 92 * plan.rank_log and not hasattr(plan, "count")
        bit, pos = recipes[0], recipes[-1]
        assert (len(bit.targets), len(bit.paid), len(bit.cells)) == (18906, 104652, 24)
        assert (len(pos.targets), len(pos.paid), len(pos.cells)) == (105216, 564144, 54)
        print(name, list(profile.rank_logs), profile.complex_log, flush=True)
    print("installed binary labels", len(binary_word().targets), len(binary_word().paid))
    forms, ports = fixed_binary_charts()
    assert len(forms) < 2**16 and len(ports) == 111
    print("binary difference forms and joint charts", len(forms), len(ports))


def main():
    start = perf_counter()
    measure(build)
    total = sum(expanded(f.name,f.read_bytes()) for f in (HERE/"inputs").rglob("*") if f.is_file())
    assert total < 2**30
    print("expanded packaged input bytes", total)
    print("instrumented installation seconds", round(perf_counter() - start, 3))
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("peak resident bytes", peak if sys.platform == "darwin" else 1024 * peak)


if __name__ == "__main__":
    main()
