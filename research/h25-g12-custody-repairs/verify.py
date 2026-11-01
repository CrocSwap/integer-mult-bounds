"""Bounded source-function controls. No full target import or scientific entry.

The source functions selected below execute against synthetic descriptor/process
tokens. The retained allocation witnesses are EXPECTED REFUTATIONS of stronger
claims; a passing verifier does not grant integrated G12/P07 acceptance.
"""
import ast
import builtins
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROWS = []


def need(value, message):
    if not value:
        raise RuntimeError(message)


def check(name, predicate, classification="bounded-control"):
    need(predicate, "CONTROL FAILED: " + name)
    ROWS.append({"name": name, "classification": classification})


def capture(function):
    try:
        function()
    except BaseException as error:
        return error
    return None


def read_sources():
    manifest = json.loads((HERE / "SOURCE-IDENTITIES.json").read_text())
    sources = {}
    for row in manifest["files"]:
        raw = (HERE / row["path"]).read_bytes()
        check("source bytes " + row["path"], len(raw) == row["bytes"] and
              hashlib.sha256(raw).hexdigest() == row["sha256"], "byte-identity")
        sources[row["path"]] = ast.parse(raw.decode(), filename=row["path"])
    source_pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in source_pins["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            check("canonical input " + row["path"],
                  hashlib.sha256(raw).hexdigest() == row["sha256"], "byte-identity")
    return sources


def definition(tree, name):
    if "." in name:
        parent, child = name.split(".", 1)
        owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == parent)
        return next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == child)
    return next(n for n in tree.body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def execute_definitions(tree, names, extra=None):
    # Only the explicitly named definitions, not imports or module-level entries.
    body = [copy.deepcopy(definition(tree, name)) for name in names]
    env = {"__builtins__": builtins.__dict__, "__name__": "_g12_synthetic_controls",
           "_need": need, "sys": sys}
    if extra:
        env.update(extra)
    exec(compile(ast.fix_missing_locations(ast.Module(body=body, type_ignores=[])),
                 "<named G12 source functions / synthetic tokens>", "exec"), env)
    return env


def source_binding(sources):
    for kind, allowed in [
        ("parent", {"_directory_chain", "_read_file", "_KnownG12Chain",
                    "_exclusive_directory", "_copy_file", "run_g12_reference"}),
        ("cold_consumer", {"_directory_chain", "_read_file", "load_original_g12_reference"}),
    ]:
        old = sources["predecessor/g12_reference_" + kind + "_v2.py.txt"]
        new = sources["corrected/g12_reference_" + kind + "_v3.py"]
        def index(tree):
            return {getattr(n, "name", "item-" + str(i)): ast.dump(n, include_attributes=False)
                    for i, n in enumerate(tree.body)}
        a, b = index(old), index(new)
        changed = {k for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
        check("only declared " + kind + " definitions changed", changed == allowed,
              "complete-AST-delta")
        selections = {t.id: n.value for n in new.body if isinstance(n, ast.Assign)
                      for t in n.targets if isinstance(t, ast.Name)
                      and t.id in {"G12_REFERENCE_HANDOFF", "G12_REFERENCE_LAUNCH_SELECTION"}}
        check(kind + " selection remains closed", bool(selections) and
              all(isinstance(v, ast.Constant) and v.value is None for v in selections.values()),
              "closed-selection")

    # Apply the literal upstream-path diff IN MEMORY to the two retained sources.
    patch = (HERE / "repairs-from-pr6339.patch").read_text().splitlines(True)
    import re
    position = 0
    while position < len(patch):
        need(patch[position].startswith("--- a/"), "expected old patch path")
        name = Path(patch[position].split()[1]).name
        position += 1
        need(patch[position].startswith("+++ b/"), "expected new patch path")
        position += 1
        base = (HERE / "predecessor" / (name + ".txt")).read_text().splitlines(True)
        cursor, output = 0, []
        while position < len(patch) and not patch[position].startswith("--- a/"):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", patch[position])
            need(match is not None, "malformed patch hunk")
            first = int(match.group(1)) - 1
            need(first >= cursor, "overlapping patch hunk")
            output.extend(base[cursor:first])
            cursor = first
            position += 1
            while position < len(patch) and not patch[position].startswith(("@@ ", "--- a/")):
                line = patch[position]
                position += 1
                need(line[:1] in (" ", "+", "-"), "unsupported patch line")
                if line[0] in " -":
                    need(cursor < len(base) and base[cursor] == line[1:], "patch base mismatch")
                    cursor += 1
                if line[0] in " +":
                    output.append(line[1:])
        output.extend(base[cursor:])
        target = (HERE / "corrected" / name.replace("_v2.py", "_v3.py")).read_text()
        check("exact in-memory diff " + name, "".join(output) == target, "complete-byte-delta")


def allocation_controls(tree, kind, version):
    names = ["_directory_chain", "_read_file"]
    if kind == "parent":
        names += ["_exclusive_directory", "_copy_file"]
    else:
        names += ["load_original_g12_reference"]
    for name in names:
        acquired, closed = [], []
        primary = RuntimeError("synthetic original body failure")
        allocation = MemoryError("injected raw-ledger allocation failure")

        def allocate():
            raise allocation

        def opened(*args, **kwargs):
            acquired.append(901)
            return 901

        def directory(*args, **kwargs):
            acquired.append(902)
            return [902], []

        def denied(*args, **kwargs):
            raise primary

        fake_os = SimpleNamespace(open=opened, close=closed.append, stat=denied,
                                  O_RDONLY=0, O_DIRECTORY=0, O_CLOEXEC=0,
                                  O_NOFOLLOW=0, O_WRONLY=0, O_CREAT=0, O_EXCL=0)
        extra = {"_RawG12Errors": allocate, "_path": lambda p: p, "os": fake_os,
                 "_directory_chain": directory}
        if name == "load_original_g12_reference":
            # Isolate the actual two allocation/acquisition statements at the
            # retained-directory boundary, not the genuine Root-authentication entry.
            node = definition(tree, name)
            statements = []
            for statement in node.body:
                if isinstance(statement, ast.Assign):
                    ids = [n.id for n in ast.walk(statement.targets[0])
                           if isinstance(n, ast.Name)]
                    if "dirs" in ids or {"primary", "secondaries", "result"} <= set(ids):
                        statements.append(copy.deepcopy(statement))
            need(len(statements) == 2, "consumer allocation-window source changed")
            env = {"__builtins__": builtins.__dict__, "_RawG12Errors": allocate,
                   "_directory_chain": directory, "retained": "/synthetic/retained"}
            unit = compile(ast.fix_missing_locations(ast.Module(body=statements,
                                                               type_ignores=[])),
                           "<actual consumer allocation window>", "exec")
            error = capture(lambda: exec(unit, env))
        else:
            env = execute_definitions(tree, [name], extra)
            args = (([900], []), "new", b"x") if name == "_copy_file" else (
                ("/synthetic/file", 10) if name == "_read_file" else ("/synthetic",))
            error = capture(lambda: env[name](*args))
        expected_acquisitions = 1 if version == "predecessor" else 0
        check(kind + "/" + name + "/" + version + " ledger-failure boundary",
              error is allocation and len(acquired) == expected_acquisitions and not closed,
              "source-function-fault-injection")


def cleanup_controls(parent):
    closes = []
    first_close = OSError("synthetic close failure")
    late_close = OSError("synthetic later close failure")
    errors = {903: first_close, 901: late_close}

    def close(fd):
        closes.append(fd)
        if fd in errors:
            raise errors[fd]

    env = execute_definitions(
        parent, ["_RawG12Errors", "_close_known_descriptors", "_finally_close_known"],
        {"os": SimpleNamespace(close=close)})
    primary = ValueError("synthetic body primary")
    secondaries = env["_RawG12Errors"]()

    def failing_body():
        try:
            raise primary
        finally:
            env["_finally_close_known"]([901, 902, 903], secondaries)
    actual = capture(failing_body)
    check("ordinary preflight keeps same primary and attempts all known closes",
          actual is primary and closes == [903, 902, 901] and
          [item[0] for item in secondaries] == [first_close, late_close],
          "source-function-positive-control")

    closes.clear()
    secondaries = env["_RawG12Errors"]()
    actual = capture(lambda: env["_finally_close_known"]([901, 902, 903], secondaries))
    check("successful body promotes first close failure once",
          actual is first_close and closes == [903, 902, 901] and
          [item[0] for item in secondaries] == [late_close],
          "source-function-positive-control")

    # Deliberately retain the still-failing stronger contract as a red witness.
    for fault in ["ledger", "snapshot", "record"]:
        closes.clear()
        allocation = MemoryError("retained " + fault + " failure witness")
        env = execute_definitions(
            parent, ["_RawG12Errors", "_close_known_descriptors", "_finally_close_known"],
            {"os": SimpleNamespace(close=close)})
        if fault == "ledger":
            def bad_ledger():
                raise allocation
            env["_RawG12Errors"] = bad_ledger
        elif fault == "snapshot":
            def bad_snapshot(values):
                raise allocation
            env["tuple"] = bad_snapshot
        else:
            class BadRecorder:
                def append(self, value):
                    raise allocation
            env["_RawG12Errors"] = BadRecorder
        secondaries = []
        def witness():
            try:
                raise primary
            finally:
                env["_finally_close_known"]([901, 902, 903], secondaries)
        actual = capture(witness)
        check("UNRESOLVED preflight " + fault + " masks primary/skips later closes",
              actual is allocation and actual is not primary and
              closes == ([903] if fault == "record" else []),
              "retained-contract-counterexample")


def pidfd_controls(old, new):
    release = execute_definitions(new, ["_KnownG12Chain.release_known_pidfds"])
    for failures in [set(), {901}, {901, 902}]:
        attempts, errors = [], {}
        chain = SimpleNamespace(fds={(1, 11): 901, (2, 12): 902},
                                unknown=False, closed=False)
        def close(fd):
            need(fd not in chain.fds.values(), "numeric owner was not retired before close")
            attempts.append(fd)
            if fd in failures:
                errors[fd] = OSError("synthetic ambiguous close")
                raise errors[fd]
        release["os"] = SimpleNamespace(close=close)
        secondaries = []
        release["release_known_pidfds"](chain, secondaries)
        check("pidfd release attempts all/retains raw failures " + str(sorted(failures)),
              attempts == [901, 902] and not chain.fds and
              chain.unknown == bool(failures) and chain.closed is False and
              [item[0] for item in secondaries] == [errors[fd] for fd in [901, 902]
                                                  if fd in failures],
              "source-function-positive-control")
        release["release_known_pidfds"](chain, secondaries)
        check("ambiguous pidfd close is never blindly retried " + str(sorted(failures)),
              attempts == [901, 902], "source-function-negative-control")

    for tree, label in [(old, "predecessor"), (new, "corrected")]:
        attempts, secondaries = [], []
        denial = PermissionError("persistent synthetic process-observation denial")
        chain = SimpleNamespace(fds={(1, 11): 901, (2, 12): 902},
                                unknown=False, closed=False)
        def denied_finish(*args):
            raise denial
        chain.finish = denied_finish
        rel_env = execute_definitions(new, ["_KnownG12Chain.release_known_pidfds"],
                                      {"os": SimpleNamespace(close=attempts.append)})
        chain.release_known_pidfds = lambda journal: rel_env["release_known_pidfds"](chain, journal)
        owner = definition(tree, "run_g12_reference")
        nested = next(n for n in owner.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_g12_finish_failure")
        nested = copy.deepcopy(nested)
        nested.body = [n for n in nested.body if not isinstance(n, ast.Nonlocal)]
        namespace = {"__builtins__": builtins.__dict__, "chain": chain,
                     "selection": {"body_deadline_ns": 1, "retention_tail_allowance_ns": 1},
                     "process": None, "secondaries": secondaries, "outer": {}, "reserved": {},
                     "lease": None, "lease_closed": False, "observation": None,
                     "science_directory": None, "run_directory": None, "retained": None,
                     "os": SimpleNamespace(close=attempts.append)}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[nested], type_ignores=[])),
                     "<actual P09 source / synthetic denied process>", "exec"), namespace)
        namespace["_g12_finish_failure"]()
        expected = [] if label == "predecessor" else [901, 902]
        check("actual P09 persistent-denial pidfd cleanup " + label,
              attempts == expected and secondaries[0][0] is denial and
              (label == "predecessor" or (not chain.fds and chain.unknown and
                                         chain.closed is False)),
              "source-function-regression-control")


def publication_size_controls(old, new):
    for tree, label in [(old, "predecessor"), (new, "corrected")]:
        fn = definition(tree, "load_original_g12_reference")
        size_gate = [copy.deepcopy(n) for n in fn.body if isinstance(n, ast.Expr)
                     and isinstance(n.value, ast.Call)
                     and isinstance(n.value.func, ast.Name) and n.value.func.id == "_uint"
                     and n.value.args and isinstance(n.value.args[0], ast.Name)
                     and n.value.args[0].id == "publication_size"]
        comparison = next(n for n in ast.walk(fn) if isinstance(n, ast.Expr)
                          and isinstance(n.value, ast.Call) and
                          any(isinstance(a, ast.Constant) and
                              a.value == "G12-N15: source-selected final publication bytes"
                              for a in n.value.args))
        code = compile(ast.fix_missing_locations(ast.Module(
            body=size_gate + [copy.deepcopy(comparison)], type_ignores=[])),
            "<actual publication domain gate>", "exec")
        class ForeignInt(int):
            pass
        for value, observed, accepted in [(1234, 1234, True), (0, 0, True),
                                         (1234.0, 1234, False), (True, 1, False),
                                         (ForeignInt(1234), 1234, False),
                                         ("1234", 1234, False), (-1, 1234, False)]:
            env = execute_definitions(tree, ["_uint"])
            env.update({"publication_size": value, "publication_sha": "digest",
                        "publication_record": {"sha256": "digest", "bytes": observed}})
            error = capture(lambda: exec(code, env))
            old_accepts = observed == value
            check("publication exact-size " + label + "/" + type(value).__name__ + "/" + repr(value),
                  (error is None) == (old_accepts if label == "predecessor" else accepted),
                  "actual-source-schema-control")


def main():
    sources = read_sources()
    source_binding(sources)
    for kind in ["parent", "cold_consumer"]:
        allocation_controls(sources["predecessor/g12_reference_" + kind + "_v2.py.txt"],
                            kind, "predecessor")
        allocation_controls(sources["corrected/g12_reference_" + kind + "_v3.py"],
                            kind, "corrected")
    parent = sources["corrected/g12_reference_parent_v3.py"]
    cleanup_controls(parent)
    pidfd_controls(sources["predecessor/g12_reference_parent_v2.py.txt"], parent)
    publication_size_controls(sources["predecessor/g12_reference_cold_consumer_v2.py.txt"],
                              sources["corrected/g12_reference_cold_consumer_v3.py"])
    need(len({row['name'] for row in ROWS}) == len(ROWS), "duplicate check identity")
    cases = sum(row['classification'].startswith(('source-function-', 'actual-source-'))
                or row['classification'] == 'retained-contract-counterexample' for row in ROWS)
    report = {"schema": "h25-g12-bounded-source-controls-v1",
              "status": "PARTIAL_SOURCE_REPAIR_WITH_RETAINED_COUNTEREXAMPLES",
              "checks_total": len(ROWS), "source_function_cases": cases,
              "metadata_checks": len(ROWS) - cases, "checks": ROWS,
              "executed_scope": "Named AST-extracted source functions/windows with synthetic tokens",
              "full_target_module_imports": 0, "original_H25_scientific_invocations": 0,
              "native_or_process_operations": 0, "author_verifier_replayed": False,
              "integrated_source_acceptance": False, "N22_P07_body_credit": False,
              "performance_or_kappa": False, "unknown_costs": "OPEN_NOT_ZERO",
              "environment": {"python": sys.version, "optimize": sys.flags.optimize}}
    print(json.dumps(report, sort_keys=True))
    print("PASS_G12_BOUNDED_SOURCE_REPAIRS source_cases=" + str(cases) +
          " metadata_checks=" + str(len(ROWS) - cases) +
          " unresolved_preflight_allocation=3 no_integrated_acceptance")


if __name__ == "__main__":
    main()
