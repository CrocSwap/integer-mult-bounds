#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Read-only check of the #1015 retention receipt against files in this checkout (no network).

1. main's research/r439-bsection-stars-seed01/inputs/PR1015-CANDIDATE.json has the git blob id of
   research/r439-bsection-multwrite/CANDIDATE.json at open #1015's head 7588c797 (pinned below);
2. NOTICE-PR1015.md here is #1015's NOTICE.md at that head, byte for byte (pinned blob id);
3. #1062's saving splits as PR1015 244 + PR923 24 + rerun star pass 15 = 283 ADDs, recomputed from
   research/r439-bsection-stars-seed01/CERTIFICATE.json (gate deltas count twice: block plus literal cleanup);
4. CONTRIBUTORS.md carries the #1015 credit line added with this receipt; the ledger's missing #1015 row is asserted
   only while docs/research/pr-ledger.json is still the base blob, and otherwise reported.
Two negative controls must fail: a block misattributed to PR923, and a one-byte change to the retained file.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEIPT = json.loads((HERE / 'RECEIPT.json').read_text())


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


def blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def attribution(cert):
    per = {}
    for b in cert['blocks']:
        per[b['source']] = per.get(b['source'], 0) + 2 * (b['original_gates'] - b['new_gates'])
    words = {k: v['literal']['native_ADDs'] for k, v in cert['words'].items()}
    return dict(per_source=per, star_rerun=words['composition'] - words['candidate'],
                total=words['helper_star'] - words['candidate'], words=words)


def check(cert, retained, notice):
    r = RECEIPT
    need(blob(retained) == r['retained_file']['pr1015_head_blob'], 'retained file is not #1015 CANDIDATE.json at its head')
    need(blob(notice) == r['pr1015_notice']['blob'], 'NOTICE-PR1015.md differs from #1015 NOTICE.md')
    a = attribution(cert)
    want = r['pr1062_saving']
    need(a['per_source'] == want['per_source'] and a['star_rerun'] == want['star_rerun'] and a['total'] == want['total'],
         'saving attribution %s' % a)
    need(sum(a['per_source'].values()) + a['star_rerun'] == a['total'], 'saving does not add up')
    return a


def main():
    cert = json.loads((ROOT / 'research/r439-bsection-stars-seed01/CERTIFICATE.json').read_text())
    retained = (ROOT / RECEIPT['retained_file']['path']).read_bytes()
    notice = (HERE / 'NOTICE-PR1015.md').read_bytes()
    a = check(cert, retained, notice)
    raw = (ROOT / 'docs/research/pr-ledger.json').read_bytes()
    numbers = {row['number'] for row in json.loads(raw)['pull_requests']}
    need(1062 in numbers, 'ledger row for #1062')
    if blob(raw) == RECEIPT['ledger_blob_at_base']:     # the recorded gap holds only for the base ledger
        need(1015 not in numbers, 'base ledger unexpectedly has a #1015 row')
        ledger = 'base ledger: #1015 row absent (gap recorded)'
    else:
        ledger = 'ledger changed since base: #1015 row %s' % ('present' if 1015 in numbers else 'still absent')
    contributors = (ROOT / 'CONTRIBUTORS.md').read_text()
    need(RECEIPT['contributors_line'] in contributors, 'CONTRIBUTORS.md lacks the #1015 credit line')
    controls = []
    bad = copy.deepcopy(cert)
    next(b for b in bad['blocks'] if b['source'] == 'PR1015')['source'] = 'PR923'
    try:
        check(bad, retained, notice)
    except SystemExit:
        controls.append('misattributed block rejected')
    try:
        check(cert, retained[:-1] + bytes([retained[-1] ^ 1]), notice)
    except SystemExit:
        controls.append('modified retained file rejected')
    need(len(controls) == 2, 'negative controls: %s' % controls)
    print(ledger)
    print('PASS_R439_PR1015_RETENTION blob=%s saving=PR1015:%d+PR923:%d+star%d=%d controls=%d' % (
        RECEIPT['retained_file']['pr1015_head_blob'][:8], a['per_source']['PR1015'], a['per_source']['PR923'],
        a['star_rerun'], a['total'], len(controls)))


if __name__ == '__main__':
    main()
