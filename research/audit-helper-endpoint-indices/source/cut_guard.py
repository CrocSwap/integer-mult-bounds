#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cut-source guard for local words checked by research/gauge44-frames-x/independent/audit_local.py.

audit_local.py climbs frames only in sections A and B; in the cut it checks only gates whose source is a centre
(the centre-path rule). A cut gate with any other source is applied to the scalar map but never frame-checked, so a
word can move priced work into the unpriced cut and still pass. This guard checks what every genuine word satisfies
and the native emitter (hpe_emit_local.py) relies on: every cut gate is an add whose source is one of the word's
eight centres and whose target is a target row (v <= t < 2v).

usage: python3 -B guard.py WORD.json.gz [--json OUT.json]   (exit 0 = PASS, 1 = violation)"""
import argparse, gzip, json, sys
from pathlib import Path


def violations(word):
    v = word['report']['v']; centres = set(word['centers'])
    out = []
    for i, e in enumerate(word['cut']):
        if not (e[0] == 'add' and e[2] in centres and v <= e[1] < 2 * v):
            out.append(dict(cut_index=i, gate=e[:5]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('word', type=Path); ap.add_argument('--json', type=Path)
    a = ap.parse_args()
    word = json.loads(gzip.decompress(a.word.read_bytes()))
    bad = violations(word)
    res = dict(status='PASS_CUT_SOURCES_ARE_CENTRES' if not bad else 'FAIL_NON_CENTRE_CUT_GATES',
               word=a.word.name, cut_gates=len(word['cut']), centres=sorted(word['centers']), violations=bad)
    if a.json: a.json.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    print(res['status'], a.word.name, 'cut', len(word['cut']), 'violations', len(bad), flush=True)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
