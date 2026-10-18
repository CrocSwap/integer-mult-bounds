# Cleanup composition and clean return

All statements below concern the pinned finite R2 words and serialized native
records. Rational scalar execution and allocation of owned clean arrays are
interface assumptions. This is not a proof of a complete multiplication theorem.

## The checked native factors

Let V = C^512 and F = F_9 be the product of the nine coordinate square-root
translations. Each source warp specifies an invertible binary matrix G by
columns. With binary arithmetic, put Q = I + G^(-T) G^(-1), and define

    q(y) = sum_i Q_ii y_i + 2 sum_(i<j) Q_ij y_i y_j  (mod 4),
    K_G |x> = i^q(Gx) |Gx>.

The checker enumerates all 512 images to invert G and derives Q from inner
products of inverse columns. It never invokes the source warp constructor.
For every cleanup event with sign s and source operator j, its actual serialized
rank-zero monomial N_j,s is compared against

    N_j,s = F K_G^s F^(-1).

The source order is first F^(-1), then K_G^s, then F. The independent retained
kernel checks all columns of this identity using exact Gaussian integers and
a non-aliasing packed radix, including the scalar global phase. It also checks
the entrywise conjugate identity. Because these factors are unitary, entrywise
conjugation is inverse transpose. The kernel is Sagar Thakrar's credited
implementation, not new code or a formal proof assistant.

There are 72 used cleanup keys per provider. Both providers are authenticated
separately and select all 72 keys; exact whole-record/source/key cache reuse
leaves 76 distinct records across the pair. Matching a local numeric operator
ID alone never permits reuse. No claim is made about the other 108 serialized
warp classes or the 3,030 child recipes in each retained archive.

## Whole body, including arbitrary private inputs

The source-to-canonical map removes exactly the 72 removed original registers.
An original private register 704+h maps to Z at the compact index of h; it
never aliases the live L role with that same numeric index. All 91 private
roles are determined by the source's narrow terminal helpers. Every one of
the 5,208 source cleanup gates is matched to the actual emitted event, in
order, with its signs, rational coefficients, operand namespaces and frame.
The first 204 are also checked as the literal reversed inverse of R2's
restore, with private-role substitution. Thus a coordinated corruption of
both cleanup representations cannot bypass that inverse-prefix check.

Every accessed live role has the FULL terminal frame. The actual body accesses
429 live roles and 91 private roles. Let D apply F on these roles and the
identity elsewhere. Scalar additions and scalings commute with this common
change of coordinates. By the checked warp identities, each native gate is
D times its source gate times D^(-1). Successive factors telescope, giving

    M_native = D M_source D^(-1).

This is an exact equality on the whole vector space of the body, including
arbitrary values of its private coordinates. It follows by composition of
verified factors, without materializing a huge dense matrix.

For the inverse-transpose orientation, each ADD exchanges its operands and
negates its coefficient, each SCALE reciprocates its coefficient, and each
unitary warp is conjugated. Inverse transpose preserves chronological gate
order: (AB)^(-T) = A^(-T) B^(-T). Replacing D by its conjugate gives the same
composition argument for the separately bound dual stream.

This statement excludes the later residual post adapters. Their positions are
bound after all frees here; their operator identities were the scope of PR3202.
The earlier prefix and its eventual live source/helper restoration are separate.

## Every actual private free is clean

The new rational row interpreter starts all 632 live entrance arrays as
independent symbols and all 91 private arrays at zero. A row is a finite sum
of rational multiples of (input column, reduced noncommutative warp word).
Only adjacent inverse warp symbols cancel. This is computation in a free
group algebra, not a floating-point or finite-field sample. Left multiplication
by a group word is injective, so the warp step cannot silently merge two terms.

Every allocation, use and actual free is processed chronologically. All 91
private rows are identically zero immediately before their frees in both
orientations. All 112 target rows remain their original entrance symbols.
Binding also excludes every private access outside the cleanup phase, and
excludes direct cleanup access to non-FULL live helper roles.

Substituting the actual invertible K_G operators for the free generators
preserves zero identities. The common coordinate change D preserves zero
as well. Combining this with the previous native equality proves clean return
for every live entrance vector, conditional only on clean allocation and the
stated native/scalar interface. No reachable-state premise from the earlier
prefix is needed for private zero-return. The 429 forward and 397 dual changed
live rows show why this is not an assertion that cleanup alone restores all
original invocation inputs.

The full live boundary is serialized deterministically and hashed in RESULT;
every replay recomputes it. Fifty-two semantic faults run after authentication:
event sign/omission/namespace/order faults, native phase/translation/quadratic/
permutation/rank faults, an independently detected coordinated inverse-prefix
fault, private inventory/prefix-allocation faults, and wrong private writes,
nonzero early frees and dirty private entrances. Each must fail its named
predicate. This evidence remains author-checked and subject to code review.
