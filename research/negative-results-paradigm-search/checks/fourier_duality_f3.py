"""Fourier duality over an odd-characteristic payload (F_3); standard library only.

Array f(H, D), H and D in F_2^e (e address bits each), payload F_3 (bits embed as 0/1, no growth).
Checks exactly, for e = 1..4 and both directions:
  XOR-shear  f(H, D) -> f(H xor D, D)  ==  WHT_H^{-1} . diag((-1)^{xi.D}) . WHT_H   (the sign pass is O(V)),
  swap == 3 XOR-shears (H ^= D, D ^= H, H ^= D) == 6 WHT layers of e bits + 3 sign passes, output stays 0/1.
So the interchange can be bought with H-layers. The README explains why this does not retire the bit primitive:
the complex primitive's own basis changes call chunk interchanges at a larger width, so the recursion is circular."""
import random

P = 3
rng = random.Random(1)


def popparity(x):
    return bin(x).count('1') & 1


def wht_axis(a, axis, e):
    """Unnormalised Walsh-Hadamard transform over the e bits of one axis, mod P."""
    n = 1 << e
    out = [row[:] for row in a]
    if axis == 1:
        out = [list(col) for col in zip(*out)]
    for idx in range(n):                     # transform each line along the chosen axis
        line = [out[k][idx] for k in range(n)]
        h = 1
        while h < n:
            for start in range(0, n, 2 * h):
                for k in range(start, start + h):
                    u, v = line[k], line[k + h]
                    line[k], line[k + h] = (u + v) % P, (u - v) % P
            h *= 2
        for k in range(n):
            out[k][idx] = line[k]
    if axis == 1:
        out = [list(col) for col in zip(*out)]
    return out


def xor_shear_direct(f, target_axis):
    n = len(f)
    g = [[0] * n for _ in range(n)]
    for H in range(n):
        for D in range(n):
            if target_axis == 0:       # (H, D) -> (H ^ D, D)
                g[H ^ D][D] = f[H][D]
            else:                      # (H, D) -> (H, D ^ H)
                g[H][D ^ H] = f[H][D]
    return g


def xor_shear_fourier(f, target_axis, e):
    n = 1 << e
    inv_n = pow(n, -1, P)
    fh = wht_axis(f, target_axis, e)
    for a in range(n):
        for b in range(n):
            xi, c = (a, b) if target_axis == 0 else (b, a)
            if popparity(xi & c):      # translation by c along the target axis -> sign (-1)^{xi.c}
                fh[a][b] = (-fh[a][b]) % P
    g = wht_axis(fh, target_axis, e)
    return [[(v * inv_n) % P for v in row] for row in g]


if __name__ == '__main__':
    for e in (1, 2, 3, 4):
        n = 1 << e
        f = [[rng.randrange(2) for _ in range(n)] for _ in range(n)]   # bit data embedded in F_3
        for ax in (0, 1):
            assert xor_shear_direct(f, ax) == xor_shear_fourier(f, ax, e), (e, ax)
        g = xor_shear_fourier(xor_shear_fourier(xor_shear_fourier(f, 0, e), 1, e), 0, e)
        assert g == [list(col) for col in zip(*f)], e
        assert all(v in (0, 1) for row in g for v in row)
    print('XOR-shear == WHT . (-1)^{xi.D} . WHT over F_3: exact for e = 1..4, both directions')
    print('swap == 3 Fourier-conjugated XOR-shears == 6 WHT layers (e bits) + 3 sign passes: exact, output 0/1')
