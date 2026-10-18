#!/usr/bin/env python3
"""Source-bound physical composition, with actual opaque native intervals.

Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from bounds import (census, exact_setup, nonnative_bound, require,
                    sign_acquisitions, translation_bound)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate(rows=None):
    if rows is None:
        manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
        rows = manifest["files"]
        for proof in manifest["external_proofs"]:
            relative = Path(proof["copy"])
            require(not relative.is_absolute() and ".." not in relative.parts, "contained proof copy")
            source = PACKAGE / relative
            require(source.is_file() and not source.is_symlink(), "regular proof copy")
            require(source.stat().st_size <= 1024 * 1024, "bounded proof copy")
            require(hashlib.sha256(source.read_bytes()).hexdigest() == proof["sha256"], "proof copy hash")
    data = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        relative = row["path"]
        require(relative not in data and not Path(relative).is_absolute(), "unique relative source")
        require(".." not in Path(relative).parts, "contained source")
        source = ROOT / relative
        require(source.is_file() and not source.is_symlink(), "regular source: " + relative)
        require(source.stat().st_size <= 32 * 1024 * 1024, "bounded source")
        raw = source.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + relative)
        data[relative] = raw
    require(sum(map(len, data.values())) <= 64 * 1024 * 1024, "bounded source closure")
    return data


def source_module(name, relative, data):
    result = ModuleType(name)
    result.__file__ = str(ROOT / relative)
    sys.modules[name] = result
    exec(compile(data[relative], result.__file__, "exec"), result.__dict__)
    return result


def load():
    data = authenticate()
    prefix = source_module("cube_prefix_runtime", "research/high-route-prefix-cost/runtime.py", data)
    # Keep the predecessor's complete modules/observer. Replace only the
    # authentication callback with this package's explicit, checked closure.
    prefix.authenticate = lambda: data
    invoice = source_module("cube_prefix_invoice", "research/high-route-prefix-cost/invoice.py", data)
    runtime = prefix.load()
    require(Path(sys.modules["linear_sign"].__file__).read_bytes() == data["research/linear-sign-total-traffic/sources/linear_sign.py"], "PR2877 sign bytes match the reached source")
    return prefix, invoice, runtime


def count_value(value):
    tape = value.tape if hasattr(value, "tape") else value
    tape = getattr(tape, "physical", tape)
    digits = []
    for digit in tape.cells[1:]:
        if digit == 3:  # RIGHT; checker observation, never production control.
            break
        require(digit in (0, 1), "binary observer input")
        digits.append(digit)
    else:
        raise ValueError("missing numeric delimiter")
    return sum(bit << i for i, bit in enumerate(digits)), len(digits)


WORDS = {
    "empty": (),
    "ordered": (("add", 1, 0, Fraction(1)),),
    "reversed": (("add", 0, 1, Fraction(-4)),),
    "swap": (("swap", 0, 1, Fraction(1)),),
    "scale": (("scale", 0, 0, Fraction(2)),),
    "half": (("scale", 1, 1, Fraction(1, 2)),),
    "negative_carry": (("scale", 0, 0, Fraction(-4)),),
    "positive_carry": (("scale", 0, 0, Fraction(4)),),
    "mixed": (("add", 0, 1, Fraction(1, 2)), ("scale", 1, 1, Fraction(-2)), ("swap", 0, 1, Fraction(1))),
}


def prepare(prefix, runtime, name, q=3, width=2, fibre=1, prefixes=1, low=None, inverse=False, occupied=0):
    state = prefix.prepare(runtime, prefixes, q, width, fibre, False, 0)
    word = WORDS[name]
    if inverse:
        word = sys.modules["compile_routes"].inverse_word(word)
    state.chart = runtime.retained.replay(word, 2)
    registry = runtime.registry(2)
    registry.register(state.chart, word)
    state.route = runtime.routes.compile_route(low or ((1, 0), (0, 1)), state.chart, state.codes)
    state.adapter.registry = registry
    # One-hot payloads avoid the periodic missing-swap false negative in PR3265.
    state.initial = bytes(int(i % state.bits == min(1, state.bits - 1)) for i in range(prefixes * state.bits))
    state.source.cells[1:len(state.initial) + 1] = state.initial
    state.entry_owners = {}
    for index in range(occupied):
        owner = state.pool.acquire()
        for bit in (1, 0, index % 2, 1):
            owner.append(bit)
        owner.rewind()
        state.entry_owners[owner.slot] = (owner, bytes(owner.physical.cells))
    return state


def complete_endpoint(state, output):
    """PR2982's independent matrix oracle extended from I to the actual low row."""
    modulus, high = state.q ** state.width, state.q ** (state.width - 1)
    lifted = [[int(value.numerator * pow(value.denominator, -1, modulus)) % modulus
               for value in row] for row in state.chart]
    expected = bytearray(len(state.initial))
    for ordinal in range(high ** 4):
        digits, remaining = [0] * 4, ordinal
        for position in range(3, -1, -1):
            remaining, digits[position] = divmod(remaining, high)
        matrix = [[state.route.low[i][j] + state.q * digits[2 * i + j]
                   for j in range(2)] for i in range(2)]
        target = 0
        for i in range(2):
            for j in range(2):
                value = sum(matrix[i][k] * lifted[k][j] for k in range(2)) % modulus
                target = target * high + (value - state.route.target_low[i][j]) // state.q
        for prefix_index in range(state.prefixes):
            for suffix in range(state.fibre_value):
                source = prefix_index * state.bits + ordinal * state.fibre_value + suffix
                destination = prefix_index * state.bits + target * state.fibre_value + suffix
                expected[destination] = state.initial[source]
    require(bytes(output.physical.cells[1:len(expected) + 1]) == expected, "affine endpoint")
    require(all(bit == state.runtime.words.BLANK for bit in output.physical.cells[len(expected) + 1:]), "complete output extent")
    require(state.source.head == output.head == 1, "endpoint heads")


def completed_boundary(prefix, state, output, originals):
    expected = {slot: row[0] for slot, row in state.entry_owners.items()}
    expected[output.slot] = output
    require(state.pool.live == expected, "preserved entry owners and one distinct output")
    for owner, original in state.entry_owners.values():
        require(owner.head == 1 and bytes(owner.physical.cells) == original, "occupied dirty role preserved")
    borrowed = prefix.borrowed_tapes(state)
    require(tuple(bytes(tape.cells) for tape in borrowed) == originals, "borrowed bytes preserved")
    require(all(tape.head == 1 for tape in borrowed), "borrowed heads restored")
    require(not state.adapter.high_bank.live and not state.adapter.high_bank.initialized, "high bank erased")
    require(state.native.closed and state.native.output.read() == state.runtime.words.BLANK, "native output consumed")
    complete_endpoint(state, output)


def check_partition(total, wrapper, setup, adapters, kernels):
    require(total == wrapper + setup + sum(row["traffic"] for row in adapters + kernels), "exact complete paid partition")


def check_native_count(actual, prefixes, counts):
    require(actual == prefixes * counts["native_calls"], "both reversed-ADD native swaps retained")


def run_case(prefix, invoice, runtime, parameters, mutation=None):
    state = prepare(prefix, runtime, **parameters)
    high = state.q ** (state.width - 1)
    operations = state.adapter.registry.compile(state.route) if high > 1 else ()
    counts = census(operations)
    trace = prefix.Trace(runtime, state.native)
    native_rows, adapter_rows, kernel_rows, sign_rows, shift_rows = [], [], [], [], []
    total_acquisitions = 0
    kernels = sys.modules["kernels"]
    originals = tuple(bytes(t.cells) for t in prefix.borrowed_tapes(state))
    tapes = prefix.physical_tapes(state)
    input_width = count_value(state.context.cap)[1]
    original_acquire = state.pool.acquire

    def acquire():
        nonlocal total_acquisitions
        total_acquisitions += 1
        return original_acquire()

    native_run = state.native.run

    def native(*args, **kwargs):
        start = trace.snapshot()
        output = native_run(*args, **kwargs)
        native_rows.append(dict(traffic=trace.snapshot() - start, fitted=state.native.last_fitted))
        return output

    adapter_swap = state.adapter.swap

    def swap(*args, **kwargs):
        start, count = trace.snapshot(), len(native_rows)
        output = adapter_swap(*args, **kwargs)
        if mutation == "adapter_read":
            args[0].read()  # Same endpoint, one extra physical operation.
        toll = trace.snapshot() - start
        require(len(native_rows) == count + 1, "one native call per whole swap adapter")
        native_toll = native_rows[-1]["traffic"]
        require(toll - native_toll <= 100000 * state.bits, "swap adapter majorant")
        adapter_rows.append(dict(traffic=toll, native=native_toll, overhead=toll - native_toll))
        return output

    def kernel(name, method):
        def observed(*args, **kwargs):
            start = trace.snapshot()
            if mutation == "coefficient" and name == "added":
                args = (*args[:-1], -args[-1])
            output = method(*args, **kwargs)
            toll = trace.snapshot() - start
            factor = {"added": 4096, "doubled": 530, "negated": 4096, "translated": 32768}[name]
            require(toll < factor * state.bits, name + " complete kernel tariff")
            kernel_rows.append(dict(kind=name, traffic=toll))
            return output
        return observed

    sign_method, shift_method = kernels.sign_address, kernels.translate_one

    def sign(source, ring, q, before, suffix):
        modulus, _ = count_value(ring.modulus)
        leading, _ = count_value(before)
        trailing, _ = count_value(suffix)
        start, acquisitions = trace.snapshot(), total_acquisitions
        output = sign_method(source, ring, q, before, suffix)
        toll, used = trace.snapshot() - start, total_acquisitions - acquisitions
        require(used == sign_acquisitions(modulus, leading, trailing), "exact pooled-sign acquire count")
        require(toll < 2053 * leading * modulus * trailing, "pooled sign transfer")
        sign_rows.append(dict(traffic=toll, acquisitions=used, modulus=modulus, before=leading, suffix=trailing))
        return output

    def shift(source, ring, before, suffix):
        modulus, _ = count_value(ring.modulus)
        leading, _ = count_value(before)
        trailing, _ = count_value(suffix)
        start = trace.snapshot()
        output = shift_method(source, ring, before, suffix)
        toll = trace.snapshot() - start
        majorant = translation_bound(modulus, leading, trailing)
        require(toll <= majorant < 1024 * leading * modulus * trailing, "pooled unit-translation tariff")
        shift_rows.append(dict(traffic=toll, majorant=majorant, modulus=modulus, before=leading, suffix=trailing))
        return output

    try:
        with ExitStack() as stack:
            stack.enter_context(trace.installed())
            stack.enter_context(patch.object(state.pool, "acquire", acquire))
            stack.enter_context(patch.object(state.native, "run", native))
            stack.enter_context(patch.object(state.adapter, "swap", swap))
            for name in ("added", "doubled", "negated", "translated"):
                stack.enter_context(patch.object(kernels, name, kernel(name, getattr(kernels, name))))
            stack.enter_context(patch.object(kernels, "sign_address", sign))
            stack.enter_context(patch.object(kernels, "translate_one", shift))
            stack.enter_context(state.scope.install())
            start, raw = trace.snapshot(), prefix.meters(tapes, trace)
            output = runtime.routes.route_packet(state.source, state.route, state.context, state.old_count, state.fibre)
            total = trace.snapshot() - start
            require(total == prefix.meters(tapes, trace) - raw, "raw physical meter / independent observer")
            try:
                completed_boundary(prefix, state, output, originals)
            finally:
                output.clear()
            check_native_count(len(native_rows), state.prefixes, counts)
            expected_kernels = {"added": counts["add"], "doubled": counts["scale"], "negated": counts["negate"], "translated": counts["translate"]}
            require(Counter(row["kind"] for row in kernel_rows) == Counter({key: value * state.prefixes for key, value in expected_kernels.items() if value}), "compiled kernel census")
            require(all(not row["fitted"] for row in native_rows), "elementary fixtures only")
            wrapper = invoice.wrapper(state.prefixes, high**4, state.fibre_value)
            setup = state.prefixes * exact_setup(high, state.fibre_value, 2, input_width, state.adapter.high_bank.capacity, operations, invoice.copy_rows)
            check_partition(total, wrapper, setup, adapter_rows, kernel_rows)
            native_toll = sum(row["traffic"] for row in native_rows)
            limit = state.prefixes * nonnative_bound(high, state.fibre_value, 2, input_width, state.adapter.high_bank.capacity, operations) + 265 * len(state.initial)
            require(total - native_toll <= limit, "complete non-native packet majorant")
            for owner, _original in state.entry_owners.values():
                owner.clear()
            state.pool.empty()
        return dict(parameters=parameters, bits=len(state.initial), compiled=[list(op) for op in operations], counts=counts,
                    total=total, wrapper=wrapper, setup=setup, native=native_toll,
                    nonnative=total-native_toll, nonnative_bound=limit,
                    adapters=adapter_rows, kernels=kernel_rows, signs=sign_rows, shifts=shift_rows)
    finally:
        for owner, _original in state.entry_owners.values():
            owner.clear()
        prefix.cleanup(state)


CASES = (
    dict(name="empty", width=1, fibre=3),
    dict(name="empty", q=5),
    dict(name="ordered"),
    dict(name="reversed"),
    dict(name="swap", fibre=3),
    dict(name="scale"),
    dict(name="half"),
    dict(name="negative_carry", q=5, low=((4, 1), (1, 1))),
    dict(name="positive_carry", q=5, low=((4, 1), (1, 1))),
    dict(name="mixed", fibre=3),
    dict(name="mixed", inverse=True),
    dict(name="mixed", width=3),
    dict(name="mixed", prefixes=3),
    dict(name="mixed", occupied=2),
)


def check_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "complete typed receipt")


def radix_checks(runtime):
    """Wide numerical contexts without allocating their exponential payloads."""
    rows = []
    for q, exponent in ((3, 1), (3, 8), (3, 32), (5, 7), (97, 8), (2**89 - 1, 3)):
        maximum = runtime.cardinal_counts.Count.literal(q**exponent)
        width = runtime.cardinal_counts.Count.literal(0)
        bank = runtime.physical_words.PhysicalArena(16)
        bank.prepare(maximum)
        modulus = bank.load(maximum)
        ring = runtime.words.Ring(modulus)
        tapes = [word.tape for word in (*bank.words, bank.template)] + [maximum.tape, width.tape]
        operations = 0

        def wrap(method):
            def counted(*args, **kwargs):
                nonlocal operations
                operations += 1
                return method(*args, **kwargs)
            return counted

        def raw_meter():
            return sum(tape.meter.reads + tape.meter.writes + tape.meter.moves for tape in tapes)

        try:
            with ExitStack() as stack:
                for name in ("read", "write", "step"):
                    stack.enter_context(patch.object(runtime.records.Tape, name, wrap(getattr(runtime.records.Tape, name))))
                initial = raw_meter()
                for _ in sys.modules["cardinality"].radix_power(ring, q):
                    width.increment()
                require(operations == raw_meter() - initial, "wide radix physical meter")
            b = (q**exponent).bit_length() + 1
            require(count_value(width)[0] == exponent, "encoded native width")
            require(operations <= 2200 * (b + 1) ** 3, "source-derived cubic radix envelope")
            require((b + 1) ** 3 <= 8 * q ** (2 * exponent), "radix-to-payload inequality")
            require(bank.live == {modulus.slot, ring.one.slot}, "radix temporaries restored")
            rows.append(dict(radix=str(q), exponent=exponent, word_bits=b, traffic=operations))
        finally:
            ring.close()
            bank.free(modulus)
            bank.erase_owned()
            maximum.close()
            width.close()
    return rows


def controls(prefix, invoice, runtime, rows):
    names = []
    changed = run_case(prefix, invoice, runtime, CASES[3], "adapter_read")
    require(changed["total"] == rows[3]["total"] + rows[3]["counts"]["native_calls"], "extra adapter reads observed")
    require(changed["native"] == rows[3]["native"], "native interval remains distinct")
    try:
        check_receipt(changed, rows[3])
    except ValueError:
        names.append("endpoint_preserving_adapter_traffic")
    else:
        raise ValueError("extra adapter traffic escaped receipt")
    try:
        run_case(prefix, invoice, runtime, CASES[3], "coefficient")
    except ValueError as exc:
        require(str(exc) == "affine endpoint", "coefficient control failed at intended endpoint")
        names.append("wrong_coefficient_full_payload")
    else:
        raise ValueError("wrong coefficient escaped endpoint")
    row = rows[3]
    dropped = [dict(item, traffic=item["overhead"]) for item in row["adapters"]]
    try:
        check_partition(row["total"], row["wrapper"], row["setup"], dropped, row["kernels"])
    except ValueError:
        names.append("omitted_native_charge")
    else:
        raise ValueError("native toll omission accepted")
    incorrect = dict(row["counts"], native_calls=row["counts"]["reversed_add"])
    try:
        check_native_count(len(row["adapters"]), 1, incorrect)
    except ValueError:
        names.append("reversed_swap_multiplicity")
    else:
        raise ValueError("single-swap reversed-ADD invoice accepted")
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    bad = [dict(row) for row in pins]
    next(row for row in bad if row["usage"] == "input")["sha256"] = "0" * 64
    try:
        authenticate(bad)
    except ValueError as exc:
        require(str(exc).startswith("source hash:"), "source control failure site")
        names.append("source_corruption_before_load")
    else:
        raise ValueError("source corruption accepted")
    altered = dict(rows[0], bits=float(rows[0]["bits"]))
    try:
        check_receipt(altered, rows[0])
    except ValueError:
        names.append("receipt_numeric_type")
    else:
        raise ValueError("receipt type mutation accepted")
    return names


def result():
    prefix, invoice, runtime = load()
    rows = [run_case(prefix, invoice, runtime, parameters) for parameters in CASES]
    kinds = {op[0] for row in rows for op in row["compiled"]}
    require(kinds == {"add", "swap", "double", "half", "negate", "translate"}, "all six compiled kinds")
    shifts = [op[-1] for row in rows for op in row["compiled"] if op[0] == "translate"]
    require(min(shifts) == -4 and max(shifts) >= 3, "extreme carry controls")
    return dict(status="PASS_HIGH_CUBE_PAID_COMPOSITION", cases=len(rows), bits=sum(row["bits"] for row in rows),
                native_calls=sum(len(row["adapters"]) for row in rows),
                controls=controls(prefix, invoice, runtime, rows), radix_checks=radix_checks(runtime), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        check_receipt(actual, json.loads((PACKAGE / "RESULT.json").read_bytes()))
        print(actual["status"], "cases=" + str(actual["cases"]), "bits=" + str(actual["bits"]),
              "native_calls=" + str(actual["native_calls"]), "controls=" + str(len(actual["controls"])))


if __name__ == "__main__":
    main()
