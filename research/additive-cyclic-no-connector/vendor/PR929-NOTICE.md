# Attribution and scope

New integration by Chafik Boukhalfa (@chafreaky), with substantial OpenAI
Codex assistance, under the repository's Apache-2.0 license.

- Ali Romman (@aliromman), PR621, head
  `520774462b19b29af41554b74def31f9d01e997e`: prime-power kernel, unit-circle
  lower bound and uniform inverse norm. Its source notice credits OpenAI's
  exact-DFT preprint, classical q-Pochhammer/Newton factorization and Alexey
  Kuznetsov. That notice is retained without alteration.
- Chafik Boukhalfa (@chafreaky), PR628, head
  `0768f97d06c623b8211e651543c66135796b62bf`: stable cyclic scans, arbitrary
  dirty source lifting, inverse words, root/interval fixtures and phase
  routing. PR862, head `57e0659150d323b784580110b36aa64a2dca2a33`, supplies
  the complementary-factor bound. PR905, head
  `aab6c0b8f4574cb36285ab5dab3fcfad0cd2b69e`, supplies the arbitrary-dirty
  cubic baseline. Their notices and proof sources are retained.
- Companion state-space filtering is classical. SciPy documents the related
  constant-input initial-state solve at
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter_zi.html
  (not the periodic closure used here). No SciPy code is consumed.
- Erwin H. Bareiss supplies classical integer-preserving Gaussian elimination:
  *Multistep Integer-Preserving Gaussian Elimination*, Argonne report ANL-7213
  (1966), https://digital.library.unt.edu/ark:/67531/metadc1035277/; and
  *Sylvester's Identity and Multistep Integer-Preserving Gaussian Elimination*,
  Mathematics of Computation 22 (1968), 565-578,
  doi:10.1090/S0025-5718-1968-0226829-0. The implementation here is new local
  code for that established algorithm.
- Mahler measure, causal Wiener-algebra inversion, companion adjugates and
  matrix perturbation arguments are established tools. Pan's factorization
  and Brent's elementary-function bounds are inherited as described and
  credited in the retained predecessor sources.

The contribution is the grouped dirty-array integration, rounded closure
and coefficient analysis, one-connector four-call construction, and explicit
cubic precision / scalar work-space accounting. Independent computational
oracles in this package are not independent human peer review. No literature
priority, practical speedup, physical tape realization, complete multiplication
theorem, or new kappa is claimed.
