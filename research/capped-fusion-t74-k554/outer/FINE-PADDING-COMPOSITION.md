# Fine source-prime padding on this package's stack, and epsilon -> 1

**Credit first.** The mechanism of this note is **PR1786 (chafreaky, Chafik Boukhalfa)**: source primes at relative gap Theta(p^-2) from their dyadic targets, which exist by **Tim Trudgian's** effective prime number theorem (arXiv:1401.2689v2, theorem 2), the resulting setup precision `Cp + 64 p^2 ceil(log2 p)`, the theta-dependent conditioning, the polynomial halo p^48 / core p^128 and the dyadic normalizers. Its full text is vendored verbatim in `vendor/pr1786/FINE-PRIME-PADDING.md` and is the proof of every statement about primes, precision, locality and normalization used here. It builds on Vlado Vojdanovski's PR1673 (capped phase-cell fusion), the fractional-shift interiors and per-visit tag accounting of PR1758 (`outer/GAUGEFREE-INTERIORS.md`), the radix-distributed union schedule (`outer/UNION-SCHEDULE.md`), Jeremy Kothe's PR1731 ledger lineage and the PR1699/PR1672 supplier. **New in this package** (only): (a) the observation that epsilon is a free parameter and the resulting exact point epsilon = 1 - 2e-30010; (b) the composition analysis below; (c) the exact ledger and independent derivation at that point.

## 1. What is used from where

| ingredient | source | role at epsilon -> 1 |
|---|---|---|
| fine primes, theta in (1/(4p^2), 1/(2p^2-1)] | PR1786 sec. 1-2 | chirp range a theta B^2 = O(a B^2/p^2): guard beta + 2 xi - 2 < 1 |
| setup precision, locality, normalizers | PR1786 sec. 3-5 | halo 48 / core 128; online precision stays O(p) |
| fractional-shift interiors, accretive circuit lemma | PR1758 (outer/GAUGEFREE-INTERIORS.md) | removes the linear gauge; **still required**: the old linear guard beta + xi <= 1 is violated at beta ~ 1, xi = 0.908 (ledger control `old_linear_guard`) |
| radix-distributed union schedule, per-visit tag work | outer/UNION-SCHEDULE.md | **still required**: the old g-factor union row 1 - eps - beta - 1/2 + xi is negative (control `old_g_factor_union_row`) and 2 beta < 1 fails (control `old_union_tag_2beta`) |
| boundary | explicit Strassen, tau = 45/16 (7^16 < 2^45), c = 3/32 | **not** the structured boundary of this package series: at xi = 0.908 < eps the boundary row is not binding, so the unproved stability claim of STRUCTURED-BOUNDARY.md is dispensable. Its file is retained as an alternative; it does not enter kappa. |

## 2. epsilon is a free parameter (answer to "what sets epsilon = 0.9999999 in PR1786")

Write delta = 1 - epsilon, beta = 1 - 3 delta, xi = epsilon(1+q) - c + s (boundary saving = main + s), c = 3/32. Every constraint of the ledger that involves epsilon or beta:

* main = epsilon q is the binding saving, kappa = floor(epsilon q) - 1e-30022;
* Gaussian row: 1 - epsilon + q beta >= epsilon q iff **beta >= 1 - delta(1 + 1/q)** (a window of width ~ 594 delta below 1);
* membership: 1 - beta - 2(1-epsilon) > 0 iff **beta < 1 - 2 delta**; header / tag per visit: 1 - beta > 0; group below dimension: epsilon - beta > 0;
* **1 - epsilon - r0 > 0** (`global_gamma_power_slack`, r0 = 1e-30010: the spare power for u <= p^r0) and `source_axis_superpolynomial` 1 - epsilon > 0;
* boundary / union rows: xi = 0.9079 < epsilon (cap_below_cell), xi - 1/2 > 0, guard 1 - (2 xi - 2) - r0 - beta = 0.184 > 0: independent of delta;
* core-face corrections epsilon + beta + 48 - 128 + 2 < 0: independent of delta.

The window for beta is non-empty for every delta > 0, and beta = 1 - 3 delta lies in it (the Gaussian row exceeds main by delta(1 - 2q)). The only lower bound on delta is **delta > r0 = 1e-30010**, a free strict slack of the proof. So PR1786's 1e-7 is an explicit interior point, not a limit; its kappa is q - 1.68e-10 only because delta = 1e-7. In this package delta = 2e-30010 (the smallest round value above r0):

    epsilon = 1 - 2e-30010, beta = 1 - 6e-30010, xi = 0.90792965478815...,
    kappa = 0.0016797549561255445213356709939207025769983114385025802954603275201628645...

which is q - 3.4e-30013 (q = b - 1e-30010 = 0.00167975495612554452133567099392070257699831143850258029546032752016286...). Exact sweep (`outer/independent_check.py`): delta in {1e-7, 1e-12, 1e-30, 1e-60, 2e-30010, 1.1e-30010 ... } all satisfy every row; delta = r0 is rejected by `global_gamma_power_slack`; beta below the Gaussian window or at the membership edge is rejected (ledger controls `beta_below_gaussian_window`, `beta_above_membership_window`, `epsilon_equals_one`, `epsilon_not_above_r0_slack`).

**Maximum epsilon.** Within this construction epsilon < 1 strictly (epsilon = 1 would mean d = p axes: source axes of O(1) size, `epsilon_equals_one` control; also kappa = epsilon q <= q), and 1 - epsilon > r0. The hard cap on any outer of this form is kappa < q (the supplier's complex saving); the remaining distance is q delta = 3.4e-30013.

## 3. Does composing with the rest of the stack relax anything further? (answer: no, nothing is left to relax)

* The binding rows at this point are main = epsilon q; boundary = main + s and union = main + s + 13/32, all other rows have positive margins >= 1e-30010. Nothing but delta moves kappa.
* Structured boundary / k5 boundary: boundary row non-binding, no effect on kappa (only on xi, which is free in (1/2, epsilon)). Using c = 1/2 would give xi = 0.5 and the same kappa; it would add the unproved structured-stability claim for nothing.
* The router row a_eff = (q+b)/2 > epsilon q by 5e-65 + q delta; using the true bit endpoint there would not change kappa (main binds).
* Therefore kappa = epsilon q - 1e-30022 with epsilon the only free quantity, and it is already within q delta = 3.4e-30013 of the ceiling q.

## 4. Obligations (same as PR1786 sec. 8, with sharper asymptotics)

1. Every "eventually" in vendor/pr1786/FINE-PRIME-PADDING.md is now needed with exponent margin delta = 2e-30010 instead of 1e-7: e.g. log x = Theta(p^(1-epsilon)) = p^(2e-30010) must dominate log p in the prime-count estimate (true for p beyond an astronomically large cutoff), source axes 2^(p^delta) must exceed every fixed polynomial of p, and the polylog factors of every row are absorbed by p^delta-type slack. This is the same logical status as the 1e-30010 slacks of every row of this package (and of PR1786's 1e-7 version with a smaller cutoff); no practical cutoff is claimed.
2. Trudgian's theorem is a cited mathematical input (vendor/pr1786); the prime and precision lemmas are PR1786's and need their review (PR1786 is a draft).
3. The composition with PR1758's accretive circuit lemma uses theta^-1 = O(p^2) in the symbol bound (PR1786 sec. 3); the Gauge-free note's guard is superseded by `beta + 2 xi - 2 < 1` at fine theta.
4. Fresh native admission of the unchanged supplier: `verify_release.py`.

## 5. Executable support

`outer/check_ledger.py` (exact, 62 strict checks (including improvement over the exact kappas of PR1828, PR1839, PR1875, PR1876 and PR1897), 17 rejecting controls, improvement over PR1786's exact kappa and PR1758), `outer/independent_check.py` (independent balance derivation, the epsilon-free sweep), `outer/check_fine_padding.py` (PR1786's finite prime witnesses, underflow control, power relations), `outer/check_gaugefree.py` (PR1758 identities).
