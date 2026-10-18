# Restored helper stars on a fixed target basis

This is an exact finite circuit construction over F2. It does not establish
an all-size multiplication theorem, global circuit optimality, or a new κ.

Let `s` be the vector of 439 arbitrary dirty helpers and `y` the vector of
111 arbitrary targets. PR589's D boundary is `(y,s) -> (y + K s,s)`.
PR915 implements this through a target change of basis E, with 306 target
transvections: apply E, inject E K s, and apply E inverse. Its complete D
bill is `306 + 6,376 + 306 = 6,988` ADDs. The other phases cost 6,220 ADDs.

## Star class and identity

A component has one center a and one or two distinct leaves b. Its physical
preparation operations are `s[a] ^= s[b]`. Centers and leaves are disjoint,
and no vertex belongs to two components. In particular, a center can be
written twice, but no written center is read by another helper preparation.

Write H = I + N, where N has a one in row a, column b for each edge (a,b).
Every nonzero column of N is a leaf and every nonzero row is a center, so
N squared is zero. Therefore H inverse = H in F2. All the helper operations
commute, including the two operations sharing a center. The implementation
still records every restoration operation explicitly, in reverse order.

The chronological program is:

1. Prepare H s on helpers, paying one ADD per edge.
2. Prepare E y on targets, paying all 306 target ADDs.
3. Add `(E K H) (H s)` to the prepared targets, paying each nonzero coefficient.
4. Restore targets with E inverse, paying 306 ADDs in the reverse order.
5. Restore helpers with H inverse, paying one ADD per edge.

Its target output is `E^-1 (E y + E K H H s) = y + K s` and its helper
output is s. Source registers are never accessed by D. Nothing requires
clean helpers or clean targets. All D operations retain frame zero.
The other phases and their literal cleanup are byte-for-byte identical as
JSON fields to PR589. The original scalar input/output map thus follows
from substitution of this exact boundary.

## Complete scalar cost

Let M = E K and let `col[j]` denote its jth column. Multiplying by H changes
only a leaf column b, to `col[b] xor col[a]`. A center is never a leaf, so
center columns stay fixed. Distinct edges affect distinct leaf columns.
Consequently the complete incremental saving of an edge is exactly

`weight(col[b]) - weight(col[b] xor col[a]) - 2`.

The subtracted two pays preparation **and** restoration. This additive
score remains valid when two edges share a center; it would generally be
invalid if a leaf were subsequently reused as a center. The verifier rejects
that geometry. No unpriced helper, temporary register or source operation is
introduced.

The candidate has 221 edges, 64 two-leaf stars, 93 one-leaf components and
61 unused helpers. Its transformed matrix weight is 4,509. The complete bill is:

`6,220 + 221 + 306 + 4,509 + 306 + 221 = 11,783 ADDs`.

This saves 1,425 against PR915, 197 against the incorporated PR926 circuit,
and 12,522 against selected PR589. The same-seed degree-one control costs
11,983; the star mechanism saves 200 relative to that control. These are
alternative D implementations; their savings must not be added.

## Precision and recursive accounting

The positive interpreter counts every ADD and the retained COPY/ERASE
operations in both orientations. It gives F = 72,847 and B = 10,394,084.
Exact integer checks give:

`64 F^3 B^2 = 2672929057893220568931365420032 < 2^104`, and

`2^18 F^5 B^4 = 6276870480677531528435239117197771736166837152483102425088 < 2^192`.

The second expression is tied to the pinned nine-stage source formula,
including its 18 bridges and charged 192 bits. It uses approximately
99.996316% of that ceiling. This small margin is checked exactly, not by
rounded bit counts. No extra precision headroom is claimed.

The unchanged native exporter/checkers must confirm all per-register MOVE
sequences, COPY/ERASE records, 439 helpers, nine copied totals, paid rank
histogram, rank mass 5,129 and 5/9/11-stage bridges. These checks preserve
the inherited paid recursive profile; ADD savings do not imply a larger κ.

## Scope and obligations

As in PR915/926, original syntactic `H2_D_frame0_targets_from_helpers` and
literal `K_equals_D` are false for this interleaved D implementation.
They are reported as false by the unchanged owning checker. The new evidence
checks the semantic arbitrary-input D map instead. The remaining original
H1/H3/H4/H5 and decomposed conclusions pass; no existing predicate is relaxed.

Adoption requires reviewing that semantic substitution, emitting and auditing
the changed complete hosted supplier, and regenerating the complete finite
and precision invoices and outer assembly. All-size/compiler, common-label
and mutable-source realization, hosting, precision/tape and analytic
assumptions remain. This package performs finite symbolic and native checks,
not proof-assistant verification of the multiplication theorem.

The bounded search finishes one greedy scan in each of two classes, maximum
one and two leaves. It scores every ordered pair but does not enumerate all
star forests, all tie orders, larger stars, changing target bases, or arbitrary
XOR circuits. It proves neither a minimum nor an impossibility result.
