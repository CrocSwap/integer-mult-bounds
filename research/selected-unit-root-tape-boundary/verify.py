#!/usr/bin/env python3
"""Ask one selected-grammar root at q=3 to read the unit ROOT tape.

The published root is fixture (256, 2, 0 events), later asserted as the
extended record (256, 2, 1). Empty events encode depth 0. This run keeps
that size and depth and substitutes unit 1, the weight the depth-zero unit
ROOT writes. It does not change kappa and does not retarget the GL2 machine.
"""

import hashlib
import inspect
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INTERCHANGE = ROOT / "research/physical-ordinary-interchange"
ARCHIVE = INTERCHANGE / "inputs/pr2809.tar"
SELECTED = "macro_selected_checks.py"
RECORDS = "inputs/pr2753/predecessor/vendor/records.py"
Q = 3
ACCEPTED = (0, 2)
COEFFICIENT = "selected identity-projector adapter and generated child coefficients"
EXTENDED = "real selected extended root program"
RESTORATION = "exact parent stream restoration and protected result commit"
WATCHED = (COEFFICIENT, EXTENDED, RESTORATION)
MARKER = (
    "PASS_SELECTED_UNIT_ROOT_TAPE_BOUNDARY q=3 root=256,1,0 "
    "coefficients=0,1 rejected_before_body no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_SELECTED_UNIT_ROOT_TAPE_BOUNDARY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def published_initial():
    return bytes((index * 7 ^ index // 3) & 1 for index in range(23))


def checker_body(initial):
    """The body the selected checker appends. It is not a position reversal."""
    return bytes(1 - bit for bit in reversed(initial))


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "certificates/selected-result.json",
        "research/bit2234-stock-threshold/README.md",
        "research/physical-ordinary-interchange/ordinary.py",
        "research/physical-ordinary-interchange/inputs/pr2809.tar",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    ordinary = (INTERCHANGE / "ordinary.py").read_text(encoding="utf-8")
    require("for word in (size, ring.one, depth):" in ordinary, "unit ROOT triple changed")
    with tarfile.open(ARCHIVE, "r:") as tar:
        selected = tar.extractfile(SELECTED).read().decode("utf-8")
        records = tar.extractfile(RECORDS).read().decode("utf-8")
    for needle in (
        "Program.fixture(indices, arena, 256, 2, (), catalogue.codes.bits)",
        "zip(requests, (0, 2))",
        COEFFICIENT,
        "== (256, 2, 1)",
        "changed = bytes(1 - bit for bit in reversed(initial))",
        RESTORATION,
    ):
        require(needle in selected, "selected root no longer states " + needle)
    require(
        "(index_arena, len(events))" in records,
        "fixture no longer encodes the depth word as the event count",
    )
    return selected


def activate():
    import sys
    sys.path.insert(0, str(INTERCHANGE))
    import source
    source.activate()
    import macro_selected_checks as selected
    from records import Program
    return selected, Program


def watch(module):
    seen = []
    original = module.need

    def watching(condition, message):
        if message in WATCHED:
            seen.append((message, bool(condition)))
        original(condition, message)

    module.need = watching
    return seen, original


def published_run(selected):
    seen, original = watch(selected)
    try:
        result = selected.run()
    finally:
        selected.need = original
    require(result["selected_coefficients"] == list(ACCEPTED), "published coefficients changed")
    require(result["source_request"] == 27825, "published source request changed")
    require(result["child_width"] == 168 and result["depth"] == 1, "published child grant changed")
    require(result["source_bits"] == 23, "published source width changed")
    require(
        result["rejected_gates"] == ["wrong_parent", "foreign_program", "wrong_source"],
        "published gate rejections changed",
    )
    require(
        [item for item in seen if item[0] == COEFFICIENT] == [(COEFFICIENT, True), (COEFFICIENT, True)],
        "published coefficient gate changed",
    )
    require(seen.count((EXTENDED, True)) == 1, "published extended root was not asserted")
    require(any(item == (RESTORATION, True) for item in seen), "published root did not reach the checker-written body")
    require(all(item[1] for item in seen), "published root failed a watched check")
    return result


def unit_run(selected, program):
    from check_support import inspect_count
    from macro_binding import SelectedBinding

    calls = []
    coefficients = []
    original_fixture = program.fixture
    original_coefficient = SelectedBinding.coefficient

    def forced(index_arena, residue_arena, root_size, root_unit, events, code_bits):
        calls.append((root_size, root_unit, len(events)))
        return original_fixture(index_arena, residue_arena, root_size, 1, events, code_bits)

    def recording(self, machine, definition, first, request):
        value = original_coefficient(self, machine, definition, first, request)
        coefficients.append((request.kind, inspect_count(value)))
        return value

    program.fixture = forced
    SelectedBinding.coefficient = recording
    seen, original_need = watch(selected)
    try:
        try:
            selected.run()
        except ValueError as error:
            message = str(error)
        else:
            fail("unit root was accepted")
    finally:
        selected.need = original_need
        program.fixture = original_fixture
        SelectedBinding.coefficient = original_coefficient
    require(calls == [(256, 2, 0)], "unit substitution did not see the published fixture call")
    require(coefficients == [("adapter", 0), ("child", 1)], "unit coefficients changed")
    require(message == COEFFICIENT, "unit rejection message changed")
    require(seen == [(COEFFICIENT, True), (COEFFICIENT, False)], "unit root passed the coefficient gate")
    require(all(message not in (EXTENDED, RESTORATION) for message, _passed in seen),
            "unit root reached the checker body")
    return coefficients, message


def evaluate():
    authenticate()
    selected, program = activate()
    fixture_source = inspect.getsource(program.fixture)
    require("(index_arena, len(events))" in fixture_source, "loaded fixture is not the event-count encoder")
    published = published_run(selected)
    coefficients, message = unit_run(selected, program)
    initial = published_initial()
    injected = checker_body(initial)
    require(injected != bytes(reversed(initial)), "checker body collapsed to a pure bit reversal")
    return {
        "q": Q,
        "published_fixture": [256, 2, 0],
        "published_coefficients": published["selected_coefficients"],
        "published_extended_root": [256, 2, 1],
        "published_source_request": published["source_request"],
        "published_child_width": published["child_width"],
        "published_depth": published["depth"],
        "published_source_bits": published["source_bits"],
        "published_rejected_gates": published["rejected_gates"],
        "published_checker_wrote_child_body": True,
        "checker_body_is_bit_reversal": False,
        "unit_root": [256, 1, 0],
        "unit_coefficients": [value for _kind, value in coefficients],
        "unit_rejected": message,
        "unit_reached_child_body": False,
        "position_reversal_compared": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
