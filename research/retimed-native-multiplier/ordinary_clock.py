"""Check integer envelopes in the ordinary fixed-tape clock proof."""

from fractions import Fraction

RANKS = {
    '8030-compact': (260_000, 1_600_000),
    '8030-high': (25_000_000, 160_000_000, 1_000_000_000, 6_000_000_000, 36_000_000_000, 224_000_000_000),
    '8030-match': tuple(7*x for x in (25_000_000, 160_000_000, 1_000_000_000, 6_000_000_000, 36_000_000_000, 224_000_000_000)),
    '8035-near': (6_835_937_536, 109_375_000_000, 1_750_000_000_000, 28_000_000_000_000, 448_000_000_000_000, 7_168_000_000_000_000),
    '8035-fixed': (106_811_524, 1_708_984_375, 27_343_750_000, 437_500_000_000, 7_000_000_000_000, 112_000_000_000_000),
}


def polynomial_to_fibre_bound():
    # X=2^16 N^4 (D+1)(w+1)^252, D+1<=256(w+1).
    # w+1<=2^259*u^258; u^a/3^(u-1)<=3*a^a.
    degree = 20 * 253
    a = 258 * degree
    return 20 * (16 + 8) + 259 * degree + 2 + a * (a - 1).bit_length()


def full_log2_B(ranks):
    # B0=2^100, B_i<=J_i^14(1+Bprev); root binary rectangle and digit rounding.
    return 40 + 16 * 1024 * sum(ranks)


def main():
    extra = polynomial_to_fibre_bound()
    assert Fraction(9*16, 15*32) == Fraction(3, 10)
    assert Fraction(1,1) / (1-Fraction(3,10)) == Fraction(10,7)
    assert all((1+y)**5 <= 2**14 * max(1, 2**(y-1)) for y in range(1, 11))
    assert all((z+1)**5 <= 2**10*3**z for z in range(1, 8))
    assert all((e+1)**5 <= 32*4**e for e in range(1, 8))
    assert all(extra + 80*min(H) < 1024*min(H) for H in RANKS.values())
    print('log2 fixed variable-amortization factor <=', extra, 'plus 80 H')
    for name, H in RANKS.items():
        print(name, 'sum H', sum(H), 'log2 B <=', full_log2_B(H))


if __name__ == '__main__':
    main()
