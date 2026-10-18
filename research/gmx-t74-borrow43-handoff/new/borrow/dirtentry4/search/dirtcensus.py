"""Census of dirt-entry (PR2833) candidates on a BORROW-WORD.

Mechanism (as read from PR2833's dirtentry_43*.json): helper k is zero-start (no start_extra), its first event is
    B[p] = add k += c*r  at frame F1.
Insert  r -= (1/c)*k  just before p (so k holds exactly c*x_r afterwards: it is clean from then on); its dirt now lives in r.
Remove every compensation gate reading k (entering helpers may not be compensated) and cancel k's remaining target response
with injections  t += a*k  at B entry, at a 1-dim entrance frame [u] (u in F1); start_extra[k] = [u]; width 9 -> 8.
Then the independent auditor (PR2833's own audit_local.run_borrow) must pass: exact frame chain, profile, free-algebra replay.

usage: dirtcensus.py WORD.json.gz AUDIT_DIR [--only k,k] [--out out.json]
"""
import sys, json, gzip, copy, io, contextlib, tempfile, re, itertools
from pathlib import Path
from fractions import Fraction as F

word_path = Path(sys.argv[1]); adir = Path(sys.argv[2])
sys.path.insert(0, str(adir))
import audit_local as AL, word_patch as WP

W = json.loads(gzip.decompress(word_path.read_bytes()))
v = 112; R = W['report']['R']; n = 2 * v + R
removed = set(W['removed']); live = [r for r in range(n) if r not in removed]
entering = set(map(int, W['start_extra'])); restored = set(map(int, W['helper_final']))
lenders = {rec[1] for rec in W['warps']}
corrsrc = {c['source'] for c in W['initial_corrections']}
pretouch = {r for e in W['precondition'] for r in AL.registers(e)}
centers = set(W['centers'])
npre = W['prelude_events']


def regs(e):
    return AL.registers(e) if e[0] in ('add', 'scale') else (e[1],)


def first_events(w):
    out = {}
    for sec in ('A', 'B'):
        for i, e in enumerate(w[sec]):
            if e[0] == 'warp': continue
            for q in regs(e):
                out.setdefault(q, (sec, i, e))
    return out


def target_dirt(w, k):
    """forward free-algebra replay (auditor's program order); return {target: {opword: coeff}} of variable k"""
    rows = {r: {(r, ()): F(1)} for r in live}
    for c in restored: rows[c + n] = {}
    corr = [['corr', t['target'], t['source'], tuple(t['operator_word']), F(t['coefficient'])] for t in w['initial_corrections']]
    byp = {}
    for op, rec in enumerate(w['warps'], 1): byp.setdefault(rec[0], []).append(op)
    fwd = []
    for p in range(len(w['B']) + 1):
        for op in byp.get(p, []): fwd.append(['warp', w['warps'][op - 1][1], op])
        if p < len(w['B']): fwd.append(w['B'][p])
    fwd += w['restore']
    prog = corr + w['precondition'] + w['compensation'] + w['A'] + w['cut'] + fwd
    for e in prog: AL.walg_apply(e, rows, False, 10 ** 6)
    res = {}
    for t in range(v, 2 * v):
        d = {wd: x for (var, wd), x in rows[t].items() if var == k}
        if d: res[t] = d
    return res


def audit(w):
    """run the auditor; fix report profile/inventory from its own derived values; return (ok, msg, report)"""
    w = copy.deepcopy(w)
    for attempt in range(3):
        p = Path(tempfile.mkdtemp()) / 'w.json.gz'
        p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode()))
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                AL.run_borrow(p, p.parent / 'out.json', None, None, w, gzip.decompress(p.read_bytes()), 0.0)
            return True, 'PASS', w['report']
        except RuntimeError as ex:
            m = str(ex)
            mm = re.match(r'paid profile mismatch (.*)', m)
            if mm: w['report']['local_profile'] = {str(a): b for a, b in eval(mm.group(1)).items()}; continue
            mm = re.match(r'width inventory mismatch (.*)', m)
            if mm: w['report']['width_inventory'] = {str(a): b for a, b in eval(mm.group(1)).items()}; continue
            return False, m[:160], None
    return False, 'loop', None


def span(vs):
    b = AL.basis(vs); out = set()
    for m in range(1, 1 << len(b)):
        x = 0
        for i in range(len(b)):
            if m >> i & 1: x ^= b[i]
        out.add(x)
    return sorted(out)


def try_helper(k, fe):
    sec, p, e = fe
    info = dict(k=k, first=[sec, p, e])
    if not (e[0] == 'add' and e[1] == k):
        info['fail'] = 'first event is not a write of k'; return info
    c = F(e[3], e[4]); r = e[2]
    if r in entering or r in restored and False: pass
    inv = -1 / c
    if inv.denominator & (inv.denominator - 1) or abs(inv.numerator) & (abs(inv.numerator) - 1):
        info['fail'] = 'non-dyadic inverse'; return info
    w = copy.deepcopy(W)
    F1 = e[-1]
    ins = ['add', r, k, inv.numerator, inv.denominator, F1]
    w[sec].insert(p, ins)
    if sec == 'B':
        for rec in w['warps']:
            if rec[0] > p: rec[0] += 1
    w['compensation'] = [g for g in w['compensation'] if not (g[0] == 'add' and g[2] == k)]
    td = target_dirt(w, k)
    if any(wd != () for d in td.values() for wd in d):
        info['fail'] = 'operator-word dirt on targets'; info['td'] = {t: {str(a): str(b) for a, b in d.items()} for t, d in td.items()}; return info
    inj = [['add', t, k, -d[()].numerator, d[()].denominator] for t, d in sorted(td.items())]
    info['injections'] = inj
    best = None; tried = []
    for u in span(F1):
        w2 = copy.deepcopy(w)
        w2['B'][0:0] = [g + [[u]] for g in inj]
        for rec in w2['warps']: rec[0] += len(inj)
        w2['start_extra'][str(k)] = [u]
        t_ = copy.deepcopy(w2); t_['A'] = w2['A'][npre:]
        w2['cleanup'] = WP.derive_cleanup(t_, restored)
        ok, msg, rep = audit(w2)
        tried.append((u, msg))
        if ok:
            key = sum(int(a) * b for a, b in rep['local_profile'].items())
            if best is None or key < best[0]: best = (key, u, rep, w2)
    info['tried'] = tried
    if best:
        info['pass'] = True; info['u'] = best[1]; info['report'] = best[2]; info['mass'] = best[0]
        info['_word'] = best[3]
    else:
        info['fail'] = 'auditor rejects every u'
    return info


if __name__ == '__main__':
    only = None; outp = None
    a = sys.argv[3:]
    if '--only' in a: only = [int(x) for x in a[a.index('--only') + 1].split(',')]
    if '--out' in a: outp = a[a.index('--out') + 1]
    fe = first_events(W)
    cands = [k for k in live if k >= 2 * v and k not in entering and k not in restored and k not in lenders
             and k not in corrsrc and k not in pretouch]
    if only: cands = only
    base_mass = sum(int(a) * b for a, b in W['report']['local_profile'].items())
    print('base profile', W['report']['local_profile'], 'mass', base_mass, 'candidates', len(cands), flush=True)
    res = []
    for k in cands:
        if k not in fe: continue
        info = try_helper(k, fe[k])
        wd = info.pop('_word', None)
        if info.get('pass') and outp:
            Path(outp).with_suffix(f'.{k}.json.gz').write_bytes(gzip.compress(json.dumps(wd, separators=(',', ':')).encode(), mtime=0))
        print(k, 'PASS' if info.get('pass') else 'fail', info.get('fail', ''), info['first'][:2], info['first'][2][:5],
              'inj', len(info.get('injections', [])), info.get('report', {}).get('local_profile'), [m for _, m in info.get('tried', [])][:3], flush=True)
        res.append(info)
    if outp: Path(outp).write_text(json.dumps(res, indent=1, default=str))
