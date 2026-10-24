"""Encoded production parameters and locality admission without enormous payloads."""
from math import isqrt
from gaussian_sources import require


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_prepare import ProductionPlan
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, sealed_constructors
    from words import BLANK
    pool = ScratchPool(128)
    scope = OuterScope(pool)
    p, u, d, t = 16384, 32, 384, 1 << 64
    s = t-t//(3*d)
    radicand = (16*p+u-1)//u
    root = isqrt(radicand)
    w = root+int(root*root != radicand)+2
    margin = 512*p*p*w
    core_start, core_length = margin+1, 17
    target_length = ((2*margin+core_length+10)*t+s-1)//s+2
    parameters = [s, t, d, u, p, 0, target_length, core_start, core_length]

    def check(values, failure=None):
        counts = tuple(Count.literal(value) for value in values)
        saved = [(bytes(value.tape.cells), value.tape.head) for value in counts]
        plan = None
        try:
            with sealed_constructors(), scope.installed():
                try:
                    s, t, d, u, p, start, length, core, core_count = counts
                    with no_decode():
                        try:
                            plan = ProductionPlan(s, t, d, u, p, Signed(start), length, Signed(core), core_count)
                        except ValueError as error:
                            require(failure is not None and failure in str(error), "precise production-domain rejection")
                            return None
                    require(failure is None, "missing production-domain rejection")
                    result = {name: decode(getattr(plan, name)) for name in ("P", "w", "m", "margin")}
                    result["start"] = (-1 if plan.start.negative else 1)*decode(plan.start.magnitude)
                    result["end"] = (-1 if plan.end.negative else 1)*decode(plan.end.magnitude)
                    return result
                finally:
                    if plan is not None:
                        plan.close()
                    pool.empty()
                    require(saved == [(bytes(value.tape.cells), value.tape.head) for value in counts],
                            "production planning preserves borrowed parameters")
        finally:
            for value in counts:
                value.close()

    actual = check(parameters)
    expected_end = (s*(2*target_length-1)+2*t-1)//(2*t)
    require(actual == {"P": 32768*p, "w": w, "m": expected_end, "margin": margin,
                       "start": 0, "end": expected_end}, "exact production precision, radius and source window")
    controls = []
    for name, index, value, message in (
        ("small_target_precision", 4, 100, "target precision at least101"),
        ("oversized_lifted_descriptor", 5, 1 << (p+2), "fits declared word width"),
        ("insufficient_concentration", 3, 1, "logarithmic Gaussian concentration"),
        ("excess_similarity", 3, p, "Gaussian similarity guard"),
        ("whole_period_window", 6, t, "principal complement gap"),
        ("insufficient_left_halo", 7, margin, "left core halo")):
        changed = list(parameters)
        changed[index] = value
        check(changed, message)
        controls.append(name)
    changed = list(parameters)
    changed[6] = ((core_start+core_length+margin-2)*t+s-1)//s
    check(changed, "right core halo")
    controls.append("insufficient_right_halo")
    for tape in pool.tapes:
        erase_marker(tape)
        require(tape.head == 1 and all(value == BLANK for value in tape.cells), "production parameter restoration")
    return {"p": p, "u": u, "d": d, "s": str(s), "t": str(t),
            "derived": {key: str(value) for key, value in actual.items()},
            "controls": controls, "pool_peak": pool.peak,
            "scope": "metadata-only production binding; no P-grid coefficient page or huge target halo is materialized"}
