# Independent check: where #4635's +0.0000016099 comes from

**No new κ.** This package checks Dugongue's native Word RAM line:
#4630 (κ = 0.0030201655, head `f4b974db1f651250a252721cf127d0491a802699`) and #4635
(κ = 0.0030217754, head `898b0c8e2ca23897c312230988515c2553154f30`). The question:
what changes between them? And does the +0.0000016099 step come from the paid profile
and critical root, or from a native transfer/absorption term?

## Result

**The step comes entirely from the changed paid profile, which #4610 supplies. No transfer or absorption term changes.**

1. **Changed ledger.** The targets (10,928 fields), the helper census {4:28, 7:7, 8:47, 9:326} and the controller are byte-identical across the two PRs. The controller blob `49a2f067…` equals main's `research/joint-helper-lattice/CONTROLLER.json` and has 18 LOCAL calls. #4635's `ARITHMETIC.json` is byte-identical to the one in #4610's round-three package at head `1eb8da6c`. The only change is the local paid profile, by {1:−36, 2:+24, 3:+16, 4:−20, 5:+4} per LOCAL call. That is 18× this change globally: {1:−648, 2:+432, 3:+288, 4:−360, 5:+72}. The local rank mass stays 5,327 and the surplus stays 752. #4630's profile equals main's p16 profile in `compact-joint-compiler/arithmetic/RESULT.json`.
2. **Critical roots.** These were recomputed by an independent method: Decimal ln/exp at 60 digits with bisection, rather than the 2^-128 outward grid of Dillon's engine. The root solves Σ targets·k^θ = Σ paid·r^θ, with one sign change on a grid of (0, 1].
   - #4630 (p16 profile): 1−θ = 0.00302016597701562…
   - #4635 (#4610 profile): 1−θ = 0.00302177587077658…
   - The raw step is 1.60989376e-6. Both stated brackets are confirmed.
3. **Decomposition.** The κ step 1.6099e-6 exceeds the raw step by only 6.24e-12. The gap between raw saving and κ is 4.770e-10 for #4630 and 4.708e-10 for #4635. The 6.24e-12 is paid from #4630's slightly larger slack. The native lift in NATIVE-LIFT.md is lossless: every κ < min(q_C, 3/32). It therefore contributes nothing numerically. #4635's README already says it does not rediscover the profile or the root. This check confirms that nothing else changes the number.
4. **Finite absorption at N = 2^(10^12).** The proof needs log-margin > 0. Using the true root:
   - #4630: margin ≥ 236.8 (stated 646/3)
   - #4635: margin ≥ 232.5 (stated 164)
   - The largest q_C this N supports is ≈ 0.0030217758354 for #4635 and ≈ 0.0030201659416 for #4630. The stated q_C values are conservative.
5. **Mirror and capacity at the #4635 root.** The worst mirror ratio is 0.56281093, below the stated 0.562811 and below β = 0.564. The capacity is η = 0.98209726, above the stated 0.982097.
6. **#4635 nine-row ledger.** I re-implemented NATIVE-LIFT.md's parameter formulas with Fraction. All of PARAMETERS.json reproduces exactly: q, stop, δ, ε, β, r, layout, ξ, all nine savings and all guards/excesses. The minimum excess is in the main-transform row: 80181306527/1604834840720000000000 ≈ 5.0e-11. Four controls reject:
   - κ = q_C
   - κ ≥ 3/32
   - #4635's κ on #4630's provider
   - an unfused O(Td) Gaussian row, whose saving δ ≈ 1.2e-11 is below κ
7. **#4630 nine-row ledger.** It reproduces: the minimum excess is 1.97983445e-11, in the main row. Each of the five rejecting controls fails for its stated reason:
   - `epsilon_one` breaks ε < 1.
   - `unfunded_outer_target` breaks the main row.
   - `membership_at_edge` breaks the membership guard.
   - `normalization_at_edge` breaks the global γ guard.
   - `key_fills_whole_word_power` breaks the key guard.

   **Observation:** the group-key guard 1−(β+1−ε) is the same expression as `beta_below_epsilon` (ε−β). It is also strictly weaker than the membership guard (ε−β) − (1−ε). So the key control is implied by the membership control, and the five controls test four independent conditions. This is redundancy, not an error.
8. **Selected frontier.** The selected κ = 0.00302015 (#4470) lies below the p16 raw root 0.0030201659770. This is consistent with #4630's statement that it does not change the p16 root.

## What is NOT covered

- Whether #4610's changed word is an admitted canonical provider. This includes the all-fiber identity, the 20 changed native maps, the 26 helper interfaces and absolute phases. #4610 is open and unselected, so #4635's number depends on it.
- The shifted-logarithmic majorant guards U, V, Q, d and the recurrence funding (.048546 > .04282).
- The retained analytic, compiler and recovery proofs, and the native algorithms themselves (fused Gaussian circuits, record products, boundary solver).
- #4635's frame-bridge and transporter lemmas. #4635 attributes no gain to them.

## Reproduce

From the repository root (Python 3.12, stdlib only, under 1 s):

```sh
python3.12 -B research/native-lift-4635-delta-check/verify.py
python3.12 scripts/research_package.py --package research/native-lift-4635-delta-check
```

PR-head inputs are vendored under `vendor/` and pinned as `head:<sha>:<path>` provenance rows in SOURCES.json. The verifier checks every vendored byte against those SHA256 pins. Its four negative controls reject:

- the #4630 profile against #4635's q_C
- a q_C above the raw root
- a one-byte tamper of the vendored profile
- the #4630 bracket applied to the #4635 profile

Metadata validation of head pins needs the PR-head commits to be present locally, for example via `git fetch origin pull/4630/head pull/4635/head pull/4610/head`.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Is #4610 head `1eb8da6c`'s round-three word an admitted canonical provider? A first step is an independent replay of its 20 changed native maps and 26 helper interfaces on all 632 columns.
2. Do the funded-majorant guards hold for the changed profile under an independent enclosure?

## Credit

Credit goes to the predecessors who did the work:

- Dugongue, for #4630, #4635 and the #4554 native assembly
- Cao Yifan, for the #4610 round-three joint-helper and native-map profile, which supplies the whole numerical step
- Cinna Davis and the #4470 joint-helper/controller lineage
- Dillon (#4532/#4535), for the critical-root criterion and engine
- zxv and Jacob Alan Sussman, for the compiler and integer matching
- Ryanson Jonathan, for mirror windows and the #4614–#4616 checks of an earlier #4610 head
- Vlado Vojdanovski (#1673), the #1758 gauge-free authors, Chafik Boukhalfa (#1786) and Tim Trudgian
- Harvey and van der Hoeven

No predecessor code is imported or executed. Vendored files are read as data, and the two `.py.txt` files only to bind stated constants.

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. New code is Apache-2.0. Vendored files keep their original Apache-2.0 notices and authorship.
