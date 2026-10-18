#!/usr/bin/env python3
"""Exact finite-alphabet census and parity-character certificates.

Adapted from Tuafo / PR1604 at c5f5bef84f6648d5573f801c283e01a333ea5f89.
Apache-2.0; substantial OpenAI assistance for Maximooch.

Default execution is read-only.  --write explicitly regenerates CERTIFICATE.json.
All address arithmetic is integral or rational; binary arithmetic applies only
to scalar register matrices and to integral-valued characters.
"""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ZERO = (0,) * 9
TARGET = (4, 0, 0, 0, 4, 0, 0, 0, 4)
COMPLEMENT_TARGET = tuple(2 * x for x in TARGET)
DIAGONAL = (0, 4, 8)
SCOPE = "three identical identity targets; ternary outer products divided by two or four; arbitrary finite restored dirty registers"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def trace(a):
    return sum(a[i] for i in DIAGONAL)


def alphabet():
    vectors = [v for v in product((-1, 0, 1), repeat=3) if any(v)]
    return sorted({tuple(s * u[i] * v[j] for i in range(3) for j in range(3)) for s in (1, 2)
                   for u in vectors for v in vectors})


def target_masks(word, frames):
    """Preserve positional multiplicities, including equal frame occurrences."""
    sums = [ZERO]
    for frame_id in word:
        sums += [add(value, frames[frame_id]) for value in sums]
    return [mask for mask, value in enumerate(sums) if value == TARGET]


def census():
    frames = alphabet()
    pairs = defaultdict(list)
    for i, left in enumerate(frames):
        for j in range(i, len(frames)):
            pairs[add(left, frames[j])].append((i, j))

    triples, quadruples = set(), set()
    for i, frame in enumerate(frames):
        for j, k in pairs.get(subtract(TARGET, frame), ()):
            if i <= j:
                triples.add((i, j, k))
    for pair_sum, left_pairs in pairs.items():
        for i, j in left_pairs:
            for k, ell in pairs.get(subtract(TARGET, pair_sum), ()):
                if j <= k:
                    quadruples.add((i, j, k, ell))

    # Five terms in [-2,2] summing to 8 cannot include a negative term:
    # even the other four maximal entries would then sum to at most 7.
    # Total trace is 24; a pair has trace <=12, a triple <=18.
    nonnegative = [i for i, frame in enumerate(frames)
                   if all(frame[d] >= 0 for d in DIAGONAL)]
    nonnegative_pairs = defaultdict(list)
    for pos, i in enumerate(nonnegative):
        for j in nonnegative[pos:]:
            if trace(frames[i]) + trace(frames[j]) >= 6:
                nonnegative_pairs[add(frames[i], frames[j])].append((i, j))
    complements = set()
    for pos_i, i in enumerate(nonnegative):
        for pos_j in range(pos_i, len(nonnegative)):
            j = nonnegative[pos_j]
            for k in nonnegative[pos_j:]:
                if trace(frames[i]) + trace(frames[j]) + trace(frames[k]) < 12:
                    continue
                triple_sum = add(add(frames[i], frames[j]), frames[k])
                for ell, m in nonnegative_pairs.get(subtract(COMPLEMENT_TARGET, triple_sum), ()):
                    if k <= ell:
                        complements.add((i, j, k, ell, m))

    # Four terms summing to 8I must all have diagonal (2,2,2).
    hadamard = tuple(i for i, frame in enumerate(frames)
                     if all(frame[d] == 2 for d in DIAGONAL))
    require(len(hadamard) == 4, "full-diagonal alphabet is not four frames")
    total = ZERO
    for i in hadamard:
        total = add(total, frames[i])
    require(total == COMPLEMENT_TARGET, "four full-diagonal frames do not sum to 8I")
    # Check the claimed unique multiset, with repetitions allowed, directly.
    full_complements = set()
    for i in hadamard:
        for j in hadamard:
            for k in hadamard:
                for ell in hadamard:
                    if i <= j <= k <= ell and add(add(frames[i], frames[j]),
                                                  add(frames[k], frames[ell])) == COMPLEMENT_TARGET:
                        full_complements.add((i, j, k, ell))
    require(full_complements == {hadamard}, "four-frame complement uniqueness failed")

    words7 = sorted({tuple(sorted(t + hadamard)) for t in triples})
    words8 = {tuple(sorted(t + c)) for t in triples for c in complements}
    words8.update(tuple(sorted(q + hadamard)) for q in quadruples)
    words8 = sorted(words8)
    counts7 = Counter(len(target_masks(w, frames)) for w in words7)
    counts8 = Counter(len(target_masks(w, frames)) for w in words8)
    survivors = [w for w in words8 if len(target_masks(w, frames)) >= 3]
    require(all(len(target_masks(w, frames)) < 3 for w in words7),
            "seven-call candidate survives coefficient-rank bound")
    return {
        "alphabet": frames,
        "decompositions_three": sorted(triples),
        "decompositions_four": sorted(quadruples),
        "complements_five": sorted(complements),
        "candidates_seven": words7,
        "candidates_eight": words8,
        "subset_census_seven": {str(k): v for k, v in sorted(counts7.items())},
        "subset_census_eight": {str(k): v for k, v in sorted(counts8.items())},
        "rank_survivors_eight": survivors,
    }


def solve_rational(rows, rhs):
    matrix = [[Fraction(x) for x in row] + [Fraction(value)]
              for row, value in zip(rows, rhs)]
    pivot_row, columns = 0, []
    for col in range(9):
        next_row = next((r for r in range(pivot_row, len(matrix)) if matrix[r][col]), None)
        if next_row is None:
            continue
        matrix[pivot_row], matrix[next_row] = matrix[next_row], matrix[pivot_row]
        scale = matrix[pivot_row][col]
        matrix[pivot_row] = [x / scale for x in matrix[pivot_row]]
        for r in range(len(matrix)):
            if r != pivot_row and matrix[r][col]:
                scale = matrix[r][col]
                matrix[r] = [x - scale * y for x, y in zip(matrix[r], matrix[pivot_row])]
        columns.append(col)
        pivot_row += 1
    if any(not any(row[:9]) and row[9] for row in matrix):
        return None
    answer = [Fraction(0)] * 9
    for r, col in enumerate(columns):
        answer[col] = matrix[r][9]
    return answer


def make_character(word, frames):
    masks = target_masks(word, frames)
    mandatory = set.intersection(*(set(j for j in range(8) if mask >> j & 1)
                                   for mask in masks))
    for odd in sorted(mandatory):
        for even in sorted(set(range(8)) - mandatory):
            values = [int(j == odd) + 2 * int(j == even) for j in range(8)]
            functional = solve_rational([frames[i] for i in word], values)
            if functional is not None:
                return {"frames": list(word),
                        "functional": [str(x) for x in functional],
                        "frame_values": values, "target_value": 1}
    raise ValueError("no one-call character found for surviving multiset")


def check_character(record, frames):
    functional = [Fraction(x) for x in record["functional"]]
    require(len(functional) == 9, "character covector must have nine entries")
    values = [sum(a * b for a, b in zip(functional, frames[i]))
              for i in record["frames"]]
    require(all(v.denominator == 1 for v in values), "character is not integral on every frame")
    require(values == record["frame_values"], "character frame values changed")
    target_value = sum(a * b for a, b in zip(functional, TARGET))
    require(target_value.denominator == 1 and target_value % 2 == 1,
            "character target must be an odd integer")
    require(target_value == record["target_value"], "character target value changed")
    require(sum(int(v) % 2 for v in values) == 1, "character does not leave exactly one call")


def multiply_binary(a, b, roles):
    result = 0
    row_mask = (1 << roles) - 1
    for i in range(roles):
        row = 0
        for k in range(roles):
            if a >> (i * roles + k) & 1:
                row ^= (b >> (k * roles)) & row_mask
        result |= row << (i * roles)
    return result


def formal_word(word, frames, roles):
    identity = sum(1 << (i * roles + i) for i in range(roles))
    result = {ZERO: identity}
    for call in word:
        role = call["role"]
        require(0 <= role < roles, "witness projector outside register range")
        frame_id = call["frame_id"]
        require(0 <= frame_id < len(frames), "witness frame outside alphabet")
        projector = 1 << (role * roles + role)
        constant = identity ^ projector
        next_result = defaultdict(int)
        for exponent, coefficient in result.items():
            next_result[exponent] ^= multiply_binary(coefficient, constant, roles)
            next_result[add(exponent, frames[frame_id])] ^= multiply_binary(coefficient, projector, roles)
        result = {exponent: coefficient for exponent, coefficient in next_result.items() if coefficient}
    return result


def check_witness(word, frames):
    require(len(word) == 9, "attaining witness must have nine calls")
    # Formal matrix coefficients cover arbitrary data and dirty inputs.  Extra
    # coordinates are identity blocks; three sizes also exercise this handling.
    for roles in (3, 4, 6):
        active = sum(1 << (i * roles + i) for i in range(3))
        dirty = sum(1 << (i * roles + i) for i in range(3, roles))
        expected = {TARGET: active}
        if dirty:
            expected[ZERO] = dirty
        require(formal_word(word, frames, roles) == expected,
                "nine-call formal identity or dirty restoration failed")


def json_value(value):
    return json.loads(json.dumps(value))


def make_certificate(data):
    frames = data["alphabet"]
    triple = data["decompositions_three"][0]
    certificate = {"schema_version": 1, "scope": SCOPE,
                   "frame_denominator": 4, "target_scaled": list(TARGET), **json_value(data)}
    certificate["character_obstructions"] = [make_character(word, frames)
                                               for word in data["rank_survivors_eight"]]
    certificate["nine_call_witness"] = [{"frame_id": i, "role": role}
                                         for role in range(3) for i in triple]
    return certificate


def check_certificate(certificate, data):
    require(certificate.get("schema_version") == 1, "wrong certificate schema")
    require(certificate.get("scope") == SCOPE, "wrong scope")
    require(certificate.get("frame_denominator") == 4, "wrong frame denominator")
    require(certificate.get("target_scaled") == list(TARGET), "wrong scaled target")
    for key, value in data.items():
        require(certificate.get(key) == json_value(value), "census mismatch: " + key)
    frames = data["alphabet"]
    records = certificate["character_obstructions"]
    require([r["frames"] for r in records] == json_value(data["rank_survivors_eight"]),
            "missing, extra or reordered character obstruction")
    for record in records:
        check_character(record, frames)
    check_witness(certificate["nine_call_witness"], frames)


def controls(certificate, data):
    mutations = []
    changed = deepcopy(certificate)
    changed["character_obstructions"][0]["functional"] = [
        str(2 * Fraction(x)) for x in changed["character_obstructions"][0]["functional"]]
    changed["character_obstructions"][0]["frame_values"] = [
        2 * x for x in changed["character_obstructions"][0]["frame_values"]]
    changed["character_obstructions"][0]["target_value"] *= 2
    mutations.append(("changed character", changed))
    changed = deepcopy(certificate)
    changed["character_obstructions"][0]["functional"] = [
        str(Fraction(x) / 2) for x in changed["character_obstructions"][0]["functional"]]
    mutations.append(("nonintegral character", changed))
    changed = deepcopy(certificate)
    changed["candidates_eight"].pop()
    mutations.append(("deleted candidate", changed))
    changed = deepcopy(certificate)
    changed["alphabet"].append(changed["alphabet"][-1])
    mutations.append(("duplicate alphabet frame", changed))
    changed = deepcopy(certificate)
    changed["target_scaled"][8] = 0
    mutations.append(("changed target", changed))
    changed = deepcopy(certificate)
    changed["frame_denominator"] = 1
    mutations.append(("wrong denominator", changed))
    changed = deepcopy(certificate)
    changed["nine_call_witness"].pop()
    mutations.append(("omitted witness call", changed))
    changed = deepcopy(certificate)
    changed["nine_call_witness"][0]["role"] = 1
    mutations.append(("wrong witness projector", changed))
    for name, changed in mutations:
        try:
            check_certificate(changed, data)
        except ValueError:
            continue
        raise ValueError("negative control accepted: " + name)
    return len(mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate CERTIFICATE.json")
    args = parser.parse_args()
    data = census()
    path = HERE / "CERTIFICATE.json"
    if args.write:
        certificate = make_certificate(data)
    else:
        certificate = json.loads(path.read_text(encoding="utf-8"))
    check_certificate(certificate, data)
    require(certificate == make_certificate(data), "certificate is not the canonical complete replay")
    control_count = controls(certificate, data)
    if args.write:
        path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("PASS_QUARTER_TERNARY_CATALYST"
          f" alphabet={len(data['alphabet'])} candidates7={len(data['candidates_seven'])}"
          f" candidates8={len(data['candidates_eight'])}"
          f" rank_survivors8={len(data['rank_survivors_eight'])}"
          f" character_obstructions={len(certificate['character_obstructions'])}"
          f" minimum_calls=9 arbitrary_dirty_registers=yes controls={control_count}")


if __name__ == "__main__":
    main()
