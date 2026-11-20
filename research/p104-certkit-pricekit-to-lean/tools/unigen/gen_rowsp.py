#!/usr/bin/env python3
"""ROWS2 generator (OUR Python, 1 proc): PACKED reverse-mode row certificate (UniRowsPDefs.pstep) for a packed trace.
Same inputs/outputs as gen_rows.py, but co-rows are single big Nats (W-bit digits, offset K = 2^KB):
  <Pre>Par.lean : rows_pkpar PK W KB NO + kernel checks PK_ok (Pk.okb) and PK_Z0 (bnd Z0)
  <Pre>Ck<k>.lean, <Pre>Seg<k>.lean, <Pre>Segs.lean, assembly <Pre>{Defs,Chain,Evs,Top1,Top2,Top3,Bot,Main}.lean
env: SEEDS (all | X | Y | XY | list), WORD, SLOT (96|128), NSI, D (scale; default: searched), W (56), KB (34),
     CAP (hot events per segment, default 6000), ONLY (segments to emit), assembly names as gen_rows.py.
usage: gen_rowsp.py Evs.lean Tabs.lean outdir Prefix Namespace EvsNs"""
import re, sys, os
evsf, tabsf, out, Pre, Ns, EvNs = sys.argv[1:7]
EV = open(evsf).read(); TB = open(tabsf).read()
chunks = {int(m.group(1)): int(m.group(2), 16) for m in re.finditer(r'^def c(\d+) : Nat := 0x([0-9a-f]+)', EV, re.M)}
order = []
for k in range(10000):
    m = re.search(r'^def seg%d : List \(Nat × Nat\) := \[([^\]]*)\]' % k, TB, re.M)
    if not m: break
    order += [(int(a), int(b)) for a, b in re.findall(r'\((\d+), [A-Za-z0-9_.]*Evs\.c(\d+)\)', m.group(1))]
mP = re.search(r'^def P : Par := ⟨(\d+), (\d+),', TB, re.M); NP, NR = int(mP.group(1)), int(mP.group(2))
NSI = os.environ.get('NSI', 'UniInhabit')
RL = NSI.replace('UniInhabit', 'UniRows'); RP = RL + 'P'   # packed-library namespace (UniRowsP / UniRowsWs4P ...)
SLOT = int(os.environ.get('SLOT', '96')); NB = (SLOT - 48) // 2; SS = 1 << SLOT
def dec(n, x):
    r = []
    for _ in range(n):
        y = x % SS; x //= SS
        r.append((y % 8, y // 8 % 2048, y // 16384 % 2048, y // 33554432 % 2048, y // 68719476736 % 2048,
                  y // 140737488355328 % 2 == 1, (y >> 48) % (1 << NB), (y >> (48 + NB)) % (1 << NB)))
    return r
chev = [dec(n, chunks[c]) for n, c in order]
NC = len(order)
seeds = os.environ.get('SEEDS', 'all')
if seeds in ('X', 'Y', 'XY'):
    import gzip, json
    live = json.load(gzip.open(os.environ['WORD']))['live']
    seeds = (list(live) if 'X' in seeds else []) + ([r + 112 for r in live] if 'Y' in seeds else [])
else:
    seeds = list(range(NP)) if seeds == 'all' else [int(x) for x in seeds.split(',') if x]
NO = NP
W = int(os.environ.get('W', '56')); KB = int(os.environ.get('KB', '34')); K = 1 << KB; B = 1 << W
R = 0
for _ in range(NO): R = (R << W) + 1
Z0 = K * R; MSK = (B - 2 * K) * R; BN = 1 << (W * NO)
def bnd(V): return V & MSK == 0 and V < BN
loc = [0] * 2048; locc = [list(loc)]
for ci in range(NC):
    for (op, r, a, c, d, neg, num, den) in chev[ci]:
        if op in (0, 1): loc[r] = c + 2
        elif op == 4: loc[r] = d + 2
        elif op == 5: loc[r] = 1
    locc.append(list(loc))
class Inexact(Exception): pass
def comb(Va, Vr, neg, p, q):
    N = Va * q + p * Z0 if neg else Va * q + p * Vr
    S = p * Vr if neg else p * Z0
    if S > N or (N - S) % q: raise Inexact(q)
    V = (N - S) // q
    if not bnd(V): raise ValueError('bound')
    return V
def runback(D, snaps):
    g = {j: Z0 + D * (1 << (W * j)) for j in seeds}; a = {}; z = 0
    for j in seeds: z |= 1 << j
    snap = [None] * (NC + 1); snap[NC] = (dict(g), dict(a), z); hotc = [0] * NC
    for ci in range(NC - 1, -1, -1):
        h = 0
        for (op, r, aa, c, d, neg, num, den) in reversed(chev[ci]):
            if not (z >> r) & 1: continue
            h += 1
            if op == 0:
                V = g.get(r, Z0) + a.get(r, Z0) - Z0
                if not bnd(V): raise ValueError('bound')
                a[r] = V; g[r] = Z0
            elif op in (1, 5): g[r] = Z0
            elif op in (2, 3):
                if den == 0 or K * (2 * den + num) >= B: raise ValueError('coef guard')
                if op == 2: g[aa] = comb(g.get(aa, Z0), g.get(r, Z0), neg, num, den); z |= 1 << aa
                else: g[r] = comb(Z0, g.get(r, Z0), neg, num, den)
        hotc[ci] = h
        if snaps: snap[ci] = (dict(g), dict(a), z)
    return snap, hotc
D = int(os.environ.get('D', '0'))
if not D:
    D = 2
    while True:
        try: runback(D, False); break
        except Inexact as ex: D *= ex.args[0]
    # minimise: drop factors while still exact
    for p in (2, 3, 5, 7, 11, 13):
        while D % (2 * p) == 0 or (p != 2 and D % p == 0):
            try: runback(D // p, False); D //= p
            except Inexact: break
        if D % 2: D *= 2
snap, hotc = runback(D, True)
CAP = float(os.environ.get('CAP', '6000'))
bounds = [NC]; acc = 0.0
for ci in range(NC - 1, -1, -1):
    if acc + hotc[ci] > CAP and acc > 0: bounds.append(ci + 1); acc = 0.0
    acc += hotc[ci]
bounds.append(0); bounds = sorted(set(bounds))
NSEG = len(bounds) - 1
print('NP', NP, 'NR', NR, 'chunks', NC, 'seeds', len(seeds), 'D', D, 'W', W, 'KB', KB, 'segments', NSEG, 'hot', sum(hotc))
print('seg hot', [sum(hotc[bounds[k]:bounds[k + 1]]) for k in range(NSEG)])
def svs(V):
    if V == Z0: return ''
    o = []
    for i in range(NO):
        x = ((V >> (W * i)) & (B - 1)) - K
        if x: o.append('%d:%d' % (i, x))
    return ','.join(o)
HD = 'import Nov15.%sPMeta\nnamespace %s\nopen %s %s %s\n' % (RL, Ns, NSI, RL, RP)
ONLY = [int(x) for x in os.environ.get('ONLY', '').split(',') if x]
segs = ONLY if ONLY else list(range(NSEG))
ASM = os.environ.get('ASM_ONLY') == '1'
if ASM: segs = []
for k in sorted(set(segs) | set(k + 1 for k in segs)):
    g, a, z = snap[bounds[k]]; L = locc[bounds[k]]
    with open('%s/%sCk%d.lean' % (out, Pre, k), 'w') as f:
        f.write('/- GENERATED by Nov15/unigen/gen_rowsp.py (lane ROWS2). DATA: packed row checkpoint %d = state before chunk %d. -/\n' % (k, bounds[k]))
        f.write(HD)
        f.write('rows_nat t%d "%s"\n' % (k, '|'.join(str(L[j]) for j in range(2048))))
        f.write('def z%d : Nat := %s\n' % (k, hex(z)))
        f.write('rows_pk g%d %d %d %d "%s"\n' % (k, W, KB, NO, '|'.join(svs(g.get(j, Z0)) for j in range(2048))))
        f.write('rows_pk a%d %d %d %d "%s"\n' % (k, W, KB, NO, '|'.join(svs(a.get(j, Z0)) for j in range(2048))))
        f.write('noncomputable def s%d : PS := ⟨t%d, z%d, g%d, a%d⟩\n' % (k, k, k, k, k))
        f.write('end %s\n' % Ns)
for k in segs:
    with open('%s/%sSeg%d.lean' % (out, Pre, k), 'w') as f:
        f.write('/- GENERATED by Nov15/unigen/gen_rowsp.py (lane ROWS2): packed backward row segment %d (chunks %d..%d), kernel rfl. -/\n'
                % (k, bounds[k], bounds[k + 1] - 1))
        f.write('import Nov15.%sCk%d\nimport Nov15.%sCk%d\nimport Nov15.%sSegs\nimport Nov15.%sPar\nnamespace %s\nopen %s %s %s\n'
                % (Pre, k, Pre, k + 1, Pre, Pre, Ns, NSI, RL, RP))
        f.write('kernel_rfl bseg%d : prun PK %d s%d (decodeAll seg%d).reverse = some s%d\n' % (k, NR, k + 1, k, k))
        f.write('end %s\n' % Ns)
if not ASM:
  with open('%s/%sPar.lean' % (out, Pre), 'w') as f:
    f.write('/- GENERATED by Nov15/unigen/gen_rowsp.py (lane ROWS2): packing parameters (kernel-checked). -/\n')
    f.write(HD + 'rows_pkpar PK %d %d %d\n' % (W, KB, NO))
    f.write('theorem PK_ok : PK.okb = true := by decide +kernel\ntheorem PK_Z0 : bnd PK PK.Z0 = true := by decide +kernel\n')
    f.write('end %s\n' % Ns)
def segdef(k): return 'def seg%d : List (Nat × Nat) := [%s]\n' % (k, ', '.join('(%d, %s.c%d)' % (order[ci][0], EvNs, order[ci][1]) for ci in range(bounds[k], bounds[k + 1])))
if not ASM:
 with open('%s/%sSegs.lean' % (out, Pre), 'w') as f:
    f.write('/- GENERATED by Nov15/unigen/gen_rowsp.py (lane ROWS2): chunk groups of the packed backward row segments. -/\n')
    f.write('import Nov15.%sEvs\nnamespace %s\n' % (NSI, Ns))
    for k in range(NSEG): f.write(segdef(k))
    f.write('def NSEG : Nat := %d\ndef DSC : Nat := %d\ndef SEEDS : List Nat := %s\n' % (NSEG, D, '[' + ', '.join(map(str, seeds)) + ']'))
    f.write('end %s\n' % Ns)
# ---- assembly
E = lambda k, d: os.environ.get(k, d)
MODEL, TR, EVS, LST, SOUND, CKEND = E('MODEL', 'M7669'), E('TR', 'tr7669'), E('EVS', 'evs7669'), E('LST', 'L7669'), E('SOUND', 'sound7669'), E('CKEND', 'Tabs.ck26')
MOK, RT, CALLER, NREG, WIMP = E('MOK', 'M7669_ok'), E('RT', 'R7'), E('CALLER', 'caller7113'), int(E('NREG', '1752')), E('WIMP', 'Nov15.UniInhabitWord')
SM = 0
for j in seeds: SM |= 1 << j
def nest(k): return 'seg%d' % k if k == NSEG - 1 else '(seg%d ++ %s)' % (k, nest(k + 1))
TPL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rowsp_main.tpl')).read()
HDR0 = 'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\nset_option autoImplicit false\nnamespace %s\nopen %s %s %s\n\n' % (Ns, NSI, RL, RP)
REGM, TABM = E('REGMOD', 'Nov15.UniInhabitReg'), E('TABSMOD', 'Nov15.UniInhabitTabs')
HDR = 'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\nset_option autoImplicit false\nnamespace %s\nopen %s %s %s WordModel Uni %s\n\n' % (Ns, NSI, RL, RP, E('OPENS', 'UniFold7113'))
PS_ = 'Nov15.%sPSound' % RL
def gen(name, imports, body, hdr=None):
    with open('%s/%s%s.lean' % (out, Pre, name), 'w') as f:
        f.write('/- GENERATED by Nov15/unigen/gen_rowsp.py (lane ROWS2): %s%s (packed seeded rows, %d segments, %d seeds). Kernel only. -/\n' % (Pre, name, NSEG, len(seeds)))
        for m in imports: f.write('import %s\n' % m)
        f.write((HDR if hdr is None else hdr) + body + '\nend %s\n' % Ns)
gen('Defs', ['Nov15.%sSegs' % Pre], 'def SMASK : Nat := %s\ndef HSC : Nat := %d\ndef ALL : List (Nat × Nat) := %s\n' % (hex(SM), D // 2, nest(0)), hdr='namespace %s\n\n' % Ns)
gen('Chain', [PS_, 'Nov15.%sDefs' % Pre] + ['Nov15.%sSeg%d' % (Pre, k) for k in range(NSEG)],
    'theorem chainAll : prun PK %d s%d (decodeAll ALL).reverse = some s0 := by\n  have c%d := bseg%d\n' % (NR, NSEG, NSEG - 1, NSEG - 1)
    + ''.join('  have c%d := prun_cat c%d bseg%d\n' % (k, k + 1, k) for k in range(NSEG - 2, -1, -1)) + '  unfold ALL; exact c0\n', hdr=HDR0)
gen('Evs', [PS_, WIMP, 'Nov15.%sDefs' % Pre],
    'theorem hAll : (%s.map Prod.fst).flatten = ALL := rfl\ntheorem evs_eq : %s = decodeAll ALL := by unfold %s; rw [chainEvs_eq, hAll]\n' % (LST, EVS, EVS))
gen('Top1', [PS_, TABM, 'Nov15.%sDefs' % Pre, 'Nov15.%sCk%d' % (Pre, NSEG)],
    'theorem tT : Tr.beq t%d %s = true := by decide +kernel\n' % (NSEG, CKEND), hdr=HDR0)
gen('Top2', [PS_, 'Nov15.%sDefs' % Pre, 'Nov15.%sPar' % Pre, 'Nov15.%sCk%d' % (Pre, NSEG)],
    'theorem tZ : ∀ j < 2048, (Nat.testBit z%d j || Nat.beq (gtA PK.Z0 11 g%d j) PK.Z0) = true := by decide +kernel\n' % (NSEG, NSEG), hdr=HDR0)
TGP = ('noncomputable def tGP (j : Nat) : Bool := bnd PK (gtA PK.Z0 11 g%d j) && bnd PK (gtA PK.Z0 11 a%d j) &&\n'
    '  decide (((gtA PK.Z0 11 g%d j : Nat) : Int) = (PK.Z0 : Int) + pkI PK.W (if Nat.testBit SMASK j then [(j, (DSC : Int))] else [])) &&\n'
    '  Nat.beq (gtA PK.Z0 11 a%d j) PK.Z0 && (!Nat.testBit SMASK j || (Nat.blt j PK.NO && Nat.ble DSC PK.K))\n' % (NSEG, NSEG, NSEG, NSEG))
BTP = ('noncomputable def colF (j : Nat) : SV := (colE %s DSC HSC idxOf (regOf j)).filter (fun e => Nat.testBit SMASK e.1)\n'
    'noncomputable def tBP (j : Nat) : Bool := bnd PK (gtA PK.Z0 11 a0 j) && decide (((gtA PK.Z0 11 a0 j : Nat) : Int) = (PK.Z0 : Int) + pkI PK.W (colF j)) &&\n'
    '  (colF j).all (fun e => Nat.blt e.1 PK.NO) && Nat.ble (sabs (colF j)) PK.K\n' % CALLER)
def split(name, pname, n, imps, hdr):
    q = (n + 3) // 4
    for i in range(4):
        gen('%s_%d' % (name, i), ['Nov15.%s%sP' % (Pre, name)], 'theorem %s_%d : ∀ j < %d, %s (j + %d) = true := by decide +kernel\n' % (name.lower(), i, max(0, min(q, n - q * i)), pname, q * i), hdr=hdr)
    cases = '  rcases (show j < %d ∨ (%d ≤ j ∧ j < %d) ∨ (%d ≤ j ∧ j < %d) ∨ (%d ≤ j ∧ j < %d) by omega) with h | h | h | h\n' % (q, q, 2*q, 2*q, 3*q, 3*q, n)
    for i in range(4):
        cases += '  · have := %s_%d (j - %d) (by omega); rwa [show j - %d + %d = j by omega] at this\n' % (name.lower(), i, q*i, q*i, q*i)
    gen(name, ['Nov15.%s%s_%d' % (Pre, name, i) for i in range(4)],
        'theorem %s : ∀ j < %d, %s j = true := by\n  intro j hj\n' % ({'Top3': 'tG', 'Bot': 'tB'}[name], n, pname) + cases, hdr=hdr)
gen('Top3P', [PS_, 'Nov15.%sDefs' % Pre, 'Nov15.%sPar' % Pre, 'Nov15.%sCk%d' % (Pre, NSEG)], TGP, hdr=HDR0)
split('Top3', 'tGP', 2048, None, HDR0)
gen('BotP', [PS_, REGM, 'Nov15.%sDefs' % Pre, 'Nov15.%sPar' % Pre, 'Nov15.%sCk0' % Pre], BTP)
split('Bot', 'tBP', NREG, None, HDR)
gen('Main', [WIMP] + ['Nov15.%s%s' % (Pre, m) for m in ['Chain', 'Evs', 'Top1', 'Top2', 'Top3', 'Bot']],
    TPL.replace('@RT', RT).replace('@CALLER', CALLER).replace('@TR', TR).replace('@MODEL', MODEL)
    .replace('@SOUND', SOUND).replace('@K', str(NSEG)).replace('@MOK', MOK).replace('@NS', Ns))
