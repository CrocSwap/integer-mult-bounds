# Exactly three swaps in the worst corank-one case

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let F be any field and m>=4. Let P in M_m(F) be idempotent of rank m-1.
At stage k=0,...,m-2 choose a nonzero entry in residual rows and columns
k,...,m-1, swap its row to k and its column to k, then clear below and to
the right by row and column additions. A nonidentity row swap and a
nonidentity column swap each cost one. All clearing additions remain.

This is PR4235/PR4245's pivot family in equal-head coordinates. If C reverses
the columns, an equal-head column index j corresponds to m-1-j in P C;
the prescribed tail position is m-1-k. No swap becomes a free relabeling.

**Theorem.** Every such P has a plan costing at most three swaps. For every
field and every m>=4 some P requires three. Thus s*(m,m-1)=3.

The result is a scoped written proof. It changes the pivot policy, and does
not audit the predecessor compiler or its census. The two elementary minor
identities below and Gaussian pivot/minor correspondence are classical.
Their use to obtain this sharp policy is the new step.

## Two minor identities

Write P=I-u v^T with v^T u=1. Such a factorization exists because I-P is a
rank-one idempotent. It can be recovered from any nonzero column of I-P
and one nonzero entry of that column. Put a_i=u_i v_i, so sum_i a_i=1.

For a coordinate set S, the determinant lemma gives

    det P[S,S] = 1 - sum_(i in S) a_i.

If equal-sized coordinate sets R,T differ by one index each, with
R\T={i} and T\R={j}, then

    det P[R,T] = +/- u_i v_j.

For the second identity, the common identity submatrix has rank |R|-1.
In the determinant expansion precisely one rank-one-update entry must
fill the unmatched row and column. Two such entries cancel by rank one.
This proves the formula including arbitrary signs and characteristic two.

For any fixed row and column order, Gaussian elimination has nonzero pivots
through stage m-2 exactly when every selected leading minor of sizes
1,...,m-1 is nonzero. Successive pivot values are ratios of successive
minors. This follows directly from the Schur determinant formula.

## One swap when the last product is nonzero

Suppose a_(m-1)!=0. Call k bad if the leading size-(k+1) principal minor
vanishes, equivalently sum_(i=0)^k a_i=1. The index m-2 is not bad because
its minor equals a_(m-1).

If there is no bad index, use all home pivots. Otherwise let f and l be
the first and last bad indices, and b=l+1. Then f<=l<m-2. Both a_f and
a_b are nonzero: the prefix immediately before f is not one, and the
prefix immediately after l is not one.

At stage f, exchange current columns f and b and make no other swaps.
For prefix sizes at most f the selected minor is the original principal
minor and is nonzero. For sizes f+1,...,b the selected row and column sets
differ by f and b, so their minor is +/-u_f v_b, which is nonzero.
For sizes at least b+1 the selected minor is again principal, up to sign;
all such proper prefixes lie beyond the last bad index. Every pivot is
therefore legal. This costs exactly one column swap.

## At most two preparatory swaps

Now suppose a_(m-1)=0. If all proper prefixes are good, no swap is needed.
Otherwise let i be the first bad index. Then a_i!=0. Simultaneously
interchange coordinates i and m-1 in the row and column orders. Think of
this as conjugating P by that transposition. Its product vector a' has
a'_i=0 and a'_(m-1)=a_i!=0.

Every prefix preceding i stays good. The size-(i+1) prefix now has the
same sum as the old size-i prefix, so it too is good. Hence all bad
indices for a' occur strictly after i. The preceding one-swap construction
for a' uses its column swap strictly after stage i, if needed.

This conjugation requires no early or out-of-family operation. Its two
swaps are performed together at stage i by choosing pivot (m-1,m-1).
All earlier pivot indices are fixed by the transposition, so their
elimination commutes with it. The new size-(i+1) minor proves that this
stage-i pivot is nonzero. Later apply the one column swap just described.
The total is at most two plus one. In particular both row and column
charges for the preparation are retained.

Finding all bad prefixes takes O(m) field operations after obtaining u,v.
Extracting u,v from P takes O(m^2) field operations. The proof gives an
explicit policy; it does not require an optimal-policy search.

## A sharp family over every field

For m>=4 take

    u = (1,1,1,0,...,0)^T,
    v = (1,1,-1,0,...,0)^T,
    P = I-u v^T.

Then v^T u=1, including in characteristic two. The final coordinate
m-1 is an isolated identity coordinate. The initial home pivot P[0,0]
is zero, and P[1,1] is also zero.

Every nonsingular size-(m-1) minor deletes one of the first three row
labels and one of the first three column labels. Indeed adj(P)=u v^T,
so a minor deleting row r and column c is +/-u_c v_r. Thus any complete
pivot plan must move an active label into the last row slot and an
active label into the last column slot. These require at least one row
swap involving that slot and one column swap involving that slot.
Clearing operations do not evade this statement: pivot/minor correspondence
refers to the selected original row and column labels.

Suppose the total cost were at most two. Those two required swaps would
be the only nonidentity swaps. Since the initial home pivot is zero, at
least one must occur at stage zero. Swapping only its row with the last
row gives pivot P[m-1,0]=0; swapping only its column gives P[0,m-1]=0.
Therefore both must occur at stage zero. The pivot is the isolated last
identity entry. Its clearing changes no other entry. The next home
pivot is still P[1,1]=0, requiring another swap. This is a contradiction.

The upper construction uses three swaps on this family, proving sharpness
for every field and every m>=4. This is an all-word obstruction within
the declared pivot family, not a finite search failure.

## Consequence and limits

PR4235's split-projector compiler over Z/p^w has the residue-field pivot
itinerary and lifts nonzero residue pivots to units. Applying this policy
to its corank-one residue therefore bounds its swap count by three.
The predecessor supplies the full-ring clearing/restoration and weighted
adapter contract; those results are cited, not rechecked here. Its
clearing ADD slots are unchanged. This is not a claim that arbitrary
matrices over a local ring have the same structure.

Corank one at m=64 has rank 63, outside the retained paid boundary r<=42.
This theorem does not lower the selected boundary's worst-case child
count or establish a new kappa. Higher corank, physical coefficient and
route preparation, encoded tapes, stock, precision, caller installation,
supplier admission and the full multiplication theorem remain outside
the result. The proof has no independent human or proof-kernel acceptance.
