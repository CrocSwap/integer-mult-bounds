#!/usr/bin/env python3
"""One legal coalescing join, independently replayed; ywz65/Codex, Apache-2.0.

PR1868 supplies the scalar fixture; PR2428 supplies the least-frame question.
No predecessor executable is imported. Rational ranks have a modular cross-check.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
ORIGINAL = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(f):
    try:
        f()
    except ValueError:
        return
    raise ValueError('control accepted')


def rank(rows, prime=None):
    rows = [[int(x) % prime if prime else Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(8):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        div = pow(rows[pivot][col], -1, prime) if prime else 1 / rows[pivot][col]
        rows[pivot] = [(x * div) % prime if prime else x * div for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            c = rows[i][col]
            rows[i] = [(x-c*y) % prime if prime else x-c*y
                       for x,y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


class Geometry:
    def __init__(self, word):
        self.word = word
        self.masks = [sum(1 << x for x in f) for f in word['frames']]

    @lru_cache(maxsize=None)
    def dimension(self, mask):
        rows = [row for i,row in enumerate(self.word['lines']) if mask >> i & 1]
        q = rank(rows)
        need(q == rank(rows, 1000003), 'rational/modular rank mismatch')
        return q

    def contains(self, outer, inner):
        return self.dimension(outer | inner) == self.dimension(outer)

    def walk(self, word, floor=None):
        cur = [self.masks[f] for f in word['start']]
        profile, climbs, cuts, copies = Counter(), [], {}, []
        for sec in 'DABC':
            for j,(fr,d,ss) in enumerate(word[sec]):
                frame = 0
                for r in (d,*ss):
                    frame |= cur[r]
                if floor == 'original' or floor == (sec,j):
                    frame |= self.masks[fr]
                if floor == 'invalid' and (sec,j) == ('B',0):
                    frame = self.masks[1]
                if sec == 'A' and j in (591,592,595,596,599):
                    cuts[j] = {'gate_frame_labels':[i for i in range(len(word['lines'])) if frame >> i & 1],
                               'rank':self.dimension(frame)}
                for r in (d,*ss):
                    need(self.contains(frame,cur[r]), 'frame descent')
                    before,after = self.dimension(cur[r]),self.dimension(frame)
                    if after > before:
                        profile[after-before] += 1
                        climbs.append([sec,j,r,before,after])
                    cur[r] = frame
            if sec == 'A':
                copies = [cur[r] for r in word['ret']]
                profile.update(self.dimension(f) for f in copies)
        for r,fr in enumerate(word['final']):
            final = self.masks[fr]
            need(self.contains(final,cur[r]), 'final leakage')
            before,after = self.dimension(cur[r]),self.dimension(final)
            if after > before:
                profile[after-before] += 1
                climbs.append(['final',0,r,before,after])
        return dict(sorted(profile.items())),climbs,copies,cuts


def scalar(word):
    n,v = len(word['start']),word['v']
    ops = [(0,d,s) for sec in 'DA' for _,d,ss in word[sec] for s in ss]
    for j,r in enumerate(word['ret']):
        ops.append((1,n,r))
        ops.extend((0,v+t,n) for t,ss in enumerate(word['scatter']) if j in ss)
        ops.append((2,n,r))
    ops.extend((0,d,s) for sec in 'BC' for _,d,ss in word[sec] for s in ss)
    expected = [(1 << r) ^ ((1 << (r-v)) if v <= r < 2*v else 0) for r in range(n)] + [0]
    for reverse in (False,True):
        state = [1 << r for r in range(n)] + [0]
        for op,d,s in reversed(ops) if reverse else ops:
            op = 3-op if reverse and op else op
            if op == 0:
                state[d] ^= state[s]
            elif op == 1:
                need(state[d] == 0,'dirty COPY temporary')
                state[d] = state[s]
            else:
                need(state[d] == state[s],'invalid ERASE')
                state[d] = 0
        need(state == expected,'dirty scalar endpoint')
    return sum(op == 0 for op,_,_ in ops)


def sources():
    records = [(ROOT / r['path'],r) for r in json.loads((HERE/'SOURCES.json').read_text())['files']]
    r = json.loads((HERE/'PREDECESSOR.json').read_text())
    records.append((HERE/r['local_path'],r))
    for p,r in records:
        b = p.read_bytes()
        need(hashlib.sha256(b).hexdigest() == r['sha256'],'source SHA: '+str(p))
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == r['git_blob'],
             'source blob: '+str(p))
    return json.loads(gzip.decompress((ROOT/WORD).read_bytes()))


def run():
    w = sources()
    need(scalar(w) == 11500,'source scalar bill')
    g = Geometry(w)
    original = g.walk(w,'original')
    need(original[0] == ORIGINAL,'source frame profile')
    fixture = copy.deepcopy(w)
    matching = [i for i,gate in enumerate(fixture['D']) if gate == [0,506,[374]]]
    need(matching, 'terminal restoration present')
    fixture['D'].pop(matching[-1])
    need(fixture['A'][288][2] == [374],'fixture source gate')
    fixture['A'][288][2] = [69]
    need(scalar(fixture) == 11499,'fixture scalar bill')
    least = g.walk(fixture)
    raised = g.walk(fixture,('A',591))
    need(fixture['A'][591] == [266,243,[244]],'chosen gate')
    for a,b,c in zip(least[2],raised[2],original[2]):
        need(g.contains(a,b) and g.contains(b,a) and g.contains(a,c) and g.contains(c,a),
             'COPY frame changed')
        need(g.dimension(a) == 7,'COPY rank')
    delta = {r:raised[0].get(r,0)-least[0].get(r,0) for r in range(1,9)}
    need(delta == {1:-4,2:-1,3:2,4:0,5:0,6:0,7:0,8:0},'coalescing delta')
    need(sum(r*n for r,n in least[0].items()) == sum(r*n for r,n in raised[0].items()) == 5129,
         'rank mass')
    damaged = copy.deepcopy(fixture); damaged['A'][288][2] = [374]
    reject(lambda: scalar(damaged))
    reject(lambda: g.walk(fixture,'invalid'))
    reject(lambda: need(least[0] == raised[0],'missing raised join'))
    reject(lambda: need(g.contains(least[2][0],g.masks[1]),'COPY full-frame mutant'))
    return {'status':'PASS_R439_COALESCED_LEGAL_JOIN','fixture_ADDs':11499,
            'dirty_columns':661,'override':['A',591],'original_gate':[266,243,[244]],
            'least_profile':least[0],'raised_profile':raised[0],'rank_mass':5129,
            'COPY_ranks':[g.dimension(x) for x in raised[2]],
            'removed_climbs':[r for r in least[1] if r not in raised[1]],
            'added_climbs':[r for r in raised[1] if r not in least[1]],
            'least_cuts':least[3],'raised_cuts':raised[3],
            'semantic_controls':4,
            'cost_saving':'4 + 2^p - 2*3^p > 0 for 0<p<1; two (2,1)->3 merges and one (1,1)->2 merge',
            'scope':'One word-level legal reframing, not an optimum, native admission or new kappa.'}


if __name__ == '__main__':
    result = run()
    result = json.loads(json.dumps(result))
    path = HERE/'RESULT.json'
    if sys.argv[1:] == ['--write-receipt']:
        need(not path.exists(),'refuse receipt overwrite')
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        need(not sys.argv[1:],'unknown argument')
        need(json.loads(path.read_text()) == result,'receipt mismatch')
    print(json.dumps(result,indent=2))
