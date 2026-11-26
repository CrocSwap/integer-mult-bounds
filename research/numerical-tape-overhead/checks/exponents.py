"""Compute sufficient bit lengths symbolically as n ≥ 2^(2^t), for integer q ≥ 2."""
import argparse


def cutoff(q):
    if q < 2:
        raise ValueError("q must be at least two")
    d = (60*q)**3
    j = 2
    while (1 << j) < j*d + 2:
        j += 1
    return j, max(1572864480, j*d)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("q", type=int, nargs="*")
    args = parser.parse_args()
    for q in args.q or [2, 10, 100, 1000, 10000, 100000]:
        j, t = cutoff(q)
        print(f"q={q}   j={j}   log2(log2(n)) >= {t}")
