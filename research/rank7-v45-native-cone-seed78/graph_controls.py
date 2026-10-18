# SPDX-License-Identifier: Apache-2.0
"""Handwritten normative controls for two abstract dependency-closure algorithms.

Prepared with substantial OpenAI Codex assistance. This worker wrote the file
without reading or importing the primary cone implementation. Root owns all
execution. The checks compare closures against explicit expected answers; they
do not independently validate the shared event-to-record semantic decoder.
"""


def _require(condition, message):
    if not condition:
        raise ValueError("graph controls: " + message)


def _record(index, outputs, roots=()):
    return {"index": index, "outputs": outputs, "roots": list(roots)}


def _fixture(name, initial, records, events, boundary):
    return {"name": name, "initial": initial, "records": records,
            "expected": {"event_indices": events, "boundary_inputs": boundary}}


def _value_fixtures():
    return [
        _fixture("source_only_ADD_demand", ["value:s", "value:t"],
                 [_record(0, {"value:t": ["value:t", "value:s"]}, ["value:s"])],
                 [], ["value:s"]),
        _fixture("COPY_kills_old_target", ["value:s", "value:t"],
                 [_record(0, {"value:t": ["value:t"]}),
                  _record(1, {"value:t": ["value:s"]}, ["value:t"])],
                 [1], ["value:s"]),
        _fixture("CLEAR_constant_keeps_its_producer", ["value:t"],
                 [_record(0, {"value:t": ["value:t"]}),
                  _record(1, {"value:t": []}, ["value:t"])], [1], []),
        _fixture("simultaneous_writes_read_pre_versions", ["value:a", "value:b"],
                 [_record(0, {"value:a": ["value:b"], "value:b": ["value:a"]},
                          ["value:a", "value:b"])], [0], ["value:a", "value:b"]),
        _fixture("same_event_root_reads_new_version", ["value:s", "value:t"],
                 [_record(9, {"value:t": ["value:s"]}, ["value:t"])],
                 [9], ["value:s"]),
        _fixture("root_only_event_is_not_a_writer", ["value:s"],
                 [_record(2, {"value:t": ["value:s"]}),
                  _record(31, {}, ["value:t"])], [2], ["value:s"]),
    ]


def _structural_fixtures():
    chart = _fixture("chart_only_dependency_keeps_unary_path",
        ["chart:r", "value:s"],
        [_record(0, {"chart:r": ["chart:r"]}),
         _record(1, {"chart:r": ["chart:r"]}),
         _record(2, {"value:t": ["value:s", "chart:r"]}, ["value:t"])],
        [0, 1, 2], ["chart:r", "value:s"])
    lifetime = _fixture("free_obligation_keeps_prefree_value_after_CLEAR_COPY",
        ["value:s", "value:spare"],
        [_record(0, {"value:z": [], "chart:z": [], "lifetime:z": []}),
         _record(1, {"value:z": ["value:s"]}),
         _record(2, {"lifetime:z": ["value:z", "chart:z", "lifetime:z"]},
                 ["lifetime:z"]),
         _record(3, {"value:z": []}),
         _record(4, {"value:z": ["value:spare"]})],
        [0, 1, 2], ["value:s"])
    return [chart, lifetime]


def _observe(result):
    _require(type(result) is dict, "algorithm did not return a dictionary")
    _require("event_indices" in result and "boundary_inputs" in result,
             "algorithm omitted advertised closure fields")
    return {"event_indices": result["event_indices"],
            "boundary_inputs": result["boundary_inputs"]}


def _positive(cone, oracle, fixture):
    records, initial = fixture["records"], fixture["initial"]
    primary = _observe(cone.reverse_demand(records, initial))
    independent = _observe(oracle.dependency_cone(records, initial))
    expected = fixture["expected"]
    _require(primary == expected, fixture["name"] + " primary differs from normative answer")
    _require(independent == expected,
             fixture["name"] + " SSA differs from normative answer")
    return {"name": fixture["name"], "status": "PASS_EXPLICIT_NORMATIVE_ANSWER",
            "expected": expected, "primary": primary, "independent": independent}


def _missing_edge(cone, oracle):
    fixture = _structural_fixtures()[0]
    records = [_record(0, {"chart:r": ["chart:r"]}),
               _record(1, {"chart:r": ["chart:r"]}),
               _record(2, {"value:t": ["value:s"]}, ["value:t"])]
    expected = fixture["expected"]
    corrupted_answer = {"event_indices": [2], "boundary_inputs": ["value:s"]}
    primary = _observe(cone.reverse_demand(records, fixture["initial"]))
    independent = _observe(oracle.dependency_cone(records, fixture["initial"]))
    _require(primary == corrupted_answer and independent == corrupted_answer,
             "missing-edge fixture does not expose its stated corrupted closure")
    _require(primary != expected and independent != expected,
             "missing chart edge was accepted against original normative answer")
    return {"name": "omit_required_chart_edge", "status": "EXPECTED_NORMATIVE_MISMATCH",
            "original_explicit_expected": expected, "corrupted_primary": primary,
            "corrupted_independent": independent,
            "meaning": "Agreement on corrupted shared records cannot validate their semantics"}


def _invalid_cases():
    empty = _record(0, {})
    return [
        ("unknown_read", [_record(0, {"value:t": ["value:missing"]})], [], (),
         "unknown pre-event input slot"),
        ("same_event_fresh_read", [_record(0, {"value:a": [], "value:b": ["value:a"]})],
         [], (), "unknown pre-event input slot"),
        ("unknown_post_event_root", [_record(0, {}, ["value:missing"])], [], (),
         "unknown post-event root slot"),
        ("unknown_final_root", [], [], ["value:missing"], "unknown final root slot"),
        ("boolean_index", [_record(True, {})], [], (), "strictly increasing nonnegative"),
        ("negative_index", [_record(-1, {})], [], (), "strictly increasing nonnegative"),
        ("duplicate_index", [_record(0, {}), _record(0, {})], [], (),
         "strictly increasing nonnegative"),
        ("decreasing_index", [_record(2, {}), _record(1, {})], [], (),
         "strictly increasing nonnegative"),
        ("extra_schema_key", [{"index": 0, "outputs": {}, "roots": [], "extra": 1}],
         [], (), "requires exactly index/outputs/roots"),
        ("nonmapping_outputs", [_record(0, [])], [], (), "invalid output map"),
        ("nonlist_dependencies", [_record(0, {"value:t": ("value:s",)})],
         ["value:s"], (), "predecessor slots must be a list"),
        ("malformed_slot", [], ["no_channel_separator"], (), "expected channel:name slot"),
        ("event_capacity", [empty] * 100001, [], (), "at most 100000 ordered records"),
        ("initial_slot_capacity", [], ["value:r" + str(i) for i in range(4097)], (),
         "slot collection capacity"),
        ("introduced_slot_capacity", [_record(0, {"value:new": []})],
         ["value:r" + str(i) for i in range(4096)], (), "total slot capacity"),
    ]


def _reject(oracle, case):
    name, records, initial, final, expected_reason = case
    try:
        oracle.dependency_cone(records, initial, final)
    except ValueError as error:
        _require(expected_reason in str(error), name + " rejected at a different guard")
        return {"name": name, "status": "EXPECTED_ORACLE_INPUT_REJECTION",
                "reason": str(error), "expected_reason": expected_reason}
    raise ValueError("graph controls: oracle accepted " + name)


def run(cone, oracle):
    """Return a serializable passing receipt, or raise an explicit exception.

    Root passes already-loaded modules; this function loads/imports nothing and
    launches no subprocesses. Invalid-input controls exercise only the oracle's
    advertised input validation, not an unstated primary-validator contract.
    """
    positives = [_positive(cone, oracle, fixture)
                 for fixture in _value_fixtures() + _structural_fixtures()]
    missing_edge = _missing_edge(cone, oracle)
    guards = [_reject(oracle, case) for case in _invalid_cases()]
    return {"status": "PASS_ABSTRACT_GRAPH_CONTROLS", "positive_fixtures": positives,
            "normative_missing_edge_control": missing_edge, "oracle_input_guards": guards,
            "counts": {"positive_fixtures": len(positives), "missing_edge_mutants": 1,
                       "oracle_input_guards": len(guards)},
            "independence_scope": "Independent closure algorithms against handwritten "
                "normative answers; shared event-to-record decoder semantics remain outside",
            "native_or_supplier_or_kappa_claim": False}
