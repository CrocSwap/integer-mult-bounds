#!/usr/bin/env python3
# Short exact arithmetic on stated numbers (stdlib, seconds). The inputs below (D, root, taxes) are
# constants typed in from the reference invoice; they are NOT recomputed from a pricing file here.
# Prints DONE_LEDGER.
from math import log
from itertools import product
from fractions import Fraction as Fr

f = lambda x: x * log(x) if x > 0 else 0.0

# 1. Ledger re-cut: D = root net of perfect mains + public stop tax - owned (stated numbers).
v, L, c = 104, 18, 56
D = 226939
root = 147560
main_perfect = 2 * v * f(8)          # both mains as one rank-8 job per port
tax_h, tax_x, tax_y = 5775, 1091, 1061
print("f(145)*v", round(f(145) * v), "share", round(f(145) * v / D, 3))
print("root net of perfect mains", round(root - L * main_perfect), "share", round((root - L * main_perfect) / D, 3))
print("public stop tax*18", L * (tax_h + tax_x + tax_y), "share", round(L * (tax_h + tax_x + tax_y) / D, 3))
print("sum check", round(root - L * main_perfect + L * (tax_h + tax_x + tax_y) - 1028), "vs", D)
print("BIT cap +14.3%: needs D cut", round(D * (1 - 1 / 1.143)), "R0 =", round(D * (1 - 1 / 1.143) / L), "R0/call")
print("+2% variant: (7927-7690)*18 =", (7927 - 7690) * 18, "share", round((7927 - 7690) * 18 / D, 4))
print("floor public 5829 + ride 292 => R0/call", 5829 + 292, "gain share", round((7927 - 5829 - 292) * 18 / D, 4))
print("S parts: L*Omega", L * (v - c), "delta*v", v, "S", L * (v - c) - v)

# 2. Column fusion of two direct-sum copies of the chain root (candidate).
# Merging two copies of a field (rank r, idle w): dD = 2(r-w) ln 2 per port (first-order form f(2x)-2f(x)=2x ln2).
ln2 = log(2)
hub = 2 * 145 * ln2
chain_field = 2 * 9 * ln2            # r=8n+1, idle=8n-8: r-w=9 for every n
local_gain_per_pair = 2 * ln2 * 1720 / v  # native net mass 1720/call
print("merge hub", round(hub, 2), "chain field", round(chain_field, 2), "local gain/pair per port", round(local_gain_per_pair, 2))
print("net per fused pair", round(local_gain_per_pair - chain_field, 2), "x18 =", round(18 * (local_gain_per_pair - chain_field), 2), "vs hub", round(hub, 2))

# 3. Non-flat toy: min rank of the partial matrix for the triangle of bases.
# Port types are pairs of bases {1,2},{2,3},{1,3}; rows (type,base), cols (type,base).
# Entry (a,b) has class P_a xor P_b; a cell's classes must cancel, identity class sums to 1.
types = [(1, 2), (2, 3), (1, 3)]
idx = [(t, a) for t in types for a in t]
P = 7


def rank_mod(M):
    M = [r[:] for r in M]
    rk = 0
    n = len(M)
    for col in range(n):
        piv = next((i for i in range(rk, n) if M[i][col] % P), None)
        if piv is None:
            continue
        M[rk], M[piv] = M[piv], M[rk]
        inv = pow(M[rk][col], P - 2, P)
        M[rk] = [(x * inv) % P for x in M[rk]]
        for i in range(n):
            if i != rk and M[i][col] % P:
                g = M[i][col]
                M[i] = [(x - g * y) % P for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk


def build(free):
    Z = [[0] * 6 for _ in range(6)]
    for i, (s, a) in enumerate(idx):
        for j, (t, b) in enumerate(idx):
            if s != t:
                # different types share exactly one base; only that identity entry is nonzero.
                common = set(s) & set(t)
                Z[i][j] = 1 if a == b and a in common else 0
    k = 0
    for t in types:
        i0 = idx.index((t, t[0]))
        z11, z12 = free[k], free[k + 1]
        k += 2
        Z[i0][i0] = z11
        Z[i0][i0 + 1] = z12
        Z[i0 + 1][i0] = (-z12) % P      # the two cross entries share a class mod Pauli
        Z[i0 + 1][i0 + 1] = (1 - z11) % P
    return Z


best = min(rank_mod(build(fr)) for fr in product(range(P), repeat=6))
print("triangle: flat registers 3, non-flat min rank mod", P, "=", best)
print("DONE_LEDGER")
