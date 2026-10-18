#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact replay of PR3190's two port-0 remainder transfers."""

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_ROWS = 9 * 74 * 408
TOTAL_ROWS = 10 * BASE_ROWS
FILL_SHA256 = "8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00"
AXIS72 = 1 << 72
ZERO = (0, 0)
ONE = (1, 0)


class VerificationError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def pinned_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    source_rows = {row["path"]: row for row in manifest["files"]}
    result = {}
    for row in manifest.get("retained_files", []):
        path = HERE / row["local_path"]
        need(path.is_file() and not path.is_symlink(), "missing or linked input: " + row["local_path"])
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256 mismatch: " + row["local_path"])
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        actual_blob = hashlib.sha1(blob, usedforsecurity=False).hexdigest()
        need(actual_blob == row["git_blob"], "retained Git blob mismatch: " + row["local_path"])
        if path.name == "PR3190-MOVES.json.gz":
            need(
                row.get("origin_head") == "5e4a3235169edddd033889da4e9f47635ff50c3e"
                and row.get("origin_path") == "research/rank7-idle-remainder-donors-t740/MOVES.json.gz"
                and row.get("origin_git_blob") == actual_blob,
                "upstream PR3190 move-list provenance record",
            )
        upstream = source_rows.get(row["upstream_path"])
        need(upstream is not None, "retained input lacks a source row: " + row["upstream_path"])
        need(upstream["sha256"] == row["sha256"] and upstream["git_blob"] == row["git_blob"],
             "retained input differs from its source row: " + row["upstream_path"])
        pin = upstream.get("pin")
        pinned_head = pin.split(":", 2)[1] if pin else manifest["base_commit"]
        need(pinned_head == row["head"], "retained input head differs from source pin: " + row["local_path"])
        result[path.name] = raw
    need(len(result) == 9, "expected the nine declared source inputs")
    return result


def decode_json(raw, compressed=False):
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(32_000_001)
    need(len(raw) <= 32_000_000, "decoded input exceeds the bounded size")
    return json.loads(raw)


def lifted_row(base, index):
    copy, original = divmod(index, BASE_ROWS)
    time, helper, owner, child, port, offset = base[original]
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def authenticated_port_zero(base_raw, journal_raw):
    need(hashlib.sha256(base_raw).hexdigest() == json.loads(journal_raw)["base_fill_sha256"],
         "exchange journal does not bind the base fill bytes")
    base = decode_json(base_raw, compressed=True)["rows"]
    journal = json.loads(journal_raw)
    need(len(base) == BASE_ROWS, "base fill row count")
    need(journal["copies"] == 10 and len(journal["edits"]) == 145, "exchange journal dimensions")
    edits = {}
    for index, before, after in journal["edits"]:
        need(type(index) is int and 0 <= index < TOTAL_ROWS, "exchange index range")
        need(index not in edits, "duplicate exchange index")
        need(before == lifted_row(base, index), "exchange preimage differs from lifted source row")
        need(len(after) == 6 and all(type(value) is int for value in after), "exchange row shape")
        need(after[:2] == before[:2], "exchange changes call or helper identity")
        edits[index] = after

    header = {
        "columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
        "dispatch_overrides": [],
    }
    prefix = json.dumps(header, sort_keys=True, separators=(",", ":"))[:-1] + ',"rows":['
    digest = hashlib.sha256(prefix.encode("utf-8"))
    projection = []
    for index in range(TOTAL_ROWS):
        row = edits[index] if index in edits else lifted_row(base, index)
        encoded = ("," if index else "") + json.dumps(row, separators=(",", ":"))
        digest.update(encoded.encode("utf-8"))
        if row[2] == 0 and row[4] == 0:
            projection.append(row)
    digest.update(b"]}\n")
    need(digest.hexdigest() == FILL_SHA256, "complete canonical PR3148 fill digest")
    need(len(projection) == 30, "owner-0, port-0 hosted role count")
    return projection


def parity(left, right):
    return (int(left) & int(right)).bit_count() & 1


def gaussian_product(left, right):
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c)


def gaussian_sum(values):
    real = imag = 0
    for a, b in values:
        real += a
        imag += b
    return (real, imag)


def matrix_identity(size=8):
    return [[ONE if row == col else ZERO for col in range(size)] for row in range(size)]


def matrix_product(left, right):
    """Dense exact product over Z[i]; operators are composed by left multiplication."""
    size = len(left)
    need(size == 8 and len(right) == size, "operator matrix dimension")
    need(all(len(row) == size for row in left + right), "operator matrix is not square")
    return [
        [
            gaussian_sum(gaussian_product(left[row][k], right[k][col]) for k in range(size))
            for col in range(size)
        ]
        for row in range(size)
    ]


def i_power(exponent):
    return ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent % 4]


def phase_gate(stream, exponent):
    gate = matrix_identity()
    gate[stream][stream] = i_power(exponent)
    return gate


def shear_gate(destination, source, coefficient):
    need(destination != source, "shear source equals destination")
    gate = matrix_identity()
    gate[destination][source] = (coefficient, 0)
    return gate


def apply_phase(operator, stream, exponent):
    return matrix_product(phase_gate(stream, exponent), operator)


def apply_shear(operator, destination, source, coefficient):
    return matrix_product(shear_gate(destination, source, coefficient), operator)


def build_context(rows, inputs):
    phases = decode_json(inputs["DATA-PHASES.json"])
    recipes = phases["recipes"]
    need(len(recipes) == 112 and all(recipe["port"] == p for p, recipe in enumerate(recipes)),
         "port recipe indexing")
    recipe = recipes[0]

    base_order = decode_json(inputs["ORDER.json"])
    dispatch_rows = decode_json(inputs["DISPATCH.json"])
    need(len(base_order) == len(dispatch_rows) == 666, "base chronology/dispatch size")
    order = [[stage, replica + 74 * copy] for stage, replica in base_order for copy in range(10)]
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    need(len(dispatch) == 666, "duplicate dispatch key")

    providers = decode_json(inputs["PROVIDERS.json"])
    plan = decode_json(inputs["PLAN.json.gz"], compressed=True)
    template = decode_json(inputs["TEMPLATE.json.gz"], compressed=True)
    moves_doc = decode_json(inputs["PR3190-MOVES.json.gz"], compressed=True)
    need(moves_doc["columns"] == ["replica", "port", "donor_child", "receiver_child", "axis"],
         "PR3190 move columns")
    need(len(moves_doc["moves"]) == 391964, "PR3190 move inventory")
    moves = [
        (int(donor), int(receiver), int(axis))
        for replica, port, donor, receiver, axis in moves_doc["moves"]
        if replica == 0 and port == 0
    ]

    used = defaultdict(set)
    hosts = defaultdict(list)
    for time, helper, owner, child, port, offset in rows:
        need(owner == port == 0, "projection role destination")
        need(0 <= time < len(order), "fill time outside lifted chronology")
        stage, replica = order[time]
        need((stage, replica % 74) in dispatch, "missing provider dispatch")
        tag = dispatch[(stage, replica % 74)]
        width = int(providers[tag]["widths"][helper])
        axes = [int(value) for value in recipe["idle_children"][child]["orthogonal_axes"]]
        positions = set(range(offset, offset + width))
        need(offset >= 0 and offset + width <= len(axes), "hosted slice out of bounds")
        need(not (used[child] & positions), "overlapping hosted slice")
        used[child].update(positions)
        stream = 2 * int(plan["pairs"][str(child)]) + int(plan["sides"][str(child)])
        hosts[time].append((stream, axes[offset:offset + width]))

    residual = {}
    for child, entry in enumerate(recipe["idle_children"]):
        need(used[child] == set(range(len(used[child]))), "hosted axes are not a compact prefix")
        residual[child] = [
            int(value) for position, value in enumerate(entry["orthogonal_axes"])
            if position not in used[child]
        ]

    blocks = {}
    active_stage = None
    skipped = Counter()
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            skipped[kind] += 1
            continue
        if kind == "local_cover_sweep":
            active_stage = int(event["stage"])
            need(active_stage not in blocks, "duplicate local stage")
            blocks[active_stage] = []
            blocks[active_stage].append(event)
            continue
        need(active_stage is not None, "data event precedes first local stage")
        blocks[active_stage].append(event)
    need(sorted(blocks) == list(range(9)), "expected nine ordered local stage blocks")
    local = {
        int(event["stage"]): event
        for event in template["recipe"]
        if event["kind"] == "local"
    }
    need(set(local) == set(range(9)), "local recipe stage inventory")

    return {
        "recipe": recipe,
        "plan": plan,
        "order": order,
        "hosts": hosts,
        "residual": residual,
        "moves": moves,
        "blocks": blocks,
        "local": local,
        "skipped": dict(skipped),
    }


def translations_for_rule(recipe, donor, receiver):
    values = []
    for stage in recipe["stage_alignment"]:
        values.extend(int(stage[key]) for key in ("entry_X", "exit_X", "entry_Y", "exit_Y"))
    values.append(int(recipe["terminal_Y_translation"]))
    values.extend(int(recipe["idle_children"][child]["translation_after"]) for child in (donor, receiver))
    return values


def transfer_axes(recipe, original, moves):
    current = {child: list(axes) for child, axes in original.items()}
    for donor, receiver, axis in moves:
        need(donor != receiver, "self transfer")
        need(axis in current[donor], "axis not in donor residual")
        need(all(parity(axis, vector) == 0 for vector in current[receiver]),
             "axis fails receiver orthogonality")
        need(all(parity(axis, vector) == 0 for vector in translations_for_rule(recipe, donor, receiver)),
             "axis fails translation rule")
        current[donor].remove(axis)
        current[receiver].append(axis)
    for axes in current.values():
        need(len(axes) <= 51, "rank cap 51")
        need(
            all(parity(left, right) == int(i == j)
                for i, left in enumerate(axes)
                for j, right in enumerate(axes)),
            "transferred axes are not orthonormal",
        )
    need(
        Counter(axis for axes in original.values() for axis in axes)
        == Counter(axis for axes in current.values() for axis in axes),
        "transfer changes the full axis multiset",
    )
    return current


def stage_blocks_apply(operator, event, context, residual, character):
    kind = event["kind"]
    recipe = context["recipe"]
    qbit = parity(character, recipe["q"])
    if kind == "local_cover_sweep":
        stage = int(event["stage"])
        local = context["local"][stage]
        x = 2 * int(local["pair"])
        y = x + 1
        for side, stream in enumerate((x, y)):
            if stage == 0:
                before = (1 - side) * qbit
            else:
                lower = (1 << (9 + 8 * (stage - 1))) - 1
                before = (character & lower).bit_count() - side * qbit
            operator = apply_phase(operator, stream, -before)
        if local["reverse"]:
            operator = apply_shear(operator, x, y, -1)
        else:
            operator = apply_shear(operator, y, x, 1)
        for side, stream in enumerate((x, y)):
            lower = (1 << (9 + 8 * stage)) - 1
            after = (character & lower).bit_count() - side * qbit
            operator = apply_phase(operator, stream, after)
        return operator

    if kind == "idle_cover_sweep":
        for side, child_value in enumerate(event["child_indices"]):
            child = int(child_value)
            exponent = sum(parity(character, axis) for axis in residual[child])
            exponent += 2 * parity(character, recipe["idle_children"][child]["translation_after"])
            operator = apply_phase(operator, 2 * int(event["pair"]) + side, exponent)
        return operator

    if kind == "bridge":
        destination = int(event["dst"])
        source = int(event["src"])
        coefficient = int(event["coefficient"])
        operator = apply_shear(operator, 2 * destination, 2 * source, coefficient)
        operator = apply_shear(operator, 2 * source + 1, 2 * destination + 1, -coefficient)
        return operator

    if kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            operator = apply_phase(operator, 2 * int(pair) + 1, 2 * qbit)
        return operator

    if kind == "terminal":
        gate = matrix_identity()
        for pair in range(int(event["pairs"])):
            even, odd = 2 * pair, 2 * pair + 1
            gate[even] = [ONE if column == odd else ZERO for column in range(8)]
            gate[odd] = [(-1, 0) if column == even else ZERO for column in range(8)]
        return matrix_product(gate, operator)

    raise VerificationError("unknown physical data event: " + kind)


def replay(context, residual, character):
    need(type(character) is int and 0 <= character < (1 << 73), "Fourier character range")
    operator = matrix_identity()
    for time, (stage, replica) in enumerate(context["order"]):
        for stream, axes in context["hosts"].get(time, ()):
            exponent = sum(parity(character, axis) for axis in axes)
            operator = apply_phase(operator, stream, exponent)
        if replica == 0:
            for event in context["blocks"][stage]:
                operator = stage_blocks_apply(operator, event, context, residual, character)
    return operator


def scalar_operator(character):
    scalar = i_power(character.bit_count())
    return [[scalar if row == col else ZERO for col in range(8)] for row in range(8)]


def differences(before, after):
    return [
        (row, col, before[row][col], after[row][col])
        for row in range(8)
        for col in range(8)
        if before[row][col] != after[row][col]
    ]


EXPECTED = {
    "14->8": [
        (3, 1, (0, 0), (-1, 1)),
        (3, 3, (0, 1), (1, 0)),
        (5, 1, (0, 0), (-1, 1)),
        (5, 3, (0, 0), (1, -1)),
        (6, 6, (0, 1), (-1, 0)),
    ],
    "15->10": [
        (0, 2, (0, 0), (-1, 1)),
        (0, 4, (0, 0), (-1, 1)),
        (2, 2, (0, 1), (1, 0)),
        (2, 4, (0, 0), (1, -1)),
        (7, 7, (0, 1), (-1, 0)),
    ],
}


def main():
    inputs = pinned_inputs()
    rows = authenticated_port_zero(inputs["BASE-FILL.json.gz"], inputs["EXCHANGE.json"])
    context = build_context(rows, inputs)
    character = AXIS72
    moves = context["moves"]
    need(moves == [(14, 8, AXIS72), (15, 10, AXIS72)], "literal port-0 moves")
    residual = context["residual"]
    need(residual[14] == residual[15] == [AXIS72], "donor rank-1 hosted remainders")
    need(
        [2 * int(context["plan"]["pairs"][str(c)])
         + int(context["plan"]["sides"][str(c)])
         for c in (14, 15, 8, 10)] == [2, 3, 6, 7],
        "physical stream mapping",
    )

    baseline = replay(context, residual, character)
    need(baseline == scalar_operator(character), "baseline is not i times the identity")
    after_by_move = {}
    for donor, receiver, axis in moves:
        label = f"{donor}->{receiver}"
        moved = transfer_axes(context["recipe"], residual, [(donor, receiver, axis)])
        after = replay(context, moved, character)
        after_by_move[label] = differences(baseline, after)
        need(after_by_move[label] == EXPECTED[label], "isolated move matrix differs: " + label)

    joint_axes = transfer_axes(context["recipe"], residual, moves)
    joint = differences(baseline, replay(context, joint_axes, character))
    expected_joint = sorted(EXPECTED["14->8"] + EXPECTED["15->10"], key=lambda item: (item[0], item[1]))
    need(joint == expected_joint, "joint changes are not the disjoint union of isolated changes")
    need(len(after_by_move["14->8"]) == len(after_by_move["15->10"]) == 5, "isolated change counts")
    need(len(joint) == 10, "joint change count")

    empty = transfer_axes(context["recipe"], residual, [])
    need(replay(context, empty, character) == baseline, "empty overlay control")

    for label, invalid in (
        ("axis outside donor remainder", [(14, 8, 1 << 71)]),
        ("self transfer", [(14, 14, AXIS72)]),
    ):
        try:
            transfer_axes(context["recipe"], residual, invalid)
        except VerificationError:
            pass
        else:
            raise VerificationError("failure control accepted: " + label)

    print(
        "PASS_INDEPENDENT_PR3190_PORT0 "
        "fill_rows=2717280 role_rows=30 moves=2 character=2^72 "
        "baseline=iI8 isolated_changes=5+5 joint_changes=10 controls=3"
    )


if __name__ == "__main__":
    main()
