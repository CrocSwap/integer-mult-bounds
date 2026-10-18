"""Exact lattice/source differential audit; not an analytic or kernel proof run."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import inspect
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def typed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_source():
    for item in json.loads((HERE / "VENDOR.json").read_text())["files"]:
        raw = (HERE / item["snapshot"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == item["git_blob"], "source Git blob")
    path = HERE / "vendor/pr1141/phase_stream.py"
    spec = importlib.util.spec_from_file_location("audited_phase1141", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def half_up(numerator, denominator):
    need(denominator > 0, "positive rounding denominator")
    return (2 * numerator + denominator) // (2 * denominator)


def product(coefficient, integer):
    return half_up(coefficient.numerator * integer, coefficient.denominator)


def turn(v, q):
    x, y = v
    return ((x, y), (-y, x), (-x, -y), (y, -x))[q % 4]


def lattice_rotate(v, coefficients, inverse=False):
    q, tangent, sine = coefficients
    x, y = turn(v, -q) if inverse else v
    sign = 1 if inverse else -1
    x += sign * product(tangent, y)
    y -= sign * product(sine, x)
    x += sign * product(tangent, y)
    return (x, y) if inverse else turn((x, y), q)


def lattice_chart(v, bits):
    x, y = v
    q = 0 if x >= abs(y) else 1 if y >= abs(x) else 2 if -x >= abs(y) else 3
    c, s = turn(v, -q)
    scale = 1 << bits
    fine = scale << 8
    tangent = F(half_up(s * fine, scale + c), fine)
    sine = F(s, scale)
    return q, min(F(1, 2), max(F(-1, 2), tangent)), min(F(1), max(F(-1), sine))


def lattice_step(state, omega, bits, inverse=False):
    value, ratio = state
    if inverse:
        ratio = lattice_rotate(ratio, omega, True)
        return lattice_rotate(value, lattice_chart(ratio, bits), True), ratio
    return lattice_rotate(value, lattice_chart(ratio, bits)), lattice_rotate(ratio, omega)


def to_source(v, bits):
    return tuple(F(x, 1 << bits) for x in v)


def from_source(v, bits):
    scaled = [x * (1 << bits) for x in v]
    need(all(x.denominator == 1 for x in scaled), "source left integer grid")
    return tuple(int(x) for x in scaled)


def source_state(source, value, ratio, omega, bits, length=1, index=0):
    phase = source.Phase(0, 1, bits, max(1, length), bits,
                         to_source(ratio, bits), omega, source.Meter())
    return source.State(phase, to_source(value, bits), to_source(ratio, bits), index)


def function_variant(function, before, after):
    text = inspect.getsource(function)
    need(before in text, "source mutation anchor")
    namespace = dict(function.__globals__)
    exec(compile(text.replace(before, after), "<explicit-source-negative-control>", "exec"), namespace)
    return namespace[function.__name__]


def build_result():
    source = load_source()
    rotation_cases = chart_cases = step_cases = trace_steps = 0
    digest = hashlib.sha256()
    grid = tuple(itertools.product(range(-3, 4), repeat=2))
    coefficients = tuple(itertools.product(range(4), (F(-1, 2), F(0), F(1, 2), F(3, 2)),
                                          (F(-1), F(0), F(1), F(-3, 2))))
    for bits in (0, 1, 2, 5):
        for c in coefficients:
            for v in grid:
                for inverse in (False, True):
                    expected = lattice_rotate(v, c, inverse)
                    actual = from_source(source.rotate(to_source(v, bits), c, bits, inverse), bits)
                    need(actual == expected, "source/lattice rotation")
                    need(lattice_rotate(actual, c, not inverse) == v, "lattice two-sided inverse")
                    restored = source.rotate(source.rotate(to_source(v, bits), c, bits, inverse), c, bits, not inverse)
                    need(restored == to_source(v, bits), "source two-sided inverse")
                rotation_cases += 1
        for v in itertools.product(range(-5, 6), repeat=2):
            need(source.chart(to_source(v, bits), bits, source.Meter()) == lattice_chart(v, bits), "source/lattice chart")
            chart_cases += 1
    # The exact permutation contract places no magnitude bound on dirty values.
    for bits in (2, 17):
        for power in (64, 257, 1024):
            for sign in (-1, 1):
                v = (sign * (2**power + 1), 2**(power - 1) - 1)
                c = (3, F(3, 2), F(-3, 2))
                expected = lattice_rotate(v, c)
                actual = from_source(source.rotate(to_source(v, bits), c, bits), bits)
                need(actual == expected and lattice_rotate(actual, c, True) == v, "large dirty rotation")
                need(source.chart(to_source(v, bits), bits, source.Meter()) == lattice_chart(v, bits), "large dirty chart")
                rotation_cases += 1
                chart_cases += 1
    states = tuple(itertools.product(range(-2, 3), repeat=2))
    omegas = ((0, F(1, 2), F(1)), (1, F(0), F(0)),
              (2, F(-1, 2), F(-1)), (3, F(3, 2), F(-3, 2)))
    for bits, value, ratio, omega in itertools.product((2, 5), states, states, omegas):
        initial = (value, ratio)
        for inverse in (False, True):
            st = source_state(source, value, ratio, omega, bits, index=int(inverse))
            st.step(inverse)
            actual = from_source(st.value, bits), from_source(st.ratio, bits)
            expected = lattice_step(initial, omega, bits, inverse)
            need(actual == expected, "source/lattice nonlinear step")
            st.step(not inverse)
            need((from_source(st.value, bits), from_source(st.ratio, bits)) == initial, "source nonlinear inverse")
        step_cases += 1
    traces = []
    for bits, length, omega in itertools.product((2, 7), (0, 1, 2, 7, 31, 128), omegas):
        initial = ((-17, 11), (3, -5))
        st = source_state(source, *initial, omega, bits, length=length)
        model = initial
        emitted = []
        for _ in range(length):
            emitted.append(source.chart(st.value, bits, source.Meter()))
            st.step()
            model = lattice_step(model, omega, bits)
            need((from_source(st.value, bits), from_source(st.ratio, bits)) == model, "forward trajectory")
        for _ in range(length):
            st.step(True)
            model = lattice_step(model, omega, bits, True)
            need((from_source(st.value, bits), from_source(st.ratio, bits)) == model, "reverse trajectory")
        need(model == initial and st.index == 0, "full reconstruction")
        again = []
        for _ in range(length):
            again.append(source.chart(st.value, bits, source.Meter()))
            st.step()
        need(again == emitted, "repeat deterministic readout")
        trace_steps += 3 * length
        digest.update(repr((bits, length, omega, emitted)).encode())
        traces.append({"bits": bits, "length": length, "quadrant": omega[0]})
    passes = []
    for length, numerator, modulus, bits in ((1, 1, 5, 2), (3, -4, 9, 3), (9, 1, 8, 2), (17, 7, 17, 4)):
        phase = source.Phase.prepare(numerator, modulus, bits, source.Meter(), length)
        initial = [to_source(((-1)**j * (2**64 + j), j - 9), bits) for j in range(length)]
        data = list(initial)
        phase.meter.layout = {id(data): (0, 0)}
        seed, omega = phase.seed, phase.omega
        source.phase_pass(data, phase, False)
        need(not phase.busy and phase.seed == seed and phase.omega == omega, "first pass state cleanup")
        source.phase_pass(data, phase, True)
        need(data == initial and not phase.busy and phase.seed == seed and phase.omega == omega, "actual prepared pass inverse")
        phase.clear()
        need(not phase.active and phase.seed == (0, 0) and phase.omega == (0, 0, 0), "seed cleanup")
        passes.append({"length": length, "numerator": numerator, "modulus": modulus, "bits": bits})

    controls = []
    # Mutate actual predecessor code: negating a rounded product is not the
    # same as rounding its negation at the source's asymmetric half ties.
    wrong = function_variant(source.rotate,
                             "real += real_round(tangent*imag, bits)",
                             "real -= real_round(-tangent*imag, bits)")
    v, c = (F(0), F(1, 4)), (0, F(1, 2), F(0))
    need(wrong(source.rotate(v, c, 2), c, 2, True) != v, "negated-coefficient inverse fault")
    controls.append("actual_rotate_negated_rounding_ties")
    wrong = function_variant(source.rotate, "quarter_turn(value, (-quadrant) % 4)", "value")
    v, c = (F(2), F(3)), (1, F(0), F(0))
    need(wrong(source.rotate(v, c, 2), c, 2, True) != v, "missing inverse quarter turn")
    controls.append("actual_rotate_missing_quarter_inverse")
    # Model a stale-chart inverse with the original authenticated functions.
    omega = (1, F(0), F(0)); initial = ((0, 4), (4, 0))
    forward = lattice_step(initial, omega, 2)
    stale = (lattice_rotate(forward[0], lattice_chart(forward[1], 2), True),
             lattice_rotate(forward[1], omega, True))
    need(stale != initial, "stale chart fault")
    controls.append("chart_before_ratio_restoration")
    need(forward != initial, "omitted reverse step fault")
    controls.append("incomplete_reconstruction")
    st = source_state(source, (4, 0), (0, 4), omega, 2)
    emitted = st.coefficients()
    st.step()
    try:
        st.erase_coefficients(emitted)
    except (ValueError, AssertionError):
        controls.append("emitted_coefficients_erased_after_state_change")
    else:
        raise ValueError("late coefficient erasure was not rejected")
    need(product(F(1, 2), 1) != -product(F(-1, 2), 1), "tie asymmetry countermodel")
    controls.append("rounder_need_not_be_odd")
    return {"rotation_cases": rotation_cases, "chart_cases": chart_cases, "nonlinear_state_cases": step_cases,
            "traces": traces, "trace_steps": trace_steps, "readout_sha256": digest.hexdigest(),
            "prepared_passes": passes, "controls": controls,
            "scope": "Exact grid reconstruction only; no analytic error, complexity, full dirty wrapper or compiler proof.",
            "kernel_run_by_this_command": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    path = HERE / "RESULT.json"
    if args.write:
        need(not path.exists(), "refuse receipt overwrite")
    spec = importlib.util.spec_from_file_location("phase_kernel_receipt", HERE / "kernel.py")
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    kernel.receipt_check()  # Structural receipt check only; does not launch Lean.
    result = build_result()
    if args.write:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        need(typed(result) == typed(json.loads(path.read_text())), "receipt mismatch")
    print("PASS_ROUNDED_PHASE_RECONSTRUCTION " + typed({k: result[k] for k in ("rotation_cases", "chart_cases", "nonlinear_state_cases", "trace_steps")}))


if __name__ == "__main__":
    main()
