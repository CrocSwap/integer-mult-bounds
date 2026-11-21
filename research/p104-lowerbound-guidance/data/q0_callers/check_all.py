#!/usr/bin/env python3
"""Re-verify every stored real Q = 0 caller word with check.py (exact replay over Q(i)[D] at q = 1,-1,i,-i; symbolic D)
and compare chat(.99) with the exact table.  [C] exact.  Standard library only (about 25 s)."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import check as qc
EXPECT = {'ml_k4': 113.8427, 'ml_k5': 115.4258, 'ml_k6': 115.2185, 'ml_k7': 114.1914, 'ml_k8': 112.7731,
          'ml_k9': 111.1722, 'ml_k10': 109.4970, 'ml_k11': 107.8061, 'ml_k12': 106.1317, 'ml_k13': 104.4915,
          'chain_k3': 107.9101, 'chain_k4': 108.2140, 'chain_k5': 100.2387, 'chain_k6': 87.6044, 'caller_C1': 107.9101}
for name, want in EXPECT.items():
    C = json.load(open(os.path.join(H, name + '.json')))
    ok, wf = qc.legal(C)
    k, n = C['stages'], C['roles']
    assert ok and wf, name
    assert n == 2 * k - 2, name                       # tight: n = 2k-2
    assert all(sum(dg[2:2 + k]) >= 2 for dg in C['diagonal']), name   # every role degree >= 2
    assert abs(qc.chat(C) - want) < 5e-5, (name, qc.chat(C))
    assert qc.chat(C) < qc.HP(k), name
    print('%-10s k=%2d n=%2d LEGAL chat=%.4f < HP(k)=%.4f' % (name, k, n, qc.chat(C), qc.HP(k)))
print('PASS %d stored Q=0 caller words: legal, tight, chat < HP(k)' % len(EXPECT))
