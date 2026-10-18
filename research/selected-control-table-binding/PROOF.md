# Binding full-ring preparation to the iterative control evaluator

This is a structural compiler-interface lemma. PR2234 supplies the selected
request catalogue, full-ring projector preparation and chronological weighted
expressions; PR2310 supplies the iterative evaluator. We join those two
implementations without changing them. The weighted normal forms and diagonal
covariance are credited to source527, PR2159, this account's PR2160/2188 and
the intervening selected compiler work. They are hypotheses of this binding
lemma, not new results attributed here.

The exact versions are PR2234 `d047ef86fbc5b1614d3d8e2b8d3441413beab73f`
and PR2310 `a5258f548bfb6da71c3b72733fbbd2fb4995c929`. Both are pending
proposals. All used source bytes and notices are retained in `sources/` and
authenticated by `SOURCES.json` before import.

## 1. Inputs and theorem

Fix an odd prime q, a positive atom width w and R = Z/(q^w). Fix the selected
PR589 catalogue at the base in `SOURCES.json`. Start with n_0 > 0 atoms and a
constant unit a in R. Take a finite chronological chain of h descents. For
each descent there is a selected request, an exact low GL64(F_q) matrix and
a frozen high matrix in [0,q^(w-1))^(64 by 64). The complete raw matrix is
g = low + q high. The slot number counts every descent, including unit and
orientation children. No frozen field is deleted after a unit reset.

The chain metadata must satisfy the consumer finite-format bounds, checked
by `Program.extents`. Each event must be one of the actual children emitted by PR2234's
`residual_plan` for its current expression and low matrix. In particular:

* A good event has the selected rank r, f = floor(n/64) > 0 and child size rf.
* A paired-diagonal event has field 0 <= j < 127, child size f, and reversal
  exactly when j >= 64. Its branch is fallback, as established by the low
  matrix. Arbitrarily choosing the opposite orientation is not a legal event.
* A unit event has size f; an orientation event has size floor(f/2) > 0.
  Each resets the weight to the constant 1 and increments the global depth.

Assume the named producer normal forms give the following coefficients from
the FULL unweighted matrix: good pivot vector delta, and fallback terminal
diagonal d with final original-row permutation pi. Assume the producer's
actual-label formula P = g sigma P0 sigma^-1 g^-1 and weighted normal-form
identities hold. The adapter verifies the two implemented projector routes
agree and checks that the chosen descent occurs in the emitted low macroplan;
those finite runtime checks do not replace proofs of the producer algorithms.

**Theorem.** `compile_chain`, followed by the unmodified PR2310 `evaluate`,
returns the same unit weight as the actual PR2234 generated expression for
every valid final atom index. It reads only coefficient tables at their
original live global slots, makes no request for the current fresh matrix or
unused stock, and restores the table head. Numerical high fields at and before
the last reset need not be prepared. Replacing them while retaining the exact
low/request specifications cannot change the result.

This algebraic theorem does not need the relation w = ceil(e^(17/10000)).
When using PR2310's cost bound, that relation and all its other physical
premises must be supplied separately. The finite fixtures here do satisfy
the relation with e = w n_0; width one is tested only at the root n_0 = 1.

## 2. The exact table interpretation

For a good event, put its r full-ring pivots in table entries 0 through r-1
and pad the remaining 64-r entries with 1. Pad the unused diagonal with 1
and unused permutation with the identity. Since an admitted final index
i < rf has floor(i/f) < r, no good evaluation can read a padded pivot.
The consumer computes

    child(i) = parent(i) delta_floor(i/f).

This is precisely the source expression's formula. Restricting delta to its
residue modulo q changes valid weights; the replay includes such a witness.

For a pair event use all 128 entries of the FULL unweighted elimination's
terminal diagonal and final original-row permutation. For t in [0,f), define

    b(row,t) = parent(row*f+t), if row < 64; otherwise 1.

At a physical child index i, let t=i for a head field and t=f-1-i for a tail
field. The consumer computes

    child(i) = d_j b(pi(j),t) / b(j,t).

These are units, so division is defined in R. It is the source FallbackPair
formula, including the complete parent coordinate and physical reversal.
The final row permutation cannot be replaced by an identity just because
the original residual is an involution. The finite control uses an actual
selected fallback with a nonidentity permutation and a nonconstant parent.

For completeness, diagonal covariance explains why this is the relevant
weighted pivot: at a fixed atom column t, let B_t be diagonal with the 64
incoming weights followed by 64 ones. During elimination the weighted state
is B_(pi_current,t) M_current B_t^-1. Multiplication by units preserves the
first available unit-pivot itinerary. The final weighted diagonal is
d_j b(pi(j),t)/b(j,t). This is the predecessor's covariance argument. Our
separate oracle actually eliminates B_t M B_t^-1 and compares all 128
diagonal entries and the full original-row permutation in the listed cases.

## 3. Extents, resets and source binding

Induct on chronological events. Before an event, the compiled Program extent
and the source Expression extent agree. The good and pair size rules above
preserve equality. At a unit reset both use f or floor(f/2); the source starts
a new expression with `birth_depth = old_depth + 1`, while the Program keeps
the earlier size steps and inserts a unit step. Thus their final sizes and
global depth agree even though their expression histories have different
representations. Every index requested by a good or pair continuation lies
in its parent's first 64f atoms. Remainder atoms are never read.

The source expression after the last reset contains only the suffix strictly
after that reset. The consumer's unit step also returns 1 without making a
parent request. Therefore no live evaluation reaches a table at or before
that reset. The adapter preserves those slot positions using valid neutral
pages but does not read their high matrices. It validates all historical
low/request specifications to establish that the recorded chain was legal.
The dead numerical fields themselves are outside the dependency graph.

Before making any numerical table, the adapter checks exact equality of
`FieldSpecification(q,w,request,low)` at the specified global slot. It also
checks membership in the selected catalogue, complete frozen-prefix length
and actual macroplan-child equality. This binds request identity, chart,
rank, low class, atom orientation and chronology together. A same-rank
request is not an interchangeable source. Page tags are local slot tokens
after these exact checks; they are not cryptographic source identifiers.
Table construction never receives unused-stock coordinates.

Starting at the final index, induction on the pending consumer request stack
now proves value equality. A root or unit event returns its stated constant;
a good continuation multiplies the matching parent value by the matching
pivot; a pair continuation evaluates its two ordered bank requests and the
matching unit quotient. These are exactly the three cases in section 2.
The predecessor reader returns the head to zero on every page read. Its
evaluator empties pending/value stacks before return and never writes page
contents. This proves the stated semantic and head boundary.

## 4. Independent evidence and its limits

The finite replay loads the actual selected word, hosting template and
geometry through the pinned PR2234 provider. It reconstructs 28,278 canonical
requests, 32 replicas and the 904,896-entry paid profile. This source binding
is attributed reuse, not another independent supplier census.

The new fixtures use selected MOVE, COPY and IDLE requests, every positive
selected paid rank (1 through 7 and 42), owner data/host charts, complete
low/high matrices and mixed histories with unit resets. Their sparse raw
matrix family is constructed by the predecessor fixture routine; it is not
an enumeration of all GL64 matrices, low classes, high lifts or descendants.
Large root extents are represented by integers; no huge payload is executed.

`oracle.py` imports no predecessor matrix or descriptor code. It constructs
the projector directly from the raw matrix, the source label and chart,
bypassing the producer's split basis. It obtains good weighted pivots from
the unreversed weighted projector by normalized forward elimination. For a
fallback it builds the full weighted 128 by 128 residual and uses normalized
Gauss-Jordan elimination, contrasting with the producer's unnormalized
algorithm. Incoming parent values and catalogue/geometry decoding are reused
explicitly. This is independent local arithmetic evidence, not a code-disjoint
proof of the complete recursive supplier.

The finite receipt and semantic fault controls are in `RESULT.json`. Their
success corroborates the structural argument and identifies necessary
bindings. No flaw in the correctly bound predecessor evaluator is claimed.
The concurrent Discussion #2319 claim studies complete two-dimensional
dispatch; the present actual selected-dimension coefficient audit is a
separate restricted interface check, not priority for that broader program.

We do not execute complete payload passes, owner packets, recursive children,
parking or cleanup at the physical machine level. We do not prove a uniform
bit-operation bound for this Python adapter or transfer the selected exponent.
In particular, table preparation and the descriptor stack still need joining
to the complete stream dispatcher at each actual coefficient-preparation site.
No formal proof assistant, full selected cold replay or new kappa is claimed.
