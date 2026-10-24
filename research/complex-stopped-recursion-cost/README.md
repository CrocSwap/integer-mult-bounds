# COMPLEX.md's stopped complex recursion meets its layer bill

**Scoped proof under COMPLEX.md's own node premises. No new κ.** This does not
accept #4100, and it changes nothing in it or in the selected record.

## Object and caller

The object is Cinna Davis's #4100 [COMPLEX.md](../unconditional-batched-crt/COMPLEX.md),
section "Time", at retained head `337d04939571a637aeab54a0f58f54fde811663a`
(pinned at canonical main `cef4b52f2a59009865bf8eabde1be3f159063703`). It
claims that the stopped complex recursion costs `O(V h^(1-q) polylog(p))`.
The recursion has the PR4088 mixed histogram over `W = 322560`, children of
width `r floor(e/73)`, and stop width `max(73, h^eta)`.

The callers are PROOF.md's synthetic-transform layers (`1 <= h <= d-1`, at
most `ell` levels) and GAUSSIAN.md's compiled layers (`h = O(p^beta)` or
`O(p^epsilon)`). The [#4100 coverage map](../../docs/research/pr4100-audit-coverage-map.md)
lists the stopped-moment proof outside #4178's caller as still open.

## Result

[PROOF.md](PROOF.md) proves the following by strong induction, for every root
width `h >= 1`. It keeps COMPLEX.md's premises explicit: (N) node cost, the
remainder bits and the child volumes; (L) leaves; (P) root placement;
(A) additivity. The layer then costs at most

    V Lambda h^(1-q) [ (c_N + c_L)/(1 - mu_tau) + 73^b c_L + 2 c_P ].

Here `mu_x = sum_r (H_r/W)(r/73)^x`. The proof handles floors, the
`e mod 73` remainder bits and every stop width `s >= 73` directly. It assumes
no monotonicity in `e`. The certified facts are:

| Fact | Value |
| --- | --- |
| `1 - mu_(1-b)` | `1.804257...e-48 > 0` (only `<= 1` is needed) |
| `1 - mu_tau` | `1.417734591407...e-28 > 0` |
| `1/(1 - mu_tau)` | in `(7.0535e27, 7.0536e27)` |
| exponent order | `1-a2 < tau < 1-q`, `1-b+eta*b < 1-q`, `72 <= 74^tau` (exact) |

**Callers.** For the synthetic transforms this gives PROOF.md's
`O(V ell d^(1-q) polylog(p))`, including levels with fewer active axes. For the
GAUSSIAN.md compiled layers it gives `O(V h^(1-q) polylog(p))`.

**Notes.** None of these changes a downstream bound.

- The leaf term needs only `mu_(1-b) <= 1`.
- The `h^eta` stop is not used by this bill. Any fixed stop `s >= 73` works.
- The floor is necessary. With a ceiling, a width-74 node has a width-96
  child.
- The uniform constant exceeds `7e27 (c_N Lambda + c_L)`. On finite trees
  with unit costs, the internal `tau`-sum over `h^tau` is only 8.8 at
  `h = 10^12`. The constant is a worst-case artifact, not a defect.

## Not covered

- Premise (N)(i): that the node's adapters, monomials, the `Gamma`-fold cover
  gathers and parking cost `O(V e^(1-a2) polylog p)`.
- Premise (N)(iii): that the actual packets realize total child volume
  `(H_r/W) v` at width `r floor(e/73)`. #4375 shows that the factorwise
  reading breaks the moment.
- The free-word lift (#4184), the cover and stock arithmetic (#4424), the
  height and precision chain (#4178, #4371, #4415), and all of CRT.md.

## Reproduce

From the repository root, with Python 3.12 (standard library only, about 7 s):

```sh
python3 scripts/research_package.py --package research/complex-stopped-recursion-cost --check-only
python3.12 -B scripts/research_package.py --package research/complex-stopped-recursion-cost
python3.12 -B research/complex-stopped-recursion-cost/verify.py
```

`verify.py` reads the constants from the pinned COMPLEX.md and PROOF.md. It
checks the exact exponent order and the certified outward-rounded enclosures
of `mu_tau` and `mu_(1-b)`. It runs three rejection controls:

- a root above the bracket, `b + 1e-47`, gives `mu > 1`;
- one extra rank-48 child per `W` breaks both moments;
- the ceiling child rule grows width 74 to 96.

It also corroborates numerically, at 60 digits, complete recursion trees for
stop widths 73, 500 and 5000. That check is corroboration, not a certificate.
It imports no code from #4100, #4171 or #4178.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Node-cost premise.** Do the adapters, the F2 row-addition monomials, the
   `Gamma`-fold common-cover packet gathers and parking cost
   `O(V e^(1-a2) polylog p)` at the actual node? First step: write a per-node
   invoice from COMPLEX.md's "Common cover" section, PR2250 §5–6 and #4424's
   row-stock layout.
2. **Child volume premise.** Do the actual child packets realize
   `Gamma H_r` rank-`r` calls of volume `V/(W Gamma)` each? First step: bind
   PR4088's owner fill and the `W`-family split to per-child packet volumes on
   one cover value.

## Task and overlap

- **Card:** `uniform-transfer-audit`, refined to one native/complex-family
  implication.
- **Claim:** https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137702
- **Overlap:** the nearest work is #4178 (height recurrence at the Gaussian
  caller), #4171 and #4330 (root and ledger numbers), #4424 (cover and stock
  arithmetic), and #4375 (frame-child reading). None writes this cost
  induction.

## Credit

The construction and every audited statement are Cinna Davis's (#4100). The
histogram and words are PR4088's. The ledger cross-check is Nick Petalas's
(#4171), the height recurrence is Jose Manuel's (jmbarrancoml, #4178), the cover
audit is Matarener's (#4424), the frame-child separation is unpaidmoon's (#4375),
and the coverage map is Ryanson Jonathan's (pinterbanget, #4311). Prepared by JoyboyBrian with
substantial assistance from Anthropic Claude (Claude Code). New work is
Apache-2.0.
