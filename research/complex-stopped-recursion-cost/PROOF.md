# The stopped complex recursion bill of #4100 COMPLEX.md

JoyboyBrian, with substantial assistance from Anthropic Claude (Claude Code).
Apache-2.0. This is an author-submitted scoped proof, not an accepted theorem.

## Object and caller

Cinna Davis's #4100 `research/unconditional-batched-crt/COMPLEX.md` (retained
head `337d04939571a637aeab54a0f58f54fde811663a`, pinned here at canonical main
`cef4b52f2a59009865bf8eabde1be3f159063703`), section "Time", states:

> Stop at width max(73,h^eta). At each internal node, all adapters, monomials,
> packet scans and parking cost O(V e^(1-a2) polylog(p)) [...] Hence the
> complete layer costs O(V h^(1-q) polylog(p)).

Its constants are the PR4088 mixed histogram
`H = {1:8060060, 2:2310120, 3:751813, 4:327210, 5:66425, 8:25920, 48:138492}`,
`W = 322560`, `b = .001730979115670792472760579929302792893760378764`,
`q = b - 10^-28`, `a_eff = (b+q)/2`, `tau = 1 - a_eff`, `eta = 10^-32`, and
`a2 = .001733394791695384296` from PROOF.md. Write

    mu_x = sum_r (H_r / W) (r/73)^x.

The callers are PROOF.md's synthetic-transform layers (`h` = active axis bits at
one FFT level, `1 <= h <= d-1`, at most `ell` levels per transform) and
GAUSSIAN.md's compiled layers (`h = O(p^beta)` or `O(p^epsilon)`).

## Premises kept explicit

These are COMPLEX.md's own premises. This package does not verify them.
`Lambda = Lambda(p) >= 1` is the polylog factor, uniform in `e`, `v` and `h`;
`c_N`, `c_L`, `c_P` are fixed constants. Fix the root width `h >= 1` and the
stop width `s = max(73, h^eta)`; every descendant uses the root's `s`.

- **(N) internal node.** A call of width `e > s` on volume `v` puts
  `f = floor(e/73)` and performs only: (i) its own adapters, monomials, packet
  scans and parking, at cost at most `c_N Lambda v e^(1-a2)`; (ii) the
  `e - 73f <= 72` remainder bits by elementary passes, at most `c_L v` each;
  (iii) for each rank `r`, children of width `r f` whose total volume is
  `(H_r/W) v`. This is COMPLEX.md's one-child reading of a rank-`r` transition;
  #4375 shows that the factorwise reading (`f` scalar copies) breaks the moment.
- **(L) leaf.** A call with `e <= s` costs at most `c_L v e`.
- **(P) root placement.** Placement and inverse cost at most
  `c_P Lambda V (h^(1-a2) + 1)`.
- **(A) additivity.** Costs of the listed parts add, and every child obeys
  (N), (L) with the same constants.

## Exact and certified facts

1. `a_eff < a2`, `q < a_eff`, `q > 0` and `eta*b < b - q` hold exactly over the
   rationals. Hence `1-a2 < tau < 1-q` and `1 - b + eta*b < 1 - q`.
2. `a_eff < 1/200` and `74^199 >= 72^200`, so `e^tau >= 74^(199/200) >= 72`
   for every integer `e >= 74`.
3. Certified outward-rounded rational enclosures give
   `1 - mu_(1-b) = 1.804257...e-48 > 0` and
   `1 - mu_tau = 1.417734591407...e-28 > 0`, so
   `1/(1 - mu_tau)` lies in `(7.0535e27, 7.0536e27)`.

`verify.py` checks all three with the standard library.

## Lemma (all root widths)

Under (N), (L), (A), every call of width `e >= 1` on volume `v` costs at most

    v [ K1 e^tau + c_L s^b e^(1-b) ],     K1 = (c_N Lambda + c_L) / (1 - mu_tau).

*Proof.* Strong induction on `e`. The recursion is well founded: an internal
width satisfies `e >= 74`, so `f >= 1`, and every child width satisfies
`1 <= r f <= 48 e / 73 < e`.

*Leaf* (`e <= s`): `c_L v e = c_L v e^(1-b) e^b <= c_L v s^b e^(1-b)`.

*Internal* (`e > s >= 73`): parts (i) and (ii) cost at most
`c_N Lambda v e^(1-a2) + 72 c_L v`. Since `e >= 1` and `1-a2 < tau`,
`e^(1-a2) <= e^tau`; by fact 2, `72 <= e^tau`. So (i)+(ii) cost at most
`(c_N Lambda + c_L) v e^tau`. For (iii), `73 f <= e` and the exponents are
positive, so `(r f)^x <= (r/73)^x e^x` for `x = tau, 1-b`. The induction
hypothesis, applied to each child and summed by (A), bounds (iii) by

    v [ K1 mu_tau e^tau + c_L s^b mu_(1-b) e^(1-b) ]
      <= v [ K1 mu_tau e^tau + c_L s^b e^(1-b) ],

using `mu_(1-b) <= 1` (fact 3). Adding, the coefficient of `v e^tau` is
`c_N Lambda + c_L + K1 mu_tau = K1`. This closes the induction. QED.

No monotonicity of the cost in `e` is used, and floors enter only through
`73 floor(e/73) <= e`.

## Theorem (COMPLEX.md's layer bill)

Under (N), (L), (P), (A), for every `h >= 1` the complete layer of volume `V`
costs at most

    V Lambda h^(1-q) [ (c_N + c_L)/(1 - mu_tau) + 73^b c_L + 2 c_P ].

*Proof.* Apply the lemma at `e = h`, `v = V`, and add (P). Since `h >= 1`,
`s^b = max(73^b, h^(eta b)) <= 73^b h^(eta b)`. The four exponents `tau`,
`1-b+eta*b`, `1-a2` and `0` are all at most `1-q` (fact 1), so each power of
`h` is at most `h^(1-q)`. Finally use `Lambda >= 1`. QED.

The constant is independent of `h`, `p` and the coefficient values. It is
effective but large, since `1/(1-mu_tau) > 7.05e27`.

## Binding to the callers

- **PROOF.md synthetic transforms.** One FFT level is one layer with
  `1 <= h <= d-1`; there are at most `ell` levels. Since `h^(1-q)` increases
  with `h`, levels with fewer active axes are covered. One transform costs at
  most `ell V Lambda K d^(1-q)`, which is PROOF.md's
  `O(V ell d^(1-q) polylog(p))`.
- **GAUSSIAN.md compiled layers.** `h = O(p^beta)` or `O(p^epsilon)` gives
  `O(V h^(1-q) polylog(p))` with the same constant.

## What the argument does and does not use

- `mu_(1-b) <= 1` suffices for the leaf term. Strictness is not needed. Its
  certified margin is only `1.8e-48`, and one extra rank-48 child per `W`
  makes `mu_(1-b) > 1` (control).
- The stop width enters only through `s >= 73`. The lemma holds for every
  fixed `s >= 73`. The `h^eta` stop costs the factor `h^(eta b)` and is not
  needed for this bill. It may serve other premises, such as control
  payloads; this package does not decide that.
- The floor is necessary. With `r ceil(e/73)` instead, a width-74 node has a
  rank-48 child of width 96, so the recursion is not well founded and the
  comparison `(r f)^x <= (r/73)^x e^x` fails (control).
- **Size of the constant.** The per-level contraction `1 - mu_tau` is only
  `1.4e-28`, so the uniform constant exceeds `7e27 (c_N Lambda + c_L)`. On
  complete finite trees with unit node costs, the internal `tau`-sum divided
  by `h^tau` is at most 8.8 for `h <= 10^12`. It grows roughly like the
  depth. The huge constant is therefore a worst-case geometric-series artifact
  and not a defect.

## Finite corroboration

`verify.py` evaluates complete recursion trees with unit costs
(`c_N = c_L = Lambda = 1`) at 60-digit Decimal precision. It covers every
`h = 75, 112, ..., 1497`, plus `h` in
`{74, 100, 146, 1000, 5329, 10^4, 389017, 10^6, 10^9, 10^12}`, with stop widths
73, 500 and 5000. It checks three things:

- the frontier sum `sum_leaves (v_l/V) e_l^(1-b)` is at most `h^(1-b)`;
- the internal sum `sum_internal (v/V) e^tau` is at most `h^tau/(1-mu_tau)`;
- the unit-cost total is below the lemma's bound.

This is numerical corroboration. It does not certify anything and does not
replace the proof.
