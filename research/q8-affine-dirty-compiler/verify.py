#!/usr/bin/env python3
"""Dirty-array Q8 compiler and exact invoice. Apache-2.0.

Arham Tahir, with substantial OpenAI Codex assistance. Standard library only.
Normal verification is read-only; --emit prints a recomputed receipt.
"""
import argparse
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LABELS = ('1', 'i', 'j', 'k', '-1', '-i', '-j', '-k')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def affine_point(g, point):
    """Left action of z^c i^a j^b on z^s i^x j^y; z=-1."""
    a, b, c = g & 1, (g >> 1) & 1, g >> 2
    x, y, s = point & 1, (point >> 1) & 1, point >> 2
    return (x ^ a) | ((y ^ b) << 1) | ((s ^ c ^ ((a ^ b) & x) ^ (b & y)) << 2)


def quaternion_point(g, point):
    """Independent reference: Hamilton multiplication of integer 4-tuples."""
    def quaternion(code):
        result = [0] * 4
        result[code & 3] = -1 if code & 4 else 1
        return result
    a, b, c, d = quaternion(g)
    e, f, h, k = quaternion(point)
    result = (a*e-b*f-c*h-d*k, a*f+b*e+c*k-d*h,
              a*h-b*k+c*e+d*f, a*k+b*h-c*f+d*e)
    axis = next(i for i, value in enumerate(result) if value)
    require(sum(abs(x) for x in result) == 1, 'not a quaternion unit')
    return axis | (4 if result[axis] < 0 else 0)


def permutation_swaps(g):
    """Chronological push-permutation swaps; no clean data cell."""
    visited, result = set(), []
    for start in range(8):
        if start in visited:
            continue
        cycle, point = [], start
        while point not in visited:
            visited.add(point)
            cycle.append(point)
            point = affine_point(g, point)
        require(point == start, 'invalid permutation cycle')
        result.extend((start, point) for point in cycle[1:])
    return result


def preparation(r, u, v):
    """L sends u to e_p; K then sends v L^-1 to e_p^T."""
    require(type(r) is int and r >= 1, 'invalid role count')
    require(type(u) is int and type(v) is int and 0 < u < 1 << r
            and 0 < v < 1 << r, 'invalid rank-one vectors')
    require((u & v).bit_count() % 2 == 1, 'coupling must be idempotent')
    p = ((u & v) & -(u & v)).bit_length() - 1
    left = [('xor', k, p) for k in range(r) if k != p and u >> k & 1]
    right = [('xor', p, k) for k in range(r) if k != p and v >> k & 1]
    return p, left + right


def compile_coupling(r, u, v, g):
    """Chronological in-place program for I + uv^T(P_g-I)."""
    p, prep = preparation(r, u, v)
    require(type(g) is int and 0 <= g < 8, 'invalid Q8 label')
    if g == 0:
        return []
    middle = [('swap', p, a, b) for a, b in permutation_swaps(g)]
    return prep + middle + list(reversed(prep))


def run_program(data, program, payload=1):
    """Each role has 8*payload cells, in address-major order.

    Cells may be bits, packed bit vectors, or symbolic linear forms.
    All mutations use XOR; a swap is explicitly three XOR instructions.
    """
    require(type(payload) is int and payload >= 1, 'invalid payload')
    require(data and all(len(row) == 8 * payload for row in data), 'bad array shape')
    require(len({id(row) for row in data}) == len(data), 'aliased role arrays')
    for op in program:
        if op[0] == 'xor':
            _, dst, src = op
            require(dst != src and 0 <= dst < len(data) and 0 <= src < len(data), 'bad XOR')
            for index in range(8 * payload):
                data[dst][index] ^= data[src][index]
        elif op[0] == 'swap':
            _, role, a, b = op
            require(0 <= role < len(data) and 0 <= a < 8 and 0 <= b < 8 and a != b, 'bad swap')
            row = data[role]
            for cell in range(payload):
                i, j = a * payload + cell, b * payload + cell
                row[i] ^= row[j]
                row[j] ^= row[i]
                row[i] ^= row[j]
        else:
            raise ValueError('unknown instruction')
    return data


def symbolic_data(r, payload=1):
    return [[1 << (role * 8 * payload + point) for point in range(8 * payload)]
            for role in range(r)]


def reference(data, u, v, g, payload=1):
    """Direct formal coefficient action, using Hamilton multiplication only."""
    result = [row[:] for row in data]
    for point in range(8):
        destination = quaternion_point(g, point)
        for cell in range(payload):
            source = point * payload + cell
            target = destination * payload + cell
            total = 0
            for role, row in enumerate(data):
                if v >> role & 1:
                    total ^= row[source]
            for role in range(len(data)):
                if u >> role & 1:
                    result[role][source] ^= total
                    result[role][target] ^= total
    return result


def check_fixture(r, u, v, g, compiler=None, payload=1):
    data = symbolic_data(r, payload)
    if compiler is None:
        compiler = compile_coupling
    program = compiler(r, u, v, g)
    actual = run_program([row[:] for row in data], program, payload)
    require(actual == reference(data, u, v, g, payload), 'dirty operator mismatch')
    require(run_program([row[:] for row in actual], list(reversed(program)), payload) == data,
            'inverse/restoration mismatch')
    return actual, program


def authenticate_sources():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))
    count = 0
    for source in sources['files']:
        if source['usage'] != 'input':
            continue
        raw = (ROOT / source['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source['sha256'], 'source SHA256 mismatch')
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(git_blob == source['git_blob'], 'source Git blob mismatch')
        count += 1
    require(count == 3, 'missing declared source')
    return count


def failure_controls():
    count = 0
    # Both L and K are needed; all roles are dirty; i has order four.
    args = (3, 3, 5, 1)
    def wrong_pivot(r, u, v, g):
        p, prep = preparation(r, u, v)
        return prep + [('swap', (p + 1) % r, a, b) for a, b in permutation_swaps(g)] + list(reversed(prep))
    for mutation in (
        lambda r, u, v, g: compile_coupling(r, u, v, g)[:-1],
        lambda r, u, v, g: list(reversed(compile_coupling(r, u, v, g))),
        lambda r, u, v, g: compile_coupling(r, u, v, g ^ 1),
        wrong_pivot,
    ):
        try:
            check_fixture(*args, compiler=mutation)
        except ValueError as error:
            require(str(error) == 'dirty operator mismatch', 'unrelated control failure')
            count += 1
        else:
            raise ValueError('semantic mutation escaped')
    for r, u, v in ((2, 1, 2), (2, 0, 1), (2, True, 1)):
        try:
            compile_coupling(r, u, v, 1)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid coupling escaped')
    return count


def compute():
    source_count = authenticate_sources()
    def distances(alphabet):
        result, queue = {0: 0}, [0]
        for point in queue:
            for label in alphabet:
                target = quaternion_point(label, point)
                if target not in result:
                    result[target] = result[point] + 1
                    queue.append(target)
        require(len(result) == 8, 'incomplete address alphabet')
        return [result[g] for g in range(8)]
    positive_lengths = distances((1, 2))
    inverse_lengths = distances((1, 5, 2, 6))
    require(positive_lengths == [0, 1, 1, 2, 2, 3, 3, 2], 'positive label bill')
    require(inverse_lengths == [0, 1, 1, 2, 2, 1, 1, 2], 'inverse label bill')
    ranks, swaps = [], []
    for g in range(8):
        a, b = g & 1, (g >> 1) & 1
        ranks.append(binary_rank([(a ^ b) << 2, b << 2, 0, g]))
        swaps.append(len(permutation_swaps(g)))
        for point in range(8):
            require(affine_point(g, point) == quaternion_point(g, point), 'Q8 affine embedding')
            shear = point ^ ((((a ^ b) & (point & 1)) ^ (b & ((point >> 1) & 1))) << 2)
            require(shear ^ g == affine_point(g, point), 'affine factorization')
    require(ranks == [0, 2, 2, 2, 1, 2, 2, 2], 'wrong affine invoice')
    require(swaps == [0, 6, 6, 6, 4, 6, 6, 6], 'wrong swap invoice')
    require(ranks[1] > 1 and ranks[4] < 2 * ranks[1], 'underpricing control')
    digest = hashlib.sha256()
    counts, total, columns, max_scalar = [], 0, 0, 0
    for r in range(1, 7):
        couplings = 0
        for u in range(1, 1 << r):
            for v in range(1, 1 << r):
                if (u & v).bit_count() % 2 != 1:
                    continue
                couplings += 1
                scalar = 2 * (u.bit_count() + v.bit_count() - 2)
                require(scalar <= 4 * (r - 1), 'sparse bound')
                max_scalar = max(max_scalar, scalar)
                for g in range(8):
                    actual, program = check_fixture(r, u, v, g)
                    require(sum(op[0] == 'xor' for op in program) == (scalar if g else 0), 'scalar bill')
                    require(sum(op[0] == 'swap' for op in program) == swaps[g], 'swap bill')
                    for row in actual:
                        for value in row:
                            digest.update(value.to_bytes(r, 'little'))
                    total += 1
                    columns += 8 * r
        require(couplings == ((1 << r) - 1) * (1 << (r - 1)), 'idempotent completeness')
        counts.append(couplings)
    packet_columns = 0
    for payload in (2, 3, 7):
        for g in range(8):
            check_fixture(5, 23, 29, g, payload=payload)
            packet_columns += 5 * 8 * payload
    return {'schema_version': 1, 'status': 'PASS_Q8_AFFINE_DIRTY_COMPILER',
            'source_inputs': source_count, 'labels': list(LABELS),
            'positive_label_lengths': positive_lengths, 'inverse_label_lengths': inverse_lengths,
            'affine_displacement_ranks': ranks, 'in_place_swaps': swaps,
            'couplings_by_roles_1_through_6': counts, 'operator_fixtures': total,
            'dirty_input_columns': columns, 'packet_input_columns': packet_columns,
            'endpoint_sha256': digest.hexdigest(), 'max_scalar_xors_in_domain': max_scalar,
            'semantic_and_domain_controls': failure_controls(), 'underpricing_controls': 1,
            'scope': 'Finite-array compiler and inherited affine-rank calibration only; no supplier or kappa admission.'}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=True) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print receipt; never writes files')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(encoded(result).decode('utf-8'), end='')
    else:
        require((PACKAGE / 'RESULT.json').read_bytes() == encoded(result), 'receipt bytes mismatch')
        print(result['status'], 'fixtures', result['operator_fixtures'],
              'dirty_columns', result['dirty_input_columns'], 'no_new_kappa')


if __name__ == '__main__':
    main()
