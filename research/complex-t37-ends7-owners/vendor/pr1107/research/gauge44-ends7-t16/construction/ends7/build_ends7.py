#!/usr/bin/env python3
"""build_ends7.py BASE_WORD RECIPE OUT [--control NAME]
Rank-seven helper ends (after PR1030) on the seven-slot k8 word: every listed helper end drops by one dimension to the
recorded subspace; the recorded B frames and early-cleanup (tail) frames drop with it. Each edit is literal (old -> new,
old checked), each new frame is a codimension-one subspace of the old one, and the input and output contents are pinned.
Controls (negative, for end7_controls.py): end_restored, wrong_frame, cone_violation. Standard library only."""
import argparse, gzip, hashlib, json, sys


def enc(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def span(vs):
    s = {0}
    for v in vs:
        assert type(v) is int and 0 < v < 512, 'GF(2)^9 vector'
        s |= {x ^ v for x in s}
    assert len(s) == 1 << len(vs), 'dependent frame basis'
    return frozenset(s)


def codim1(old, new):
    a, b = span(old), span(new)
    assert b < a and len(a) == 2 * len(b), 'not a codimension-one lowering'


def build(word, rec, control=None):
    assert rec['schema'] == 1
    assert hashlib.sha256(enc(word)).hexdigest() == rec['input_sha256'], 'base word content pin'
    for q, old, new in rec['ends']:
        assert word['helper_final'][str(q)] == old, 'old end %d' % q
        codim1(old, new); word['helper_final'][str(q)] = new
    for sec, i, old, new in rec['frames']:
        assert sec in ('A', 'B') and word[sec][i][-1] == old, 'old %s frame %d' % (sec, i)
        codim1(old, new); word[sec][i][-1] = new
    for j, ci, old, new in rec['early_cleanup']:
        assert word['early_cleanup'][j] == [ci, old], 'old tail %d' % j
        codim1(old, new); word['early_cleanup'][j][1] = new
    for k in ('local_profile', 'local_rank_mass', 'width_inventory'):
        word['report'][k] = rec['expected'][k]
    if control is None:
        assert hashlib.sha256(enc(word)).hexdigest() == rec['expected']['output_sha256'], 'output content pin'
        return word
    c = rec['controls'][control]
    if control == 'end_restored':        # the end goes back to dimension eight; frames and accounting stay lowered
        q, old, new = next(e for e in rec['ends'] if e[0] == c['helper'])
        word['helper_final'][str(q)] = old
    elif control == 'wrong_frame':       # one lowered B frame replaced by a different codimension-one subspace
        sec, i, old, new = next(f for f in rec['frames'] if [f[0], f[1]] == c['frame'])
        codim1(old, c['wrong']); word[sec][i][-1] = c['wrong']
    elif control == 'cone_violation':    # helper end and its own chain lowered to a subspace that misses the cone
        q = c['helper']; word['helper_final'][str(q)] = c['end']
        for sec, i, fr in c['own_frames']:
            if sec == 'T': word['early_cleanup'][i][1] = fr
            else: word[sec][i][-1] = fr
    else:
        raise SystemExit('unknown control ' + control)
    return word


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base'); ap.add_argument('recipe'); ap.add_argument('out'); ap.add_argument('--control')
    a = ap.parse_args()
    word = json.loads(gzip.decompress(open(a.base, 'rb').read()))
    rec = json.load(open(a.recipe))
    w = build(word, rec, a.control)
    raw = enc(w); gz = gzip.compress(raw, 9, mtime=0); gz = gz[:9] + b'\xff' + gz[10:]
    open(a.out, 'wb').write(gz)
    print(json.dumps(dict(status='PASS_RANK7_ENDS_BUILT' if a.control is None else 'CONTROL_BUILT', control=a.control,
                          content_sha256=hashlib.sha256(raw).hexdigest(), ends=len(rec['ends']), frames=len(rec['frames']),
                          tails=len(rec['early_cleanup']))))


if __name__ == '__main__':
    main()
