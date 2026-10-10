# w3 bit word with kernel, target-prefix, plateau and reorder stages, priced against PR304's complex supplier

**Conditional κ = 377274908385506513145517 / 500000000000000000000000000 = 0.000754549816771013026291034.**

That is +0.2200% over PR #310 (0.000752893499605334868002344, the w3 word's own admission), which this package
extends. It is +0.1382% over PR #311 (0.000753508664880762517753401, 209 target-prefix squares on the same word).
These are conditional asymptotic exponents, not measured multiplication speeds. No priority or optimality is claimed.

This package is PR #310's `w3-bitword` package. It keeps the complete source binding, inert-role deletion, bank, chart,
finite and PR233/PR256 complex admission, and adds four transcript stages after the source binding plus one supplier
admission. Every native checker of PR #310 then runs fresh on the final word.

| step | items | local Σφ change | κ after the step (exact grid) |
|---|---|---:|---|
| PR #310 w3 word | – | 1,068,458.57 | 7.52893499605e-4 |
| 1. kernel stage (`code/kernel_stage.py`) | 433 kernel families + 85 zero-response singles, entrance rank 840, 132 new frames | entrance change (stock 162,123 → 161,843) | 7.53675926616e-4 |
| 2. target-prefix + plateau stage (`code/target_plateau_stage.py`) | 45 F₂ target-prefix groups; 660 five-gate plateaus retimed into 660 new dim-15 frames | −1,025.22 | – |
| 3. reorder stage (`code/reorder_stage.py`) | just-in-time MOVE normalisation + 172 commuting ADD relocations (two rounds, fixed point) | −326.55 | bit cap 7.54549816771e-4 |
| 4. complex supplier | PR304's program via PR309's source-bound adapter, priced at 7635/10⁷ | – | **7.54549816771e-4** |

With PR233's supplier (7547/10⁷) the complex side binds after step 3, at κ = 377065428344163231288117/5·10²⁶ =
7.541308566883e-4. Step 4 lifts that cap, so the bit side binds again. The bit coarse saving is 7.5512e-4, and the
complex supplier is 7.635e-4.

## Reproduce

Python 3.11+ with `requirements.txt` (NumPy, SciPy, SymPy, mpmath), a C++17 compiler and Boost headers:

```sh
python3 -m pip install -r research/w3-bitword-stages/requirements.txt
python3 -B research/w3-bitword-stages/verify.py --output /tmp/w3-stages-proof --cxx g++ --boost-include /usr/include
```

It takes about 20 minutes. The PR249 source replay dominates the runtime. The PR256 complex source, the PR304 adapter and all stages
run fresh. Nothing is downloaded and nothing is published.

## Stages

- **Kernel stage.** This is the multicut kernel condensation of PR254/259/266/272, re-derived on the w3 word.
  - The cut is the end of the initial target-correction prefix (record 819,879), and 12,058 helpers are eligible.
  - The 433 families are twin pairs, integer and F₂ triples, and multi-donor families with shared donors allowed on nested E chains. They come from a multi-seed packing.
  - For each family, the pivot's prefix reads are removed. The pivot enters at the nondegenerate E. Each donor receives `d += a·p` at E after the cut and `d −= a·p` at FULL at the end.
  - The 85 zero-response helpers have no prefix reads in the w3 word, so they enter directly at their first frame.
  - `code/kernel_checks.py` checks:
    - exact rank and 9I−J Gram nondegeneracy of all 132 new frames;
    - the F₂ kernel identity of every family on the original prefix responses;
    - E inside every member's first frame;
    - that no member is a source owner or donor key, and that pivots and donors are disjoint.
  - `code/kernel_replay.py` checks:
    - GF(2) replays with random dirty inputs: sources unchanged, targets t⊕x, helpers restored, all registers equal to #310's;
    - controls that omit the Q (category 28) or Q⁻¹ (category 29) gates and are rejected.
- **Target-prefix and plateau stage.** This is the PR268/273 mechanism re-derived on the kernel word.
  - At the global target cut, a dependent target t with an integer-exact window dependency R_t = Σ ±R_p (k ≤ 3) has its window reads replaced by setup at ZERO and restore at a common close frame.
  - The 660 identical five-gate dim-13 components are retimed into the exact intersection of their four next frames (dim 15).
  - Checks:
    - nested chains;
    - forward and inverse F₂ all-column replays;
    - an integer replay mod 2⁶¹−1 equal on every register;
    - the source-span rule (0 violations).
- **Reorder stage.** This is PR #299/#306's stage on the cohort word.
  - The screen is re-run and must reproduce the frozen selection.
  - Checks: the crossed-interval contract, an integer replay equal on every register, a nonvacuous omission control, and the fixed point.
- **PR304 supplier.** The PR309-vendored adapter archive is pinned by hash and its members by inventory. It is extracted fresh and runs gx.check1 on the actual PR304 program, together with its label, scalar, splice, cover, router, precision and row guards and two moment engines (7636/10⁷ rejected). The physical row coefficient 16,170 stays below the retained 20,161.

The native chain then runs:
- legality (518 selections), and all 23,627 global and 22,172 compact F₂ columns (payload 97 bits < 104);
- the bank review, made generic: census and width-120 tiling read from `stages/bank-tiling.json`, 105,523 banks per stage, stock 809,215 / 161,843, 3,026,400 assignments;
- exact charts for all 4,265 new frames and 22,118 changed projectors (≤ 342 factors);
- price: two moment engines, eight levels, 47 strict constraints, adjacent grid point rejected;
- the finite invoice: coefficient 58,364,056,416,171,201 < 2⁸⁰, selector charge 571,950,117,600 < 2⁴⁰.

PR #310's own README and PROOF are kept as `README-PR310.md` and `PROOF-PR310.md`.

## Scope

This is a finite construction under the same inherited all-size interfaces as PR #310: compiler, common weighted
charts, restored rows, selectors, routing, prime supply, complex dirty lifting, precision/recovery and analytic
transfer. No Lean proof, unconditional theorem or runtime result is claimed.
