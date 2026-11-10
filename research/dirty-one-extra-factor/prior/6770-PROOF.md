# The sharp joint interval envelope for the balanced dirty word

Prepared for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is a scoped written proof, conditional on the precisely
identified predecessor lemmas below; it is not a supplier-admission proof.

## Contract and result

Use Chafik Boukhalfa's unchanged #628 balanced word on n >= 1 formal
noncommuting factors. There is a protected source x, an unread target y,
and h = ceil(log2 n) distinct dirty scratch registers z1,...,zh, one per
depth. Siblings reuse the same deeper scratch. Every cut is at a complete
ideal leaf, `target += sign A_j source`.

For a matrix over the free noncommutative integer algebra, its coefficient
row mass is the sum of the absolute integer coefficients of all monomials
in that row, after collecting equal words. Define

```text
F(0) = 2,
F(h) = floor(h^2/2) + h + 2,  h >= 1.
```

For every ordered pair of cuts s,t in either word orientation, every row
of `P_t P_s^-1` has mass at most F(h). This is the sharp uniform envelope
at each height: Arham Tahir's #1374 family at n=2^h attains F(h), including
with commuting real scalar factors in {+1,-1}. At h=0 one leaf attains two.
Sharpness is over all n at a fixed height, not a claim that every n attains it.

Consequently the maximum joint-register operator norm is at most F(h) for
arbitrary contractive factors, without commutation. It is at most F(h) G
when factors commute and every subset product, including the empty product,
has norm at most G >= 1. The latter implication uses #1278's squarefree
interval theorem. The contraction implication does not require it.

The predecessor upper envelope was h^2+2h+3 for h>=1 (Nick Petalas,
#5872); the new gain is ceil(h^2/2)+h+1. #1374 already supplied both the
matching lower family and the explicit sharp-constant question. The new
content here is the upper proof, specifically the inverse-prefix sparsity
invariant and its use in chronological phase products.

## Imported premises and notation

Hanson Sun's #1085 proves that every prefix and inverse prefix, for both
orientations, has entries zero or one signed monomial; its source row and
target column are identity. For a positive call of complete product T,
the target/source coefficient of a prefix is 0 or T, and that of its
inverse is 0 or -T. A suffix has the same entry-size bound, because it is
the inverse of a prefix of the inverse word. Each such child row has mass
at most its number of registers. We use these assertions as written premises.

Write B for the ordered left product, A for the ordered right product,
and z for the parent's first scratch. The completed child maps are

```text
U = I + e_z B e_x^T,   V = I + e_y A e_z^T,
F = V^-1 U^-1 V U = I + e_y AB e_x^T.
```

Let P_a be a positive prefix of the left child and Q_b a positive prefix
of the right child. They act on the same deeper scratch W. #1278's four
positive-parent phase formulas are

```text
0: P_a;   1: Q_b U;   2: P_a U^-1 V U;   3: Q_b F.
```

At a child boundary either adjacent representation gives the same map.
The last representation includes the final boundary. Negative prefixes
have the same maps after complementary cuts and full-map multiplication.
All algebra below uses matrix action on column vectors, with chronological
execution multiplying on the left. No factor commutation is used.

## Lemma 1: scratch support has at most one direction per pair

For every positive prefix and its inverse, each scratch diagonal entry is
one, and for every pair of distinct scratch registers at most one of the
two opposite off-diagonal entries is nonzero.

Induct on the call. Completed outer maps only change z by a multiple of x
or y by a combination of x,z. Their left or right multiplication does not
change the scratch-to-scratch block of the active child, in any of the four
phase formulas or their inverses. For a left child z is its unread target:
its column in this block is the identity column. For a right child z is
its protected source: its row in this block is the identity row. The block
on W satisfies the induction hypothesis. Thus z cannot participate in
both directions of any pair, nor can any pair inside W. Its diagonal and
the deeper diagonals are one. This also proves the claim for an unused
reserved depth, whose row and column are identity. The leaf case is empty.

In particular, with k scratch registers the scratch-to-scratch block has
coefficient mass at most k(k+1)/2. #1085's unit entry-size premise is used
here: counting occupied entries is then counting their coefficient mass.

## Lemma 2: inverse-positive-prefix source occupancy is nonadjacent

For an inverse of a positive prefix, record which entries in its source
column are nonzero, in row order `(target,z1,...,zk)`. This binary string
has no consecutive ones. The leaf strings have length one, so the claim
holds initially.

For an active left child, let f in {0,1} indicate its inverse-prefix
target/source entry, which is `-f B`; let v be its deeper source-occupancy
string. Its induction string is `(f,v)`. Inverting the four phase formulas
gives the following parent strings:

| Phase | Inverse-parent source occupancy `(y,z,W)` |
| --- | --- |
| 0 | `(0,f,v)` |
| 1 | `(0,1,0,...,0)` |
| 2 | `(1-f,f,v)` |
| 3 | `(1,0,...,0)` |

For phase 1, `U^-1 Q_b^-1 e_x = e_x-e_z B`, because x is external
to the right child. For phase 3, `F^-1 Q_b^-1 e_x = e_x-e_y AB`.
For phase 2, applying `U^-1 V^-1 U` to `P_a^-1 e_x` leaves the z
coefficient `-f B`, changes the y coefficient to `-(1-f)AB`, and leaves
the W coefficients unchanged. These are exact free-algebra identities.
Since `(1-f)f=0`, all four strings remain nonadjacent. Padding unused
deepest registers adds zero bits, so unequal child sizes cause no exception.

There are therefore at most ceil(k/2) occupied source entries among the k
scratch rows. Their target entries vanish. Lemma 1 now gives the new bound

```text
H(k) := k(k+1)/2 + ceil(k/2) = floor((k+1)^2/2)
```

on the *sum of the masses of all scratch rows* of an inverse-positive
prefix. For k=0 this is zero. Left multiplication by the full positive
map changes only the child's target row. Hence a positive suffix
`U P_a^-1` or `V Q_a^-1` has the same scratch rows and the same H(k) bound.

## Lemma 3: cross-child products with the correct right factor

Embed a left-child map L on `(x,z,W)` and a right-child map R on `(z,y,W)`;
there are k shared scratch registers W. Every entry has mass at most one.
Assume that the rightmost factor in a product is either an inverse-positive
prefix or a positive suffix, so its W-row mass sum is at most H(k).
All its rows have mass at most k+2.

For R L, the y row is the sum of its own identity row, at most one copy of
L's z row, and at most one monomial multiple of each W row of L. Its mass
is at most `1+(k+2)+H(k)`. A W row is bounded by `(k+2)+H(k)`; the z row
is L's z row, and x is fixed. Thus every row of R L is bounded by

```text
H(k)+k+3 = F(k+1).
```

For L R, the z row is at most one x term, the unchanged z row, and the
weighted sum of W rows of R: mass at most `H(k)+2`. A W row has at most
one x term plus that W-row sum; the y row is unchanged from R. Thus its
maximum row mass is at most `max(H(k)+2,k+2) <= F(k+1)`.
The products use shared W throughout; no fresh scratch is introduced.

## All six phase pairs, both cut orders

Induct on n, keeping both cut orders. Both children have height at most
h-1; pad them to k=h-1 shared scratch registers as needed. Lemma 2 holds
with this padding. Same-phase intervals reduce to child intervals, including
the reversed order, and are bounded by F(h-1) <= F(h).

For distinct phases, the three adjacent pairs and their inverses are:

| Pair | Forward interval | Reverse interval |
| --- | --- | --- |
| 0,1 | `Q_b (U P_a^-1)` | `(P_a U^-1) Q_b^-1` |
| 1,2 | `(P_b U^-1) (V Q_a^-1)` | `(Q_a V^-1) (U P_b^-1)` |
| 2,3 | `(Q_b V^-1) P_a^-1` | `P_a (V Q_b^-1)` |

Every factor is a child prefix, inverse prefix or suffix. In each product
the rightmost factor is specifically an inverse-positive prefix or positive
suffix. Lemma 3 applies and gives F(h). This chronological restriction is
the point that the generic product of two arbitrary prefix bounds misses.

For repeated left phases, #1278 gives

```text
I_02 = P_b P_a^-1 + e_y A [e_z^T U P_a^-1].
```

The added row is external to the child. Its mass including its identity
entry is at most `1+(k+2)=h+2`; the other rows are child-interval rows.
For the inverse interchange a,b and negate the added term. Thus both orders
are bounded by `max(F(h-1),h+2) <= F(h)`.

For repeated right phases,

```text
I_13 = Q_b Q_a^-1 - [(Q_b V^-1)e_z] B e_x^T.
```

The new column x is external to the child. Its contribution to each row has
mass at most one, by the prefix entry-size premise for `Q_b V^-1`.
The reverse formula interchanges a,b and changes minus to plus. Hence both
orders are bounded by `F(h-1)+1 <= F(h)`, also at h=1.

The final pair is

```text
I_03 = Q_b P_a^-1 + e_y AB e_x^T,
I_03^-1 = P_a Q_b^-1 - e_y AB e_x^T.
```

For the forward direction, only the y row requires a refinement to Lemma 3.
Write `Q_b[y,z]=e A` and `P_a^-1[z,x]=-f B`, e,f in {0,1}.
If e=0, the target row has mass at most `H(k)+2` (its identity, the W-row
sum, and the added AB). If e=1, combine the added AB with the z-row
contribution before applying the triangle inequality. Its x entry is
`(1-f)AB`; its other entries are unchanged from A times the z row. The
combined row has mass at most k+2: when f=1 the x terms cancel, and when
f=0 the original z-row x entry was absent, leaving at most k+1 other
entries before the one addition. The y row is therefore bounded by
`1+H(k)+(k+2)=F(h)`. Other rows already obey Lemma 3.

For the reverse direction, Lemma 3 bounds the z and W rows of
`P_a Q_b^-1`; the extra term changes only the external y row. That row
is the y row of Q_b^-1 plus one x entry, of mass at most `k+3=h+2`.
This too is at most F(h).

The n=1 base consists only of identity and the single leaf shear in either
sign and has envelope two. This completes the induction for positive words
and both cut orders. An interval of the negative word is a positive-word
interval at the complementary cuts in the opposite order, so both word
orientations follow. The proof never expands a rounded leaf internally.

## Sharpness and operator substitution

#1374's pinned lower theorem uses n=2^h, scalar factors all +1 except
`A_(n-2^j-1)=-1` for 0<=j<=h-2, and chronological cuts

```text
a_h = floor(3*4^(h-1)/5),   b_h = (4^h+2)/3.
```

Its target row is exactly

```text
y + (-1)^(h-1)(1+floor(h/2)) x
  + sum_(j=1..h) j*(-1)^(h+j) z_j.
```

The absolute row sum is F(h). This predecessor theorem supplies all-height
attainment; our verifier independently corroborates that target row by
literal replay at small sizes and compressed exact scalar prefix matrices
at larger heights. No priority is claimed for the lower family or the old
n<=16 maximum census.

For arbitrary contractive factors every formal word evaluates to an operator
of norm at most one, so coefficient row mass bounds the maximum joint norm.
For commuting factors with all subset products bounded by G, first invoke
#1278's squarefree conclusion in the free algebra, then commute each
surviving word into a subset product and apply the triangle inequality.
Bounding individual factors by G alone is not sufficient. Sharpness of the
coefficient envelope and contraction-domain envelope does not claim equality
F(h)G for every fixed nonminimal choice of G.

## Trust boundary

The all-size conclusion is the written induction using #1085 and #1278
as stated premises, and #1374 for sharpness. Exact finite checks corroborate
the new invariants, six phase identities, interval bounds and scalar witnesses;
they are not the basis for extrapolation. Formal proof-kernel verification
and independent human review are unclaimed. This theorem concerns arbitrary
joint disturbances; Philippe Van Velzen's separate destination-only #2177
result is unchanged. Internal rounding, inverse-leaf preimages, precision,
physical movement, compiler, stock, analytic recovery and a complete caller
invoice remain outside scope. No selected framework assumption or kappa changes.
