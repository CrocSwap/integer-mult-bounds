"""Exact QQ16 retained-tail replay on a formal arbitrary ordinary residue.

Apache-2.0. Prepared for @jgilfoil with substantial OpenAI Codex assistance.
No predecessor executable is imported or executed. The event projection is
checked against Ali Romman's retained QQ16 witness. Local pair indices are
read from the literal assertion in the main replica-prefix source audit.
The compressed parent template and physical endpoint types are not replayed:
their identification with these source assertions remains inherited.
"""

import ast
from copy import deepcopy
import json
from pathlib import Path


WITNESS = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
WITNESS_NOTE = "research/joint-query/evidence/QQ16-SELECTED-WITNESS.md"
PAIR_SOURCE = "research/replica-prefix-audit/verify.py"
SOURCE_PATHS = (WITNESS, WITNESS_NOTE, PAIR_SOURCE)
PAIR_VECTOR = [0, 0, 0, 1, 1, 2, 2, 3, 3]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_pairs(root):
    """Read a unique literal binding without running the predecessor audit."""
    tree = ast.parse((Path(root) / PAIR_SOURCE).read_text())
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "schedule_audit"]
    need(len(functions) == 1, "unique source schedule_audit function")
    assignments = [node for node in ast.walk(functions[0])
                   if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "expected_pairs"
                           for target in node.targets)]
    need(len(assignments) == 1, "unique source expected_pairs assignment")
    pairs = ast.literal_eval(assignments[0].value)
    need(type(pairs) is list and all(type(p) is int for p in pairs)
         and pairs == PAIR_VECTOR, "source stage/pair vector")
    # Verify that this literal is actually compared to the parent call pair.
    comparison_found = False
    for node in ast.walk(functions[0]):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
            continue
        left, right = node.left, node.comparators[0]
        if (isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name)
                and left.value.id == "call" and isinstance(left.slice, ast.Constant)
                and left.slice.value == "pair" and isinstance(right, ast.Subscript)
                and isinstance(right.value, ast.Name) and right.value.id == "expected_pairs"
                and isinstance(right.slice, ast.Name) and right.slice.id == "s"):
            comparison_found = True
    need(comparison_found, "source pair assertion refers to actual parent calls")
    return pairs


def recipe_from_pairs(pairs):
    """Reconstruct the 19 logical events; then bind their full projection."""
    events = [{"kind": "local", "stage": 0, "pair": pairs[0], "reverse": False}]
    for j in range(4):
        events.append({"kind": "local", "stage": 2*j+1,
                       "pair": pairs[2*j+1], "reverse": True})
        if j < 3:
            events.append({"kind": "bridge", "src": j+1, "dst": j, "coefficient": 1})
        events.append({"kind": "local", "stage": 2*j+2,
                       "pair": pairs[2*j+2], "reverse": False})
        if j < 3:
            events.append({"kind": "bridge", "src": j+1, "dst": j, "coefficient": -1})
    for source in (2, 1, 0):
        events.append({"kind": "bridge", "src": source, "dst": source+1, "coefficient": 1})
    events.append({"kind": "terminal"})
    return events


def projection(event):
    if event["kind"] == "local":
        return {"kind": "local", "stage": event["stage"]}
    return dict(event)


def bind_recipe(recipe, pairs, witness):
    need(len(recipe) == 19, "nineteen logical events")
    locals_seen = [event for event in recipe if event["kind"] == "local"]
    need(len(locals_seen) == 9 and all(
        event == {"kind": "local", "stage": stage, "pair": pairs[stage],
                  "reverse": bool(stage % 2)}
        for stage, event in enumerate(locals_seen)), "local stage/pair/orientation binding")
    need(recipe[:2] == [
        {"kind": "local", "stage": 0, "pair": 0, "reverse": False},
        {"kind": "local", "stage": 1, "pair": 0, "reverse": True}], "initial local pair")
    expected = [{key: value for key, value in event.items() if key != "ordinary"}
                for event in witness["trajectory_after_B1"]]
    need([projection(event) for event in recipe[2:]] == expected,
         "all retained witness event identities")
    need(sum(event["kind"] == "bridge" for event in recipe) == 9,
         "nine ordinary bridges")


def replay(recipe, omit_canceling_bridge=False, classify_hole_as_completed=False):
    """Track integer multiples of a free vector g, never its query values.

    A local call is used only when its full source is provably zero. In
    the forward direction its target ordinary Y may be arbitrary. In the
    backward direction both selected registers are zero and the ordinary
    Y source must be zero. The literal conserved-map equations then imply
    zero new selected fields without any condition on B_s g.
    """
    x, y = [0] * 4, [1, 0, 0, 0]
    histories = {0: 0}  # supplied by the independently checked first pair
    trace, calls = [], []
    completed, endpoint_types = None, None
    skipped = False
    for event in recipe[2:]:
        kind = event["kind"]
        if (omit_canceling_bridge and not skipped
                and event == {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}):
            skipped = True
            continue
        if kind == "bridge":
            source, target, coefficient = event["src"], event["dst"], event["coefficient"]
            need(type(coefficient) is int and abs(coefficient) == 1, "signed unit bridge")
            x[target] += coefficient * x[source]
            y[source] -= coefficient * y[target]
        elif kind == "local":
            stage, pair = event["stage"], event["pair"]
            source_coefficient = y[pair] if event["reverse"] else x[pair]
            need(source_coefficient == 0,
                 "local source must vanish at stage " + str(stage))
            if event["reverse"]:
                # a = 0 from the zero selected X_T; future/current queries
                # are zero because the complete Y source is zero.
                x[pair] -= y[pair]
            else:
                # f = 0; the forward source output w is also zero.
                y[pair] += x[pair]
                histories[stage] = 0
            calls.append({"stage": stage, "pair": pair,
                          "orientation": "backward" if event["reverse"] else "forward",
                          "source_coefficient": source_coefficient})
        else:
            need(kind == "terminal", "tail event alphabet")
            completed = list(x)
            need(not any(completed), "all completed-X descendants vanish")
            x, y = list(y), [-coefficient for coefficient in x]
            endpoint_types = [["former_Y_hole", "completed_X_descendant"] for _ in range(4)]
            if classify_hole_as_completed:
                endpoint_types[0][0] = "completed_X_descendant"
            need(all(coefficient == 0
                     for pair in range(4)
                     for coefficient, tag in zip((x[pair], y[pair]), endpoint_types[pair])
                     if tag == "completed_X_descendant"),
                 "former-Y hole cannot be counted as completed-X")
        record = projection(event)
        record["ordinary"] = [coefficient for pair in zip(x, y) for coefficient in pair]
        trace.append(record)
    need(sorted(histories) == [0, 2, 4, 6, 8] and not any(histories.values()),
         "all five forward histories vanish")
    need(completed == [0] * 4 and endpoint_types is not None, "terminal observed")
    need(x == [1, 0, 0, 0] and y == [0] * 4, "sole final former-Y residue")
    return {"trajectory_after_B1": trace, "local_zero_source_checks": calls,
            "forward_histories": {str(stage): value for stage, value in sorted(histories.items())},
            "completed_X_coefficients": completed,
            "final_coefficients": [coefficient for pair in zip(x, y) for coefficient in pair],
            "final_type_classification": endpoint_types,
            "zero_selected_cuts_from_B1": len(trace) + 1}


def verify(root):
    """Return deterministic evidence; source-byte pins belong to the driver."""
    root = Path(root)
    for source in SOURCE_PATHS:
        need((root / source).is_file(), "missing tail source: " + source)
    witness = json.loads((root / WITNESS).read_text())
    # Record the inherited endpoint contract expressly, rather than inferring
    # the native type from the terminal field's current name.
    note = (root / WITNESS_NOTE).read_text()
    need("This is a former Y field with the phased native\noutput type." in note,
         "retained former-Y endpoint interpretation")
    pairs = source_pairs(root)
    recipe = recipe_from_pairs(pairs)
    bind_recipe(recipe, pairs, witness)
    result = replay(recipe)
    need(result["trajectory_after_B1"] == witness["trajectory_after_B1"],
         "complete retained witness trajectory")
    controls = []

    def reject(name, action, expected):
        try:
            action()
        except ValueError as error:
            need(str(error) == expected, "wrong tail rejection: " + name)
            controls.append({"mutation": name, "rejected_by": expected})
        else:
            raise ValueError("tail mutation accepted: " + name)

    reject("omit the first canceling negative bridge",
           lambda: replay(recipe, omit_canceling_bridge=True),
           "local source must vanish at stage 3")
    wrong_pair = deepcopy(recipe)
    next(event for event in wrong_pair if event.get("stage") == 2)["pair"] = 1
    reject("bind F2 to pair 1", lambda: bind_recipe(wrong_pair, pairs, witness),
           "local stage/pair/orientation binding")
    reject("classify the former-Y hole as completed-X",
           lambda: replay(recipe, classify_hole_as_completed=True),
           "former-Y hole cannot be counted as completed-X")
    # The F2 mutation has the SAME ordinary trace on this particular family:
    # both candidate X sources are zero. Its rejection is a source-binding
    # check, expressly not claimed as an algebraic separation.
    need(replay(wrong_pair)["trajectory_after_B1"] == result["trajectory_after_B1"],
         "wrong-F2 control is structural rather than a false trajectory claim")
    return {"status": "PASS_RETAINED_QQ16_TAIL", "logical_event_count": len(recipe),
            "post_B1_event_count": len(recipe) - 2, "stage_pairs": pairs,
            "recipe": recipe, "arbitrary_residue": "formal free ordinary vector g",
            "checks": result, "rejecting_controls": controls,
            "source_boundary": {
                "event_projection": WITNESS,
                "pair_vector_assertion": PAIR_SOURCE + ":schedule_audit.expected_pairs",
                "native_endpoint_interpretation": WITNESS_NOTE,
                "compressed_parent_template_replayed": False,
                "complete_native_word_or_type_validation": False}}


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parents[2]), sort_keys=True, indent=2))
