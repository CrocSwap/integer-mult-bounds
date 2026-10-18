#!/usr/bin/env python3
"""Replay every census-legal fifth exchange through the repository builder and price the survivors.

python3 -I -B oracle_filter.py --root REPO --census RESULTS.json --out ORACLE.json

Independent cross-check of census.py. Each census-legal candidate is rebuilt as an X4 recipe
extension and passed to build_jx.build. The script records the builder's verdict, checks each
accepted profile against the census profile, and prices each distinct accepted profile with the
repository pricer. Expected: every legal candidate accepted, zero profile mismatches. Apache-2.0.
"""
import argparse
import json
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import census as C  # noqa: E402
import jx5  # noqa: E402

KAPPA_X4 = Q('1661634653669567/1000000000000000000')


def run(root, census_out):
    sw4 = C.load_word_file(root / jx5.REL['sw4_word'], jx5.PINS['sw4_content'])
    rc = json.loads((root / jx5.REL['recipe_x4']).read_text())
    oracle = jx5.load_build_jx(root)
    pairs = {p['h']: p for p in jx5.domain(sw4)[0]}
    legal = json.loads(Path(census_out).read_text())['legal_candidates']
    acc, rej, mismatch = {}, {}, 0
    for r in legal:
        (ha, hb, s1, s2), mask = r['c'], r['mask']
        e1 = jx5.pair_edits(sw4, pairs[ha], s1)[0]
        e2 = jx5.pair_edits(sw4, pairs[hb], s2)[0]
        moved = sorted(x['i'] for x in e1['replace'] + e2['replace'])
        rc2 = json.loads(json.dumps(rc))
        rc2['edits'] = jx5.merge(rc['edits'], e1, e2)
        rc2['raises'] = rc['raises'] + [[moved[j], list(sw4['B'][moved[j]][-1])]
                                        for j in range(len(moved)) if mask >> j & 1]
        try:
            p = oracle.build(sw4, rc2)['report']['local_profile']
        except oracle.Reject as e:
            rej[e.args[0][0]] = rej.get(e.args[0][0], 0) + 1
            continue
        k = json.dumps(p, sort_keys=True)
        acc[k] = acc.get(k, 0) + 1
        mismatch += p != r['profile']
    tmp = Path(tempfile.mkdtemp(prefix='x5o-'))
    kappa = {k: Q(jx5.price(root, json.loads(k), tmp, 'o%d' % i)['kappa']) for i, k in enumerate(acc)}
    best = max(kappa.values()) if kappa else None
    return dict(input=len(legal), oracle_accepted=sum(acc.values()), oracle_rejected=rej,
                profile_mismatch=mismatch, distinct=len(acc),
                baseline_kappa=str(KAPPA_X4),
                best_kappa=str(best) if best is not None else None,
                best_float=float(best) if best is not None else None,
                improving=sum(acc[k] for k in kappa if kappa[k] > KAPPA_X4),
                equal=sum(acc[k] for k in kappa if kappa[k] == KAPPA_X4))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default=str(HERE.parent.parent))
    ap.add_argument('--census', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    r = run(Path(a.root).resolve(), a.census)
    Path(a.out).write_text(json.dumps(r, indent=1) + '\n')
    print(json.dumps(r, indent=1))


if __name__ == '__main__':
    main()
