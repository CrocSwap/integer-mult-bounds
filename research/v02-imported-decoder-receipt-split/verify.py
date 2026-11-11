#!/usr/bin/env python3
"""Reconcile the imported-decoder receipts on one V02 child digest.

The child is parsed with ast and never imported. A passing run shows that an
identity replacement of a snapshotted json.loads binding during the first fd0
read cannot reach three json.loads calls and phase SEALED on these bytes.
It is not a harness replay, a parent join, or a selected-frontier change.
"""

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
INPUTS = PACKAGE / "inputs"
UPSTREAM = "b5587eef1dd66d477a2e4d7b6f83616e07a01386"

CHILD_SHA = "7001e2ba395ebb7e943816301be7830e6a9bb699acc182e2bbeb786148459048"
INTERMEDIATE_SHA = "1ae26dddbdd917481e5972b4b98eca21a48733eefd04f1585741b7583b42f807"
INGRESS_SHA = "bd74779a39172a77185bf118faccf4a6804ae97fd7c6e0de2ce27ce33d47f4bb"
REVIEW_SHA = "6db9bd22e5e34eef213d0f4e29553713a58de16680618566dabdf6a01b29e35c"

IMPORT_ALIAS = "V02 preseal retained import alias changed"
HELPER_ALIAS = "V02 preseal retained helper alias changed"
DESCRIPTOR = "V02 preseal retained helper descriptor changed"
ALIAS_MUTATION = "json.loads alias replaced during first fd0 read"

UPSTREAM_PATHS = {
    "selected_child_preseal_v1.py.txt":
        "research/h25-v02-parent-custody-evidence/snapshots/"
        "trusted-preseal-ingress/selected_child_preseal_v1.py.txt",
    "INTERMEDIATE-7001e2ba.json":
        "research/h25-v02-parent-custody-evidence/snapshots/"
        "trusted-preseal-ingress/review/INTERMEDIATE-7001e2ba.json",
    "INGRESS-INDEPENDENT.json":
        "research/h25-v02-parent-custody-evidence/snapshots/"
        "trusted-preseal-ingress/review/INGRESS-INDEPENDENT.json",
    "REVIEW-final.json":
        "research/h25-v02-parent-custody-evidence/snapshots/"
        "trusted-preseal-ingress/review/REVIEW-final.json",
}


def fail(message):
    raise SystemExit("FAIL_V02_IMPORTED_DECODER_RECEIPT_SPLIT: " + message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_bytes(name):
    return (INPUTS / name).read_bytes()


def call_name(node):
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id + "." + func.attr
    return None


def calls_in(node):
    found = []

    def walk(current):
        for child in ast.iter_child_nodes(current):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(child, ast.Call):
                found.append(child)
            walk(child)

    walk(node)
    return found


def top_function(tree, name):
    found = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(found) != 1:
        fail("expected one top-level function " + name + ", found " + str(len(found)))
    return found[0]


def nested_function(fn, name):
    found = [
        node for node in ast.walk(fn)
        if isinstance(node, ast.FunctionDef) and node.name == name and node is not fn
    ]
    if len(found) != 1:
        fail("expected one nested function " + name + " in " + fn.name + ", found " + str(len(found)))
    return found[0]


def sole_try(fn):
    found = [node for node in fn.body if isinstance(node, ast.Try)]
    if len(found) != 1 or len(found[0].handlers) != 1:
        fail(fn.name + " needs one try with one handler")
    return found[0]


def ancestors(root, node):
    parents = {}
    for current in ast.walk(root):
        for child in ast.iter_child_nodes(current):
            parents[id(child)] = current
    chain = []
    while id(node) in parents:
        node = parents[id(node)]
        chain.append(node)
    return chain


def gated_by_import_flag(root, node):
    for parent in ancestors(root, node):
        test = parent.test if isinstance(parent, (ast.If, ast.IfExp)) else None
        if isinstance(test, ast.Name) and test.id == "include_import_functions":
            return True
    return False


def binding_base(test):
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or not isinstance(test.ops[0], ast.IsNot):
        return None
    if len(test.comparators) != 1 or not isinstance(test.comparators[0], ast.Name):
        return None
    if test.comparators[0].id != "value":
        return None
    left = test.left
    if not isinstance(left, ast.Subscript) or not isinstance(left.value, ast.Name):
        return None
    if not isinstance(left.slice, ast.Name) or left.slice.id != "key":
        return None
    return left.value.id


def raise_message(stmt):
    if not isinstance(stmt, ast.Raise) or not isinstance(stmt.exc, ast.Call):
        return None
    call = stmt.exc
    if not isinstance(call.func, ast.Name) or call.func.id != "error0" or len(call.args) != 1:
        return None
    if not isinstance(call.args[0], ast.Constant) or not isinstance(call.args[0].value, str):
        return None
    return call.args[0].value


def for_iter_name(node):
    if isinstance(node, ast.For) and isinstance(node.iter, ast.Name):
        return node.iter.id
    return None


def identity_checks(fn):
    found = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.If) or len(node.body) != 1:
            continue
        message = raise_message(node.body[0])
        base = binding_base(node.test)
        if message is None or base is None:
            continue
        iters = [for_iter_name(parent) for parent in ancestors(fn, node)]
        found.append({
            "message": message,
            "base": base,
            "iters": [name for name in iters if name],
            "gated": gated_by_import_flag(fn, node),
        })
    return found


def import_descriptors_deferred(fn):
    assignment = None
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != "records":
            continue
        value = node.value
        if not isinstance(value, ast.IfExp) or not isinstance(value.test, ast.Name):
            continue
        if value.test.id != "include_import_functions":
            continue
        added = value.body
        if not isinstance(added, ast.BinOp) or not isinstance(added.op, ast.Add):
            continue
        if not isinstance(added.left, ast.Name) or added.left.id != "functions0":
            continue
        if not isinstance(added.right, ast.Name) or added.right.id != "import_functions0":
            continue
        if not isinstance(value.orelse, ast.Name) or value.orelse.id != "functions0":
            continue
        assignment = node
    if assignment is None:
        return False
    for node in ast.walk(fn):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == "records":
            messages = [raise_message(item) for item in ast.walk(node) if isinstance(item, ast.Raise)]
            if DESCRIPTOR in messages:
                return True
    return False


def flag_default_false(fn):
    args = fn.args
    if [arg.arg for arg in args.args] != ["include_import_functions"] or args.kwonlyargs or args.vararg or args.kwarg:
        return False
    if len(args.defaults) != 1 or not isinstance(args.defaults[0], ast.Constant):
        return False
    return args.defaults[0].value is False


def is_read_one(call):
    if call_name(call) != "_READ" or len(call.args) != 2:
        return False
    count, size = call.args
    return (isinstance(count, ast.Constant) and count.value == 0
            and isinstance(size, ast.Constant) and size.value == 1)


def is_plain_recheck(call):
    return call_name(call) == "source_recheck" and call.args == [] and call.keywords == []


def is_true_recheck(call):
    return (call_name(call) == "source_recheck" and call.keywords == [] and len(call.args) == 1
            and isinstance(call.args[0], ast.Constant) and call.args[0].value is True)


def is_document(call):
    return call_name(call) == "_document"


def read_loop_events(loop):
    events = []
    for stmt in list(loop.body) + list(loop.orelse):
        for call in calls_in(stmt):
            if is_read_one(call):
                events.append("read")
            elif is_plain_recheck(call):
                events.append("recheck")
            elif is_document(call):
                events.append("document")
    return events


def recheck_follows_read(events):
    seen_read = False
    for event in events:
        if event == "read":
            seen_read = True
        elif event == "recheck" and seen_read:
            return True
    return False


def receive_labels(try_node):
    labels = []
    for stmt in try_node.body:
        calls = calls_in(stmt)
        if isinstance(stmt, ast.While):
            labels.append("while")
        elif any(is_true_recheck(call) for call in calls):
            labels.append("true")
        elif any(is_document(call) for call in calls):
            labels.append("document")
    return labels


def phase_values(node):
    values = []
    if isinstance(node, ast.Assign):
        nodes = [node]
    else:
        nodes = [item for item in ast.walk(node) if isinstance(item, ast.Assign)]
    for item in nodes:
        for target in item.targets:
            if not isinstance(target, ast.Subscript) or not isinstance(target.slice, ast.Constant):
                continue
            if target.slice.value != "phase" or not isinstance(item.value, ast.Constant):
                continue
            if isinstance(item.value.value, str):
                values.append(item.value.value)
    return values


def handler_stops(try_node):
    handler = try_node.handlers[0]
    if not isinstance(handler.type, ast.Name) or handler.type.id != "BaseException":
        return False
    values = []
    for stmt in handler.body:
        values.extend(phase_values(stmt))
    reraises = any(isinstance(stmt, ast.Raise) for stmt in handler.body)
    return "STOP" in values and "SEALED" not in values and reraises


def install_events(try_node):
    events = []

    def walk(current):
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(current, ast.Call):
            name = call_name(current)
            if name in {"_receive_v02_preseal", "_construct_v02_issued_input", "_register_v02_live"}:
                events.append(name)
        if isinstance(current, ast.Assign):
            events.extend("phase:" + value for value in phase_values(current))
        for child in ast.iter_child_nodes(current):
            walk(child)

    for stmt in try_node.body:
        walk(stmt)
    return events


def has_order(events, names):
    cursor = 0
    for name in names:
        while cursor < len(events) and events[cursor] != name:
            cursor += 1
        if cursor == len(events):
            return False
        cursor += 1
    return True


def loads_sites(tree):
    sites = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            sites.extend(node.name for call in calls_in(node) if call_name(call) == "json.loads")
    return sites


def structural_facts(source):
    tree = ast.parse(source)
    if not any(isinstance(node, ast.Import) and any(alias.name == "json" and alias.asname is None for alias in node.names)
               for node in tree.body):
        fail("child does not import json")
    receive = top_function(tree, "_receive_v02_preseal")
    install = top_function(tree, "install_before_capture")
    construct = top_function(tree, "_construct_v02_issued_input")
    register = top_function(tree, "_register_v02_live")
    checker = nested_function(receive, "source_recheck")
    checks = identity_checks(checker)
    receive_try = sole_try(receive)
    install_try = sole_try(install)
    loops = [stmt for stmt in receive_try.body if isinstance(stmt, ast.While)]
    if len(loops) != 1:
        fail("expected one read loop in _receive_v02_preseal, found " + str(len(loops)))
    events = read_loop_events(loops[0])
    labels = receive_labels(receive_try)
    installed = install_events(install_try)
    sites = loads_sites(tree)
    document_calls = {
        "_receive_v02_preseal": sum(is_document(call) for call in calls_in(receive)),
        "_construct_v02_issued_input": sum(is_document(call) for call in calls_in(construct)),
        "_register_v02_live": sum(is_document(call) for call in calls_in(register)),
    }
    return {
        "import_alias_unconditional": any(
            item["message"] == IMPORT_ALIAS and item["base"] == "namespace"
            and "imports0" in item["iters"] and "items" in item["iters"] and not item["gated"]
            for item in checks
        ),
        "helper_alias_unconditional": any(
            item["message"] == HELPER_ALIAS and item["base"] == "namespace0"
            and "items0" in item["iters"] and not item["gated"]
            for item in checks
        ),
        "recheck_after_first_read": recheck_follows_read(events),
        "no_document_in_read_loop": "document" not in events,
        "true_recheck_before_document": (
            "while" in labels and "true" in labels and "document" in labels
            and labels.index("while") < labels.index("true") < labels.index("document")
        ),
        "receive_document_calls": document_calls["_receive_v02_preseal"],
        "construct_document_calls": document_calls["_construct_v02_issued_input"],
        "register_document_calls": document_calls["_register_v02_live"],
        "receive_handler_stops_and_reraises": handler_stops(receive_try),
        "install_handler_stops_and_reraises": handler_stops(install_try),
        "sealed_after_receive": has_order(installed, [
            "_receive_v02_preseal",
            "_construct_v02_issued_input",
            "_register_v02_live",
            "phase:SEALED",
        ]) and installed.index("phase:SEALED") > installed.index("_receive_v02_preseal"),
        "loads_only_in_document": sites == ["_document"],
        "import_descriptors_deferred": import_descriptors_deferred(checker) and flag_default_false(checker),
    }


def identity_cannot_seal(facts):
    required = (
        "import_alias_unconditional",
        "helper_alias_unconditional",
        "recheck_after_first_read",
        "no_document_in_read_loop",
        "true_recheck_before_document",
        "receive_handler_stops_and_reraises",
        "install_handler_stops_and_reraises",
        "sealed_after_receive",
        "loads_only_in_document",
    )
    return all(facts[name] for name in required)


def require_published_structure(facts):
    if not identity_cannot_seal(facts):
        fail("published child does not obstruct SEALED for an identity replacement during the first read: "
             + json.dumps(facts, sort_keys=True))
    if (facts["receive_document_calls"], facts["construct_document_calls"], facts["register_document_calls"]) != (2, 1, 0):
        fail("success-path _document counts differ from 2, 1, 0")
    if not facts["import_descriptors_deferred"]:
        fail("imported function descriptors are checked on the per-byte recheck")


def claims_sealed_identity_mutation(receipt):
    remaining = receipt.get("remaining_counterexample")
    if not isinstance(remaining, dict):
        return False
    return (receipt.get("source_sha256") == CHILD_SHA
            and remaining.get("mutation") == ALIAS_MUTATION
            and remaining.get("foreign_callbacks") == 3
            and remaining.get("final_phase") == "SEALED")


def case_row(document, name):
    rows = [row for row in document["tests"] if row.get("case") == name]
    if len(rows) != 1:
        fail("expected one ingress case " + name)
    return rows[0]


def require_receipts(intermediate, ingress, review, ingress_bytes):
    if intermediate.get("status") != "REQUIRES_IMPORTED_DECODER_RECONCILIATION":
        fail("intermediate status changed")
    if intermediate.get("actual_fd0_calls") != 0 or intermediate.get("actual_original_executions") != 0:
        fail("intermediate actual-execution counters changed")
    if not claims_sealed_identity_mutation(intermediate):
        fail("intermediate receipt no longer claims three callbacks and SEALED for the identity mutation")
    alias = case_row(ingress, "imported_decoder_alias_after_read")
    imported_code = case_row(ingress, "imported_decoder_code_after_read")
    helper_alias = case_row(ingress, "decoder_alias_after_read")
    helper_code = case_row(ingress, "decoder_code_after_read")
    expected = (
        (alias, IMPORT_ALIAS, 1),
        (imported_code, DESCRIPTOR, 1111),
        (helper_alias, HELPER_ALIAS, 1),
        (helper_code, DESCRIPTOR, 1),
    )
    for row, message, reads in expected:
        if row.get("result") != "PASS_INERT_ONLY" or row.get("message") != message or row.get("fd0_model_reads") != reads:
            fail("ingress case disagrees with the published refusal: " + row.get("case", ""))
    if ingress.get("candidate_sha256") != CHILD_SHA:
        fail("ingress receipt names a different child")
    recorded_ingress = (review.get("files") or {}).get("INGRESS-INDEPENDENT.json") or {}
    if recorded_ingress.get("sha256") != sha256(ingress_bytes) or recorded_ingress.get("bytes") != len(ingress_bytes):
        fail("final review's ingress digest does not match the vendored ingress receipt")
    if ingress.get("actual_fd0_calls") != 0 or ingress.get("actual_original_executions") != 0:
        fail("ingress actual-execution counters changed")
    if ingress.get("actual_origin_authenticated") is not False or ingress.get("original_activity_credit") != 0:
        fail("ingress receipt claims origin authentication or activity credit")
    pins = review.get("source_pins") or {}
    if pins.get("selected_child_preseal_v1.py.txt") != CHILD_SHA:
        fail("final review pins a different child")
    if review.get("status") != "ACCEPT_PROSPECTIVE_CONDITIONAL_SOURCE_ONLY":
        fail("final review status changed")
    for name, expected_value in (
        ("operational_channel_accepted", False),
        ("protected_origin_authenticated", False),
        ("real_live_profile_tested", False),
        ("actual_fd0_or_tool_calls", 0),
        ("original_omission_cases", 0),
        ("original_activity_credit", 0),
    ):
        if review.get(name) != expected_value:
            fail("final review field " + name + " is not the published negative")
    harness = (review.get("files") or {}).get("test_ingress_independent.py") or {}
    if harness.get("sha256") != "52d6b54ee6c465a00d6bc4d0a5ccf4271376651a061246cf293d7a5dce0a429b" or harness.get("bytes") != 4450:
        fail("final review no longer records the absent ingress harness digest")


def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        fail("mutation anchor " + label + " occurs " + str(count) + " times")
    return source.replace(old, new, 1)


def mutation_controls(source, intermediate):
    removed_alias = replace_once(
        source,
        "                for key,value in items:\n"
        "                    if namespace[key] is not value:\n"
        "                        raise error0('V02 preseal retained import alias changed')\n",
        "",
        "import-alias check",
    )
    removed_recheck = replace_once(
        source,
        "            part=_READ(0,1)\n            source_recheck()\n",
        "            part=_READ(0,1)\n",
        "post-read recheck",
    )
    sealed_on_error = replace_once(
        source,
        "        state['owner']['quarantine'][0] = True\n"
        "        if state['primary'][0] is None:\n"
        "            state['primary'][0] = error\n"
        "        state['phase'] = 'STOP'\n"
        "        raise\n",
        "        state['owner']['quarantine'][0] = True\n"
        "        if state['primary'][0] is None:\n"
        "            state['primary'][0] = error\n"
        "        state['phase'] = 'SEALED'\n"
        "        raise\n",
        "install error phase",
    )
    eager_descriptors = replace_once(
        source,
        "records = functions0 + import_functions0 if include_import_functions else functions0",
        "records = functions0 + import_functions0",
        "descriptor gate",
    )
    quiet = json.loads(json.dumps(intermediate))
    quiet["remaining_counterexample"]["foreign_callbacks"] = 0
    controls = (
        ("delete import-alias check", removed_alias, False),
        ("delete post-read recheck", removed_recheck, False),
        ("seal in the install handler", sealed_on_error, False),
        ("check import descriptors on every recheck", eager_descriptors, True),
    )
    for label, mutant, still_blocked in controls:
        facts = structural_facts(mutant)
        if identity_cannot_seal(facts) != still_blocked:
            fail("mutant did not flip the identity obstruction as required: " + label)
        if label.startswith("check import") and facts["import_descriptors_deferred"]:
            fail("descriptor mutant still defers the import descriptor check")
    if claims_sealed_identity_mutation(quiet):
        fail("callback mutant still claims the conflicting outcome")
    return len(controls) + 1


def compare_upstream(blobs):
    probe = subprocess.run(
        ["git", "cat-file", "-e", UPSTREAM + "^{commit}"],
        cwd=REPO, capture_output=True,
    )
    if probe.returncode != 0:
        return 0, len(blobs)
    for name, data in blobs.items():
        show = subprocess.run(
            ["git", "cat-file", "blob", UPSTREAM + ":" + UPSTREAM_PATHS[name]],
            cwd=REPO, capture_output=True,
        )
        if show.returncode != 0:
            fail("upstream commit is present but " + UPSTREAM_PATHS[name] + " is not")
        if show.stdout != data:
            fail("vendored bytes differ from " + UPSTREAM_PATHS[name])
    return len(blobs), 0


def main():
    blobs = {
        name: load_bytes(name)
        for name in (
            "selected_child_preseal_v1.py.txt",
            "INTERMEDIATE-7001e2ba.json",
            "INGRESS-INDEPENDENT.json",
            "REVIEW-final.json",
        )
    }
    expected = {
        "selected_child_preseal_v1.py.txt": CHILD_SHA,
        "INTERMEDIATE-7001e2ba.json": INTERMEDIATE_SHA,
        "INGRESS-INDEPENDENT.json": INGRESS_SHA,
        "REVIEW-final.json": REVIEW_SHA,
    }
    for name, digest in expected.items():
        if sha256(blobs[name]) != digest:
            fail("pin mismatch: " + name)
    source = blobs["selected_child_preseal_v1.py.txt"].decode()
    intermediate = json.loads(blobs["INTERMEDIATE-7001e2ba.json"].decode())
    ingress = json.loads(blobs["INGRESS-INDEPENDENT.json"].decode())
    review = json.loads(blobs["REVIEW-final.json"].decode())
    facts = structural_facts(source)
    require_published_structure(facts)
    require_receipts(intermediate, ingress, review, blobs["INGRESS-INDEPENDENT.json"])
    mutations = mutation_controls(source, intermediate)
    compared, absent = compare_upstream(blobs)
    if compared != 4 and absent != 4:
        fail("upstream comparison was neither complete nor wholly absent")
    print("PASS_V02_IMPORTED_DECODER_RECEIPT_SPLIT")
    print("child_sha256=" + CHILD_SHA)
    print("identity_replacement_during_first_read_can_seal=false")
    print("success_path_document_calls=3")
    print("import_descriptor_check_deferred=true")
    print("ingress_imported_alias_reads=1")
    print("ingress_imported_code_reads=1111")
    print("intermediate_foreign_callbacks=3")
    print("intermediate_final_phase=SEALED")
    print("protected_origin_authenticated=false")
    print("original_omission_cases=0")
    print("mutation_controls=" + str(mutations))
    print("upstream_blobs_compared=" + str(compared))
    print("upstream_blobs_absent=" + str(absent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
