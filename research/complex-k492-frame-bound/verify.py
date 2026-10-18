#!/usr/bin/env python3
"""Verify the fixed-order A/B frame exclusion for the PR626 jp8 and ck complex providers.

Standard library only; no optimizer. Prepared with substantial AI assistance (Anthropic Claude). Apache-2.0.

usage: python3 -B verify.py [--work K492_REPLAY_DIR] [--control NAME]
Without --work the committed copies in data/ are used; with --work the freshly
replayed jp8-local/ck-local outputs of research/complex-k492-owner-repair/verify.sh
are used. Either way the decompressed payloads must match the pinned hashes.
"""
import argparse, copy, gzip, hashlib, itertools, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import model as Mo
import engine as E

if not __debug__: raise SystemExit('assertions are the proof checks: run without -O')
PINS = json.loads((HERE / 'SOURCES.json').read_text())
GAUSS = {0: 1, 1: 2, 2: 5, 3: 16}     # number of subspaces of F_2^g
CONTROLS = ('drop_component', 'inflate_dual', 'alter_domain', 'accepted_endpoint', 'suboptimal_baseline', 'wrong_word')


def dec(x, direction, digits=40):
    """outward-rounded decimal string (direction -1: floor, +1: ceil)"""
    s = 10 ** digits; n = (x.numerator * s) // x.denominator
    if direction > 0 and Q(n, s) < x: n += 1
    return '%s%d.%0*d' % ('-' if n < 0 else '', abs(n) // s, digits, abs(n) % s)


def sha(b): return hashlib.sha256(b).hexdigest()


def check_component(comp, dual, baseline_frames, engines):
    cols, rhs = comp['cols'], comp['rhs']
    assert len(dual) == len(rhs) and all(len(r) == 8 for r in dual), 'dual shape'
    q = [tuple(Q(x) for x in r) for r in dual]
    forms = set()
    for name, cost, entries in cols:
        v = list(cost)
        for r, a in entries:
            for k in range(8): v[k] -= a * q[r][k]
        forms.add(tuple(v))
    for v in forms: assert E.nonnegative(v, engines), ('negative reduced cost', v)
    obj = tuple(sum((rhs[i] * q[i][k] for i in range(len(rhs))), Q(0)) for k in range(8))
    # literal baseline point: x(i, baseline) = 1 and y(e, baseline pair) = 1
    base = Mo.ZERO
    for name, cost, entries in cols:
        if name[0] == 'x' and baseline_frames[name[1]] == name[2]: base = Mo.add(base, cost)
        if name[0] == 'y' and (baseline_frames[name[1][0]], baseline_frames[name[1][1]]) == name[2]: base = Mo.add(base, cost)
    assert obj == tuple(Q(x) for x in base), ('dual objective differs from the literal baseline', obj, base)
    return len(forms), base


def worse_block(c, F, nodes, free):
    """a legal, strictly different-profile assignment: move one same-frame block of free macros to span(in)/meet(out)"""
    seq = Mo.chains(c, nodes); pos = {(i, r): k for r, ch in enumerate(seq) for k, i in enumerate(ch)}
    H0 = Mo.profile(c, F, nodes, [nd[2] for nd in nodes])
    for i0 in sorted(free):
        f = nodes[i0][2]; B = {i0}; st = [i0]
        while st:
            j = st.pop()
            for r in nodes[j][0]:
                k = pos[(j, r)]
                for q in (k - 1, k + 1):
                    if 0 <= q < len(seq[r]) and seq[r][q] not in B and nodes[seq[r][q]][2] == f: B.add(seq[r][q]); st.append(seq[r][q])
        if not B <= free: continue
        ins = []; outs = []
        for j in B:
            for r in nodes[j][0]:
                k = pos[(j, r)]
                if k == 0 or seq[r][k - 1] not in B: ins.append(nodes[seq[r][k - 1]][2] if k else F[c['start'][r]])
                if k + 1 == len(seq[r]) or seq[r][k + 1] not in B: outs.append(nodes[seq[r][k + 1]][2] if k + 1 < len(seq[r]) else F[c['final'][r]])
        L = Mo.basis([x for g in ins for x in g]); U = outs[0]
        for g in outs[1:]: U = Mo.meet(U, g)
        for G in (L, U):
            if G == f: continue
            trial = [nd[2] for nd in nodes]
            for j in B: trial[j] = G
            if Mo.profile(c, F, nodes, trial) != H0: return {j: G for j in B}
    raise AssertionError('no alternative block found')


def brute(c, F, nodes, comp, engines, limit=4096):
    """independent exhaustive check of small components: all legal assignments, exact symbolic cost difference"""
    vs = comp['nodes']; doms = [comp['domains'][i] for i in vs]
    total = 1
    for d in doms: total *= len(d)
    if total > limit: return None
    seq = Mo.chains(c, nodes); S = set(vs); count = 0
    regs = sorted({r for i in vs for r in nodes[i][0]})
    def cost(assign):
        v = Mo.ZERO
        for r in regs:
            ch = seq[r]; prev = F[c['start'][r]]
            for i in ch + [None]:
                G = F[c['final'][r]] if i is None else assign.get(i, nodes[i][2])
                if not Mo.contains(G, prev): return None
                v = Mo.add(v, Mo.vec(len(G) - len(prev))); prev = G
        return v
    b = cost({i: nodes[i][2] for i in vs})
    for choice in itertools.product(*doms):
        v = cost(dict(zip(vs, choice)))
        if v is None: continue
        count += 1
        diff = tuple(x - y for x, y in zip(v, b))
        assert E.nonnegative(diff, engines), ('brute force found a cheaper legal assignment', vs, choice)
    return count


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path); ap.add_argument('--controls', action='store_true')
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    if a.controls:
        rejected = []
        for ctl in CONTROLS:
            try: run(a.work, ctl, None)
            except AssertionError as e:
                rejected.append(ctl); print('REJECTED control', ctl, '-', str(e)[:120], flush=True)
            else: raise SystemExit('control accepted: ' + ctl)
        print('PASS_CONTROLS', len(rejected), 'of', len(CONTROLS), 'rejected'); return
    run(a.work, None, a.out)


def run(work, ctl, out):
    class a: pass
    a.work = work
    assert sha(E.REPO_ENGINE.read_bytes()) == E.REPO_ENGINE_SHA256, 'repository moment engine pin'
    endpoint = E.B_ACCEPTED if ctl == 'accepted_endpoint' else E.B_NEXT
    engA = E.engine_a(endpoint); engB = E.engine_b(endpoint); engines = (engA, engB)
    duals = json.loads(gzip.decompress((HERE / 'data/DUALS.json.gz').read_bytes()))
    assert sha(gzip.decompress((HERE / 'data/DUALS.json.gz').read_bytes())) == PINS['duals_payload_sha256']
    report = {'programs': {}}
    local = {}
    for word in ('jp8', 'ck'):
        d = (a.work / (word + '-local')) if a.work else HERE / 'data' / word
        if ctl == 'wrong_word' and word == 'jp8': d = (a.work / 'ck-local') if a.work else HERE / 'data/ck'
        rec = json.loads((HERE.parents[1] / PINS['inputs'][word]['pr626_receipt']['path']).read_text())
        assert rec['canonical_word_sha256'] == PINS['inputs'][word]['CANONICAL-WORD']['gzip_sha256']
        assert rec['local_programs_sha256'] == PINS['inputs'][word]['LOCAL-PROGRAMS']['gzip_sha256']
        for f in ('CANONICAL-WORD', 'LOCAL-PROGRAMS'):
            got = Mo.payload_sha(d / (f + '.json.gz'))
            assert got == PINS['inputs'][word][f]['payload_sha256'], ('input payload pin', word, f)
        for prog in ('forward', 'backward'):
            key = '%s/%s' % (word, prog)
            c, ev = Mo.load(d, prog)
            F, nodes, climbs, center = Mo.extract(c, ev)
            Hc = Counter(center)
            for r, l in climbs.items(): Hc.update(l)
            assert dict(Hc) == {int(k): z for k, z in c['local_profile'].items()}, 'emitted climbs + centre steps = local profile'
            lo, hi = Mo.intervals(c, F, nodes)
            assert Mo.profile(c, F, nodes, [nd[2] for nd in nodes]) + Counter(center) == Hc
            comps, const, base, free = Mo.lp(c, F, nodes, lo, hi)
            if ctl == 'alter_domain':
                comp = next(x for x in comps if any(len(v) > 2 for v in x['domains'].values()))
                i = next(i for i, v in comp['domains'].items() if len(v) > 2)
                G = next(g for g in comp['domains'][i] if g != nodes[i][2])
                comp['domains'][i].remove(G)
                drop = {j for j, col in enumerate(comp['cols']) if (col[0][0] == 'x' and col[0][1:] == (i, G)) or (col[0][0] == 'y' and ((col[0][1][0] == i and col[0][2][0] == G) or (col[0][1][1] == i and col[0][2][1] == G)))}
                comp['cols'] = [col for j, col in enumerate(comp['cols']) if j not in drop]
                assert len(comp['domains'][i]) < GAUSS[len(hi[i]) - len(lo[i])]
            for comp in comps:          # completeness: every subspace of every interval is a choice
                for i in comp['nodes']:
                    g = len(hi[i]) - len(lo[i]); dom = comp['domains'][i]
                    assert len(set(dom)) == len(dom) == GAUSS[g], ('incomplete domain', i)
                    assert all(Mo.contains(G, lo[i]) and Mo.contains(hi[i], G) for G in dom)
            cert = duals[key]
            if ctl == 'drop_component': cert = cert[:-1]
            if ctl == 'inflate_dual':
                cert = copy.deepcopy(cert); k0 = max(range(len(cert)), key=lambda j: len(cert[j]))
                cert[k0][0][0] = str(Q(cert[k0][0][0]) + 1)
            assert len(cert) == len(comps), 'one certificate per component'
            bf = {i: nodes[i][2] for i in free}
            if ctl == 'suboptimal_baseline':
                bf.update(worse_block(c, F, nodes, free))
            forms = 0; total = const; brute_assignments = 0; brute_components = 0
            for comp, dual in zip(comps, cert):
                nf, cb = check_component(comp, dual, bf, engines); forms += nf; total = Mo.add(total, cb)
                bc = brute(c, F, nodes, comp, engines) if ctl is None else None
                if bc is not None: brute_assignments += bc; brute_components += 1
            assert total == base, 'components and constants recompose the literal baseline'
            mass = sum(len(F[c['final'][r]]) - len(F[c['start'][r]]) for r in range(2 * c['v'] + c['R']))
            report['programs'][key] = {'macros': len(nodes), 'free_macros_with_choices': len(free),
                'domain_frames': sum(len(x['domains'][i]) for x in comps for i in x['nodes']),
                'components': len(comps), 'lp_rows': sum(len(x['rhs']) for x in comps), 'lp_columns': sum(len(x['cols']) for x in comps),
                'distinct_reduced_cost_forms': forms, 'brute_forced_components': brute_components,
                'brute_forced_legal_assignments': brute_assignments, 'register_rank_mass': mass,
                'local_profile': {str(k): v for k, v in sorted(Hc.items())}}
            local[key] = Hc
            print('PASS', key, json.dumps(report['programs'][key]), flush=True)
    # global consequence at the endpoint
    assembly = HERE.parents[1] / PINS['assembly']['path']
    assert sha(assembly.read_bytes()) == PINS['assembly']['sha256']
    A = json.loads(assembly.read_text()); Hg = {int(k): v for k, v in A['complex_profile'].items()}
    assert Q(A['complex_lower']) == E.B_ACCEPTED and A['binding'] == 'complex'
    calls = A['provider_counts']; assert calls == {'ck': 8, 'jp8': 64}
    for prog in ('forward', 'backward'):
        rem = {k: Hg.get(k, 0) - 64 * local['jp8/' + prog].get(k, 0) - 8 * local['ck/' + prog].get(k, 0) for k in set(Hg) | set(local['jp8/' + prog]) | set(local['ck/' + prog])}
        assert all(v >= 0 for v in rem.values()), 'local profiles are contained in the global profile'
    la, ua = E.moment_a(Hg, endpoint); R = E._repo(); lb, ub = R.moment(Hg, E.M_DIM, E.W_LIVE, endpoint)
    assert la > 1 and lb > 1, 'baseline global moment must exceed one at the excluded endpoint'
    la0, ua0 = E.moment_a(Hg, E.B_ACCEPTED); lb0, ub0 = R.moment(Hg, E.M_DIM, E.W_LIVE, E.B_ACCEPTED)
    assert ua0 < 1 and ub0 < 1
    report.update(status='PASS_FIXED_ORDER_AB_FRAME_EXCLUSION_PR626', excluded_complex_endpoint=str(endpoint),
                  accepted_complex_endpoint=str(E.B_ACCEPTED), global_moment_minus_one_at_excluded={'engine_a': [dec(la - 1, -1), dec(ua - 1, 1)], 'repo_engine': [dec(lb - 1, -1), dec(ub - 1, 1)]},
                  scope='Every simultaneous reassignment of A/B scalar-macro frames of the emitted PR626 jp8 and ck provider programs, '
                        'with macro list/order/operands, starts, finals, target levels, centre chains and all non-A/B macro frames fixed. '
                        'No scalar rewrite, reordering, width/owner/hosting change, other supplier or outer theorem is covered.')
    if out: out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'], 'excluded b =', endpoint, flush=True)


if __name__ == '__main__':
    main()
