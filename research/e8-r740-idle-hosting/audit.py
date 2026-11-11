"""Independent audit of the two idle-axis-hosted templates (no code shared with the generators).
Re-derives hosting windows from each template's own schedule and checks, for every replica and invocation:
  * every helper residual has exactly one owner: a bank slot or a hosted slot;
  * a hosted slot lies on the data family of the idle child it names, inside that child's pending coordinates,
    disjoint from every other hosted slot of the family, and its invocation lies strictly between the last
    local invocation or bridge naming that pair and the child (the window);
  * the child keeps exactly the remaining coordinates; banks are tiled exactly (bit) or padded (complex);
  * the emitted paid profile, live stock and rank deficit 2496 are recomputed from scratch.
Mutation controls must be rejected.  usage: audit.py PARENT_CHANGED_DIR BIT_DIR COMPLEX_DIR OUT.json"""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
V, K, T, L = 120, 4, 8, 9
DATA = 2 * K * V * T

def wins(events):
    """events: ('local', stage, pair) | ('bridge', a, b) | ('idle', idx, pair); window = local stages after the last
    local/bridge touch of the pair and before the child"""
    last = {}; seen = []; w = {}
    for pos, e in enumerate(events):
        if e[0] == 'local': seen.append((pos, e[1], e[2])); last[e[2]] = pos
        elif e[0] == 'bridge': last[e[1]] = pos; last[e[2]] = pos
        else:
            lo = last.get(e[2], -1); w[e[1]] = {s for q, s, p in seen if lo < q < pos and p != e[2]}
    return w

def audit_bit(t, parent_t, widths):
    assert t['local_programs'] == parent_t['local_programs'] and len(t['calls']) == 72
    ev = []; rank = {}; pair = {}
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': ev.append(('local', e['stage'], e['pair']))
        elif e['kind'] == 'bridge': ev.append(('bridge', e['dst'], e['src']))
        elif e['kind'] == 'idle':
            ev.append(('idle', e['idx'], e['pair'])); rank[e['idx']] = e['rank']; pair[e['idx']] = e['pair']
    W = wins(ev); hs = t['hosting']
    used = defaultdict(set); hosted = {}
    for i, cp, off, w, s, h in hs['slots']:
        assert s in W[i], ('window', i, s)
        assert w == widths[h] and 0 <= off and off + w <= rank[i]
        cells = set(range(off, off + w)); assert not cells & used[i, cp], ('overlap', i, cp); used[i, cp] |= cells
        assert (s, h) not in hosted; hosted[s, h] = (i, cp, off, w)
    rem = {}
    for i in rank:
        if rank[i] == 0: continue
        for cp in range(2 * V): rem[i, cp] = rank[i] - len(used[i, cp])
        rr = Counter(rem[i, cp] for cp in range(2 * V))
        if str(i) in hs['remainders']: assert {int(k): v for k, v in hs['remainders'][str(i)].items()} == dict(rr)
        else: assert rr == Counter({rank[i]: 2 * V})
    occ = defaultdict(set); LIVE = t['live']; bank_lo = {}
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners']; assert len(own) == 2 * V + len(widths)
        assert own[:2 * V] == next(q for q in parent_t['calls'] if (q['stage'], q['replica']) == (s, rep))['owners'][:2 * V]
        for h, (f, r) in enumerate(own[2 * V:]):
            if (s, h) in hosted:
                i, cp, off, w = hosted[s, h]; side, port = divmod(cp, V)
                assert r == ['hosted', i, off, w] and f == rep * 960 + (2 * pair[i] + side) * V + port
                assert pair[i] != p
                occ['h', f, i, s, rep, h] = True
            else:
                assert r[0] == 'bank' and r[2] == widths[h] and DATA <= f < LIVE
                cells = set(range(r[1], r[1] + r[2])); assert cells <= set(range(64)) and not cells & occ[f]; occ[f] |= cells
                bank_lo[f] = s
    banks = [f for f in occ if isinstance(f, int)]
    assert sorted(banks) == list(range(DATA, LIVE)) and all(occ[f] == set(range(64)) for f in banks)
    paid = Counter()
    for c in t['calls']:
        for z in t['local_programs'][c['orientation']]:
            if z[0] == 0 and z[4]: paid[z[4]] += 1
            if z[0] == 2: paid[z[5]] += 1
    for (i, cp), r_ in rem.items():
        if r_: paid[r_] += T
    mass = sum(r * n for r, n in paid.items()); assert 64 * LIVE - mass == 2496
    assert 64 * 64 > 2 * max(paid) ** 2
    return paid, sum(1 for _ in hosted) * T

def audit_complex(t, parent_t, local_checks):
    R = 560; m = 73
    assert t['local_programs'] == parent_t['local_programs'] and len(t['calls']) == 72
    prank = {}
    for it in parent_t['idle_children']: prank.setdefault(it['child'], it['rank'])
    stage_pair = {e['stage']: e['pair'] for e in t['recipe'] if e['kind'] == 'local'}
    ev = []; side = {}; pairs = {}
    for e in t['execution_schedule']:
        if e['kind'] == 'local_cover_sweep': ev.append(('local', e['stage'], stage_pair[e['stage']]))
        elif e['kind'] == 'bridge': ev.append(('bridge', e['dst'], e['src']))
        elif e['kind'] == 'idle_cover_sweep':
            for sd, ch in enumerate(e['child_indices']):
                if ch in prank: ev.append(('idle', ch, e['pair'])); side[ch] = sd; pairs[ch] = e['pair']
    W = wins(ev); hs = t['hosting']
    used = defaultdict(set); hosted = {}
    for i, port, off, w, s, h in hs['slots']:
        assert w == 9 and s in W[i] and 0 <= off and off + 9 <= prank[i]
        cells = set(range(off, off + 9)); assert not cells & used[i, port]; used[i, port] |= cells
        assert (s, h) not in hosted; hosted[s, h] = (i, port, off)
    rem = {}
    for it in parent_t['idle_children']: rem[it['child'], it['port']] = it['rank'] - len(used[it['child'], it['port']])
    got = {(it['child'], it['port']): it['rank'] for it in t['idle_children']}
    assert got == {k: r for k, r in rem.items() if r} and all(it['replicas'] == T for it in t['idle_children'])
    LIVE = t['live']; occ = defaultdict(set)
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners']; assert len(own) == 2 * V + R
        assert own[:2 * V] == next(q for q in parent_t['calls'] if (q['stage'], q['replica']) == (s, rep))['owners'][:2 * V]
        for h, (f, r) in enumerate(own[2 * V:]):
            if (s, h) in hosted:
                i, port, off = hosted[s, h]
                assert r == [3, i, off] and f == rep * 960 + (2 * pairs[i] + side[i]) * V + port and pairs[i] != p
            else:
                assert r[0] == 2 and 0 <= r[1] < 8 and DATA <= f < LIVE and r[1] not in occ[f]; occ[f].add(r[1])
    banks = sorted(occ); assert banks == list(range(DATA, LIVE))
    paid = Counter()
    for c in t['calls']:
        for r_, z in local_checks[c['orientation']]['paid_profile'].items(): paid[int(r_)] += z
    for (ch, port), r_ in rem.items():
        if r_: paid[r_] += T
    for f in banks: paid[m - 9 * len(occ[f])] += 1
    mass = sum(r * n for r, n in paid.items()); assert m * LIVE - mass == 2496
    assert m * m > 2 * max(paid) ** 2
    return paid, len(hosted) * T

def main():
    par, bd, cd, outp = map(Path, sys.argv[1:5])
    pbt = json.loads(gzip.decompress((par / 'bit426-source-centres/global/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    bt = json.loads(gzip.decompress((bd / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    bg = json.loads((bd / 'GLOBAL.json').read_text())
    assert hashlib.sha256(gzip.decompress((bd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == bg['template_sha256']
    st = json.loads((par / 'bit426-source-centres/records/249-states.json').read_text())
    fs = json.loads((par / 'bit426-source-centres/records/frames.json').read_text())['frames']
    widths = [8 - fs[str(st['initial'][str(i)])]['dim'] for i in range(240, st['n'])]
    pct = json.loads(gzip.decompress((par / 'split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    ct = json.loads(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
    ch = json.loads((cd / 'HOSTED.json').read_text())
    assert hashlib.sha256(gzip.decompress((cd / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() == ch['template_sha256']
    lc = json.loads((par / 'split-centres/LOCAL-CHECKS.json').read_text())
    bp, bh = audit_bit(bt, pbt, widths); assert bp == Counter({int(k): v for k, v in bg['profile'].items()})
    cp, chh = audit_complex(ct, pct, lc); assert cp == Counter({int(k): v for k, v in ch['global_profile'].items()})
    controls = []
    def reject(name, fn, which):
        q = copy.deepcopy(bt if which == 'bit' else ct); fn(q)
        try:
            (audit_bit(q, pbt, widths) if which == 'bit' else audit_complex(q, pct, lc))
        except (AssertionError, KeyError, IndexError, StopIteration): controls.append(name)
        else: raise AssertionError('mutation accepted: ' + name)
    def outside(q):           # move one hosted residual to a stage outside its window
        sl = q['hosting']['slots'][0]; i = sl[0]; s_bad = next(s for s in range(9) if s not in q['hosting']['windows'][str(i)][2]); sl[4] = s_bad
    reject('bit: hosted residual outside its window', outside, 'bit')
    reject('bit: overlapping hosted coordinates', lambda q: q['hosting']['slots'][1].__setitem__(2, q['hosting']['slots'][0][2]) if q['hosting']['slots'][1][:2] == q['hosting']['slots'][0][:2] else q['hosting']['slots'][1].__setitem__(1, q['hosting']['slots'][0][1]) or q['hosting']['slots'][1].__setitem__(2, q['hosting']['slots'][0][2]), 'bit')
    reject('bit: understated live stock', lambda q: q.__setitem__('live', q['live'] - 1), 'bit')
    reject('bit: hosted owner on the active pair', lambda q: q['calls'][0]['owners'].__setitem__(240 + next(h for h in range(len(widths)) if q['calls'][0]['owners'][240 + h][1][0] == 'hosted'), [0, ['hosted', 0, 0, 8]]), 'bit')
    reject('bit: missing remainder child', lambda q: q['hosting']['slots'].pop(), 'bit')
    reject('complex: hosted residual outside its window', lambda q: q['hosting']['slots'][0].__setitem__(4, next(s for s in range(9) if s not in q['hosting']['windows'][str(q['hosting']['slots'][0][0])][2])), 'complex')
    reject('complex: remainder child understated', lambda q: q['idle_children'][0].__setitem__('rank', q['idle_children'][0]['rank'] - 1), 'complex')
    reject('complex: dropped bank', lambda q: q.__setitem__('live', q['live'] - 1), 'complex')
    reject('complex: duplicated hosted residual', lambda q: q['hosting']['slots'].append(list(q['hosting']['slots'][0])), 'complex')
    res = dict(status='PASS_INDEPENDENT_IDLE_AXIS_HOSTING_AUDIT', bit_template_sha256=bg['template_sha256'], complex_template_sha256=ch['template_sha256'],
               bit_profile={str(k): v for k, v in sorted(bp.items())}, complex_profile={str(k): v for k, v in sorted(cp.items())},
               bit_live=bt['live'], complex_live=ct['live'], bit_hosted_residuals=bh, complex_hosted_residuals=chh,
               bit_maxchild=max(bp), complex_maxchild=max(cp), mutations_rejected=controls)
    outp.write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: v for k, v in res.items() if 'profile' not in k}))
if __name__ == '__main__': main()
