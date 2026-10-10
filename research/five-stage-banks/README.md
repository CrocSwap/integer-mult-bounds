# Completed entrance banks on the five-stage bit supplier

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{177145602695277}{250000000000000000}=0.000708582410781108 .
$$

That is **+0.694%** over PR234 (`703701743496697/10^18`, the five-stage construction) and +1.99% over PR230.

| Construction | Bit coarse saving | Conditional κ |
|---|---:|---:|
| PR234: five-stage suppliers, paid rank-5a exteriors | 7.04197e-4 | 0.000703701743496697 |
| **This: same suppliers, entrance residuals in width-120 banks** | **7.09085e-4** | **0.000708582410781108** |

The bit side still binds. PR234's five-stage complex supplier (`747454944651775/10^18`) has about 5% slack.

## What is new

PR234 completes each of its 2,279 genuine independent auxiliary entrances with one bundled exterior child of rank 5a: 2,200 of rank 100 (a = 20), 18 of rank 60, 48 of rank 65 and 13 of rank 90. Its own ledger notes these entrances are "not banked".

PR197 and PR205 showed, for the three-stage cover, that such an exterior correction can be replaced by completed banks: route every residual `I − P_σ` of an entrance chart into a full-width bank whose disjoint residual involutions multiply to the full weighted endpoint. This package applies that construction to the five-stage cover, at bank width m = 120.

- **Charts.** 231 distinct entrance frames (220 PR200 rank-20 frames and 11 PR210 joint frames of ranks 12, 13 and 18), each with the G-orthogonal complement `15a − (Σa)1` for `G = 9I − J` followed by an exact kernel basis. Each chart is inverted fraction-free and its elementary factors replayed; at most 221 factors, numerators ≤ 40, denominators ≤ 36.
- **Banks.** Twelve data copies, so every physical chain has 60 residual occurrences (5 stages × 12 copies). Residual ranks are 4, 12, 11, 6 (entrances) and 24 (the 14,364 other physical chains). They fill exactly 177,179 banks of width 120:
  - 360 banks of 8×11 + 8×4,
  - 108 banks of 10×12,
  - 39 banks of 20×6,
  - 4,304 banks of 30×4,
  - 172,368 banks of 5×24.
- **Colouring.** The chain/bank multigraph (998,580 incidences, degree 60 at every chain, at most 30 at a bank) gets a proper 60-edge-colouring, checked at both ends; colour j + 5b is stage j of copy b. A duplicated colour is rejected.
- **Profile.** Remove exactly the 2,279 exterior children; keep every other child. Over 12 copies, W = 12·4v + 177,179 = 261,659 at m = 120, with deficit 52,800 = 12·4,400 (unchanged per copy) and largest child 50.
- **Arithmetic.** PR234's own interval moment engine (with the inherited 10⁻¹⁶ bad-class envelope) certifies the coarse saving `709084856078931/10^18`; the next 10⁻¹⁸ point fails. Three finite ordinary levels from PR234's retained ordinary saving, and PR234's unchanged outer-47 assembly with its η = 10⁻¹², β = 10⁻⁹ and bridge, give κ. All 47 strict inequalities and 7 margins pass; the adjacent grid point is rejected.
- **Routing.** The conservative additional selector-call bound is 18·((W−1) + R·120·(221+119)) = 12,227,329,044 < 2⁴⁰, absorbed by the inherited ordinary toll as in PR197.

## Verify

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds pull/234/head
git worktree add --detach ../pr234 af3fe331ca60c936229e060681ffccbc1c208678
python3 -m pip install sympy==1.14.0
python3 -B research/five-stage-banks/verify.py --pr234-root ../pr234 --full
```

`--full` first runs PR234's own fresh verifier (all six mandatory stages, a few minutes) and requires its freshly computed mathematics to match; then it rebuilds the 231 charts, all banks and the colouring, and recomputes the moments and assembly, comparing with `certificate.json`. Without `--full`, PR234's pinned expected mathematics is used.

## Scope

A conditional finite construction and composition, not an unconditional multiplication theorem. Every PR234 dependency remains: the five-stage physical/scalar/prime checks, complex scalar theorems, weighted q-local compiler, complete-stream movement, copied-centre and restored-row interfaces, ordinary leaves, prime supply, precision/recovery and the all-size reduction. The bank endpoint argument is PR197's (disjoint residual involutions commute and multiply to the full endpoint, on arbitrary dirty contents), applied at width 120 with one colour per (stage, copy). Source-owned PR210 gauges are not banked, as in PR234.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
