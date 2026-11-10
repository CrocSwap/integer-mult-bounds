#!/usr/bin/env python3
"""Optional exact closure of deletion 10947 with two scalar compensators.

Jerry Chen / @CubeJerry with substantial OpenAI ChatGPT assistance.
Apache-2.0. No new kappa. Standard library only; explicit checks survive -O.
The primary package supplies authenticated event semantics and its retained
word. This extension recomputes the full domain; it reads no prior report.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys
import time
import types

PRIMARY_SHA256 = 'b1561af0138ebae887728eb561005a2336f00887b5948a3b03f5b44b379b39c5'
DELETE = 10947
EXPECTED_PAIR_COUNT = 46381
EXPECTED_PAIR_SHA256 = 'b43d8f9399c442c9e67753741c4c4c1e407143bf2d0cd5f44b5d73f2df43d4c1'
EXPECTED_SINGLE_EVENTS = {12280, 12282, 12287, 12288}
NATIVE_HEAD = '2a7ca44fbda3abaa4df355b183ed7d7478eef7c1'
PAYLOAD_SHA256 = 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'
LITERAL_CONTROLS = (
    (10114, 12280, '-3', '-1'), (10114, 12287, '-3', '-1'),
    (11169, 12280, '-3', '-1'), (11169, 12287, '-3', '-1'),
    (11225, 12280, '-2', '-1'), (11225, 12287, '-2', '-1'),
    (12195, 12280, '-3', '-1'), (12195, 12287, '-3', '-1'),
    (12280, 12290, '-1', '1'), (12280, 12398, '-1', '1'),
    (12280, 12282, '-3', '-2'), (12280, 12288, '-3', '2'),
    (12282, 12288, '1', '3'), (12282, 12287, '1', '3'),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(dst, src, coefficient=Q(1)):
    if not coefficient:
        return
    for j, value in src.items():
        result = dst.get(j, Q(0)) + coefficient * value
        if result:
            dst[j] = result
        else:
            dst.pop(j, None)


def dot(row, column):
    if len(row) > len(column):
        row, column = column, row
    return sum((value * column[j] for j, value in row.items() if j in column), Q(0))


def multiply(left, right):
    answer = []
    for row in left:
        out = {}
        for j, value in row.items():
            add(out, right[j], value)
        answer.append(out)
    return answer


def outer_add(matrix, column, row, coefficient=Q(1)):
    for i, value in column.items():
        add(matrix[i], row, coefficient * value)


def authenticate_primary(package):
    path = package / 'verify.py'
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    need(actual == PRIMARY_SHA256, ('primary verifier SHA-256 mismatch', actual))
    name = '_authenticated_contact_primary'
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def direction(vector):
    if not vector:
        return None, Q(0)
    coefficient = vector[min(vector)]
    return tuple(sorted((i, x / coefficient) for i, x in vector.items())), coefficient


def project(vector, target):
    """vector = component*target + scale*normalized_quotient."""
    pivot = min(target)
    component = vector.get(pivot, Q(0)) / target[pivot]
    quotient = dict(vector)
    add(quotient, target, -component)
    key, scale = direction(quotient)
    return key, scale, component


def target_in_span(first, second):
    ka, sa, ca = first
    kb, sb, cb = second
    if ka is None:
        return ca != 0 or (kb is None and cb != 0)
    if kb is None:
        return cb != 0
    return ka == kb and ca * sb != cb * sa


def rref(equations):
    """Canonical RREF in x,y,Z, with RHS in the fourth slot."""
    basis = {}
    for equation in equations:
        row = list(map(Q, equation))
        for pivot, earlier in sorted(basis.items()):
            if row[pivot]:
                factor = row[pivot]
                row = [a - factor * b for a, b in zip(row, earlier)]
        pivot = next((i for i in range(3) if row[i]), None)
        if pivot is None:
            if row[3]:
                return None
            continue
        factor = row[pivot]
        row = [x / factor for x in row]
        for old_pivot, earlier in list(basis.items()):
            if earlier[pivot]:
                factor = earlier[pivot]
                basis[old_pivot] = [a - factor * b for a, b in zip(earlier, row)]
        basis[pivot] = row
    return tuple(tuple(basis[p]) for p in sorted(basis))


def classify_system(rows, determinant):
    """None means this deliberately narrow rule proves neither obstruction.

    The pinned source needs only a fixed-x or fixed-y substitution after
    the linear monomial test. Unexpected residual shapes are rejected.
    """
    if rows is None:
        return 'inconsistent_monomial_system'
    residual = [determinant[1], determinant[2], determinant[3], -determinant[0]]
    for row in rows:
        pivot = next(i for i in range(3) if row[i])
        if residual[pivot]:
            factor = residual[pivot]
            residual = [a - factor * b for a, b in zip(residual, row)]
    if not any(residual):
        return 'determinant_in_C1_linear_span'
    if len(rows) != 1:
        return None
    row = rows[0]
    pivots = [i for i in range(3) if row[i]]
    if len(pivots) != 1 or pivots[0] == 2:
        return None
    fixed = pivots[0]
    value = row[3] / row[fixed]
    d0, dx, dy, dxy = determinant
    if fixed == 0:
        if d0 + dx * value == 0 and dy + dxy * value == 0:
            return 'determinant_zero_after_fixed_x'
    elif d0 + dy * value == 0 and dx + dxy * value == 0:
        return 'determinant_zero_after_fixed_y'
    return None


def transfer_coefficients(module, program, pairs):
    """Sweep from/to small direction classes, not once per ordinary event."""
    requests = defaultdict(set)
    for (a, b), (_, special) in pairs.items():
        requests[special].add(b if special == a else a)
    answer = {}
    for special, others in sorted(requests.items()):
        later = {x for x in others if x > special}
        earlier = {x for x in others if x < special}
        if later:
            column = {program[special][1]: Q(1)}
            for index in range(special + 1, max(later) + 1):
                event = program[index]
                op, dst = event[:2]
                if index in later:
                    answer[special, index] = column.get(module.source(event), Q(0))
                if op == 'ADD':
                    value = column.get(dst, Q(0)) + module.coefficient(event) * column.get(event[2], Q(0))
                elif op == 'COPY':
                    value = module.coefficient(event) * column.get(event[2], Q(0))
                elif op == 'SCALE':
                    value = module.coefficient(event) * column.get(dst, Q(0))
                elif op in ('INIT', 'CLEAR'):
                    value = Q(0)
                else:
                    need(op == 'MOVE', ('unknown transfer event', event))
                    continue
                if value:
                    column[dst] = value
                else:
                    column.pop(dst, None)
        if earlier:
            row = {module.source(program[special]): Q(1)}
            for index in range(special - 1, min(earlier) - 1, -1):
                event = program[index]
                op, dst = event[:2]
                if index in earlier:
                    answer[index, special] = row.get(dst, Q(0))
                if op in ('ADD', 'COPY'):
                    src = event[2]
                    value = row.get(src, Q(0)) + module.coefficient(event) * row.get(dst, Q(0))
                    if value:
                        row[src] = value
                    else:
                        row.pop(src, None)
                    if op == 'COPY':
                        row.pop(dst, None)
                elif op == 'SCALE':
                    value = module.coefficient(event) * row.get(dst, Q(0))
                    if value:
                        row[dst] = value
                    else:
                        row.pop(dst, None)
                elif op in ('INIT', 'CLEAR'):
                    row.pop(dst, None)
                else:
                    need(op == 'MOVE', ('unknown reverse transfer event', event))
    need(set(answer) == set(pairs), 'incomplete pair transfers')
    return answer


def small_boundary_system(a, b, kind, tau, projections_u, projections_v):
    """C1 in the exact basis (target direction, normalized quotient)."""
    if kind == 'column_common':
        pa, pb = projections_u[a][2], projections_u[b][2]
        _, sa, ca = projections_v[a]
        _, sb, cb = projections_v[b]
        equations = ((pa * ca, pb * cb, tau * pb * ca, -1),
                     (pa * sa, pb * sb, tau * pb * sa, 0))
    else:
        qa, qb = projections_v[a][2], projections_v[b][2]
        _, sa, ca = projections_u[a]
        _, sb, cb = projections_u[b]
        equations = ((qa * ca, qb * cb, tau * qa * cb, -1),
                     (qa * sa, qb * sb, tau * qa * sb, 0))
    return rref(equations)


def expanded_boundary_system(a, b, tau, restricted_u, restricted_v, target_u, target_v):
    equations = {}
    terms = ((0, restricted_u[a], restricted_v[a], Q(1)),
             (1, restricted_u[b], restricted_v[b], Q(1)),
             (2, restricted_u[b], restricted_v[a], tau),
             (3, target_u, target_v, Q(-1)))
    for slot, column, row, factor in terms:
        for i, u in column.items():
            for j, v in row.items():
                equations.setdefault((i, j), [Q(0)] * 4)[slot] += factor * u * v
    return rref(equations.values())


def rank_and_null(matrix):
    """Independent sparse elimination, using literal endpoint rows only."""
    basis = {}
    for initial in matrix:
        row = dict(initial)
        while row:
            pivot = min(row)
            if pivot not in basis:
                factor = row[pivot]
                basis[pivot] = {j: x / factor for j, x in row.items()}
                break
            add(row, basis[pivot], -row[pivot])
    if len(basis) == len(matrix):
        return len(basis), {}
    free = next(j for j in range(len(matrix)) if j not in basis)
    null = {free: Q(1)}
    for pivot, row in sorted(basis.items(), reverse=True):
        value = -sum(x * null.get(j, Q(0)) for j, x in row.items() if j != pivot)
        if value:
            null[pivot] = value
    need(null and all(dot(row, null) == 0 for row in matrix), 'literal null vector failed')
    return len(basis), null


def positive_control(module):
    program = [['ADD', 0, 1, '1', 0], ['ADD', 1, 0, '1', 0], ['ADD', 0, 1, '1', 0],
               ['ADD', 0, 1, '-1', 0], ['ADD', 1, 0, '-1', 0], ['ADD', 0, 1, '-1', 0]]
    original, _ = module.literal(program, 2)
    identity = [{0: Q(1)}, {1: Q(1)}]
    need(original == identity, 'positive control source identity')
    program[0][3], program[1][3], program[2][3] = '0', '2', '3/2'
    endpoint, _ = module.literal(program, 2)
    need(endpoint == [{0: Q(2)}, {1: Q(1, 2)}], 'positive joint endpoint')
    need(rank_and_null(endpoint)[0] == 2, 'positive joint rank')
    repaired = [{j: value * (Q(1, 2) if j == 0 else 1) * (2 if i == 1 else 1)
                 for j, value in row.items()} for i, row in enumerate(endpoint)]
    need(repaired == identity, 'positive dyadic supported hub repair')
    need(classify_system(rref(((0, 2, 0, 1),)), (Q(1), Q(0), Q(0), Q(0))) is None,
         'singularity classifier rejected the positive joint control')
    return {'changed_coefficients': ['0', '2', '3/2'], 'endpoint_diagonal': ['2', '1/2'],
            'supported_dyadic_hub_repair': True, 'scope': 'algebraic control, not a MOVE contraction'}


def verify(package):
    started = time.monotonic()
    module = authenticate_primary(package)
    word, payload = module.load_word()
    need(payload == PAYLOAD_SHA256, 'wrong native canonical payload')
    program, n, owned = word['program'], word['public'], word['owned_fields']
    endpoint, dimension, K, R = module.source_check(word)
    original, _ = module.literal(program, n, owned)
    need(original == endpoint, 'original full public endpoint is not A')
    need(program[DELETE] == ['ADD', 796, 438, '-1', 245], 'wrong fixed deletion')
    need(program[10946] == ['MOVE', 438, 911, 245, False] and
         program[14152] == ['MOVE', 438, 245, 127, False], 'wrong contraction MOVEs')
    touches = [i for i in range(10947, 14152) if program[i][1] == 438 or
               (program[i][0] in ('ADD', 'COPY') and program[i][2] == 438)]
    need(touches == [DELETE], 'unexpected intervening touch of helper 438')
    need(dimension[245] - dimension[911] == dimension[127] - dimension[245] == 1,
         'contraction is not ranks 1+1')
    Rbar, Kbar = set(range(n)) - R, set(range(n)) - K
    need(all(i in K - R and j in R - K for i, row in enumerate(endpoint)
             for j in row if i != j), 'A-I endpoint support')
    identity = [{i: Q(1)} for i in range(n)]
    ainverse = [{j: value if j == i else -value for j, value in row.items()}
                for i, row in enumerate(endpoint)]
    need(multiply(endpoint, ainverse) == identity == multiply(ainverse, endpoint), 'A inverse')
    deleted_program = [list(event) for event in program]
    deleted_program[DELETE][3] = '0'
    baseline, prefix = module.literal(deleted_program, n, owned, True)
    suffix = module.responses(deleted_program, n, owned)
    u0 = {i: -module.coefficient(program[DELETE]) * value for i, value in suffix[DELETE].items()}
    v0 = prefix[DELETE]
    expected = [dict(row) for row in endpoint]
    outer_add(expected, u0, v0)
    need(baseline == expected, 'deleted endpoint rank-one formula')
    aiu0 = module.inverse_endpoint_column(u0, word['live'])
    denominator = 1 + dot(v0, aiu0)
    need(denominator == 1, ('deleted baseline determinant is not one', denominator))
    v0ai = {}
    for j, value in v0.items():
        add(v0ai, ainverse[j], value)
    baseline_inverse = [dict(row) for row in ainverse]
    outer_add(baseline_inverse, aiu0, v0ai, -1 / denominator)
    need(multiply(baseline, baseline_inverse) == identity == multiply(baseline_inverse, baseline),
         'deleted baseline inverse verification')
    defect = {}
    for i in sorted(Rbar):
        row = {j: baseline[i].get(j, Q(0)) - endpoint[i].get(j, Q(0)) for j in sorted(Kbar)
               if baseline[i].get(j, Q(0)) != endpoint[i].get(j, Q(0))}
        if row:
            defect[i] = row
    need(defect, 'deleted C1 defect is zero')
    pivot = min(defect)
    target_v = defect[pivot]
    column = min(target_v)
    target_u = {i: row.get(column, Q(0)) / target_v[column] for i, row in defect.items()}
    need(all(value and defect[i] == {j: value * x for j, x in target_v.items()}
             for i, value in target_u.items()), 'deleted C1 defect is not rank one')
    gates = sorted(set(prefix) - {DELETE})
    need(set(gates) == {i for i, event in enumerate(program) if i != DELETE and module.scalar_event(event)},
         'scalar compensator domain mismatch')
    restricted_u = {k: {i: x for i, x in suffix[k].items() if i in Rbar} for k in gates}
    restricted_v = {k: {i: x for i, x in prefix[k].items() if i in Kbar} for k in gates}
    pu = {k: project(restricted_u[k], target_u) for k in gates}
    pv = {k: project(restricted_v[k], target_v) for k in gates}
    zero_u = {k for k in gates if not restricted_u[k]}
    zero_v = {k for k in gates if not restricted_v[k]}
    common_u = {k for k in gates if pu[k][0] is None and pu[k][2]}
    common_v = {k for k in gates if pv[k][0] is None and pv[k][2]}
    pairs = {}
    for special in sorted(common_u):
        for other in sorted(zero_u | common_u):
            if other != special and target_in_span(pv[special], pv[other]):
                pairs.setdefault(tuple(sorted((special, other))), ('column_common', special))
    for special in sorted(common_v):
        for other in sorted(zero_v | common_v):
            if other != special and target_in_span(pu[special], pu[other]):
                pairs.setdefault(tuple(sorted((special, other))), ('row_common', special))
    domain_hash = hashlib.sha256(json.dumps(sorted(pairs), separators=(',', ':')).encode()).hexdigest()
    need(len(pairs) == EXPECTED_PAIR_COUNT and domain_hash == EXPECTED_PAIR_SHA256,
         ('independently rebuilt pair-domain pin differs', len(pairs), domain_hash))
    transfers = transfer_coefficients(module, deleted_program, pairs)
    inverse_responses = {}
    for k in gates:
        value = module.inverse_endpoint_column(suffix[k], word['live'])
        add(value, aiu0, -dot(v0, value) / denominator)
        inverse_responses[k] = value
    self_dot = {k: dot(prefix[k], inverse_responses[k]) for k in gates}
    # Recompute all one-compensator possibilities to close x=0 or y=0.
    need(common_u & common_v == EXPECTED_SINGLE_EVENTS, 'one-compensator event domain differs')
    singles = []
    for k in sorted(common_u & common_v):
        delta = -1 / (pu[k][2] * pv[k][2])
        determinant = 1 + delta * self_dot[k]
        need(determinant == 0, ('nonsingular one-compensator candidate', k, delta, determinant))
        singles.append({'event': k, 'delta': str(delta),
                        'new_coefficient': str(module.coefficient(program[k]) + delta), 'determinant': '0'})
    classifications = Counter()
    for (a, b), (kind, _) in sorted(pairs.items()):
        tau = transfers[a, b]
        rows = small_boundary_system(a, b, kind, tau, pu, pv)
        aa, bb = self_dot[a], self_dot[b]
        ab, ba = dot(prefix[a], inverse_responses[b]), dot(prefix[b], inverse_responses[a])
        determinant = (Q(1), aa, bb, aa * bb - ab * ba + tau * ab)
        classification = classify_system(rows, determinant)
        need(classification is not None, ('unclosed joint coefficient system', a, b, rows, determinant))
        classifications[classification] += 1
    need(sum(classifications.values()) == len(pairs), 'incomplete joint classification')
    literal_controls = []
    mixed_term_rejection = None
    for a, b, sx, sy in LITERAL_CONTROLS:
        x, y = Q(sx), Q(sy)
        need((a, b) in pairs, ('literal control missing from domain', a, b))
        tau = transfers[a, b]
        kind = pairs[a, b][0]
        need(small_boundary_system(a, b, kind, tau, pu, pv) ==
             expanded_boundary_system(a, b, tau, restricted_u, restricted_v, target_u, target_v),
             ('compressed/expanded C1 equations differ', a, b))
        changed = [list(event) for event in deleted_program]
        for index, delta in ((a, x), (b, y)):
            event = changed[index]
            event[2 if event[0] == 'SCALE' else 3] = str(module.coefficient(event) + delta)
        literal, _ = module.literal(changed, n, owned)
        predicted = [dict(row) for row in baseline]
        outer_add(predicted, suffix[a], prefix[a], x)
        outer_add(predicted, suffix[b], prefix[b], y)
        outer_add(predicted, suffix[b], prefix[a], x * y * tau)
        need(literal == predicted, ('literal joint expansion differs', a, b))
        if (a, b) == (12280, 12282):
            need(x * y * tau and suffix[b] and prefix[a], 'mixed-term control is degenerate')
            mutant = [dict(row) for row in baseline]
            outer_add(mutant, suffix[a], prefix[a], x)
            outer_add(mutant, suffix[b], prefix[b], y)
            need(mutant != literal, 'dropping the mixed term was not rejected')
            mixed_term_rejection = {'events': [a, b], 'transfer': str(tau),
                                    'mutation': 'omit x*y*tau*u_b*v_a', 'rejected': True}
        need(all(literal[i].get(j, Q(0)) == endpoint[i].get(j, Q(0)) for i in Rbar for j in Kbar),
             ('literal C1 differs', a, b))
        rank, null = rank_and_null(literal)
        need(rank < n, ('literal endpoint nonsingular', a, b))
        literal_controls.append({'events': [a, b], 'deltas': [sx, sy], 'rank': rank,
                                 'null_vector': {str(i): str(x) for i, x in sorted(null.items())}})
    need(mixed_term_rejection is not None, 'missing mixed-term rejection control')
    positive = positive_control(module)
    return {'schema_version': 1, 'status': 'PASS',
            'claim': 'fixed deletion 10947 plus two arbitrary scalar compensators has no invertible endpoint satisfying necessary C1; no new kappa',
            'primary_verifier_sha256': PRIMARY_SHA256, 'native_head': NATIVE_HEAD,
            'native_payload_sha256': PAYLOAD_SHA256, 'python': platform.python_version(),
            'deleted_event': DELETE, 'original_endpoint_verified': True,
            'deleted_baseline_determinant': '1', 'deleted_baseline_inverse_verified': True,
            'eligible_scalar_compensators': len(gates),
            'C1_defect': {'rank': 1, 'column_nonzeros': len(target_u), 'row_nonzeros': len(target_v)},
            'direction_classes': {'nonzero_common_output': len(common_u), 'zero_output': len(zero_u),
                                  'nonzero_common_input': len(common_v), 'zero_input': len(zero_v)},
            'pair_domain': {'count': len(pairs), 'sha256': domain_hash,
                            'column_common': sum(kind == 'column_common' for kind, _ in pairs.values()),
                            'additional_row_common': sum(kind == 'row_common' for kind, _ in pairs.values())},
            'one_compensator_closure': singles, 'joint_classification': dict(sorted(classifications.items())),
            'literal_controls': literal_controls, 'positive_joint_control': positive,
            'semantic_mutation_controls': [mixed_term_rejection],
            'arithmetic_scope': 'all rational coefficient changes, including zero and non-dyadic values; legality is never used to accept a candidate',
            'limitations': 'one fixed deletion, existing scalar coefficients only, fixed operands/order/frames; no new word, invoice or frontier change',
            'elapsed_seconds': round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True, help='primary contact-rigidity package directory')
    parser.add_argument('--output', type=Path, help='optional JSON certificate destination')
    args = parser.parse_args()
    result = verify(args.package.resolve())
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
