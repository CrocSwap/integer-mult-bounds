#!/usr/bin/env python3
"""Finite formal-ring corroboration for one clean-helper word; no source imports.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Credit Nick Petalas PR6800, Josie Elliston PR6138, Nick Petalas PR6122,
Cinna Davis, Ali Romman PR5617 and Matarener PR6114. Rank/Gram methods are
classical. Source dirty-capacity theorem is cited, not replayed here.
"""
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
SOURCE_HEAD = 'c94197e40c9e8a25f643d776160659871e5ce9ac'
EXPECTED_SOURCES = {
    'vendor/PR6800-PROOF.md': ('research/restored-dirty-query-capacity/PROOF.md',
        6061, 'e82afe4b80b34dcdd69b59c2104f88cf9242c8b93554442e30c35de305deff98',
        'c5f42331896c9bfcbe348c9ecd1a5c9431503fdb'),
    'vendor/PR6800-README.md': ('research/restored-dirty-query-capacity/README.md',
        7386, 'bec1134b11d08664897821f28888dda6f88946d7ca9a405be3f95802aae26387',
        '8df37528f5d2f9f5e818f71d30c7106c7ae43082'),
}
OTHER = ((2, 4, 6), (0, 4, 6), (0, 2, 6), (0, 2, 4))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate source metadata key: ' + key)
        result[key] = value
    return result


def bad_number(value):
    raise ValueError('non-integer source metadata number: ' + value)


def authenticate():
    raw = (P / 'SOURCE-PINS.json').read_bytes()
    pins = json.loads(raw, object_pairs_hook=unique, parse_float=bad_number,
                      parse_constant=bad_number)
    need(type(pins.get('schema_version')) is int and pins['schema_version'] == 1,
         'source schema')
    rows = pins.get('files')
    need(type(rows) is list and len(rows) == 2 and
         {r.get('local_path') for r in rows} == set(EXPECTED_SOURCES), 'source inventory')
    observed = {}
    for row in rows:
        name = row['local_path']
        path, size, digest, git_blob = EXPECTED_SOURCES[name]
        need(row.get('source_repository') == 'petalas/integer-mult-bounds' and
             row.get('source_commit') == SOURCE_HEAD and row.get('source_path') == path
             and row.get('mode') == '100644', 'source identity: ' + name)
        need(type(row.get('bytes')) is int and row['bytes'] == size and
             row.get('sha256') == digest and row.get('git_blob') == git_blob,
             'source pin: ' + name)
        data = (P / name).read_bytes()
        need(len(data) == size and sha(data) == digest and blob(data) == git_blob,
             'source bytes: ' + name)
        observed[name] = digest
    return sha(raw), observed


def identity(n):
    return tuple(1 << i for i in range(n))


def zero(n):
    return (0,) * n


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a, b):
    result = []
    for row in a:
        value = 0
        while row:
            low = row & -row
            value ^= b[low.bit_length() - 1]
            row ^= low
        result.append(value)
    return tuple(result)


def rank(matrix):
    pivots = {}
    for row in matrix:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def trace(matrix):
    result = 0
    for i, row in enumerate(matrix):
        result ^= (row >> i) & 1
    return result


def pair_multiply(a, b):
    """(A0+Q A1)(B0+Q B1), retaining both coefficients and their order."""
    return (add(multiply(a[0], b[0]), multiply(a[1], b[1])),
            add(multiply(a[0], b[1]), multiply(a[1], b[0])))


def product(chronological):
    value = (identity(8), zero(8))
    for gate in chronological:
        value = pair_multiply(gate, value)
    return value


def check_paid(matrix):
    need(len(matrix) == 8 and all(type(x) is int and 0 <= x < 256 for x in matrix),
         'paid matrix format')
    need(multiply(matrix, matrix) == zero(8), 'paid square-zero')
    need(rank(matrix) <= 2, 'paid rank cap')


def construction():
    unit = identity(8)
    full = tuple(sum(1 << j for j in range(8)
                     if j % 2 == i % 2 and j // 2 != i // 2) for i in range(8))
    terms = tuple(tuple(full[i] if i // 2 == block else 0 for i in range(8))
                  for block in range(4))
    for term in terms:
        check_paid(term)
        need(rank(term) == 2, 'constructed paid rank')
    basis = (*unit[:6], 1 | 4 | 16 | 64, 2 | 8 | 32 | 128)
    need(multiply(basis, basis) == unit and rank(basis) == 8, 'common basis inverse')
    gates = [(basis, zero(8))]
    for term in terms:
        free, paid = (add(unit, term), zero(8)), (unit, term)
        need(pair_multiply(free, free) == (unit, zero(8)), 'free inverse')
        need(pair_multiply(paid, paid) == (unit, zero(8)), 'paid inverse')
        gates.extend([free, paid])
    gates.append((basis, zero(8)))
    helper = tuple((1 << (6 + i % 2)) if i < 6 else 0 for i in range(8))
    expected = (helper, add(unit, helper))
    forward, backward = product(gates), product(reversed(gates))
    need(forward == backward == expected, 'complete formal operator')
    need(pair_multiply(forward, backward) == (unit, zero(8)), 'formal inverse')
    return terms, basis, expected


def apply_binary(matrix, vector):
    result = 0
    for i, row in enumerate(matrix):
        result |= ((row & vector).bit_count() & 1) << i
    return result


def pair_action(operator, vector):
    lo = sum((x & 1) << i for i, x in enumerate(vector))
    hi = sum((x >> 1) << i for i, x in enumerate(vector))
    a = apply_binary(operator[0], lo) ^ apply_binary(operator[1], hi)
    b = apply_binary(operator[0], hi) ^ apply_binary(operator[1], lo)
    return tuple(((a >> i) & 1) | (((b >> i) & 1) << 1) for i in range(8))


def q(value):
    """Literal two-coefficient scalar multiplication by Q, Q squared equals1."""
    return ((value & 1) << 1) | (value >> 1)


def literal_gate(value, block, paid, q_is_one):
    a, b, c = OTHER[block]
    first = value[a] ^ value[b] ^ value[c]
    second = value[a + 1] ^ value[b + 1] ^ value[c + 1]
    if paid and not q_is_one:
        first, second = q(first), q(second)
    value[2 * block] ^= first
    value[2 * block + 1] ^= second


def literal(vector, inverse=False, omit_paid=-1, omit_free=-1,
            without_basis=False, q_is_one=False):
    """Execute explicit component gates, without using any binary matrix routine."""
    value = list(vector)
    if not without_basis:
        value[6] ^= value[0] ^ value[2] ^ value[4]
        value[7] ^= value[1] ^ value[3] ^ value[5]
    for block in (range(3, -1, -1) if inverse else range(4)):
        order = (True, False) if inverse else (False, True)
        for paid in order:
            if not ((paid and block == omit_paid) or
                    (not paid and block == omit_free)):
                literal_gate(value, block, paid, q_is_one)
    if not without_basis:
        value[6] ^= value[0] ^ value[2] ^ value[4]
        value[7] ^= value[1] ^ value[3] ^ value[5]
    return tuple(value)


def endpoint(vector):
    return tuple(q(x) ^ ((vector[6 + i % 2] ^ q(vector[6 + i % 2]))
                         if i < 6 else 0) for i, x in enumerate(vector))


def exhaustive(operator):
    digest = hashlib.sha256()
    clean = 0
    for number in range(1 << 16):
        value = tuple((number >> (2 * i)) & 3 for i in range(8))
        forward, backward = literal(value), literal(value, inverse=True)
        expected = pair_action(operator, value)
        need(forward == backward == expected == endpoint(value), 'full formal vector case')
        after_forward = literal(forward, inverse=True)
        after_backward = literal(backward)
        need(after_forward == after_backward == value, 'literal roundtrip')
        if not (value[6] or value[7]):
            clean += 1
            need(forward[:6] == tuple(q(x) for x in value[:6]) and
                 forward[6:] == (0, 0), 'clean entrance/return')
        digest.update(bytes(value + forward + backward + after_forward + after_backward))
    need(clean == 4096, 'complete clean domain')
    return {'formal_vectors': 65536, 'clean_vectors': clean,
            'forward_checks': 65536, 'reverse_checks': 65536,
            'roundtrip_compositions': 131072, 'literal_word_executions': 262144,
            'profile_sha256': digest.hexdigest()}


def one_helper_reduction():
    unit = identity(7)
    target = (*identity(6), 0)
    digest = hashlib.sha256()
    for column in range(64):
        projection = tuple((1 << i) | (((column >> i) & 1) << 6)
                           for i in range(6)) + (0,)
        shear = projection[:6] + (64,)
        need(trace(projection) == 0 and rank(projection) == 6 and
             multiply(projection, projection) == projection, 'one-helper projection')
        need(multiply(shear, shear) == unit and
             multiply(multiply(shear, projection), shear) == target,
             'one-helper public-fixing shear')
        forbidden = projection[:6] + (64,)
        need(trace(forbidden) == 1, 'one-helper nonzero scalar block trace')
        digest.update(bytes(projection + shear + forbidden))
    need(rank(identity(6)) == 6, 'zero-helper projection')
    return {'binary_A_columns': 64, 'projection_and_shear_cases': 64,
            'nonzero_scalar_block_trace_cases': 64,
            'profile_sha256': digest.hexdigest(),
            'minimality_basis': 'Written all-field trace/projection reduction plus cited PR6800 '
                               'dirty projection floor9; not an exhaustive word search.'}


class EndpointMismatch(ValueError):
    def __init__(self, witness):
        super().__init__('endpoint mismatch')
        self.witness = witness


def check_contract(actual, claimed):
    for index in range(8):
        value = tuple(int(i == index) for i in range(8))
        got, expected = actual(value), claimed(value)
        if got != expected:
            raise EndpointMismatch({'input': list(value), 'actual': list(got),
                                    'false_claim': list(expected)})


def rejection(name, call, expected_reason="endpoint mismatch"):
    try:
        call()
    except ValueError as error:
        need(str(error) == expected_reason, 'control rejected for wrong reason: ' + name)
        if expected_reason == 'endpoint mismatch':
            need(isinstance(error, EndpointMismatch) and
                 error.witness['actual'] != error.witness['false_claim'],
                 'control requires an actual endpoint witness: ' + name)
        result = {'name': name, 'status': 'rejected', 'reason': str(error)}
        if isinstance(error, EndpointMismatch):
            result['witness'] = error.witness
        return result
    raise ValueError('control did not reject: ' + name)


def controls(operator):
    wrong_rank = (8, 16, 32, 0, 0, 0, 0, 0)
    wrong_endpoint = ((operator[0][0] ^ 1,) + operator[0][1:],
                      (operator[1][0] ^ 1,) + operator[1][1:])
    dirty_claim = lambda v: tuple(q(x) if i < 6 else x for i, x in enumerate(v))
    tests = [
        rejection('non_square_zero_paid', lambda: check_paid(identity(8)), 'paid square-zero'),
        rejection('paid_rank_cap', lambda: check_paid(wrong_rank), 'paid rank cap'),
        rejection('omitted_common_basis', lambda: check_contract(
            lambda v: literal(v, without_basis=True), endpoint)),
        rejection('omitted_free_normalizer_cleanup', lambda: check_contract(
            lambda v: literal(v, omit_free=0), endpoint)),
        rejection('wrong_public_endpoint', lambda: check_contract(
            literal, lambda v: pair_action(wrong_endpoint, v))),
        rejection('missing_paid_call', lambda: check_contract(
            lambda v: literal(v, omit_paid=0), endpoint)),
        rejection('formal_Q_collapsed_to_one', lambda: check_contract(
            lambda v: literal(v, q_is_one=True), endpoint)),
        rejection('false_arbitrary_dirty_restoration', lambda: check_contract(
            literal, dirty_claim)),
    ]
    need(len(tests) == 8, 'control count')
    return tests


def main():
    try:
        pin_sha, sources = authenticate()
        terms, basis, operator = construction()
        check_contract(literal, endpoint)
        observed = exhaustive(operator)
        helper = one_helper_reduction()
        rejected = controls(operator)
        receipt = {'schema_version': 1, 'status': 'PASS_CLEAN_TWO_HELPER_QUERY',
                   'source_head': SOURCE_HEAD, 'source_manifest_sha256': pin_sha,
                   'source_sha256': sources, 'paid_terms': [list(x) for x in terms],
                   'paid_ranks': [rank(x) for x in terms],
                   'constructed_paid_rank_sum': sum(rank(x) for x in terms),
                   'common_basis': list(basis),
                   'formal_operator': {'constant_rows': list(operator[0]),
                                       'Q_rows': list(operator[1])},
                   'exhaustive_F2_Q_checks': observed, 'one_helper_reduction': helper,
                   'rejection_controls': rejected,
                   'methods': ['Ordered pair-polynomial binary matrix multiplication',
                               'Separate literal component-gate vector interpreter',
                               'All65536F2[Q]/(Q2-1) input vectors; no predecessor imports'],
                   'limits': 'One explicit n6/k4/r2/h2 clean construction. All-field and h2minimal '
                             'statements rest on written proofs and cited PR6800floor9. '
                             'No all-words census, paid-rank8optimality, predecessor replay, '
                             'physical/native cost, caller/supplier or frontier claim.'}
        receipt['instrumentation'] = ('Python-managed fixed-size matrices and streaming finite '
                                      'verification storage are not physical helper resources.')
        receipt['package_sha256'] = {f.relative_to(P).as_posix(): sha(f.read_bytes())
                                    for f in sorted(P.rglob('*')) if f.is_file()}
        print(json.dumps(receipt, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('FAIL_CLEAN_TWO_HELPER_QUERY: ' + str(error), file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
