"""(f) multiplicative index maps.
1. Row-major 2^e x 2^e transposition == index map k -> 2^e k mod N, N = 2^{2e}-1 (k<N), and CRT form.
2. BFS word length of 2^e in (Z/N)^x over a fixed generator set S (fixed-unit multiplications, each O(V)),
   compared with the valuation lower bound e/log2(C)."""
import math
from collections import deque


def check_identities(e):
    n = 1 << e
    N = n * n - 1
    for i in range(n):
        for j in range(n):
            k = i * n + j
            kt = j * n + i
            if k < N:
                assert (n * k) % N == kt, (e, i, j)
                if n > 2:
                    a, b = k % (n - 1), k % (n + 1)
                    at, bt = kt % (n - 1), kt % (n + 1)
                    assert at == a and bt == (-b) % (n + 1), (e, i, j)
    return True


def bfs_len(e, gens):
    n = 1 << e
    N = n * n - 1
    target = n % N
    gs = []
    for g in gens:
        g %= N
        if math.gcd(g, N) != 1:
            continue
        gs.append(g)
        gs.append(pow(g, -1, N))
    gs = sorted(set(gs))
    dist = {1: 0}
    dq = deque([1])
    while dq:
        x = dq.popleft()
        if x == target:
            return dist[x], gs
        for g in gs:
            y = (x * g) % N
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    return None, gs


if __name__ == "__main__":
    for e in range(1, 8):
        check_identities(e)
    print("identities: transposition == x2^e mod (2^{2e}-1), CRT negation of the (2^e+1)-residue: OK for e=1..7")
    S = [-1, 2, 3, 5, 7]
    C = 7
    print("generators S =", S, "(and inverses); valuation bound L >= e/log2(C) = e/%.3f" % math.log2(C))
    for e in range(2, 11):
        L, gs = bfs_len(e, S)
        print(f"e={e:2d} N=2^{2*e}-1  BFS length of 2^e = {L:3d}   bound e/log2C = {e/math.log2(C):6.2f}   naive = {e}")
    S2 = [-1, 3, 5, 7, 11, 13]
    print("generators without 2:", S2)
    for e in range(2, 10):
        L, gs = bfs_len(e, S2)
        print(f"e={e:2d} BFS length of 2^e = {L}   bound e/log2(13) = {e/math.log2(13):.2f}")
