"""Semantic rejection and ownership controls for the closed binary callback."""
import ast
from dataclasses import replace
from pathlib import Path

from check_callback import context_fixture, no_decode, snapshot
from check_words import audit
from controller import selected_offset
from records import Fields, Program, Tape
from stream import positive_extent
from words import Arena, Ring, Word, need


def expect(action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), "intended semantic control")
        return str(error)
    raise ValueError("semantic control did not reject")


def callback_controls(template):
    controls = {}
    for fault in ("source_code", "rank", "high_range", "root_nonunit", "non_prime_power",
                  "source_range", "column_range", "padded_index", "pair_orientation", "compacted_reset"):
        kind = "pair_reverse" if fault == "pair_orientation" else "unit_reset" if fault == "compacted_reset" else "good"
        specs, events, rows, root_size = context_fixture(template, kind)
        modulus, unit, source_value, column_value = 9, 1, 4, 0
        events, rows = list(events), list(rows)
        if fault == "source_code":
            rows[0] = (33, rows[0][1])
            message = "original global raw-field code"
        elif fault == "rank":
            events[0] = (0, 11, 1, 0, False, False)
            message = "actual selected rank"
        elif fault == "high_range":
            changed = [list(row) for row in rows[-1][1]]
            changed[-1][-1] = 3
            rows[-1] = (22, tuple(map(tuple, changed)))
            message = "canonical high digit"
        elif fault == "root_nonunit":
            unit, message = 3, "root coefficient unit"
        elif fault == "non_prime_power":
            modulus, message = 15, "modulus is a power"
        elif fault == "source_range":
            source_value, message = 9, "canonical source atom"
        elif fault == "column_range":
            column_value, message = 7, "current selected column"
        elif fault == "padded_index":
            message = "canonical root-index word extent"
        elif fault == "pair_orientation":
            events[1] = (1, 33, 7, 118, False, False)
            message = "physical pair field and reversal"
        else:
            rows.pop(0)
            message = "original global raw-field code"
        residues = Arena(modulus.bit_length()+1)
        indices = Arena(root_size.bit_length()+1+(2 if fault == "padded_index" else 0), capacity=256)
        m, source = residues.input(modulus), residues.input(source_value)
        column = indices.input(column_value)
        program = Program.fixture(indices, residues, root_size, unit, tuple(events))
        fields = Fields.fixture(indices, residues, tuple(rows))
        before = (snapshot(program.tape), snapshot(fields.tape), bytes(m.cells), bytes(source.cells), bytes(column.cells))
        ring = Ring(m)
        controls[fault] = expect(lambda: no_decode(lambda: selected_offset(
            ring, indices, program, fields, specs, 22, 63, column, source)), message)
        ring.close()
        need(before == (snapshot(program.tape), snapshot(fields.tape), bytes(m.cells), bytes(source.cells), bytes(column.cells)),
             "rejection preserves encoded inputs")
        audit(residues, (m, source))
        audit(indices, (column,))
        residues.free_many(m, source)
        indices.free(column)
        audit(residues, ())
        audit(indices, ())
    padded = Arena(20, capacity=4)
    suffix = padded.input(1)
    controls["shared_spectator_padding"] = expect(lambda: positive_extent(suffix), "separately canonical")
    padded.free(suffix)
    audit(padded, ())
    invalid = Arena(7, capacity=4)
    modulus = invalid.input(9)
    controls["padded_modulus"] = expect(lambda: Ring(modulus), "canonical modulus word")
    audit(invalid, (modulus,))
    controls["decode_barrier"] = expect(lambda: no_decode(lambda: modulus.inspect()), "escaped to a host integer")
    leak = invalid.zero()
    controls["scratch_leak"] = expect(lambda: audit(invalid, (modulus,)), "exact live numerical registers")
    invalid.free_many(leak, modulus)
    audit(invalid, ())
    return controls


def source_barrier():
    """Inspect the runtime call paths, excluding declared fixture encoders."""
    root = Path(__file__).resolve().parent
    found = []
    for name in ("words.py", "matrices.py", "records.py", "controller.py", "stream.py"):
        tree = ast.parse((root/name).read_text())
        def visit(node, excluded=False):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                excluded = excluded or node.name in ("fixture", "input", "inspect")
            if not excluded and isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    need(node.func.id not in ("pow", "divmod", "gcd", "eval", "exec"), "no host numerical oracle")
                if isinstance(node.func, ast.Attribute):
                    need(node.func.attr not in ("inspect", "input", "fixture", "from_bytes", "gcd"), "no runtime numerical decoding")
            for child in ast.iter_child_nodes(node):
                visit(child, excluded)
        visit(tree)
        found.append(name)
    return {"runtime_modules": found, "excluded_input_helpers": ["fixture", "input", "inspect"]}


def large_source_codes(template):
    specs, events, rows, root_size = context_fixture(template)
    rename = {code: (1 << 80)+code for code in specs}
    specs = {rename[code]: replace(spec, code=rename[code]) for code, spec in specs.items()}
    events = tuple((kind, rename[code], rank, field, reverse, half) for kind, code, rank, field, reverse, half in events)
    rows = tuple((rename[code], high) for code, high in rows)
    residues, indices = Arena(5), Arena(root_size.bit_length()+1, capacity=256)
    m, source, column = residues.input(9), residues.input(4), indices.input(0)
    program = Program.fixture(indices, residues, root_size, 1, events, code_bits=96)
    fields = Fields.fixture(indices, residues, rows, code_bits=96)
    ring = Ring(m)
    result, prepared = no_decode(lambda: selected_offset(ring, indices, program, fields, specs, rename[22], 63, column, source))
    need(result.inspect() == 7 and prepared == (rename[11], rename[22]), "compile-time code width does not truncate source identity")
    residues.free(result)
    ring.close()
    audit(residues, (m, source))
    audit(indices, (column,))
    residues.free_many(m, source)
    indices.free(column)
    return {"code_bits": 96, "offset": 7, "prepared_codes": list(prepared)}
