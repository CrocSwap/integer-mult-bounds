# A paid two-register ADD retiming in the P104 physical dual

**One finite construction, no new supplier or kappa.** This package crosses one
of PR2662's fixed ADD barriers by changing the common chart of **both** operands.
The complete word keeps its exact physical boundary and all scalar operations,
while replacing `H6 + H7 + 2H1` by `H7 + H8`. Its paid rank mass stays 3542;
its local recursive child sum strictly decreases for every `0 < p < 1` at a
fixed caller width. This answers one concrete two-register-compensation handoff
in [Discussion 2619](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619).

The starting construction is commdata2338's
[PR2662](https://github.com/CrocSwap/integer-mult-bounds/pull/2662), exact head
`b67542b2896c21106f3945673bbf5b6e131408cc`, building on ywz65's physical dual
[PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586), head
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`.
Their complete boundary, original endpoint fusion, and native ancestry remain
credited; none is claimed anew. Predecessor WORD, README and RESULT bytes are
retained unchanged and pinned in `PREDECESSORS.json`.

## Exact change

Indices below are zero-based in the retained PR2662 word. Let

```
A = span(400,80),                 dim A = 2
E = span(391),                    dim E = 1
B = span(258,130,64,32,16,10,6,1), dim B = 8
D = F_2^9,                       dim D = 9.
```

Both A and E are contained in B. Event 4644 is
`X90 += N90/2`, with both operands in B. Replace these four transports:

| Role | Original events | Original route | New route just before the ADD |
|---|---|---|---|
| X90 | 3897, 5152 | A -> B -> D, ranks 6+1 | A -> D, rank 7 |
| N90 | 4643, 4645 | E -> B -> D, ranks 7+1 | E -> D, rank 8 |

Perform the unchanged ADD in D. The later `X90 *= -1` at event 5048 keeps
its position and coefficient but its chart annotation becomes D. No other
scalar/private instruction changes. The resulting full word is `WORD.json`;
`model.rewrite` regenerates it from exact predecessor events and checks the
intervening dependencies, including source reads.

## Proof of the physical identity

Use PR2586's canonical dual charts `Delta_W = conjugate(Gamma_W)` and define
`T_VU = Delta_V Delta_U^(-1)`. These are exact linear operators on each
512-address physical register. Put `S_c(x,n) = (x + c*n,n)`, with `c=1/2`.
The same transport applied to both registers commutes with this scalar ADD:

```
diag(T_DB,T_DB) S_c = S_c diag(T_DB,T_DB).
```

Consequently the original two-register fragment is exactly

```
diag(T_DB,T_DB) S_c diag(T_BA,T_BE)
  = S_c diag(T_DA,T_DE).
```

The statement holds for arbitrary inputs and includes global phases. It needs
both operands; moving just X90 would be incorrect. The literal dependency scan
shows that X90 has no use between 3897 and 4644 and only its sign between 4644
and 5152; N90 has no other use between 4643 and 4645. Operations on other
registers commute with these transports. The scalar sign also commutes with
transport. Thus the local equality embeds in the entire word without changing
its public boundary, dirty-helper restoration or any private lifetime.

The two new exact native recipes in `NATIVE.json` are generated with the
retained Clifford compiler. The separate retained Gaussian interpreter checks
their signed Pauli actions, phases, and all 512 basis columns each. The
independently written checker also verifies every column against the literal
old two-edge composition and checks intrinsic block ranks 7 and 8.

## Complete local invoice and moment

| Quantity | PR2662 | This word |
|---|---:|---:|
| Events | 5270 | 5268 |
| Positive transports | 1942 | 1940 |
| Scalar ADDs / signs | 3104 / 208 | 3104 / 208 |
| Exact private zero erasures | 8 | 8 |
| Paid rank mass | 3542 | 3542 |

The new complete profile is

```
1502 H1 + 58 H2 + 74 H3 + 93 H4 + 57 H5 + 56 H6 + 91 H7 + 9 H8.
```

Its exact difference is `H8 - H6 - 2H1`. For `m>0` and `0<p<1`, strict
subadditivity gives `8^p < 6^p + 2^p < 6^p + 2`; hence the change in the
unnormalized child sum is `(8^p - 6^p - 2)/m^p < 0`. Dividing by an unchanged
positive role count preserves the sign. This proof needs no floating-point
threshold or root calculation. Equality at p=1 is the unchanged rank mass.

This is the complete **local positive-child** bill. Physical address/scalar
work, actual owner windows, idle and residual costs, intrinsic adapters,
precision/tape, rounded strict-zero erasure and all-size admission remain
unpriced or inherited obligations. Retiming changes which frames are held
between these events, so old hosting or precision claims cannot silently be
transferred. No favorable full supplier moment is inferred. The underlying
forward construction still corrects only two of 104 rows; the other 102 retain
Gram/2. The selected frontier is unchanged.

## Reproduce and validation scope

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -O -B research/p104-dual-add-retiming/verify.py
python3 -I -O -B research/p104-dual-add-retiming/independent_check.py
python3 -I -B research/p104-dual-add-retiming/verify.py --regenerate
python3 scripts/research_package.py --package research/p104-dual-add-retiming
```

The primary sparse Fraction replay checks the source and candidate against the
E8-derived full logical map, all 128164 endpoint coefficients, 150 arbitrary
dirty helpers, every chronological frame and eight exact private zeros. The
separately authored dense scaled-integer checker reconstructs the candidate
independently, checks the same complete endpoint, and performs 2048 Gaussian
column equalities against direct and composed chart transports. It imports
none of the candidate model, builder or primary verifier. Both intentionally
reuse the pinned native interpreter; they are not independent implementations
of that interpreter or the entire inherited compiler stack.

Controls exercise one-operand retiming, stale ADD/sign charts, changed scalar
coefficients, wrong phase, undercharged compensation, new dependency reads and
broken private cleanup. `test_verify.py` checks Git-free relocated replay,
actual source/executable/receipt corruption, output refusal and unchanged files
after normal verification. All external source bytes are authenticated before
retained interpreter/compiler code is executed directly from those bytes.
Regeneration compares complete JSON content. Default verification writes no
artifacts; `--out NEW.json` refuses an existing file.

The unchanged native recipes and original physical-dual theorem are inherited
from the exact predecessor chain; this package does **not** rerun their entire
native cold replay. No proof-assistant, independent human, hosted CI, global
supplier, optimality or practical runtime result is claimed.

## Selection, evidence status and credit

The user explicitly chose endpoint work after the initial catalogue draw
`3589f7a12b6aed66c34e4be4895a9263` selected complex mechanisms. An exploratory
floating-point screen considered 447 neighboring-frame proposals at 288
blocked endpoint ADDs. Its 80 negative scores were proposals only, not
certificates. This package establishes **only the single X90/N90 change**;
it claims neither a certified census nor an optimal choice among them.

Scientific base: canonical main at the implementation checkpoint,
`6bd33bc0b87a01e9c9d8b1c01576f3ddbcaee850`, priority revision 5. The earlier
exploration used `b5ea56e0a5ac4552166253b1fa4be0753bb38c30`; refreshed guidance,
selected record and relevant native inputs were unchanged. The final refresh
at 2026-10-15 18:04 UTC found main
`719105847d558bc5538d7f005e7ca7fcc6201e31`; the guidance, task catalogue,
selected record, package runner and relevant native inputs still matched.
The scientific baseline and historical source pins are intentionally retained.
`TASK.json` records
scope, overlap coverage and publication status. Live overlap was limited to
the 100 most recently updated open PR bodies, the relevant discussion and
local notes/ledger; full authenticated remote pagination was unavailable.
This does not establish novelty or cover unpublished work. No retrospective
public reservation is claimed.

The final overlap refresh found ywz65's concurrent
[PR2712](https://github.com/CrocSwap/integer-mult-bounds/pull/2712), head
`afa5d6649460dcdb93489babd74f0ee9d01a4911`, whose proof and source windows
were inspected. It applies the same standard common-chart identity to two
early stars on Y0/Y1 and N2/N4/N33/N34 (source events 104--981), using ZERO
as their common chart. This package supplies a different late X90/N90 window
(3897--5152), using the full chart D, and a separately authored complete
checker. The mechanism itself is not claimed as new. Neither package is used
as a certificate for the other, and this package makes no combined-word or
additive-saving claim. PR2712 is concurrent context, not a live replay input.

Prepared for Vasek with substantial OpenAI Codex assistance in research,
proof, implementation, tests and writing. Two separate Codex agents independently
reconstructed the full candidate; one audited the mathematical implication,
and one supplied the retained dense/native checker. A third separate agent
reviewed the final proof, code and source bindings and found no actionable
defect. This is independent agent
checking, not independent human review.

Credit commdata2338/PR2662 for endpoint fusion and the ADD-barrier handoff;
ywz65/PR2586 and PR2497 for the complete canonical physical dual and logical
clean dual; PR2551 for the physical-boundary distinction; Nick Petalas/PR2550
for complementary frames; Ross Richardson/PR2445; commdata2338/PR2393;
Hiroki Kumazaki; Philippe Van Velzen; Chafik Boukhalfa/PR1991;
Rohan Arun/PR1972; Adam Gall/PR1940; Josie Elliston/PR1071;
Ali Romman/PR1125 and PR1862 for fixture/interpreter lineage; and icekylinx/PR531
and retained exact-compiler ancestry. The elementary commuting-operator and
concavity identities are standard. Retained source notices are unchanged;
new material is Apache-2.0 under the repository license.

## Open next questions

1. Can actual owner windows host the new rank-seven and rank-eight children
   and the changed holding intervals without repaying the local saving?
   First construct the X90/N90 window with all idle/residual charges. No such
   owner schedule is supplied here; this blocks any supplier-cost claim.
2. Can the same simultaneous-operand identity be composed across several
   blocked ADDs? First check exact dependency-window compatibility, including
   shared operands, then regenerate a single complete word and native invoice.
   Preliminary individual scores do not establish simultaneous feasibility.
   Stop before further expansion unless the complete boundary/cost ledger
   gives a useful consumer and an explicit remaining budget.
