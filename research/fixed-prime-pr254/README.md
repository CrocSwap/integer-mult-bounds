# Fixed prime and seven finite levels on PR254's response-kernel entrance gauges

Conditional **κ = 710465204542247142217 / 10^24 = 7.10465204542247142217 × 10⁻⁴**,
an exact gain of `3909417142217/10^24` (≈ 3.909 × 10⁻¹²) over Dugongue's PR254
(`71046520063283/10^17`). The bit supplier binds.

This is an arithmetic refinement of PR254's unchanged physical construction, using exactly the
method gabriele-nespoli introduced in PR235 (later applied by PR243, PR247, PR248, PR252 and PR253 to
other parents). No word, frame, bank, chart or finite cost of PR254 is changed.

## Reproduce

From the repository root, Python 3.11+, standard library only:

```sh
python3 -B research/fixed-prime-pr254/verify.py
python3 -B research/fixed-prime-pr254/verify.py --parent-output /path/to/fresh/pr254/run   # optional
```

The default mode reads PR254's packaged receipts `expected/COHORT-EXACT-PRICE.json` and
`expected/COHORT-FINITE-INVOICE.json` (pinned by SHA-256). PR254's own verifier asserts that its fresh
native outputs equal these receipts; a fresh run here (`verify.py --output … --cxx g++ --boost-include …`
in `research/cohort-kernel-entrances132`) produced byte-identical files, and `--parent-output` accepts
such a run directly.

## What the verifier does

1. **Reproduces PR254 exactly** from its receipts with PR254's parameters: rare density 10⁻¹⁶, three
   completed ordinary levels from `384599/10^10`, η = 10⁻¹², β = 10⁻⁹, 10⁻¹⁷ grid. It recovers PR254's
   coarse saving `71097032054791/10^17` and κ `71046520063283/10^17`.
2. **Fixes the prime** q = 2¹²⁷ − 1 before any width (Lucas–Lehmer, 125 updates recomputed; PR235 also
   kernel-checks it in Lean). The retained bit theorem bounds the bad fraction by 2m³/q, so the rare density
   is ρ = 3456000/q < 10⁻¹⁶. **Every rare edge still pays the full 32m² rank-one fallback.**
3. **Brackets the coarse saving** on a 10⁻²⁷ grid with the public interval engine, confirmed by an
   independent atanh engine for both the accepted and the excluded point. Reinstating density 10⁻¹⁶ at the
   new point fails the lower moment bound, so the gain depends on the proved density.
4. **Seven acyclic completed ordinary levels**, a_j = (1−c)c + c·a_(j−1), each using only level j−1; all
   four admission gaps (atom, borrowing, remainder, stock) are positive at every level and the PR234 finite
   cutoff rule applies.
5. **Unchanged outer assembly**: all 47 strict constraints and seven margins with η = 10⁻²⁴ (as in PR243
   and the reviewed main result), β = 10⁻⁹, on a 10⁻²⁴ grid; the adjacent grid point is rejected. The new
   κ exceeds PR254's **unrounded** outer bound, so this is not a rounding change.

## Fixed costs under the larger prime

PR254's finite invoice already charges its literal construction (40 replicas, literal stock 869195,
selector bill 626938189600). Its counted primitive coefficient `62447396383377201` (< 2⁵⁶) and signed
payload prefix (95 bits) stay below 2⁸⁰ < q, so the q-power bound B(q) < q^14401 is unchanged in form.
All chart denominators (dividing 4, 18, route denominators 1, 2, 3, 6) and normalizer factors are units
modulo q. q-dependent initialization and table scans remain in the retained primitive constant, which may
depend on q and the fixed recipe but not on width.

## Scope

Conditional on everything PR254 retains: the all-size compiler, common weighted chart, restored rows,
selectors, routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction.
The complex supplier (saving `29898197786071/4·10^16`) is PR234's five-stage supplier; its profile and the
finite bridge are vendored from PR251's fresh certificate and checked again here (complex moment < 1).
No unconditional theorem, Lean certificate of the multiplication bound, or runtime claim.
