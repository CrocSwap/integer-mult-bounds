#!/usr/bin/env python3
"""Bounded replay: rebuild PR2530's derivative, substitute the repacked fill, reconstruct it literally, and check the claim bindings.
Rejecting controls on the fill (missing role, out-of-window role, duplicated family) must fail reconstruct.py.
The full native/global/outer replay is full_replay.py."""
import copy, subprocess, sys, tempfile
from fractions import Fraction as Q
from pathlib import Path
from build import HERE, ROOT, build, read, write, need, sha


def verify(work):
    p = build(work / 'build'); rejected = []
    need(read(work / 'build/repack-owners/PROFILE.json') == read(HERE / 'PROFILE.json'), 'exact global profile of the repacked fill')
    fillpath = p / 'new/borrow-fill/FILL.json.gz'; fill = read(fillpath)
    windows = read(work / 'build/repack-parent-data/PLAN.json')['windows']
    for label in ['missing-role', 'outside-window', 'duplicate-family']:
        bad = copy.deepcopy(fill)
        if label == 'missing-role':
            bad['rows'].pop()
        elif label == 'outside-window':
            row = bad['rows'][0]; allowed = windows[f'{row[2]},{row[3]}'][1]; row[0] = next(t for t in range(666) if t not in allowed)
        else:
            a, b = next((a, b) for a, b in zip(bad['rows'], bad['rows'][1:]) if a[0] == b[0]); b[2:] = a[2:]
        write(fillpath, bad); out = work / ('bad-' + label)
        r = subprocess.run([sys.executable, '-B', str(p / 'reconstruct.py'), '--out', str(out)], capture_output=True, text=True)
        need(r.returncode != 0, 'accepted physical mutation ' + label); rejected.append(dict(control=label, reason=r.stderr[-300:]))
    write(fillpath, fill)
    claim = read(HERE / 'CLAIM.json'); ledger = read(HERE / 'evidence/OUTER-LEDGER.json'); leader = read(ROOT / 'research/source-partner-lifetimes/CLAIM.json')
    k = Q(claim['kappa'])
    need(k == Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational']), 'exact outer claim binding')
    need(k > Q(leader['kappa']) and k - Q(leader['kappa']) == Q(claim['gain_over_pr2530']), 'comparison with PR2530')
    need(ledger['profile'] == read(HERE / 'PROFILE.json') and ledger['W'] == 66304, 'outer profile binding')
    need(sum(int(r) * n for r, n in ledger['profile'].items()) == 73 * 66304 - 23680, 'rank mass')
    need(Q(claim['complex_lower']) == Q(read(HERE / 'evidence/OUTER-B.json')['b_above_endpoint']) - Q(1, 10 ** 24), 'endpoint binding')
    need(len(rejected) == 3, 'rejecting controls')
    receipt = dict(status='PASS_SOURCE_PARTNER_REPACK_LITERAL_OWNERS', roles=len(fill['rows']), controls_rejected=rejected,
                   scope='Literal physical owners of the repacked fill and claim bindings; full native/global/outer replay is full_replay.py.')
    write(work / 'RESULT.json', receipt); print(receipt['status'], flush=True)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path); a = ap.parse_args()
    if a.work:
        a.work.mkdir(parents=True, exist_ok=False); verify(a.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='source-partner-repack-') as tmp:
            verify(Path(tmp))
