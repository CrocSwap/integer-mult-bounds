# Attribution and scope

New integration by Chafik Boukhalfa (@chafreaky), with substantial OpenAI Codex
assistance, under the repository's Apache-2.0 license.

- Ali Romman (@aliromman), PR621, head
  `520774462b19b29af41554b74def31f9d01e997e`: prime-power kernel, unit-circle
  nonvanishing and uniform inverse norm. Its original proof and notice retain
  the OpenAI exact-DFT preprint and classical q-Pochhammer/Newton lineage.
- Chafik Boukhalfa, PR628 `0768f97d06c623b8211e651543c66135796b62bf`:
  stable scans, arbitrary-source integer lifts, fixtures and phase routing;
  PR862 `57e0659150d323b784580110b36aa64a2dca2a33`: complementary-factor bound;
  PR905 `aab6c0b8f4574cb36285ab5dab3fcfad0cd2b69e`: arbitrary-dirty cubic
  baseline; PR929 `85a1d11adbbd7610d269cfeb3e477cf7d457f2eb`: rounded
  higher-order companion closure, coefficient windows, gauge preparation,
  fraction-free solve and one-connector four-call construction.
- PR929's Gaussian arithmetic, weighted-filter helpers and grouped module
  are retained unchanged. This package uses its source index view and dense
  original-factor oracle; the new execution lives in `bounded.py`.
- Grouped partial fractions, projection onto one-sided Laurent coefficients,
  Mahler/Wiener bounds and companion-state filtering are classical tools.
  There is no novelty claim for those tools or for polynomial Bezout identities.
- Integer-preserving elimination is Erwin H. Bareiss's classical method:
  *Multistep Integer-Preserving Gaussian Elimination*, ANL-7213 (1966),
  https://digital.library.unt.edu/ark:/67531/metadc1035277/; and the 1968
  Mathematics of Computation article, doi:10.1090/S0025-5718-1968-0226829-0.
  PR929's notice also retains the state-space, Pan and Brent references.

The new contribution is the two-call additive integration with bounded
numerators, negative-history evaluation, no borrowed data array, explicit
cubic budgets and charged scalar preparation/workspace. No literature
priority, new multiplication exponent, physical implementation or independent
human/delegated-agent review is claimed.
