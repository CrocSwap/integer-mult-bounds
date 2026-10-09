#!/usr/bin/env python3
"""Bind exact power comparisons to four pinned local and complete profiles.

No compiler replay or numerical real arithmetic is needed here. Run after
incremental_audit.py. This independently checks every complete child row,
including unchanged exterior/data contributions, rather than presuming that
the changes to the two local profiles are the complete change.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = {
    64: ('790a14e28e935398072b9a9a68694ce7fba8940f',
         'research/ranked-pair-verification/selected-certificate.json', 'bit',
         'research/ranked-pair-verification/finite-frames/pair-ranked-{}-receipt.json', 'profile'),
    65: ('49e84f939d15b618b50714eb039cabf97c74256a',
         'research/reordered-rank-pair/paired-candidate.json', 'bit',
         'research/reordered-rank-pair/frame-profiles-{}.json', None),
    67: ('b3745601e947a94316bf25c2c6263d93c06e3364',
         'research/slot-cost-rank-pair/paired-candidate.json', 'bit',
         'research/slot-cost-rank-pair/frame-profiles-{}.json', None),
    68: ('734c58e225e9d2254570c3b50296ed96943f62ea',
         'research/global-anchor-screen/selected-arithmetic.json', 'profile',
         'research/global-anchor-screen/selected-profiles-{}.json', None),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    args = ap.parse_args()
    whole, local, inputs = {}, {}, {}
    for n, (pin, path, field, template, axisfield) in SOURCES.items():
        def read(source):
            raw = subprocess.check_output(['git', '-C', str(args.repo), 'show', pin+':'+source])
            return json.loads(raw), hashlib.sha256(raw).hexdigest()
        cert, digest = read(path)
        profile = cert[field]
        assert (profile['m'], profile['W']) == (575, 137151806)
        whole[n] = {int(t): c for t, c in profile['child_multiplicities'].items()}
        assert sum(t*c for t, c in whole[n].items()) == 78860441550
        local[n] = {}
        axes = []
        for h in (23, 25):
            axis, axisdigest = read(template.format(h))
            if axisfield:
                axis = axis[axisfield]
            local[n][h] = axis['blocks']
            assert axis['rank_sum'] == {23: 642620, 25: 915250}[h]
            axes.append(dict(h=h, path=template.format(h), sha256=axisdigest,
                             extraction=axisfield or 'entire object', blocks=axis['blocks']))
        inputs[n] = dict(pin=pin, url=f'https://github.com/CrocSwap/integer-mult-bounds/pull/{n}',
                         full_profile_path=path, full_profile_sha256=digest, extraction=field,
                         child_multiplicities=whole[n], axes=axes)
    result = json.loads((HERE/'power-dominance.json').read_text())
    for row in result['comparisons']:
        n, old = row['new'], row['old']
        d = {t: whole[n].get(t, 0)-whole[old].get(t, 0)
             for t in set(whole[n]) | set(whole[old])}
        d = {t: c for t, c in d.items() if c}
        assert d == {int(t): c for t, c in row['signed_multiplicities'].items()}
        assert all(1 <= t <= 25 for t in d)
        for t in range(1, 26):
            expected = sum(rep*((local[n][h][t] if t < len(local[n][h]) else 0)
                               -(local[old][h][t] if t < len(local[old][h]) else 0))
                           for h, rep in ((23, 2300), (25, 1771)))
            assert d.get(t, 0) == expected
        caps = {k: sum(c*min(t, k) for t, c in d.items()) for k in range(1, 26)}
        assert caps == {int(k): c for k, c in row['capped_sums'].items()}
        prefix = {k: sum(caps[j] for j in range(1, k+1)) for k in range(1, 26)}
        assert prefix == {int(k): c for k, c in row['prefix_capped_sums'].items()}
        row['full_child_difference_matches_local_difference'] = True
        row['source_inputs'] = [n, old]
    result['finite_inputs'] = inputs
    result['binding'] = 'Every nonzero complete child-multiset difference equals the two local profile differences with replications 2300 and 1771. No unchanged-exterior assumption is needed for this comparison.'
    result['comparison_checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/'power-dominance.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS all five complete child-multiset comparisons, local profiles, exact cap prefixes, and pinned input hashes')

if __name__ == '__main__':
    main()
