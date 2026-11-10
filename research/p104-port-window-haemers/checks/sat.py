"""The SAT side of the k = 2 data: regenerate every DIMACS instance and compare variable count, clause count and sha256 with the record;
evaluate explicit labellings on the formulas (the witness satisfies the 14-port formula at rank 17, a mutant does not, Gram tensor I_2
satisfies the full formula at rank 18); verify the shipped DRAT proof file against its recorded sha256. No solver is run here."""
import sys, os, lzma, hashlib, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from satenc import Enc, KALL, OALL, dt

res = load('sat_results.json')
inst = res['instances']
sha = {}
for name, rec in inst.items():
    sub, R = ('full' if name.startswith('full') else 'sub14'), rec['inner_dim']
    e = Enc(R, sub)
    s = e.sha256()
    sha[name] = s
    req(e.nv == rec['variables'] and len(e.cl) == rec['clauses'] and s == rec['dimacs_sha256'],
        '%s: regenerated formula has %d variables, %d clauses, sha256 %s...' % (name, e.nv, len(e.cl), s[:12]))
    if name == 'sub14_r17':
        W = load('witness14.json')
        coords = {int(t): c for t, c in W['coords'].items()}

        def labels(coords):
            lab = {}
            for t in e.oth:
                assert all(c in e.supp[t] for c in coords[t]), 'witness coordinate outside the support of port %d' % t
                for i in range(2):
                    for c, v in e.U[t][i].items():
                        lab[v] = c == coords[t][i]
                    for c, v in e.W[t][i].items():
                        lab[v] = c == coords[t][i]
            return lab

        bad = e.evaluate(labels(coords))
        req(not bad, 'sub14_r17: the exact 14-port representation (k = 2, 17 coordinates) satisfies all %d clauses' % len(e.cl))
        mut = None
        for t in e.oth:
            for i in range(2):
                for s2 in e.oth + KALL:
                    if s2 != t and dt(t, s2) == 0:
                        for new in coords[s2]:
                            if new in e.supp[t] and new not in coords[t] and mut is None:
                                mut = (t, i, new)
        t, i, new = mut
        c2 = {u: list(v) for u, v in coords.items()}
        c2[t][i] = new
        bad = e.evaluate(labels(c2))
        req(len(bad) > 0, 'control: moving one coordinate of port %d onto a coordinate of an orthogonal port falsifies %d clauses' % (t, len(bad)))
    if name == 'full_r18':
        # Gram representation tensor I_2 in the gauge: coordinates 2i + a carry dot(t, K_i) on row a, coordinates 16 + a carry dot(t, v)
        lab = {}
        for t in e.oth:
            co = [dt(t, c) for c in KALL]
            ev = (1 + sum(co)) % 2
            for D in (e.U, e.W):
                for a in range(2):
                    for c, v in D[t][a].items():
                        lab[v] = (bool(co[c // 2]) and c % 2 == a) if c < 16 else (bool(ev) and c - 16 == a)
        bad = e.evaluate(lab)
        req(not bad, 'full_r18: the Gram representation tensor I_2 (rank 18) satisfies the full formula (all %d clauses)' % len(e.cl))
        key = next(iter(lab))
        lab[key] = not lab[key]
        bad = e.evaluate(lab)
        req(len(bad) > 0, 'control: flipping one label bit of that representation falsifies %d clauses' % len(bad))
    del e

pr = res['proof']
with lzma.open(os.path.join(DATA, 'full_k2_rank17_f2.drat.xz'), 'rb') as f:
    raw = f.read()
req(len(raw) == pr['uncompressed_bytes'] and hashlib.sha256(raw).hexdigest() == pr['uncompressed_sha256'],
    'full_r17: the shipped proof decompresses to %d bytes with the recorded sha256; its drat-trim verification against the formula with sha256 %s... is a recorded external run' % (len(raw), sha['full_r17'][:12]))
req(raw[:1] in (b'a', b'd'), 'proof file begins with a binary DRAT lemma marker')
req(math.ceil(53 * 2 / 6) == 18 and inst['full_r17']['kissat_4_0_4'] == 'UNSAT' and inst['full_r16']['kissat_4_0_4'] == 'UNSAT',
    'consistency: Theorem 3 gives rank >= ceil(53 * 2 / 6) = 18 at k = 2 over every field, and the F_2 formula at rank 16 and 17 is recorded UNSAT')
req(inst['sub14_r17']['kissat_4_0_4'] == 'SAT' and inst['sub14_r16']['kissat_4_0_4'] == 'UNSAT' and inst['full_r18']['kissat_4_0_4'] == 'SAT',
    'recorded controls: the 14-port formula is SAT at 17 and UNSAT at 16; the full formula is SAT at 18')
finish('PASS_SAT')
