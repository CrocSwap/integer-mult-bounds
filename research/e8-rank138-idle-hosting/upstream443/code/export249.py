"""Export a bitE8/1 word to PR249 snapshot format (249-records.bin, 249-states.json, frames.json) and stage it for
PR #266's official cohort checkers. Our own exporter (helpers may start at a kernel entrance E, sigma = dim E).
Records (int32 x 6): MOVE(0,role,old,new,rank,0), ADD(1,dst,src,1,frame,phase), COPY(2,centre,temp,frame,ZERO,rank),
ERASE(3,centre,temp,frame,ZERO,0). A gate with several sources: MOVE every participant to the gate frame, then one ADD
per source. Frames: B = integer label vectors of a basis among the frame's root lines; A = primitive integer
annihilator rows under the standard dot product (exact over Q).
usage: export249.py WORD.json.gz SNAPDIR COHORT_IN COHORT_OUT
Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0."""
import sys, os, json, struct, math, shutil
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import load_word, Lat, to_masks


def nullspace(B, h):
    M = [[Q(x) for x in r] for r in B]; piv = []; rk = 0
    for col in range(h):
        p = next((i for i in range(rk, len(M)) if M[i][col] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]; pv = M[rk][col]; M[rk] = [x / pv for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][col] != 0:
                f = M[i][col]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        piv.append(col); rk += 1
    A = []
    for fc in [x for x in range(h) if x not in piv]:
        a = [Q(0)] * h; a[fc] = Q(1)
        for i, pc in enumerate(piv): a[pc] = -M[i][fc]
        den = 1
        for x in a: den = den * x.denominator // math.gcd(den, x.denominator)
        ai = [int(x * den) for x in a]; g = 0
        for x in ai: g = math.gcd(g, abs(x))
        A.append([x // g for x in ai])
    return A


def export(c, out):
    os.makedirs(out, exist_ok=True)
    L = Lat(c['lines']); masks = to_masks(c, L); v, R, h = c['v'], c['R'], c['h']; n = 2 * v + R
    fid = {}; frames = {}
    for k, m in enumerate(masks):
        if m in fid: continue
        fid[m] = k; B = [list(L.lines[i]) for i in L.basis(m)]
        A = nullspace(B, h) if B else [[int(i == j) for j in range(h)] for i in range(h)]
        assert len(A) + len(B) == h and all(sum(x * y for x, y in zip(a, b)) == 0 for a in A for b in B)
        frames[str(k)] = dict(dim=len(B), B=B, A=A)
    F = lambda f: fid[masks[f]]
    ZERO = fid[0]; FULL = fid[(1 << v) - 1]
    dim = {int(a): b['dim'] for a, b in frames.items()}
    cur = [F(f) for f in c['start']]; rec = []
    def move(r, f):
        if cur[r] != f: rec.append((0, r, cur[r], f, dim[f] - dim[cur[r]], 0)); cur[r] = f
    def run(gates, ph):
        for f, d, srcs in gates:
            f = F(f)
            for r in [d] + srcs: move(r, f)
            for s in srcs: rec.append((1, d, s, 1, f, ph))
    run(c['D'], 1); run(c['A'], 2)
    temp = n
    for k, q in enumerate(c['ret']):
        fq = cur[q]; rec.append((2, q, temp, fq, ZERO, dim[fq]))
        for t, row in enumerate(c['scatter']):
            if k in row: rec.append((1, v + t, temp, 1, ZERO, 3))
        rec.append((3, q, temp, fq, ZERO, 0))
    run(c['B'], 4); run(c['C'], 5)
    for r in range(n): move(r, F(c['final'][r]))
    with open(out + '/249-records.bin', 'wb') as fh:
        for e in rec: fh.write(struct.pack('<6i', *e))
    st = dict(n=n, v=v, h=h, R=R, ZERO=ZERO, FULL=FULL, initial={str(r): F(c['start'][r]) for r in range(n)},
              final={str(r): F(c['final'][r]) for r in range(n)}, retained_totals=c['ret'], source_owned_roles=[], regs=[])
    json.dump(st, open(out + '/249-states.json', 'w'), sort_keys=True, separators=(',', ':'))
    json.dump(dict(frames=frames), open(out + '/frames.json', 'w'), sort_keys=True, separators=(',', ':'))
    return st, frames, rec


if __name__ == '__main__':
    c = load_word(sys.argv[1]); snap, cin, cout = sys.argv[2:5]
    st, frames, rec = export(c, snap)
    os.makedirs(cin, exist_ok=True); os.makedirs(cout, exist_ok=True)
    json.dump(st, open(cin + '/249-states.json', 'w')); json.dump(dict(frames=frames), open(cin + '/frames.json', 'w'))
    json.dump({'donor_keys': []}, open(cin + '/249-DONOR-OWNERSHIP.json', 'w'))
    json.dump({}, open(cout + '/COHORT249-FRAMES.json', 'w'))
    json.dump({k: int(x) for k, x in st['initial'].items()}, open(cout + '/COHORT249-INITIAL.json', 'w'))
    json.dump([], open(cout + '/COHORT249-SELECTION.json', 'w'))
    shutil.copy(snap + '/249-records.bin', cout + '/COHORT249-RECORDS.bin')
    print('   exported %d records, %d distinct frames, n %d, ZERO %d, FULL %d' % (len(rec), len(frames), st['n'], st['ZERO'], st['FULL']))
