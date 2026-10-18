"""PROOF3 Task 2: exact census of k destination errors, with the checks of PROOF3 section B.

Channel model: k unit errors e_i (independent symbols, |e_i| <= 1) at the destinations of k
distinct completed leaves i <= t; register w at the cut after leaf t receives
sum_i M_{i->t}[w, y_i] e_i, bounded by the channel mass  sum_i |M_{i->t}[w, y_i]|.
E_k(n) = max of the channel mass over orientations, cuts t, registers w, and sets of <= k leaves.

Checks per n (MODE ok):
  M1    E_k <= k * max(1, fl(n)) for all k                                   (Thm M1)
  M2    E_2 == 2 * max(1, fl(n))   (n >= 2)                                   (Thm M2)
  M3    n >= 4, n+1 not a power of 2: at every (t, w) at most 2F(floor(n/2)) channels have mass
        fl(n); equality is attained                                          (Thm M3)
  OMEGA n >= 4: the single cut Omega_n of omega.py attains E_k for every k     (Conj C1)
  END   endpoint profile of every register = PR2067's response counts C_v(n), all masses 1
Usage: python3 multi3.py LO HI [MODE]"""
import sys
from check2 import gen, fl
from omega import omega, profile_at


def T(n):
    return 1 if n == 1 else T(n // 2) + 2 * T(n - n // 2)


def F(k):
    """# leaves of a size-k call whose exit support has the full size fl(k)+1 (Lemma X tight)."""
    if k == 1:
        return 1
    return F(k // 2) + (2 * F(k - k // 2) if (k + 1) & k == 0 else 0)


def F_closed(k):
    s = bin(k)[2:]
    j = len(s) - len(s.lstrip('1'))
    return 2 * j - 1


def C2067(n):
    """PR2067 endpoint response counts, rows (x, y, z_1, z_2, ...)."""
    if n == 1:
        return [0, 1]
    l, r = n // 2, n - n // 2
    cl, cr = C2067(l), C2067(r)
    z = [2 * T(l)]
    for k in range(max(len(cl), len(cr)) - 2):
        zl = cl[2 + k] if 2 + k < len(cl) else 0
        zr = cr[2 + k] if 2 + k < len(cr) else 0
        z.append(2 * zl + 2 * zr)
    return [0, T(n)] + z


def responses(n, s, mode='ok'):
    w = [e for e, _ in gen(n, s, mode=mode)]
    R = max(2, (n - 1).bit_length() + 2)
    for t in range(len(w)):
        rows = [{v: {(): 1}} for v in range(R)]
        resp = [[] for _ in range(R)]
        for j in range(t, -1, -1):
            x, y, f, sg = w[j]
            for v in range(R):
                r = rows[v]
                p = r.get(y)
                if p:
                    resp[v].append(sum(abs(c) for c in p.values()))
                    q = r.setdefault(x, {})
                    for m, c in p.items():
                        k = m + (f,)
                        val = q.get(k, 0) + sg * c
                        if val:
                            q[k] = val
                        else:
                            del q[k]
        for v in range(R):
            yield t, v, sorted(resp[v], reverse=True), t == len(w) - 1


def run(n, mode='ok'):
    H = max(1, fl(n))
    best = []
    topcount = 0
    endprof = {}
    for s in (1, -1):
        for t, v, ms, last in responses(n, s, mode):
            acc = 0
            for k, m in enumerate(ms):
                acc += m
                if k == len(best):
                    best.append(0)
                if acc > best[k]:
                    best[k] = acc
            topcount = max(topcount, sum(1 for m in ms if m == fl(n)))
            if last:
                endprof[(s, v)] = ms
    for k in range(1, len(best)):
        best[k] = max(best[k], best[k - 1])
    fails = []
    if any(best[k] > (k + 1) * H for k in range(len(best))):
        fails.append('M1')
    if n >= 2 and best[1] != 2 * H:
        fails.append(('M2', best[1]))
    if n >= 4 and (n + 1) & n:
        if topcount != 2 * F(n // 2) or F(n // 2) != F_closed(n // 2):
            fails.append(('M3', topcount, 2 * F(n // 2)))
    if n >= 4 and mode == 'ok':
        t, v = omega(n)
        om = profile_at(n, t, v)
        acc, pre = 0, []
        for m in om:
            acc += m; pre.append(acc)
        if any((pre[k] if k < len(pre) else pre[-1]) != best[k] for k in range(len(best))):
            fails.append('OMEGA')
    C = C2067(n)
    for (s, v), ms in endprof.items():
        want = C[v] if v < len(C) else 0
        if ms != [1] * want:
            fails.append(('END', s, v, len(ms), want)); break
    return best, topcount, fails


def rle(best):
    inc = [best[0]] + [best[k] - best[k - 1] for k in range(1, len(best))]
    out = []
    for d in inc:
        if out and out[-1][0] == d: out[-1][1] += 1
        else: out.append([d, 1])
    while out and out[-1][0] == 0: out.pop()
    return ' '.join('%dx%d' % (d, c) for d, c in out)


if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    mode = sys.argv[3] if len(sys.argv) > 3 else 'ok'
    bad = 0
    for n in range(lo, hi + 1):
        best, tc, fails = run(n, mode)
        bad += bool(fails)
        print(mode, 'n', n, 'fl', fl(n), 'E_inf', best[-1], 'T2067', T(n), 'maxcount(fl)', tc,
              '2F(b)', 2 * F(n // 2) if n >= 2 else '-', 'E_k runs', rle(best),
              'FAIL ' + str(fails[:3]) if fails else 'ok', flush=True)
    print('SUMMARY multi3', mode, lo, hi, 'failing sizes', bad)
