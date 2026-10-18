#!/usr/bin/env python3
"""Independent exact character obstruction for the owner0/port0 axis16 move.

The retained implementation supplies authenticated JSON parsing and reconstruction
of the T740 fill.  No retained operator constructor or replay is called.  This
file expands elementary 8 by 8 matrices, multiplies them, and reverses their
factor lists to obtain exact inverses over Gaussian integers.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.machinery
import importlib.util
import json
import marshal
from pathlib import Path
import struct
import tempfile
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/idle-star-paired-axis-census/verify.py"
SOURCE_SHA256 = "8be7cc5becb41c8812ee4d262222244eeacc1e01c77697669c4c2404cafda4fe"
BASE_MAIN = "463113d675af7410ac91d53a4fed51ec6494eb9a"
Z = (0, 0)
O = (1, 0)
I = (0, 1)
N = 8


def need(condition, message):
    if not condition:
        raise ValueError(message)


def plus(a, b):
    return (a[0] + b[0], a[1] + b[1])


def minus(a, b):
    return (a[0] - b[0], a[1] - b[1])


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def unit(exponent):
    return (O, I, (-1, 0), (0, -1))[exponent % 4]


def ident():
    return [[O if a == b else Z for b in range(N)] for a in range(N)]


def multiply(left, right):
    result = [[Z for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            coefficient = left[a][b]
            if coefficient != Z:
                for c in range(N):
                    if right[b][c] != Z:
                        result[a][c] = plus(result[a][c], times(coefficient, right[b][c]))
    return result


def scale(matrix, coefficient):
    return [[times(coefficient, x) for x in row] for row in matrix]


def defect(matrix):
    return [[minus(x, O if a == b else Z) for b, x in enumerate(row)]
            for a, row in enumerate(matrix)]


def scalar_json(number):
    if isinstance(number, Fraction):
        return number.numerator if number.denominator == 1 else [number.numerator, number.denominator]
    return number


def cjson(number):
    return [scalar_json(number[0]), scalar_json(number[1])]


def sparse_json(matrix):
    return [[a, b, cjson(matrix[a][b])] for a in range(N) for b in range(N) if matrix[a][b] != Z]


def character_parity(character, vector):
    return (character & vector).bit_count() % 2


def authenticated_source(source_path=SOURCE):
    need(source_path.is_file() and not source_path.is_symlink(), "retained parser path")
    source_bytes = source_path.read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA256, "retained parser source bytes")
    module = types.ModuleType("_absorption_authenticated_inputs")
    module.__file__ = str(source_path)
    exec(compile(source_bytes, str(source_path), "exec", optimize=0), module.__dict__)
    # Poison the operator functions: accidental reuse fails even during -O.
    def forbidden(*_args, **_kwargs):
        raise ValueError("independent oracle attempted retained matrix arithmetic")
    module.run_data_event = forbidden
    module.replay = forbidden
    return module


def authenticated_context():
    """Use only the retained source's parsing/provenance side of the interface."""
    module = authenticated_source()
    module.authenticate()
    load = lambda path: module.decode(module.read_bytes(path))
    vendor = SOURCE.parent / "vendor"
    base = load(vendor / "BASE-FILL.json.gz")["rows"]
    journal = load(vendor / "EXCHANGE.json")
    rows = module.project_all_ports(base, module.journal_edits(base, journal))
    order_base = load(ROOT / "research/rank7-joint-endframes/allocation/ORDER.json")
    order = [[stage, replica + 74 * copy] for stage, replica in order_base for copy in range(10)]
    dispatch = {(stage, replica): tag for stage, replica, tag in
                load(ROOT / "research/rank7-joint-endframes/allocation/DISPATCH.json")}
    providers = load(vendor / "PROVIDERS.json")
    plan = load(ROOT / "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz")
    template = load(ROOT / "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz")
    recipes = load(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json")["recipes"]
    return module.prepare_port(0, rows[0], order, dispatch, providers, plan, template, recipes)


def elementary(kind, first, second=0, coefficient=0):
    matrix = ident()
    inverse = ident()
    if kind == "phase":
        matrix[first][first] = unit(second)
        inverse[first][first] = unit(-second)
    elif kind == "shear":
        need(first != second, "self shear")
        matrix[first][second] = (coefficient, 0)
        inverse[first][second] = (-coefficient, 0)
    elif kind == "swap":
        need(first != second, "self swap")
        matrix[first], matrix[second] = matrix[second], matrix[first]
        inverse = [list(row) for row in matrix]
    else:
        raise ValueError("unknown independent elementary factor")
    need(multiply(matrix, inverse) == ident() == multiply(inverse, matrix), "elementary inverse")
    return matrix, inverse


def factors(context, residual, character):
    """Column-vector factors in chronological execution order, with 20 cuts."""
    need(type(character) is int and 0 <= character < 1 << 73, "character domain")
    result = []
    child_sites = {}
    recipe = context["recipe"]
    template = context["template"]
    q = character_parity(character, recipe["q"])

    def append(kind, a, b=0, coefficient=0, child=None):
        if child is not None:
            need(child not in child_sites, "duplicate child cut")
            child_sites[child] = len(result)
        result.append(elementary(kind, a, b, coefficient))

    blocks = {}
    stage = None
    for event in template["execution_schedule"]:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
            need(stage not in blocks, "duplicate stage")
            blocks[stage] = []
        need(stage is not None, "event before stage")
        blocks[stage].append(event)
    need(set(blocks) == set(range(9)), "stage coverage")

    for time, (stage, replica) in enumerate(context["order"]):
        for stream, axes in context["hosts"].get(time, ()):
            append("phase", stream, sum(character_parity(character, v) for v in axes))
        if replica != 0:
            continue
        for event in blocks[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                local = next(row for row in template["recipe"] if row["kind"] == "local"
                             and row["stage"] == stage)
                pair = local["pair"]
                lower = (1 << (1 + 8 * stage)) - 1
                upper = (1 << (9 + 8 * stage)) - 1
                # Entry/exit phases are reconstructed from the interval endpoints,
                # with the stage0 entry treated separately.
                for side in (0, 1):
                    entry = (1 - side) * q if stage == 0 else (character & lower).bit_count() - side * q
                    append("phase", 2 * pair + side, -entry)
                if local["reverse"]:
                    append("shear", 2 * pair, 2 * pair + 1, -1)
                else:
                    append("shear", 2 * pair + 1, 2 * pair, 1)
                for side in (0, 1):
                    append("phase", 2 * pair + side, (character & upper).bit_count() - side * q)
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    stream = 2 * event["pair"] + side
                    append("phase", stream, sum(character_parity(character, v) for v in residual[child]), child=child)
                    # Retain this factor when the preceding phase is omitted.
                    append("phase", stream, 2 * character_parity(character, recipe["idle_children"][child]["translation_after"]))
            elif kind == "bridge":
                a, b, c = event["dst"], event["src"], event["coefficient"]
                append("shear", 2 * a, 2 * b, c)
                append("shear", 2 * b + 1, 2 * a + 1, -c)
            elif kind == "terminal_Y_translations":
                for pair in event["pairs"]:
                    append("phase", 2 * pair + 1, 2 * q)
            elif kind == "terminal":
                for pair in range(event["pairs"]):
                    append("swap", 2 * pair, 2 * pair + 1)
                    append("phase", 2 * pair + 1, 2)
            else:
                raise ValueError("unknown data event: " + kind)
    need(set(child_sites) == set(range(20)), "twenty residual sites")
    return result, child_sites


def operators_at_cuts(word, sites, character):
    forward = [ident()]
    backward_inverse = [ident()]
    for matrix, inverse in word:
        forward.append(multiply(matrix, forward[-1]))
        backward_inverse.append(multiply(backward_inverse[-1], inverse))
    suffix = [None] * (len(word) + 1)
    suffix_inverse = [None] * (len(word) + 1)
    suffix[-1] = ident()
    suffix_inverse[-1] = ident()
    for position in range(len(word) - 1, -1, -1):
        matrix, inverse = word[position]
        suffix[position] = multiply(suffix[position + 1], matrix)
        suffix_inverse[position] = multiply(inverse, suffix_inverse[position + 1])
    target = scale(ident(), unit(character.bit_count()))
    required = {}
    for child, position in sites.items():
        prefix_inv = backward_inverse[position]
        suffix_inv = suffix_inverse[position + 1]
        replacement = multiply(multiply(suffix_inv, target), prefix_inv)
        need(multiply(multiply(suffix[position + 1], replacement), forward[position]) == target,
             "B R A equals target")
        required[child] = replacement
    return forward[-1], required


def rank_two_minor(matrix):
    for a in range(N):
        for b in range(a + 1, N):
            for c in range(N):
                for d in range(c + 1, N):
                    determinant = minus(times(matrix[a][c], matrix[b][d]), times(matrix[a][d], matrix[b][c]))
                    if determinant != Z:
                        return {"rows": [a, b], "columns": [c, d], "determinant": cjson(determinant)}
    return None


def ray_minor(left, right):
    entries = [(a, b) for a in range(N) for b in range(N)]
    pivot = next(((a, b) for a, b in entries if left[a][b] != Z), None)
    if pivot is None:
        return None
    a, b = pivot
    for c, d in entries:
        determinant = minus(times(left[a][b], right[c][d]), times(right[a][b], left[c][d]))
        if determinant != Z:
            return {"entries": [[a, b], [c, d]], "determinant": cjson(determinant)}
    return None


def common_projector_test(character_matrices):
    """Necessary rank/ray tests only; absence of a witness is not sufficiency."""
    nonzero = []
    for character, matrix in character_matrices:
        changed = defect(matrix)
        minor = rank_two_minor(changed)
        if minor is not None:
            return {"kind": "rank_at_least_two", "character": character, "minor": minor,
                    "defect": sparse_json(changed)}
        if sparse_json(changed):
            if nonzero:
                previous_character, previous = nonzero[0]
                minor = ray_minor(previous, changed)
                if minor is not None:
                    return {"kind": "varying_projector", "characters": [previous_character, character],
                            "minor": minor, "defects": [sparse_json(previous), sparse_json(changed)]}
            nonzero.append((character, changed))
    return None


def controls():
    half = Fraction(1, 2)
    projector = [[Z for _ in range(N)] for _ in range(N)]
    for a in (0, 1):
        for b in (0, 1):
            projector[a][b] = (half, 0)
    need(multiply(projector, projector) == projector and rank_two_minor(projector) is None,
         "fixed non-coordinate projector fixture")
    def phase_on(q, phase):
        return [[plus(O if a == b else Z, times(minus(phase, O), q[a][b]))
                 for b in range(N)] for a in range(N)]
    valid = [(0, ident()), (1, phase_on(projector, I)), (2, phase_on(projector, (-1, 0))),
             (3, phase_on(projector, (0, -1)))]
    need(common_projector_test(valid) is None, "rejected valid non-coordinate projector")
    other = [[Z for _ in range(N)] for _ in range(N)]
    other[2][2] = O
    varying = [(0, ident()), (1, phase_on(projector, I)), (2, phase_on(other, I))]
    need(common_projector_test(varying[:2]) is None, "single-character fixture must pass")
    variation = common_projector_test(varying)
    need(variation is not None and variation["kind"] == "varying_projector", "varying-projector control not rejected")
    rank_two = ident()
    rank_two[0][0] = I
    rank_two[1][1] = I
    ranked = common_projector_test([(0, ident()), (16, rank_two)])
    need(ranked is not None and ranked["kind"] == "rank_at_least_two", "rank-two control not rejected")
    # The insertion formula must use both inverses in the displayed order.
    left, left_inv = elementary("shear", 0, 1, 1)
    right, right_inv = elementary("shear", 1, 0, 1)
    correct = multiply(right_inv, left_inv)
    reversed_order = multiply(left_inv, right_inv)
    need(multiply(multiply(right, correct), left) == ident(), "noncommuting correct-order fixture")
    need(multiply(multiply(right, reversed_order), left) != ident(), "noncommuting wrong-order control")
    return {"fixed_noncoordinate_projector_accepted": True, "single_character_false_positive_accepted": True,
            "varying_projector_rejected": variation, "rank_two_rejected": ranked,
            "noncommuting_inverse_order_control": True}


def source_controls():
    """Demonstrate fresh byte compilation against both accepted .pyc cache forms."""
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source-control input bytes")
    with tempfile.TemporaryDirectory(prefix="absorption-source-control-") as temporary:
        path = Path(temporary) / "retained.py"
        path.write_bytes(raw)
        cache = Path(importlib.util.cache_from_source(str(path)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        canary = "ABSORPTION_BYTECODE_CANARY"
        payload = marshal.dumps(compile("raise ValueError('" + canary + "')", str(path), "exec"))
        timestamp_header = struct.pack("<III", 0, int(path.stat().st_mtime) & 0xffffffff, len(raw))
        unchecked_header = struct.pack("<I", 1) + b"uncheck!"
        try:
            for header in (timestamp_header, unchecked_header):
                cache.write_bytes(importlib.util.MAGIC_NUMBER + header + payload)
                cached_code = importlib.machinery.SourceFileLoader("cache_control", str(path)).get_code("cache_control")
                need(canary in cached_code.co_consts, "poisoned bytecode fixture was not active")
                fresh_module = authenticated_source(path)
                need(fresh_module.BASE_MAIN == "997e6a9ca7b4f95d50e366f61412fd640d72a88a",
                     "fresh loader did not execute authenticated parser source")
        finally:
            # An inherited -X pycache_prefix can place this outside the source
            # TemporaryDirectory; remove the explicit fixture in either case.
            cache.unlink(missing_ok=True)
        path.write_bytes(raw + b"\n# changed source\n")
        rejected = False
        try:
            authenticated_source(path)
        except ValueError as error:
            rejected = str(error) == "retained parser source bytes"
        need(rejected, "changed source hash accepted")
    return {"matching_timestamp_bytecode_ignored": True, "unchecked_hash_bytecode_ignored": True,
            "changed_source_bytes_rejected": True}


def run():
    fixture_results = controls()
    source_fixture_results = source_controls()
    context = authenticated_context()
    original = {child: list(axes) for child, axes in context["residual"].items()}
    need(len(original) == 20, "residual domain")
    need(len(original[10]) == len(original[12]) == 48, "source/destination residual ranks")
    need(original[10].count(16) == 1 and 16 not in original[12], "axis16 transfer preimage")
    altered = {child: list(axes) for child, axes in original.items()}
    altered[10].remove(16)
    altered[12].append(16)
    translation_word, translation_sites = factors(context, original, 1)
    phase_site = translation_sites[10]
    need(translation_word[phase_site + 1][0] != ident(), "nontrivial retained translation fixture")
    damaged_word = list(translation_word)
    damaged_word[phase_site + 1] = (ident(), ident())
    damaged_operator, damaged_required = operators_at_cuts(damaged_word, translation_sites, 1)
    need(damaged_operator != scale(ident(), unit(1)) and
         damaged_required[10] != translation_word[phase_site][0],
         "missing selected-child translation control was not detected")
    fixture_results["nonzero_translation_omission_rejected"] = True
    characters = list(dict.fromkeys([0, 16] + [1 << bit for bit in range(73)]))
    baseline_characters = list(dict.fromkeys(characters + [(1 << 73) - 1] +
                                            [(1 << bit) | (1 << (bit + 1)) for bit in range(72)]))
    for character in baseline_characters:
        word, sites = factors(context, original, character)
        operator, required = operators_at_cuts(word, sites, character)
        need(operator == scale(ident(), unit(character.bit_count())), "independent baseline operator")
        for child, position in sites.items():
            need(required[child] == word[position][0], "baseline required phase at every site")
    all_required = {child: [] for child in range(20)}
    _, zero_sites = factors(context, altered, 0)
    for character in characters:
        word, sites = factors(context, altered, character)
        need(sites == zero_sites, "character-independent site locations")
        operator, required = operators_at_cuts(word, sites, character)
        for child in range(20):
            if character == 0:
                need(required[child] == ident(), "R(0)=I")
            all_required[child].append((character, required[child]))
    witnesses = []
    survivors = []
    for child in range(20):
        witness = common_projector_test(all_required[child])
        if witness is None:
            survivors.append(child)
        else:
            witnesses.append({"child": child, "factor_index": zero_sites[child], **witness})
    return {
        "status": "PASS_INDEPENDENT_ALL_TWENTY_SITES_OBSTRUCTED" if not survivors else "INCOMPLETE_SURVIVING_SITES",
        "base_main": BASE_MAIN,
        "retained_parser_sha256": SOURCE_SHA256,
        "fill_payload_sha256": "8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00",
        "owner": 0, "port": 0, "source_child": 10, "destination_child": 12, "axis": 16,
        "residual_ranks_before": [len(original[child]) for child in range(20)],
        "residual_ranks_after": [len(altered[child]) for child in range(20)],
        "baseline_characters_checked": len(baseline_characters),
        "candidate_characters": characters, "candidate_sites_checked": 20,
        "all_eight_input_columns_checked": True,
        "translations_retained": True,
        "R_zero_identity_all_sites": True,
        "witnesses": witnesses, "surviving_sites": survivors,
        "controls": fixture_results,
        "source_controls": source_fixture_results,
        "new_kappa": None,
        "scope": "Fixed source-pinned T740 owner0/port0 axis16 child10-to-child12 overlay; one Fourier-diagonal scalar stream child replacement with fixed stream-only input/output adapters tensored with address identity, at one existing residual phase site; all other events fixed. Encoders that mix addresses with streams are excluded.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expected = None
    if args.output is None:
        receipt = PACKAGE / "INDEPENDENT.json"
        need(receipt.is_file() and not receipt.is_symlink(), "missing or linked fixed independent receipt")
        expected = json.loads(receipt.read_bytes())
    else:
        need(not args.output.exists() and not args.output.is_symlink(), "refusing to overwrite existing independent output")
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        need(result == expected, "fixed independent receipt differs")
    else:
        with args.output.open("x", encoding="utf-8") as output:
            output.write(encoded)
    print(result["status"], "sites=20", "characters=" + str(len(result["candidate_characters"])),
          "baseline=" + str(result["baseline_characters_checked"]), "no_new_kappa")
    if result["surviving_sites"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
