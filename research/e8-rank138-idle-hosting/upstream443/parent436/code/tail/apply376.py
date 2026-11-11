"""Our own re-implementation (from the data semantics in PR376's PROOF.md) of applying PR376's frozen frame witness
and helper-reuse witness to PR370's E8 bit word. Does not import or run PR376 code.
usage: apply376.py SRC370.json.gz FRAMESEL.json REUSESEL.json OUT.json.gz"""
import sys, os, json, gzip, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import save_word

def canon(c): return json.dumps(c, sort_keys=True, separators=(',', ':')).encode()

def apply_frames(c, sel):
    w = json.loads(json.dumps(c)); pos = []
    for ph in ('D', 'A', 'B', 'C'):
        w[ph] = [[f, d, [s]] for f, d, ss in c[ph] for s in ss]
        pos += [(ph, i) for i in range(len(w[ph]))]
    for e in sel['entries']:
        ph, i = pos[e['scalar_index']]
        assert ph == e['phase'] != 'D' and w[ph][i] == [e['old_frame'], e['dst'], [e['src']]]
        w[ph][i][0] = e['new_frame']
    return w

def apply_reuse(c, sel):
    v = c['v']; n = 2 * v + c['R']; nA = len(c['A']); ops = c['A'] + c['B']
    pairs = {p['at']: p for p in sel['pairs']}
    alias = {p['new']: p['old'] for p in sel['pairs']}
    for p in sel['pairs']:
        assert ops[p['at']][0] == p['frame'] and ops[p['at']][1] == p['new'] and p['at'] < nA
    keep = [r for r in range(n) if r not in alias]; idx = {r: i for i, r in enumerate(keep)}
    rm = lambda r: idx[alias.get(r, r)]
    new = []; split = None
    for i, (f, d, ss) in enumerate(ops):
        if i == nA: split = len(new)
        if i in pairs:
            p = pairs[i]; new.append([f, rm(p['old']), [rm(s) for s in p['sources']]])
        new.append([f, rm(d), [rm(s) for s in ss]])
    o = json.loads(json.dumps(c)); o['A'], o['B'] = new[:split], new[split:]
    o['R'] = c['R'] - len(alias)
    o['start'] = [c['start'][r] for r in keep]; o['final'] = [c['final'][r] for r in keep]
    o['ret'] = [rm(q) for q in c['ret']]
    full, zero = c['final'][0], c['start'][v]
    o['C'] = [[full, d, list(ss)] for _, d, ss in reversed(new) if d >= 2 * v]
    # target compensation from helper dirt (F2 symbolic over helper initial values)
    R = o['R']; dirt = [0] * (2 * v + R)
    for r in range(2 * v, 2 * v + R): dirt[r] = 1 << (r - 2 * v)
    for _, d, ss in o['A']:
        for s in ss: dirt[d] ^= dirt[s]
    cp = [dirt[q] for q in o['ret']]
    for t, row in enumerate(o['scatter']):
        for k in row: dirt[v + t] ^= cp[k]
    for _, d, ss in o['B']:
        for s in ss: dirt[d] ^= dirt[s]
    o['D'] = [[zero, v + t, [2 * v + j for j in range(R) if dirt[v + t] >> j & 1]] for t in range(v) if dirt[v + t]]
    return o

if __name__ == '__main__':
    raw = open(sys.argv[1], 'rb').read(); c = json.loads(gzip.decompress(raw))
    fs = json.load(open(sys.argv[2])); rs = json.load(open(sys.argv[3]))
    assert hashlib.sha256(raw).hexdigest() == fs['input_sha256']
    w1 = apply_frames(c, fs); assert hashlib.sha256(canon(w1)).hexdigest() == rs['retimed_input_sha256']
    w2 = apply_reuse(w1, rs); h = hashlib.sha256(canon(w2)).hexdigest(); assert h == rs['output_sha256'], h
    save_word(w2, sys.argv[4]); print('PASS our reconstruction of the PR376 word, sha', h)
