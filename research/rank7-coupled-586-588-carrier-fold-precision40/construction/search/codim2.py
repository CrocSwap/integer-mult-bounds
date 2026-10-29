"""codim2.py -- exact census of rank-7 (codimension-2) paired extractions for FRESH helpers (9->7).
For every 7-dim subspace V of F2^9 (43,435 = triples {n1<n2<n3=n1^n2} of normals): R_V = registers (live, non-target, non-restored)
whose terminal frame lies in V (mode 'lower': solver lower bound of the terminal frame; mode 'literal': literal terminal frame).
Exact implication used for pruning: the admissible pairing at V is a restriction of the pairing at each hyperplane E_ni containing V,
so prank(V) > 0 requires prank(E_n1), prank(E_n2), prank(E_n3) > 0.  For those V the exact pairing rank on R_V is computed.
usage: python -B codim2.py WORD.json.gz OUT.json [lower|literal] [V-basis-to-report e.g. 256,128,66,36,22,8,1]"""
import sys, json, time, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
from lower import per_normal_R, terminal_lower

def main():
    wp, op = sys.argv[1], sys.argv[2]; mode = sys.argv[3] if len(sys.argv) > 3 else 'lower'
    probe = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    t0 = time.time(); w = load(wp); fr = frames(w); sp = CE.spaces(w, fr=fr); H = sp['H']
    tl, g, al = terminal_lower(w)
    term = tl if mode == 'lower' else {r: fr['terminal'][r] for r in tl}
    restored = set(map(int, w['helper_final']))
    regs = [r for r in live_regs(w) if r not in restored]
    idx = {r: i for i, r in enumerate(regs)}
    Rbits = {}
    for n in range(1, 512):
        b = 0
        for r in regs:
            if all(((x & n).bit_count() & 1) == 0 for x in term[r]): b |= 1 << idx[r]
        Rbits[n] = b
    unbits = lambda b: [regs[i] for i in range(len(regs)) if b >> i & 1]
    hyper = {}
    for n in range(1, 512):
        key = Rbits[n]
        if key not in hyper: hyper[key] = per_normal_R(w, sp, n, unbits(key))['prank']
    prank_n = {n: hyper[Rbits[n]] for n in range(1, 512)}
    live_normals = sorted(n for n in prank_n if prank_n[n] > 0)
    nV = 0; cand = []
    for n1 in range(1, 512):
        for n2 in range(n1 + 1, 512):
            n3 = n1 ^ n2
            if n3 <= n2: continue
            nV += 1
            if prank_n[n1] and prank_n[n2] and prank_n[n3]: cand.append((n1, n2, n3))
    out = dict(word=wp, mode=mode, subspaces=nV, normals_with_pairing=live_normals, triples_all_three_nonzero=len(cand), V=[])
    seen = {}
    for (n1, n2, n3) in cand:
        b = Rbits[n1] & Rbits[n2]; R = unbits(b)
        if b not in seen: seen[b] = per_normal_R(w, sp, n1, R)
        res = seen[b]
        Vb = list(PM.basis([z for z in range(1, 512) if ((z & n1).bit_count() & 1) == 0 and ((z & n2).bit_count() & 1) == 0]))
        piv = sorted(H & set(R))
        out['V'].append(dict(normals=[n1, n2, n3], V=Vb, R=R, pivots=piv, dimA=res['dimA'], dimB=res['dimB'], prank=res['prank'],
                             alphas=[{str(k): str(v) for k, v in a.items()} for a in res['alphas']] if res['prank'] else [],
                             ys=[{str(k): str(v) for k, v in y.items()} for y in res['ys']] if res['prank'] else []))
        print(f'V {n1},{n2},{n3} basis {Vb}: |R_V|={len(R)} pivots={len(piv)} dimA={res["dimA"]} dimB={res["dimB"]} prank={res["prank"]}', flush=True)
    if probe is not None:
        P = PM.basis(probe); R = [r for r in regs if PM.contained(term[r], P)]
        res = per_normal_R(w, sp, 1, R)
        out['probe'] = dict(V=list(P), R=R, R_with_restored=[r for r in live_regs(w) if PM.contained(term[r], P)], dimA=res['dimA'], dimB=res['dimB'], prank=res['prank'], H_size=len(H))
        print('PROBE', out['probe'], flush=True)
    out['seconds'] = round(time.time() - t0, 1)
    print(f'{mode}: {nV} subspaces; normals with nonzero pairing {live_normals}; V with all three containing normals nonzero: {len(cand)}; '
          f'V with nonzero pairing: {sum(1 for v in out["V"] if v["prank"])} ({out["seconds"]}s)', flush=True)
    json.dump(out, open(op, 'w'), indent=0)

if __name__ == '__main__': main()
