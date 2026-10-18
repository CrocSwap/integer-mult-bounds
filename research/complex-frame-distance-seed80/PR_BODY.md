Independently check the exact complex canonical-frame recursive-rank obligation at frozen PR1042: all 1,004 frames, 2,896 child edges and 224 endpoint adapters pass literal P/D/C symplectic replay and a separate Lagrangian-intersection check. A written proof derives rankB = dimU + dimV -2dim(U intersectV).

The complete F2^5 census covers 374 subspaces and 139,876 ordered pairs. Absolute dimension difference undercounts 128,712 nonnested pairs; the selected edges are all nested and unaffected. This is verification of a standard rank identity, not a new algebraic formula or kappa.

Reproduce:

```
python -I -O -B research/complex-frame-distance-seed80/verify.py
python -I -O -B research/complex-frame-distance-seed80/test_package.py
```

The 15 rejection controls include missing/wrong recipes and omitted diagonal gates that remain symplectic but violate the required Lagrangian. A separate phase mutation intentionally passes the rank checker, documenting that no global-phase or operator-equality check is claimed. No native/provider/precision/outer replay.

Credits: icekylinx PR425/433 compiler lineage, LeaverSAT/LeaverSAT2 and PR1004/1005/1018, Jeremy Kothe PR1042; prior PR702/712 phase and PR911 binary-interface audits are distinct. Contributor @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
