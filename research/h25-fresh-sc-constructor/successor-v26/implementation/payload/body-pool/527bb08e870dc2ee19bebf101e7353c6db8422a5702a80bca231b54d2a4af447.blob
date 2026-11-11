"""Bounded finite controls for the P3 one-record encoder.

The parent imports and runs this in the serial guarded queue, after compiling
and loading the extension. No build, timing, files, network, or orchestration is
performed here. All checks use exceptions and remain active under python -O.
"""
import hashlib
import json
import sys
from types import ModuleType

from trace_adapter import make_trace_type


def _need(condition, message):
    if not condition:
        raise RuntimeError(message)


class _CaptureHash:
    def __init__(self, failure=None):
        self.digest = hashlib.sha256()
        self.chunks = []
        self.failure = failure

    def update(self, data):
        _need(type(data) is bytes, "Trace update did not receive exact bytes")
        if self.failure == "before":
            raise ValueError("injected hash failure before update")
        self.digest.update(data)
        self.chunks.append(data)
        if self.failure == "after":
            raise ValueError("injected hash failure after update")

    def copy(self):
        return self.digest.copy()

    def hexdigest(self):
        return self.digest.hexdigest()


class _IntSubclass(int):
    pass


class _TupleSubclass(tuple):
    pass


class _ListSubclass(list):
    pass


def _capture(function):
    try:
        value = function()
    except Exception as error:
        return ("error", type(error), str(error))
    return ("return", type(value), value)


def _state(trace):
    # Exact field types are part of the comparison: bool must not equal int by
    # accident. Counter fixtures use ordinary strings/ints only.
    return (type(trace.count), trace.count, type(trace.bytes), trace.bytes,
            trace.hasher.hexdigest(), trace.hasher.copy().hexdigest(),
            tuple(trace.hasher.chunks), trace.receipt())


def _literal(call, inputs, output):
    us, vs = inputs
    if output is None:
        result = {"type": "None"}
    else:
        result = {"type": "list", "values": output}
    record = {"call": call, "us": us, "vs": vs, "result": result}
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"


def _admitted(call, us, vs, output):
    def unsigned(value):
        return type(value) is int and 0 <= value <= (1 << 64) - 1
    return (unsigned(call) and type(us) is tuple and type(vs) is tuple and
            len(us) <= 64 and len(vs) <= 64 and
            all(unsigned(value) for value in us) and
            all(unsigned(value) for value in vs) and
            (output is None or
             (type(output) is list and len(output) <= 64 and
              all(unsigned(value) for value in output))))


def run_controls(backend, native_encoder_module):
    """Return a JSON-safe receipt; never compile or invoke the full caller.

    Native entry replacement *before arithmetic* is an additional parent-owned
    integration control because this standalone factory has no RuntimeGuard.
    """
    reference_type = backend.ComplementTrace
    candidate_type = make_trace_type(backend, native_encoder_module)
    encoder = native_encoder_module.encode_record
    _need(candidate_type.before is reference_type.before and
          candidate_type.receipt is reference_type.receipt,
          "Adapter replaced an original observation boundary")
    _need(candidate_type._h25_native_entries ==
          ((native_encoder_module, "encode_record", encoder),),
          "Adapter does not expose the exact native ownership triple")
    _need(backend.ComplementTrace is reference_type,
          "Trace factory changed the reference backend")
    module = backend.load_source("_h25_trace_control_source")
    label = module.Label
    counts = {"byte_and_prefix_pairs": 0, "native_admitted": 0,
              "native_fallback": 0, "error_pairs": 0,
              "before_pairs": 0, "native_argument_errors": 0,
              "no_alias_checks": 0, "digit_limit_pairs": 0,
              "source_module_loads": 1, "factory_rejections": 0}
    ledger = hashlib.sha256()

    # Factory admission does not bless a proxy, a Python replacement, or a
    # native function belonging to another module. Live drift after binding
    # remains the separate parent-owned pre-arithmetic guard obligation.
    wrong_owner = ModuleType("_h25_wrong_trace_owner")
    wrong_owner.encode_record = encoder
    for invalid_owner in (object(), wrong_owner):
        outcome = _capture(lambda invalid_owner=invalid_owner:
                           make_trace_type(backend, invalid_owner))
        _need(outcome[0] == "error" and outcome[1] is RuntimeError,
              "Trace factory accepted an invalid native owner")
        counts["factory_rejections"] += 1
    try:
        native_encoder_module.encode_record = lambda *args: b"replacement"
        outcome = _capture(lambda: make_trace_type(backend, native_encoder_module))
        _need(outcome[0] == "error" and outcome[1] is RuntimeError,
              "Trace factory accepted a replaced native entry")
        counts["factory_rejections"] += 1
    finally:
        native_encoder_module.encode_record = encoder

    def pair(failure=None):
        oracle = reference_type(label)
        candidate = candidate_type(label)
        oracle.hasher = _CaptureHash(failure)
        candidate.hasher = _CaptureHash(failure)
        return oracle, candidate

    def compare_after(oracle, candidate, inputs, output, expected_error=None):
        expected = _capture(lambda: oracle.after(inputs, output))
        actual = _capture(lambda: candidate.after(inputs, output))
        _need(actual == expected, "Trace exception/return contract differs")
        _need(_state(candidate) == _state(oracle),
              "Trace prefix, bytes, count, exact types or receipt differs")
        if expected_error is None:
            _need(expected == ("return", type(None), None),
                  "An expected successful trace case failed")
        else:
            _need(expected[0] == "error" and expected[1] is expected_error,
                  "Trace fixture did not fail with the expected exact exception")
            counts["error_pairs"] += 1
        counts["byte_and_prefix_pairs"] += 1
        ledger.update(expected[0].encode("ascii") + b":" +
                      expected[1].__name__.encode("ascii") + b"\n")
        if expected[0] == "error":
            ledger.update(expected[2].encode("utf-8") + b"\n")
        ledger.update(oracle.hasher.copy().digest())

    def record(oracle, candidate, inputs, output):
        us, vs = inputs
        call = oracle.count
        literal = _literal(call, inputs, output)
        native = encoder(call, us, vs, output)
        if _admitted(call, us, vs, output):
            _need(type(native) is bytes and native == literal,
                  "Native record bytes differ from literal sorted ASCII JSON")
            counts["native_admitted"] += 1
        else:
            _need(native is NotImplemented,
                  "Native encoder admitted an unsupported exact domain")
            counts["native_fallback"] += 1
        compare_after(oracle, candidate, inputs, output)
        _need(oracle.hasher.chunks[-1] == literal and
              candidate.hasher.chunks[-1] == literal,
              "Adapter lost exact canonical bytes or final LF")
        ledger.update(literal)

    # This stream compares every completed prefix, not just the final digest.
    maximum = (1 << 64) - 1
    fixtures = [
        (((), ()), []),
        (((), ()), None),
        (((0,), (0, 1, 2)), [0, 1, 2]),
        (((1, 2), (1, 2, 4)), [4]),
        (((2, 1), (1, 2, 4)), [4]),
        (((1,), (4, 2, 1)), [2, 4]),
        (((1,), (4, 2, 1)), [4, 2]),
        (((9, 10, 99, 100, 999, 1000), (maximum,)), [maximum, 0]),
        (((maximum,) * 64, (maximum,) * 64), [maximum] * 64),
        (((0,) * 65, ()), []),
        (((), (0,) * 65), []),
        (((), ()), [0] * 65),
        (((-1,), (0,)), [-2]),
        (((1 << 64,), (1 << 100,)), [1 << 100]),
        (((True,), ()), []),
        (((_IntSubclass(7),), ()), []),
        ((_TupleSubclass((1, 2)), (1, 2, 4)), [4]),
        (([1, 2], (1, 2, 4)), [4]),
        (("lambda: \u03bb", ()), None),
        (({"z": 2, "a": 1}, ()), []),
    ]
    oracle, candidate = pair()
    for inputs, output in fixtures:
        record(oracle, candidate, inputs, output)
    stream_receipt = oracle.receipt()

    # Count itself is serialized, and unsupported count types must use JSON.
    for count in (0, 9, 10, 99, 100, maximum, 1 << 64, -1, True, 1.5, _IntSubclass(3)):
        left, right = pair()
        left.count = right.count = count
        record(left, right, ((1,), (1, 2)), [2])
    left, right = pair()
    left.count = right.count = maximum
    record(left, right, ((maximum,) * 64, (maximum,) * 64), [maximum] * 64)
    _need(len(left.hasher.chunks[0]) == 4112,
          "Maximum admitted record does not match the checked buffer bound")

    # Native direct-call admission has no user-defined conversion callbacks.
    callbacks = []
    class IndexOnly:
        def __index__(self):
            callbacks.append("index")
            return 3
    index_only = IndexOnly()
    direct_unsupported = [
        (index_only, (), (), []), (0, (index_only,), (), []),
        (0, (), (index_only,), []), (0, (), (), [index_only]),
        (0, (), (), _ListSubclass([1])), (0, (), (), (1,)),
        (0, (), (), [True]), (0, (), (), [_IntSubclass(1)]),
        (0, (), (), object()),
    ]
    for args in direct_unsupported:
        _need(encoder(*args) is NotImplemented,
              "Native unsupported-input sentinel changed")
        # A valid call after each rejection detects an uncleared error flag.
        _need(encoder(0, (), (), []) == _literal(0, ((), ()), []),
              "Native fallback left stale error state")
        counts["native_fallback"] += 1
    _need(callbacks == [], "Native admission invoked a custom integer callback")
    for arguments in ((), (0,), (0, (), ()), (0, (), (), [], None)):
        outcome = _capture(lambda arguments=arguments: encoder(*arguments))
        _need(outcome[0] == "error" and outcome[1] is TypeError,
              "Native FASTCALL arity error changed")
        counts["native_argument_errors"] += 1
    outcome = _capture(lambda: encoder(call=0, us=(), vs=(), output=[]))
    _need(outcome[0] == "error" and outcome[1] is TypeError,
          "Native FASTCALL unexpectedly admitted keyword arguments")
    counts["native_argument_errors"] += 1

    # Existing after validation must win before any encoding or hash update.
    invalid_outputs = [(1,), _ListSubclass([1]), [True], [_IntSubclass(1)],
                       [index_only], 3, NotImplemented]
    for output in invalid_outputs:
        left, right = pair()
        compare_after(left, right, ((), ()), output, RuntimeError)
        _need(left.count == 0 and left.bytes == 0 and left.hasher.chunks == [],
              "Invalid output changed the observation prefix")
    for inputs, error_type in ((7, TypeError), (((),), ValueError),
                               (((), (), ()), ValueError)):
        left, right = pair()
        compare_after(left, right, inputs, [], error_type)
    left, right = pair()
    compare_after(left, right, ((index_only,), ()), [], TypeError)
    _need(callbacks == [], "JSON fallback invoked a custom integer callback")

    # Original input unpacking can run a callback. Each implementation must
    # consume it once before encoding and preserve that event order.
    unpack_events = []
    class PairInput:
        def __iter__(self):
            unpack_events.append("unpack")
            yield (1,)
            yield (1, 2)
    left, right = pair()
    compare_after(left, right, PairInput(), [2])
    _need(unpack_events == ["unpack", "unpack"],
          "Trace changed input-unpacking callback multiplicity")

    # Preserve failures before hash mutation, after hash mutation, and after a
    # successful hash but before/between the original counter assignments.
    for failure in ("before", "after"):
        left, right = pair(failure)
        compare_after(left, right, ((1,), (1, 2)), [2], ValueError)
        _need(left.count == 0 and left.bytes == 0,
              "Hash failure advanced the public counters")
        _need(bool(left.hasher.chunks) is (failure == "after"),
              "Hash failure test did not exercise its declared boundary")
    left, right = pair()
    left.bytes = right.bytes = "bad byte counter"
    compare_after(left, right, ((1,), (1, 2)), [2], TypeError)
    _need(left.count == 0 and len(left.hasher.chunks) == 1,
          "Byte-counter failure did not preserve the post-hash boundary")
    left, right = pair()
    left.count = right.count = "bad call counter"
    compare_after(left, right, ((1,), (1, 2)), [2], TypeError)
    _need(left.bytes == len(left.hasher.chunks[0]) and
          left.count == "bad call counter",
          "Call-counter failure did not follow the byte-counter increment")

    # Unsupported wide integers still reach ordinary decimal digit limits.
    # Restore the process setting on success or any control failure.
    original_limit = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        left, right = pair()
        record(left, right, ((10 ** 639,), ()), [])
        counts["digit_limit_pairs"] += 1
        for inputs, output in (
            (((10 ** 640,), ()), []),
            (((-(10 ** 640),), ()), []),
            (((), ()), [10 ** 640]),
        ):
            left, right = pair()
            _need(encoder(0, inputs[0], inputs[1], output) is NotImplemented,
                  "Wide decimal integer escaped JSON fallback")
            compare_after(left, right, inputs, output, ValueError)
            _need(left.count == 0 and left.bytes == 0 and left.hasher.chunks == [],
                  "Decimal-limit failure changed the prefix")
            counts["native_fallback"] += 1
            counts["digit_limit_pairs"] += 1
        sys.set_int_max_str_digits(0)
        left, right = pair()
        record(left, right, ((10 ** 700, -(10 ** 700)), ()), [10 ** 700])
        counts["digit_limit_pairs"] += 1
    finally:
        sys.set_int_max_str_digits(original_limit)

    def raw(values, basis_type=dict):
        value = object.__new__(label)
        value.basis = basis_type(enumerate(values))
        return value

    # Both before methods take private ordered snapshots before later writes.
    left, right = pair()
    small, big = raw((4, 1)), raw((4, 2, 1))
    left_inputs = left.before(small, big)
    right_inputs = right.before(small, big)
    _need(left_inputs == right_inputs == ((4, 1), (4, 2, 1)) and
          type(right_inputs) is tuple and all(type(row) is tuple for row in right_inputs),
          "Before lost exact ordered snapshot tuples")
    small.basis.clear()
    big.basis[0] = 999
    big.basis[3] = 8
    _need(left_inputs == right_inputs == ((4, 1), (4, 2, 1)),
          "Before snapshot aliases a mutable basis")
    compare_after(left, right, right_inputs, [2])
    counts["before_pairs"] += 1
    shared = raw((2, 1))
    _need(left.before(shared, shared) == right.before(shared, shared) == ((2, 1), (2, 1)),
          "Before changed aliased-label snapshot order")
    counts["before_pairs"] += 1
    basis_events = []
    class SideEffectDict(dict):
        def values(self):
            basis_events.append("values")
            return super().values()
    class ChildLabel(label):
        pass
    child = object.__new__(ChildLabel)
    child.basis = {0: 1}
    missing = object.__new__(label)
    bad_before = [object(), child, missing, raw((1,), SideEffectDict), raw((True,))]
    for invalid in bad_before:
        left, right = pair()
        good = raw((1, 2))
        expected = _capture(lambda: left.before(invalid, good))
        actual = _capture(lambda: right.before(invalid, good))
        _need(actual == expected and expected[0] == "error" and
              expected[1] is RuntimeError and _state(left) == _state(right),
              "Before rejection semantics changed")
        counts["before_pairs"] += 1
    _need(basis_events == [], "Before invoked unsupported basis.values")

    # Success must retain no caller vectors or output aliases. Bytes are owned
    # immutable copies, so later mutation cannot alter an observed prefix.
    left, right = pair()
    us, vs, output = (1, 3), (1, 2, 4), [2, 4]
    inputs = (us, vs)
    before_refs = (sys.getrefcount(us), sys.getrefcount(vs), sys.getrefcount(output))
    record(left, right, inputs, output)
    _need((sys.getrefcount(us), sys.getrefcount(vs), sys.getrefcount(output)) == before_refs,
          "Trace encoder retained a caller vector or output reference")
    before_prefix = _state(right)
    output[:] = [999]
    _need(_state(right) == before_prefix and _state(left) == before_prefix,
          "Observed bytes retain a mutable output alias")
    counts["no_alias_checks"] += 2

    return {
        "status": "TRACE_ENCODING_FINITE_CONTROLS_PASS",
        "counts": counts,
        "fixture_sha256": ledger.hexdigest(),
        "ordered_fixture_stream": stream_receipt,
        "native_interface": "encode_record(call,us,vs,output): exact bytes with LF or NotImplemented",
        "comparison": "Original ComplementTrace, literal sorted ASCII JSON, exact per-record bytes, every prefix and exception/counter state",
        "native_entry_freshness": "Parent integration must additionally reject native owner/entry replacement before arithmetic at every original live guard boundary",
        "timing_claim": None,
    }
