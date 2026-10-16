#!/usr/bin/env python3
"""Independent conditional reserve-composition audit. No supplier admission."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tarfile
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_SOURCE = 64 * 1024 * 1024
MAX_WORD = 50000
MAX_STAGES = 7
MAX_WIDTH = 9


class Rejected(ValueError):
    """A source, semantic contract or receipt failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Rejected(message)


def source_bytes(path: Path, digest: str) -> bytes:
    require(path.stat().st_size <= MAX_SOURCE, "source capacity")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"source pin: {path}")
    return data


def authenticated_inputs() -> tuple[dict, dict]:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(manifest["files"]) <= 16, "source inventory capacity")
    inputs = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            inputs[entry["path"]] = source_bytes(ROOT / entry["path"], entry["sha256"])
    require(len(manifest["pending_sources"]) == 2, "pending source inventory")
    for entry in manifest["pending_sources"]:
        source_bytes(PACKAGE / entry["path"], entry["sha256"])
    binding = json.loads(inputs["certificates/selected-result.json"])
    assembly_path = "research/community-frontier1094-audit/ASSEMBLY.json"
    require(binding["certificate"] == assembly_path, "selected certificate path")
    require(hashlib.sha256(inputs[assembly_path]).hexdigest() ==
            binding["certificate_sha256"], "selected assembly binding")
    archive = manifest["archive_members"][0]
    with tarfile.open(fileobj=io.BytesIO(inputs[archive["path"]]), mode="r:gz") as bundle:
        members = bundle.getmembers()
        require(len(members) <= 1024, "archive member capacity")
        member = bundle.getmember(archive["member"])
        require(member.isfile() and member.size <= 65536, "assembler member type/size")
        stream = bundle.extractfile(member)
        require(stream is not None, "assembler absent")
        with stream:
            code = stream.read()
    require(hashlib.sha256(code).hexdigest() == archive["sha256"], "member pin")
    for fragment in (b"BIT_L,BIT_T=9,32", b"BIT_M=1+7*BIT_L", b"range(7)"):
        require(fragment in code, "selected producer/stage formula")
    expected_path = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
    expected_data = inputs[expected_path]
    blob = hashlib.sha1(b"blob " + str(len(expected_data)).encode() + b"\0" + expected_data)
    assembly = json.loads(inputs[assembly_path])
    require(blob.hexdigest() == assembly["bit_supplier"]["git_blob_sha1"], "BIT blob binding")
    return assembly, json.loads(expected_data)


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def stage_records(assembly: dict, sigma: int) -> list[dict]:
    require(type(sigma) is int and 1 <= sigma <= 8194, "stock coefficient domain")
    ell = (8 * sigma - 1).bit_length()
    records = []
    for branch, key, chain in (("native", "complex_lower", "bootstrap"),
                               ("conservative", "conservative_complex_lower", "conservative_bootstrap")):
        stages = assembly[chain]
        require(len(stages) == MAX_STAGES, "seven source stages required")
        s = min(Q(assembly["bit_lower"]), (1 - Q(1, 10**24)) * Q(assembly[key])) - Q(1, 10**27)
        old = Q(384599, 10**10)
        for index, source in enumerate(stages, 1):
            a = (1 - s) * s + s * old
            delta = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
            cutoff = max(ceil_q(36 / delta**2), ceil_q(1032 / delta))
            require(old < a < s < 1 - a and 0 < delta <= 1 - s, "stage gaps")
            require(Q(source["exponent"]) == a and Q(source["gap"]) == delta, "source recurrence")
            require(int(source["cutoff_log2"]) == cutoff, "source cutoff")
            require(cutoff >= 3 and cutoff * delta**2 >= 36, "fit quadratic guard")
            require(cutoff * delta >= 2 * (4 + ell), "fit stock guard")
            records.append(dict(branch=branch, stage=index, previous_stage=index - 1,
                                cutoff_log2=str(cutoff), sigma=sigma, ell=ell,
                                external_leaf_factor_hypothesis=1))
            old = a
    return records


@dataclass(frozen=True)
class Action:
    kind: str
    h: tuple[int, ...]
    d: tuple[int, ...] = ()


def wrapper_word(level: int, width: int, fault: str = "") -> list[Action]:
    """Expand nested borrowed-high-digit wrappers with an explicit bounded stack."""
    require(type(level) is int and 0 <= level <= MAX_STAGES, "level capacity")
    require(type(width) is int and 1 <= width <= MAX_WIDTH, "width capacity")
    require(fault in ("", "omit_high", "cancelled_row"), "fault alphabet")
    h, d = tuple(range(width)), tuple(range(width, 2 * width))
    pending = [("call", level, h, d, True)]
    word = []
    for _ in range(MAX_WORD):
        if not pending:
            return word
        kind, j, h, d, root = pending.pop()
        if kind != "call":
            word.append(Action(kind, h, d))
            continue
        body = [("begin", j, h, d, root)]
        if j == 0 or len(h) < 3:
            body.append(("swap", j, h, d, root))
        else:
            hb, db, hh, dh = h[1:], d[1:], h[:1], d[:1]
            body.append(("sub", j, hb, db, False))
            for pass_index in range(2):
                body.extend([("begin", j, hb, db, False),
                             ("call", j - 1, hb, db, False),
                             ("reverse", j, hb, db, False)])
                if root and fault == "cancelled_row":
                    body.append(("negate", j, (2 * width,), (), False))
                body.append(("end", j, hb, db, False))
                body.append((("add" if pass_index == 0 else "diff"), j, hb, db, False))
            if not (root and fault == "omit_high"):
                body.append(("call", j - 1, hh, dh, False))
        body.append(("end", j, h, d, root))
        pending.extend(reversed(body))
        require(len(pending) + len(word) < MAX_WORD, "word capacity")
    raise Rejected("word expansion exhausted")


def apply_action(state: list[list[int]], action: Action, q: int) -> None:
    h, d, kind = action.h, action.d, action.kind
    if kind == "negate":
        state[h[0]] = [(-x) % q for x in state[h[0]]]
    elif kind == "reverse":
        for field in (h, d):
            values = [state[i] for i in reversed(field)]
            for i, value in zip(field, values):
                state[i] = value
    else:
        for left, right in zip(h, d):
            x, y = state[left], state[right]
            if kind == "swap":
                state[left], state[right] = y, x
            elif kind == "sub":
                state[right] = [(b - a) % q for a, b in zip(x, y)]
            elif kind == "add":
                state[right] = [(a + b) % q for a, b in zip(x, y)]
            elif kind == "diff":
                state[right] = [(a - b) % q for a, b in zip(x, y)]
            else:
                raise Rejected("unknown action")


def evaluate(word: list[Action], width: int, q: int, check_calls: bool = True) -> list[list[int]]:
    require(len(word) < MAX_WORD and 1 <= width <= MAX_WIDTH, "evaluation capacity")
    require(q in (3, 5), "fixture radix")
    dimension = 2 * width + 3
    state = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    snapshots = []
    for action in word:
        if action.kind == "begin":
            targets = set(action.h + action.d)
            snapshots.append({i: state[i][:] for i in range(dimension) if i not in targets})
        elif action.kind == "end":
            require(bool(snapshots), "unmatched return")
            old = snapshots.pop()
            if check_calls:
                require(all(state[i] == value for i, value in old.items()), "child spectator/row return")
        else:
            apply_action(state, action, q)
    require(not snapshots, "unclosed call")
    return state


def expected_swap(width: int) -> list[list[int]]:
    dimension = 2 * width + 3
    order = list(range(width, 2 * width)) + list(range(width)) + list(range(2 * width, dimension))
    return [[int(j == i) for j in range(dimension)] for i in order]


def cancelled_row_trace(word: list[Action], width: int, q: int) -> list[int]:
    dimension = 2 * width + 3
    state = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    trace = []
    for action in word:
        if action.kind not in ("begin", "end"):
            apply_action(state, action, q)
        if action.kind == "negate":
            trace.append(state[2 * width][2 * width])
    return trace


def wrapper_checks() -> dict:
    cases, columns, maximum_word = 0, 0, 0
    for level in range(MAX_STAGES + 1):
        for width in range(1, MAX_WIDTH + 1):
            word = wrapper_word(level, width)
            maximum_word = max(maximum_word, len(word))
            for q in (3, 5):
                require(evaluate(word, width, q) == expected_swap(width), "nested endpoint")
                cases += 1
                columns += 2 * width + 3
    bad = wrapper_word(2, 4, "cancelled_row")
    require(evaluate(bad, 4, 3, False) == expected_swap(4), "cancellation control endpoint")
    try:
        evaluate(bad, 4, 3)
    except Rejected as error:
        require(str(error) == "child spectator/row return", "cancellation rejection reason")
    else:
        raise Rejected("endpoint-only completion incorrectly accepted")
    row_trace = cancelled_row_trace(bad, 4, 3)
    require(row_trace == [2, 1], "literal canceled-row witness")
    missing = evaluate(wrapper_word(2, 4, "omit_high"), 4, 3)
    require(missing != expected_swap(4), "omitted high exchange control")
    return dict(cases=cases, basis_columns=columns, maximum_word=maximum_word,
                cancelled_row_endpoint_passes=True, cancelled_row_child_contract_rejected=True,
                cancelled_row_witness=dict(q=3, stage=2, width=4, initial_row=1,
                                           after_body_returns=row_trace),
                omitted_high_exchange_rejected=True)


def result() -> dict:
    assembly, expected = authenticated_inputs()
    bit = expected["nine"]["bit"]
    require((bit["live"], bit["physical"], bit["maxchild"]) == (28416, 28425, 42), "selected BIT producer")
    require(max(map(int, expected["nine"]["profile"])) == 42, "maximal child")
    require(2**17 * 42**28 < 64**28 and bit["physical"] < 2**80, "packet/depth premises")
    sigma = (64**2 + 1) * Q(28, 17)
    require(sigma == 6748, "inherited coefficient")
    stages = stage_records(assembly, int(sigma))
    return dict(status="CONDITIONAL_RESERVE_COMPOSITION_AUDIT", stages=stages,
                wrappers=wrapper_checks(), selected_kappa=assembly["kappa"],
                actual_packet_implementation_checked=False, uniform_time_H2_checked=False,
                new_supplier_or_exponent=False)


def main() -> None:
    require(len(sys.argv) == 1, "no regeneration or extra arguments")
    observed = result()
    recorded = json.loads((PACKAGE / "RESULT.json").read_text())
    require(json.dumps(observed, sort_keys=True) == json.dumps(recorded, sort_keys=True), "required receipt")
    print("PASS_SELECTED_RESERVE_COMPOSITION stages=14 sigma=6748 wrappers=144 child_return_control=1 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Rejected, OSError, ValueError, KeyError, TypeError, tarfile.TarError) as error:
        print(f"FAIL_SELECTED_RESERVE_COMPOSITION: {error}", file=sys.stderr)
        raise SystemExit(1)
