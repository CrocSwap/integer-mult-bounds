# Selected stock envelope at m=73: bound quantities and the exact missing shape lemma

**Card `selected-stock-envelope`, scope unchanged.** The drawn card asks: what
explicit uniform stock envelope does the actual selected stopped producer
supply at one bootstrap stage? This package takes the producer the card's
acceptance gate names — the selected **m=73 complex** producer, the one that
binds the shared saving and the selected kappa — at the native stage-1 domain
(`e >= 2^4785575287428`, `w = ceil(e^s)`). It is a construction attempt that
terminates at an exact, line-level missing lemma. No kappa, supplier, frontier
or selected-record change.

```sh
python3 -B research/selected-stock-envelope-m73/verify.py
```

Expected:

```text
PASS_SELECTED_STOCK_ENVELOPE_M73 sp72_bits=2628 families=14826 B=2642 ledger=16469->15555 halving=5329>4608 guard=18,17<=6562783 missing_lemma=A_B_rho_unbound controls=5 checks=45
```

Python 3.12, standard library only, exact integers, about one second. Every
input is byte-pinned in `SOURCES.json`; `verify.py` re-hashes all six inputs,
reimplements all arithmetic, and rejects five mutation controls. No retained
script is imported or executed.

## What is now bound to source at the m=73 producer

1. **Per-level stock.** The charged per-level stock allowance is exactly
   `B = 2628 + 14 = 2642` bits: the closed-form group order
   `|Sp(72,2)| = 2^1296 * prod_{j=1..36} (2^(2j) - 1)` has bit length 2628,
   and the physical-family count `14336 + 480 + 8 + 2 = 14826` has bit length
   14. Both numbers are recomputed from scratch here; the identity between the
   ledger's `B`, the symplectic order and the family split was reported but not
   decomposed in the retained stock bill
   (`research/selected-coarse-depth-stock/PROOF.md`).
2. **Depth.** The halving guard is exact: `73^2 = 5329 > 2 * 48^2 = 4608`, so
   two levels more than halve the child count at maximum child rank 48. The
   sharper coarse rate `43/26` per `log2` unit is the retained conditional
   result of PR 2105 (Sricharan Vagvala, `theon199`), and is imported here only
   as a named conditional.
3. **Both row ledgers, recomputed.** `2*2642 + 9909 + 252 + 1024 = 16469 < 20161`
   is the assembler's retained row charge, and
   `4370 + 9909 + 252 + 1024 = 15555` with `4370 = ceil(43*2642/26)` is the
   conditional refinement; the 914-bit difference is reproduced exactly.

## The exact obstruction (recorded missing lemma)

The retained fit chain needs H3 in the w-shaped normalization: a bound
`log_q S(e,w) <= sigma * w * (1 + log2 e)` uniform at the stage's widths. The
retained coarse-depth proof reduces the m=73 case to two shape premises and
states verbatim that they are not established
(`research/selected-coarse-depth-stock/PROOF.md`):

```text
log_q C(w) <= A*w + B,   log_q S_leaf(e,w) <= rho*w*(1+log2 e)
sigma <= (43/26)*(1-s)*(A+B) + rho
Actual A, B and rho are not established here.
```

This package searched for the missing `A` in the retained cover sources and can
now state the obstruction precisely. The only w-shaped per-level divisor in the
retained notes is the **ordinary** cover formula
`W(w) = W_0 q^{m^2(w-1)}` (`notes/three-stage-cover-bit.tex`), whose `m^2(w-1)`
digits are explicitly charged in the row reserve; it is written for the
ordinary cover and used at `m=64`. The complex cover note
`notes/three-stage-cover-complex.tex` ("Three invocation banks and a finite
orthogonal cover") states **no** w-shaped divisor at all: `verify.py` checks
the bounded no-match `q^{m^2(w-1)}` and `W(w)` absent from that pinned file.
The finite invoice charges `2*2642` bits per `log2` unit with no `w` term. So
the w-dependence `A`, the w-shaped constant `B`, and the leaf reserve `rho`
have no source binding for the m=73 complex stopped producer. Neither the
historical `m=120` increment `57,604` nor the external allowance `252` may be
substituted for them (card scope triggers).

The producer identification itself is a recorded ambiguity, not resolved here:
`docs/research/selected-bootstrap-scope-map.md` binds "the actual selected
stopped producer" of the four conditional reserve proposals to the ordinary
PR589 BIT `m=64` producer (maximum child rank 42, 28,425 physical roles),
while the card's acceptance gate demands an m=73 binding. Predecessors derived
conditional coefficients `8194` and `6748` for the m=64 producer under named
interfaces (PRs 2084 and 2120); those are not m=73 proofs, and this package
claims neither.

## Sufficient-guard comparison (consistency only)

Under either conditional ledger reading, `ceil(log2(8*sigma))` is 18 (16469)
or 17 (15555), far below the recorded stage-1 sufficient guard
`H_1 = 6,562,783`. This comparison is a consistency check of the kind the
acceptance gate requests; a large numerical headroom is not a proved envelope,
and the contribution is the bound quantities plus the missing lemma above.

## Reproduce and evidence limits

```sh
python3 -B research/selected-stock-envelope-m73/verify.py
python3 scripts/research_package.py --package research/selected-stock-envelope-m73 --check-only
```

`verify.py` checks 45 assertions including 21 source citations by substring,
and rejects five controls: `|Sp(70,2)|` in place of `|Sp(72,2)|`, a wrong `B`,
a row-ledger off-by-one, a rank-52 child that breaks only the halving guard,
and a wrong cover exponent. This is a finite source-bound arithmetic audit and
an exact recorded obstruction. It is not a supplier replay, not a cold replay,
not a stock implementation, and not a multiplication theorem.

## Open next questions

1. **Bind `A` (or prove `A = 0`).** Derive the w-dependence of the complex
   producer's per-level row divisor from the physical stock identity, or prove
   the divisor is w-independent. Relevance: it is the only nonlinear-shaped
   constant in `sigma <= (43/26)*(1-s)*(A+B) + rho`. First step: read the
   retained invoice sources behind the 14,826-family identity for any
   per-row digit charge. Blocked by: no such sentence exists in the pinned
   cover notes.
2. **Bind `rho`.** Find the complex analogue of the ordinary leaf reserve
   statement. Relevance: additive term of the composed coefficient. Blocked by:
   the retained complex sources state no per-leaf reserve recurrence.
3. **Producer wording.** Maintainer decision on whether "the actual selected
   stopped producer" means the ordinary BIT m=64 chain or the complex m=73
   producer. Relevance: determines which of the two coefficient families the
   outer proof must cite.

## Credit and attribution

Sricharan Vagvala (`theon199`), PR 2105, supplied the exact complex coarse
depth thresholds, the sharp `43/26` rate and the conditional stock bill with
the `16469 -> 15555` comparison; this package recomputes its arithmetic
independently and binds `B` to the group order and family split. Adam Gall
(PR 2084, `adamgall`) and Nick Petalas (PR 2120, `petalas`) supplied the
conditional m=64 parent-stock coefficients `8194` and `6748`. Josie Elliston
(PR 1965) and ToikY (PR 1990) supplied the fourteen headrooms and the
factor-16 fit extension whose source boundary names the uncomputed
coefficient. Hiroki KUMAZAKI (PR 2972, `kumagi`) closed the cutoff-pair
arithmetic and left the coefficient unresolved; Riquelme Soares (PR 2931,
`hevlyo`) supplied the stage-3 pair. The selected BIT supplier is
DreamingOfClouds's PR 589; the m=73 complex profile and the Sp(72,2) stock
factor belong to the retained selected invoice lineage
(`research/community-frontier1094-audit/ASSEMBLY.json`, retained engines).
Philippe Van Velzen's stage-1/stage-2 conditional envelope chain (discussion
#1166, 2026-10-14/15) informed the reading of the ordinary producer; no
result of that fork chain is claimed here.

Aaron Wang, with help from opencode (substantial AI assistance; no model named;
no independent human review claimed). New material is Apache-2.0; retained
predecessor files keep their original attribution.
