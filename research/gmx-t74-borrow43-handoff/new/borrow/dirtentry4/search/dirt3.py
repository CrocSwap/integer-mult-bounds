"""General dirt-entry census: helper k enters at a 1-dim frame [u] (width 9 -> 8), its compensation is removed and its dirt
response D_orig (= lambda_k at A start) is cancelled by inserted reads  z += beta*k  while k is still pure (before its first event p),
each at gate frame G with cur_z = G (zero-cost, 'free') or cur_z subset G subset next_z ('climb'), G = [u] (or F1 when 2-dim... only [u] here).
Targets may receive an A-injection only if their A-end level contains u (lifted targets).  PR2833's case is the B-first special case
(k pure through A, so targets can be injected at B entry).  usage: dirt3.py WORD AUDIT_DIR [--only ..] [--out prefix] [--climb]
"""
import sys, json, gzip, copy
from pathlib import Path
from fractions import Fraction as F
exec(open(Path(__file__).with_name('dirtcensus.py')).read().split("if __name__ == '__main__':")[0])

full = AL.basis([1 << i for i in range(9)])
# global forward sequence
seq = []   # (section, index_in_section or None, item)
for i, e in enumerate(W['A']): seq.append(('A', i, e))
for i, e in enumerate(W['cut']): seq.append(('cut', i, e))
byp = {}
for op, rec in enumerate(W['warps'], 1): byp.setdefault(rec[0], []).append(op)
for p in range(len(W['B']) + 1):
    for op in byp.get(p, []):
        rec = W['warps'][op - 1]; seq.append(('Bw', p, ['warp', rec[1], op, rec[3], rec[4]]))
    if p < len(W['B']): seq.append(('B', p, W['B'][p]))
for i, e in enumerate(W['restore']): seq.append(('R', i, e))
L = len(seq)
istar = lambda r: v <= r < 2 * v
lev = {v + int(t): AL.basis(U) for t, U in W['target_levels'].items()}


def touch(e):
    return (e[1],) if e[0] == 'warp' else regs(e)


# forward frames: frame of z just before each of its touches
start = [(p,) for p in W['ports']] + [()] * (v + R)
for q, U in W['start_extra'].items(): start[int(q)] = AL.basis(U)
cur = start.copy()
touches = {}   # z -> list of (tau, frame_before, frame_of_gate)
for tau, (sec, i, e) in enumerate(seq):
    for z in touch(e):
        if e[0] == 'warp':
            fr = AL.basis(e[4]); touches.setdefault(z, []).append((tau, cur[z], ('warp', AL.basis(e[3])))); cur[z] = fr
        else:
            fr = AL.basis(e[-1]) if e[-1] is not None else cur[z]
            touches.setdefault(z, []).append((tau, cur[z], fr)); cur[z] = fr
endframe = cur

# reverse adjoint sweep, lambda_z at 'before gate tau' for every touch
lam = {t: {t: F(1)} for t in range(v, 2 * v)}; taint = set()
lam_at = {}   # (z, tau) -> (lambda, tainted)   value valid for the segment ending at touch tau
lam_start = {}
for tau in range(L - 1, -1, -1):
    sec, i, e = seq[tau]
    if e[0] == 'warp':
        z = e[1]
        if lam.get(z): taint.add(z)
    elif e[0] == 'add':
        a, b = e[1], e[2]; c = F(e[3], e[4])
        if lam.get(a):
            d = lam.setdefault(b, {})
            for t, x in lam[a].items():
                y = d.get(t, 0) + c * x
                if y: d[t] = y
                else: d.pop(t, None)
            if a in taint: taint.add(b)
    else:
        s = F(e[2], e[3])
        if e[1] in lam: lam[e[1]] = {t: s * x for t, x in lam[e[1]].items()}
    for z in touch(e): lam_at[z, tau] = (dict(lam.get(z, {})), z in taint)
for z in range(n): lam_start[z] = (dict(lam.get(z, {})), z in taint)

# segments: (z, t0, t1, frame, nextframe, lambda, tainted); insertion allowed for tau in [t0, t1]
segs = []
for z in live:
    if z in restored or z in lenders or z in centers: continue
    tl = touches.get(z, [])
    prev = 0; fr = start[z]
    for (tau, fb, fg) in tl:
        lz, tn = lam_at[z, tau]
        if not tn and lz: segs.append((z, prev, tau, fb, None if isinstance(fg, tuple) and fg and fg[0] == 'warp' else fg, lz, tn))
        prev = tau + 1
    # after last touch: lambda is zero for non-targets (nothing reads it later) unless target
    if istar(z):
        lz = {z: F(1)}; segs.append((z, prev, L, endframe[z], 'END', lz, False))
print('segments', len(segs), flush=True)


def ok_frame(z, fb, fg, tau, G):
    if not AL.contained(fb, G): return False
    if fg == 'END':
        # target after last touch: only allowed if no frame obligation remains... (targets end at full via final climb)
        return True
    if fg is None: return False
    if not AL.contained(G, fg): return False
    if istar(z):
        # A-end target level equality
        sec = seq[tau][0] if tau < L else 'R'
        if sec == 'A':
            return AL.contained(G, lev.get(z, ())) and AL.contained(lev.get(z, ()), G) or False
    return True


def greedy_span(vecs, rhs):
    """exact: find combination of vecs (list of (key, dict)) equal to rhs; returns {key: coef} using a pivot basis"""
    basisrows = []   # list of (pivot_t, row dict, combo dict)
    def reduce(row, combo):
        row = dict(row); combo = dict(combo)
        for pt, br, bc in basisrows:
            if pt in row:
                f = row[pt]
                for t, x in br.items():
                    y = row.get(t, 0) - f * x
                    if y: row[t] = y
                    else: row.pop(t, None)
                for kk, x in bc.items():
                    y = combo.get(kk, 0) - f * x
                    if y: combo[kk] = y
                    else: combo.pop(kk, None)
        return row, combo
    for key, vec in vecs:
        row, combo = reduce(vec, {key: F(1)})
        if not row: continue
        pt = min(row); f = row[pt]
        row = {t: x / f for t, x in row.items()}; combo = {kk: x / f for kk, x in combo.items()}
        # keep fully reduced
        for j, (pt2, br2, bc2) in enumerate(basisrows):
            if pt in br2:
                g = br2[pt]
                br2 = {t: br2.get(t, 0) - g * row.get(t, 0) for t in set(br2) | set(row)}; br2 = {t: x for t, x in br2.items() if x}
                bc2 = {kk: bc2.get(kk, 0) - g * combo.get(kk, 0) for kk in set(bc2) | set(combo)}; bc2 = {kk: x for kk, x in bc2.items() if x}
                basisrows[j] = (pt2, br2, bc2)
        basisrows.append((pt, row, combo))
        r_, c_ = reduce(rhs, {})
        if not r_: return {kk: -x for kk, x in c_.items()}
    return None


if __name__ == '__main__':
    args = sys.argv[3:]
    only = [int(x) for x in args[args.index('--only') + 1].split(',')] if '--only' in args else None
    outp = args[args.index('--out') + 1] if '--out' in args else None
    climb = '--climb' in args
    excl = set(int(x) for x in args[args.index('--excl') + 1].split(',')) if '--excl' in args else set()
    cands = [k for k in live if k >= 2 * v and k not in entering and k not in restored and k not in lenders
             and k not in corrsrc and k not in pretouch and k not in centers]
    if only: cands = only
    results = []
    for k in cands:
        tk = touches[k]; p, fb, F1 = tk[0]
        if isinstance(F1, tuple) and F1 and F1[0] == 'warp': continue
        Dk, tn = lam_start[k]
        info = dict(k=k, p=p, sec=seq[p][0], F1=F1, nD=len(Dk))
        if tn or not F1:
            info['fail'] = 'tainted' if tn else 'first gate at zero frame'; results.append(info)
            print(k, info['sec'], p, 'F1', F1, info['fail'], flush=True); continue
        found = None
        Us = ([tuple(AL.basis(F1))] if (len(F1) > 1 and '--raise' in args) else []) + [(u,) for u in span(F1)]
        for U in Us:
            u = U
            pool = []
            for G in ([U, AL.basis(F1)] if len(F1) > len(U) else [U]):
              for (z, t0, t1, fz, fg, lz, _) in segs:
                if z == k or z in excl: continue
                lo = max(t0, npre); hi = min(t1, p)   # insertion strictly before k's first event p (tau <= p)
                if lo > hi: continue
                if not ok_frame(z, fz, fg, hi, G): continue
                free = (fz == G) or (fg != "END" and fg == G)
                if not free and not climb: continue
                pool.append(((z, hi, free, G), lz))
            pool.sort(key=lambda x: (not x[0][2], -x[0][1]))
            sol = greedy_span(pool, {t: -x for t, x in Dk.items()})
            if sol is not None:
                found = (u, sol); break
        if not found:
            info['fail'] = 'D not in span of compatible reads'; results.append(info)
            print(k, info['sec'], p, 'F1', F1, 'nD', len(Dk), info['fail'], flush=True); continue
        u, sol = found
        w2 = copy.deepcopy(W)
        w2['compensation'] = [g for g in w2['compensation'] if not (g[0] == 'add' and g[2] == k)]
        # insert gates; process from latest tau to earliest so indices stay valid
        ins = sorted(((z, tau, x, G) for (z, tau, free, G), x in sol.items()), key=lambda x: (-x[1], -len(x[3])))
        for z, tau, x, G in ins:
            sec, i, _ = seq[tau] if tau < L else ('R', len(W['restore']), None)
            g = ['add', z, k, x.numerator, x.denominator, list(G)]
            if sec == 'A': w2['A'].insert(i, g)
            elif sec == 'B':
                w2['B'].insert(i, g)
                for rec in w2['warps']:
                    if rec[0] > i: rec[0] += 1
            elif sec == 'Bw':
                w2['B'].insert(i, g)
                for rec in w2['warps']:
                    if rec[0] > i: rec[0] += 1
            else:
                info['fail'] = 'insertion in ' + sec; break
        if 'fail' in info:
            results.append(info); print(k, info['fail']); continue
        w2['start_extra'][str(k)] = list(u)
        t_ = copy.deepcopy(w2); t_['A'] = w2['A'][npre:]
        w2['cleanup'] = WP.derive_cleanup(t_, restored)
        ok, msg, rep = audit(w2)
        info.update(u=u, ninj=len(sol), audit=msg, profile=rep and rep['local_profile'], free=all(f for (_, _, f, _) in sol), gates=[[z, tau, str(x), G] for (z, tau, f, G), x in sol.items()])
        if ok and outp: Path(f'{outp}.{k}.json.gz').write_bytes(gzip.compress(json.dumps(w2, separators=(',', ':')).encode(), mtime=0))
        print(k, info['sec'], p, 'F1', F1, 'nD', len(Dk), 'u', u, 'ninj', len(sol), msg, rep and rep['local_profile'], flush=True)
        results.append(info)
    if outp: Path(outp + '.json').write_text(json.dumps(results, indent=1, default=str))
