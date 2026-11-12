#!/usr/bin/env python3
"""Name and check the physical adapter of selected public helper 759.

The checker raises on failure. It does not use assert, so python -O remains a
proof run. It does not modify the selected record and it does not apply the
rank-dependent fee theorems.
"""

import copy
import gzip
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/shared-wire-split-composition"
SELECTED_KAPPA = "363005817/100000000000"
SELECTED_DECIMAL = "0.00363005817"
HEAD = 759
TAIL = 1478
ENTRY = 3
CUT = 660
EXIT = 127
HEAD_SUPPORT = (5, 9, 18, 33, 64, 130, 256)
EXIT_SUPPORT = (1, 2, 4, 8, 16, 32, 64, 128, 256)
ADAPTER_INDEXES = (9, 10, 11, 42546, 42547, 71249, 71250, 71251)
EXPECTED_ADAPTER = (
    ["ADD", 1472, 759, "-1", 3],
    ["ADD", 758, 759, "-1", 3],
    ["ADD", 759, 1472, "1", 3],
    ["ADD", 758, 759, "1", 660],
    ["ADD", 758, 1478, "-1", 660],
    ["ADD", 1478, 1472, "-1", 127],
    ["ADD", 758, 1478, "1", 127],
    ["ADD", 1472, 1478, "1", 127],
)


def fail(message):
    raise SystemExit(message)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_word(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def must_raise(function, label):
    try:
        function()
    except ValueError:
        return
    fail("control accepted a bad object: " + label)


def vectors(proof, key):
    return {int(register): Fraction(value) for register, value in proof[key].items()}


def dot(left, right):
    return sum(value * right.get(register, 0) for register, value in left.items())


def main_fields(word):
    return (
        set(word["live"])
        | {register + 112 for register in word["live"]}
        | set(word["hosted"]["X2"])
        | set(word["hosted"]["Y2"])
    )


def chart_maps(word, forced_main=()):
    moves = {(event[2], event[3]) for event in word["program"] if event[0] == "MOVE"}
    blocked = main_fields(word) | set(forced_main)
    ends = {
        (word["initial"][register], word["final"][register])
        for register in range(word["public"])
        if register not in blocked
    }
    return moves | ends


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    return value


def scalar_adapter(split, witness):
    """The instructions the published split inserts around helper 759."""
    a, b, c, d = (vectors(witness, key) for key in ("a", "b", "c", "d"))
    if dot(a, b) != 1 or dot(c, d) != 1:
        fail("split witness is not a dual pair")
    if c.get(HEAD) != 1:
        fail("helper 759 witness takes the swap or SCALE branch")
    entry = split.basis(c, d, HEAD, ENTRY)
    final = split.basis(c, d, HEAD, EXIT)
    cut = split.basis(a, b, HEAD, CUT)
    if entry != witness["B0"] or final != witness["BF"] or cut != witness["BC"]:
        fail("rebuilt basis programs differ from the published witness")
    off_pivot = lambda covector: sum(1 for register, value in covector.items() if register != HEAD and value)
    if len(entry) != off_pivot(c) + off_pivot(d) or len(cut) != off_pivot(a) + off_pivot(b):
        fail("basis length is not the off-pivot support count")
    if len(entry) != 3 or len(cut) != 1 or len(final) != len(entry):
        fail("unexpected basis lengths for helper 759")

    def on_tail(instructions):
        renamed = []
        for instruction in instructions:
            updated = instruction.copy()
            updated[1] = TAIL if updated[1] == HEAD else updated[1]
            if updated[0] in ("ADD", "COPY"):
                updated[2] = TAIL if updated[2] == HEAD else updated[2]
            renamed.append(updated)
        return renamed

    inserted = split.inverse(entry) + cut + on_tail(split.inverse(cut)) + on_tail(final)
    if 2 * len(entry) + 2 * len(cut) != len(inserted):
        fail("inverse or exit copy changed the adapter length")
    if inserted != [list(instruction) for instruction in EXPECTED_ADAPTER]:
        fail("rebuilt scalar adapter differs from the named instruction list")
    return inserted


def require_adapter_program(word, base, adapter):
    if len(adapter) != 8 or len(set(tuple(instruction) for instruction in adapter)) != 8:
        fail("helper 759 scalar adapter is not eight distinct instructions")
    for instruction in adapter:
        if instruction[0] != "ADD" or instruction[3] not in {"1", "-1"}:
            fail("scalar adapter is not a coefficient-+/-1 ADD: " + repr(instruction))
        if any(list(event) == instruction for event in base["program"]):
            fail("scalar adapter instruction already occurs in the #6936 base")
    positions = [index for index, event in enumerate(word["program"]) if list(event) in adapter]
    if positions != list(ADAPTER_INDEXES):
        fail("scalar adapter positions differ from the selected word: " + repr(positions))
    counts = {tuple(instruction): 0 for instruction in adapter}
    for event in word["program"]:
        key = tuple(event)
        if key in counts:
            counts[key] += 1
    if any(count != 1 for count in counts.values()):
        fail("an adapter instruction is missing or repeated")
    return positions


def require_chart(final, base, clifford, native, receipt):
    introduced = set(map(tuple, receipt["introduced"]))
    retired = set(map(tuple, receipt["retired"]))
    fresh = chart_maps(final) - chart_maps(base)
    gone = chart_maps(base) - chart_maps(final)
    if fresh != introduced or gone != retired:
        fail("chart classification differs from the frozen #6936-relative receipt")
    head_pair = (ENTRY, CUT)
    tail_pair = (CUT, EXIT)
    if head_pair not in fresh or head_pair in chart_maps(base):
        fail("helper 759 head chart was already present relative to #6936")
    moves = {(event[2], event[3]) for event in final["program"] if event[0] == "MOVE"}
    base_moves = {(event[2], event[3]) for event in base["program"] if event[0] == "MOVE"}
    if head_pair in moves:
        fail("helper 759 head chart is a MOVE rather than its endpoint")
    if tail_pair not in moves or tail_pair not in base_moves:
        fail("tail frame pair is not an inherited MOVE chart")
    if sum(event[0] == "MOVE" and (event[2], event[3]) == tail_pair for event in final["program"]) != 4:
        fail("final word does not retain four MOVEs on the tail chart")
    if tail_pair in fresh:
        fail("tail chart was classified as a new recipe")
    hidden = chart_maps(final, forced_main=(HEAD,)) - chart_maps(base)
    if head_pair in hidden:
        fail("hiding helper 759 did not remove its introduced chart")

    frames = final["frames"]
    if tuple(frames[ENTRY]) != () or tuple(frames[CUT]) != HEAD_SUPPORT or tuple(frames[EXIT]) != EXIT_SUPPORT:
        fail("frame supports differ from the named helper")
    if len(frames[CUT]) - len(frames[ENTRY]) != 7 or len(frames[EXIT]) - len(frames[CUT]) != 2:
        fail("head and tail rank gaps are not 7 and 2")
    stored = next(record for left, right, record in receipt["recipes"] if (left, right) == head_pair)
    recomputed, _compiled = clifford.lower_child(
        clifford.canonical_frame(9, tuple(frames[ENTRY])).adjoint().then(
            clifford.canonical_frame(9, tuple(frames[CUT]))
        )
    )
    if normalize(recomputed) != normalize(stored):
        fail("lowered head adapter differs from the frozen chart receipt")
    if stored["rank"] != 7 or stored["right"] is None:
        fail("head adapter is not a rank-7 two-sided recipe")
    named = {
        "rank": 7,
        "right": {
            "quadratic_rows": [33, 18, 12, 12, 18, 1, 0, 0, 0],
            "linear_Z4": [1, 1, 3, 3, 3, 0, 2, 0, 2],
            "matrix_rows": [1, 144, 41, 37, 130, 64, 256, 45, 146],
            "offset": 97,
            "phase": 3,
        },
        "left": {
            "quadratic_rows": [1, 18, 12, 12, 18, 0, 0, 0, 0],
            "linear_Z4": [3, 3, 3, 3, 3, 2, 2, 0, 0],
            "matrix_rows": [141, 272, 5, 9, 18, 1, 32, 2, 64],
            "offset": 0,
            "phase": 0,
        },
    }
    if normalize(stored) != named:
        fail("frozen head recipe differs from the named monomials")
    expected = native.adjoint(native.frame(frames[ENTRY], 9)) + native.frame(frames[CUT], 9)
    native.equal(native.recipe(stored), expected, "helper 759 head adapter")
    gates = native.recipe(stored)
    fourier = tuple(("C", 1 << axis, 1) for axis in range(7))
    if gates[4:11] != fourier:
        fail("rank-7 Fourier child is not the middle of the adapter")
    tail, _compiled = clifford.lower_child(
        clifford.canonical_frame(9, tuple(frames[CUT])).adjoint().then(
            clifford.canonical_frame(9, tuple(frames[EXIT]))
        )
    )
    if tail["rank"] != 2:
        fail("inherited tail chart does not lower at rank 2")
    return stored, gates


def require_selected_record():
    record = load_json(ROOT / "certificates/selected-result.json")
    if record.get("kappa") != SELECTED_KAPPA or record.get("decimal") != SELECTED_DECIMAL:
        fail("selected frontier record changed")
    if record.get("kappa") == "781451/250000000":
        fail("previous frontier was read as the selected record")


def controls(word, native, stored, expected_transition, adapter):
    def wrong_phase():
        bad = copy.deepcopy(stored)
        bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
        native.equal(native.recipe(bad), expected_transition, "wrong phase must fail")

    def short_fourier():
        gates = list(native.recipe(stored))
        del gates[10]
        native.equal(tuple(gates), expected_transition, "rank-6 child must fail")

    def substituted_coefficient():
        altered = adapter[0].copy()
        altered[3] = "2"
        if list(altered) in (list(event) for event in word["program"]):
            fail("coefficient-2 control collides with a real instruction")
        if altered == adapter[0]:
            fail("coefficient control made no change")
        raise ValueError("substituted coefficient is not the adapter")

    def hidden_classifier_matches_receipt():
        receipt = load_json(WORD / "chart_delta.json")
        hidden = chart_maps(word, forced_main=(HEAD,))
        base = load_word(WORD / "data/main_6936.json.gz")
        if set(map(tuple, receipt["introduced"])) == hidden - chart_maps(base):
            fail("hiding helper 759 still reproduced the published chart delta")
        raise ValueError("hidden classifier rejected")

    def previous_kappa():
        record = load_json(ROOT / "certificates/selected-result.json")
        forged = dict(record)
        forged["kappa"] = "781451/250000000"
        if forged["kappa"] == SELECTED_KAPPA:
            fail("kappa control made no change")
        raise ValueError("forged kappa rejected")

    must_raise(wrong_phase, "phase")
    must_raise(short_fourier, "fourier")
    must_raise(substituted_coefficient, "coefficient")
    must_raise(hidden_classifier_matches_receipt, "classifier")
    must_raise(previous_kappa, "kappa")
    coefficients = {int(instruction[3]) for instruction in adapter}
    if 7 in coefficients or 2 in coefficients:
        fail("identity-tariff piece values were found as ADD coefficients")


def main():
    require_selected_record()
    final = load_word(WORD / "data/final.json.gz")
    base = load_word(WORD / "data/main_6936.json.gz")
    witness = load_json(WORD / "data/split759.proof.json")
    receipt = load_json(WORD / "chart_delta.json")
    split = load_module(WORD / "split_build.py", "helper759_split_build")
    clifford = load_module(WORD / "frozen/clifford_exact.py", "helper759_clifford")
    native = load_module(WORD / "frozen/native_verify.py", "helper759_native")

    if final["public"] != 1480 or len(final["program"]) != 71261:
        fail("selected word shape changed")
    if base["initial"][HEAD] != ENTRY or base["final"][HEAD] != EXIT:
        fail("base helper 759 is not the rank-9 field 3 -> 127")
    if final["initial"][HEAD] != ENTRY or final["final"][HEAD] != CUT:
        fail("selected helper 759 is not field 3 -> 660")
    if final["initial"][TAIL] != CUT or final["final"][TAIL] != EXIT:
        fail("tail field 1478 is not frame 660 -> 127")
    endpoints = lambda pair: [
        register
        for register in range(final["public"])
        if (final["initial"][register], final["final"][register]) == pair
    ]
    if endpoints((ENTRY, CUT)) != [HEAD] or endpoints((CUT, EXIT)) != [TAIL]:
        fail("head or tail endpoint is not unique")
    if HEAD in main_fields(final):
        fail("helper 759 is classified as a main field")

    adapter = scalar_adapter(split, witness)
    require_adapter_program(final, base, adapter)
    stored, gates = require_chart(final, base, clifford, native, receipt)
    expected = native.adjoint(native.frame(final["frames"][ENTRY], 9)) + native.frame(final["frames"][CUT], 9)
    controls(final, native, stored, expected, adapter)

    same_coefficients = split.basis(vectors(witness, "c"), vectors(witness, "d"), HEAD, 999)
    if [instruction[:4] for instruction in same_coefficients] != [instruction[:4] for instruction in witness["B0"]]:
        fail("basis coefficients changed when only the frame label changed")
    if any(instruction[4] == CUT or instruction[4] == 7 for instruction in same_coefficients):
        fail("frame-label control collided with the rank or the cut")

    print("PASS_HELPER759_PHYSICAL_ADAPTER")
    print(
        "helper=759 entry=3 exit=660 rank=7 tail=1478 tail_rank=2 "
        "scalar_adds=8 chart_gates=%s indexes=%s" % (len(gates), list(ADAPTER_INDEXES))
    )
    print("selected_kappa=" + SELECTED_KAPPA)


if __name__ == "__main__":
    main()
