#!/usr/bin/env python3
"""Independent Gaussian-integer, primitive-operation cut calculation.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Literal stream semantics are independently transcribed from Gonzalo-Mier's
PR3199-lineage idle-star-paired-axis-census interpreter. Only the primary
verifier's authenticate/source_context definitions are reused, for source/data
binding and parsing; no primary or historical operator routine is called.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
ZERO = (0, 0)
ONE = (1, 0)
CHARACTERS = (0, 16, 33554432, 33554448)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def minus(a, b):
    return a[0] - b[0], a[1] - b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def quarter_turn(a, power):
    for _ in range(power % 4):
        a = (-a[1], a[0])
    return a


def unit(size=8):
    return [[ONE if r == c else ZERO for c in range(size)] for r in range(size)]


def target(character):
    scalar = quarter_turn(ONE, character.bit_count())
    return [[scalar if r == c else ZERO for c in range(8)] for r in range(8)]


def character_bit(character, axis):
    return (character & axis).bit_count() % 2


def authenticated_context():
    """Import just the two explicitly permitted context/data definitions.

    Compile exact source text with assertions enabled. AST selection prevents
    accidentally calling the primary matrix operations through this namespace.
    The retained interpreter itself is authenticated and source-compiled by
    source_context; its arithmetic/replay routines are never invoked here.
    """
    path = PACKAGE / "verify.py"
    require(path.is_file() and not path.is_symlink(), "missing primary context source")
    source_text = path.read_bytes().decode("utf-8")
    tree = ast.parse(source_text, str(path))
    names = {"authenticate", "source_context"}
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name in names]
    require(len(definitions) == 2, "two permitted context definitions")
    context_tree = ast.Module(body=definitions, type_ignores=[])
    namespace = {
        "PACKAGE": PACKAGE, "ROOT": ROOT, "BASE": BASE, "require": require,
        "hashlib": hashlib, "json": json, "types": types,
    }
    exec(compile(context_tree, str(path), "exec", optimize=0), namespace)
    namespace["authenticate"]()
    old, context = namespace["source_context"]()
    require("operations" not in namespace and "requirements" not in namespace,
            "operator helpers excluded from reused namespace")
    # ast.dump changes its representation of default fields across Python
    # versions. Fingerprint exact selected source text, not AST serialization.
    segments = [ast.get_source_segment(source_text, node) for node in definitions]
    require(all(isinstance(segment, str) for segment in segments), "selected context source segments")
    digest = hashlib.sha256(b"\n\n".join(segment.encode("utf-8") for segment in segments)).hexdigest()
    return context, old.TOTAL_ROWS, digest


def primitives(context, residual, character):
    """Flatten physical chronology into elementary operations on eight rows.

    Each item is (kind, destination, source-or-power, coefficient, label).
    For a phase, the third entry is its power of i and coefficient is unused.
    For a signed exchange, destination/source identify a pair. The exchange is
    (X,Y) -> (Y,-X). Literal child phase sites remain distinct from the following
    translation, including when either happens to be identity at this character.
    """
    require(type(character) is int and 0 <= character < 1 << 73, "73-bit character")
    recipe = context["recipe"]
    q = character_bit(character, recipe["q"])
    stages = {}
    current = None
    for event in context["template"]["execution_schedule"]:
        kind = event["kind"]
        if kind in {"bank_padding_cover_sweep", "translate_every_live_family"}:
            # These are helper-family events, outside this eight-stream map.
            continue
        if kind == "local_cover_sweep":
            current = event["stage"]
            require(current not in stages, "unique local stage")
            stages[current] = []
        require(current is not None, "stage boundary precedes physical event")
        stages[current].append(event)
    require(set(stages) == set(range(9)), "complete nine-stage chronology")
    local_steps = {event["stage"]: event for event in context["template"]["recipe"]
                   if event["kind"] == "local"}
    require(set(local_steps) == set(range(9)), "complete local recipe")
    ops, sites = [], {}

    def phase(stream, power, label):
        ops.append(("phase", stream, power % 4, 0, label))

    def add(destination, source, coefficient, label):
        require(destination != source and coefficient in {-1, 1}, "elementary shear")
        ops.append(("add", destination, source, coefficient, label))

    for time, (stage, owner) in enumerate(context["order"]):
        for index, (stream, axes) in enumerate(context["hosts"].get(time, ())):
            phase(stream, sum(character_bit(character, axis) for axis in axes),
                  f"host:{time}:{index}")
        if owner != 0:
            continue
        for event in stages[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                local = local_steps[stage]
                x, y = 2 * local["pair"], 2 * local["pair"] + 1
                if stage == 0:
                    entering = (q, 0)
                else:
                    low = (character & ((1 << (9 + 8 * (stage - 1))) - 1)).bit_count()
                    entering = (low, low - q)
                phase(x, -entering[0], f"local-enter:{stage}:X")
                phase(y, -entering[1], f"local-enter:{stage}:Y")
                if local["reverse"]:
                    add(x, y, -1, f"local-source:{stage}")
                else:
                    add(y, x, 1, f"local-source:{stage}")
                low = (character & ((1 << (9 + 8 * stage)) - 1)).bit_count()
                phase(x, low, f"local-exit:{stage}:X")
                phase(y, low - q, f"local-exit:{stage}:Y")
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    require(child not in sites, "unique completed child site")
                    stream = 2 * event["pair"] + side
                    sites[child] = len(ops)
                    phase(stream, sum(character_bit(character, axis) for axis in residual[child]),
                          f"residual:{child}")
                    translation = recipe["idle_children"][child]["translation_after"]
                    phase(stream, 2 * character_bit(character, translation),
                          f"idle-translation:{child}")
            elif kind == "bridge":
                destination, source, coefficient = event["dst"], event["src"], event["coefficient"]
                add(2 * destination, 2 * source, coefficient,
                    f"bridge:{stage}:X:{destination}:{source}")
                add(2 * source + 1, 2 * destination + 1, -coefficient,
                    f"bridge:{stage}:Y:{source}:{destination}")
            elif kind == "terminal_Y_translations":
                for pair in event["pairs"]:
                    phase(2 * pair + 1, 2 * q, f"terminal-translation:{pair}")
            elif kind == "terminal":
                for pair in range(event["pairs"]):
                    ops.append(("exchange", 2 * pair, 2 * pair + 1, 0,
                                f"terminal-exchange:{pair}"))
            else:
                raise ValueError("unhandled physical data event: " + kind)
    require(set(sites) == set(range(20)), "all twenty completed child sites")
    return ops, sites


def act_rows(matrix, op, inverse=False):
    kind, destination, source, coefficient, _ = op
    if kind == "phase":
        power = -source if inverse else source
        matrix[destination] = [quarter_turn(value, power) for value in matrix[destination]]
    elif kind == "add":
        coefficient *= -1 if inverse else 1
        matrix[destination] = [plus(a, (coefficient * b[0], coefficient * b[1]))
                               for a, b in zip(matrix[destination], matrix[source], strict=True)]
    elif kind == "exchange":
        x, y = matrix[destination], matrix[source]
        if inverse:
            matrix[destination], matrix[source] = [(-a, -b) for a, b in y], x
        else:
            matrix[destination], matrix[source] = y, [(-a, -b) for a, b in x]
    else:
        raise ValueError("unknown elementary row operation")


def undo_on_right(matrix, op):
    """Right multiplication by an elementary inverse, as column updates.

    A row shear E=I+c e_d e_s^T gives col_s <- col_s-c col_d.
    An exchange E=[[0,1],[-1,0]] gives (col_d,col_s)<-(col_s,-col_d).
    """
    kind, destination, source, coefficient, _ = op
    if kind == "phase":
        for row in matrix:
            row[destination] = quarter_turn(row[destination], -source)
    elif kind == "add":
        for row in matrix:
            value = row[destination]
            row[source] = minus(row[source], (coefficient * value[0], coefficient * value[1]))
    elif kind == "exchange":
        for row in matrix:
            x, y = row[destination], row[source]
            row[destination], row[source] = y, (-x[0], -x[1])
    else:
        raise ValueError("unknown elementary column operation")


def forward(ops):
    state = unit()
    for op in ops:
        act_rows(state, op)
    return state


def required_at(ops, cut, character, reverse_prefix=False):
    # A=e_(k-1)...e_0, B=e_(n-1)...e_(k+1), so R=B^-1 T A^-1.
    # Undo suffix by inverse row operations in reverse chronological order;
    # undo prefix on the right in forward chronological order. No generic
    # matrix multiplication, matrix inversion, fractions, or source replay.
    state = target(character)
    for op in reversed(ops[cut + 1:]):
        act_rows(state, op, inverse=True)
    prefix = ops[:cut]
    for op in reversed(prefix) if reverse_prefix else prefix:
        undo_on_right(state, op)
    return state


def insert_matrix(state, replacement):
    out = [[ZERO for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for column in range(8):
            for middle in range(8):
                out[row][column] = plus(out[row][column],
                                        times(replacement[row][middle], state[middle][column]))
    return out


def complete(ops, cut, replacement):
    state = unit()
    for index, op in enumerate(ops):
        if index == cut:
            state = insert_matrix(state, replacement)
        else:
            act_rows(state, op)
    return state


def defect(matrix):
    return [[minus(value, ONE if row == column else ZERO)
             for column, value in enumerate(values)]
            for row, values in enumerate(matrix)]


def nonzero_minor(matrix):
    for rows in itertools.combinations(range(8), 2):
        for columns in itertools.combinations(range(8), 2):
            a, b = rows
            c, d = columns
            determinant = minus(times(matrix[a][c], matrix[b][d]),
                                times(matrix[a][d], matrix[b][c]))
            if determinant != ZERO:
                return {"rows": list(rows), "columns": list(columns),
                        "determinant": list(determinant)}
    return None


def exact_rank(matrix):
    """Fraction-free Gaussian-integer elimination; rank over Q(i), hence C."""
    work = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(8):
        selected = next((row for row in range(pivot_row, 8)
                         if work[row][column] != ZERO), None)
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        pivot = work[pivot_row][column]
        for row in range(pivot_row + 1, 8):
            entry = work[row][column]
            if entry != ZERO:
                work[row] = [minus(times(pivot, value), times(entry, top))
                             for value, top in zip(work[row], work[pivot_row], strict=True)]
        pivot_row += 1
        if pivot_row == 8:
            break
    return pivot_row


def equal_operator(actual, expected):
    require(actual == expected, "complete operator mismatch")


def rank_one_necessary(matrix):
    require(nonzero_minor(defect(matrix)) is None, "rank-two defect")


def rejects(check, reason):
    rejection = None
    try:
        check()
    except ValueError as exc:
        rejection = str(exc)
    require(rejection == reason, "intended rejection missing: " + reason)


def first_difference(left, right):
    for row in range(8):
        for column in range(8):
            if left[row][column] != right[row][column]:
                return {"row": row, "column": column, "actual": list(left[row][column]),
                        "expected": list(right[row][column])}
    return None


def synthetic_controls():
    # Two valid reciprocal characterwise charts select distinct coordinate lines.
    first = unit()
    act_rows(first, ("phase", 0, 1, 0, "first-character"))
    second = unit()
    act_rows(second, ("phase", 6, 1, 0, "second-character"))
    rank_one_necessary(first)
    rank_one_necessary(second)
    require(defect(first) != defect(second), "different projectors at different characters")

    # L=I+3E_25, L^-1=I-3E_25: an oblique, fixed projector
    # L E_22 L^-1 = E_22-3E_25, not an orthogonal coordinate projection.
    oblique = unit()
    act_rows(oblique, ("add", 2, 5, 3, "L-inverse"), inverse=True)
    act_rows(oblique, ("phase", 2, 1, 0, "D"))
    act_rows(oblique, ("add", 2, 5, 3, "L"))
    rank_one_necessary(oblique)
    d = defect(oblique)
    require(d[2][2] == (-1, 1) and d[2][5] == (3, -3), "oblique reciprocal conjugation")

    rank_two = [list(row) for row in first]
    act_rows(rank_two, ("phase", 6, 1, 0, "two-active-lines"))
    rejects(lambda: rank_one_necessary(rank_two), "rank-two defect")

    # Rejecting rank-two is only a necessary test: a nonzero nilpotent rank-one
    # transvection is deliberately not claimed to be a reciprocal phase chart.
    return {
        "character_dependent_distinct_projectors": True,
        "fixed_oblique_projector": True,
        "identity_z_equals_one": nonzero_minor(defect(unit())) is None,
        "rank_two_rejected_by_named_check": True,
    }


def sensitivity_controls(context, residual):
    # The obstruction characters have no active idle translation. Character1
    # separately exercises the signed translation and nontrivial global phase.
    character = 1
    ops, sites = primitives(context, residual, character)
    equal_operator(forward(ops), target(character))
    index = next(index for index, op in enumerate(ops)
                 if op[4].startswith("idle-translation:") and op[2] != 0)
    omitted = forward(ops[:index] + ops[index + 1:])
    rejects(lambda: equal_operator(omitted, target(character)), "complete operator mismatch")

    bridge = next(index for index, op in enumerate(ops) if op[4].startswith("bridge:"))
    mutated = list(ops)
    kind, destination, source, coefficient, label = mutated[bridge]
    mutated[bridge] = kind, destination, source, -coefficient, label
    source_change = forward(mutated)
    rejects(lambda: equal_operator(source_change, target(character)), "complete operator mismatch")

    # An actual noncommuting cut, not a scalar fixture: reversing right-side
    # prefix inverses fails full target completion at child12/character1.
    cut = sites[12]
    correct = required_at(ops, cut, character)
    equal_operator(complete(ops, cut, correct), target(character))
    wrong_order = required_at(ops, cut, character, reverse_prefix=True)
    wrong_completion = complete(ops, cut, wrong_order)
    rejects(lambda: equal_operator(wrong_completion, target(character)), "complete operator mismatch")
    require(target(character)[0][0] == (0, 1), "global i phase retained")
    return {
        "character": character,
        "omitted_active_translation": {"operation": ops[index][4],
                                       "difference": first_difference(omitted, target(character))},
        "source_bridge_sign_mutation": {"operation": ops[bridge][4],
                                        "difference": first_difference(source_change, target(character))},
        "reversed_prefix_inverse_order": {"site": 12,
                                          "difference": first_difference(wrong_completion, target(character))},
        "global_phase_i_checked": True,
    }


def run():
    context, rows, context_digest = authenticated_context()
    original = {child: list(axes) for child, axes in context["residual"].items()}
    require([len(original[child]) for child in (10, 12)] == [48, 48], "original rank48 pair")
    require(original[10].count(16) == 1 and 16 not in original[12], "literal axis16 transfer")
    moved = {child: list(axes) for child, axes in original.items()}
    moved[10].remove(16)
    moved[12].append(16)
    require([len(moved[child]) for child in (10, 12)] == [47, 49], "candidate rank47/49 pair")

    witnesses, receiver, rank_profiles = {}, {}, {}
    completed = unchanged = 0
    primitive_count = None
    for character in CHARACTERS:
        ops, sites = primitives(context, moved, character)
        base_ops, base_sites = primitives(context, original, character)
        require(sites == base_sites, "transfer preserves physical cut locations")
        equal_operator(forward(base_ops), target(character))
        require(primitive_count is None or primitive_count == len(ops), "character-independent chronology size")
        primitive_count = len(ops)
        ranks = []
        for child in range(20):
            cut = sites[child]
            literal = unit()
            act_rows(literal, base_ops[cut])
            base_required = required_at(base_ops, cut, character)
            equal_operator(base_required, literal)
            rank_one_necessary(base_required)
            unchanged += 1
            required = required_at(ops, cut, character)
            equal_operator(complete(ops, cut, required), target(character))
            completed += 1
            rank = exact_rank(defect(required))
            ranks.append(rank)
            if character == 33554448:
                minor = nonzero_minor(defect(required))
                require(minor is not None and rank >= 2, "unresolved one-site candidate at " + str(child))
                rejects(lambda required=required: rank_one_necessary(required), "rank-two defect")
                witnesses[str(child)] = {"required_matrix": required, "defect_rank": rank, **minor}
            if child == 12:
                receiver[str(character)] = required
        rank_profiles[str(character)] = ranks

    return {
        "status": "PASS_INDEPENDENT_CHARACTERWISE_RANK_OBSTRUCTION",
        "base_commit": BASE,
        "source_manifest_sha256": hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest(),
        "reused_context_definitions_sha256": context_digest,
        "authenticated_fill_rows": rows,
        "owner_replica": 0,
        "port": 0,
        "transfer": {"axis": 16, "donor": 10, "receiver": 12,
                     "old_ranks": [48, 48], "candidate_ranks": [47, 49]},
        "character_bits": 73,
        "characters": list(CHARACTERS),
        "witness_character": 33554448,
        "sites": 20,
        "primitive_operations_per_character": primitive_count,
        "all_arbitrary_input_columns": 8,
        "replacement_completion_checks": completed,
        "literal_unchanged_child_checks": unchanged,
        "defect_rank_profiles": rank_profiles,
        "witnesses": witnesses,
        "receiver_samples": receiver,
        "synthetic_controls": synthetic_controls(),
        "sensitivity_controls": sensitivity_controls(context, original),
        "independence": "Primary authenticate/source_context definitions reused only for authenticated data parsing; independent Gaussian-integer primitive semantics, inverse row/column cut replay and fraction-free rank; no primary/source operator routines called.",
        "coverage": "All20 existing phase-child cuts, all8 arbitrary stream columns at4 exact characters, plus active translation/global-phase/factor-order controls at character1. One rank-two minor per site at33554448 refutes its full-domain necessary condition.",
        "new_kappa": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = PACKAGE / "INDEPENDENT.json"
        require(expected.is_file() and not expected.is_symlink(), "missing independent fixed receipt")
        require(result == json.loads(expected.read_bytes()), "committed independent result mismatch")
    print("PASS_INDEPENDENT_CHARACTERWISE_RANK_OBSTRUCTION sites=20 characters=4 columns=8 no_new_kappa")


if __name__ == "__main__":
    main()
