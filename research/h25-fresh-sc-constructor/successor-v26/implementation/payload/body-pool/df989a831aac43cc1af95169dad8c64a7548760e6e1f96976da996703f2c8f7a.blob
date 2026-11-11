"""Finite independent qualification for the bounded packed GF(2) backend.

The source oracle is a fresh unchanged module. The second oracle uses dense
0/1 lists and addition modulo two; it never calls the native extension or the
source's packed rank, dot, echelon, reduce, or complement routines.
"""
from __future__ import annotations

from collections import UserDict
import builtins
from types import FunctionType
import hashlib
from itertools import permutations, product
import json
import time

from native_backend import ComplementTrace, attach_trace, bind, guard_module, load_source, require


def dense_rank(rows, width):
    work = [list(row) for row in rows]
    require(all(len(row) == width and all(x in (0, 1) for x in row) for row in work),
            "Independent oracle requires dense binary rows")
    rank = 0
    for column in range(width - 1, -1, -1):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(rank + 1, len(work)):
            if work[i][column]:
                work[i] = [(a + b) % 2 for a, b in zip(work[i], work[rank])]
        rank += 1
    return rank


def dense_vectors(vectors, width):
    return [[(value // (2 ** column)) % 2 for column in range(width)] for value in vectors]


def pairing_rows(left, right, width):
    left_dense = dense_vectors(left, width)
    right_dense = dense_vectors(right, width)
    return [[sum(a * b for a, b in zip(x, y)) % 2 for y in right_dense] for x in left_dense]


def independent_complement(small, big, out):
    width = max((x.bit_length() for x in small + big + out), default=0)
    big_dense = dense_vectors(big, width)
    out_dense = dense_vectors(out, width)
    big_rank = dense_rank(big_dense, width)
    pairing = pairing_rows(big, small, width)
    pairing_rank = dense_rank(pairing, len(small))
    require(all(value == 0 for row in pairing_rows(out, small, width) for value in row),
            "Independent oracle found a nonorthogonal complement vector")
    require(dense_rank(big_dense + out_dense, width) == big_rank,
            "Independent oracle found a complement vector outside the ambient span")
    require(len(out) == len(big) - pairing_rank,
            "Independent oracle found a wrong number of coefficient-kernel vectors")
    require(dense_rank(out_dense, width) == big_rank - pairing_rank,
            "Independent oracle found an incomplete complement span")


def raw(label, rows, factory=dict):
    obj = object.__new__(label)
    obj.basis = factory((i, value) for i, value in enumerate(rows))
    return obj


def exact_list(actual, expected):
    require(type(actual) is list and type(expected) is list, "Complement output is not an exact list")
    require(all(type(value) is int for value in actual), "Complement output contains a non-int")
    require(actual == expected, "Ordered complement vectors differ from the unchanged source")


def capture(action):
    try:
        value = action()
    except Exception as error:
        return ("error", type(error).__name__, str(error))
    return ("value", type(value).__name__, value)


class IntSubclass(int):
    pass


class DictSubclass(dict):
    pass


class ValuesOnly:
    def __init__(self, pairs):
        self.rows = tuple(value for _, value in pairs)

    def values(self):
        return iter(self.rows)


class BrokenValues:
    def __init__(self, pairs):
        self.rows = tuple(value for _, value in pairs)

    def values(self):
        def iterator():
            yield from self.rows[:1]
            raise ValueError("frozen broken values iterator")
        return iterator()


def run_controls(native):
    oracle = load_source("_matrix_finite_unchanged_oracle")
    candidate = load_source("_matrix_finite_candidate")
    guard_module(oracle)
    state = bind(candidate, native)
    counts = {"ordered_complements": 0, "gram_cases": 0, "fallback_cases": 0,
              "boundary_cases": 0, "real_label_permutations": 0, "binding_rejections": 0,
              "oracle_negative_controls": 0}
    transcript = hashlib.sha256()

    def record(tag, *values):
        transcript.update(json.dumps((tag, values), separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n")

    def complement_case(small, big):
        reference = oracle.Label.complement_in(raw(oracle.Label, small), raw(oracle.Label, big))
        actual = candidate.Label.complement_in(raw(candidate.Label, small), raw(candidate.Label, big))
        exact_list(actual, reference)
        independent_complement(list(small), list(big), actual)
        record("complement", small, big, actual)
        counts["ordered_complements"] += 1

    def gram_case(vectors):
        reference = oracle.Label.nondegenerate(raw(oracle.Label, vectors))
        actual = candidate.Label.nondegenerate(raw(candidate.Label, vectors))
        width = max((x.bit_length() for x in vectors), default=0)
        dense = pairing_rows(vectors, vectors, width)
        independent = dense_rank(dense, len(vectors)) == len(vectors)
        require(type(actual) is bool and actual is reference and actual is independent,
                "Gram nondegeneracy differs from an independent oracle")
        answer = native.gram_rank(dict(enumerate(vectors)))
        if answer is not NotImplemented:
            rows, rank = answer
            reference_rows = tuple(sum(value * (2 ** j) for j, value in enumerate(row)) for row in dense)
            require(type(rows) is tuple and all(type(row) is int for row in rows), "Native Gram row types changed")
            require(type(rank) is int and rows == reference_rows and rank == dense_rank(dense, len(vectors)),
                    "Native Gram transcript differs from the dense oracle")
        record("gram", vectors, actual)
        counts["gram_cases"] += 1

    # Exhaustive ordered row lists (including zero/dependence), widths <= 3.
    short = [()] + [tuple(row) for n in (1, 2) for row in product(range(8), repeat=n)]
    for small in short:
        for big in short:
            complement_case(small, big)
    for n in range(4):
        for rows in product(range(8), repeat=n):
            gram_case(rows)

    # Cross native word, augmented-width, independent/dependent and permutation
    # boundaries without assuming a machine word bound for the Python fallback.
    coordinates64 = tuple(1 << i for i in range(64))
    boundary_pairs = [
        ((), coordinates64),
        ((1 << 63,), coordinates64[:63]),
        (coordinates64[:63], (1 << 63,)),
        (coordinates64, ()),
        ((1,), coordinates64),                 # augmented 65 -> fallback
        (coordinates64, (1,)),                 # augmented 65 -> fallback
        ((), coordinates64 + (1 << 64,)),      # 65 values -> fallback
        ((1 << 64,), (1, 1 << 64)),            # vector-width fallback
        ((1 << 127,), (1 << 64, 1 << 127)),
        ((1 << 63 | 7,), (3, 5, 1 << 63, 1 << 63 | 7)),
        ((0,) * 32, (0,) * 32),
    ]
    for small, big in boundary_pairs:
        complement_case(small, big)
        gram_case(small)
        gram_case(big)
        counts["boundary_cases"] += 1
    for rows in ((0,), (2 ** 64 - 1,), (1 << 63,), coordinates64,
                 coordinates64 + (1 << 64,), (1 << 200, 3 << 199)):
        gram_case(rows)
        counts["boundary_cases"] += 1

    # Actual Label construction and dictionary insertion order are retained.
    for ordered in permutations((1, 2, 4, 8)):
        small_o, big_o = oracle.Label(ordered[:2]), oracle.Label(ordered)
        small_c, big_c = candidate.Label(ordered[:2]), candidate.Label(ordered)
        require(list(small_c.basis.items()) == list(small_o.basis.items()) and
                list(big_c.basis.items()) == list(big_o.basis.items()) and
                small_c.key == small_o.key and big_c.key == big_o.key,
                "Label constructor or canonical keys changed")
        actual = small_c.complement_in(big_c)
        exact_list(actual, small_o.complement_in(big_o))
        independent_complement(list(small_o.basis.values()), list(big_o.basis.values()), actual)
        record("real_label_order", ordered, actual)
        counts["real_label_permutations"] += 1

    # Unsupported kinds must preserve ordinary return/exception behavior; no
    # coercion, narrowing or mask repair is allowed before calling the fallback.
    fallback_fixtures = [
        ((-1, 2), dict), ((True, False, 2), dict), ((IntSubclass(3), 5), dict),
        ((1 << 100, 3), dict), ((1.5, 2), dict), (("1", 2), dict),
        ((1, 2), DictSubclass), ((1, 2), UserDict), ((1, 2), ValuesOnly),
        ((1, 2), BrokenValues),
    ]
    for values, factory in fallback_fixtures:
        left_o, left_c = raw(oracle.Label, values, factory), raw(candidate.Label, values, factory)
        right_o, right_c = raw(oracle.Label, (1, 2, 4)), raw(candidate.Label, (1, 2, 4))
        expected = capture(lambda: left_o.nondegenerate())
        actual = capture(lambda: left_c.nondegenerate())
        require(actual == expected, "Nondegenerate fallback result/exception changed")
        expected_pair = capture(lambda: left_o.complement_in(right_o))
        actual_pair = capture(lambda: left_c.complement_in(right_c))
        require(actual_pair == expected_pair, "Complement fallback result/exception changed")
        reverse_expected = capture(lambda: right_o.complement_in(left_o))
        reverse_actual = capture(lambda: right_c.complement_in(left_c))
        require(reverse_actual == reverse_expected, "Other-basis fallback result/exception changed")
        record("fallback", factory.__name__, repr(values), actual, actual_pair, reverse_actual)
        counts["fallback_cases"] += 3
    for factory in (lambda cls: object.__new__(cls), lambda cls: raw(cls, (), lambda _: None)):
        left_o, left_c = factory(oracle.Label), factory(candidate.Label)
        require(capture(left_o.nondegenerate) == capture(left_c.nondegenerate), "Missing basis fallback changed")
        right_o, right_c = raw(oracle.Label, (1,)), raw(candidate.Label, (1,))
        require(capture(lambda: left_o.complement_in(right_o)) == capture(lambda: left_c.complement_in(right_c)),
                "Missing self basis exception changed")
        require(capture(lambda: right_o.complement_in(left_o)) == capture(lambda: right_c.complement_in(left_c)),
                "Missing other basis exception changed")
        counts["fallback_cases"] += 3
    class OracleChild(oracle.Label):
        pass
    class CandidateChild(candidate.Label):
        pass
    child_o, child_c = OracleChild((3, 5)), CandidateChild((3, 5))
    require(child_c.nondegenerate() is child_o.nondegenerate(), "Subclass nondegenerate fallback changed")
    exact_list(child_c.complement_in(candidate.Label((1, 2, 4))), child_o.complement_in(oracle.Label((1, 2, 4))))
    counts["fallback_cases"] += 2

    # Reject rebinding modules whose helpers or target methods have changed.
    for name in ("dot", "rank", "method"):
        changed = load_source("_matrix_binding_rejection_" + name)
        if name == "method":
            changed.Label.complement_in = lambda self, other: []
        else:
            setattr(changed, name, lambda *args: 0)
        failure = capture(lambda: bind(changed, native))
        require(failure[0] == "error" and failure[1] == "RuntimeError", "Binding guard admitted changed source code")
        counts["binding_rejections"] += 1
    for bad in ((1 << 64,), (-1,), (True,), (IntSubclass(1),)):
        require(native.gram_rank(dict(enumerate(bad))) is NotImplemented, "Native bound/type fallback failed")
    require(native.complement(dict(enumerate((1,))), dict(enumerate(coordinates64))) is NotImplemented,
            "Native augmented-width bound failed")

    # These independent checks must catch a mathematically wrong result and a
    # same-subspace reordered witness respectively, including under python -O.
    bad_math = capture(lambda: independent_complement([1], [1, 2], [1]))
    require(bad_math[0] == "error", "Independent complement control accepted a wrong result")
    bad_order = capture(lambda: exact_list([4, 2], [2, 4]))
    require(bad_order[0] == "error", "Ordered witness control accepted a reordered result")
    counts["oracle_negative_controls"] += 2

    # A bounded fixed corpus drawn from the frozen h25 label families; repeated
    # timings include dict conversion and dispatch, and remain diagnostic only.
    full = tuple(1 << i for i in range(25))
    star = tuple(3 | (1 << i) for i in range(2, 25))
    fixtures = [(full[:12], full), (star, full), ((7,), full), ((), full)]
    for small, big in fixtures:
        complement_case(small, big)
        gram_case(small)
        gram_case(big)
    oracle_pairs = [(raw(oracle.Label, u), raw(oracle.Label, v)) for u, v in fixtures]
    candidate_pairs = [(raw(candidate.Label, u), raw(candidate.Label, v)) for u, v in fixtures]
    micro = {}
    micro_results = {}
    for name, pairs in (("unchanged_python", oracle_pairs), ("native_with_conversion", candidate_pairs)):
        start_wall, start_cpu = time.perf_counter(), time.process_time()
        saved = []
        for _ in range(128):
            for small, big in pairs:
                saved.append((small.complement_in(big), small.nondegenerate(), big.nondegenerate()))
        micro[name] = {"wall_seconds": time.perf_counter() - start_wall,
                       "cpu_seconds": time.process_time() - start_cpu}
        micro_results[name] = saved
    require(micro_results["unchanged_python"] == micro_results["native_with_conversion"],
            "Fixed conversion-plus-kernel micro corpus changed")
    require(all(value > 0 for value in state["counters"].values()), "A native or fallback path was untested")
    v2 = v2_binding_and_trace_controls(native)
    return {"status": "FINITE_NATIVE_GF2_CONTROLS_PASS", "counts": counts,
            "native_and_fallback_calls": dict(state["counters"]),
            "fixture_sha256": transcript.hexdigest(), "micro": micro, "v2_controls": v2,
            "micro_repetitions": 128, "micro_fixtures": len(fixtures),
            "micro_scope": "Fixed h25 label families with conversion; diagnostic only, not complete side speed",
            "independent_oracle": "Dense binary lists, descending pivots, addition modulo 2; no packed/source/native helpers"}


def v2_binding_and_trace_controls(native):
    """Fail-closed lookup/dispatch drift and symmetric complete transcript controls."""
    counts = {"prebind_shadow_rejections": 0, "effective_builtins_rejections": 0,
              "postbind_drift_rejections": 0, "class_dispatch_rejections": 0,
              "real_builtin_drift_rejections": 0, "trace_pairs": 0,
              "trace_negative_controls": 0, "native_proxy_rejections": 0}
    observed = []

    def bad_helper(*args, **kwargs):
        observed.append("modified helper executed")
        return 0

    def rejected(action, message):
        before = list(observed)
        outcome = capture(action)
        require(outcome[0] == "error" and outcome[1] == "RuntimeError", message)
        require(observed == before, "A drift check invoked the modified helper/descriptor")

    class NativeProxy:
        def __getattribute__(self, name):
            observed.append("native proxy attribute read")
            return bad_helper
    proxy_source = load_source("_matrix_v2_native_proxy")
    rejected(lambda: bind(proxy_source, NativeProxy()), "Native proxy admitted before type check")
    counts["native_proxy_rejections"] += 1

    # Check every relevant effective builtin lookup, not just function bytecode.
    for name in ("list", "sum", "enumerate", "len", "range", "next", "max", "all", "tuple", "sorted"):
        changed = load_source("_matrix_v2_shadow_" + name)
        changed.__dict__[name] = bad_helper
        rejected(lambda: bind(changed, native), "Prebind global builtin shadow admitted: " + name)
        counts["prebind_shadow_rejections"] += 1

    # FunctionType captures the active builtins pointer at construction time.
    # Restoring module.__builtins__ cannot make this forged function acceptable.
    changed = load_source("_matrix_v2_function_builtins")
    canonical_builtins = changed.__dict__["__builtins__"]
    changed.__dict__["__builtins__"] = dict(canonical_builtins, sum=bad_helper)
    forged = FunctionType(changed.Label.nondegenerate.__code__, changed.__dict__)
    changed.__dict__["__builtins__"] = canonical_builtins
    changed.Label.nondegenerate = forged
    rejected(lambda: bind(changed, native), "Forged effective function builtins admitted")
    counts["effective_builtins_rejections"] += 1
    changed = load_source("_matrix_v2_module_builtins")
    changed.__dict__["__builtins__"] = dict(changed.__dict__["__builtins__"])
    rejected(lambda: bind(changed, native), "Alternate module builtins owner admitted")
    counts["effective_builtins_rejections"] += 1

    for name in ("basis", "__getattribute__"):
        changed = load_source("_matrix_v2_pre_descriptor_" + name)
        if name == "basis":
            changed.Label.basis = property(bad_helper)
        else:
            changed.Label.__getattribute__ = bad_helper
        rejected(lambda: bind(changed, native), "Prebind custom Label dispatch admitted")
        counts["class_dispatch_rejections"] += 1

    mutations = (
        ("dot_identity", lambda module, state: setattr(module, "dot", bad_helper)),
        ("rank_identity", lambda module, state: setattr(module, "rank", bad_helper)),
        ("sum_shadow", lambda module, state: setattr(module, "sum", bad_helper)),
        ("list_shadow", lambda module, state: setattr(module, "list", bad_helper)),
        ("module_builtins", lambda module, state: module.__dict__.__setitem__("__builtins__", dict(builtins.__dict__))),
        ("dot_code", lambda module, state: setattr(module.dot, "__code__", (lambda x, y: 0).__code__)),
        ("dot_defaults", lambda module, state: setattr(module.dot, "__defaults__", (0,))),
        ("saved_method_code", lambda module, state: setattr(state["original_nondegenerate"], "__code__", (lambda self: False).__code__)),
        ("label_init_code", lambda module, state: setattr(module.Label.__init__, "__code__", (lambda self, vectors: None).__code__)),
        ("basis_descriptor", lambda module, state: setattr(module.Label, "basis", property(bad_helper))),
        ("getattribute_dispatch", lambda module, state: setattr(module.Label, "__getattribute__", bad_helper)),
        ("label_global", lambda module, state: setattr(module, "Label", object)),
    )
    for name, mutate in mutations:
        module = load_source("_matrix_v2_post_" + name)
        state = bind(module, native)
        small, big = raw(module.Label, (1,)), raw(module.Label, (1, 2))
        # Capture bound entry points before changing class attribute dispatch.
        gram_call = small.nondegenerate
        complement_call = small.complement_in
        before = dict(state["counters"])
        mutate(module, state)
        rejected(gram_call, "Postbind drift admitted by nondegenerate: " + name)
        rejected(lambda: complement_call(big), "Postbind drift admitted by complement: " + name)
        require(state["counters"] == before, "Drift reached native work or fallback")
        counts["postbind_drift_rejections"] += 2

    # The shared builtins dictionary is restored in finally before any following
    # numerical fixture. No altered builtin is called to observe the mutation.
    for postbind in (False, True):
        module = load_source("_matrix_v2_real_builtin_" + str(postbind))
        if postbind:
            state = bind(module, native)
            small = raw(module.Label, (1,))
            call = small.nondegenerate
            before = dict(state["counters"])
        original_sum = builtins.sum
        try:
            builtins.sum = bad_helper
            rejected(call if postbind else lambda: bind(module, native), "Shared builtin drift admitted")
        finally:
            builtins.sum = original_sum
        if postbind:
            require(state["counters"] == before, "Shared builtin drift reached arithmetic")
        counts["real_builtin_drift_rejections"] += 1

    # Native dispatch mutation is rejected even though the wrapper retains the
    # original C callable. Restore it before another independently bound module.
    module = load_source("_matrix_v2_native_dispatch")
    state = bind(module, native)
    small = raw(module.Label, (1,))
    before = dict(state["counters"])
    original_native = native.gram_rank
    try:
        native.gram_rank = bad_helper
        rejected(small.nondegenerate, "Changed native dispatch admitted")
    finally:
        native.gram_rank = original_native
    require(state["counters"] == before, "Native dispatch drift reached arithmetic")
    counts["postbind_drift_rejections"] += 1

    # Both complete arms have the same observer and bytes; ordinary unsupported
    # integer width still works with tracing, while custom containers are never
    # observed by the full-run trace and keep their existing finite fallback tests.
    oracle = load_source("_matrix_v2_trace_oracle")
    candidate = load_source("_matrix_v2_trace_candidate")
    guard_module(oracle)
    oracle_rank, candidate_rank = [], []
    oracle_trace = ComplementTrace(oracle.Label)
    candidate_trace = ComplementTrace(candidate.Label)
    attach_trace(oracle, oracle_rank, oracle_trace)
    bind(candidate, native, candidate_rank, candidate_trace)
    fixtures = [((), ()), ((), (1, 2, 4)), ((1,), (1, 2, 4)),
                ((3, 5), (1, 2, 4)), ((4, 1), (4, 2, 1)),
                ((1 << 64,), (1, 1 << 64)), ((1 << 100,), (1, 2, 1 << 100))]
    for us, vs in fixtures:
        left_o, right_o = raw(oracle.Label, us), raw(oracle.Label, vs)
        left_c, right_c = raw(candidate.Label, us), raw(candidate.Label, vs)
        exact_list(left_c.complement_in(right_c), left_o.complement_in(right_o))
        require(left_c.nondegenerate() is left_o.nondegenerate(), "Traced Gram result changed")
        counts["trace_pairs"] += 1
    require(oracle_trace.receipt() == candidate_trace.receipt() and oracle_rank == candidate_rank,
            "Baseline/candidate exact ordered stream differs")
    list_trace, none_trace = ComplementTrace(oracle.Label), ComplementTrace(oracle.Label)
    list_trace.after(((), ()), [])
    none_trace.after(((), ()), None)
    require(list_trace.receipt()["sha256"] != none_trace.receipt()["sha256"], "Trace conflates [] with None")
    order_a, order_b = ComplementTrace(oracle.Label), ComplementTrace(oracle.Label)
    order_a.after(((1,), (1, 2, 4)), [2, 4])
    order_b.after(((1,), (1, 2, 4)), [4, 2])
    require(order_a.receipt()["sha256"] != order_b.receipt()["sha256"], "Trace loses output order")
    input_a, input_b = ComplementTrace(oracle.Label), ComplementTrace(oracle.Label)
    input_a.after(((1, 2), (1, 2, 4)), [4])
    input_b.after(((2, 1), (1, 2, 4)), [4])
    require(input_a.receipt()["sha256"] != input_b.receipt()["sha256"], "Trace loses input order")
    invalid = raw(oracle.Label, (1,), BrokenValues)
    rejected(lambda: oracle_trace.before(invalid, raw(oracle.Label, (1,))), "Full trace accepted a side-effecting fallback container")
    counts["trace_negative_controls"] += 4
    require(observed == [], "A guarded modified helper was invoked")
    return {"status": "V2_RUNTIME_AND_COMPLEMENT_STREAM_PASS", "counts": counts,
            "complement_fixture_stream": oracle_trace.receipt(),
            "modified_helper_invocations": len(observed),
            "runtime_policy": "Reject before native/fallback on source helper, effective builtins, class, function, closure or native dispatch drift"}
