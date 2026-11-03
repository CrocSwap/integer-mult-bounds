"""Bounded differential P2 controls; parent runner executes this module.

Four fresh source modules are loaded (traced/untraced reference/candidate). Each
private binding is safely restored and reused across negative cases. This suite
supplements, and never replaces, PR5995's independent finite controls.
"""
from __future__ import annotations

import builtins
import hashlib
import json
from types import FunctionType, ModuleType

_TYPE = type
_LEN = len
_TUPLE = tuple
_DICT = dict
_LIST = list
_OBJECT = object
_SETATTR = setattr
_DELATTR = delattr
_GETATTR = getattr
_STR = str
_RUNTIME_ERROR = RuntimeError
_MISSING = object()


def _require(condition, message):
    if not condition:
        raise _RUNTIME_ERROR(message)


def _capture(action):
    try:
        value = action()
    except Exception as error:
        return ("error", _TYPE(error).__name__, _STR(error))
    return ("value", _TYPE(value).__name__, value)


def _attribute_patch(owner, name, value=_MISSING):
    """Prepare a reversible patch; absent attributes use exact owner dictionaries."""
    namespace = owner.__dict__
    present = name in namespace
    original = namespace[name] if present else _MISSING

    def apply():
        if value is _MISSING:
            _DELATTR(owner, name)
        else:
            _SETATTR(owner, name, value)

    def restore():
        if present:
            _SETATTR(owner, name, original)
        else:
            _DELATTR(owner, name)

    return apply, restore


def _function_patch(function, name, value):
    original = _GETATTR(function, name)

    def apply():
        _SETATTR(function, name, value)

    def restore():
        _SETATTR(function, name, original)

    return apply, restore


def _cell_patch(cell, empty):
    original = cell.cell_contents
    replacement = _OBJECT()

    def apply():
        if empty:
            del cell.cell_contents
        else:
            cell.cell_contents = replacement

    def restore():
        cell.cell_contents = original

    return apply, restore


def _combined_patch(*patches):
    def apply():
        completed = []
        try:
            for forward, backward in patches:
                forward()
                completed.append(backward)
        except Exception:
            while completed:
                completed.pop()()
            raise

    def restore():
        for _, backward in patches[::-1]:
            backward()

    return apply, restore


def _snapshot(env):
    trace = env["trace"]
    return (_DICT(env["state"]["counters"]), _TUPLE(env["rank_calls"]),
            None if trace is None else trace.receipt(), _TUPLE(env["callbacks"]))


def _functions(env):
    module, state = env["module"], env["state"]
    label = state["label"]
    rows = [("echelon", module.echelon), ("reduce", module.reduce),
            ("dot", state["original_dot"]), ("original_rank", state["original_rank"]),
            ("Label.__init__", label.__init__), ("Label.contains", label.contains),
            ("original_nondegenerate", state["original_nondegenerate"]),
            ("original_complement", state["original_complement"]),
            ("installed_nondegenerate", label.nondegenerate),
            ("installed_complement", label.complement_in)]
    if env["traced"]:
        rows.append(("traced_rank", module.rank))
    return rows


def _make_env(backend, native, traced, suffix):
    module = backend.load_source("_h25_p2_" + suffix)
    callbacks = []

    def bad_helper(*args, **kwargs):
        callbacks.append("modified helper executed")
        return 0

    class ProbeValues:
        def values(self):
            callbacks.append("fallback values executed")
            raise ValueError("P2 fallback values sentinel")

    class ChangedModule(ModuleType):
        def __getattribute__(self, name):
            callbacks.append("modified module dispatch executed")
            return _OBJECT.__getattribute__(self, name)

    rank_calls = []
    trace = backend.ComplementTrace(module.Label) if traced else None
    state = backend.bind(module, native, rank_calls if traced else None, trace)
    label = state["label"]

    def raw(rows, custom=False):
        obj = _OBJECT.__new__(label)
        obj.basis = ProbeValues() if custom else {i: value for i, value in enumerate(rows)}
        return obj

    small, big = raw((1,)), raw((1, 2))
    wide_small, wide_big = raw((1 << 100,)), raw((1, 1 << 100))
    custom_small, custom_big = raw((), True), raw((1, 2))
    # Capture dispatch before class/global mutations. The direct guard reference
    # also remains usable when a wrapper's shared runtime closure is emptied.
    ordinary_gram = small.nondegenerate
    ordinary_complement = small.complement_in
    wide_gram = wide_small.nondegenerate
    wide_complement = wide_small.complement_in
    custom_gram = custom_small.nondegenerate
    custom_complement = custom_small.complement_in
    actions = [("held_guard", state["runtime_guard"].check),
               ("native_gram", ordinary_gram),
               ("native_complement", lambda: ordinary_complement(big)),
               ("wide_gram", wide_gram),
               ("wide_complement", lambda: wide_complement(wide_big)),
               ("container_gram", custom_gram),
               ("container_complement", lambda: custom_complement(custom_big))]
    return {"backend": backend, "module": module, "state": state,
            "native": native, "trace": trace, "rank_calls": rank_calls,
            "callbacks": callbacks, "traced": traced, "actions": actions,
            "bad_helper": bad_helper, "changed_module_type": ChangedModule}


def _case_patches(env):
    """Independent behavioral perturbations, not a copy of guard predicates."""
    module, state = env["module"], env["state"]
    label, native = state["label"], env["native"]
    bad = env["bad_helper"]
    cases = []
    for tag, function in _functions(env):
        cases.append(("function/code/" + tag,
                      _function_patch(function, "__code__", function.__code__.replace(co_name="p2_changed_code"))))
        cases.append(("function/defaults/" + tag,
                      _function_patch(function, "__defaults__", (_OBJECT(),))))
        cases.append(("function/kwdefaults/" + tag,
                      _function_patch(function, "__kwdefaults__", {"p2_probe": _OBJECT()})))
        closure = function.__closure__
        if closure is not None:
            for name, cell in zip(function.__code__.co_freevars, closure):
                cases.append(("cell/rebind/" + tag + "/" + name, _cell_patch(cell, False)))
                cases.append(("cell/empty/" + tag + "/" + name, _cell_patch(cell, True)))
    for name in ("echelon", "reduce", "dot", "rank", "Label", "__builtins__"):
        cases.append(("global/rebind/" + name, _attribute_patch(module, name, bad)))
        cases.append(("global/delete/" + name, _attribute_patch(module, name)))
    for name in ("all", "enumerate", "len", "list", "max", "next", "range",
                 "sorted", "sum", "tuple", "int", "dict", "type", "object"):
        cases.append(("builtin/shadow/" + name, _attribute_patch(module, name, bad)))
        cases.append(("builtin/shared/" + name, _attribute_patch(builtins, name, bad)))
    for name in ("__init__", "contains", "nondegenerate", "complement_in"):
        cases.append(("class/rebind/" + name, _attribute_patch(label, name, bad)))
        cases.append(("class/delete/" + name, _attribute_patch(label, name)))
    for name in ("__module__", "__doc__"):
        cases.append(("class/metadata/" + name, _attribute_patch(label, name, "P2 changed metadata")))
    cases.append(("class/basis_descriptor", _attribute_patch(label, "basis", property(bad))))
    cases.append(("class/getattribute", _attribute_patch(label, "__getattribute__", bad)))
    for name in ("gram_rank", "complement"):
        cases.append(("native/rebind/" + name, _attribute_patch(native, name, bad)))
        cases.append(("native/delete/" + name, _attribute_patch(native, name)))
    original_module_type = _TYPE(module)
    cases.append(("module/dispatch", (
        lambda: _SETATTR(module, "__class__", env["changed_module_type"]),
        lambda: _SETATTR(module, "__class__", original_module_type))))
    cases.append(("precedence/global-before-builtin", _combined_patch(
        _attribute_patch(module, "dot", bad), _attribute_patch(module, "sum", bad))))
    cases.append(("precedence/builtin-before-class", _combined_patch(
        _attribute_patch(module, "sum", bad), _attribute_patch(label, "contains", bad))))
    cases.append(("precedence/function-before-native", _combined_patch(
        _function_patch(state["original_dot"], "__defaults__", (_OBJECT(),)),
        _attribute_patch(native, "gram_rank", bad))))
    # Empty-cell access has a different exception from function metadata drift,
    # making this an observable check of order within the function-record group.
    wrapper = label.nondegenerate
    first_cell = wrapper.__closure__[0]
    cases.append(("precedence/original-function-before-wrapper-cell", _combined_patch(
        _function_patch(state["original_dot"], "__defaults__", (_OBJECT(),)),
        _cell_patch(first_cell, True))))
    return cases


def _exercise_patch(env, patch):
    apply, restore = patch
    observations = []
    apply()
    try:
        for tag, action in env["actions"]:
            before = _snapshot(env)
            outcome = _capture(action)
            after = _snapshot(env)
            observations.append((tag, outcome))
            _require(outcome[0] == "error", "P2 drift was accepted: " + tag)
            _require(before == after, "P2 drift reached work or callbacks: " + tag)
    finally:
        restore()
    # A restored binding must be live again; this also catches incomplete cleanup
    # before the next perturbation reuses it.
    env["state"]["runtime_guard"].check()
    return observations


def _inventory(env, candidate):
    guard = env["state"]["runtime_guard"]
    records = guard.functions
    expected = _functions(env)
    expected_count = (11 if env["traced"] else 10) if candidate else 13
    _require(_LEN(records) == expected_count, "P2 function record count changed")
    unique = []
    for record in records:
        function = record[0]
        if not any(function is previous for previous in unique):
            unique.append(function)
    _require(_LEN(unique) == _LEN(expected), "P2 distinct function coverage changed")
    for _, function in expected:
        _require(any(function is seen for seen in unique), "P2 lost a distinct function")
    # Derive required first occurrence order from bind's original-preservation
    # contract, independently of the candidate deduplication implementation.
    module, state = env["module"], env["state"]
    original = [module.echelon, module.reduce, state["original_dot"], state["original_rank"],
                state["label"].__init__, state["label"].contains,
                state["original_nondegenerate"], state["original_complement"]]
    current = [value for value in state["label"].__dict__.values() if _TYPE(value) is FunctionType]
    incoming = original + current + [module.rank]
    expected_first = []
    for function in incoming:
        if not any(function is seen for seen in expected_first):
            expected_first.append(function)
    _require(_LEN(unique) == _LEN(expected_first) and all(a is b for a, b in zip(unique, expected_first)),
             "P2 first-distinct record order changed")
    # Same code is not same identity. Two live functions must survive even if
    # they share code/globals/builtins and are repeated in the input sequence.
    dot = state["original_dot"]
    twin = FunctionType(dot.__code__, dot.__globals__)
    cls = env["backend"].RuntimeGuard
    extra = _OBJECT.__new__(cls)
    cls.__init__(extra, module, state["label"], env["native"], [twin, dot, twin])
    stored = [record[0] for record in extra.functions]
    _require(sum(item is twin for item in stored) == (1 if candidate else 2),
             "P2 same-object identity multiplicity changed")
    _require(sum(item is dot for item in stored) == 1, "P2 same-code distinct function disappeared")
    original_defaults = twin.__defaults__
    try:
        twin.__defaults__ = (_OBJECT(),)
        outcome = _capture(extra.check)
    finally:
        twin.__defaults__ = original_defaults
    _require(outcome == ("error", "RuntimeError", "Runtime drift: function code or calling environment"),
             "P2 distinct same-code function drift was accepted")
    extra.check()
    return {"records": _LEN(records), "distinct_functions": _LEN(unique),
            "captured_cell_reads": sum(_LEN(record[7]) for record in records),
            "same_code_distinct_function_rejected": True}


def run_guard_controls(reference_backend, candidate_backend, native):
    """Run finite old/new failure and state comparisons using one real C module.

    Backends must be distinct objects; reference must contain untouched PR5995
    RuntimeGuard, and the candidate class must be installed before this call.
    The parent must also run all original independent finite controls.
    """
    _require(reference_backend is not candidate_backend, "P2 requires separate backend modules")
    _require(reference_backend.RuntimeGuard is not candidate_backend.RuntimeGuard,
             "P2 reference and candidate guards are not independent")
    transcript = hashlib.sha256()
    counts = {"source_loads": 0, "binding_modes": 0, "mutation_pairs": 0,
              "mutation_action_pairs": 0, "stable_action_pairs": 0,
              "same_code_distinct_controls": 0}
    inventories = {}
    for traced in (False, True):
        suffix = "traced" if traced else "untraced"
        reference = _make_env(reference_backend, native, traced, "reference_" + suffix)
        candidate = _make_env(candidate_backend, native, traced, "candidate_" + suffix)
        counts["source_loads"] += 2
        counts["binding_modes"] += 1
        inventories[suffix] = {"reference": _inventory(reference, False),
                               "candidate": _inventory(candidate, True)}
        counts["same_code_distinct_controls"] += 2
        # Initial live successes and unsupported-input behavior establish that
        # the later PASS-then-mutate tests do not use an always-rejecting guard.
        for (tag_r, action_r), (tag_c, action_c) in zip(reference["actions"], candidate["actions"]):
            _require(tag_r == tag_c, "P2 stable action tags differ")
            result_r, result_c = _capture(action_r), _capture(action_c)
            _require(result_r == result_c and _snapshot(reference) == _snapshot(candidate),
                     "P2 stable native/fallback behavior differs: " + tag_r)
            transcript.update(json.dumps((suffix, "stable", tag_r, result_r),
                                         separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n")
            counts["stable_action_pairs"] += 1
        cases_r, cases_c = _case_patches(reference), _case_patches(candidate)
        _require(_LEN(cases_r) == _LEN(cases_c), "P2 mutation case counts differ")
        for (tag_r, patch_r), (tag_c, patch_c) in zip(cases_r, cases_c):
            _require(tag_r == tag_c, "P2 mutation tags differ")
            observed_r = _exercise_patch(reference, patch_r)
            observed_c = _exercise_patch(candidate, patch_c)
            _require(observed_r == observed_c, "P2 failure outcome differs: " + tag_r)
            _require(_snapshot(reference) == _snapshot(candidate), "P2 restored state differs: " + tag_r)
            transcript.update(json.dumps((suffix, tag_r, observed_r),
                                         separators=(",", ":"), sort_keys=True).encode("ascii") + b"\n")
            counts["mutation_pairs"] += 1
            counts["mutation_action_pairs"] += _LEN(observed_r)
        reference["state"]["runtime_guard"].check()
        candidate["state"]["runtime_guard"].check()
    return {"status": "P2_DIFFERENTIAL_RUNTIME_GUARD_CONTROLS_PASS", "counts": counts,
            "inventories": inventories, "transcript_sha256": transcript.hexdigest(),
            "old_finite_controls_still_required": True,
            "comparison": "exact exception type/message, state/prefix/counter/callback effects; traceback frames excluded",
            "scope": "serial stable runtime, first-distinct identities, live entry checks; no arbitrary concurrent mutation"}
