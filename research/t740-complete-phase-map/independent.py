#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Independent raw-input replay and exact rational-inverse substitution.

The raw projection follows the attributed PR3272 independent checker.  No
executable predecessor or primary module is imported.  Ambient phases here
use 73 explicit coefficients and sets of quadratic coordinate pairs; inverse
identities use Laurent polynomials with 20-component exponent vectors.
"""

from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BITS = 73
SITES = tuple(range(20))
ZERO = ((0,) * BITS, frozenset())
EXP_ZERO = (0,) * len(SITES)
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


def inputs(root=ROOT):
    pins = {row["path"]: row for row in json.loads(
        (PACKAGE / "SOURCES.json").read_bytes())["files"]}
    result = {}
    for name, relative in INPUTS.items():
        pin = pins[relative]
        require(pin["usage"] == "input", "independent input declaration")
        path = Path(root) / relative
        require(path.is_file() and not path.is_symlink(), "independent input file")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + relative)
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
                "source Git blob: " + relative)
        result[name] = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    return result


def context(data):
    """Project only owner zero/port zero directly from base rows and edits."""
    base = data["fill"]["rows"]
    count = 9 * 74 * 408
    require(len(base) == count, "base fill size")

    def lift(index):
        copy, old = divmod(index, count)
        time, helper, owner, child, port, offset = base[old]
        return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]

    edits = {}
    journal = data["journal"]
    require(journal["copies"] == 10 and len(journal["edits"]) == 145, "journal dimensions")
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < 10 * count, "journal index")
        require(index not in edits and before == lift(index), "journal preimage")
        require(len(after) == 6 and all(type(value) is int for value in after), "journal row")
        require(after[:2] == before[:2], "journal call/helper preservation")
        edits[index] = after
    rows = [lift(index) for index, row in enumerate(base)
            if row[2] == row[4] == 0 and index not in edits]
    rows.extend(row for row in edits.values() if row[2] == row[4] == 0)
    require(len(rows) == 30, "projected hosted rows")
    require(len(data["order"]) == 666, "base order size")
    order = [(stage, owner + 74 * copy) for stage, owner in data["order"] for copy in range(10)]
    dispatch = {(stage, owner): tag for stage, owner, tag in data["dispatch"]}
    require(len(dispatch) == 666, "dispatch coverage")
    recipe = data["recipes"]["recipes"][0]
    full = [list(map(int, child["orthogonal_axes"])) for child in recipe["idle_children"]]
    require(len(full) == 20, "all twenty child slots")
    used, hosts = [set() for _ in full], {}
    for time, helper, owner, child, port, offset in rows:
        require(owner == port == 0, "projected identity")
        stage, caller = order[time]
        width = data["providers"][dispatch[stage, caller % 74]]["widths"][helper]
        positions = set(range(offset, offset + width))
        require(0 <= offset and offset + width <= len(full[child]), "hosted slice range")
        require(not used[child] & positions, "hosted slice overlap")
        used[child].update(positions)
        stream = 2 * data["plan"]["pairs"][str(child)] + data["plan"]["sides"][str(child)]
        hosts.setdefault(time, []).append((stream, full[child][offset:offset + width]))
    residual = []
    for child, axes in enumerate(full):
        require(used[child] == set(range(len(used[child]))), "hosted prefix")
        require(all((left & right).bit_count() % 2 == int(i == j)
                    for i, left in enumerate(axes) for j, right in enumerate(axes)),
                "full child basis orthonormality")
        residual.append([axis for index, axis in enumerate(axes) if index not in used[child]])
    return recipe, order, hosts, residual


@cache
def parity(vector):
    require(type(vector) is int and 0 <= vector < 1 << BITS, "binary phase axis")
    support = [i for i in range(BITS) if vector >> i & 1]
    return (tuple(int(i in support) for i in range(BITS)),
            frozenset((i, j) for offset, i in enumerate(support) for j in support[offset + 1:]))


@cache
def phase_add(left, right):
    return tuple((a + b) % 4 for a, b in zip(left[0], right[0])), left[1] ^ right[1]


def phase_scale(value, scalar):
    return tuple(scalar * entry % 4 for entry in value[0]), value[1] if scalar % 2 else frozenset()


def phase_sum(values):
    result = ZERO
    for value in values:
        result = phase_add(result, value)
    return result


def phase_value(value, character):
    return (sum(coefficient for i, coefficient in enumerate(value[0]) if character >> i & 1)
            + 2 * sum(bool(character >> i & 1 and character >> j & 1) for i, j in value[1])) % 4


def local_event(template, q, stage, phase, shear):
    locals_ = [item for item in template["recipe"]
               if item["kind"] == "local" and item["stage"] == stage]
    require(len(locals_) == 1, "unique local recipe")
    local = locals_[0]
    x, y = 2 * local["pair"], 2 * local["pair"] + 1
    for side, row in enumerate((x, y)):
        prefix = ((tuple(int(i < 9 + 8 * (stage - 1)) for i in range(BITS)), frozenset())
                  if stage else ZERO)
        before = phase_add(prefix, phase_scale(q, -side if stage else 1 - side))
        phase(row, phase_scale(before, -1))
    shear(x, y, -1) if local["reverse"] else shear(y, x, 1)
    after = tuple(int(i < 9 + 8 * stage) for i in range(BITS)), frozenset()
    for side, row in enumerate((x, y)):
        phase(row, phase_add(after, phase_scale(q, -side)))


def data_event(template, recipe, residual, event, phase, shear, matrix, seen):
    kind, q = event["kind"], parity(recipe["q"])
    if kind == "local_cover_sweep":
        local_event(template, q, event["stage"], phase, shear)
    elif kind == "idle_cover_sweep":
        for side, child in enumerate(event["child_indices"]):
            exponent = phase_sum(parity(axis) for axis in residual[child])
            translation = recipe["idle_children"][child]["translation_after"]
            exponent = phase_add(exponent, phase_scale(parity(translation), 2))
            seen[child] += 1
            phase(2 * event["pair"] + side, exponent, 1 << child)
    elif kind == "bridge":
        destination, source, coefficient = event["dst"], event["src"], event["coefficient"]
        shear(2 * destination, 2 * source, coefficient)
        shear(2 * source + 1, 2 * destination + 1, -coefficient)
    elif kind == "terminal_Y_translations":
        for pair in event["pairs"]:
            phase(2 * pair + 1, phase_scale(q, 2))
    elif kind == "terminal":
        for pair in range(event["pairs"]):
            x, y = matrix[2 * pair], matrix[2 * pair + 1]
            matrix[2 * pair] = y
            matrix[2 * pair + 1] = [{key: -value for key, value in entry.items()} for entry in x]
    else:
        raise ValueError("unrecognized source event: " + kind)


def stage_blocks(template):
    blocks, stage = {}, None
    for event in template["execution_schedule"]:
        kind = event["kind"]
        if kind in ("bank_padding_cover_sweep", "translate_every_live_family"):
            continue
        if kind == "local_cover_sweep":
            stage = event["stage"]
            require(stage not in blocks, "duplicate stage")
            blocks[stage] = []
        require(stage is not None, "event before local stage")
        blocks[stage].append(event)
    require(set(blocks) == set(range(9)), "nine local stages")
    return blocks


def replay(data, prepared):
    recipe, order, hosts, residual = prepared
    template = data["template"]
    matrix = [[{(0, ZERO): 1} if i == j else {} for j in range(8)] for i in range(8)]
    peak, visited, seen = 8, Counter(), Counter()

    def measure():
        nonlocal peak
        peak = max(peak, sum(len(entry) for row in matrix for entry in row))

    def phase(row, value, variable=0):
        for column, entry in enumerate(matrix[row]):
            changed = {}
            for (mask, exponent), coefficient in entry.items():
                require(not mask & variable, "repeated formal phase")
                key = mask | variable, phase_add(exponent, value)
                changed[key] = changed.get(key, 0) + coefficient
            matrix[row][column] = {key: coefficient for key, coefficient in changed.items() if coefficient}
        measure()

    def shear(destination, source, coefficient):
        require(destination != source and coefficient in (-1, 1), "source shear")
        for column in range(8):
            changed = dict(matrix[destination][column])
            for key, value in matrix[source][column].items():
                changed[key] = changed.get(key, 0) + coefficient * value
            matrix[destination][column] = {key: value for key, value in changed.items() if value}
        measure()

    blocks = stage_blocks(template)
    q = parity(recipe["q"])
    for time, (stage, owner) in enumerate(order):
        for row, axes in hosts.get(time, []):
            phase(row, phase_sum(parity(axis) for axis in axes))
        if owner:
            continue
        visited[stage] += 1
        for event in blocks[stage]:
            data_event(template, recipe, residual, event, phase, shear, matrix, seen)
    require(visited == Counter({i: 1 for i in range(9)}), "source chronology")
    require(seen == Counter({i: 1 for i in SITES}), "twenty phase sites")
    normalizer = ((3,) * BITS, frozenset())
    for row in range(8):
        phase(row, normalizer)
    ambient = {ZERO: 0, phase_scale(q, -1): -1}
    terms = []
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            require(len({phase for _, phase in entry}) <= 1, "entry has distinct ambient factors")
            for (mask, exponent), coefficient in entry.items():
                require(exponent in ambient, "unaccounted ambient character phase")
                terms.append([i, j, mask, ambient[exponent], coefficient])
    return sorted(terms), peak


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for powers, coefficient in polynomial.items():
            result[powers] = result.get(powers, 0) + coefficient
    return {powers: coefficient for powers, coefficient in result.items() if coefficient}


def negative(polynomial):
    return {powers: -coefficient for powers, coefficient in polynomial.items()}


def multiply(*polynomials):
    result = {EXP_ZERO: Fraction(1)}
    for polynomial in polynomials:
        out = {}
        for left, a in result.items():
            for right, b in polynomial.items():
                key = tuple(x + y for x, y in zip(left, right))
                out[key] = out.get(key, 0) + a * b
        result = {powers: coefficient for powers, coefficient in out.items() if coefficient}
    return result


def quotient(numerator, denominator):
    """After substitution every inverse denominator must be a nonzero monomial."""
    require(len(denominator) == 1, "inverse denominator is not one nonzero monomial")
    powers, coefficient = next(iter(denominator.items()))
    require(coefficient != 0, "zero inverse denominator")
    return {tuple(x - y for x, y in zip(key, powers)): Fraction(value, coefficient)
            for key, value in numerator.items() if value}


def inverse_certificate(terms):
    """Substitute the exact source polynomial into a separately derived inverse.

    The common nonzero character factor is removed from each entry first.
    Division is allowed only after its substituted denominator is proved a
    monomial, so the certificate proves every division is valid on the torus.
    """
    matrix = [[{} for _ in range(8)] for _ in range(8)]
    for row, column, mask, ambient, coefficient in terms:
        require(ambient == (-1 if row % 2 and column % 2 == 0 else 0), "ambient factor pattern")
        powers = tuple(int(mask >> index & 1) for index in SITES)
        matrix[row][column] = add(matrix[row][column], {powers: Fraction(coefficient)})
    one = {EXP_ZERO: Fraction(1)}
    z, recovered, denominators = {}, [], []

    def divide(numerator, denominator):
        result = quotient(numerator, denominator)
        powers, coefficient = next(iter(denominator.items()))
        denominators.append([list(powers), str(coefficient)])
        return result

    def put(index, polynomial):
        expected = tuple(int(i == index) for i in SITES)
        require(polynomial == {expected: 1}, "rational inverse fails at site " + str(index))
        z[index] = polynomial
        recovered.append(index)

    m = matrix
    put(13, m[0][0]); put(12, m[1][1])
    put(0, divide(add(m[0][2], m[2][2]), z[13]))
    put(1, add(one, divide(m[1][2], multiply(z[0], z[12]))))
    put(15, divide(m[2][2], multiply(z[0], z[1])))
    u = add(z[12], negative(m[3][1]))
    put(14, add(m[3][0], u))
    put(3, divide(u, z[14])); put(2, divide(m[3][3], u))
    put(4, divide(add(m[4][4], negative(m[0][4])), z[15]))
    put(5, add(one, divide(m[3][4], multiply(z[4], z[14]))))
    put(17, divide(m[4][4], multiply(z[4], z[5])))
    p = divide(add(m[5][1], multiply(z[3], z[14])), z[3])
    put(16, divide(add(divide(m[5][2], z[0]),
                       negative(multiply(z[14], add(one, negative(z[1])))), p), z[1]))
    put(7, divide(p, z[16])); put(6, divide(m[5][5], p))
    put(8, divide(add(m[0][6], m[6][6]), z[17]))
    put(9, add(one, divide(m[5][6], multiply(z[8], z[16]))))
    put(19, divide(m[6][6], multiply(z[8], z[9])))
    p = add(z[16], negative(divide(m[7][1], multiply(z[3], z[7]))))
    put(18, divide(add(divide(m[7][4], z[4]),
                       negative(multiply(z[16], add(one, negative(z[5])))), p), z[5]))
    put(11, divide(p, z[18])); put(10, divide(m[7][7], p))
    require(set(z) == set(SITES), "complete inverse")
    require(all(sum(entry.values()) == int(i == j) for i, row in enumerate(m)
                for j, entry in enumerate(row)), "all-one phase image")
    return {"recovered_sites": recovered, "checked_divisions": len(denominators),
            "denominators": denominators}


def build():
    data = inputs()
    prepared = context(data)
    terms, peak = replay(data, prepared)
    certificate = inverse_certificate(terms)
    return {"schema_version": 1, "sites": list(SITES), "ambient_bits": BITS, "owner": 0, "port": 0,
            "residual_ranks": [[i, len(prepared[3][i])] for i in SITES],
            "polynomial_matrix": terms, "peak_symbolic_terms": peak,
            "matrix_terms": len(terms), "ambient_phase_vector": prepared[0]["q"],
            "inverse_checked_sites": len(certificate["recovered_sites"]),
            "inverse_entry_count": 20, "baseline_identity": True,
            "independent_inverse": certificate}


def main():
    observed = build()
    expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
    for key in ("schema_version", "sites", "ambient_bits", "owner", "port", "residual_ranks",
                "polynomial_matrix", "peak_symbolic_terms", "matrix_terms",
                "ambient_phase_vector", "inverse_checked_sites", "inverse_entry_count",
                "baseline_identity"):
        require(expected.get(key) == observed[key], "independent receipt mismatch: " + key)
    print(json.dumps({"independent": "pass", "polynomial_terms": len(observed["polynomial_matrix"]),
                      "recovered_sites": len(observed["independent_inverse"]["recovered_sites"]),
                      "checked_divisions": observed["independent_inverse"]["checked_divisions"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
