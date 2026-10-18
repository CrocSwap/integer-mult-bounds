#!/usr/bin/env python3
"""Entry point: independent audit of PR #2802's seven-stage increment over PR #2751 (retired5 + retired7 stages),
verdict extended to PR #2818.

Runs the 28 named rules of increment_audit.py on the pinned inputs, then the 20 negative controls of
increment_controls.py (each must be rejected by its named rule, and some must also be accepted by named rules).
Inputs are git blobs at the pinned PR heads, checked against sha256 pins; --fetch downloads refs/pull/<n>/head only
for absent commits (FETCH_HEAD only).  An unreadable or mismatching input prints a FAIL line (exit 1).

Usage (repository root):  python3 -I -B research/t74-retired7-increment-audit/verify.py --fetch [--out RECEIPT.json]
Final line: PASS_T74_RETIRED7_INCREMENT_AUDIT rules=28/28 controls=20/20 ... or FAIL_T74_RETIRED7_INCREMENT_AUDIT ...
If this zlib does not reproduce #2802's pinned FILL.json.gz bytes, ATTRIBUTION-RETIRED5 compares the reconstructed
retired5 fill only through its pinned canonical-JSON sha256 (not with #2802's recorded gzip hash) and a NOTE line says so.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import increment_audit as A  # noqa: E402
import increment_controls as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(HERE)))
    ap.add_argument('--blob-dir', help='exported blobs laid out as DIR/<commit[:12]>/<repo path>')
    ap.add_argument('--fetch', action='store_true', help='fetch the pinned PR heads if absent (writes FETCH_HEAD only)')
    ap.add_argument('--out', help='write the deterministic receipt here')
    a = ap.parse_args()
    t0 = time.monotonic()
    if a.fetch and not a.blob_dir:
        A.fetch_missing(a.repo)
    try:
        js = A.load_all(a.repo, a.blob_dir)
    except (A.Fail, OSError, ValueError) as e:
        print('FAIL_T74_RETIRED7_INCREMENT_AUDIT inputs: %s' % e)
        return 1
    res = A.run_all(js)
    r5 = res['rules'].get('ATTRIBUTION-RETIRED5', {})
    if r5.get('ok') and r5['info'].get('fill_gzip_sha256_equals_recorded') is not True:
        print("NOTE: this zlib does not reproduce #2802's FILL.json.gz bytes; the retired5 fill was compared through its "
              "pinned canonical-JSON sha256 only, not with #2802's recorded gzip fill_sha256")
    ok_c, ctl = K.run(js)
    n_rules = len(res['rules'])
    n_pass = sum(1 for v in res['rules'].values() if v['ok'])
    n_ctl = sum(1 for v in ctl.values() if v['control_ok'])
    receipt = dict(
        status='PASS' if (res['ok'] and ok_c) else 'FAIL',
        commits=A.COMMIT, pins={k: dict(commit=A.COMMIT[v[0]], path=v[1], sha256=v[2]) for k, v in sorted(A.PINS.items())},
        claims_under_test=A.CLAIMED, rules=res['rules'], controls=ctl,
        scope=('Finite exact checks of the PR #2802 seven-stage increment (retired5 stages refit5/alias5/refit5c, retired7 '
               'stages refit7/hostmove2/alias7/refit7c) over the pinned PR #2751 words: event diff, per-register occupancy, '
               'warps/frames/profile, free-algebra and matrix replays, the 271728-role fill with word-derived R, complete '
               'profile/mass/root, PR #2818 identity, and attribution against PR #2766 and the recorded retired5 step. '
               'Inherited T74/#1319 admission, native lowering, outer proof and PR #2751 recovery are not checked.'))
    if a.out:
        with open(a.out, 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True, default=str)
            fh.write('\n')
    line = '%s rules=%d/%d controls=%d/%d commit2802=%s commit2818=%s' % (
        'PASS_T74_RETIRED7_INCREMENT_AUDIT' if receipt['status'] == 'PASS' else 'FAIL_T74_RETIRED7_INCREMENT_AUDIT',
        n_pass, n_rules, n_ctl, len(ctl), A.COMMIT['c2802'][:12], A.COMMIT['c2818'][:12])
    print('elapsed %.0fs' % (time.monotonic() - t0))
    print(line)
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
