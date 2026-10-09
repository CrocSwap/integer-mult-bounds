# Completed width-120 entrance banks on the five-stage bit supplier

## 1. Inputs

PR234 at `af3fe331ca60c936229e060681ffccbc1c208678` freshly verifies a five-stage bit supplier on PR210's
source471 helper (m = 120, W = 23,683, deficit 4,400) and a five-stage complex supplier (saving
747454944651775/10^18). Its bit histogram contains one bundled exterior child of rank 5a for each of the 2,279
genuine independent entrances (2,200 PR200 rank-20 gauges that are not alias recipients and 79 PR210 joint
gauges of ranks 12, 13, 18). PR210's three rank-19 source-owned gauges, and PR210's source-owned rank-2/4
entrances, are not banked. Every other child is retained unchanged.

## 2. Charts

For each of the 231 distinct entrance frames σ = ker A ⊂ Q^24 use G = 9I − J. Rows 15a − (Σa)1 span the
G-orthogonal complement of σ; place them before an exact integer basis of σ to form B. The checker verifies
G-orthogonality, both identities B·C = C·B = d·I, and an independent replay of the elementary factors of B⁻¹.
In this chart the residual projector I − P_σ is diag(I_{24−a}, 0). Every chart integer is below 2^80, so the
charts stay invertible at every retained prime q > 2^80. They are address charts and change no scalar word.

## 3. Banks and scheduling

Take twelve data copies of the five-stage construction. Each physical chain then has 60 residual occurrences,
one per (stage j, copy b). Entrance chains have residual rank 24 − a ∈ {4, 12, 11, 6}; the other 14,364
physical chains have residual rank 24. The occurrences are partitioned into 177,179 banks of width exactly
120 (patterns in README). The chain/bank multigraph has degree 60 at every chain and at most 30 at every bank,
so it has a proper 60-edge-colouring; the checker verifies it at both ends and rejects a duplicated colour.
Colour j + 5b denotes stage j of copy b: every phase-major stage invocation receives every physical chain
exactly once and uses no bank twice, and each data copy keeps PR234's stage order.

## 4. Bank endpoint

After the charts, the residual projectors of a bank occupy disjoint coordinate intervals and sum to I_120.
For disjoint projectors D_P D_Q = D_(P+Q) = D_Q D_P, so the bank's weighted residual involutions commute and
multiply to the full weighted endpoint on arbitrary bank contents (PR197 §4, unchanged). The bank endpoint
therefore supplies exactly the correction each bundled rank-5a exterior child supplied, and those 2,279
children are removed. This is the same mechanism as PR197/PR205 at width 72; only the number of stage windows
(five) and the bank width (120 = 5·24) change.

## 5. Profile and arithmetic

Over twelve copies: W = 12·(4·1760) + 177,179 = 261,659, rank mass 12·(2,837,560 − 226,200), deficit
52,800 = 12·4,400. PR234's moment engine certifies the paid coarse saving 709084856078931/10^18 with the
inherited 10^-16·32m bad-class envelope; the next grid point fails, and banking strictly improves the paid
moment at PR234's own coarse saving. Three finite ordinary levels from PR234's retained 384599/10^10 and PR234's
unchanged outer-47 assembly (η = 10^-12, β = 10^-9, same finite bridge) give κ = 177145602695277/250000000000000000.
The extra routing calls are bounded by 12,227,329,044 < 2^40 and absorbed by the inherited ordinary toll exactly
as in PR197.

## 6. Limits

Conditional on every interface PR234 retains. No unconditional all-size theorem, Lean build or measured multiplier
performance is claimed.
