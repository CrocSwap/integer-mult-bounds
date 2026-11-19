"""Amount of odd division needed by every matrix-unit readout of the two-site decoder."""
from collections import Counter
from fractions import Fraction
from math import gcd, lcm
from double_readout import P, binary_transform, prepare
from flag_weights import solution, weight
from compile_row import apply
from bell_reads import transvection


def shell_map(j):
    S = P.IDENTITY
    for i in range(j):
        S = tuple(transvection(17 << i, v) for v in S)
    return S


def census():
    unit = lcm(*(v.denominator for root in (0,1,16) for v in solution(root)))
    denominator = unit * 16
    shells = []
    for j in range(5):
        S = shell_map(j)
        X = P.point_set(S[:4])
        P.require(P.distance(P.BASE, X) == j, "shell representative")
        ws = [apply(S,v) for v in range(256)]
        counts = Counter()
        distinct = set()
        zeros = 0
        for x in range(16):
            for y in range(16):
                numerators = []
                for t in range(16):
                    for z in range(16):
                        val = weight(P.BASE, z | (x<<4), X, ws[t | (y<<4)])
                        numerators.append(val.numerator * (unit // val.denominator))
                binary_transform(numerators)
                for value in numerators:
                    d = denominator // gcd(denominator, value)
                    odd = d // (d & -d)
                    zeros += value == 0
                    distinct.add(abs(value))
                    counts[odd] += 1
        shells.append((j, len(distinct), counts, zeros))
    return shells


def verify():
    full = 21556663020569210160884269703315625
    shells = census()
    profile = [(distinct, zeros, len(counts)) for _,distinct,counts,zeros in shells]
    P.require(profile == [(10,64140,10),(25,62720,22),(42,57216,35),
                          (44,38912,36),(27,0,24)], "shell multipliers or zeros")
    for j, _, counts, _ in shells:
        P.require(sum(counts.values()) == 65536 and full not in counts and
                  lcm(*counts) == (full//3 if j == 0 else full), "shell common divisor")

    divisors = []
    for j,i,k,m,n,expected in (
        (0,1,1,1,1,562788258996425089753125),
        (1,2,2,4,4,6293916210385170849893217431625),
    ):
        read = prepare(shell_map(j),0,0,[(i,k,m,n,(1,0))],weight)
        gauss = read(0)
        den = lcm(*(v.denominator for v in gauss))
        divisor = den // (den & -den)
        P.require(divisor == expected, "nonzero matrix-unit divisor witness")
        divisors.append(divisor)
    P.require(lcm(*divisors) == full and full.bit_length() == 115,
              "minimal joint odd divisor")
    joint = [(0,0,1,1,(1,0)), (1,1,2,2,(1,0)), (1,1,4,2,(2,0))]
    value = prepare(shell_map(4),0,0,joint,weight)(0)
    expected = Fraction(35434033216309953801405149, 1412737467716023757103711499276492800000)
    P.require(value == (expected,0) and expected.denominator == (full << 16),
              "one superposed input attains the complete divisor")
    print("PASS 327,680 exact Walsh multipliers and a pair of matrix-unit witnesses.",
          "Sharp common odd divisor:", full)


if __name__ == '__main__':
    verify()
