# Independent review of fixed-prime complete matcher descriptors

**Accepted within the stated fixed-template source contracts.** The exact
reviewed proof hash is
`cbf42e276c2d1b25d72064801b6f0c0fb1ecab2d7cb0f771640a8bc4301dc14b`.
This is separate orchestrator mathematical/source review with an independent
fraction-free-minor oracle. It is model-assisted review, not human or kernel
acceptance. No constructor or author scientific checker is imported.

## Local-ring construction and the exact alphabet

The pinned ordered-affine source lemma permits every rational coefficient
whose denominator is prime to q. Only coefficients used for multiplication
or division must also have unit numerators. This distinction is essential:
discarding an additive coefficient divisible by q changes the action at
higher prime powers. The complete matcher and its inverse are dyadic, hence
belong to the local ring of q-integral rationals for every odd prime q.

After k pivots, the untouched Schur block is invertible over that local
ring. Its reduction modulo the prime q is invertible over a field, so its
next column contains a unit. Selecting that row, scaling by the unit pivot
and clearing the column preserves q-integrality. The algorithm terminates
after N columns. Its finite rational list is independent of the subsequently
chosen exponent w. Applying the ring homomorphism to every q-power proves
the all-width conclusion; finite modular tests alone would not prove it.

If the elimination list is E1 through Em and acts on S-transpose, then
`Em ... E1 S^t=I`. The forward execution list must be the reversed list of
inverses. Its total operator on a column is S-transpose, giving right
multiplication by S on the original row. The inverse uses the original
elimination chronology. Both conventions have been independently replayed.

The theorem requires q prime. The executable checks an odd positive q and
the actual pivot/denominator conditions; it does not certify primality.
This is correctly stated as a caller premise. The determinant-one example
`[[3,5],[1,2]]` has no entry-unit first pivot after transposition modulo15,
so the field-based guarantee must not be generalized silently.

## The input-sensitive height bound

Let `S=A/D`, `D=2^s`, and `M=max(1,max|A_ij|)`. For the selected row order,
let delta_k be the determinant of its first k rows and first k columns.
Normalized pivot rows are Cramer ratios of k-minors. Remaining rows are
Schur complements, whose entries are a (k+1)-minor divided by
`D*delta_k`. The next pivot is precisely
`delta_(k+1)/(D*delta_k)`. Row swaps choose a different row subset/order,
which changes signs but not the determinant bound.

Clearing a column updates one row at a time. A row already updated has the
new checkpoint formula; an unprocessed row retains the old formula. Thus
the argument covers every coefficient actually recorded, not just completed
elimination stages. The newly normalized pivot row has the next Cramer
formula. The reciprocal of a scaling has the same numerator/denominator
bound. With `Delta=N! M^N`, every minor of every size is at most Delta,
and all recorded reduced numerator/denominator magnitudes are at most
`D Delta`. The stated
`K=s+N(bit_length(M)+bit_length(N))+1` therefore suffices uniformly in q,w.

The independent checker uses Bareiss fraction-free determinants, rather
than the author's rational elimination, to verify 23,112 selected pivot
minor identities. Every selected minor is a unit modulo its q. It checks
all emitted coefficient heights and both exact word identities for all
2,516 descriptors. This is finite corroboration of the Cramer/Schur proof,
not a replacement for that proof at arbitrary N or coefficient heights.

## Carry, inverse and coupling

For fixed low representatives, `g0 A-D h0` is divisible by q entrywise.
The rational carry therefore has denominator dividing D. Each numerator
after dividing by q has magnitude strictly below `NM+D`, since each low
entry is at most q-1. No denominator q remains hidden in that representation.
This yields the stated fixed carry size and the exact lifted identity.

The inverse must first recover the original low representative and subtract
its carry before applying the inverse linear word. Equivalently its carry
is `-C_S(g0) S^-1`. The displayed composition identity retains the order
of S and T and follows by expanding the same representatives. Width1
has no high-field service; the low permutation remains.

At a coupled off-diagonal contact, differing routes change the source row
to `g S_j S_i^-1`. Sharing the descriptor makes this g without identifying
or merging the two separately owned payload fields. The existing ownership,
external-weight and complete-job boundary contracts remain necessary.

## Source counts and what their cost means

For one high row, there are at most N(N-1) additions, N swaps and N unit
scalings. Even charging two ordinary interchanges for every addition gives
`N(2N(N-1)+N)<=2N^3`. Including all N^2 carry translations gives exactly
the conservative bound `N*N(N-1)+N^2=N^3` ordered shifts. The N high rows
use at most N^2 rational-unit scaling records. Inversion preserves these
categories and counts. All high coordinates, complete gaps and suffixes
are covered; the final compiler dimension must be used in these formulas.

A rational-unit scaling expands into numerator scaling, inverse-denominator
scaling and possibly sign reversal. It is not a one-bit instruction. The
integer bucket count can be exponential in the input height K, and the low
table can contain up to q^(N^2) entries. The proof explicitly keeps these
as fixed-template constants and retains their selection, scanning and
cleanup charges. It does not assert a new polynomial physical bound in N,K.

The source ordered-affine lemma already absorbs polynomial preparation in
the complete q-power target fibre. The candidate supplies bounded fixed
descriptors to that existing lemma. It does not prove its tape/ownership
premises anew or improve its previously stated 2N^3 tariff. The quantitative
large-prime condition and completed earlier-stage service remain in force.

## Independent evidence, provenance and limits

`independent.py` authenticates all nine retained inputs by SHA256, and the
seven published source entries carrying Git blob IDs by Git object hash.
The other two inputs are the already reviewed dyadic proof and complete basis
file, now published in #8092 at
`2fa1ba900f88ec6d32829eb69986cf585e3006af`; publication provenance should link
that exact commit without changing their frozen bytes.

The checker validates 5,032 exact forward/inverse word products, 23,112
fraction-free pivot minors, all rational coefficient domains/heights and
both direction invoices. Negative controls distinguish reversed forward
chronology, a low-zero shear that acts nontrivially modulo q^2, and the
composite-modulus pivot boundary. The author's separate checker adds the
larger modular carry and low-chart catalogue; those executions are not
relabelled as this reviewer's independent work.

The contribution is concrete source-bound descriptor certificates and
input-height/control accounting for the newly carried dyadic catalogue.
General elimination, fixed-rational routing, the ordered-affine lemma and
the prior full-GL bridge are credited existing work. This does not solve
the restricted #6201 factorization, growing outer prime avoidance, global
storage or a complete multiplication theorem. No new kappa is claimed.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
