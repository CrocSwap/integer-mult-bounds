"""Adversarial source, chronology, geometry and arithmetic checks."""
import ast
from dataclasses import replace
from pathlib import Path

from cardinality import Natural
from checks import audit, no_decode, small_forms, small_trace
from numeric import Geometry, selected_coefficient
import oracle
import packet
from plan import Reference, Request, compile_plan
from records import Fields, Program, Tape
from sources import compile_specification, compile_templates
from stream import one_bit_suffix
from trace import child
from words import Arena, BLANK, LEFT, RIGHT, Ring, need


def expect(action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), "intended semantic rejection")
        return str(error)
    raise ValueError("missing semantic rejection")


def natural_value(value):
    cells = value.tape.cells
    stop = cells.index(RIGHT)
    return sum(bit << i for i, bit in enumerate(cells[1:stop]))


def cardinalities():
    count = 0
    for value in (*range(256), (1 << 521)+(1 << 127)+9):
        for radix in (3, 5):
            arena = Arena(max(2, value.bit_length()+1), capacity=4)
            word = arena.input(value)
            original = bytes(word.cells)
            natural = no_decode(lambda: Natural(word))
            need(no_decode(lambda: one_bit_suffix(natural)) == (value == 1), "single-bit suffix recognition")
            no_decode(lambda: natural.multiply_small(radix))
            need(natural_value(natural) == value*radix, "binary cardinality multiplication")
            remainder = no_decode(lambda: natural.divide_small(radix))
            need(natural_value(natural) == value and remainder == 0, "exact cardinality division")
            remainder = no_decode(lambda: natural.divide_small(radix))
            need(natural_value(natural) == value//radix and remainder == value % radix,
                 "quotient/remainder cardinality invariant")
            natural.close()
            need(natural.tape.head == 1 and bytes(natural.tape.cells).rstrip(bytes([BLANK])) == bytes([LEFT]),
                 "erased cardinality tape")
            need(bytes(word.cells) == original and word.head == 1, "preserved cardinality input")
            arena.free(word)
            audit(arena, ())
            count += 1
    return {"cases": count, "largest_input_bits": 522, "fixed_radices": [3, 5]}


def source_rejections(template):
    low, high = oracle.fixture(template, 2, high=1)
    spec = compile_specification(22, template, low)
    plan = compile_plan(oracle.projector(template, low, ((0,)*64,)*64, 1), template.rank, 3, True)
    result = {}
    for fault in ("source_code", "plan_rank", "plan_branch", "child_half", "child_coordinate",
                  "child_kind", "child_field", "high_range", "root_nonunit"):
        arena, indices = Arena(5), Arena(8, capacity=256)
        modulus, coordinate = arena.input(9), indices.input(7 if fault == "child_coordinate" else 0)
        ring = Ring(modulus)
        program = Program.fixture(indices, arena, 64, 3 if fault == "root_nonunit" else 2, ())
        data = [list(row) for row in high]
        if fault == "high_range":
            data[0][0] = 3
        fields = Fields.fixture(indices, arena, ((33 if fault == "source_code" else 22, tuple(map(tuple, data))),))
        selected = replace(plan, rank=1) if fault == "plan_rank" else replace(plan, good=False) if fault == "plan_branch" else plan
        request = Request("adapter", coordinate, Reference("head", 0, 1, 0))
        if fault.startswith("child_"):
            request = Request("child", coordinate, child_kind="unit" if fault == "child_kind" else "good",
                              field=1 if fault == "child_field" else 0, half=fault == "child_half")
        message = {
            "source_code": "original global raw-field code", "plan_rank": "selected trace/source binding",
            "plan_branch": "selected trace/source binding", "child_half": "halving only at unit reset",
            "child_coordinate": "requested completed-child coordinate", "child_kind": "actual low-class branch",
            "child_field": "physical pair field and reversal", "high_range": "canonical high digit",
            "root_nonunit": "root coefficient unit",
        }[fault]
        original = bytes(program.tape.cells), bytes(fields.tape.cells), bytes(modulus.cells), bytes(coordinate.cells)
        result[fault] = expect(lambda: no_decode(lambda: selected_coefficient(
            selected, ring, indices, program, fields, {22: spec}, 22, request)), message)
        ring.close()
        need(original == (bytes(program.tape.cells), bytes(fields.tape.cells), bytes(modulus.cells), bytes(coordinate.cells))
             and program.tape.head == fields.tape.head == 1, "rejection preserves original inputs")
        audit(arena, (modulus,))
        audit(indices, (coordinate,))
        arena.free(modulus)
        indices.free(coordinate)
        audit(arena, ())
        audit(indices, ())
    return result


def geometry_rejections():
    result = {}
    for fault in ("prefix_padding", "spectator_padding", "field_count", "child_cutoff"):
        arena, indices, prefix_arena = Arena(5), Arena(8, capacity=256), Arena(20 if fault == "prefix_padding" else 2)
        spectator = Arena(20 if fault == "spectator_padding" else 2)
        m, f, depth, parent = arena.input(9), indices.input(1), indices.input(0), indices.input(2)
        fields, prefix, extent = indices.input(2 if fault == "field_count" else 1), prefix_arena.input(1), spectator.input(1)
        ring = Ring(m)
        plan = compile_plan([[1, 2], [0, 0]], 1, 3, True)
        geometry = Geometry(plan, indices, f, depth, 22, object())
        if fault == "child_cutoff":
            first, second, width = indices.input(0), indices.input(64), indices.input(64)
            iterator = child(geometry, first, second, width, "good")
            result[fault] = expect(lambda: no_decode(lambda: next(iterator)), "below selected cutoff")
        else:
            source, directory = Tape(), Tape()
            message = "original frozen/current field count" if fault == "field_count" else "separately canonical"
            result[fault] = expect(lambda: no_decode(lambda: packet.run(
                source, geometry, parent, ring, 3, extent, extent, prefix, fields, directory,
                lambda _fields, _request: arena.copy(ring.one))), message)
            need(source.head == directory.head == 1 and source.cells == directory.cells == bytearray([LEFT]),
                 "geometry rejection preserves payload and directory")
        geometry.close()
        ring.close()
        arena.free(m)
        indices.free_many(f, depth, parent, fields)
        prefix_arena.free(prefix)
        spectator.free(extent)
        for work in (arena, indices, prefix_arena, spectator):
            audit(work, ())
    return result


def source_barrier():
    root = Path(__file__).resolve().parent
    modules = ["forms.py", "numeric.py", "trace.py", "children.py", "cardinality.py", "bitstream.py",
               "stream_runner.py", "packet.py", "plan.py", "vendor/words.py", "vendor/matrices.py",
               "vendor/records.py", "vendor/controller.py", "vendor/stream.py"]
    for name in modules:
        tree = ast.parse((root/name).read_text())
        def visit(node, excluded=False):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                excluded = excluded or node.name in ("fixture", "input", "inspect", "compile_plan")
            if not excluded and isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    need(node.func.id not in ("pow", "divmod", "gcd", "eval", "exec"), "no native numerical oracle")
                    if node.func.id == "int":
                        child_flag = (name == "children.py" and len(node.args) == 1 and
                                      isinstance(node.args[0], ast.Attribute) and node.args[0].attr in ("reverse", "half"))
                        borrow_flag = (name == "vendor/words.py" and len(node.args) == 1 and
                                       ast.unparse(node.args[0]) == "digit < 0")
                        need(child_flag or borrow_flag, "only finite flags become native integers")
                if isinstance(node.func, ast.Attribute):
                    need(node.func.attr not in ("inspect", "input", "fixture", "from_bytes", "gcd"),
                         "no runtime numerical decoding")
            for descendant in ast.iter_child_nodes(node):
                visit(descendant, excluded)
        visit(tree)
    return {"runtime_modules": modules, "excluded_compile_or_fixture_helpers": ["compile_plan", "fixture", "input", "inspect"]}


def run():
    negative = {}
    for fault, columns in (("final_permutation", 1), ("redirected_pair", 1), ("omit_reversal", 3), ("wrong_inverse", 1)):
        negative[fault] = small_trace(columns, fault)["trace_sha256"]
    return {"chronology": small_forms(), "wrong_endpoint_controls": negative, "cardinalities": cardinalities(),
            "source_rejections": source_rejections(compile_templates(3)[0]),
            "geometry_rejections": geometry_rejections(), "source_barrier": source_barrier()}
