#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exhaustive width-neutral local sweeps on the final X54 mixed-T37 words, using #1186's toolkit unchanged.

Families (each candidate priced by the toolkit's exact frame solver; negative delta = gain):
  repair    every read fusion (`fusion.candidates`) with single/pair swap repairs and full read-set exchanges
            (`repair.py`, unchanged, default options);
  exchange  every subset of swappable post-copy reads of every copy pair (BRoute's SW4 read-set exchange);
  joint     joint triangle-hybrid candidates with up to three fused reads, partial swaps and both restore modes.

The toolkit is not on main: pass `--toolkit` pointing at research/exact-frame-toolkit from PR #1186 head
9254a3cc610a72e9c4600da089d5cdbcab996b9c (its paths.py must see a checkout containing the retained engines).
Output is nomination data only; a gain would still need native and strict owner admission.

usage: python -B sweep.py --toolkit DIR --word D3|D4 --out OUT_DIR [--workers 6] [--families repair,exchange,joint]
"""
import argparse, gzip, itertools, json, os, subprocess, sys, time
from pathlib import Path

PKG = Path(__file__).resolve().parent
WORDS = {'D3': PKG / 'inputs/D3-WORD.json.gz', 'D4': PKG / 'inputs/D4-WORD.json.gz'}


def summarize_repair(rows):
    out = []
    for r in rows:
        b = r.get('best')
        out.append(dict(t=r['t'], A=r['A'], H=r['H'], p=r['p'], rest=r['rest'], tried=r['tried'], nrepairs=r['nrepairs'],
                        best=None if not b else dict(delta=b['delta'], steps=b['steps'], profile=b['profile'])))
    return out


def exchange_sweep(C, X, J, word):
    P = C.Pricer(str(word)); w = P.base; out = []
    for h, (r, ic) in X.copy_pairs(w).items():
        M = X.movable_reads(w, h, r, ic)
        if not M:
            continue
        sw = [(m, J.swap_edit(w, h, r, ic, m)) for m in M]
        sw = [(m, s) for m, s in sw if s]
        for k in range(1, len(sw) + 1):
            for sub in itertools.combinations(sw, k):
                ed = J.merge([s for _, s in sub])
                res = dict(status='overlap') if ed is None else P.price(ed, timeout=120)
                out.append(dict(h=h, r=r, swapped=[m[0] for m, _ in sub], status=res.get('status'), delta=res.get('delta'),
                                profile=res.get('profile')))
    return out


def joint_sweep(C, J, word):
    P = C.Pricer(str(word)); out = []
    for c in J.candidates(P.base, max_fused=3, allow_partial=True, restores=('canon', 'after')):
        res = P.price(c['ed'], timeout=120)
        out.append(dict(h=c['h'], r=c['r'], fused=c['fused'], swapped=c['swapped'], status=res.get('status'),
                        delta=res.get('delta'), profile=res.get('profile')))
    return out


def tally(rows, key=lambda r: r.get('delta')):
    deltas = [key(r) for r in rows]
    ok = [d for d in deltas if d is not None]
    return dict(candidates=len(rows), feasible=len(ok), gains=sum(d < 0 for d in ok), best_delta=min(ok) if ok else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--toolkit', type=Path, required=True)
    ap.add_argument('--word', choices=sorted(WORDS), required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--families', default='repair,exchange,joint')
    a = ap.parse_args()
    tk = a.toolkit.resolve(); word = WORDS[a.word]; a.out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(tk))
    import harness as C, exchange as X, joint as J
    summary = dict(word=a.word, toolkit=str(tk))
    fams = a.families.split(',')
    if 'repair' in fams:
        raw = a.out / f'repair-{a.word}.raw.json'; t0 = time.time()
        subprocess.run([sys.executable, '-B', str(tk / 'repair.py'), str(word), str(raw), '--workers', str(a.workers)], cwd=tk, check=True)
        rows = summarize_repair(json.load(open(raw)))
        json.dump(rows, gzip.open(a.out / f'REPAIR-{a.word}.json.gz', 'wt'), sort_keys=True)
        summary['repair'] = dict(tally(rows, key=lambda r: r['best']['delta'] if r['best'] else None), seconds=round(time.time() - t0))
    if 'exchange' in fams:
        rows = exchange_sweep(C, X, J, word)
        json.dump(rows, gzip.open(a.out / f'EXCHANGE-{a.word}.json.gz', 'wt'), sort_keys=True)
        summary['exchange'] = tally(rows)
    if 'joint' in fams:
        rows = joint_sweep(C, J, word)
        json.dump(rows, gzip.open(a.out / f'JOINT-{a.word}.json.gz', 'wt'), sort_keys=True)
        summary['joint'] = tally(rows)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
