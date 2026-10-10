# Exact extension and proof boundary

## Physical input

The input is the complete PR251 source527 construction at commit 2b030c06a811473ae8ed49dce07bc7ea50b72e9e, not a reconstructed proxy. Its parent verifier regenerates all eight stages and checks the emitted word against all 20,107 formal F2 columns in both directions, arbitrary dirty-register restoration, both reflected frame ledgers, 37 transported entrances, 24 physical replicas, and all bank assignments. The extension changes none of those gates, frames, roles, charts, endpoints, or lifetimes.

The literal profile has dimension m = 120, stock W = 521425, 11792280 paid children, rank mass 62465400, deficit 105600, and maximum child rank 50. Its bank selectors, copied centers, routes, full fallback, and restored rows stay fully charged.

## Rare-class refinement

Take the fixed prime
q = 2^127 - 1 = 170141183460469231731687303715884105727.
PR235 proves primality with Lucas-Lehmer and a Lean kernel proof. For m = 120, the exceptional-class density is exactly

rho = 2*m^3/q = 3456000/170141183460469231731687303715884105727 < 10^-16.

The old conservative envelope is replaced by this exact density only in the rare-class term. Every rare child still pays the complete 32*m^2 rank-one fallback, and the total finite coefficient remains 37443766921470961 < 2^80 < q. The selector bill remains 376079448960.

Using the full literal histogram, the existing public moment engine and an independent atanh-based rational engine bracket the fixed-prime coarse saving at

c = 355469382902250964672679/500000000000000000000000000

on the 10^-27 grid. The accepted endpoint is strictly below one, the adjacent coarse point is rejected by both engines, and the inherited delta_tau and delta_linear gaps remain positive.

## Finite ordinary levels and outer assembly

Starting from the retained completed saving 384599/10^10, each ordinary level is

a_j = (1-c)c + c*a_(j-1).

Eight levels reach the certified 10^-27 outer grid. Each level's exact positive gaps are checked against the fully charged q-power coefficient by the inherited cutoff rule. expected.json records every gap and cutoff. The coefficient remains strictly below 2^80, so the fixed prime dominates it. No fallback, bank selector, router, copied-center, or restoration term is dropped.

The final assembly keeps beta = 10^-9, changes only eta from 10^-12 to 10^-24, and recomputes the complete balanced outer assembly. All 47 strict inequalities and all seven margins pass. The next 10^-27 kappa grid point fails at both the final finite saving and the coarse cap. The bit supplier remains binding.

The exact decomposition is:

- PR251 baseline: 710433687047883000000000/10^27.
- Fixed prime, eight finite levels, eta = 10^-12: 710433690950939525300899/10^27.
- eta = 10^-24: 710433690953069816941696/10^27.
- Fixed-prime/finite-level gain: 3903056525300899/10^27.
- Backoff gain: 2130291640797/10^27.
- Total gain over PR251: 3905186816941696/10^27.

The exact moments, interval bounds, all assembly data and finite cutoffs are pinned in expected.json and recomputed by fixed_prime_math.py.

## Conditional theorem boundary

This is a conditional exponent refinement. It retains PR251/PR244/PR234's all-size weighted compiler, common weighted chart, restored-row bound, selector and bank interfaces, exact-tape routing, prime-supply assumptions, precision/recovery interface, complex symbolic correctness, and analytic reduction. Finite replay establishes the physical word, its accounting, exact rational inequalities, and the stated refinement under those inherited interfaces. It is not an unconditional proof of a multiplication algorithm and it does not certify practical runtime.
