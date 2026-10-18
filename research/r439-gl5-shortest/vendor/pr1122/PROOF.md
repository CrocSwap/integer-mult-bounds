# Finite composition and complete accounting

Write the local circuit, in execution order, as D, A, scatter, B, C on 111
source registers, 111 target registers and 439 arbitrary dirty helpers. COPY
uses a separate temporary, initially empty; every copied center remains
unchanged until its ERASE. The source and helper registers must be restored,
and target i must finish as its initial value plus source i over F2.

## Composition argument

The verifier propagates sets of formal input columns through each A, B and D
phase, separately and in both directions. Each chosen phase has exactly the
same F2 linear map as its PR589 phase on all 661 independent input registers.
Equality on this basis proves equality for all inputs by linearity. This
includes arbitrary dirt and target contents; zero-initialized helper tests
would not suffice. No equality of their positive integer lifts is assumed.

A and the z-destination operations of B write only source/helper registers
from source/helper registers. Here z denotes those registers. The new C is
the literal reverse of those elementary transvections, each at the full
frame, so it restores the same z map after scatter and B. Scatter and target
reads are frozen. Consequently each of the eight compositions has the same
full F2 endpoint. The implementation also checks that endpoint directly,
forward and backward, using explicit copied-center lifetimes. Independent
owning and native checkers provide further evidence for the stated finite
construction.

Algebraic equality alone would not establish physical frame legality.
The owning checker checks every nested climb and endpoint. Native records
then compare every register's entire ordered MOVE sequence with PR589,
including rank increments, and compare every COPY/ERASE record. This checks
the physical use of all existing sources and helpers, rather than inferring
unchanged cost from an equal helper count.

## Exact local bill

For the full composition the ADD counts are:

| Phase | ADDs |
|---|---:|
| D | 5,548 |
| A | 1,706 |
| Scatter | 527 |
| B | 800 |
| C | 2,071 |
| Total | **10,652** |

D consists of 236 helper preparation ADDs, 306 target preparation ADDs,
4,464 injection ADDs, 306 reversed target ADDs, and 236 reversed helper ADDs.
The copied PR1062 certificate records 162 components, including 74 two-leaf
stars. None of these operations is free. Their realized boundary is checked
directly rather than trusting the historical search score.

Relative to PR1062 only A and its part of C change: 2,130 becomes 1,706,
and 2,495 becomes 2,071. Thus the complete saving is 2 × 424 = 848. Relative
to PR589 the total saving is 24,305 − 10,652 = 13,653. The 12 B ADDs and 12
paired C ADDs already included in PR980's 872 headline saving cannot be
added a second time: the PR1062 B circuit replaces those same blocks.

The common-frame source access of each ADD, all preparation and restoration,
and all scatter ADDs are included in the literal stream. Frame transitions
and nine rank-seven COPY/ERASE pairs retain their original invoices. Paid
rank mass is 5,129. No helper, source projection, recursive child or other
record is added. In particular this is a change to the finite scalar bill,
not an improvement of the recursive moment.

For 5, 9 and 11 stages the scalar word costs are respectively 53,260,
95,868 and 117,172 ADDs. The corresponding bridge additions are 666, 1,998
and 2,664. Totals are therefore **53,926, 97,866 and 119,836**, with **45,
81 and 99** fresh copied-center events. The reverse stages account for 18,
36 and 45 of those events; they are not additional to the stated totals.
The unchanged native checker verifies these counts and all physical input
columns at each stage count. These are finite-stage invoices, not a complete
whole-call hosted-supplier invoice.

## Precision interaction

For a forward ADD, a cancellation-free upper bound adds the two operand
bounds. The signed inverse negates the scalar ADD coefficient, but absolute
value propagation still adds the same bounds in reverse order. COPY takes
the original's bound; ERASE closes the temporary. Starting each ordinary
register at bound one yields complete positive prefixes F and B. This
triangle-inequality bound applies to arbitrary inputs of absolute value at
most one; scaling gives the corresponding general input bound.

For the full composition the explicit stream and separate macro interpreter
agree on F = 15,223 and B = 3,910,388. The native exporter/checker agrees too.
The exact inherited expressions are:

```
local = 2^6 F^3 B^2
      = 3452394524099512658714524672 < 2^104
nine  = 2^18 F^5 B^4
      = 50109557170207398770972615575887331408085730734374912 < 2^192
```

The nine-stage formula and 18 bridge exponent are bound to the pinned
global_k.py syntax; the 192-bit production charge is checked in the pinned
PR589 receipt. The native local expression is compared as an exact integer,
not just by its bit length. These are conservative positive envelopes, not
claims of tight signed prefix norms.

The isolated PR1062 D gives 193 nine-stage bits and fails admission. The
same D with A gives 190, with B gives 182, and with both gives 176. This is
an explicit example where equal phase endpoints and smaller scalar count
do not suffice for precision admission. Every corner is fully repriced.
No unchanged per-phase bound or monotonicity assumption is used.

## Interface boundary

PR1062 D includes helper and target basis changes. It therefore fails the
original syntactic H2 shape test and the literal K extractor, exactly as
PR915/926/967 do. The source predicates are preserved and their false values
are required for the four affected corners. Semantic D equality is a distinct
finite result. H1/H3/H4/H5 and the other decomposed conclusions pass. This
package does not promote semantic equality to acceptance by an unmodified
whole-supplier interface, change the selected certificate, or claim a new
kappa. The remaining adoption and inherited theorem obligations are listed
in README.md.
