# Verification record and limits

The four commands in VERIFY.json were executed through
`python -B scripts/research_package.py --package research/current-rounded-positive-leaf`.
All four passed, normally and under `-O`; each had a 120-second cap. The
package metadata/provenance check also passed. The command started at the
20:17 UTC checkpoint and its completed success was observed at 20:20 UTC on
2026-11-09. These are observation timestamps, not per-test benchmark times.

## Arithmetic and interface evidence

`check_interfaces.py` uses independently constructed signed bitstrings and
integer/Fraction reference rounding, separate from the production codec.
It physically checks every accepted preimage of every h-bit rounded output
for h=2..4,g=1..3: 392 integers. Thirty-six threshold/extreme controls place
an overflowing component after a valid zero component and require a true
overflow. All 180 signed input values for h=2..5,g in {1,2,5} are physically
lifted, compared with exact shifts, dropped, and recovered.

Thirty-two metadata cases use ranks 1..8, f in {1,2,7,31}, widths 2/3/17/31,
and both one and three coefficients per record. They check all 23 exact
values before and after private cutoff transport, the physical growth
formula, original-parent preservation and retirement. These metadata
specimens do not pretend to materialize their potentially enormous complete
fields. The actual source catalogue and every distinct rank are bound
separately. Five invalid ranks and three bad grants are rejected.

Two deliberate production-control mutations are detected by independent
oracles: dropping the rounding carry and suppressing signed-overflow
rejection. A larger then smaller actual kernel call has the same smaller
action count as a fresh run (1,903,955) while retaining a larger sum of
private visited extents (32,004 versus 16,373). Materialized array extents and
visited intervals are separately labelled. Forty-two wrapper Count leases
were simultaneously live at the measured peak, below the proved fixed pool.

## Complete small numerical executions

The seven fixtures in NUMERIC-RESULT.json total **25,146,787 literal physical
actions**. They exercise positive and negative upward half ties; two
columns; a rank-two positive child with original f=t=1; spectators and a
nonzero offset; multiple rows, outer multiplicity and coefficients per
record; and a late actual output overflow. Six return the complete Fraction
matrix answer. The overflow case has an earlier valid output prefix and
preserves the complete original input. Every case checks byte-equal parent,
origins, all 521 blank private roles, closed leases/views and ancestor bytes.

One fixture invokes the exact actual raw PAID binding at event 9896. Its
small leaf-local descriptor is **not** a valid full nine-coordinate/global
selected producer descriptor. None of these small witnesses is a 4096-record
selected packet, an enclosing compiler trace, or a full native MOVE. The
all-source and all-width statements are the explicit quantified proof and
inherited source contracts, not an extrapolation of these examples.

The independent Fraction oracle implements the exact phase-correct Gaussian
matrix directly; it does not import the retained Gaussian evaluator.
Complete containing-fibre norm preservation and the single-rounded eta_X
bound are checked exactly. The physical hardware is a retained literal
read/write/unit-move implementation, with checker-only visited-highwater
instrumentation. No bulk tape primitive or algorithmic speedup is inferred
from using a faster host representation.

## Review independence and remaining obligations

The lead separately reviewed the complete source join, signed/drop proof,
cutoff/record semantics, scope suspension, inventory and cost. Its additional
dynamic-drop and width checks are recorded separately in LEAD-REVIEW.md.
These are model-assisted checks sharing source context, not independent
human or formal-kernel admission. The new source guards authenticate 204
unchanged retained files and check exact Count/Tape/codec object identity;
they are not a general static compiler proof.

The full current producer, physical placement, total monomial interfaces,
global radius/precision, the conditional width mapping and every nonleaf
and analytic obligation remain open. Arbitrary interruption and malformed
late output are outside the staged-return theorem. No κ or selected
certificate is changed.
