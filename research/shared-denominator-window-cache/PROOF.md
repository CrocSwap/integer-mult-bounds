# Shared-denominator principal-window cache

This is a scoped written construction, produced by Nick Petalas. Finite tests
corroborate the implementation. Independent human and formal proof-kernel review
are unclaimed. No multiplication theorem or new kappa follows.

## Boundary and theorem

Let H be one fixed rational N by N source. For every row i, choose a positive
integer q_i clearing every denominator in that row, and put Z=diag(q) H. These
scales and the integer source Z are prepared once and retained separately. A
window J is an ordered list of m distinct source labels. An update removes its
first label and appends a label not in the retained list. The appended label may
equal the removed one.

Assume the old principal window Z[J,J], the retained principal window B, and
the incoming principal window are nonsingular. The empty retained matrix at m=1
has determinant one. The predecessor's weighted strict diagonal dominance is
one sufficient all-window premise. We cite that premise without replaying its
scientific checks; this construction also applies outside that class whenever
these exact nonsingularity conditions hold.

After one exact initialization, the cache stores

    d = det Z[J,J],        A = adj Z[J,J].

Its inverse output is represented exactly by

    H[J,J]^-1 = A diag(q_J) / d.                         (1)

A slide updates d,A with integer additions, multiplications and exactly
2(m-1)^2 exact integer divisions. It uses O(m^2) arithmetic operations and
O(m^2) live integer fields. The inverse coefficient state contains m^2 integer
cofactors and one signed common determinant. It therefore removes m^2-1
per-entry denominator fields compared with m^2 individually stored rationals.
This count excludes labels, source storage, row scales, initialization scratch
and materialized outputs. It counts representation fields, not distinct heap
objects. Common cofactors can be larger than individually reduced numerators;
no total-bit-space or runtime improvement is asserted.

Equation (1) follows from Z_J=diag(q_J) H_J. The row scales occur on the RIGHT
of the inverse, so they multiply columns of A. A left multiplication here would
be wrong for a nonsymmetric source.

## Delete the outgoing coordinate

Simultaneously permute rows and columns to move the outgoing coordinate last.
This does not change the determinant. Write the correspondingly permuted cache
and source as

    adj M = [ E  f ; g  b ],      M = [ B  u0 ; v0  a0 ],
    d = det M,                    b = det B.

The last equality is the bottom-right cofactor identity. Since M and B are
nonsingular, the Schur inverse identity yields

    B^-1 = E/d - (f/d)(d/b)(g/d).

Multiplication by b gives the deletion formula

    C = adj B = (b E - f g) / d.                        (2)

All quotients in (2) are integers because the left side is an adjugate of an
integer matrix. The implementation uses divmod and rejects a nonzero remainder,
rather than truncating. It performs (m-1)^2 such divisions. Negative d is legal.
For m=1, A=[1], b=1 and C is empty, so (2) needs no division.

## Border the retained matrix

Read the incoming column u, row v and diagonal a from the SAME integer source.
Let

    p = C u,         r = v C,         e = a b - v p.

The determinant formula for a bordered matrix gives

    e = det [ B u ; v a ].

The Schur inverse formula, multiplied by e, gives its adjugate

    A_new = [ (e C + p r)/b    -p ;
                         -r     b ],     d_new=e.       (3)

In detail, B^-1=C/b and the Schur complement is e/b. The inverse top-left
block is C/b + p r/(b e); the other blocks are -p/e, -r/e and b/e. Thus (3)
holds entry by entry over the rationals. Its top-left block is integral because
it is part of an integer adjugate. There are another (m-1)^2 exact divisions.
For m=1, e=a and A_new=[1], including negative nonzero a.

Equations (2) and (3) prove the state invariant by induction over every finite
sequence of legal slides. The induction does not retain an expanding product
of historic denominators. Both row and column order are part of the invariant.
Incoming singularity or a zero deletion pivot is rejected before publication
of a new state. The old immutable cache remains available after every failure.

These are classical Schur and determinantal-condensation identities. The new
contribution is their composition as a shared-denominator sliding cache with
an explicit persistent state, rational-source orientation and bounded integer
implementation. It does not claim invention of the underlying identities.

## Heights do not grow with the number of slides

Put C0=max(1,max_ij |Z_ij|), Q=max_i q_i, k=m-1, and

    L = m! C0^m.

Leibniz expansion bounds every stored determinant by L and every stored
cofactor by (m-1)! C0^(m-1), hence also by L. Retained determinants and cofactors
satisfy the same common bound. These estimates depend on the fixed source and
window width, not on the number of preceding slides.

A deletion numerator has magnitude at most 2 L^2. Each component of p or r
has magnitude at most k L C0. During evaluation of e, the absolute sum is at
most L C0 + k^2 L C0^2. Once e is formed it is a determinant and has magnitude
at most L. A bordering numerator is at most

    L^2 (1 + k^2 C0^2).

These bounds also cover partial sums by the triangle inequality. The integer
numerators in (1) have magnitude at most L Q. Thus stored and temporary bit
heights are polynomial in m, log C0 and log Q, uniformly over the slide count.
The quotient and remainder do not require an unbounded denominator chain.

If every input numerator and denominator has magnitude less than 2^B, row-wise
least-common-multiple clearing gives q_i <= 2^(NB) and
C0 <= 2^((N+1)B). Initial clearing is global-source work, not free per-window
normalization. Row scaling can substantially enlarge integers. Bit arithmetic,
source access, output formation and exact initialization must all be charged.

## Implementation and finite evidence

`initialize` validates the bounded rational source and distinct ordered labels.
It uses classical pivoted Bareiss determinant elimination and one dense rational
inverse to obtain the integer adjugate. No Fraction survives in the cache. This
adds a separately paid determinant computation to dense initialization. The
constructor also clears N^2 source entries, using row-wise denominator lcms;
the subsequent dense initialization is O(m^3) rational/integer arithmetic.
No faster setup is claimed.
The mathematical update accepts any exact initial adjugate/determinant pair.

`slide`, `delete_first` and `border` contain only integer arithmetic. They build
a new immutable cache and share the original source and row scales. The explicit
`materialize` adapter creates reduced Fractions only when requested; it is not
called by a slide. Storing its output reinstates per-entry denominators and its
additional output storage is payable. The integer numerator adapter costs
m^2 multiplications and leaves the shared determinant intact.

The implementation supports 1<=N<=32, 1<=m<=min(N,16), and at most 256 bits
per reduced input numerator/denominator. The written formulas hold for arbitrary
finite dimensions. New evidence enumerates its own sources and slides rather
than rerunning PR3872's scientific suite. A separate Leibniz/cofactor oracle
imports neither initialization nor slide arithmetic. It checks complete ordered
windows, signed nonsymmetric rational streams, both division pivots and the
source-row orientation. The verifier emits the enumerated counts and SHA256
bindings; no receipt is handwritten.

Power-of-Ten inspection: all loops are bounded by the validated dimensions,
fixed census domains or explicit 48/64-step streams, and no function recurses.
Every function is below 60 lines. Invalid source/label/pivot/quotient checks use
ValueError and remain active under -O. Frozen cache values confine mutation to
local construction. Returned quotient/remainder and pivot searches are checked.
There is no dynamic code execution or callback registration. Standard dataclass
construction is the only generated method mechanism.

Managed-runtime deviation to rule 3: CPython integers, Fractions during
initialization/materialization, tuples and temporary lists allocate dynamically.
The bounded dimensions and the height bounds above bound live arithmetic state;
a slide retains only a constant number of O(m^2) arrays. The caller must account
for any old cache states or materialized outputs it retains. Follow-up physical
integration must provide its own fixed storage allocator and include conversion,
allocation, erasure and routing costs. No such program is supplied here.
Warning-strict normal and optimized runs are registered; external static type
or lint tooling is not required by the repository replay contract.

## Remaining obligations

This is an arithmetic preparation component. It does not implement the actual
protected factor pages, a rounded Gaussian producer, a fixed-tape integer
arithmetic routine, dirty-helper operations, supplier admission or any of the
five retained framework assumptions. Production nonsingularity, initialization,
source row clearing, bit costs, page emission, input/output ownership, storage,
precision, movement and cleanup must be bound to an actual caller separately.
