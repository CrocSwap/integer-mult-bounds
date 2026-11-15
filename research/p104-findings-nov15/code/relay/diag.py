import sys
from drive import *
base_ops = [(float(i), e) for i, e in enumerate(W['program'])]
tl = timeline(base_ops, NP, W['owned_fields'], W['initial'])
P = W['program']
for F in map(int, sys.argv[1:]):
    hs = {s[0] for s in X['stops'][F]}
    for i, e in enumerate(P):
        if evframe(e) != F or e[0] != 'ADD': continue
        r, s = e[1], e[2]
        print('F', F, 'op', i, e)
        for d in (-1, 1):
            # co-presence windows
            st = stays(tl, r); ss = stays(tl, s)
            w = [(max(a[0], b[0]), min(a[1], b[1]), a[2]) for a in st for b in ss if a[2] == b[2] and max(a[0], b[0]) < min(a[1], b[1]) and a[2] != F]
            w = [x for x in w if (x[0] < i if d < 0 else x[1] > i)]
            if not w: print('   dir', d, 'no co-presence'); continue
            x = max(w, key=lambda x: x[1]) if d < 0 else min(w, key=lambda x: x[0])
            lo, hi = (min(x[1], i), i) if d < 0 else (i, max(x[0], i))
            blk = []
            for k in range(int(lo) + 1 if lo > -1e17 else 0, int(hi) if hi < 1e17 else len(P)):
                O = P[k]
                if O[0] == 'ADD' and (O[1] in (r, s) or O[2] in (r, s)):
                    kind = ('W' + ('r' if O[1] == r else 's') if O[1] in (r, s) else '') + ('R' + ('r' if O[2] == r else 's') if O[2] in (r, s) else '')
                    blk.append((k, kind, O[4], dim[O[4]]))
                elif O[0] == 'SCALE' and O[1] in (r, s): blk.append((k, 'S' + ('r' if O[1] == r else 's'), O[3], dim[O[3]]))
            from collections import Counter
            print('   dir', d, 'meet frame', x[2], 'dim', dim[x[2]], 'intervening', len(blk), Counter(b[1] for b in blk), blk[:6])
