# The printed #4100 ledger boundary row uses tau_eff

**Scoped sentence proof. No new κ.** #4100 is not accepted. The selected
conditional result stays `0.00302015`.

## Result

On the one numeric balance printed for the #4100 union schedule, the boundary
row is `tau_eff = 2 + 10^{-64}`. It is not `tau = 45/16`.

UNION-SCHEDULE §4 gives, at a common `(eps, xi)`,

```text
S_u = xi + 1/2 - eps,    S_b = c + xi - eps,    c = (3 - tau) / 2,
```

so `S_b - S_u = c - 1/2`. GAUGEFREE-INTERIORS §6 prints the 14-digit point

```text
eps = 0.99999437577296,  xi = 0.50167412128176,  beta = 0.99664613320944
```

and UNION-SCHEDULE §5b prints its half-up rounding to seven decimals,
`0.9999944`, `0.5016741`, `0.9966461`, at `tau_eff = 2 + 1e-64`. From those
14 digits the union saving is exactly

```text
S_u = 1049840943 / 625000000000 = 0.0016797455088,
```

which matches the displayed kappa prefix `0.001679745508802299` through
`0.00167974550880`.

At `tau_eff` the two rows differ by `5 · 10^{-65}`, inside the paragraph's
joint margin of about `10^{-64}`. At `tau = 45/16` they differ by `13/32`,
and the boundary saving on this point is `-0.4045702544912`. The sentence
that the union and boundary rows both bind is false at `45/16`.

`tau = 45/16` remains the dense Strassen exponent in `GAUSSIAN.md` and in
FINE-PRIME §6. That paragraph says the cost needs no structured inverse.
The short-field layout sentence sits later, on the union-cost paragraph.
UNION-SCHEDULE §6 assumes that row-field movement and says the note does not
change the boundary matrix exponent. Copying the layout lemma in therefore
keeps the §5b boundary exponent, which is `tau_eff`.

[PROOF.md](PROOF.md) records the argument. `research/pr4100-row-field-ledger`
showed that both exponents absorb the movement and left this choice open.
That absorption is not recomputed.

## Scope

Card `uniform-transfer-audit`, refined to the exponent-naming question in
`research/pr4100-row-field-ledger`. Priority revision 7. Base
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. The #4100 text is the package
retained on that commit. Selected κ stays `0.00302015`.

This is item 3 of the ordered eligible list below.

## Ordered eligible list

Handoffs on Discussion #1166 through 2026-10-23T13:22Z were read first. The
fresh posts are authors' own CLAIM and DONE notes. They do not put an
unclaimed request ahead of the priority table. The list is the
current-priorities card order, and inside `uniform-transfer-audit` the #4311
shortest-list row order. Each row contributes the first still-open successor
of its latest merged package, then the second. A row is dropped when a merged
package, an open PR, an excluded unpaidmoon delivery, or a fork `cursor/*`
branch already answers it.

1. The PR2809 encoded continuation stack keeps `O_q(V)` visited space at the new `c` (`research/bit-stock-recurrence-audit`).
2. The stored narrow band has at most `2p` off-diagonal entries and the rounding meets `2^{-5p}` (`research/narrow-row-half-gap` question 1). The half-gap itself is #4648.
3. **This package.** Which printed boundary exponent the #4100 ledger uses when the layout lemma is copied in.
4. A word-level scalar inventory at the two excluded `p = 2` CRT corners (`research/crt-arena-batch-threshold` question 1). The full batch for `p >= 3` is already proved.
5. Compose that full-batch allowance with reservoir placement and the paid repair-key service (`crt-arena-batch-threshold` question 2).
6. Enclose the separator corners of the translated chirp origin (`research/gaussian-prime-origin`).
7. Extract the explicit density constant `C` and `k` for `mu` (`pr4100-row-field-ledger` question 2).
8. Replace the CRT repair-key premise by a literal tape program (`research/crt-mask-repair-bridge` question 1). #4644 joined the mask and left this arithmetic unpaid.
9. Carry that bridge to a many-target macro (`crt-mask-repair-bridge` question 2).
10. One matched QQ16 park/restore bill against the external-call protocol (`joint-query-controller`). The finite four-provider replay already has its own package.

## Evidence and reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/pr4100-ledger-boundary-exponent --check-only
python3 -B scripts/research_package.py --package research/pr4100-ledger-boundary-exponent
```

`verify.py` prints `PASS_LEDGER_BOUNDARY_EXPONENT`. It checks the rational
identity, both gaps, the seven-digit rounding, the sentence order, and the
rejecting control that `45/16` puts the boundary saving below zero. No ledger
program, no carving replay, and no proof kernel is run.

## Open next questions

1. Does a byte-identical `outer/check_ledger.py` regenerate this `tau_eff`
   point? Section 5b cites that script, and the #4100 tree does not contain
   it. The first step is a blob whose stdout contains
   `eps = 0.99999437577296`. Nothing here searches history for a substitute.
2. What explicit `C` and `k` satisfy `mu ≤ C (W/B) (log p)^k`? The
   predecessor left this open. Naming `tau_eff` does not supply the constant.
   The carving program is not an input here.

## Credit

The Strassen sentence and the union schedule are Cinna Davis's #4100.
The gauge-free parameter point is the vendored GAUGEFREE-INTERIORS note.
`research/pr4100-row-field-movement` and `research/pr4100-row-field-ledger`
are unpaidmoon's layout count and the substitution that left this choice
open. The coverage map is PR #4311 (Ryanson Jonathan).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
