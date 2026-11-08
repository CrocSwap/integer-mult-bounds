"""Exact source-bound algebra and actual physical compiler-boundary checks."""
from fractions import Fraction
from contextlib import contextmanager
from collections import Counter as Observations
from hashlib import sha256
from pathlib import Path
import argparse
import importlib
import importlib.metadata
import json
import platform
import random
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings
from frontend import (HADAMARD, SIGNS, HALF, Layout, PreparedCall, address,
                      compile_route, encode_controls, need)


def permutation_target(values, program, coefficients=1, rows=1):
    """Independent endpoint oracle: original axis images, without H or D words."""
    layout = program.layout
    labels = {label: c for c, label in enumerate(layout.labels)}
    out = [None]*len(values)
    local_mask = (1 << layout.local_bits)-1
    for row in range(rows):
        for old in range(1 << layout.n):
            label = tuple((old >> (start+layout.local_bits)) & ((1 << (width-layout.local_bits))-1)
                          for start, width in zip(layout.starts, layout.lengths))
            new = old
            for axis, start in enumerate(layout.starts):
                original_local = (old >> start) & local_mask
                image = program.permutations[labels[label]][axis][original_local]
                new = (new & ~(local_mask << start)) | (image << start)
            for c in range(coefficients):
                out[(row*(1 << layout.n)+new)*coefficients+c] = values[(row*(1 << layout.n)+old)*coefficients+c]
    need(all(x is not None for x in out), "independent original-coordinate bijection")
    return out


def algebra_execute(values, program, wrong_diagonal=False, omit_normalization=False):
    layout = program.layout
    data = [(Fraction(a), Fraction(b)) for a, b in values]
    packed = [None]*len(data)
    for original, value in enumerate(data):
        packed[address(original, layout.gather)] = value
    n = 1 << layout.local_bits
    for kind, value in program.stages:
        if kind == HADAMARD:
            for axis, bit in enumerate(value):
                mask = 1 << (axis*layout.local_bits+bit)
                for index in range(len(packed)):
                    if not index & mask:
                        a, b = packed[index], packed[index | mask]
                        packed[index] = tuple(x+y for x, y in zip(a, b))
                        packed[index | mask] = tuple(x-y for x, y in zip(a, b))
        elif kind == SIGNS:
            for index, entry in enumerate(packed):
                label = index >> (layout.g*layout.local_bits)
                if wrong_diagonal:
                    label = 0
                sign = 0
                for axis in range(layout.g):
                    local = (index >> (axis*layout.local_bits)) & (n-1)
                    sign ^= value[label][axis][local]
                if sign:
                    packed[index] = (-entry[0], -entry[1])
        elif not omit_normalization:
            packed = [tuple(x/(1 << layout.g) for x in entry) for entry in packed]
    return [packed[address(original, layout.gather)] for original in range(len(packed))]


def make_program(compiler, lengths, m, seed):
    rng = random.Random(seed)
    layout = Layout(tuple(lengths), m)
    rows = []
    for _ in layout.labels:
        group = []
        for _ in range(layout.g):
            perm = list(range(1 << m))
            rng.shuffle(perm)
            group.append(perm)
        rows.append(group)
    return compile_route(compiler, layout, rows)


def algebra(compiler):
    cases = []
    bad_label = bad_scale = 0
    s = compiler.s
    C = s.Matrix([[1+s.I, 1-s.I], [1-s.I, 1+s.I]])/2
    phase = s.diag(1, s.I)
    need(s.simplify(((1-s.I)/2)*phase*C*phase) == compiler.H/2,
         "source Gaussian C/phase/normalizer convention")

    class AppendOnlyControl:
        def __init__(self):
            self.data = []
        def append(self, value):
            need(value in (0, 1), "binary prepared control")
            self.data.append(value)
        def rewind(self):
            pass

    encoded_stages = 0
    for m, g, extras, seed in ((1, 1, (2,), 54), (1, 3, (0, 1, 1), 55),
                               (2, 2, (1, 1), 56), (3, 2, (1, 0), 57),
                               (2, 3, (0, 1, 0), 58)):
        lengths = tuple(m+x for x in extras)
        program = make_program(compiler, lengths, m, seed)
        values = [((i*7)%13-6, (i*11)%17-8) for i in range(1 << sum(lengths))]
        expected = permutation_target(values, program)
        actual = algebra_execute(values, program)
        need(actual == expected, "complete retained global compiler route")
        _, _, prepared = encode_controls(program, AppendOnlyControl)
        cursor = 0
        position_width = max(1, (program.layout.n-1).bit_length())
        for kind, value in program.stages:
            need(prepared.data[cursor:cursor+2] == [kind & 1, kind >> 1], "source opcode export")
            cursor += 2
            if kind == HADAMARD:
                for axis, local in enumerate(value):
                    block = prepared.data[cursor:cursor+position_width]
                    selected = sum(bit*(1 << index) for index, bit in enumerate(block))
                    need(selected == axis*m+local, "source global selected coordinate export")
                    cursor += position_width
            elif kind == SIGNS:
                expected_bits = [bit for coarse in value for axis in coarse for bit in axis]
                need(prepared.data[cursor:cursor+len(expected_bits)] == expected_bits,
                     "sequential source-preparation equals complete stage tables")
                cursor += len(expected_bits)
            encoded_stages += 1
        need(prepared.data[cursor:] == [0, 0], "exact source control ending")
        bad_label += algebra_execute(values, program, wrong_diagonal=True) != expected
        bad_scale += algebra_execute(values, program, omit_normalization=True) != expected
        cases.append(dict(m=m, g=g, n=sum(lengths), seed=seed, stages=len(program.stages),
                          coefficients=len(values), coarse_labels=len(program.layout.labels)))
    need(bad_label >= 4 and bad_scale == len(cases), "nonconstant-label and raw-H controls discriminate")
    lifts = 0
    for w in range(2, 7):
        for g in range(1, 5):
            P = w+g
            for a in range(-(1 << (w-1)), 1 << (w-1)):
                for b in range(-(1 << (w-1)), 1 << (w-1)):
                    need((a << g)**2+(b << g)**2 < 1 << (2*P), "encoded complex unit disk")
                    lifts += 1
    return dict(status="PASS_COMPILER_T74_ALGEBRA", cases=cases,
                complex_lifts=lifts, encoded_source_stages=encoded_stages,
                coarse_label_controls=bad_label, normalization_controls=bad_scale)


def finite_owner(recursive):
    """Actual #3627 fixture binding with its explicitly reduced row geometry.

    Only precision varies in the 7-axis geometry; dependent lengths are
    computed. This is not the production guard or selected finite supplier.
    """
    source = importlib.import_module("check_composed")
    owner, visits = source.fixture("fixture-ell1" if recursive else "standard", recursive)
    if not recursive:
        return owner, visits
    from active_plan import ActiveWidthPlan
    from cardinal_counts import Count
    from encoded import compare
    from machine import copy_symbols
    from router_metadata import owned
    from session import sealed_constructors

    class ReducedPlan(ActiveWidthPlan):
        def compute(self, precision, selected, left, right, coefficients, outer_rows, residue):
            self.clear()
            need(self.closed and not self.pool.live, "closed reduced recursive fixture")
            with sealed_constructors(), self.scope.installed():
                for actual, expected in zip((selected, left, right, coefficients, outer_rows, residue),
                                            (7, 1, 0, 2, 1, 0)):
                    with owned(Count.literal(expected)) as (constant,):
                        need(compare(actual, constant) == 0, "declared recursive fixture geometry")
                fixed = dict(selected=7, left=1, right=0, coefficients=2, outer_rows=1, residue=0,
                             zero=0, d=7, K=1, G=1, H=1, depth=2, q0=2, qF=2, qB=1, Q0=5,
                             delta=28, gaussians=512, prefixes=2, original_rows=4, padded_rows=4,
                             stock=4, core_width=2, core_front=0, core_back=0)
                for name, value in fixed.items():
                    with owned(Count.literal(value)) as (constant,):
                        copy_symbols(constant.tape, self.roles[name])
                copy_symbols(precision.tape, self.roles["precision"])
                with owned(Count(precision), Count.literal(2), Count(precision), Count.literal(59)) as (inp, two, work, extra):
                    inp.add(two)
                    work.add(extra)
                    copy_symbols(inp.tape, self.roles["input_bits"])
                    copy_symbols(work.tape, self.roles["work_bits"])
                    work.multiply_small(128)
                    copy_symbols(work.tape, self.roles["row_bits"])
                self.pool.empty()
            self.fast = True
            self.closed = True
            return self

    owner.root.plan = ReducedPlan(2, 1, 2, guard_exponent=2)
    return owner, visits


@contextmanager
def certified_fixture_floors():
    """Exactly specialize two costly encoded powers on a finite declared set.

    The actual exposure and direct-root plan producers still run. Only their
    integer floor-power helper is replaced by a compiled finite lookup. Each
    value is independently certified by two exact integer inequalities; no
    payload value or runtime Count is decoded to select it. Production uses
    the unchanged general helper and does not enter this context.
    """
    import active_plan
    import composed_plan
    from cardinal_counts import Count
    from encoded import compare
    from router_metadata import owned
    table = {}
    for numerator, denominator in ((997, 1000), (1, 500)):
        for base in range(1, 33):
            target = base**numerator
            lower = 1
            while (lower+1)**denominator <= target:
                lower += 1
            need(lower**denominator <= target < (lower+1)**denominator,
                 "independent exact finite floor-power certificate")
            table[(numerator, denominator, base)] = lower
    certify_fixture_floor_table(table)
    uses, misses = {}, []
    original_active = active_plan.floor_power
    original_exposure = composed_plan.floor_power

    def folded(value, numerator, denominator, delegate):
        if (numerator, denominator) in ((997, 1000), (1, 500)):
            for base in range(1, 33):
                with owned(Count.literal(base)) as (candidate,):
                    if compare(value, candidate) == 0:
                        key = (numerator, denominator, base)
                        uses[key] = uses.get(key, 0)+1
                        return Count.literal(table[key])
        misses.append([numerator, denominator])
        return delegate(value, numerator, denominator)

    with patch.object(active_plan, "floor_power", lambda value, a, b: folded(value, a, b, original_active)), \
            patch.object(composed_plan, "floor_power", lambda value, a, b: folded(value, a, b, original_exposure)):
        yield table, uses, misses


def certify_fixture_floor_table(table):
    domain = {(a, b, n) for a, b in ((997, 1000), (1, 500)) for n in range(1, 33)}
    need(set(table) == domain, "complete declared floor-power certificate domain")
    for (a, b, n), root in table.items():
        need(type(root) is int and root >= 0 and root**b <= n**a < (root+1)**b,
             "independent exact finite floor-power certificate")


def physical_case(compiler, recursive=False):
    from bridge import GlobalBoundary
    from cardinal_counts import Count
    from check_support import bits, no_decode
    from records import Tape
    from session import erase_marker
    from words import BLANK
    source = importlib.import_module("check_composed")
    if recursive:
        program = make_program(compiler, (1, 1, 1, 1, 1, 2, 2), 1, 84)
        p, w, coefficients, rows = 0, 2, 1, 1
    else:
        program = make_program(compiler, (2, 1), 1, 54)
        p, w, coefficients, rows = 0, 2, 1, 1
    n, g = program.layout.n, program.layout.g
    values = [((-1 if i%3 == 0 else 1 if i%3 == 1 else 0),
               (-1 if i%5 == 0 else 1 if i%5 == 1 else 0)) for i in range((1 << n)*coefficients*rows)]
    expected_values = permutation_target(values, program, coefficients, rows)
    original = source.encode(values, w)
    expected = source.encode(expected_values, w)
    owner, visits = finite_owner(recursive)
    observations = Observations()
    boundary = GlobalBoundary(owner, lambda event: observations.update([event]))
    payload = Tape()
    for bit in original:
        payload.append(bit)
    payload.rewind()
    prepared = PreparedCall(program, p, w, coefficients, rows, Tape, Count)
    forward, inverse, code = prepared.controls
    all_tapes = (payload, forward, inverse, code)
    saved = [(bytes(t.cells), t.head) for t in all_tapes]
    counts = prepared.parameters
    saved_counts = [(bytes(x.tape.cells), x.tape.head) for x in counts]
    raw_entries, exposures, router_plans, root_plans, bit_plans = [], [], [], [], []
    retained = owner.run
    from composed_plan import ExposurePlan
    from router_plan import Plan as RouterPlan
    from composed_sources import active
    from check_support import inspect_count
    compile_exposure = ExposurePlan.compile
    compile_router = RouterPlan.compile
    compute_root = owner.root.plan.compute
    select_bit = active().root.ordinary.select

    def observe(payload_, selected_, *args):
        raw_entries.append(dict(parameters=[inspect_count(x) for x in args],
                                selected_descriptor=list(bits(selected_))))
        return retained(payload_, selected_, *args)

    def observe_exposure(plan, selected):
        result = compile_exposure(plan, selected)
        exposures.append(dict(mode=plan.mode, fields={name: inspect_count(value)
                         for name, value in sorted(plan.fields.items())}))
        return result

    def observe_root(*args):
        result = compute_root(*args)
        root_plans.append(dict(fast=result.fast, fields={name: inspect_count(result.count(name))
                          for name in sorted(result.roles)}))
        return result

    def observe_router(plan, pairs):
        result = compile_router(plan, pairs)
        router_plans.append(dict(mode=plan.mode, parameters={name: inspect_count(getattr(plan, name))
                            for name in ("n", "p", "k", "width")},
                            fields={name: inspect_count(value) for name, value in sorted(plan.fields.items())}))
        return result

    def observe_bit(width, q, profile):
        result = select_bit(width, q, profile)
        bit_plans.append(dict(q=q, profile=[profile.numerator, profile.denominator],
                         fields={name: value if name == "fits" else inspect_count(value)
                                 for name, value in sorted(result.items())}))
        return result

    try:
        with no_decode(), patch.object(owner, "run", observe), \
                patch.object(ExposurePlan, "compile", observe_exposure), \
                patch.object(RouterPlan, "compile", observe_router), \
                patch.object(owner.root.plan, "compute", observe_root), \
                patch.object(active().root.ordinary, "select", observe_bit):
            returned = prepared.run(boundary, payload)
        actual = bits(returned)
        need(actual == expected, "physical emitted global route on original coordinates")
        need([(bytes(t.cells), t.head) for t in all_tapes] == saved, "borrowed full packets and program preserved")
        need([(bytes(x.tape.cells), x.tape.head) for x in counts] == saved_counts, "borrowed encoded parameters preserved")
        boundary.idle()
        need(boundary.closed and boundary.current is None and not boundary.pool.live,
             "closed physical global-boundary owner")
        need(all(t.head == 1 and all(x == BLANK for x in t.cells) for t in boundary.pool.tapes),
             "erased wrapper physical bodies and markers")
        need(owner.root.machine.closed and owner.root.plan.closed and not owner.root.plan.pool.live
             and all(t.head == 1 and t.read() == BLANK for t in owner.root.plan.roles.values()),
             "restored actual recursive machine and root planning baselines")
        need(visits.get("enter", 0) == visits.get("return", 0), "balanced actual recursive child return")
        need(not recursive or visits.get("enter", 0) > 0, "actual recursive backend was executed")
        need(all(x["profile"] == [1, 577] for x in bit_plans), "actual retained BIT selector")
        from controls import rejects
        protected = rejects(lambda: prepared.run(boundary, payload),
                            "consume the previous compiler-boundary output")
        return dict(status="PASS_COMPILER_T74_PHYSICAL", recursive=recursive,
                    source_permutation_seed=84 if recursive else 54,
                    original_axis_lengths=list(program.layout.lengths), p=p, signed_width=w,
                    raw_H_entries=raw_entries, calls=dict(boundary.calls, **observations),
                    actual_exposure_plans=exposures, actual_root_plans=root_plans,
                    actual_router_plans=router_plans,
                    actual_BIT_plans=bit_plans,
                    protected_output_rejection=protected,
                    root_calls=dict(owner.calls), child_events=dict(visits),
                    wrapper_peak_leases=boundary.pool.peak,
                    payload_bits=len(original), output_sha256=sha256(actual).hexdigest(),
                    code_sha256=sha256(bytes(code.cells)).hexdigest(),
                    export=program.export())
    finally:
        if boundary.output.read() != BLANK:
            boundary.output.clear()
            erase_marker(boundary.output)
        payload.clear()
        prepared.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("algebra", "physical", "recursive", "controls"), required=True)
    args = parser.parse_args()
    pins = bindings.authenticate()
    compiler = bindings.compiler()
    need(compiler.s.__version__ == "1.13.3", "declared exact SymPy version")
    if args.suite == "algebra":
        result = algebra(compiler)
    elif args.suite == "controls":
        from controls import physical_macros, source_and_compiler
        result = dict(status="PASS_COMPILER_T74_CONTROLS", source=source_and_compiler(compiler))
        with bindings.runtime():
            owner, _ = finite_owner(False)
            result["physical"] = physical_macros(owner)
            from controls import floor_controls
            result["finite_floor_controls"] = floor_controls(certified_fixture_floors, certify_fixture_floor_table)
    else:
        with bindings.runtime():
            with certified_fixture_floors() as (table, uses, misses):
                result = physical_case(compiler, args.suite == "recursive")
                result["finite_exact_metadata_folds"] = [
                    dict(numerator=key[0], denominator=key[1], input=key[2],
                         output=table[key], calls=uses[key]) for key in sorted(uses)]
                result["floor_certificate_domain"] = dict(inputs=[1, 32], exponent_pairs=[[997, 1000], [1, 500]])
                result["floor_cache_fallback_calls"] = misses
    result["source_sha256"] = pins
    result["environment"] = dict(python=platform.python_version(), sympy=compiler.s.__version__,
                                 mpmath=importlib.metadata.version("mpmath"),
                                 optimization=sys.flags.optimize)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
