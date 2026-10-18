#!/usr/bin/env python3
"""Source-bound census of paired rank-changing idle-axis transfers."""

from __future__ import annotations

from collections import defaultdict
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE_MAIN = "997e6a9ca7b4f95d50e366f61412fd640d72a88a"
FILL_SHA256 = "8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00"
BASE_ROWS = 9 * 74 * 408
TOTAL_ROWS = 10 * BASE_ROWS
MAX_RAW = 32_000_000

# The allocation and journal are retained byte-for-byte from PR3148's head,
# as already bound by PR3187. Git blob IDs are checked as well as SHA256.
VENDOR_PINS = {
    "BASE-FILL.json.gz": (
        "68b8bae90144248774b1920cd27f9519caa3dc427704d8a9da6d4c491d912fc4",
        "92b49b42b8f381d686a9fb8057e74e4b7548cd5c",
    ),
    "EXCHANGE.json": (
        "5063791f327d067f37478488c97ce449e5b34cfb61d6309fc6924c5e360fe839",
        "f323db0fd94a80f691b1606e813d0738b27058ae",
    ),
    "PROVIDERS.json": (
        "52eb0d85caa7b2d4a93acdf5011f52b793f61ddca86235fb03cd9a09397ad4cd",
        "0b2343675099d0a9fe90da6e1f1e53f50235567e",
    ),
}
NOTICE_PINS = {
    "PR3133-NOTICE": "c9731c9cca25ede32c2a1b3aef6d5b249973cb2ed5fb2494407bdca598763661",
    "PR3133-CREDITS.md": "1d9d8f56d8899f55878e4cb2c4e052b22506444016a51c2e678773505f5189e6",
}

ZERO = (0, 0)
ONE = (1, 0)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bytes(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), f"missing or linked input: {path}")
    require(path.stat().st_size <= MAX_RAW, f"oversized input: {path}")
    return path.read_bytes()


def decode(raw: bytes):
    if raw[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_RAW + 1)
    require(len(raw) <= MAX_RAW, "oversized decoded input")
    return json.loads(raw)


def blob_sha(raw: bytes) -> str:
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    return hashlib.sha1(blob, usedforsecurity=False).hexdigest()


def authenticate() -> None:
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    require(sources["base_commit"] == BASE_MAIN, "unexpected base main")
    retained = {row["local_path"]: row for row in sources.get("retained_sources", [])}
    for name, (sha, blob) in VENDOR_PINS.items():
        row = retained.get("vendor/" + name)
        require(row is not None, "retained source missing from SOURCES.json: " + name)
        require(row["sha256"] == sha and row["git_blob"] == blob, "retained source manifest drift: " + name)
    for row in sources["files"]:
        path = read_bytes(ROOT / row["path"])
        require(hashlib.sha256(path).hexdigest() == row["sha256"], "main source SHA256")
        require(blob_sha(path) == row["git_blob"], "main source Git blob")
    for name, (sha, blob) in VENDOR_PINS.items():
        raw = read_bytes(PACKAGE / "vendor" / name)
        require(hashlib.sha256(raw).hexdigest() == sha, "retained PR3148 SHA256: " + name)
        require(blob_sha(raw) == blob, "retained PR3148 Git blob: " + name)
    for name, sha in NOTICE_PINS.items():
        raw = read_bytes(PACKAGE / "vendor" / name)
        require(hashlib.sha256(raw).hexdigest() == sha, "retained notice SHA256: " + name)


def lifted_row(base, index):
    copy, original = divmod(index, BASE_ROWS)
    time, helper, owner, child, port, offset = base[original]
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def journal_edits(base, journal):
    require(len(base) == BASE_ROWS, "base role count")
    require(journal.get("copies") == 10 and len(journal.get("edits", [])) == 145, "journal size")
    edits = {}
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < TOTAL_ROWS, "journal index")
        require(index not in edits, "duplicate journal edit")
        require(before == lifted_row(base, index), "journal preimage")
        require(len(after) == 6 and all(type(x) is int for x in after), "journal row")
        require(after[:2] == before[:2], "changed call/helper identity")
        edits[index] = after
    return edits


def project_all_ports(base, edits):
    header = {
        "columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
        "dispatch_overrides": [],
    }
    prefix = json.dumps(header, sort_keys=True, separators=(",", ":"))[:-1] + ',"rows":['
    digest = hashlib.sha256(prefix.encode())
    rows = [[] for _ in range(112)]
    for index in range(TOTAL_ROWS):
        row = edits[index] if index in edits else lifted_row(base, index)
        encoded = ("," if index else "") + json.dumps(row, separators=(",", ":"))
        digest.update(encoded.encode())
        if row[2] == 0:
            rows[row[4]].append(row)
    digest.update(b"]}\n")
    require(digest.hexdigest() == FILL_SHA256, "complete PR3148 T740 fill payload")
    require(len(rows) == 112 and all(rows), "port projection coverage")
    return rows


def parity(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def rotate(value, exponent: int):
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[exponent % 4]


def phase(matrix, stream: int, exponent: int) -> None:
    matrix[stream] = [rotate(value, exponent) for value in matrix[stream]]


def shear(matrix, dst: int, src: int, coefficient: int) -> None:
    matrix[dst] = [
        (a + coefficient * c, b + coefficient * d)
        for (a, b), (c, d) in zip(matrix[dst], matrix[src], strict=True)
    ]


def identity():
    return [[ONE if i == j else ZERO for j in range(8)] for i in range(8)]


def stage_blocks(template):
    blocks = {}
    stage = None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if kind == "local_cover_sweep":
            stage = event["stage"]
            blocks[stage] = []
        require(stage is not None, "data event precedes first local stage")
        blocks[stage].append(event)
    require(set(blocks) == set(range(9)), "nine stage blocks")
    return blocks


def run_data_event(matrix, event, context, residual, character):
    recipe = context["recipe"]
    kind = event["kind"]
    qbit = parity(character, recipe["q"])
    if kind == "local_cover_sweep":
        stage = event["stage"]
        local = next(
            item
            for item in context["template"]["recipe"]
            if item["kind"] == "local" and item["stage"] == stage
        )
        x, y = 2 * local["pair"], 2 * local["pair"] + 1
        for side, stream in enumerate((x, y)):
            before = (
                (1 - side) * qbit
                if stage == 0
                else (character & ((1 << (9 + 8 * (stage - 1))) - 1)).bit_count()
                - side * qbit
            )
            phase(matrix, stream, -before)
        if local["reverse"]:
            shear(matrix, x, y, -1)
        else:
            shear(matrix, y, x, 1)
        for side, stream in enumerate((x, y)):
            after = (character & ((1 << (9 + 8 * stage)) - 1)).bit_count() - side * qbit
            phase(matrix, stream, after)
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            exponent = sum(parity(character, v) for v in residual[child])
            exponent += 2 * parity(
                character, recipe["idle_children"][child]["translation_after"]
            )
            phase(matrix, 2 * event["pair"] + side, exponent)
    elif kind == "bridge":
        dst, src, coefficient = event["dst"], event["src"], event["coefficient"]
        shear(matrix, 2 * dst, 2 * src, coefficient)
        shear(matrix, 2 * src + 1, 2 * dst + 1, -coefficient)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            phase(matrix, 2 * pair + 1, 2 * qbit)
    elif kind == "terminal":
        for pair in range(event["pairs"]):
            matrix[2 * pair], matrix[2 * pair + 1] = (
                matrix[2 * pair + 1],
                [rotate(value, 2) for value in matrix[2 * pair]],
            )
    else:
        raise ValueError("unknown physical data event: " + kind)


def replay(context, residual, character, blocks):
    require(type(character) is int and 0 <= character < 1 << 73, "Fourier character")
    matrix = identity()
    for time, (stage, replica) in enumerate(context["order"]):
        for stream, axes in context["hosts"].get(time, ()):
            phase(matrix, stream, sum(parity(character, v) for v in axes))
        if replica == 0:
            for event in blocks[stage]:
                run_data_event(matrix, event, context, residual, character)
    return matrix


def prepare_port(port, rows, order, dispatch, providers, plan, template, recipes):
    recipe = recipes[port]
    hosts = defaultdict(list)
    used_positions = defaultdict(set)
    hosted_axes = defaultdict(list)
    full_axes = [list(map(int, child["orthogonal_axes"])) for child in recipe["idle_children"]]
    for time, helper, owner, child, row_port, offset in rows:
        require(owner == 0 and row_port == port, "owner/port projection")
        stage, replica = order[time]
        tag = dispatch[(stage, replica % 74)]
        width = providers[tag]["widths"][helper]
        axes = full_axes[child]
        require(offset >= 0 and offset + width <= len(axes), "host slice range")
        positions = set(range(offset, offset + width))
        require(not used_positions[child] & positions, "host slice overlap")
        used_positions[child].update(positions)
        hosted_axes[child].extend(axes[offset : offset + width])
        stream = 2 * plan["pairs"][str(child)] + plan["sides"][str(child)]
        hosts[time].append((stream, axes[offset : offset + width]))
    residual = {}
    for child, axes in enumerate(full_axes):
        require(
            used_positions[child] == set(range(len(used_positions[child]))),
            "noncompact hosted prefix",
        )
        residual[child] = [v for i, v in enumerate(axes) if i not in used_positions[child]]
    return {
        "recipe": recipe,
        "template": template,
        "order": order,
        "hosts": hosts,
        "residual": residual,
        "full_axes": full_axes,
        "hosted_axes": hosted_axes,
    }


def orthonormal(values):
    return all(parity(a, b) == int(i == j) for i, a in enumerate(values) for j, b in enumerate(values))


def paired_overlay(residual, source_left, source_right, target_left, target_right, axis):
    result = {child: list(values) for child, values in residual.items()}
    for child in (source_left, source_right):
        require(axis in result[child], "axis missing from both source children")
        result[child].remove(axis)
    result[target_left].append(axis)
    result[target_right].append(axis)
    return result


def matrix_differences(left, right):
    return [
        [i, j, list(left[i][j]), list(right[i][j])]
        for i in range(8)
        for j in range(8)
        if left[i][j] != right[i][j]
    ]


def baseline_target(character):
    value = rotate(ONE, character.bit_count())
    return [[value if i == j else ZERO for j in range(8)] for i in range(8)]


def check_baseline(context, residual, blocks):
    modes = [0] + [1 << i for i in range(73)] + [(1 << 73) - 1]
    modes += [(1 << i) | (1 << (i + 1)) for i in range(72)]
    for character in modes:
        require(
            replay(context, residual, character, blocks) == baseline_target(character),
            "baseline exact physical operator",
        )
    return len(modes)


def check_candidate_pair(context, blocks, source_children, target_children):
    # Each selected axis is an orthogonal source-basis vector and is orthogonal
    # to every original destination axis, including the destination's hosted slice.
    baseline = context["residual"]
    for child in source_children + target_children:
        require(orthonormal(baseline[child]), "paired residual basis is not orthonormal")
    eligible = []
    for axis in sorted(set(baseline[source_children[0]]) & set(baseline[source_children[1]])):
        if any(parity(axis, v) for child in target_children for v in context["full_axes"][child]):
            continue
        if any(len(baseline[child]) + 1 > 51 for child in target_children):
            continue
        trial = paired_overlay(
            baseline,
            source_children[0],
            source_children[1],
            target_children[0],
            target_children[1],
            axis,
        )
        # Check the complete hosted + residual basis at all affected children.
        valid = True
        for child in set(source_children + target_children):
            combined = context["hosted_axes"].get(child, []) + trial[child]
            if not orthonormal(combined):
                valid = False
                break
        if not valid:
            continue
        eligible.append(axis)
    failures = 0
    witness = None
    for axis in eligible:
        original = replay(context, baseline, axis, blocks)
        altered = replay(
            context,
            paired_overlay(
                baseline,
                source_children[0],
                source_children[1],
                target_children[0],
                target_children[1],
                axis,
            ),
            axis,
            blocks,
        )
        differences = matrix_differences(original, altered)
        if differences:
            failures += 1
            if witness is None:
                witness = {
                    "axis": axis,
                    "baseline": original,
                    "overlay": altered,
                    "differences": differences,
                }
    return len(eligible), failures, witness


def check_mutations(base, journal):
    altered = json.loads(json.dumps(journal))
    altered["edits"][0][1][0] ^= 1
    try:
        journal_edits(base, altered)
    except ValueError:
        return True
    return False


def run():
    authenticate()
    vendor = PACKAGE / "vendor"
    base = decode(read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    journal = decode(read_bytes(vendor / "EXCHANGE.json"))
    rows_by_port = project_all_ports(base, journal_edits(base, journal))
    order_base = decode(read_bytes(ROOT / "research/rank7-joint-endframes/allocation/ORDER.json"))
    require(len(order_base) == 666, "base chronology count")
    order = [[stage, replica + 74 * copy] for stage, replica in order_base for copy in range(10)]
    dispatch_rows = decode(read_bytes(ROOT / "research/rank7-joint-endframes/allocation/DISPATCH.json"))
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    require(len(dispatch) == 666, "base dispatch count")
    providers = decode(read_bytes(vendor / "PROVIDERS.json"))
    plan = decode(read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz"))
    template = decode(read_bytes(ROOT / "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz"))
    recipes = decode(read_bytes(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"))["recipes"]
    require(len(recipes) == 112, "port recipe count")
    blocks = stage_blocks(template)

    forward_count = reverse_count = forward_failures = reverse_failures = 0
    per_port = []
    first_forward_witness = None
    baseline_modes = None
    for port in range(112):
        context = prepare_port(port, rows_by_port[port], order, dispatch, providers, plan, template, recipes)
        context["residual"] = context.pop("residual")
        if port == 0:
            baseline_modes = check_baseline(context, context["residual"], blocks)
        require(
            replay(context, context["residual"], 0, blocks) == identity(),
            "zero-character baseline identity control",
        )
        f, ff, fw = check_candidate_pair(
            context, blocks, (8, 10), (12, 13)
        )
        r, rf, rw = check_candidate_pair(
            context, blocks, (12, 13), (8, 10)
        )
        forward_count += f
        reverse_count += r
        forward_failures += ff
        reverse_failures += rf
        per_port.append([port, f, ff, r, rf])
        if port == 0:
            first_forward_witness = fw
    require(check_mutations(base, journal), "mutated journal preimage accepted")
    require(baseline_modes == 147, "baseline positive-control mode count")
    require(forward_count == forward_failures and reverse_count == reverse_failures, "unrejected eligible transfer")
    require(forward_count == reverse_count == 2688, "paired transfer count")
    require(all(row[1] == row[2] == row[3] == row[4] == 24 for row in per_port), "per-port paired census")
    require(first_forward_witness is not None and first_forward_witness["axis"] == 7, "exact forward witness")
    return {
        "status": "PASS_NO_OPERATOR_PRESERVING_RANK_CHANGING_PAIRED_TRANSFER",
        "base_main": BASE_MAIN,
        "fill_payload_sha256": FILL_SHA256,
        "authenticated_fill_rows": TOTAL_ROWS,
        "ports": 112,
        "baseline_modes_port0": baseline_modes,
        "forward": {"eligible": forward_count, "fail_at_own_axis_character": forward_failures},
        "reverse": {"eligible": reverse_count, "fail_at_own_axis_character": reverse_failures},
        "port0_forward_witness": first_forward_witness,
        "per_port_counts": per_port,
        "selected_frontier_changed": False,
        "new_kappa": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    expected_path = PACKAGE / "RESULT.json"
    if args.write_result:
        expected_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif expected_path.is_file():
        expected = json.loads(read_bytes(expected_path))
        require(result == expected, "stored result differs")
    print(
        result["status"]
        + f" ports={result['ports']} forward={result['forward']['eligible']}"
        + f" reverse={result['reverse']['eligible']} baseline_modes={result['baseline_modes_port0']}"
        + " no_new_kappa"
    )


if __name__ == "__main__":
    main()
