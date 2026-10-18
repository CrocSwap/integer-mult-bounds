#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Scalar-endpoint audit of the k-dimensional port-group decoders of PR2297 (k=5) and PR2041 (k=3).

Standard library, exact F2/integer/rational arithmetic. No predecessor executable is imported; the two published
CANDIDATE.json files are vendored byte-for-byte and pinned by commit, git blob and sha256. The selected labels come
from the pinned selected replay archive (the same member and payload hash as research/paired-plane-scalar-mask-
obstruction, PR1889). The pinned research/complex-local-word-ceiling/ceiling.py is loaded for the budget section.

Port i has port space E_i = span{q_g : g in the group of port i}; the proposed contract is source E_j -> FULL,
target 0 -> E_i^perp. A cross-addition from source j into target i is rank-zero only when E_j <= E_i^perp, i.e. the
two port spaces are orthogonal (PR1889's plane rule; philippeVV, Discussion 1587, for arbitrary label subspaces).
A scalar decoder K (K[target][source]) therefore needs a common nonzero diagonal and K_ij = 0 on every other
non-free pair. The script checks, for each cover:
  1. positive control: the published F2 factorisation reproduces B0_ij = q_i.q_j, and the published charges are the
     label-support F2 ranks; the same terms are also priced by port-space span pairing rank;
  2. the free-pair census of the k-group mask (k=5: none at all, since dim E^perp = 9 - dim E);
  3. the literal integer lift K = H^T of the published terms (left factor = source, PR2297 PROOF.md; the reverse
     orientation is reported too): forbidden nonzero entries, the parity-forced ones (B0_ij = 1 forces an odd entry
     in every parity-preserving integral lift), the diagonal, and a dirty scalar replay of all 112 source columns
     with distinct dirt per target, with positive and single-defect controls;
  4. the rank any valid scalar decoder must have (exact maximum-weight clique of pairwise non-orthogonal groups);
  5. budget: rank_F2 blockdiag(Gram E_t) = sum_t dim E_t, the floor of philippeVV's Theorem 1 for 2-integral
     decoders in port-space pricing, which the direct per-port decoder attains; zero-saving thresholds (uniform u as in
     the PRs, and exact unpaid accounting, 8/9 families per port per call); incumbent-tie thresholds from ceiling.py.
The computed receipt must equal the committed RESULT.json (run with --out to regenerate it).

Scope: an audit of published binary factorisations as scalar decoders. It does not rule out even-denominator
(2-adic) cancellation decoders, an operator- or block-valued interpretation, or another call contract.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
Usage: python3 -I -B verify.py [--out]
"""

import hashlib
import importlib.util
import json
import sys
import tarfile
from fractions import Fraction
from pathlib import Path

if not __debug__:
    sys.stdout.write('FAIL_KPORT_GROUP_SCALAR_ENDPOINT refusing to run under python -O\n')
    sys.exit(2)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
CEILING = 'research/complex-local-word-ceiling/ceiling.py'
CEILING_SHA = '86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc'
FIXTURES = {
    'PR2297': dict(file='fixtures/PR2297-CANDIDATE.json', k=5,
                   commit='49f9c1a08bf1fe67a62bd6d2825aa0d03e1b1518',
                   path='research/five-plane-port-p112-seed1f7fdfe4/CANDIDATE.json',
                   git_blob='ca69901755dde5f6e8adf7dd6df936dc3ab0142d',
                   sha256='5b69c7a873f19a64ed73a1c1281d20398d2675b3281fd4fa259aed9cf91a86c0'),
    'PR2041': dict(file='fixtures/PR2041-CANDIDATE.json', k=3,
                   commit='d6569306710fe97fac2f5ccf1c062ddfe95a3711',
                   path='research/tri-plane-port-p112-seeddb093026/CANDIDATE.json',
                   git_blob='438d5c4b1564495bbfeaca2cffa42453c455b3ad',
                   sha256='92b5f2f835e9f226bba2d936b7bf9ba9300462a9112492bcb70229eb63a84901'),
}
PORTS = 112
M, FAMILIES, STAGES = 73, 896, 9
W_PER_CALL = Fraction(FAMILIES, STAGES)          # families per call
PER_PORT = W_PER_CALL / PORTS                    # 8/9 families per port per call
SELECTED_LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}  # selected word without its eight rank-8 centre children
NO_SAVING = 'relaxation has no positive saving'


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def dot(a, b):
    return (a & b).bit_count() & 1


def rank_f2_rows(rows):
    """F2 rank of a list of integer bit-rows."""
    basis = []
    for v in rows:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def pairing_rank(left, right):
    """F2 rank of the dot-product matrix between two lists of 9-bit vectors."""
    return rank_f2_rows([sum(dot(a, b) << k for k, b in enumerate(right)) for a in left])


def load_labels():
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        stream = archive.extractfile(MEMBER)
        need(stream is not None, 'missing selected phase payload')
        payload = stream.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'selected phase payload hash')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda r: r['port'])
    need([r['port'] for r in recipes] == list(range(PORTS)), 'port indexing')
    q = [r['q'] for r in recipes]
    need(len(set(q)) == PORTS and all(0 < v < 512 and dot(v, v) for v in q), 'selected odd distinct labels')
    need(all(r['terminal_Y_translation'] == r['q'] for r in recipes), 'selected unpaid-line terminal correction')
    return q


def load_fixture(name):
    f = FIXTURES[name]
    data = (HERE / f['file']).read_bytes()
    need(hashlib.sha256(data).hexdigest() == f['sha256'], '%s fixture sha256' % name)
    need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == f['git_blob'], '%s fixture git blob' % name)
    d = json.loads(data)
    return d['candidate'] if 'candidate' in d else d


def cover_of(cand, q):
    groups = [list(g) for g in (cand['blocks'] if 'blocks' in cand else cand['groups'])]  # PR2297: blocks add the pair
    need(sorted(i for g in groups for i in g) == list(range(PORTS)), 'cover partitions the 112 ports')
    for g in groups:
        need(all(dot(q[a], q[b]) == (a == b) for a in g for b in g), 'group labels orthonormal')
    return groups, {i: gi for gi, g in enumerate(groups) for i in g}


def literal_lift(cand, q):
    """H[i][j] = sum over terms of [q_i.l = 1][q_j.r = 1] as integers, with the terms' label-support charges."""
    H = [[0] * PORTS for _ in range(PORTS)]
    supports = []
    for t in cand['terms']:
        left = [i for i in range(PORTS) if dot(q[i], t['left_label'])]
        right = [j for j in range(PORTS) if dot(q[j], t['right_label'])]
        need(left == list(t['left_support']) and right == list(t['right_support']), 'term supports match labels')
        need(pairing_rank([q[i] for i in left], [q[j] for j in right]) == t['copy_rank'], 'published label charge')
        supports.append((left, right))
        for i in left:
            row = H[i]
            for j in right:
                row[j] += 1
    return H, supports


def max_weight_clique(nodes, adj, weight):
    """Exact maximum-weight clique of a small graph by branch and bound."""
    best, best_w = [], 0

    def grow(chosen, cw, cand):
        nonlocal best, best_w
        if cw + sum(weight[v] for v in cand) <= best_w:
            return
        if cw > best_w:
            best, best_w = list(chosen), cw
        for v in sorted(cand, key=lambda x: -weight[x]):
            cand = cand - {v}
            grow(chosen + [v], cw + weight[v], {u for u in cand if u in adj[v]})
            if cw + sum(weight[u] for u in cand) <= best_w:
                return
    grow([], 0, set(nodes))
    return best


def mask_violations(K, free):
    bad = [(i, j) for i in range(PORTS) for j in range(PORTS) if i != j and (i, j) not in free and K[i][j] != 0]
    return bad, sorted({K[i][i] for i in range(PORTS)})


def is_scalar_decoder(K, free):
    bad, diag = mask_violations(K, free)
    return not bad and len(diag) == 1 and diag[0] != 0


def dirty_failures(K, free):
    """Replay every source basis column on targets with distinct dirt d_i = 1000 + i. A column fails if a non-free
    target moves, or if the diagonal output is not d_j + c for the most common diagonal c."""
    diag = [K[i][i] for i in range(PORTS)]
    c = max(set(diag), key=diag.count)
    failing = 0
    for j in range(PORTS):
        out = [1000 + i + K[i][j] for i in range(PORTS)]
        ok = all(out[i] == 1000 + i for i in range(PORTS) if i != j and (i, j) not in free)
        failing += not (ok and c != 0 and out[j] == 1000 + j + c)
    return failing


def load_ceiling():
    path = ROOT / CEILING
    need(hashlib.sha256(path.read_bytes()).hexdigest() == CEILING_SHA, 'ceiling.py pin')
    spec = importlib.util.spec_from_file_location('pinned_complex_ceiling', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def has_saving(cm, local, centre, unpaid):
    try:
        cm.ceiling(local, M, FAMILIES, STAGES, centre, unpaid=unpaid)
        return True
    except ValueError as e:
        need(str(e) == NO_SAVING, 'unexpected ceiling error: %s' % e)
        return False


def tie_threshold(cm, a, unpaid, r):
    """Largest decoder charge, as rank-r children added to the selected word, whose moment still passes at a."""
    lo, hi = 0, 2000 // r
    while lo < hi:
        mid = (lo + hi + 1) // 2
        prof = dict(SELECTED_LOCAL)
        prof[r] = prof.get(r, 0) + mid
        if cm.relax(prof, M, FAMILIES, STAGES, mid * r, a, unpaid=unpaid)[1] < 1:
            lo = mid
        else:
            hi = mid - 1
    return lo * r


def audit(name, q, B0, cm, a_incumbent):
    f = FIXTURES[name]
    cand = load_fixture(name)
    k = f['k']
    groups, group_of = cover_of(cand, q)
    dims = [len(g) for g in groups]
    # 1. positive control and pricing of the published terms
    H, supports = literal_lift(cand, q)
    need(all((H[i][j] & 1) == B0[i][j] for i in range(PORTS) for j in range(PORTS)), 'F2 identity sum = B0')
    label_charge = sum(t['copy_rank'] for t in cand['terms'])
    span_of = lambda ports: [q[g] for gi in sorted({group_of[p] for p in ports}) for g in groups[gi]]
    port_space_charge = sum(pairing_rank(span_of(left), span_of(right)) for left, right in supports)
    # 2. mask census
    gl = [[q[a] for a in g] for g in groups]
    orth = {(a, b): pairing_rank(gl[a], gl[b]) == 0 for a in range(len(groups)) for b in range(len(groups))}
    free = {(i, j) for i in range(PORTS) for j in range(PORTS) if i != j and orth[(group_of[i], group_of[j])]}
    orth_group_pairs = sorted((a, b) for (a, b), o in orth.items() if o and a < b)
    free_between_k = sum(1 for (i, j) in free if dims[group_of[i]] == k and dims[group_of[j]] == k)
    if 2 * k > 9:
        need(not free and all(not orth[(a, a)] for a in range(len(groups))), 'no free pair when 2k > 9')
    line_free = {(i, j) for i in range(PORTS) for j in range(PORTS) if i != j and B0[i][j] == 0}
    need(free != line_free and free <= line_free, 'group mask is strictly finer than the line mask')
    # 3. literal lift against the mask
    K = [[H[j][i] for j in range(PORTS)] for i in range(PORTS)]   # K[target i][source j], left factor = source
    Krev = [[H[i][j] for j in range(PORTS)] for i in range(PORTS)]
    bad, diag = mask_violations(K, free)
    bad_rev, _ = mask_violations(Krev, free)
    parity = [(i, j) for (i, j) in bad if B0[i][j] == 1]
    need(len(parity) == sum(1 for i in range(PORTS) for j in range(PORTS) if i != j and B0[i][j]),
         'every B0-one pair is forbidden and odd in the literal lift')
    need(len(bad_rev) == len(bad), 'forbidden count is orientation-independent')
    ce = (0, 7)
    need(B0[0][7] == 1 and K[0][7] != 0 and Krev[0][7] != 0, 'counterexample pair')
    # 4. rank forced on any valid scalar decoder
    nodes = [a for a in range(len(groups)) if not orth[(a, a)]]
    adj = {a: {b for b in nodes if b != a and not orth[(a, b)]} for a in nodes}
    clique = max_weight_clique(nodes, adj, {a: dims[a] for a in nodes})
    need(all(not orth[(a, b)] for a in clique for b in clique if a != b), 'clique check')
    rank_floor = sum(dims[a] for a in clique)
    if 2 * k > 9:
        need(rank_floor == PORTS, 'k=5: K must be diagonal on all ports')
    # 5. budget
    gram_floor = sum(pairing_rank(gl[group_of[i]], gl[group_of[i]]) for i in range(PORTS))  # blockdiag_i Gram(E_i)
    direct = sum(dims[group_of[i]] for i in range(PORTS))       # per-port frame rank dim E_i
    need(gram_floor == direct, 'Gram floor equals the direct decoder charge')
    zero_uniform = k * W_PER_CALL
    zero_exact = PER_PORT * direct                               # sum over ports of (8/9) dim E_i unpaid per call
    need(direct - zero_exact == Fraction(direct, 9), 'direct deficit is -sum dim E_i / 9')
    need(not has_saving(cm, SELECTED_LOCAL, direct, k), 'direct decoder has no saving under uniform u')
    need(has_saving(cm, SELECTED_LOCAL, int(zero_uniform) - 1, k), 'positive control: charge below u*w saves')
    ties = {r: tie_threshold(cm, a_incumbent, k, r) for r in range(1, 10)}
    # controls
    good = [[(1 if i == j else (7 if (i, j) in free else 0)) for j in range(PORTS)] for i in range(PORTS)]
    one_bad = [row[:] for row in good]
    one_bad[ce[0]][ce[1]] = 1
    need(is_scalar_decoder(good, free) and dirty_failures(good, free) == 0, 'positive fixture accepted')
    controls = {
        'published literal lift': not is_scalar_decoder(K, free) and dirty_failures(K, free) == PORTS,
        'binary pairing B0 as endpoint': not is_scalar_decoder(B0, free),
        'line-mask decoder under the group mask': not is_scalar_decoder(
            [[(1 if i == j else (5 if (i, j) in line_free else 0)) for j in range(PORTS)] for i in range(PORTS)], free),
        'one forbidden entry': not is_scalar_decoder(one_bad, free) and dirty_failures(one_bad, free) == 1,
        'unequal diagonal': not is_scalar_decoder(
            [[((2 if i == 0 else 1) if i == j else 0) for j in range(PORTS)] for i in range(PORTS)], free),
    }
    need(all(controls.values()), 'negative controls: %s' % [c for c, ok in controls.items() if not ok])
    return dict(
        pr=name, k=k, commit=f['commit'], path=f['path'],
        group_sizes={str(s): dims.count(s) for s in sorted(set(dims))},
        published_terms=len(cand['terms']), label_support_charge=label_charge, port_space_charge=port_space_charge,
        free_ordered_pairs=len(free), free_ordered_pairs_between_k_groups=free_between_k,
        orthogonal_group_pairs=[[groups[a], groups[b]] for a, b in orth_group_pairs],
        literal_lift_forbidden_nonzero=len(bad), parity_forced_forbidden=len(parity),
        literal_lift_diagonal_values=diag, dirty_columns_failing=dirty_failures(K, free),
        counterexample=dict(target=0, source=7, q_target=q[0], q_source=q[7],
                            coefficient_left_is_source=K[0][7], coefficient_left_is_target=Krev[0][7],
                            dirty_target_in=11, literal_out=11 + K[0][7], required_out=11),
        forced_rank_lower_bound=rank_floor, max_nonorthogonal_group_clique=len(clique),
        two_integral_floor=gram_floor, direct_charge=direct,
        zero_saving_uniform_u=str(zero_uniform), zero_saving_exact=str(zero_exact),
        incumbent_tie_by_child_rank={str(r): c for r, c in ties.items()},
        min_even_denominator_gain=dict(zero_saving_uniform=str(direct - zero_uniform),
                                       zero_saving_exact=str(direct - zero_exact),
                                       incumbent_tie=direct - max(ties.values())),
        controls=sorted(controls))


def main(out=False):
    q = load_labels()
    B0 = [[dot(q[i], q[j]) for j in range(PORTS)] for i in range(PORTS)]
    cm = load_ceiling()
    incumbent = cm.ceiling({**SELECTED_LOCAL, 8: 8},
                           M, FAMILIES, STAGES, 64)
    results = [audit(n, q, B0, cm, incumbent[0]) for n in ('PR2297', 'PR2041')]
    receipt = dict(object='k-dimensional port-group decoders of PR2297 and PR2041 as scalar decoders',
                   b0_offdiagonal_ones=sum(B0[i][j] for i in range(PORTS) for j in range(PORTS) if i != j),
                   incumbent_ceiling=[str(x) for x in incumbent], results=results)
    for r in results:
        print('%s (k=%d, groups %s): F2 identity reproduces B0; charge %d label-support, %d port-space; free ordered '
              'pairs %d (%d between k-groups); literal lift: %d forbidden nonzero, %d parity-forced, diagonal %s, '
              '%d/112 dirty columns fail; rank >= %d vs %d terms; 2-integral floor = direct charge %d vs zero-saving '
              '%.1f (uniform u) / %.1f (exact), incumbent tie %d-%d' % (
                  r['pr'], r['k'], r['group_sizes'], r['label_support_charge'], r['port_space_charge'],
                  r['free_ordered_pairs'], r['free_ordered_pairs_between_k_groups'],
                  r['literal_lift_forbidden_nonzero'], r['parity_forced_forbidden'], r['literal_lift_diagonal_values'],
                  r['dirty_columns_failing'], r['forced_rank_lower_bound'], r['published_terms'],
                  r['two_integral_floor'], float(Fraction(r['zero_saving_uniform_u'])),
                  float(Fraction(r['zero_saving_exact'])), min(r['incumbent_tie_by_child_rank'].values()),
                  max(r['incumbent_tie_by_child_rank'].values())))
        c = r['counterexample']
        print('  counterexample: target 0 (q=%d) <- source 7 (q=%d): literal coefficient %d (%d with the reverse '
              'orientation); dirty target 11 -> %d, required 11' % (c['q_target'], c['q_source'],
                                                                     c['coefficient_left_is_source'],
                                                                     c['coefficient_left_is_target'], c['literal_out']))
    text = json.dumps(receipt, indent=1, sort_keys=True) + '\n'
    if out:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need((HERE / 'RESULT.json').read_text() == text, 'computed receipt differs from committed RESULT.json')
    print('PASS_KPORT_GROUP_SCALAR_ENDPOINT_AUDIT %s' % ' '.join(
        '%s:forbidden=%d,parity=%d,rank>=%d,floor=%d' % (r['pr'], r['literal_lift_forbidden_nonzero'],
                                                         r['parity_forced_forbidden'], r['forced_rank_lower_bound'],
                                                         r['two_integral_floor']) for r in results))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main('--out' in sys.argv[1:]))
    except Fail as e:
        sys.stdout.write('FAIL_KPORT_GROUP_SCALAR_ENDPOINT %s\n' % e)
        sys.exit(1)
