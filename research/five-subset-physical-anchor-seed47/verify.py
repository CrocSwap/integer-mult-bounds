#!/usr/bin/env python3
"""Exact spatial Gaussian-dyadic lowering of one frozen common-frame block.

Apache-2.0. Prepared for ToikY with substantial OpenAI Codex assistance.
The output-anchor identity is standard linear algebra, not a novelty claim.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N, ROLES, BASE = 512, 13, 'c5108f0f68d482e5712a8e26a5978d47762dfc16'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def parity(x):
    return x.bit_count() & 1


def span(rows):
    out = {0}
    for x in rows:
        out |= {v ^ x for v in out}
    return out


def orthogonal(rows):
    return {x for x in range(N) if all(not parity(x & r) for r in rows)}


def basis(space):
    if space == {0}:
        return []
    for x in sorted(space):
        if parity(x):
            tail = basis({v for v in space if not parity(v & x)})
            if tail is not None:
                return [x] + tail
    return None


def extension(rows):
    out = list(rows)
    image = span(out)
    need(len(image) == 1 << len(out), 'independent child directions')
    for i in range(9):
        if 1 << i not in image:
            out.append(1 << i)
            image |= {x ^ (1 << i) for x in image}
    need(len(out) == 9 and len(image) == N, 'invertible address map')
    return out


def table(columns):
    need(len(columns) == 9 and all(type(v) is int and 0 < v < N for v in columns),
         'address columns')
    out = [0] * N
    for x in range(1, N):
        b = x & -x
        out[x] = out[x ^ b] ^ columns[b.bit_length() - 1]
    need(len(set(out)) == N, 'bijective address permutation')
    return out


def inverse_columns(columns):
    p = table(columns)
    inv = [0] * N
    for x, y in enumerate(p):
        inv[y] = x
    return [inv[1 << i] for i in range(9)]


def phase(factors, k):
    return sum(sign * parity(mask & k) for mask, sign in factors) % 4


def recipe(role, old, new, directions):
    need(directions is not None, 'orthonormal residual exists')
    g = extension(directions)
    delta = 0
    for i in range(9):
        d = (phase(new, 1 << i) - phase(old, 1 << i)
             - sum(parity(v & (1 << i)) for v in directions)) % 4
        need(d in (0, 2), 'rank-zero Pauli adapter')
        if d:
            delta |= 1 << i
    for k in range(N):
        need((phase(new, k) - phase(old, k)) % 4 ==
             (sum(parity(v & k) for v in directions) + 2 * parity(delta & k)) % 4,
             'exact adapter phase on every character')
    stream = [['PERM', role, inverse_columns(g)],
              ['CHILD', role, len(directions), False], ['PERM', role, g]]
    if delta:
        stream.append(['SHIFT', role, delta])
    return stream, {'role': role, 'from_factors': old, 'to_factors': new,
                    'basis': directions, 'shift': delta}


def reverse(stream):
    out = []
    for rec in reversed(stream):
        op, r, *a = rec
        if op == 'PERM':
            out.append([op, r, inverse_columns(a[0])])
        elif op == 'CHILD':
            # C_r^2 is the Pauli translation, so C_r^-1=X_r C_r.
            # Pay the wrapper explicitly and use only forward children.
            if not a[1]:
                out.append(['SHIFT', r, (1 << a[0]) - 1])
            out.append([op, r, a[0], False])
        elif op == 'SHIFT':
            out.append(rec)
        elif op == 'AXPY':
            out.append([op, r, a[0], -a[1], a[2]])
        else:
            raise ValueError('unknown primitive')
    return out


def construct():
    f = load(HERE / 'inputs/pr1230-WITNESS.json')['witness']
    s, t, alpha, beta = [f[k] for k in
                        ('source_labels', 'target_labels', 'source_signs', 'target_signs')]
    need(s == [31, 55, 457, 458, 481, 482] and t == [47, 59, 87, 151, 279, 451],
         'frozen label coverage')
    need(all((1, 0, -1, 0)[(x & y).bit_count() % 4] == alpha[i] * beta[j]
             for i, x in enumerate(s) for j, y in enumerate(t)), 'half-scaled kernel')
    u = span(f['U_basis'])
    ub, wb = basis(u), basis(orthogonal(f['U_basis']))
    need(ub is not None and wb is not None and len(ub) == 4 and len(wb) == 5,
         'separator basis')
    full = [[1 << i, 1] for i in range(9)]
    frames = [[[x, 1]] for x in s] + [full + [[x, -1]] for x in t] + [[[x, 1] for x in ub]]
    programs = []
    for anchor in [None] + list(range(6)):
        stream, transforms = [], []
        def move(role, old, new, directions, invert=False):
            code, rec = recipe(role, old, new, directions)
            if invert:
                code = reverse(code)
                rec['from_factors'], rec['to_factors'] = rec['to_factors'], rec['from_factors']
                rec['inverse_child'] = True
            rec.update({'start': len(stream), 'end': len(stream) + len(code)})
            transforms.append(rec)
            stream.extend(code)
        for i, x in enumerate(s):
            move(i, [], frames[i], [x])
        for j, x in enumerate(t):
            move(6 + j, [], frames[6 + j], basis(orthogonal([x])))
        if anchor is None:
            move(12, [], frames[12], ub)
            logical = ([[12, i, alpha[i], 0] for i in range(6)]
                       + [[6 + j, 12, beta[j], 1] for j in range(6)]
                       + [[12, i, -alpha[i], 0] for i in reversed(range(6))]
                       + [[6 + j, 12, -beta[j], 1] for j in range(6)])
        else:
            p = 6 + anchor
            logical = ([[6 + j, p, -beta[j] * beta[anchor], 0] for j in range(6) if j != anchor]
                       + [[p, i, beta[anchor] * alpha[i], 1] for i in range(6)]
                       + [[6 + j, p, beta[j] * beta[anchor], 0] for j in range(6) if j != anchor])
        for dst, src, sign, den in logical:
            if dst == 12:
                directions = basis({v for v in u if not parity(v & s[src])})
            elif src == 12:
                directions = basis({v for v in orthogonal(f['U_basis']) if not parity(v & t[dst - 6])})
            elif src < 6:
                directions = basis(orthogonal([s[src], t[dst - 6]]))
            else:
                directions = [t[src - 6], t[dst - 6]]
            move(src, frames[src], frames[dst], directions)
            stream.append(['AXPY', dst, src, sign, den])
            move(src, frames[src], frames[dst], directions, invert=True)
        for i, x in enumerate(s):
            move(i, frames[i], full, basis(orthogonal([x])))
        for j, x in enumerate(t):
            move(6 + j, frames[6 + j], full, [x])
        move(12, frames[12] if anchor is None else [], full, wb if anchor is None else [1 << i for i in range(9)])
        programs.append({'name': 'baseline' if anchor is None else 'anchor-' + str(anchor),
                         'anchor': anchor, 'logical_word': logical, 'stream': stream,
                         'transforms': transforms})
    return {'h': 9, 'roles': ROLES, 'seed': 47, 'base_commit': BASE,
            'U_orthonormal_basis': ub, 'programs': programs}


def normalize(row):
    re, im, e = row
    while e and all(not (x & 1) for x in re + im):
        re, im, e = [x // 2 for x in re], [x // 2 for x in im], e - 1
    return re, im, e


def quarter(row, mask, inverse=False):
    re, im, e = row
    rr, ii = [0] * len(re), [0] * len(re)
    for x in range(len(re)):
        y = x ^ mask
        if inverse:
            rr[x], ii[x] = re[x] + im[x] + re[y] - im[y], im[x] - re[x] + re[y] + im[y]
        else:
            rr[x], ii[x] = re[x] - im[x] + re[y] + im[y], re[x] + im[x] + im[y] - re[y]
    return normalize((rr, ii, e + 1))


def execute(stream):
    length = N * ROLES
    state = []
    for r in range(ROLES):
        re = [0] * length
        re[r * N] = 1
        state.append((re, [0] * length, 0))
    peak = Fraction(1)
    for rec in stream:
        op, role, *a = rec
        need(type(role) is int and 0 <= role < ROLES, 'physical role')
        re, im, e = state[role]
        if op == 'PERM':
            need(len(a) == 1, 'PERM fields')
            perm = table(a[0])
            rr, ii = [0] * length, [0] * length
            for x in range(length):
                y = (x // N) * N + perm[x % N]
                rr[y], ii[y] = re[x], im[x]
            state[role] = rr, ii, e
        elif op == 'SHIFT':
            need(len(a) == 1 and type(a[0]) is int and 0 <= a[0] < N, 'SHIFT fields')
            state[role] = [re[x ^ a[0]] for x in range(length)], [im[x ^ a[0]] for x in range(length)], e
        elif op == 'CHILD':
            need(len(a) == 2 and type(a[0]) is int and 1 <= a[0] <= 9 and type(a[1]) is bool, 'CHILD fields')
            for q in range(a[0]):
                state[role] = quarter(state[role], 1 << q, a[1])
                rr, ii, ee = state[role]
                peak = max(peak, Fraction(sum(abs(x) for x in rr + ii), 1 << ee))
        elif op == 'AXPY':
            need(len(a) == 3 and all(type(x) is int for x in a) and 0 <= a[0] < ROLES
                 and a[0] != role and a[1] in (-1, 1) and a[2] in (0, 1), 'AXPY fields')
            sr, si, se = state[a[0]]
            ee = max(e, se + a[2])
            rr = [(x << (ee - e)) + a[1] * (y << (ee - se - a[2])) for x, y in zip(re, sr)]
            ii = [(x << (ee - e)) + a[1] * (y << (ee - se - a[2])) for x, y in zip(im, si)]
            state[role] = normalize((rr, ii, ee))
        else:
            raise ValueError('unknown physical primitive')
        rr, ii, ee = state[role]
        peak = max(peak, Fraction(sum(abs(x) for x in rr + ii), 1 << ee))
    return state, str(peak)


def expected(inverse=False):
    f = load(HERE / 'inputs/pr1230-WITNESS.json')['witness']
    alpha, beta = f['source_signs'], f['target_signs']
    impulse = ([1] + [0] * (N - 1), [0] * N, 0)
    for i in range(9):
        impulse = quarter(impulse, 1 << i, inverse)
    fr, fi, fe = impulse
    rows = []
    for r in range(ROLES):
        re, im, e = [0] * (N * ROLES), [0] * (N * ROLES), fe
        re[r * N:(r + 1) * N], im[r * N:(r + 1) * N] = fr, fi
        if 6 <= r < 12:
            re, im, e = [x * 2 for x in re], [x * 2 for x in im], fe + 1
            for i in range(6):
                c = alpha[i] * beta[r - 6] * (-1 if inverse else 1)
                re[i * N:(i + 1) * N], im[i * N:(i + 1) * N] = [c * x for x in fr], [c * x for x in fi]
        rows.append(normalize((re, im, e)))
    return rows


def invoice(program):
    stream = program['stream']
    profile = Counter(x[2] for x in stream if x[0] == 'CHILD')
    copies = 0
    for x in stream:
        if x[0] not in ('PERM', 'SHIFT'):
            continue
        perm = table(x[2]) if x[0] == 'PERM' else [i ^ x[2] for i in range(N)]
        visited = set()
        for i in range(N):
            if i in visited:
                continue
            cycle, j = [], i
            while j not in visited:
                cycle.append(j)
                visited.add(j)
                j = perm[j]
            if len(cycle) > 1:
                # One complex temporary: save, rotate, then final write.
                copies += len(cycle) + 1
    return {'profile': {str(k): profile[k] for k in sorted(profile)},
            'rank_mass': sum(k * v for k, v in profile.items()), 'children': sum(profile.values()),
            'ADDs': sum(x[0] == 'AXPY' for x in stream),
            'half_scales': sum(x[0] == 'AXPY' and x[4] == 1 for x in stream),
            'address_permutations': sum(x[0] == 'PERM' for x in stream),
            'translations': sum(x[0] == 'SHIFT' for x in stream),
            'rank_zero_complex_value_copies': copies,
            'AXPY_complex_value_accesses': 3 * N * sum(x[0] == 'AXPY' for x in stream),
            'dyadic_scalar_multiplications': N * sum(x[0] == 'AXPY' and x[4] == 1 for x in stream),
            'address_xor_upper_bound': 9 * N * sum(x[0] in ('PERM', 'SHIFT') for x in stream),
            'permutation_workspace': 'one complex scalar temporary plus512 visited bits; fixed table/program metadata additional',
            'COPYs': 0, 'ERASEs': 0, 'roles': ROLES, 'addresses_per_role': N,
            'raw_input_columns': N * ROLES}


def pins():
    sources = load(HERE / 'SOURCES.json')
    need(sources['base_commit'] == BASE, 'fixed base')
    need({x['path'] for x in sources['retained_inputs']} ==
         {'inputs/pr1230-WITNESS.json', 'inputs/pr1230-PROOF.md', 'inputs/pr1230-README.md'}, 'retained source inventory')
    need(len(sources['retained_inputs']) == 3 and len(sources['repository_inputs']) == 5, 'source cardinality')
    need({x['path'] for x in sources['repository_inputs']} ==
         {'notes/general-clifford-frames.tex', 'certificates/selected-result.json',
          'research/community-frontier1094-audit/ASSEMBLY.json',
          'research/community-frontier1094-audit/SELECTED-SOURCE.json',
          'docs/research/community-batch1099-review.md'}, 'repository input inventory')
    need(len({x['path'] for x in sources['package_sources']}) == len(sources['package_sources']),
         'checker inventory unique')
    if sys.argv[1:] != ['--write']:
        need({x['path'] for x in sources['package_sources']} ==
             {'verify.py', 'independent.py', 'test_package.py'}, 'exact checker inventory')
    for field, root in [('retained_inputs', HERE), ('repository_inputs', ROOT), ('package_sources', HERE)]:
        for x in sources[field]:
            raw = (root / x['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == x['sha256'], 'source SHA256: ' + x['path'])
            if 'git_blob' in x:
                need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == x['git_blob'], 'source Git blob')
    return sum(len(sources[x]) for x in ('retained_inputs', 'repository_inputs', 'package_sources'))


def controls(programs, forward):
    """Valid physical streams with demonstrably wrong mathematical endpoints."""
    parent, anchor = programs[0]['stream'], programs[6]['stream']
    mutants = []
    adds = [i for i, x in enumerate(anchor) if x[0] == 'AXPY']
    for i in (adds[0], adds[5], adds[-1]):
        mutants.append(anchor[:i] + anchor[i + 1:])
    g = deepcopy(anchor)
    g[adds[5]][4] = 0
    mutants.append(g)
    g = deepcopy(anchor)
    g[adds[0]][3] *= -1
    mutants.append(g)
    i = next(i for i, x in enumerate(anchor) if x[0] == 'SHIFT')
    mutants.append(anchor[:i] + anchor[i + 1:])
    g = deepcopy(anchor)
    i = next(i for i, x in enumerate(g) if x[0] == 'CHILD')
    g[i][3] = True
    mutants.append(g)
    i = next(i for i, x in enumerate(anchor) if x[0] == 'CHILD' and x[2] == 9)
    mutants.append(anchor[:i] + anchor[i + 1:])
    for g in mutants:
        actual, _ = execute(g)
        need(actual != forward, 'endpoint mutation must fail')
    # Clean source-only replay misses the original helper's old-value correction.
    parent_adds = [i for i, x in enumerate(parent) if x[0] == 'AXPY']
    keep = set(parent_adds[-6:])
    actual, _ = execute([x for i, x in enumerate(parent) if i not in keep])
    need(actual != forward and all(a[0][:6 * N] == b[0][:6 * N]
         and a[1][:6 * N] == b[1][:6 * N] and a[2] == b[2]
         for a, b in zip(actual, forward)), 'dirty-helper control requires every input')
    # Strictly improved full moments: subadditivity proves the all-p range.
    for p in (0, 1):
        old = 24 * 3 ** p + 25 * 4 ** p + 5 ** p
        new = 20 * 2 ** p + 12 * 7 ** p + 9 ** p
        need(old > new, 'moment endpoint control')
    return len(mutants) + 1


def main():
    need(sys.argv[1:] in ([], ['--write'], ['--quick']), 'usage: verify.py [--write|--quick]')
    pins()
    constructed = construct()
    program_path, result_path = HERE / 'PROGRAMS.json', HERE / 'RESULT.json'
    writing = sys.argv[1:] == ['--write']
    if not writing:
        need(canonical(load(program_path)) == canonical(constructed), 'physical program mismatch')
    forward, backward = expected(), expected(True)
    records = []
    programs = [constructed['programs'][0], constructed['programs'][6]] if sys.argv[1:] == ['--quick'] else constructed['programs']
    for p in programs:
        need(all(not x[3] for x in p['stream'] if x[0] == 'CHILD'), 'forward-only child service')
        fw, fp = execute(p['stream'])
        bw, bp = execute(reverse(p['stream']))
        need(fw == forward and bw == backward, 'full physical dirty boundary: ' + p['name'])
        cost = invoice(p)
        old = p['anchor'] is None
        need(cost['rank_mass'] == (285 if old else 241)
             and cost['ADDs'] == (24 if old else 16)
             and cost['half_scales'] == (12 if old else 6), 'complete declared invoice')
        inverse_cost = invoice({'stream': reverse(p['stream'])})
        records.append({'name': p['name'], 'anchor': p['anchor'], 'invoice': cost,
                        'inverse_invoice': inverse_cost,
                        'forward_digest': digest(fw), 'inverse_digest': digest(bw),
                        'forward_component_l1_peak': fp, 'inverse_component_l1_peak': bp})
    result = {'base_commit': BASE, 'seed': 47, 'selected_anchor': 5, 'programs': records,
              'complete_columns': ROLES * N, 'coefficient_ring': 'Z[i,1/2]',
              'input_output_contract': 'All13 raw arrays; F on every output after y += Kx/2; arbitrary helper and target dirt.',
              'source_contract': 'Temporarily mutable/unobserved inside each query, restored at return; frame descents allowed.',
              'normalized_parent_budget': 13 * 9, 'new_kappa': False}
    if sys.argv[1:] != ['--quick']:
        result['semantic_controls'] = controls(constructed['programs'], forward)
    if writing:
        program_path.write_text(json.dumps(constructed, indent=2) + '\n')
        result_path.write_text(json.dumps(result, indent=2) + '\n')
    elif sys.argv[1:] == ['--quick']:
        saved = load(result_path)
        need(canonical(records) == canonical([saved['programs'][0], saved['programs'][6]]), 'quick receipt mismatch')
    else:
        need(canonical(load(result_path)) == canonical(result), 'exact receipt mismatch')
    print('PASS_PHYSICAL_OUTPUT_ANCHOR programs=' + str(len(programs)) +
          ' ADDs=24->16 rank_mass=285->241 columns=6656 no_new_kappa')


if __name__ == '__main__':
    main()
