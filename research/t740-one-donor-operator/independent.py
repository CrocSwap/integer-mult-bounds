#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Independent raw-input replay using bit-packed Boolean quadratic phases.

No executable predecessor or primary-checker module is imported.  Polynomial
coefficients are integers, and the final fourth-root census is exact.
"""

from collections import Counter
from functools import cache
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BITS = 73
SITES = (8, 10, 12, 13, 14)
ZERO_PHASE = (0, 0, 0)
INPUTS = {
    "fill": "research/idle-star-paired-axis-census/vendor/BASE-FILL.json.gz",
    "journal": "research/idle-star-paired-axis-census/vendor/EXCHANGE.json",
    "providers": "research/idle-star-paired-axis-census/vendor/PROVIDERS.json",
    "order": "research/rank7-joint-endframes/allocation/ORDER.json",
    "dispatch": "research/rank7-joint-endframes/allocation/DISPATCH.json",
    "plan": "research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz",
    "template": "research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz",
    "recipes": "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    rows = {row["path"]: row for row in manifest["files"]}
    result = {}
    for name, relative in INPUTS.items():
        require(relative in rows, "missing independent input pin: " + relative)
        row = rows[relative]
        require(row.get("usage") == "input", "independent source is not an input")
        path = ROOT / relative
        require(path.is_file() and not path.is_symlink(), "invalid independent source")
        require(path.stat().st_size <= 32_000_000, "oversized independent source")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
                "source Git blob")
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        require(len(raw) <= 32_000_000, "oversized decoded independent source")
        result[name] = json.loads(raw)
    return result


def context(data):
    """Project the requested owner directly, without the full-fill compiler."""
    base = data["fill"]["rows"]
    count = 9 * 74 * 408
    require(len(base) == count, "base fill row count")

    def lift(index):
        copy, original = divmod(index, count)
        time, helper, owner, child, port, offset = base[original]
        return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]

    edits = {}
    journal = data["journal"]
    require(journal["copies"] == 10 and len(journal["edits"]) == 145,
            "journal dimensions")
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < 10 * count, "edit index")
        require(index not in edits and before == lift(index), "edit preimage")
        require(len(after) == 6 and all(type(v) is int for v in after), "edit row")
        require(after[:2] == before[:2], "edit call/helper identity")
        edits[index] = after
    # Only copy zero can have owner zero before the journal.  Include any
    # journal row moved into this owner/port, and exclude its old incarnation.
    rows = [lift(index) for index, row in enumerate(base)
            if row[2] == 0 and row[4] == 0 and index not in edits]
    rows.extend(row for row in edits.values() if row[2] == 0 and row[4] == 0)
    require(len(rows) == 30, "owner-zero port-zero projection")
    base_order = data["order"]
    require(len(base_order) == 666, "base order length")
    order = [(stage, replica + 74 * copy) for stage, replica in base_order
             for copy in range(10)]
    dispatch = {(stage, replica): tag for stage, replica, tag in data["dispatch"]}
    require(len(dispatch) == 666, "dispatch coverage")
    recipe = data["recipes"]["recipes"][0]
    full = [list(map(int, child["orthogonal_axes"]))
            for child in recipe["idle_children"]]
    used = [set() for _ in full]
    hosts = {}
    for time, helper, owner, child, port, offset in rows:
        require(owner == port == 0, "projection identity")
        stage, replica = order[time]
        width = data["providers"][dispatch[stage, replica % 74]]["widths"][helper]
        require(0 <= offset and offset + width <= len(full[child]), "host slice range")
        positions = set(range(offset, offset + width))
        require(not used[child] & positions, "overlapping hosted slices")
        used[child].update(positions)
        stream = 2 * data["plan"]["pairs"][str(child)] + data["plan"]["sides"][str(child)]
        hosts.setdefault(time, []).append((stream, full[child][offset:offset + width]))
    residual = []
    for child, axes in enumerate(full):
        require(used[child] == set(range(len(used[child]))), "hosted prefix")
        residual.append([axis for index, axis in enumerate(axes) if index not in used[child]])
    for child in SITES:
        axes = full[child]
        require(all((left & right).bit_count() % 2 == (i == j)
                    for i, left in enumerate(axes) for j, right in enumerate(axes)),
                "source full basis is not orthonormal")
    require([len(used[child]) for child in SITES] == [0, 0, 0, 0, 31],
            "four idle children and one partially hosted donor")
    return recipe, order, hosts, residual


@cache
def parity_phase(vector):
    """The lifted parity function modulo four, encoded without symbolic XOR."""
    require(type(vector) is int and 0 <= vector < 1 << BITS, "binary axis")
    indices = [i for i in range(BITS) if vector >> i & 1]
    cross = sum(1 << (BITS * i + j) for offset, i in enumerate(indices)
                for j in indices[offset + 1:])
    return vector, 0, cross


def add_phase(left, right):
    # Low-bit carries enter the high linear coefficient; cross coefficients
    # are already even and therefore add by XOR.
    return (left[0] ^ right[0],
            left[1] ^ right[1] ^ (left[0] & right[0]),
            left[2] ^ right[2])


def scale_phase(value, coefficient):
    coefficient %= 4
    if coefficient == 0:
        return ZERO_PHASE
    if coefficient == 1:
        return value
    if coefficient == 2:
        return 0, value[0], 0
    return value[0], value[1] ^ value[0], value[2]


def sum_phase(values):
    result = ZERO_PHASE
    for value in values:
        result = add_phase(result, value)
    return result


def symbolic_replay(data, prepared):
    recipe, order, hosts, residual = prepared
    template = data["template"]
    # Keys are (five-variable squarefree monomial mask, low linear bits,
    # high linear bits, even quadratic bits).  Coefficients are integers.
    matrix = [[{(0, 0, 0, 0): 1} if row == column else {}
               for column in range(8)] for row in range(8)]
    seen_sites = Counter()
    peak = 8

    def measure():
        nonlocal peak
        peak = max(peak, sum(len(entry) for row in matrix for entry in row))

    def phase(row, exponent, monomial=0):
        for column in range(8):
            changed = {}
            for (mask, low, high, cross), coefficient in matrix[row][column].items():
                require(not mask & monomial, "phase variable encountered twice on a path")
                key = (mask | monomial, *add_phase((low, high, cross), exponent))
                changed[key] = coefficient
            matrix[row][column] = changed
        measure()

    def shear(destination, source, coefficient):
        require(destination != source and type(coefficient) is int, "shear")
        for column in range(8):
            result = matrix[destination][column]
            for key, value in matrix[source][column].items():
                result[key] = result.get(key, 0) + coefficient * value
            matrix[destination][column] = {key: value for key, value in result.items() if value}
        measure()

    blocks = {}
    current = None
    for event in template["execution_schedule"]:
        if event["kind"] in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if event["kind"] == "local_cover_sweep":
            current = event["stage"]
            require(current not in blocks, "duplicate local block")
            blocks[current] = []
        require(current is not None, "event before first block")
        blocks[current].append(event)
    require(set(blocks) == set(range(9)), "nine data blocks")
    q = parity_phase(recipe["q"])
    visited = Counter()
    for time, (stage, replica) in enumerate(order):
        for stream, axes in hosts.get(time, []):
            phase(stream, sum_phase(parity_phase(axis) for axis in axes))
        if replica != 0:
            continue
        visited[stage] += 1
        for event in blocks[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                local = [item for item in template["recipe"]
                         if item["kind"] == "local" and item["stage"] == stage]
                require(len(local) == 1, "local recipe ambiguity")
                local = local[0]
                x, y = 2 * local["pair"], 2 * local["pair"] + 1
                for side, row in enumerate((x, y)):
                    before = (scale_phase(q, 1 - side) if stage == 0 else
                              add_phase(((1 << (9 + 8 * (stage - 1))) - 1, 0, 0),
                                        scale_phase(q, -side)))
                    phase(row, scale_phase(before, -1))
                if local["reverse"]:
                    shear(x, y, -1)
                else:
                    shear(y, x, 1)
                for side, row in enumerate((x, y)):
                    after = add_phase(((1 << (9 + 8 * stage)) - 1, 0, 0),
                                      scale_phase(q, -side))
                    phase(row, after)
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    exponent = sum_phase(parity_phase(axis) for axis in residual[child])
                    exponent = add_phase(exponent, scale_phase(parity_phase(
                        recipe["idle_children"][child]["translation_after"]), 2))
                    monomial = 0
                    if child in SITES:
                        seen_sites[child] += 1
                        monomial = 1 << SITES.index(child)
                    phase(2 * event["pair"] + side, exponent, monomial)
            elif kind == "bridge":
                destination, source, coefficient = event["dst"], event["src"], event["coefficient"]
                shear(2 * destination, 2 * source, coefficient)
                shear(2 * source + 1, 2 * destination + 1, -coefficient)
            elif kind == "terminal_Y_translations":
                for pair in event["pairs"]:
                    phase(2 * pair + 1, scale_phase(q, 2))
            elif kind == "terminal":
                for pair in range(event["pairs"]):
                    matrix[2 * pair], matrix[2 * pair + 1] = (
                        matrix[2 * pair + 1],
                        [{key: -value for key, value in entry.items()}
                         for entry in matrix[2 * pair]])
            else:
                raise ValueError("unknown data event: " + kind)
    require(visited == Counter({stage: 1 for stage in range(9)}), "data block chronology")
    require(seen_sites == Counter({child: 1 for child in SITES}), "five phase injection sites")
    normalizer = scale_phase(((1 << BITS) - 1, 0, 0), -1)
    for row in range(8):
        phase(row, normalizer)
    polynomial = []
    for row in range(8):
        for column in range(8):
            for (mask, low, high, cross), coefficient in matrix[row][column].items():
                require((low, high, cross) == ZERO_PHASE, "uncancelled ambient character phase")
                polynomial.append([row, column, mask, coefficient])
    return sorted(polynomial), peak


def assignment_census(polynomial):
    accepted = []
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for exponents in product(range(4), repeat=len(SITES)):
        matrix = [[(0, 0) for _ in range(8)] for _ in range(8)]
        for row, column, mask, coefficient in polynomial:
            exponent = sum(exponents[i] for i in range(len(SITES)) if mask >> i & 1) % 4
            real, imaginary = roots[exponent]
            before = matrix[row][column]
            matrix[row][column] = (before[0] + coefficient * real,
                                   before[1] + coefficient * imaginary)
        if all(matrix[row][column] == (int(row == column), 0)
               for row in range(8) for column in range(8)):
            accepted.append(list(exponents))
    return {"total": 4 ** len(SITES), "accepted": len(accepted),
            "accepted_exponents": accepted}


def build():
    data = inputs()
    prepared = context(data)
    polynomial, peak = symbolic_replay(data, prepared)
    forcing = [[child, row] for child, row in zip(SITES, (6, 7, 1, 0, 3))]
    for child, row in forcing:
        diagonal = [term for term in polynomial if term[:2] == [row, row]]
        require(diagonal == [[row, row, 1 << SITES.index(child), 1]], "forcing diagonal")
    census = assignment_census(polynomial)
    require(census["accepted_exponents"] == [[0] * 5], "nontrivial accepted phase assignment")
    return {
        "sites": list(SITES), "ambient_bits": BITS, "owner": 0, "port": 0,
        "residual_ranks": [[child, len(prepared[3][child])] for child in SITES],
        "polynomial_matrix": polynomial, "character_dependent_terms": 0,
        "forcing_diagonal": forcing, "exact_phase_assignments": census,
    }, peak


def main():
    observed, peak = build()
    expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
    for key, value in observed.items():
        require(expected.get(key) == value, "independent receipt mismatch: " + key)
    print(json.dumps({"independent": "pass", "polynomial_terms": len(observed["polynomial_matrix"]),
                      "peak_terms": peak, "phase_assignments": observed["exact_phase_assignments"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
