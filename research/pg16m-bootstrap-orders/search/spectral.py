"""Spectral lower bound: any order passes a prefix of size 273, so cost >= |dS|/2 >= lambda2 * 273 * 273 / 546 / 2.
usage (numpy): python spectral.py [graph16_59.txt]"""
import sys
import numpy as np
tok = open(sys.argv[1] if len(sys.argv) > 1 else "graph16_59.txt").read().split()
V, d = int(tok[0]), int(tok[1])
nb = np.array(tok[2:], dtype=np.int64).reshape(V, d)
A = np.zeros((V, V))
for v in range(V):
    A[v, nb[v]] = 1
ev = np.linalg.eigvalsh(d * np.eye(V) - A)
l2 = ev[1]
bound = l2 * (V // 2) * (V - V // 2) / V / 2
print(f"lambda2 {l2:.9f}  bound {bound:.4f}  certified integer bound {int(np.ceil(bound - 1e-6))}")
assert abs(l2 - 11) < 1e-6 and int(np.ceil(bound - 1e-6)) == 751
print("PASS_SPECTRAL_751")
