"""Channel-mass profile at the conjectured universal cut Omega_n (PROOF3 Task 2):
top sign +, follow V' from the top down to the size-2 call D = V'^d (d = ceil(log2 n) - 1),
cut right after D's U-leaf (x_D -> z_D), register w = z_D (deepest scratch level, register d+2).
Prints {mass: count} (high to low), Tot, and the k -> E_k breakpoints.
Usage: python3 omega.py LO HI"""
import sys
from collections import Counter
from check2 import gen, fl


def omega(n):
    W = gen(n, 1)
    d = (n - 1).bit_length() - 1
    path = ("V'",) * d + ('U',)
    t = [i for i, (_, p) in enumerate(W) if p == path]
    assert len(t) == 1, (n, path)
    return t[0], d + 2


def profile_at(n, t, v, s=1):
    w = [e for e, _ in gen(n, s)]
    row = {v: {(): 1}}
    ms = []
    for j in range(t, -1, -1):
        x, y, f, sg = w[j]
        p = row.get(y)
        if p:
            ms.append(sum(abs(c) for c in p.values()))
            q = row.setdefault(x, {})
            for m, c in p.items():
                k = m + (f,)
                val = q.get(k, 0) + sg * c
                if val: q[k] = val
                else: del q[k]
    return sorted(ms, reverse=True)


def profile(n):
    if n == 1:
        return [1]
    t, v = omega(n)
    return profile_at(n, t, v)


if __name__ == '__main__':
    for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        ms = profile(n)
        c = Counter(ms)
        print('n', n, 'fl', fl(n), 'Tot', sum(ms), 'channels', len(ms),
              'profile', ' '.join('%dx%d' % (m, c[m]) for m in sorted(c, reverse=True)), flush=True)
