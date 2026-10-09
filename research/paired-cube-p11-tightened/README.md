# Re-instantiated phase-stop on the p = 11 paired cubes: conditional κ = 5.108294e-4

Under #152's retained interfaces this package certifies

    T(n) = O(n (log n)^(1 - kappa)),   kappa = 2554147/5000000000 = 5.108294e-4

This is #152's construction unchanged — eumemic's paired cubes at p = 11
(h = 22, R = 18,473) with the h = 21 bit word in #97's frozen format — with
one assembly instantiation constant re-chosen: the phase-stop
`beta`: `PHASE_STOP = 1/10^6` (the merged #144 value #152 inherited) becomes
`10^-12`.

The phase-stop is a free positive constant of the retained #144 assembly: it
enters only the `(1 - beta) * AC - 10^-10` bit-ceiling term and the 47 strict
inequalities, and #152's complex side binds (`AC = 5113520/10^10`), so the
ceiling moves directly onto kappa. The same re-instantiation, at the same
constant and for the same reason, is the move of #104 over #97 and of #135,
#137 and #138 in this repository's lineage. No word, plan, row, bridge or
lemma changes; every inherited interface remains an assumption exactly as in
#152.

| | phase-stop | kappa |
|---|---:|---:|
| #152 (inherited) | 10^-6 | 5108289/10^10 |
| this branch | 10^-12 | **2554147/5\*10^9** (+5 grid points) |

The next 10^-10 grid point is rejected. The atom exponent and the 10^-10
backoff in the ceiling term are left at #152's pinned values: at the complex-
binding face the atom contributes nothing (verified), and the backoff
literal is part of #152's published interface rather than a declared free
constant.

## Verify

From the repository root (Python 3.10+ stdlib; about a minute; do not use `-O`):

    python3 research/paired-cube-p11-tightened/verify.py

The script reproduces #152's published kappa exactly at the inherited
constants, then rebinds the module-global `PHASE_STOP` to 10^-12 and reruns
#152's own 47-constraint assembly, asserting the new grid value and the
next-point rejection at both steps.

## Credits

- eumemic: #152 (the p = 11 instance and the h = 21 bit word this branch
  re-prices), #117 (the positive DAG), with Anthropic Claude assistance.
- icekylinx: #144/#130 (paired cubes, shared cores, the assembly whose
  phase-stop is re-instantiated here).
- Zhihao Chen (#97 frozen-word reader), Swapnil Jain (round-seven checkers),
  an664 (#128 completed-core sharing).
- The re-instantiation and this package: Abhinav Ramachandran with Hermes
  (Nous Research) assistance.

## Scope

Conditional, as in #152: no unconditional multiplication theorem is claimed.
All inherited written proof dependencies (shared-core execution, word-frame
nesting, uniformity and tape contracts) remain explicit assumptions.
