"""Bounded P1 controls. Parent runner alone imports/executes this module.

run_controls(backend, set_adapter) takes the existing trusted backend and the
already loaded set adapter; it performs no implicit module-name import.
The two module instances keep the literal reference independent. Tiny raw
fixtures use an explicitly trusted finite-fixture lease issuer; these fixtures
do not establish the complete CLI's constructor provenance.
"""
from __future__ import annotations

import gc
import sys

def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def typed(value):
    if type(value) is dict:
        return ("dict", tuple((typed(key), typed(item)) for key, item in value.items()))
    if type(value) is list or type(value) is tuple:
        return (type(value).__name__, tuple(typed(item) for item in value))
    return (type(value).__name__, value)


def outcome(function, checks):
    try:
        return ("value", typed(function(checks)))
    except Exception as error:
        return ("error", type(error).__name__, error.args)


def configure(module, circuit, triples, *, keep_list=False):
    if keep_list:
        circuit.triples[:] = triples
    else:
        circuit.triples = list(triples)
    circuit.active = set()
    circuit.args = [None]
    circuit.support = [0]
    circuit.pieces = []
    seen = set()
    for target in circuit.triples:
        if target in seen:
            continue
        seen.add(target)
        for coefficient, predicate in ((module.Q(1, 2), lambda size: size == 0),
                                       (module.Q(-1, 2), lambda size: size == 2)):
            mask = sum(1 << index for index, other in enumerate(circuit.triples)
                       if predicate(len(set(target) & set(other))))
            if mask:
                circuit.support.append(mask)
                circuit.args.append(None)
                circuit.pieces.append((target, len(circuit.support)-1, coefficient))


def raw(module, triples):
    circuit = object.__new__(module.ComplexSideCircuit)
    configure(module, circuit, triples)
    checks = object.__new__(module.Checks)
    checks.c = circuit
    return circuit, checks


class Prefix:
    def __init__(self, events, action=None):
        self.events = events
        self.action = action

    def __iter__(self):
        self.events.append("prefix")
        if self.action is not None:
            self.action()
        return iter(())


class RecursivePrefix:
    def __init__(self, events):
        self.events = events
        self.action = None
        self.entered = False

    def __iter__(self):
        self.events.append("prefix")
        if not self.entered:
            self.entered = True
            self.action()
        return iter(())


def run_controls(backend, set_adapter):
    load_source = backend.load_source
    bind_verify_map = set_adapter.bind_verify_map
    # Policy-only checks use literal digests, never import/execute alternate
    # Fraction source. Actual loaded code still receives the existing checks.
    source_pin_cases = []
    for digest, expected_profile in (
            ("cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231",
             "recorded-local-cpython-3.12.3"),
            ("d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0",
             "official-cpython-3.12.15-e848e4b09ca4bc67c0041c9ce7526dae471d4c36")):
        need(set_adapter._fraction_source_profile(digest) == expected_profile,
             "Reviewed Fraction source pin was not recognized")
        source_pin_cases.append({"digest": digest, "outcome": "recognized"})
    class StringSubclass(str):
        pass
    for unsupported in ("0"*64, "", StringSubclass(digest)):
        try:
            set_adapter._fraction_source_profile(unsupported)
        except RuntimeError as error:
            need(error.args == ("Set reuse Fraction source differs",), "Unknown source-pin rejection changed")
        else:
            raise RuntimeError("Unreviewed or non-exact source digest was admitted")
        source_pin_cases.append({"input_type": type(unsupported).__name__, "outcome": "rejected"})
    oracle = load_source("_h25_set_controls_original")
    candidate = load_source("_h25_set_controls_candidate")
    original_candidate = candidate.Checks.verify_map
    literal = oracle.Checks.verify_map
    rows = []
    standard = [(0, 1, 2), (3, 4, 5), (0, 1, 3), (0, 4, 5)]

    def binding():
        candidate.Checks.verify_map = original_candidate
        result = bind_verify_map(candidate)
        need(set_adapter._fraction_source_profile(result["receipt"]["fraction_sha256"]) ==
             result["receipt"]["fraction_source_profile"], "Receipt misreports selected Fraction source")
        candidate.Checks.verify_map = result["verify_map"]
        result["owner"].seal()
        return result

    def fixture_issue(result, circuit, checks):
        # Explicit trusted test-only issuer. The full driver must use actual
        # post-original-constructor captures, never raw fixture provenance.
        owner = result["owner"]
        owner.arm_cli()
        need(owner.capture_c(circuit), "Fixture circuit capture failed")
        need(owner.capture_checks(checks), "Fixture Checks capture failed")

    def compare(name, result, left, right, left_events=(), right_events=(), *, fast=0, fallbacks=1):
        expected = outcome(literal, left)
        actual = outcome(result["verify_map"], right)
        need(actual == expected, "Set control outcome differs: " + name)
        need(list(right_events) == list(left_events), "Set control callback order differs: " + name)
        need(result["receipt"]["fast_admissions"] == fast, "Set control fast-path count differs: " + name)
        need(result["receipt"]["fallback_calls"] == fallbacks, "Set control fallback count differs: " + name)
        need(result["owner"].current is None, "Set control retained an active token: " + name)
        rows.append({"name": name, "outcome": actual[0], "fast_admissions": fast, "fallback_calls": fallbacks})
        result["owner"].disarm_cli()

    # Exact values, all intersection sizes, duplication/order, and integer width.
    for name, triples in (
            ("all-intersection-sizes", standard),
            ("duplicate-positional-triples", standard + [standard[0]]),
            ("reordered-triples", list(reversed(standard))),
            ("negative-and-wide-integers", [(-5, 1 << 100, 9), (-5, 1 << 100, 10), (2, 3, 4)]),
            ("empty-triples", [])):
        result = binding()
        _, left = raw(oracle, triples)
        circuit, right = raw(candidate, triples)
        fixture_issue(result, circuit, right)
        compare(name, result, left, right, fast=1, fallbacks=0)
        need(result["receipt"]["private_operand_sets_constructed"] == len(triples),
             "Set construction count differs from positional triple count")
        need(result["receipt"]["reservations_expired"] == 1, "Successful lease did not expire")

    # No allowance: ordinary source method executes, including prefix once.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    left_c.active, right_c.active = Prefix(left_events), Prefix(right_events)
    compare("no-allowance-prefix-once", result, left, right, left_events, right_events)
    need(left_events == ["prefix"], "Missing-lease fixture did not cover prefix")

    # Correctly shaped objects cannot borrow another Checks identity.
    result = binding()
    _, left = raw(oracle, standard)
    right_c, captured = raw(candidate, standard)
    right = object.__new__(candidate.Checks)
    right.c = right_c
    fixture_issue(result, right_c, captured)
    compare("wrong-checks-identity", result, left, right)

    result = binding()
    _, left = raw(oracle, standard)
    captured_c, right = raw(candidate, standard)
    other_c, _ = raw(candidate, standard)
    fixture_issue(result, captured_c, right)
    right.c = other_c
    compare("wrong-circuit-link", result, left, right)

    # Reservation is spent before a prefix can reenter the method.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    left_c.active, right_c.active = RecursivePrefix(left_events), RecursivePrefix(right_events)
    left_c.active.action = lambda: literal(left)
    right_c.active.action = lambda: result["verify_map"](right)
    fixture_issue(result, right_c, right)
    compare("prefix-reentry-single-reservation", result, left, right, left_events, right_events,
            fast=1, fallbacks=1)
    need(left_events == ["prefix", "prefix"] and result["receipt"]["reservations"] == 1,
         "Recursive fixture did not consume one outer reservation")

    # The post-prefix state, not an earlier eager snapshot, supplies operands.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    changed = [(10, 11, 12), (10, 11, 13), (20, 21, 22)]
    left_events, right_events = [], []
    left_c.active = Prefix(left_events, lambda: configure(oracle, left_c, changed, keep_list=True))
    right_c.active = Prefix(right_events, lambda: configure(candidate, right_c, changed, keep_list=True))
    fixture_issue(result, right_c, right)
    compare("post-prefix-mutated-values", result, left, right, left_events, right_events,
            fast=1, fallbacks=0)
    need(result["receipt"]["private_operand_sets_constructed"] == len(changed),
         "Set cache preceded prefix mutation")

    # Prefix exceptions happen before set construction, even with a valid lease.
    def fail_prefix():
        raise ValueError("prefix sentinel")

    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    left_c.active, right_c.active = Prefix(left_events, fail_prefix), Prefix(right_events, fail_prefix)
    fixture_issue(result, right_c, right)
    compare("failing-prefix-no-eager-cache", result, left, right, left_events, right_events,
            fast=0, fallbacks=0)
    need(result["receipt"]["private_operand_sets_constructed"] == 0, "Failing prefix built sets")

    # Callback-bearing triple subclasses must use literal post-prefix tail.
    def callback_triple(events, base):
        class Triple(tuple):
            def __iter__(self):
                events.append("triple-iter")
                return tuple.__iter__(self)
        return Triple(base)

    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    left_c.triples[0] = callback_triple(left_events, standard[0])
    right_c.triples[0] = callback_triple(right_events, standard[0])
    fixture_issue(result, right_c, right)
    compare("tuple-subclass-callback-fallback", result, left, right, left_events, right_events)
    need(left_events, "Tuple callback fixture did not execute callbacks")

    def callback_integer(events, value):
        class Integer(int):
            def __hash__(self):
                events.append("integer-hash")
                return int.__hash__(self)
        return Integer(value)

    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    left_c.triples[0] = (callback_integer(left_events, 0), 1, 2)
    right_c.triples[0] = (callback_integer(right_events, 0), 1, 2)
    fixture_issue(result, right_c, right)
    compare("integer-subclass-hash-fallback", result, left, right, left_events, right_events)
    need(left_events, "Integer callback fixture did not execute callbacks")

    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_c.triples[0] = (False, 1, 2)
    right_c.triples[0] = (False, 1, 2)
    fixture_issue(result, right_c, right)
    compare("bool-member-exact-type-fallback", result, left, right)

    # The got dictionary can retain a hostile equality key from the prefix.
    def collision_key(circuit, events, base):
        class Target(tuple):
            __hash__ = tuple.__hash__
            fired = False

            def __eq__(self, other):
                events.append("collision-equality")
                if not self.fired:
                    self.fired = True
                    circuit.triples.reverse()
                return tuple.__eq__(self, other)
        return Target(base)

    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    for circuit, events in ((left_c, left_events), (right_c, right_events)):
        target, node, coefficient = circuit.pieces[0]
        circuit.pieces[0] = (collision_key(circuit, events, target), node, coefficient)
    fixture_issue(result, right_c, right)
    compare("got-collision-key-fallback", result, left, right, left_events, right_events)
    if sys.flags.optimize:
        # This fixture's collision lookup is in the original tail assert.
        need(left_events == [] and right_events == [],
             "Optimized collision fixture unexpectedly executed assertion-only equality")
    else:
        need(left_events, "Collision fixture did not reach custom equality")

    # Runtime source-global drift retains original live resolution in fallback.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    def logging_set(events):
        def wrapped(values):
            events.append("set")
            return set(values)
        return wrapped
    oracle.set, candidate.set = logging_set(left_events), logging_set(right_events)
    fixture_issue(result, right_c, right)
    try:
        compare("live-source-set-resolution", result, left, right, left_events, right_events)
        need(len(left_events) == 4*len(standard)**2, "Literal fallback lost original set calls")
    finally:
        del oracle.set
        del candidate.set

    result = binding()
    _, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_events, right_events = [], []
    original_q = candidate.Q
    def logging_q(events):
        def wrapped(*args):
            events.append("Q")
            return original_q(*args)
        return wrapped
    fixture_issue(result, right_c, right)
    oracle.Q, candidate.Q = logging_q(left_events), logging_q(right_events)
    try:
        compare("live-Fraction-global-resolution", result, left, right, left_events, right_events)
        if sys.flags.optimize:
            # Every original verify_map Q(...) call is inside an assert.
            need(left_events == [] and right_events == [],
                 "Optimized Fraction fixture unexpectedly executed assertion-only constructors")
        else:
            need(left_events, "Fraction callback fixture did not execute callbacks")
    finally:
        oracle.Q = candidate.Q = original_q

    # The exact Fraction class is mutable: unchanged class identity alone is
    # insufficient. A changed method after binding must deny optimization.
    result = binding()
    _, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    fixture_issue(result, right_c, right)
    original_hash = original_q.__hash__
    hash_events = []
    def traced_hash(value):
        hash_events.append("fraction-hash")
        return original_hash(value)
    original_q.__hash__ = traced_hash
    try:
        expected = outcome(literal, left)
        expected_events = list(hash_events)
        hash_events.clear()
        actual = outcome(result["verify_map"], right)
        need(actual == expected and hash_events == expected_events and hash_events,
             "Changed Fraction method fallback differs")
        need(result["receipt"]["fast_admissions"] == 0 and result["receipt"]["fallback_calls"] == 1,
             "Changed Fraction method was admitted")
    finally:
        original_q.__hash__ = original_hash
        result["owner"].disarm_cli()
    rows.append({"name": "changed-Fraction-hash", "outcome": actual[0], "fast_admissions": 0, "fallback_calls": 1})

    # A used capability cannot cache values for a later invocation.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    fixture_issue(result, right_c, right)
    need(outcome(result["verify_map"], right) == outcome(literal, left), "Initial leased call differs")
    configure(oracle, left_c, changed)
    configure(candidate, right_c, changed)
    compare("used-capability-changed-later-input", result, left, right, fast=1, fallbacks=1)
    need(result["receipt"]["private_operand_sets_constructed"] == len(standard),
         "Used capability constructed a second private cache")

    # Observable known hooks deny optimization without changing hook policy.
    for hook in ("trace", "profile", "gc-callback"):
        result = binding()
        _, left = raw(oracle, standard)
        right_c, right = raw(candidate, standard)
        fixture_issue(result, right_c, right)
        def quiet_trace(frame, event, arg):
            return quiet_trace
        def quiet_gc(phase, info):
            return None
        if hook == "trace":
            sys.settrace(quiet_trace)
        elif hook == "profile":
            sys.setprofile(quiet_trace)
        else:
            gc.callbacks.append(quiet_gc)
        try:
            actual = outcome(result["verify_map"], right)
        finally:
            if hook == "trace":
                sys.settrace(None)
            elif hook == "profile":
                sys.setprofile(None)
            else:
                gc.callbacks.remove(quiet_gc)
        need(actual == outcome(literal, left), "Hook-denied fallback differs: " + hook)
        need(result["receipt"]["fast_admissions"] == 0 and result["receipt"]["fallback_calls"] == 1,
             "Known hook was admitted: " + hook)
        result["owner"].disarm_cli()
        rows.append({"name": "known-hook-" + hook, "outcome": actual[0], "fast_admissions": 0, "fallback_calls": 1})

    # Deliberate tail assertion failure retains a traceback: cached operands
    # must have been cleared/reset even while the frame itself remains live.
    result = binding()
    left_c, left = raw(oracle, standard)
    right_c, right = raw(candidate, standard)
    left_c.support[1] ^= 1 << 20
    right_c.support[1] ^= 1 << 20
    fixture_issue(result, right_c, right)
    expected = outcome(literal, left)
    retained = None
    try:
        actual = ("value", typed(result["verify_map"](right)))
    except Exception as error:
        actual = ("error", type(error).__name__, error.args)
        retained = error.__traceback__
    need(actual == expected, "Tail-failure outcome differs")
    if not sys.flags.optimize:
        need(actual[0] == "error" and actual[1] == "AssertionError", "Tail-failure fixture did not fail")
        found = False
        while retained is not None:
            if retained.tb_frame.f_code is result["verify_map"].__code__:
                found = True
                values = retained.tb_frame.f_locals
                need(values["_h25_sr_sets"] is None and values["_h25_sr_left"] is None,
                     "Retained traceback kept private cached operands")
            retained = retained.tb_next
        need(found, "Candidate traceback frame was not inspected")
    need(result["owner"].current is None, "Tail error retained lease")
    need(result["receipt"]["fast_admissions"] == 1, "Tail cleanup fixture did not use cached sets")
    result["owner"].disarm_cli()
    rows.append({"name": "traceback-cleanup", "outcome": actual[0], "fast_admissions": 1, "fallback_calls": 0})

    candidate.Checks.verify_map = original_candidate
    need(oracle.Checks.verify_map is literal, "Independent source reference was changed")
    return {"status": "P1_FINITE_SET_CONTROLS_PASS", "optimize": sys.flags.optimize,
            "cases": len(rows), "rows": rows, "source_pin_policy_cases": source_pin_cases,
            "scope": "Bounded finite semantics and negative controls; not full-caller ownership or performance evidence"}
