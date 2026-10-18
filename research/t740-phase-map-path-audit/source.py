# SPDX-License-Identifier: Apache-2.0
"""Independent, bounded projection of canonical T740 JSON to primitive gates.

The completed-call interpretation follows PR3187/3199/3272/3297. No predecessor
Python module is loaded. This is not a revalidation of the physical interface.
"""

import gzip
import hashlib
import io
import json
from dataclasses import dataclass
from pathlib import Path

BITS = 73
BASE_ROWS = 9 * 74 * 408
MAX_BYTES = 32_000_000
MAX_GATES = 512
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATHS = {
    "fill": "research/idle-star-paired-axis-census/vendor/BASE-FILL.json.gz",
    "edits": "research/idle-star-paired-axis-census/vendor/EXCHANGE.json",
    "providers": "research/idle-star-paired-axis-census/vendor/PROVIDERS.json",
    "order": "research/rank7-joint-endframes/allocation/ORDER.json",
    "dispatch": "research/rank7-joint-endframes/allocation/DISPATCH.json",
    "plan": "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz",
    "template": "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz",
    "phases": "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_inputs(root: Path = ROOT) -> dict:
    pins = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    pins = {entry["path"]: entry for entry in pins}
    result = {}
    for name, relative in PATHS.items():
        path = root / relative
        require(path.is_file() and not path.is_symlink(), "missing or linked input")
        require(path.stat().st_size <= MAX_BYTES, "input exceeds byte limit")
        raw = path.read_bytes()
        pin = pins[relative]
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source hash: " + relative)
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
                "source blob: " + relative)
        if raw[:2] == b"\x1f\x8b":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "decoded input exceeds byte limit")
        result[name] = json.loads(raw)
    return result


def lifted(base: list, index: int) -> list[int]:
    copy, original = divmod(index, BASE_ROWS)
    time, helper, owner, child, port, offset = base[original]
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def project_rows(data: dict) -> list[list[int]]:
    base = data["fill"]["rows"]
    require(len(base) == BASE_ROWS, "base role count")
    journal = data["edits"]
    require(journal["copies"] == 10 and len(journal["edits"]) == 145, "journal size")
    edits = {}
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < 10 * BASE_ROWS, "edit index")
        require(index not in edits and before == lifted(base, index), "edit preimage")
        require(len(after) == 6 and all(type(x) is int for x in after), "edit row")
        require(before[:2] == after[:2], "call/helper identity changed")
        edits[index] = after
    # At owner zero, only the zero lift can contribute an unedited row.
    rows = [lifted(base, index) for index, row in enumerate(base)
            if index not in edits and row[2] == row[4] == 0]
    rows.extend(row for row in edits.values() if row[2] == row[4] == 0)
    require(len(rows) == 30, "owner-zero port-zero projection")
    return sorted(rows)


def hosting(data: dict) -> tuple[list, dict, list]:
    require(len(data["order"]) == 666, "base order size")
    order = [(stage, owner + 74 * copy)
             for stage, owner in data["order"] for copy in range(10)]
    dispatch = {(stage, owner): tag for stage, owner, tag in data["dispatch"]}
    require(len(dispatch) == 666, "dispatch size")
    children = data["phases"]["recipes"][0]["idle_children"]
    require(len(children) == 20, "child count")
    full = [list(map(int, child["orthogonal_axes"])) for child in children]
    used, hosts = [set() for _ in children], {}
    for time, helper, _owner, child, _port, offset in project_rows(data):
        stage, caller = order[time]
        width = data["providers"][dispatch[stage, caller % 74]]["widths"][helper]
        require(0 <= child < 20 and 0 <= offset < offset + width <= len(full[child]),
                "hosted interval range")
        positions = set(range(offset, offset + width))
        require(not used[child].intersection(positions), "hosted overlap")
        used[child].update(positions)
        stream = 2 * data["plan"]["pairs"][str(child)] + data["plan"]["sides"][str(child)]
        hosts.setdefault(time, []).append((stream, full[child][offset:offset + width]))
    residual = []
    for child, axes in enumerate(full):
        require(len(axes) <= BITS and all(0 < a < 1 << BITS for a in axes), "axis range")
        require(all((a & b).bit_count() % 2 == int(i == j)
                    for i, a in enumerate(axes) for j, b in enumerate(axes)), "orthonormal axes")
        require(used[child] == set(range(len(used[child]))), "hosted prefix")
        residual.append([a for i, a in enumerate(axes) if i not in used[child]])
    return order, hosts, residual


@dataclass(frozen=True)
class Gate:
    kind: str
    row: int
    source: int = -1
    coefficient: int = 1
    phases: tuple[tuple[int, int], ...] = ()
    site: int = -1


def phase(row: int, axes: list[int], coefficient: int = 1, site: int = -1) -> Gate:
    require(len(axes) <= BITS and 0 <= row < 8, "phase gate bounds")
    require(-1 <= site < 20 and all(0 <= a < 1 << BITS for a in axes), "phase axes/site")
    return Gate("phase", row, phases=tuple((a, coefficient) for a in axes), site=site)


def coordinate_prefix(width: int) -> list[int]:
    require(0 <= width <= BITS, "prefix width")
    return [1 << index for index in range(width)]


def local_gates(event: dict, data: dict) -> list[Gate]:
    stage = event["stage"]
    matches = [row for row in data["template"]["recipe"]
               if row["kind"] == "local" and row["stage"] == stage]
    require(len(matches) == 1 and 0 <= stage < 9, "unique local stage")
    local = matches[0]
    x, y = 2 * local["pair"], 2 * local["pair"] + 1
    q = data["phases"]["recipes"][0]["q"]
    gates = []
    for side, row in enumerate((x, y)):
        if stage:
            gates.append(phase(row, coordinate_prefix(9 + 8 * (stage - 1)), -1))
            gates.append(phase(row, [q], side))
        else:
            gates.append(phase(row, [q], side - 1))
    gates.append(Gate("add", x, y, -1) if local["reverse"] else Gate("add", y, x, 1))
    for side, row in enumerate((x, y)):
        gates.extend((phase(row, coordinate_prefix(9 + 8 * stage)), phase(row, [q], -side)))
    return gates


def event_gates(event: dict, data: dict, residual: list) -> list[Gate]:
    kind = event["kind"]
    if kind == "local_cover_sweep":
        return local_gates(event, data)
    if kind == "idle_cover_sweep":
        gates = []
        for side, child in enumerate(event["child_indices"]):
            row = 2 * event["pair"] + side
            translation = data["phases"]["recipes"][0]["idle_children"][child]["translation_after"]
            gates.extend((phase(row, residual[child], site=child), phase(row, [translation], 2)))
        return gates
    if kind == "bridge":
        d, s, c = event["dst"], event["src"], event["coefficient"]
        require(c in (-1, 1) and d != s, "bridge coefficient/rows")
        return [Gate("add", 2 * d, 2 * s, c), Gate("add", 2 * s + 1, 2 * d + 1, -c)]
    if kind == "terminal_Y_translations":
        q = data["phases"]["recipes"][0]["q"]
        return [phase(2 * pair + 1, [q], 2) for pair in event["pairs"]]
    if kind == "terminal":
        require(event["pairs"] == 4, "terminal width")
        return [Gate("exchange", 2 * pair, 2 * pair + 1) for pair in range(4)]
    raise ValueError("unknown data event: " + kind)


def gates_from_inputs(data: dict) -> tuple[list[Gate], list[int]]:
    order, hosts, residual = hosting(data)
    events = data["template"]["execution_schedule"]
    require(len(events) <= 64, "schedule event bound")
    blocks, current = {}, -1
    for event in events:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue  # The inherited projection concerns data streams only.
        if event["kind"] == "local_cover_sweep":
            current = event["stage"]
            require(current not in blocks, "duplicate stage")
            blocks[current] = []
        require(current >= 0, "event before first stage")
        blocks[current].extend(event_gates(event, data, residual))
    require(set(blocks) == set(range(9)), "stage coverage")
    gates, seen_stages = [], []
    for time, (stage, owner) in enumerate(order):
        gates.extend(phase(row, axes) for row, axes in hosts.get(time, []))
        if owner == 0:
            seen_stages.append(stage)
            gates.extend(blocks[stage])
    require(sorted(seen_stages) == list(range(9)), "owner-zero stage chronology")
    gates.extend(phase(row, coordinate_prefix(BITS), -1) for row in range(8))
    require(len(gates) <= MAX_GATES, "primitive gate bound")
    sites = [gate.site for gate in gates if gate.site >= 0]
    require(sorted(sites) == list(range(20)), "one insertion per site")
    return gates, [len(axes) for axes in residual]
