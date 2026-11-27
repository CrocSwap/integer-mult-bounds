"""Exact rational arithmetic for the eventual coefficient. Execute with Python 3."""
from fractions import Fraction as F

A, B, C = F(17, 4), F(11, 3), F(10, 3)
fixed = F(299, 36)


def q(j):
    return 3*j + (3*j+2).bit_length() + 2


def point(j, a):
    return 240*(a*q(j)*2**(3*j)+2)


def main():
    pos = 240*(2**17+2)
    height, slope = F(pos, 2), A/16
    for j in range(4, 7):
        for a, right in [(1, A), (2, B), (4, C)]:
            target = point(j, a)
            if target < pos:
                continue
            height += (target-pos)*slope
            pos, slope = target, right/2**j
            if (j, a) == (6, 1):
                assert (pos, height) == (1_572_864_480, 200_560_880)
                normalized = height/(240*2**(2*j)*q(j))
                assert normalized == F(2_507_011, 307_200) < fixed
                break
    assert 2*point(5, 4) < point(6, 1)
    assert fixed == F(20, 3)+(fixed-F(7, 4))/4
    assert (fixed+A)**3 < 4*fixed**3
    assert (fixed+A+2*B)**3 < 16*fixed**3
    # α is the positive cube root of this number.
    cube = 240*fixed**3
    assert (F(159, 4) + F(115, 12))**3 < cube < (F(479, 8) - F(33, 4))**3
    assert 2**30 <= point(6, 1)
    assert 512*31 <= 2**30 and 2**30+2 <= 2**31
    assert (F(182)+2*F(479, 8)+1)*16 < 2**20
    print("S =", point(6, 1), "h6 =", normalized, "h* =", fixed)
    print("exact cube of limiting native coefficient =", cube)
    print("all high widths pay the full 60-profile and one additional binary bit")


if __name__ == "__main__":
    main()
