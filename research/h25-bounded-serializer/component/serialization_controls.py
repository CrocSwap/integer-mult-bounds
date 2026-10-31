"""Parent-executed bounded controls; imports no scientific module itself."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType

import bounded_serialization as candidate


_NAMES = ("result.json", "witness.json", "rank-trace.json")


def _need(value, message):
    if not value:
        raise RuntimeError(message)


def _fixture():
    return ({"ok": True, "number": 3}, {
        "support": [0, 1, 3], "args": [None, (0, 1)], "kind": [None, "in"],
        "active": [1, 2], "pieces": [((0, 1, 2), 2, (1, 2))],
        "labels": [(1, [(2, 3), (0, 1)], 2, (1, 3))],
        "code": {"roles": 3, "gates": [(1, (0,), (1, 2))],
                 "sources": [((2, 1, 0), 1), ((0, 1, 2), 2)], "outputs": [(1, 2), (0, 1)]},
    }, [((1, 2), 2), ((1, 2), 1), ((2,), 1)], [])


def _outcome(function):
    try:
        return ("return", function())
    except BaseException as error:
        return ("error", type(error).__name__, str(error))


def _original_writer(comparison, expected):
    namespace = dict(comparison.write_scientific.__globals__)
    namespace["EXPECTED"] = expected
    # Same original code, separate globals; the imported comparison is untouched.
    return FunctionType(comparison.write_scientific.__code__, namespace,
                        comparison.write_scientific.__name__,
                        comparison.write_scientific.__defaults__,
                        comparison.write_scientific.__closure__)


def _expected(comparison, fixture):
    result, witness, ranks, _ = fixture
    return {
        "result_sha256": hashlib.sha256(comparison.canonical(result)).hexdigest(),
        "exact_witness_sha256": hashlib.sha256(comparison.canonical(witness)).hexdigest(),
        "rank_trace_sha256": hashlib.sha256(comparison.canonical(ranks)).hexdigest(),
        "rank_call_count": len(ranks),
        "rank_distinct_matrix_count": len({rows for rows, _ in ranks}),
    }


def _finals(path):
    return {name: (path / name).read_bytes() for name in _NAMES if (path / name).is_file()}


def run_controls(comparison, output_root):
    """Run once in a new external directory under the parent's guard.

    comparison supplies the unchanged write_scientific/canonical/require.
    No full caller, native build, scientific import or timer is started here.
    """
    root = Path(output_root)
    _need(not root.exists(), "Refusing existing serializer control evidence")
    root.mkdir(parents=True)
    rows = []
    original_source = comparison.write_scientific.__code__
    total_cap = 16777216
    base_expected = _expected(comparison, _fixture())

    def equal(name, factory=_fixture, *, limits=None, expected_override=None, admitted=None):
        before = factory()
        after = factory()
        _need(before[1] is not after[1] and before[2] is not after[2], "Shared control inputs")
        try:
            expected = _expected(comparison, factory())
        except BaseException:
            expected = dict(base_expected)
        if expected_override is not None:
            expected_override(expected)
        original = _original_writer(comparison, expected)
        writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require,
                                       **(limits or {}))
        case = root / name
        left, right = case / "original", case / "candidate"
        left.mkdir(parents=True)
        right.mkdir()
        old = _outcome(lambda: original(left, *before[:3]))
        new = _outcome(lambda: writer(right, *after[:3]))
        _need(old == new, "Serializer outcome differs: " + name + " " + repr((old, new)))
        _need(before[3] == after[3], "Callback count/order differs: " + name)
        _need(_finals(left) == _finals(right), "Final artifact bytes differ: " + name)
        if admitted is not None:
            expected_status = "LITERAL_REFERENCE_FALLBACK" if not admitted else (
                "BOUNDED_SERIALIZATION_PASS" if new[0] == "return" else "FAILED_EVIDENCE_RETAINED")
            _need(writer.last_operation["status"] == expected_status, "Admission differs: " + name)
        if new[0] == "return" and writer.last_operation["status"] == "BOUNDED_SERIALIZATION_PASS":
            _need(not tuple(right.glob(".serialization-*")), "Successful staging leaked")
            for record in writer.last_operation["files"].values():
                _need(record["sha256"] == record["copy_sha256"] and
                      record["hashed_bytes"] == record["accepted_write_bytes"] ==
                      record["copy_read_bytes"] == record["copy_write_bytes"],
                      "Copy verification/cost count differs")
        rows.append({"case": name, "outcome": new[0], "operation": writer.last_operation})

    equal("ordinary", admitted=True)

    def empty():
        result, witness, ranks, events = _fixture()
        for key in witness:
            if key == "code":
                witness[key] = {"gates": [], "outputs": [], "roles": 0, "sources": []}
            else:
                witness[key] = []
        return result, witness, [], events
    equal("empty", empty, admitted=True)

    for length in (1, 1023, 1024, 1025, 2048):
        def length_case(length=length):
            result, witness, ranks, events = _fixture()
            witness["support"] = list(range(length))
            return result, witness, ranks, events
        equal("rows-" + str(length), length_case, admitted=True)

    for length, expected_admitted in ((169, True), (170, True), (171, False)):
        def size_case(length=length):
            result, witness, ranks, events = _fixture()
            witness["kind"] = ["a" * length, "z"]
            return result, witness, ranks, events
        equal("byte-bound-" + str(length), size_case,
              limits={"batch_bytes": 2045, "batch_rows": 3, "copy_bytes": 127},
              admitted=expected_admitted)

    def scalar_case():
        result, witness, ranks, events = _fixture()
        witness["kind"] = [None, True, False, 0.0, -0.0, 1.25, float("inf"),
                           -float("inf"), float("nan"), '\\"\b\f\n\r\t\x00',
                           "\u1234\U0001f642\ud800\udfff"]
        witness["support"] = [0, -1, (1 << 53) - 1, 1 << 53, (1 << 64) - 1,
                              1 << 64, -(1 << 64), 1 << 2300]
        return result, witness, ranks, events
    equal("scalars-unicode-wide", scalar_case, admitted=True)

    def huge():
        result, witness, ranks, events = _fixture()
        witness["support"] = [1 << 20000, -(1 << 20000)]
        return result, witness, ranks, events
    old_digits = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(0)
        equal("wide-unlimited", huge, admitted=True)
        sys.set_int_max_str_digits(640)
        equal("wide-digit-error", huge, admitted=True)
    finally:
        sys.set_int_max_str_digits(old_digits)

    def interned():
        result, witness, _, events = _fixture()
        row = (1, 2, 3)
        return result, witness, [(row, 2), (row, 1), (tuple([1, 2, 3]), 2)], events
    equal("interned-rank-rows", interned, admitted=True)

    for depth in (30, 33):
        def nested(depth=depth):
            result, witness, ranks, events = _fixture()
            value = 1
            for _ in range(depth):
                value = [value]
            witness["kind"] = [value]
            return result, witness, ranks, events
        equal("depth-" + str(depth), nested, admitted=depth == 30)

    def circular():
        result, witness, ranks, events = _fixture()
        cycle = []
        cycle.append(cycle)
        witness["kind"] = [cycle]
        return result, witness, ranks, events
    equal("circular", circular, admitted=False)

    def callback_list():
        result, witness, ranks, events = _fixture()
        class Observed(list):
            def __iter__(self):
                events.append("list-iter")
                return super().__iter__()
        witness["kind"] = Observed(["in", "x"])
        return result, witness, ranks, events
    equal("callback-list", callback_list, admitted=False)

    def callback_dict():
        result, witness, ranks, events = _fixture()
        class Observed(dict):
            def items(self):
                events.append("dict-items")
                return super().items()
        result = Observed(result)
        return result, witness, ranks, events
    equal("callback-dict", callback_dict, admitted=False)

    def callback_raising():
        result, witness, ranks, events = _fixture()
        class Observed(dict):
            def items(self):
                events.append("raising-items")
                raise LookupError("observed conversion failure")
        witness["kind"] = [Observed({"x": 1})]
        return result, witness, ranks, events
    equal("callback-error", callback_raising, admitted=False)

    def subclass_int():
        result, witness, ranks, events = _fixture()
        class Observed(int):
            def __repr__(self):
                events.append("int-repr")
                return "7"
        witness["support"] = [Observed(7)]
        return result, witness, ranks, events
    equal("int-subclass", subclass_int, admitted=False)

    def unknown():
        result, witness, ranks, events = _fixture()
        class Unknown:
            pass
        witness["kind"] = [Unknown()]
        return result, witness, ranks, events
    equal("unsupported-object", unknown, admitted=False)

    for location in ("result", "witness", "rank"):
        def malformed(location=location):
            result, witness, ranks, events = _fixture()
            if location == "result":
                result = {1: 1, "x": 2}
            elif location == "witness":
                witness["kind"] = [set([1])]
            else:
                ranks = [([1], 1)]
            return result, witness, ranks, events
        equal("malformed-" + location, malformed, admitted=False)

    def nonstring_keys():
        result, witness, ranks, events = _fixture()
        result = {2: "b", 1: "a"}
        return result, witness, ranks, events
    equal("nonstring-supported-keys", nonstring_keys, admitted=False)

    for key in ("result_sha256", "exact_witness_sha256", "rank_trace_sha256",
                "rank_call_count", "rank_distinct_matrix_count"):
        def alter(expected, key=key):
            expected[key] = "0" * 64 if type(expected[key]) is str else expected[key] + 1
        equal("expected-" + key, expected_override=alter, admitted=True)

    def fault_case(name, fault, expected_error, *, final_names=(), missing_final_names=(),
                   manifest_may_fail=False):
        fixture = _fixture()
        expected = _expected(comparison, _fixture())
        original = _original_writer(comparison, expected)
        writer = candidate._make_writer(original, comparison.canonical, expected, comparison.require,
                                        batch_bytes=2048, batch_rows=3, copy_bytes=31, fault=fault)
        output = root / name
        output.mkdir()
        outcome = _outcome(lambda: writer(output, *fixture[:3]))
        _need(outcome[0] == "error" and outcome[1] == expected_error,
              "Fault did not surface: " + name + " " + repr(outcome))
        _need(writer.last_operation["status"] == "FAILED_EVIDENCE_RETAINED", "Fault hidden")
        for filename in final_names:
            _need((output / filename).exists(), "Earlier/failing final disappeared: " + name)
        for filename in missing_final_names:
            _need(not (output / filename).exists(), "Later/unaccepted final appeared: " + name)
        if writer.last_operation["stage"] is not None:
            stage = Path(writer.last_operation["stage"])
            _need(stage.is_dir(), "Failed staging evidence deleted")
            if not manifest_may_fail:
                _need((stage / "failure.json").is_file(), "Failure manifest missing")
        rows.append({"case": name, "outcome": outcome, "operation": writer.last_operation})
        return writer.last_operation

    def raising(event_name, filename=None, error_type=OSError, text="injected IO failure"):
        def fault(event, information):
            path = information.get("path")
            if event == event_name and (filename is None or (path is not None and path.name == filename)):
                raise error_type(text)
            return NotImplemented
        return fault

    for event in ("stage_create", "stage_open", "stage_write", "stage_flush", "stage_after_close", "stage_hash"):
        fault_case("failure-" + event, raising(event), "OSError", missing_final_names=_NAMES)

    for filename in _NAMES:
        index = _NAMES.index(filename)
        for event in ("final_open", "final_write", "final_flush", "final_after_close"):
            present = _NAMES[:index] if event == "final_open" else _NAMES[:index + 1]
            fault_case("failure-" + event + "-" + filename, raising(event, filename), "OSError",
                       final_names=present, missing_final_names=_NAMES[index + 1:])

    for length in (0, 1):
        def short(event, information, length=length):
            if event == "final_write" and information["path"].name == "witness.json":
                information["stream"].write(information["data"][:length])
                return length
            return NotImplemented
        fault_case("short-final-" + str(length), short, "OSError",
                   final_names=_NAMES[:2], missing_final_names=_NAMES[2:])

    def corrupt(event, information):
        if event == "copy_read" and information["path"].name == "witness.json":
            raw = information["stream"].read(31)
            if raw:
                return bytes([raw[0] ^ 1]) + raw[1:]
            return raw
        return NotImplemented
    fault_case("copy-corrupt-content", corrupt, "RuntimeError",
               final_names=_NAMES[:2], missing_final_names=_NAMES[2:])

    def mutate_stage(event, information):
        if event == "after_acceptance":
            with (information["stage"] / "witness.json").open("ab") as stream:
                stream.write(b" ")
        return NotImplemented
    fault_case("stage-mutated-size", mutate_stage, "RuntimeError",
               final_names=_NAMES[:1], missing_final_names=_NAMES[1:])
    fault_case("copy-read-error", raising("copy_read", "witness.json"), "OSError",
               final_names=_NAMES[:2], missing_final_names=_NAMES[2:])
    fault_case("copy-hash-error", raising("copy_hash", "witness.json"), "OSError",
               final_names=_NAMES[:2], missing_final_names=_NAMES[2:])
    fault_case("cleanup-unlink-error", raising("cleanup_unlink", "witness.json"), "OSError",
               final_names=_NAMES)
    fault_case("cleanup-rmdir-error", raising("cleanup_rmdir"), "OSError", final_names=_NAMES)

    def dual_error(event, information):
        if event == "stage_write":
            raise ValueError("primary write failure")
        if event == "stage_after_close":
            raise OSError("secondary close failure")
        return NotImplemented
    evidence = fault_case("primary-plus-close-error", dual_error, "ValueError", missing_final_names=_NAMES)
    _need(evidence["error"]["message"] == "primary write failure" and evidence.get("close_errors"),
          "Close failure masked primary error")

    def manifest_error(event, information):
        if event == "stage_write":
            raise ValueError("primary write failure")
        if event == "failure_manifest":
            raise OSError("secondary manifest failure")
        return NotImplemented
    evidence = fault_case("primary-plus-manifest-error", manifest_error, "ValueError",
                          missing_final_names=_NAMES, manifest_may_fail=True)
    _need(evidence["failure_manifest_error_type"] == "OSError", "Manifest failure hidden")

    for name in ("reference_global", "json_default", "expected_value"):
        expected = _expected(comparison, _fixture())
        original = _original_writer(comparison, expected)
        writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
        output = root / ("drift-" + name)
        output.mkdir()
        saved_default = json.JSONEncoder.default
        saved_canonical = original.__globals__["canonical"]
        try:
            if name == "reference_global":
                original.__globals__["canonical"] = lambda value: b"wrong"
            elif name == "json_default":
                json.JSONEncoder.default = lambda self, value: "wrong"
            else:
                expected["rank_call_count"] += 1
            outcome = _outcome(lambda: writer(output, *_fixture()[:3]))
        finally:
            json.JSONEncoder.default = saved_default
            original.__globals__["canonical"] = saved_canonical
        _need(outcome[0:2] == ("error", "RuntimeError") and not tuple(output.iterdir()),
              "Source/expected drift reached output")
        rows.append({"case": "drift-" + name, "outcome": outcome})

    # Effective builtin and previously absent global dependencies are part of
    # the source-bound encoder, not merely public callable identities.
    for name in ("effective_builtin", "json_global_shadow", "keyword_default"):
        expected = _expected(comparison, _fixture())
        original = _original_writer(comparison, expected)
        if name == "effective_builtin":
            namespace = dict(original.__globals__)
            namespace["__builtins__"] = dict(original.__builtins__)
            original = FunctionType(original.__code__, namespace, original.__name__)
        writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
        output = root / ("drift-" + name)
        output.mkdir()
        saved_allow_nan = json.JSONEncoder.__init__.__kwdefaults__["allow_nan"]
        _need("str" not in json.encoder.__dict__, "Unexpected JSON str shadow at test entry")
        try:
            if name == "effective_builtin":
                original.__builtins__["len"] = lambda value: 0
            elif name == "json_global_shadow":
                json.encoder.__dict__["str"] = object
            else:
                json.JSONEncoder.__init__.__kwdefaults__["allow_nan"] = False
            outcome = _outcome(lambda: writer(output, *_fixture()[:3]))
        finally:
            json.encoder.__dict__.pop("str", None)
            json.JSONEncoder.__init__.__kwdefaults__["allow_nan"] = saved_allow_nan
        _need(outcome[0:2] == ("error", "RuntimeError") and not tuple(output.iterdir()),
              "Effective JSON dependency drift reached output")
        rows.append({"case": "drift-" + name, "outcome": outcome})

    saved_default = json.JSONEncoder.default
    def late_drift(event, information):
        if event == "final_after_close" and information["path"].name == "rank-trace.json":
            json.JSONEncoder.default = lambda self, value: "drift"
        return NotImplemented
    try:
        fault_case("exit-json-drift", late_drift, "RuntimeError", final_names=_NAMES)
    finally:
        json.JSONEncoder.default = saved_default

    expected = _expected(comparison, _fixture())
    original = _original_writer(comparison, expected)
    writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
    output = root / "fallback-exit-json-drift"
    output.mkdir()
    result, witness, ranks, events = _fixture()
    class MutatingDict(dict):
        def items(self):
            events.append("dict-items")
            json.JSONEncoder.default = lambda self, value: "drift"
            return super().items()
    try:
        outcome = _outcome(lambda: writer(output, MutatingDict(result), witness, ranks))
    finally:
        json.JSONEncoder.default = saved_default
    _need(outcome[0:2] == ("error", "RuntimeError") and
          writer.last_operation["status"] == "FALLBACK_EXIT_FRESHNESS_FAILED" and
          all((output / name).is_file() for name in _NAMES),
          "Fallback runtime drift escaped successful-exit guard")
    rows.append({"case": "fallback-exit-json-drift", "outcome": outcome})

    # Preserve direct-call overwrite behavior, separately from parent run-dir guard.
    expected = _expected(comparison, _fixture())
    original = _original_writer(comparison, expected)
    writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
    output = root / "existing-finals"
    output.mkdir()
    for name in _NAMES:
        (output / name).write_bytes(b"previous bytes")
    writer(output, *_fixture()[:3])
    old = root / "existing-finals-reference"
    old.mkdir()
    original(old, *_fixture()[:3])
    _need(_finals(old) == _finals(output), "Direct wb overwrite changed")
    rows.append({"case": "existing-finals", "outcome": "return"})

    # One writer invocation cannot populate a reusable data/PASS cache.
    state_fixture = _fixture()
    snapshot = copy.deepcopy(state_fixture[:3])
    expected = _expected(comparison, _fixture())
    original = _original_writer(comparison, expected)
    writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
    first = root / "state-first"
    first.mkdir()
    writer(first, *state_fixture[:3])
    _need(state_fixture[:3] == snapshot, "Serializer mutated input objects")
    state_fixture[1]["support"].append(99)
    second = root / "state-changed"
    second.mkdir()
    outcome = _outcome(lambda: writer(second, *state_fixture[:3]))
    _need(outcome[0:2] == ("error", "RuntimeError") and not _finals(second),
          "Changed input reused a stale serializer PASS")
    rows.append({"case": "state-mutation-between-writes", "outcome": outcome})

    # Unsupported Path subclass delegates before any candidate path operation.
    path_events = []
    class ObservedPath(type(root)):
        def __truediv__(self, other):
            path_events.append(str(other))
            return super().__truediv__(other)
    expected = _expected(comparison, _fixture())
    original = _original_writer(comparison, expected)
    writer = candidate.make_writer(original, comparison.canonical, expected, comparison.require)
    left = root / "path-original"
    right = root / "path-candidate"
    left.mkdir()
    right.mkdir()
    original(ObservedPath(left), *_fixture()[:3])
    original_events = list(path_events)
    path_events.clear()
    writer(ObservedPath(right), *_fixture()[:3])
    _need(path_events == original_events and _finals(left) == _finals(right) and
          writer.last_operation["status"] == "LITERAL_REFERENCE_FALLBACK",
          "Unsupported path callback/fallback changed")
    rows.append({"case": "path-subclass-fallback", "outcome": "return"})

    _need(comparison.write_scientific.__code__ is original_source, "Original writer changed")
    _need(len(rows) <= 128, "Finite serializer case cap exceeded")
    actual_bytes = sum(path.stat().st_size for path in root.rglob("*") if path.is_file())
    _need(actual_bytes <= total_cap, "Finite serializer retained-byte cap exceeded")
    receipt = {"status": "SERIALIZATION_FINITE_PASS", "case_count": len(rows),
               "retained_bytes": actual_bytes, "retained_byte_cap": total_cap,
               "optimization": sys.flags.optimize, "cases": rows,
               "scope": "Finite exact-schema/unsupported/reference/regular-file controls; no full caller or performance claim"}
    (root / "controls.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt
