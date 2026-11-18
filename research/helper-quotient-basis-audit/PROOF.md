# Exact audit of the fixed helper restrictions

## Result and boundary

All 33 certificates in [QUOTIENTS.json](QUOTIENTS.json) preserve the
surviving normalized operator of the supplied parent graph. All 67
receiver identities hold over the rationals on arbitrary independent
entrances of their actual intermediate graph. The final graph has
1,468 public fields: all 400 main fields and 1,068 helpers.
The parent has 1,501 public fields and 1,101 helpers.

This is a separate implementation audit of the construction in
[PR #7713](https://github.com/CrocSwap/integer-mult-bounds/pull/7713).
It adds checking evidence. The construction and its gain are source
work. No new kappa or complete supplier admission is claimed.

## Independent variables and restriction

Give entrance r the formal basis vector e_r. A local formula
`sum(q_d h_d)` has vector `sum(q_d v_d)`. The checker evaluates these
vectors in dependency order. Each has integer coefficients and one
positive integer denominator; common factors are reduced exactly.
Vector equality implies equality for every rational entrance assignment.
No random test, modular surrogate or floating point is used.

The parent calculation checks every helper row is e_r and every main
row uses only main entrances. Its normalized endpoint is therefore
a direct sum of a main matrix and an identity on helpers.

For helper r let `s=sum(a_i x_i)`, with a_r nonzero. Substitute
`x_r=-sum(i!=r, a_i x_i)/a_r`. Every other entrance stays independent.
Every retained helper and main output keeps its value. The removed
helper output is discarded, so its productive target must be debited.

At each receiver the checker proves `s=sum(b_j h_j)` before the
substitution. All listed banks are at that receiver. Their sum is
zero on the restricted space. A nonzero pivot coefficient gives a
local expression for the removed paid bank. Replace every read of it
and delete its send. Donor charts and the complete dependency graph
are checked after each step. A replacement can use a later source
key if the resulting graph is acyclic. Its equations then have a
unique solution, and the restricted original values satisfy them.

For a transposed step, reverse scalar incidence edges, interchange
public entrances and exits, and reverse paid chart pairs. This gives
the normalized transpose, whose helper block is still an identity.
Apply the same argument and transpose back. This argument concerns
rational coordinates. It does not check physical chart phases.

Stable source labels remain through the sequence. Removed labels
are isolated as formal identities. Before compaction, each such
identity must have no other reader. Delete its row and column and
renumber the survivors. Every main label and first-plane partner
survives. The final forward matrix is compared directly with the
surviving parent matrix. An exact forward evaluation of the final
transposed graph also checks the transposed matrix.

## The two requested cases

Step 1 is forward, with entrance form `x264-x407-x434/4`.

| Chart | Checked receiver form | Removed key | Paid rank |
| ---: | --- | ---: | ---: |
| 441 | `h94689-h94690-h94703` | 94703 | 2 |
| 527 | `h95863` | 95863 | 4 |
| 127 | `h103556-h104045/4-h104100` | 104100 | 3 |

The lost helper rank is nine. This calculation visits 59 paid
ancestors and performs 12,293 coefficient products.

Step 13 is the first transposed step, after twelve forward steps.
Its entrance form is x559. At chart 807 the checked form is
`2h99290+2h104187`; at chart 3 it is `-2h97558`. Keys 104187 and
97558 have ranks three and six. The lost target rank is nine.
The calculation visits seven paid ancestors and performs 374
coefficient products. The forward-orientation control rejects this
certificate. The check uses its actual intermediate graph.

## Complete debits

Frame vectors are checked for binary independence. Every paid pair
has strictly nested spans. Every surviving helper has a strictly
larger output span. Rank is the dimension difference. Each step
removes at least two positive paid ranks whose sum equals the lost
helper rank. Direct counts before and after the sequence agree with
all accumulated certificate debits.

Per call, paid jobs fall from 6,121 to 6,054 and helper targets from
1,101 to 1,068. Both rank masses fall by 200. The unchanged published
fixed caller and root rows, with declared multiplicity 16, give:

| Quantity | Parent | Candidate |
| --- | ---: | ---: |
| Paid jobs | 101488 | 100416 |
| Productive jobs | 21152 | 20624 |
| Paid rank mass | 271568 | 268368 |
| Productive rank mass | 272896 | 269696 |

The surplus stays 1,328. Both complete histograms match the source
receipts. The checker does not prove fixed-caller admission.
For `0<t<1`, positive ranks with `sum(d_i)=d` satisfy
`sum(d_i^t)>d^t`: divide by `d^t` and use `u^t>u` for `0<u<1`.
Thus each step has a favorable signed power change under that model.
Neither this fact nor the histogram counts certify a kappa root.

## Evidence and residual obligations

The parent evaluation uses 9,280,471 coefficient products. The 67
receiver checks use 116,794. The final forward and transposed checks
use 9,657,314 and 7,948,543 respectively. Each final orientation covers
all 1,468 rows. The compact hash matches the source hash recorded in
[RESULT.json](RESULT.json).

Controls change one nonzero receiver coefficient in each of 67
relations, change each of 33 entrance pivots, omit each productive
debit, and use the wrong orientation for role 559. All are rejected.
Normal and optimized Python run the same explicit checks.

The parent graph was exported with the source constructor. This audit
checks its endpoint but does not independently reconstruct its raw
word or earlier cuts. The source proof and code were read first.
The new forward basis routine differs from the source reverse relation
expansion. Hash serialization uses the same standard-library topological
order; scientific basis evaluation uses the local dependency routine.

Physical phased operators, owned erasure, compiler lowering, precision
tape and analytic recovery remain outside this audit. The source
numerical crossing, scalar schedule, native port contacts and complete
multiplier were not replayed. This is not blind, human or formal-kernel
review. No selected assumption is discharged.
