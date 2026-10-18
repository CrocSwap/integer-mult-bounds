#!/usr/bin/env python3
"""Defect-sensitive mathematical and source-integrity controls; Apache-2.0."""
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
v = types.ModuleType("validation_verifier")
v.__file__ = str(ROOT / "verify.py")
exec(compile((ROOT / "verify.py").read_bytes(), v.__file__, "exec"), v.__dict__)


def rejects(fn, message):
    try:
        fn()
    except ValueError as error:
        v.need(message in str(error), "wrong rejecting obligation: " + str(error))
        return
    raise ValueError("unexpected acceptance: " + message)


def semantic_controls(m):
    good = (0, 1, 1, 0, 0, 0)
    half = (2, 2, 1, 0, 0, 1)
    for args, bounds in [({}, (11, 15)), ({}, (12, 9)),
                         ({"events": (good,)}, (12, 13)),
                         ({"events": (half,)}, (12, 14))]:
        rejects(lambda: v.run_callback(m, bounds=bounds, **args), "numerical lifetime budget")
    # Caller-space control is small: no full directory is needed to reject
    # dropping one of the eight persistent caller words from the composition.
    case = v.fixture(m, events=(half,))
    resident = [case.indices.zero() for _ in range(8)]
    baseline = len(case.indices.live)-8
    original = m.words.Arena.zero
    def budget(arena):
        result = original(arena)
        if arena is case.indices:
            v.need(len(arena.live)-baseline <= 22, "composed index allowance")
        return result
    with patch.object(m.words.Arena, "zero", budget):
        rejects(lambda: m.controller.Callback(case.ring, case.indices, case.program, case.fields,
                                              case.specifications, 0, allow_fallback=True),
                "composed index allowance")
    case.indices.free_many(*resident)

    # Constructor's own ValueError rollback is checked before fixture disposal.
    for defect in ("code", "nonunit", "chronology"):
        case = v.fixture(m, events=(good,))
        if defect == "code":
            high = [[0]*64 for _ in range(64)]
            case.fields = m.records.Fields.fixture(case.indices, case.residues,
                                                    [(0, high), (0, high)], code_bits=8)
            expected = "original global raw-field code"
        elif defect == "nonunit":
            case.program = m.records.Program.fixture(case.indices, case.residues,
                                                      case.root, 0, case.events, code_bits=8)
            expected = "root coefficient unit"
        else:
            # Give the first STEP a wrong parent, preserving all delimiters.
            level = case.indices.literal(1)
            m.records.seek_record(case.program.tape, level)
            case.program.tape.step(1)
            for j in range(6):
                m.records.read_finite(case.program.tape, 8 if j == 1 else m.records.FINITE_BITS)
            case.program.tape.write(m.words.ONE)
            case.program.tape.rewind()
            case.indices.free(level)
            expected = "chronological program extents"
        saved = tuple(v.saved_arena(a) for a in (case.residues, case.indices))
        tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
        rejects(lambda: m.controller.Callback(case.ring, case.indices, case.program, case.fields,
                                              case.specifications, 0, allow_fallback=True), expected)
        v.need(saved == tuple(v.saved_arena(a) for a in (case.residues, case.indices)),
               "constructor rollback before teardown")
        v.need(tapes == (bytes(case.program.tape.cells), bytes(case.fields.tape.cells)), "failure input bytes")
        v.need(case.program.tape.head == case.fields.tape.head == 1, "failure input heads")

    # A new restored scalar inside validation is behaviorally harmless but can
    # exceed the proven peak. The meter must reject it; suppressing only its
    # budget guard admits the same endpoint, demonstrating defect sensitivity.
    original_inverse = m.words.Ring.inverse
    def changed_inverse(ring, value):
        extra = ring.arena.zero()
        try:
            return original_inverse(ring, value)
        finally:
            if extra.slot in ring.arena.live:
                ring.arena.free(extra)
    with patch.object(m.words.Ring, "inverse", changed_inverse):
        rejects(lambda: v.run_callback(m), "numerical lifetime budget")
        accepted = v.run_callback(m, bounds=(13, 15))
        v.need(accepted["peak"]["validation"][0] == 13, "budget control sensitive")
    return 10


def integrity_controls():
    with tempfile.TemporaryDirectory(prefix="validation-controls-") as temporary:
        root = Path(temporary) / "package"
        shutil.copytree(ROOT, root)
        # A read-only export stays read-only. Only this disposable mutation
        # copy needs writable files/directories (copytree preserves modes).
        root.chmod(0o755)
        for path in root.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        original_root = v.ROOT
        v.ROOT = root
        try:
            source = root / "vendor/words.py"
            original = source.read_bytes()
            source.write_bytes(original+b"\n# corrupt\n")
            rejects(v.authenticate, "source sha256")
            source.write_bytes(original)
            snapshot = root / "evidence/PR2801-SNAPSHOT.json"
            original_snapshot = snapshot.read_bytes()
            snapshot.write_bytes(original_snapshot+b" ")
            rejects(v.authenticate, "snapshot pin")
            snapshot.write_bytes(original_snapshot)

            # Effective timestamp-cache substitution: first prove that an
            # ordinary importer would run the malicious same-size cache.
            stat = source.stat()
            poison = b"raise RuntimeError('effective cached substitution')\n"
            poison += b"#"*(len(original)-len(poison))
            source.write_bytes(poison)
            os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            py_compile.compile(str(source), doraise=True)
            source.write_bytes(original)
            os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            spec = importlib.util.spec_from_file_location("poison_probe", source)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except RuntimeError as error:
                v.need(str(error) == "effective cached substitution", "effective stale cache")
            else:
                raise ValueError("cache control was ineffective")
            with v.runtime() as m:
                positive = v.run_callback(m)
                v.need(positive["peak"]["validation"] == [12, 10], "authenticated source ignores cache")

            # bool == int in Python must not make a typed receipt acceptable.
            actual = {"schema": 1, "fixtures": [positive]}
            receipt = root / "control-receipt.json"
            receipt.write_text(json.dumps(actual))
            v.check_receipt(actual, receipt)
            forged = {"schema": True, "fixtures": [positive]}
            v.need(actual == forged, "typed control reaches equality trap")
            receipt.write_text(json.dumps(forged))
            rejects(lambda: v.check_receipt(actual, receipt), "typed fixed receipt")
        finally:
            v.ROOT = original_root
    return 4


def main():
    with v.runtime() as m:
        semantic = semantic_controls(m)
    integrity = integrity_controls()
    print(f"PASS_VALIDATION_CONTROLS semantic={semantic} integrity={integrity} optimized={sys.flags.optimize}")


if __name__ == "__main__":
    main()
