"""Independent audit of the cross-copy hosted eleven-stage R715 bit template (8 pooled replicas) and of the cross-copy
hosted complex template; no code shared with the generators.
usage: audit_split11.py PARENT_BIT_DIR LOCAL_DIR BIT_DIR UPSTREAM442_CHANGED COMPLEX_DIR OUT.json"""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_split import audit_complex, check_pieces, wins
V, K, L, T, R, M = 120, 5, 11, 8, 715, 78
LOCAL = 2 * V + R; DATA = 2 * K * V * T
def digest(t):
    h = hashlib.sha256(); n = 0
    for call in t['calls']:
        for z in t['local_programs'][call['orientation']]:
            x = [z[0], call['owners'][z[1]]]
            if z[0] == 0: x.extend(z[2:])
            else: x.append(call['owners'][z[2]] if z[2] < LOCAL else [t['live'], ['private', 0]]); x.extend(z[3:])
            h.update(json.dumps(x, separators=(',', ':')).encode()); h.update(b'\n'); n += 1
    return h.hexdigest(), n
def prefix_bits(t):
    live = t['live']; norm = [1] * live + [0]; prefix = 1; callmap = {(c['stage'], c['replica']): c for c in t['calls']}
    fams = lambda o: [o[0]] + ([o[1][4]] if o[1][0] == 'hosted-split' else [])
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep':
            for rep in range(T):
                call = callmap[e['stage'], rep]; own = call['owners']
                for z in t['local_programs'][call['orientation']]:
                    if z[0] == 0: continue
                    xs = fams(own[z[1]]); ys = fams(own[z[2]]) if z[2] < LOCAL else [live]
                    if z[0] == 1:
                        inc = abs(z[3]) * max(norm[y] for y in ys)
                        for x in xs: norm[x] += inc; prefix = max(prefix, norm[x])
                    elif z[0] == 2: norm[live] = max(norm[x] for x in xs); prefix = max(prefix, norm[live])
                    else: norm[live] = 0
        elif e['kind'] == 'bridge':
            d, ss = e['dst'], e['src']
            for rep in range(T):
                for port in range(V):
                    for x, y in [(rep * 1200 + 2 * d * V + port, rep * 1200 + 2 * ss * V + port), (rep * 1200 + (2 * ss + 1) * V + port, rep * 1200 + (2 * d + 1) * V + port)]:
                        norm[x] += norm[y]; prefix = max(prefix, norm[x])
    assert norm[live] == 0
    return prefix.bit_length()
def audit_bit(t, parent_t, widths):
    mutable = {'version', 'live', 'hosting', 'helper_route', 'calls', 'schedule'}
    assert set(t) == set(parent_t)
    assert {k: v for k, v in t.items() if k not in mutable} == {k: v for k, v in parent_t.items() if k not in mutable}
    assert t['replicas'] == T and t['m'] == M and t['stages'] == L and t['live'] == DATA and len(t['calls']) == L * T
    assert t['schedule'] == parent_t['schedule']
    ev = []; rank = {}; pair = {}
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': ev.append(('local', e['stage'], e['pair']))
        elif e['kind'] == 'bridge': ev.append(('bridge', e['dst'], e['src']))
        elif e['kind'] == 'idle': ev.append(('idle', e['idx'], e['pair'])); rank[e['idx']] = e['rank']; pair[e['idx']] = e['pair']
    W = wins(ev); hs = t['hosting']; copies = 2 * V * T
    assert hs['windows'] == {str(i): [pair[i], rank[i], sorted(W[i])] for i in W if rank[i] > 0 and W[i]}
    wid = [widths[h % R] for h in range(R * T)]
    used, hosted = check_pieces(hs, W, rank, wid, copies)
    assert set(hosted) == {(s, h) for s in range(L) for h in range(R * T)}
    rem = {}
    for i in rank:
        if rank[i] == 0: continue
        for cp in range(copies): rem[i, cp] = rank[i] - len(used[i, cp])
        rr = Counter(rem[i, cp] for cp in range(copies))
        if str(i) in hs['remainders']: assert {int(k): v for k, v in hs['remainders'][str(i)].items()} == dict(rr)
        else: assert rr == Counter({rank[i]: copies})
    assert {(c['stage'], c['replica']) for c in t['calls']} == {(s, r) for s in range(L) for r in range(T)}
    fam = lambda i, cp: (cp // (2 * V)) * (2 * K * V) + (2 * pair[i] + (cp % (2 * V)) // V) * V + cp % V
    for c, pc in zip(t['calls'], parent_t['calls']):
        assert {k: v for k, v in c.items() if k != 'owners'} == {k: v for k, v in pc.items() if k != 'owners'}
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners']; assert len(own) == LOCAL and own[:2 * V] == pc['owners'][:2 * V]
        for r, (f, rt) in enumerate(own[2 * V:]):
            i, segs = hosted[s, rep * R + r]; assert pair[i] != p and 0 <= f < DATA
            if len(segs) == 1:
                cp, off, w = segs[0]; assert rt == ['hosted', i, off, w] and f == fam(i, cp)
            else:
                (c1, o1, w1), (c2, o2, w2) = segs; assert c1 != c2
                assert rt == ['hosted-split', i, o1, w1, fam(i, c2), o2, w2] and f == fam(i, c1)
        assert len({(f, tuple(rt)) for f, rt in own}) == LOCAL
    paid = Counter()
    for c in t['calls']:
        for z in t['local_programs'][c['orientation']]:
            if z[0] == 0 and z[4]: paid[z[4]] += 1
            if z[0] == 2: paid[z[5]] += 1
    for (i, cp), r_ in rem.items():
        if r_: paid[r_] += 1
    mass = sum(r * n for r, n in paid.items()); assert M * DATA - mass == (2 * K * V - L * 72) * T
    assert M ** 3 > 2 * max(paid) ** 3
    return paid, len(hosted), sum(1 for _, segs in hosted.values() if len(segs) == 2)
def main():
    par, local, bd, chg, cd, outp = map(Path, sys.argv[1:7])
    tpl = lambda p: json.loads(gzip.decompress(Path(p).read_bytes()))
    pbt = tpl(par / 'GLOBAL-TEMPLATE.json.gz'); pg = json.loads((par / 'GLOBAL.json').read_text())
    bt = tpl(bd / 'GLOBAL-TEMPLATE.json.gz'); bg = json.loads((bd / 'GLOBAL.json').read_text())
    th = hashlib.sha256(gzip.decompress((bd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
    assert th == bg['template_sha256'] and bg['parent_template_sha256'] == pg['template_sha256']
    st = json.loads((local / 'records/249-states.json').read_text()); fs = json.loads((local / 'records/frames.json').read_text())['frames']
    widths = [8 - fs[str(st['initial'][str(h)])]['dim'] for h in range(2 * V, LOCAL)]
    bp, bh, bs = audit_bit(bt, pbt, widths); assert bp == Counter({int(k): v for k, v in bg['profile'].items()})
    assert bg['hosted_residuals'] == bh and bg['live'] == bt['live'] and bg['split_residuals'] == bs
    dg, n = digest(bt); assert dg == bg['emitted_program_sha256'] and n == bg['emitted_events'] == pg['emitted_events'] and dg != pg['emitted_program_sha256']
    pb = prefix_bits(bt); assert pb == bg['global_prefix_bits']
    pct = tpl(chg / 'split-centres/GLOBAL-TEMPLATE.json.gz'); ct = tpl(cd / 'GLOBAL-TEMPLATE.json.gz'); ch = json.loads((cd / 'HOSTED.json').read_text())
    assert hashlib.sha256(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == ch['template_sha256']
    lc = json.loads((chg / 'split-centres/LOCAL-CHECKS.json').read_text())
    cp, chh, cs = audit_complex(ct, pct, lc); assert cp == Counter({int(k): v for k, v in ch['global_profile'].items()})
    controls = []
    def reject(name, fn, which):
        q = copy.deepcopy(bt if which == 'bit' else ct); fn(q)
        try: (audit_bit(q, pbt, widths) if which == 'bit' else audit_complex(q, pct, lc))
        except (AssertionError, KeyError, IndexError, StopIteration, ValueError, TypeError): controls.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    def first_split(q): return next(pc for pc in q['hosting']['pieces'] if len(pc[3]) == 2)
    def outside(q):
        pc = q['hosting']['pieces'][0]; pc[0] = next(s for s in range(L) if s not in q['hosting']['windows'][str(pc[2])][2])
    reject('bit: hosted residual outside its window', outside, 'bit')
    reject('bit: split piece widths do not sum to the residual width', lambda q: first_split(q)[3][1].__setitem__(2, first_split(q)[3][1][2] + 1), 'bit')
    reject('bit: split pieces on two different children', lambda q: first_split(q).__setitem__(2, (first_split(q)[2] + 1) % len(q['hosting']['windows'])), 'bit')
    reject('bit: overlapping hosted coordinates', lambda q: q['hosting']['pieces'][1][3][0].__setitem__(0, q['hosting']['pieces'][0][3][0][0]) or q['hosting']['pieces'][1][3][0].__setitem__(1, q['hosting']['pieces'][0][3][0][1]), 'bit')
    reject('bit: overstated live stock', lambda q: q.__setitem__('live', q['live'] + 1), 'bit')
    reject('bit: hosted owner on the active pair', lambda q: q['calls'][0]['owners'].__setitem__(240, [q['calls'][0]['pair'] * V * 2, ['hosted', 0, 0, 8]]), 'bit')
    reject('bit: missing hosted residual', lambda q: q['hosting']['pieces'].pop(), 'bit')
    reject('bit: changed idle rank', lambda q: next(e for e in q['schedule'] if e['kind'] == 'idle').__setitem__('rank', 1), 'bit')
    reject('bit: wrong owner family', lambda q: q['calls'][0]['owners'].__setitem__(241, [q['calls'][0]['owners'][241][0] + 1, q['calls'][0]['owners'][241][1]]), 'bit')
    reject('bit: changed local program', lambda q: q['local_programs']['forward'].pop(), 'bit')
    reject('complex: hosted residual outside its window', outside, 'complex')
    reject('complex: split piece widths do not sum to nine', lambda q: first_split(q)[3][0].__setitem__(2, first_split(q)[3][0][2] + 1), 'complex')
    reject('complex: remainder child understated', lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] - 1), 'complex')
    reject('complex: dropped bank', lambda q: q.__setitem__('live', q['live'] - 1), 'complex')
    reject('complex: duplicated hosted residual', lambda q: q['hosting']['pieces'].append(list(q['hosting']['pieces'][0])), 'complex')
    res = dict(status='PASS_INDEPENDENT_CROSS_COPY_ELEVEN_STAGE_AUDIT', template_sha256=th, emitted_program_sha256=dg, emitted_events=n,
               profile={str(k): v for k, v in sorted(bp.items())}, live=bt['live'], physical=bt['live'] + 9, hosted_residuals=bh, split_residuals=bs,
               physical_prefix_bits=pb, rank_mass=sum(r * z for r, z in bp.items()), deficit=(2 * K * V - L * 72) * T, maxchild=max(bp),
               complex_template_sha256=ch['template_sha256'], complex_profile={str(k): v for k, v in sorted(cp.items())}, complex_live=ct['live'],
               complex_hosted_residuals=chh, complex_split_residuals=cs, complex_maxchild=max(cp), mutations_rejected=controls)
    outp.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: v for k, v in res.items() if 'profile' not in k}))
if __name__ == '__main__': main()
