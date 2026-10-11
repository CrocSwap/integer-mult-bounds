# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""Exhaustive exact operator identities for every Lemma G instance of one variant (all 512 basis columns of every input).
  I-tr     every transition used by the program (climbs and centre steps): serialized recipe == T_b T_a^-1 (definition)
  I-comp   the nonzero-frame compensation segment (head of A): for every input register (target or entering helper) the segment
           acts as  h_t -> T_{lam_t} (h_t + sum_j c_tj T_{E_j}^-1 h_j),  h_j -> h_j   (labels lam from the stream)
  I-centre every centre phase, both orientations: forward  h_t += q_t T_{L_t} T_{c_k}^-1 h_r ;  backward  h_r -= sum_t q_t T_{c_k} T_{L_t}^-1 h_t
  I-helper every entering helper: L_E^-1 . (product of the recipes of ITS emitted climb chain E -> ... -> FULL) . R_E^-1 == C_[w] (x) I
usage: lg_instances.py VARIANT [skip_tr]"""
import sys, json, time
from collections import defaultdict
from lg_lib import load, check_labels
from lg_phys import Model, run
from gd import GD, identity_batch, fourier_circ
import os
SP = os.environ['LG_BASE']          # the output directory of verify.py: <SP>/<variant>/{split-centres,hosted}


def main(name, skip_tr=False):
    d = load(f'{SP}/{name}'); m = Model(d); c = d['c']; v = c['v']; start = c['start']
    I = identity_batch(); rep = {'variant': name}; t0 = time.time()
    fw, bw = d['progs']['forward'], d['progs']['backward']
    # ---- I-tr -------------------------------------------------------------------------------------------------
    used = sorted({(e[3], e[4]) for e in fw + bw if e[0] == 'climb'} | {(e[2], e[3]) for e in fw + bw if e[0] == 'center'})
    if not skip_tr:
        badtr = [ab for ab in used if not m.rec_transition(I.copy(), *ab).equals(m.def_transition(I.copy(), *ab))]
        rep['I-tr'] = dict(transitions=len(used), columns_each=512, failures=badtr)
        print(name, 'I-tr', len(used), 'failures', len(badtr), round(time.time() - t0), flush=True)
    # ---- labels along the forward stream ----------------------------------------------------------------------
    lam = {r: start[r] for r in range(2 * v + c['R'])}
    iA = fw.index(['phase', 'A']); seg_end = None; comp = []
    for idx in range(iA + 1, len(fw)):
        e = fw[idx]
        if e[0] == 'climb': lam[e[2]] = e[4]; continue
        if e[0] == 'scalar' and e[1][0] == 'add':
            t, s = e[1][1][1], e[1][2][1]
            if v <= t < 2 * v and start[s] != 0 and e[2] == start[s]: comp.append((t, s, e[1][3], e[1][4])); continue
        seg_end = idx; break
    seg = fw[iA + 1:seg_end]
    # labels at the end of the segment
    lam_end = {r: start[r] for r in range(2 * v + c['R'])}
    for e in fw[:seg_end]:
        if e[0] == 'climb': lam_end[e[2]] = e[4]
    tg = sorted({t for t, s, a, b in comp}); hs = sorted({s for t, s, a, b in comp})
    regs = tg + hs; badc = []
    for r in regs:
        got = run(m, seg, {('L', r): I})
        exp = {}
        if r in tg: exp[r] = m.def_transition(I.copy(), 0, lam_end[r])
        else:
            exp[r] = I.copy()
            for t, s, a, b in comp:
                if s != r: continue
                x = m.def_transition(I.copy(), start[r], lam_end[t]); x.scale(a, b) if b > 0 else x.scale(-a, -b)
                if t in exp: exp[t].add_scaled(x, 1, 1)
                else: exp[t] = x
        keys = set(exp) | {k[1] for k in got if k[0] == 'L'}
        for k in keys:
            a_ = got.get(('L', k)); b_ = exp.get(k)
            if a_ is None: a_ = GD.zeros(512)
            if b_ is None: b_ = GD.zeros(512)
            if not a_.equals(b_): badc.append((r, k))
    rep['I-comp'] = dict(compensation_gates=len(comp), targets=len(tg), entering_helpers_compensating=len(hs),
                         input_registers=len(regs), columns_each=512, target_levels_after_segment=sorted({lam_end[t] for t in tg}), failures=badc)
    print(name, 'I-comp gates', len(comp), 'inputs', len(regs), 'failures', len(badc), round(time.time() - t0), flush=True)
    # ---- I-centre -----------------------------------------------------------------------------------------------
    badk = []; cinfo = []
    for orient, ev in (('forward', fw), ('backward', bw)):
        lamc = {r: start[r] for r in range(2 * v + c['R'])}
        i0 = ev.index(['phase', 'centers']); i1 = ev.index(['phase', 'B'])
        for e in ev[:i0]:
            if e[0] == 'climb': lamc[e[2]] = e[4]
        cent = ev[i0 + 1:i1]
        groups = defaultdict(list); cur = None
        for e in cent:
            if e[0] == 'scalar':
                op = e[1]; ks = [x[1] for x in op[1:] if isinstance(x, list) and x[0] == 'C']
                if ks: cur = ks[0]
            elif e[0] == 'center': cur = e[1]
            groups[cur].append(e)
        for k, evs in sorted(groups.items()):
            r = c['centers'][k]; cf = c['center_frames'][k]; assert lamc[r] == cf
            terms = [(op[1][1], op[3], op[4]) for _, op, f in [e for e in evs if e[0] == 'scalar'] if op[0] == 'add' and op[1][0] == 'L' and op[2][0] == 'C'] if orient == 'forward' else \
                    [(op[2][1], op[3], op[4]) for _, op, f in [e for e in evs if e[0] == 'scalar'] if op[0] == 'add' and op[1][0] == 'C' and op[2][0] == 'L']
            path = [cf] + [e[3] for e in evs if e[0] == 'center'] if orient == 'forward' else None
            if orient == 'forward':
                got = run(m, evs, {('L', r): I})
                exp = {r: I.copy()}
                for t, a, b in terms:
                    x = m.def_transition(I.copy(), cf, lamc[t]); x.scale(a, b)
                    if t in exp: exp[t].add_scaled(x, 1, 1)
                    else: exp[t] = x
                for kk in set(exp) | {q[1] for q in got if q[0] == 'L'}:
                    a_, b_ = got.get(('L', kk)), exp.get(kk)
                    if not (a_ or GD.zeros(512)).equals(b_ or GD.zeros(512)): badk.append((orient, k, kk))
                if any(q[0] == 'C' and not y.is_zero() for q, y in got.items()): badk.append((orient, k, 'copy not cleared'))
                cinfo.append(dict(centre=k, register=r, frame=cf, path_dims=[len(m.frames[f]) for f in path], targets=len(terms)))
            else:
                for t, a, b in terms:
                    got = run(m, evs, {('L', t): I})
                    x = m.def_transition(I.copy(), lamc[t], cf); x.scale(-a, b)
                    exp = {t: I.copy(), r: x}
                    for kk in set(exp) | {q[1] for q in got if q[0] == 'L'}:
                        a_, b_ = got.get(('L', kk)), exp.get(kk)
                        if not (a_ or GD.zeros(512)).equals(b_ or GD.zeros(512)): badk.append((orient, k, t, kk))
                    if any(q[0] == 'C' and not y.is_zero() for q, y in got.items()): badk.append((orient, k, t, 'copy not cleared'))
    rep['I-centre'] = dict(centres=len(c['centers']), detail=cinfo, failures=badk)
    print(name, 'I-centre failures', len(badk), round(time.time() - t0), flush=True)
    # ---- I-helper -----------------------------------------------------------------------------------------------
    badh = []; widths = defaultdict(int)
    for r in range(2 * v, 2 * v + c['R']):
        if start[r] == 0: continue
        chain = [(e[3], e[4]) for e in fw if e[0] == 'climb' and e[2] == r]
        assert chain[0][0] == start[r] and chain[-1][1] == 1
        Rc, Lc, w = m.wraps[start[r]]; widths[w] += 1
        g = I.copy().apply_circ(Rc, inverse=True)
        for a, b in chain: m.rec_transition(g, a, b)
        g.apply_circ(Lc, inverse=True)
        if not g.equals(I.copy().apply_circ(fourier_circ(range(w)))): badh.append(r)
    rep['I-helper'] = dict(entering_helpers=sum(widths.values()), widths=dict(widths), columns_each=512, failures=badh)
    print(name, 'I-helper', sum(widths.values()), 'failures', len(badh), round(time.time() - t0), flush=True)
    rep['seconds'] = round(time.time() - t0, 1)
    json.dump(rep, open(f'INSTANCES-{name}.json', 'w'), indent=1)


if __name__ == '__main__': main(sys.argv[1], len(sys.argv) > 2)
