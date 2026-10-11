# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""Necessity controls for Lemma G on the headline word: each mutant edits the EMITTED stream (and, where stated, the start label) so
that exactly one clause is violated.  For each mutant we report
  checker : the clauses lg_lib flags (label checker + exact scalar replay)  -- must be non-empty (mutant rejected)
  physics : whether the exact physical identity still holds (targeted + random columns; transitions without a recipe are executed
            as T_b T_a^-1).  FAIL => the clause is needed for the operator identity; PASS => the clause is an accounting clause
            (paid children / rank mass / lifetimes), needed for the cost certificate, not for exactness."""
import copy, json, random, sys, time
from lg_lib import load, check_labels, scalar_replay, Frames, rank2
from lg_phys import Model, run, expected, compare
from gd import GD
import os
SP = os.environ['LG_BASE']          # the output directory of verify.py: <SP>/<variant>/{split-centres,hosted}
d = load(f'{SP}/gauge80-kernel42'); c0 = d['c']; m = Model(d); v = c0['v']; start = c0['start']; Fr = Frames(c0['frames'])
FW, BW = d['progs']['forward'], d['progs']['backward']
iA = FW.index(['phase', 'A']); iC = FW.index(['phase', 'centers']); iB = FW.index(['phase', 'B'])


def comp_gates(ev):
    out = []
    for i in range(iA + 1, iC):
        e = ev[i]
        if e[0] == 'scalar' and e[1][0] == 'add':
            t, s = e[1][1][1], e[1][2][1]
            if v <= t < 2 * v and start[s] != 0 and e[2] == start[s]: out.append(i)
    return out


def climbs_of(ev, r, lo=0, hi=None):
    return [i for i in range(lo, hi or len(ev)) if ev[i][0] == 'climb' and ev[i][2] == r]


def both(fn):
    """apply an index-based edit to forward and backward alike (outside the centre phase the streams are aligned)"""
    return fn(copy.deepcopy(FW), 'forward'), fn(copy.deepcopy(BW), 'backward')


def physics(fw, bw, regs, orients=('forward', 'backward')):
    rng = random.Random(7); cols = [(r, b) for r in regs for b in (0, rng.randrange(1, 512))] + [(rng.randrange(m.n), rng.randrange(512)) for _ in range(8)]
    init = {}
    for ci, (r, b) in enumerate(cols): init.setdefault(('L', r), GD.zeros(len(cols))).re[b, ci] = 1
    res = {}
    for o, ev in (('forward', fw), ('backward', bw)):
        if o not in orients or ev is None: continue
        try:
            got = run(m, ev, init, mode='fallback'); bad, left = compare(m, got, expected(m, init, o == 'backward'))
            res[o] = 'PASS' if not bad and not left else f'FAIL (registers {bad[:4]})'
        except Exception as ex: res[o] = f'FAIL ({type(ex).__name__}: {ex})'
    return res


def checker(fw, bw, c=None):
    c = c or c0; out = set(); msgs = []
    for o, ev in (('forward', fw), ('backward', bw)):
        if ev is None: continue
        viol, info, _ = check_labels(c, ev, o == 'backward'); sv = scalar_replay(c, ev, o == 'backward')
        out |= {x[0] for x in viol + sv}; msgs += [f'{o}: {x[0]} {x[1]}' for x in (viol + sv)[:2]]
    return sorted(out), msgs[:3]


R = []
def record(name, clause, fw, bw, regs, c=None, orients=('forward', 'backward')):
    t = time.time(); flags, msgs = checker(fw, bw, c); ph = physics(fw, bw, regs, orients)
    R.append(dict(mutant=name, violates=clause, checker_flags=flags, rejected=bool(flags), first_messages=msgs, physics=ph, seconds=round(time.time() - t, 1)))
    print(json.dumps(R[-1]), flush=True)


# ---------- choose instances ---------------------------------------------------------------------------------------
CG = comp_gates(FW)
# a target whose comps span two levels E1 < E2 with the climb E1 -> E2 in between
tgt2 = None
for i in CG:
    t = FW[i][1][1][1]; cl = climbs_of(FW, t, iA, iC)
    if len(cl) == 2: tgt2 = t; break
g0 = CG[0]; t0_, s0_ = FW[g0][1][1][1], FW[g0][1][2][1]; E0 = FW[g0][2]

# M1  G0 at a compensation gate: the target is NOT at E_j (its climb 0->E removed; next climb starts at 0)
def m1(ev, o):
    cl = climbs_of(ev, t0_, iA, None); a = cl[0]; assert ev[a][3] == 0 and ev[a][4] == E0 and a < g0
    nxt = cl[1]; ev[nxt] = ['climb', ev[nxt][1], t0_, 0, ev[nxt][4], Fr.dim[ev[nxt][4]]]; del ev[a]; return ev
fw, bw = both(m1); record('M1 compensation gate with the target still at label 0', 'G0 (common label at a nonzero-frame compensation)', fw, bw, [t0_, s0_])

# M2  G1 virtual entrance violated: a physical T_E (climb 0 -> E) is executed on the helper; its start is declared 0
def m2(ev, o):
    i = ev.index(['phase', 'A']); ev.insert(i + 1, ['climb', 'A', s0_, 0, start[s0_], Fr.dim[start[s0_]]]); return ev
c2 = copy.deepcopy(c0); c2['start'][s0_] = 0
fw, bw = both(m2); record('M2 physical T_E on an entering helper (no virtual entrance)', 'G1 (virtual entrance)', fw, bw, [s0_], c=c2)

# M3  G2 (target chain monotone; the (b) condition): the target visits its levels out of nesting order (E2 first, descends to E1)
def m3(ev, o):
    t = tgt2; cl = climbs_of(ev, t, iA, iC); a, b = cl[0], cl[1]                 # 0->E1 at a, E1->E2 at b
    E1, E2 = ev[a][4], ev[b][4]; assert Fr.sub(E1, E2)
    g1 = [i for i in range(a + 1, b) if ev[i][0] == 'scalar' and ev[i][1][0] == 'add' and t in (ev[i][1][1][1], ev[i][1][2][1])]
    E1g = [ev[i] for i in g1]
    for i in reversed(g1): del ev[i]
    b -= len(g1); ev[a] = ['climb', 'A', t, 0, E2, Fr.dim[E2]]; del ev[b]
    iCm = ev.index(['phase', 'centers'])
    last = max(i for i in range(a, iCm) if ev[i][0] == 'scalar' and ev[i][1][0] == 'add' and t in (ev[i][1][1][1], ev[i][1][2][1]))
    ins = [['climb', 'A', t, E2, E1, Fr.dim[E1] - Fr.dim[E2]]] + E1g + [['climb', 'A', t, E1, E2, Fr.dim[E2] - Fr.dim[E1]]]
    ev[last + 1:last + 1] = ins; return ev
fw, bw = both(m3); record('M3 target visits its entrance levels out of nesting order (descends E2 -> E1)', 'G2 (monotone nested chain; selection condition (b))', fw, bw, [tgt2])

# M3b G2 for a helper (selection condition (a)): the entering helper's first climb detours through a frame that does not contain E_j
def m3b(ev, o):
    cl = climbs_of(ev, s0_); i = cl[0]; a, b = ev[i][3], ev[i][4]
    X = next(f for f in range(len(Fr.F)) if Fr.dim[f] == Fr.dim[a] and not Fr.sub(a, f) and Fr.sub(f, b))
    ev[i:i + 1] = [['climb', ev[i][1], s0_, a, X, 0], ['climb', ev[i][1], s0_, X, b, Fr.dim[b] - Fr.dim[X]]]; return ev
fw, bw = both(m3b); record('M3b entering helper leaves the nested chain (E_j -> X -> F, X not containing E_j)', 'G2 (monotone nested chain; selection condition (a))', fw, bw, [s0_])

# centre mutants (forward stream; the centre phase is orientation specific)
cents = {}
for i in range(iC + 1, iB):
    e = FW[i]
    if e[0] == 'center': cents.setdefault(e[1], []).append(i)
kdeep = next(k for k, L in cents.items() if len(L) >= 3)             # a centre with a chain c_k -> L1 -> L2 -> ... -> 0
st = cents[kdeep]; rk = c0['centers'][kdeep]
scat_after = lambda i: [j for j in range(i + 1, iB) if FW[j][0] == 'scalar' and FW[j][1][0] == 'add' and FW[j][1][2] == ['C', kdeep] and all(FW[q][0] != 'center' for q in range(i + 1, j))]
lev1 = scat_after(st[0])                                            # scatters at the first served level L1 != 0
tl = FW[lev1[0]][1][1][1]

def m4(ev, o):     # scatter into a level-L1 target after the copy has descended further
    e = ev[lev1[0]]; del ev[lev1[0]]; j = st[1]                   # st[1] index shifts by one
    ev.insert(j, e); return ev
record('M4 scatter into a level-L1 target after the copy descended below L1', 'G3 (scatter meets the target at its level)', m4(copy.deepcopy(FW), 'f'), None, [rk, tl], orients=('forward',))

def m5(ev, o):     # the last descent L_last -> 0 skipped; level-0 targets scattered at L_last
    j = st[-1]; del ev[j]; return ev
r5 = [FW[j][1][1][1] for j in scat_after(st[-1])][:2]
record('M5 last centre descent step skipped (level-0 targets scattered at L_last)', 'G3 (chain reaches every served level; bottom 0)', m5(copy.deepcopy(FW), 'f'), None, [rk] + r5, orients=('forward',))

def m6(ev, o):     # copy made after the first descent: the copy is declared at L1 while the centre register is at c_k
    cp = next(j for j in range(iC, st[0]) if ev[j][0] == 'scalar' and ev[j][1][0] == 'copy' and ev[j][1][1] == ['C', kdeep])
    e = ev[cp]; del ev[cp]; ev.insert(st[0], ['scalar', e[1], FW[st[0]][3]]); return ev
record('M6 centre copy taken at the wrong label (after the first descent)', 'G3 (copy at the centre label c_k)', m6(copy.deepcopy(FW), 'f'), None, [rk, tl], orients=('forward',))

def m7(ev, o):     # a climb of an unrelated register moved inside a live centre phase
    touched = {x[1] for e in ev[iC:iB] if e[0] == 'scalar' for x in e[1][1:] if isinstance(x, list) and x[0] == 'L'}
    def free(i):                     # no event touches the register between the centre phase and this climb
        r = ev[i][2]
        for q in range(iC, i):
            e = ev[q]
            if e[0] in ('climb',) and e[2] == r: return False
            if e[0] == 'scalar' and any(isinstance(x, list) and x == ['L', r] for x in e[1][1:]): return False
        return True
    j = next(i for i in range(iB, len(ev)) if ev[i][0] == 'climb' and ev[i][2] not in touched and free(i)); e = ev[j]; del ev[j]
    ev.insert(st[0] + 1, ['climb', 'centers', e[2], e[3], e[4], e[5]]); return ev
fw7 = m7(copy.deepcopy(FW), 'f'); r7 = fw7[st[0] + 1][2]
record('M7 a child of another register runs while a centre copy is live', 'G3 (copy lifetime)', fw7, None, [r7, rk], orients=('forward',))

def m8(ev, o):     # a centre step detours through a frame outside the centre frame (chain not inside c_k)
    j = st[0]; a, b = ev[j][2], ev[j][3]
    X = next(f for f in range(len(Fr.F)) if Fr.dim[f] == Fr.dim[b] + 1 and Fr.sub(b, f) and not Fr.sub(f, a))
    ev[j:j + 1] = [['center', kdeep, a, X, Fr.dim[a] - Fr.dim[X]], ['center', kdeep, X, b, 1]]; return ev
record('M8 centre chain leaves the centre frame (c_k -> X -> L1, X not inside c_k)', 'G3 (nested chain inside c_k; selection condition (c))', m8(copy.deepcopy(FW), 'f'), None, [rk, tl], orients=('forward',))

# M9  coefficient of one compensation doubled (labels intact)
def m9(ev, o):
    e = ev[g0]; e[1][3] *= 2; return ev
fw, bw = both(m9); record('M9 compensation coefficient doubled', 'S (scalar identity)', fw, bw, [t0_, s0_])

# M10 compensation executed after the helper's first climb (not as the first gate on j)
def m10(ev, o):
    e = ev[g0]; j = climbs_of(ev, s0_)[0]; del ev[g0]; ev.insert(j, e); return ev
fw, bw = both(m10); record('M10 compensation moved after the helper started climbing', 'G0 + S (compensation reads the entrance value)', fw, bw, [t0_, s0_])

# M11 kernel update with the donor still at label 0
kg = next(i for i in range(iA + 1, iC) if FW[i][0] == 'scalar' and FW[i][1][0] == 'add' and FW[i][1][1][1] >= 2 * v and start[FW[i][1][2][1]] != 0 and FW[i][2] != 0)
dn = FW[kg][1][1][1]
def m11(ev, o):
    cl = climbs_of(ev, dn); a = cl[0]; assert ev[a][3] == 0 and a < kg
    ev[cl[1]] = ['climb', ev[cl[1]][1], dn, 0, ev[cl[1]][4], Fr.dim[ev[cl[1]][4]]]; del ev[a]; return ev
fw, bw = both(m11); record('M11 kernel donor update with the donor still at label 0', 'G0 (common label at a nonzero-frame kernel update; inherited #471)', fw, bw, [dn, FW[kg][1][2][1]])

# M12 pre wrapper after the helper's first gate
def m12(ev, o):
    p = ev.index(['residual_adapter', 'pre', s0_, start[s0_]]); e = ev[p]; del ev[p]; ev.insert(g0, e); return ev
fw, bw = both(m12); record('M12 R_E^-1 wrapper after the first gate on the helper', 'G1 (wrapper surrounds the whole invocation)', fw, bw, [s0_, t0_])

# M13 post wrapper dropped
def m13(ev, o):
    ev.remove(['residual_adapter', 'post', s0_, start[s0_]]); return ev
fw, bw = both(m13); record('M13 L_E^-1 wrapper dropped', 'G1 (wrapper surrounds the whole invocation)', fw, bw, [s0_])

json.dump(R, open('MUTANTS.json', 'w'), indent=1)
print('rejected by the checker:', sum(r['rejected'] for r in R), '/', len(R))
