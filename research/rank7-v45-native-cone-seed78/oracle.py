# SPDX-License-Identifier: Apache-2.0
"""Independent forward SSA oracle for abstract, time-ordered dependency records.

Prepared with substantial OpenAI Codex assistance. This module is new cone
verification logic, not a native kernel or a multiplication theorem. It imports
no producer code and has no command-line entry point or import-time execution.
"""


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _slot(value):
    _require(isinstance(value, str), "oracle: state slot must be a string")
    channel, separator, name = value.partition(":")
    _require(bool(channel and separator and name), "oracle: expected channel:name slot")
    return value


def _slots(values, label):
    _require(type(values) in (list, tuple, set, frozenset),
             "oracle: " + label + " must be a finite slot collection")
    _require(len(values) <= 4096, "oracle: slot collection capacity")
    return [_slot(value) for value in values]


def _graph(records, initial):
    _require(type(records) is list and len(records) <= 100000,
             "oracle: expected at most 100000 ordered records")
    nodes = [{"id": i, "slot": slot, "version": 0, "producer": None,
              "predecessors": []} for i, slot in enumerate(initial)]
    state = {slot: i for i, slot in enumerate(initial)}
    counters = {slot: 0 for slot in initial}
    events, event_roots, previous = [], {}, -1
    for record in records:
        _require(type(record) is dict and set(record) == {"index", "outputs", "roots"},
                 "oracle: record requires exactly index/outputs/roots")
        index = record["index"]
        _require(type(index) is int and index >= 0 and index > previous,
                 "oracle: event indices must be strictly increasing nonnegative integers")
        previous = index
        outputs = record["outputs"]
        _require(type(outputs) is dict and len(outputs) <= 4096,
                 "oracle: invalid output map")
        pending = []
        for output, inputs in outputs.items():
            output = _slot(output)
            _require(type(inputs) is list, "oracle: predecessor slots must be a list")
            inputs = _slots(inputs, "predecessors")
            _require(all(slot in state for slot in inputs),
                     "oracle: unknown pre-event input slot")
            pending.append((output, sorted({state[slot] for slot in inputs})))
        _require(len(set(state) | set(outputs)) <= 4096, "oracle: total slot capacity")
        written = []
        # Every predecessor above was resolved before any output is installed.
        for output, predecessors in pending:
            version = counters.get(output, -1) + 1
            counters[output] = version
            node_id = len(nodes)
            nodes.append({"id": node_id, "slot": output, "version": version,
                          "producer": index, "predecessors": predecessors})
            state[output] = node_id
            written.append(node_id)
        requested = _slots(record["roots"], "post-event roots")
        _require(all(slot in state for slot in requested),
                 "oracle: unknown post-event root slot")
        resolved = sorted({state[slot] for slot in requested})
        event_roots[index] = resolved
        events.append({"index": index, "output_versions": written,
                       "root_versions": resolved})
    return state, nodes, events, event_roots


def dependency_cone(records, initial_slots, final_slots=()):
    """Build forward SSA, then return the exact backward-reachable event set.

    Record: {'index': int, 'outputs': {slot: [pre-event input slots]},
             'roots': [post-event state slots]}.
    Slots use channel:name strings. Outputs can introduce fresh slots, including
    constants with no predecessors. All reads must already exist before the
    event; simultaneous outputs never read each other's new versions. Initial
    and final collections can be lists, tuples, sets, or frozensets. Repeated
    dependency/root slots are normalized as graph edges, without algebraic
    cancellation. Inputs are never mutated. No event-kind semantics are inferred.
    """
    initial = sorted(set(_slots(initial_slots, "initial slots")))
    state, nodes, events, event_roots = _graph(records, initial)
    final = _slots(final_slots, "final slots")
    _require(all(slot in state for slot in final), "oracle: unknown final root slot")
    roots = {state[slot] for slot in final}
    roots.update(node for values in event_roots.values() for node in values)
    pending, reached, selected, boundary = list(roots), set(), set(), set()
    while pending:
        node_id = pending.pop()
        if node_id in reached:
            continue
        reached.add(node_id)
        node = nodes[node_id]
        if node["producer"] is None:
            boundary.add(node["slot"])
        else:
            selected.add(node["producer"])
        pending.extend(node["predecessors"])
    return {"event_indices": sorted(selected), "boundary_inputs": sorted(boundary),
            "versions": nodes, "events": events, "event_roots": event_roots,
            "root_versions": sorted(roots), "reachable_versions": sorted(reached),
            "initial_versions": {slot: i for i, slot in enumerate(initial)},
            "final_versions": {slot: state[slot] for slot in sorted(set(final))}}
