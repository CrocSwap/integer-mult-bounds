# Semantic boundary, complete cost and the finite search class

All circuit identities here are over F2. Positive integer envelopes are a
separate calculation; cancellation in F2 cannot lower their invoice.

## Boundary identity on arbitrary inputs

Let `x` be the 111 source registers, `y` the 111 arbitrary target registers,
and `s` the 439 arbitrary dirty helpers. PR589's D has matrix K and endpoint
`(x,y,s) -> (x,y+Ks,s)`. PR915 supplies a fixed chronological word of 306
target transvections, with matrix E. It directly injects EK between E and
its inverse. Both K and E are reconstructed from pinned inputs.

Partition the helper coordinates into 152 unchanged pairs, 40 triples and
15 untouched singletons. Each triple joins exactly one original PR926 pair
to a distinct originally unmatched helper. Let H be the invertible map on
helpers obtained by the concatenation of the chosen component words. Each
component acts on disjoint coordinates, so no hidden connection between
components is needed. Inside a component the operations can fail to commute.

Perform these five steps:

1. Apply H to the helpers.
2. Apply E to the targets.
3. Inject `M = E K H^-1` from helpers to targets, once per nonzero coefficient.
4. Apply E^-1 to the targets.
5. Apply H^-1 to the helpers.

After step 3 the target is `Ey + E K H^-1 Hs = Ey + EKs`.
Steps 4 and 5 produce `y+Ks` and `s`. No step reads or writes x. This proves
the D boundary for arbitrary target and helper dirt. Chronological reversal
implements each inverse because each individual CNOT is self-inverse;
applying the component's original order is generally incorrect. A control
detects that mistake in the actual candidate.

For a chronological helper operation `s_d <- s_d + s_q`, write its matrix
as S. Extending H on the left changes the middle on the right by S:
`E K (S H)^-1 = (E K H^-1) S`. Thus column q, not column d, changes by XOR
with column d. The search uses this packed-column rule. The independent
verifier obtains H^-1 by Gaussian elimination and derives the columns from
that inverse. Full arbitrary-input column checks additionally test the
complete emitted D and its inverse against the original K.

## Complete finite bill

For a chosen helper component Q with preparation length l, its contribution
is `2l + wt((EK H^-1)|Q)`. The factor two pays both preparation and undo.
The target preparation and undo add 612, regardless of Q. Because the helper
components are disjoint, their column weights and costs add exactly.

The chosen schedule has helper preparation length
`152 + 38*2 + 2*3 = 234`, middle weight 4,540, and D cost
`2*234 + 2*306 + 4540 = 5620`. The unchanged A/scatter/B/C suffix costs
6,220, giving 11,840 complete ADDs and saving 140 relative to PR926.

The old and new D gates are at frame zero. They use only existing targets
and helpers already at that frame. The candidate changes no source access,
copied-total role, child profile or frame schedule. The literal exported
MOVE sequence of every register and all COPY/ERASE records are compared
with PR589, not inferred only from the endpoint identity. At 5/9/11 stages
the 140 local savings correspond to 700/1,260/1,540 ADDs; the unchanged
bridge and copy operations remain fully charged by the native checker.

These counts are finite compiler evidence, not a complete asymptotic
recurrence or a replacement global supplier invoice.

## Exhaustive small group and bounded larger search

There are `(8-1)(8-2)(8-4)=168` invertible 3 by 3 Boolean matrices. The
six directed CNOTs generate the group: row addition plus row swapping
(three additions) gives Gaussian elimination. BFS therefore reaches all
168 maps and gives a shortest representative for each, for its declared
generator order. No claim depends on an unstated synthesis heuristic.

The independent distance certificate consists of the 168 realizing words
and their lengths. Direct enumeration checks that every invertible matrix
appears once. For every directed generator edge, the two endpoint lengths
differ by at most one. Starting at distance zero for identity, these
inequalities show every identity-to-matrix path has length at least its
recorded length. Its realizing word supplies equality. This certifies the
unweighted shortest CNOT length, not a precision optimum.

For each original pair and unmatched helper the search evaluates all 168
maps using one such representative, totaling 1,774,080 scored alternatives.
It then performs one seed-12 tie-broken greedy pass over all positive-gain
alternatives, rejecting coordinate conflicts and failing integer guards.
The verifier independently repeats every score and the full pass. The 40
accepted changes are compatible by construction.

Different shortest representatives can have different positive envelopes;
longer representatives can also have different envelopes. Neither family
is exhausted here. Nor are alternate E, components of size four or more,
changes to an already accepted triple, or other greedy orders. No optimality
claim is made for the 11,840-ADD complete word.

## Precision and interfaces

Literal noncancelling execution in both directions gives F=72,399 and
B=10,464,656. The integer expressions in the README satisfy strict 104-bit
local and 192-bit nine-stage inequalities. Every admitted intermediate word
passes the same two inequalities. The staged native replay independently
agrees with both maxima, includes all bridge operations and rejects omitted
bridges. The 115 rejected alternatives are not evidence of a universal
obstruction; they fail these specific complete-word bounds at their turn.

Replacing D preserves the full finite endpoint because the new D agrees
with the original D before the unchanged suffix begins. Original gate-local
H2 and the literal K extractor still reject its internal form. Consequently
the construction relies on the same semantic D-substitution obligation as
PR915/926. Whole-hosted emission, precision allocation, supplier admission,
outer assembly and the selected theorem's inherited assumptions remain
outside this result.

The identity and exact finite checks do not formalize the full integer
multiplication theorem. Basis conjugation and semantic substitution are
predecessor mechanisms credited in NOTICE.md, not new claims of priority.
