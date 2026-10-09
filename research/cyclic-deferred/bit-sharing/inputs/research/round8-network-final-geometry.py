"""Direct final-candidate bit geometry, using the pinned exact round-seven tools.
Stdlib only. Original-node inclusions use their checked nesting theorem;
new sigma/V and chronological data inclusions use exact rational annihilators.
This does not use old high-rank corner profiles: the opposite-bank compiler
instead supplies one child per rational idempotent's full rank.
"""
import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / 'round7-public/tree/independent/deferred-readout'
sys.path.insert(0, str(BASE))
import check_lifted as cl
import deferred as dr
from linalg import Echelon, Q31, null_exact, primitive, rank_mod

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=HERE/'round8-foundations-minimal-v-word.json.gz')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    def progress(message): print(round(time.monotonic()-started, 2), message, flush=True)
    W, D = dr.load(23)
    with gzip.open(args.candidate, 'rt') as f: candidate = json.load(f)
    sigma = dict(zip(D['readout_order'], D['sigma']))
    for s in candidate['removed_original_slots']: del sigma[s]
    sigma.update({int(s): B for s, B in candidate['new_frames'].items()})
    D['readout_order'] = [s for kind, s in candidate['events'] if kind == 'read' and s in sigma]
    assert len(D['readout_order']) == len(sigma) == len(set(D['readout_order']))
    D['sigma'] = [sigma[s] for s in D['readout_order']]
    vs = dict(zip(D['vleaf_slots'], D['vleaf_start']))
    vs.update({int(s): B for s, B in candidate.get('vstart_overrides', {}).items()})
    D['vleaf_start'] = [vs[s] for s in D['vleaf_slots']]
    if 'xs_order_actual' in candidate: D['xs_order'] = candidate['xs_order_actual']
    S = dr.Schedule(W, D)
    h = S.h
    full = [[int(i == j) for j in range(h)] for i in range(h)]
    pr = cl.Prog(W)
    bas, dn = cl.spans(pr)
    users = cl.users_of(pr, dn)
    linked = {use: donor for donor, use in pr.mL.items()}
    assert len(linked) == len(pr.mL) == len(W['links'])
    for n, (early, late_users) in pr.late.items():
        assert late_users and sorted(early+late_users) == [
            k for k in range(len(users[n])) if (n, k) not in linked]
    fr = cl.Frames(pr, dn, bas, users)
    assert fr.check_structure() == (0, 0, 0, True)
    fr.cobases()
    dims, _ = fr.dims()
    late, _ = cl.late_frames(fr, pr, users)
    assert S.node_dims == dims
    assert {('c', n, lt): r for (n, lt), r in S.late_dims.items()} == late
    progress('DAG, original nesting premises and exact frame dimensions pass')

    def usekey(n, k):
        u = users[n][k]
        return ('n', u[1]) if u[0] == 'gate' else cl.root_key(u)
    exact_cache = {}
    def exact(key):
        if key not in exact_cache:
            kind = key[0]
            if kind == '0': B = []
            elif kind == 'F': B = full
            elif kind == 'sigma': B = S.sigma[key[1]]
            elif kind == 'v': B = S.vstart[key[1]]
            elif kind == 'c':
                n, lt = key[1:]
                B = exact(usekey(n, lt[-1]))
                for k in reversed(lt[:-1]): B = fr.intersect_exact(exact(usekey(n, k)), B)
            else: B = fr.exact_basis(key)
            B = [primitive(row) for row in B]
            assert len(B) == S.dim(key)
            exact_cache[key] = B
        return exact_cache[key]
    annihilators = {}
    def inside(A, B):
        if not A or len(B) == h: return True
        kb = tuple(map(tuple, B))
        if kb not in annihilators: annihilators[kb] = null_exact(B, h)
        return all(sum(x*y for x, y in zip(a, z)) == 0
                   for a in A for z in annihilators[kb])
    methods = Counter()
    def included(a, b):
        if a == b or a == ('0',) or b == ('F',): method = 'identity/zero/full'
        elif a[0] == b[0] == 'n' and b[1] in fr.succ[a[1]]: method = 'checked node-successor theorem'
        elif a[0] == 'n' and b[0] in ('out', 'ret') and fr.rid[b] in fr.droots[a[1]]: method = 'checked direct-root theorem'
        elif a[0] == 'n' and b[0] == 'c' and a[1] == b[1]: method = 'node in every late successor'
        elif a[0] == b[0] == 'c' and a[1] == b[1] and set(b[2]) <= set(a[2]): method = 'nested exact intersections'
        elif a[0] == 'c' and b in [usekey(a[1], k) for k in a[2]]: method = 'exact intersection in member'
        else:
            method = 'exact rational annihilator'
            assert inside(exact(a), exact(b)), ('containment', a, b)
        assert S.dim(a) <= S.dim(b), ('dimension', a, b)
        methods[method] += 1

    steps = set()
    for s in range(S.R):
        chain = S.chain_keys(s)
        steps.update(zip(chain, chain[1:]))
    actual_v = defaultdict(list)
    for kind, s in candidate['events']:
        if kind == 'V': actual_v[S.srcop[s]].append(s)
    assert dict(S.xs) == dict(actual_v)
    assert sorted(s for slots in actual_v.values() for s in slots) == sorted(S.srcop)
    for n, slots in S.xs:
        chain = [('n', n)] + [('v', s) for s in slots] + [('F',)]
        steps.update(zip(chain, chain[1:]))
    CF = [{t: c for t, c in row.items() if c % 2} for row in S.adjoint()]
    by_target = defaultdict(list)
    for s in S.readout:
        for t in CF[s]: by_target[t].append(('sigma', s))
    for t, T in enumerate(S.trip):
        chain = [('0',)] + by_target[t] + [('out', T[0], T)]
        steps.update(zip(chain, chain[1:]))
    for a, b in sorted(steps, key=str): included(a, b)
    progress('All auxiliary and actual chronological X/Y chains pass')

    # The full-rank reduction below is a nonzero rational Gram determinant
    # witness; it is not a numerical substitute for zero containment tests.
    mq = cl.ModQ(fr, late)
    used = set(k for pair in steps for k in pair)
    used.update(('ret', c) for c in S.ret.values())
    for key in sorted(used, key=str):
        if key[0] in ('sigma', 'v'):
            B = exact(key)
            assert all(len(row) == h for row in B)
            E = Echelon(Q31)
            for row in B: E.insert(row)
            assert len(E.rows) == len(B), ('independence', key)
            mq.bcache[key] = E.rows
        assert mq.nondeg(key), ('degenerate', key)
    assert mq.dimfail == 0
    for s in S.readout:
        Trows = [[9*int(i in S.trip[t])-3 for i in range(h)] for t in CF[s]]
        assert all(sum(x*y for x, y in zip(row, cov)) == 0 for row in S.sigma[s] for cov in Trows)
    progress('All used frames nondegenerate; exact F2 target orthogonality passes')

    def nondeg(B):
        sums = [sum(row) for row in B]
        gram = [[9*sum(x*y for x, y in zip(a, b))-sa*sb
                 for b, sb in zip(B, sums)] for a, sa in zip(B, sums)]
        return rank_mod(gram, Q31) == len(B)
    controls = {'isotropic_frame_rejected': not nondeg([[1]*9+[0]*(h-9)])}
    for s in S.readout:
        B = exact(S.start_key(s))
        if len(B) == h: continue
        bad = next((row for row in full if not inside([row], B)), None)
        if bad is not None:
            controls['outside_start_rejected'] = not inside([bad], B)
            break
    controls['reversed_target_chain_rejected'] = any(
        len(exact(a)) < len(exact(b)) and not inside(exact(b), exact(a))
        for seq in by_target.values() for a, b in zip(seq, seq[1:]))
    assert all(controls.values()) and len(controls) == 3
    inputs = [args.candidate, BASE/'deferred.py', BASE/'check_lifted.py', BASE/'linalg.py']
    inputs += [BASE.parent.parent/'certificates/round7'/name
               for name in ['witness_23.json.gz', 'deferred_23.json.gz']]
    out = dict(status='PASS', candidate_sha256=hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
               node_frames=len(dims), late_frames=len(late), used_frames=len(used),
               distinct_chain_steps=len(steps), inclusion_methods=dict(methods),
               actual_F2_target_support=True, actual_V_chronology=True,
               all_frame_dimensions_exact=True, all_used_frames_nondegenerate=True,
               all_auxiliary_source_target_chains_nested=True,
               all_sigma_target_orthogonality_exact=True, controls=controls,
               elapsed=time.monotonic()-started,
               inputs_sha256={str(p.relative_to(HERE)) if p.is_relative_to(HERE) else str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
               scope='Rational bit geometry of final candidate, not full tape execution. Pair with literal frame ledger and general opposite-bank rank factorization; no old corner witness is needed.')
    args.output.write_text(json.dumps(out, indent=2)+'\n')
    progress('PASS; receipt written to '+str(args.output))

if __name__ == '__main__': main()
