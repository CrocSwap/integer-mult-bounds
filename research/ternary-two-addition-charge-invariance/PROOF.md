# Two-addition sublevels depend only on the charges

This scoped proof was produced by Nick Petalas. It answers a bounded part of
Open next question 1 in SHIN09-git's [PR #6712](https://github.com/CrocSwap/integer-mult-bounds/pull/6712),
head `03caa7f6cb5bd21c834024e9d81f6b43eb325b91`.
The header model, charge graph, separation criterion and scalar settlement
lemma are predecessor work. The new step is the elimination of hidden
zero-charge packets from every successful word of length at most two.

## Statement and model

Work over F3. Let u be a nonzero m-column, b a row, and W a d-by-m matrix,
with bu=1 and Wu=0. Here m>=2 and d>=1. Row dependencies in W are allowed.
The guards are the full affine family b+lambda W for lambda in F3^d.
They test every proper leading principal minor of
G(I-u(b+lambda W))G^-1. Permutations and nonzero coordinate scalings of G
are free. Each elementary row addition costs one. No auxiliary coordinates
may be added. Let C(u,b,W) be the minimum cost of a passing header.

Define scalar and vector charges x_i=u_i b_i and y_i=u_i W_:i.
For two instances of the same m,d with the same multiset of pairs (x_i,y_i),

    min(C(u,b,W),3) = min(C(u',b',W'),3).                 (T)

Thus the predicates C=0, C=1 and C=2 depend only on that multiset, in every
dimension. If equal-charge instances have different prices, the smaller
price is at least three. This does not prove full charge sufficiency.

## Three predecessor facts used

The determinant at a prefix S is 1-sum_(i in S)(x_i+lambda y_i).
For the full family, passing requires every y_i=0: every proper vector
prefix must be zero, and successive differences plus sum_i y_i=0 give
individual vanishing. When separated, a passing permutation exists exactly
when D=sum_i lift(x_i) is 1 or -2, where lift(0)=0, lift(1)=1, lift(2)=-1.
The latter follows by reading the scalar order backwards: its nonzero
partial sums must alternate between 1 and -1 and finish at 1.

For a separated state the exact additional price is

    L(D)=min(|D-1|,|D+2|)/3.                            (1)

Every addition changes two scalar charges with conserved sum modulo three,
so D changes by 0 or +/-3. This proves the lower bound even if intermediate
states are not separated. For sufficiency, merge two positive charges when
D>1, or two negative charges when D<-2. A merge sets one image coordinate
to zero and puts the sum on the other. The slope columns at active scalar
coordinates are zero, so these merges preserve separation. Enough pairs
exist until D reaches 1 or -2. These are the scalar facts proved in PR6712;
the short argument fixes their exact meaning here.

Finally move every free monomial operation to the end by conjugation.
Connect the two labels of each paid addition. Every connected component
conserves its total scalar and vector charges. In a successful word every
component therefore has initial total vector charge zero. The dual rows on
each component undergo an invertible transformation, so a nonzero slope
restriction on that component cannot become the zero restriction.

## Charge-visible operations

Whenever (x_i,y_i) is nonzero, u_i is nonzero. A free diagonal scaling
normalizes u_i to one. Its dual entries then become exactly b_i=x_i and
W_:i=y_i. Consequently a word touching only nonzero-charge coordinates
can be copied, with the same length, to every equal-charge instance.
Its unchanged coordinates and endpoint have the same charges. The final
passing permutation is determined by these endpoint charges.

The only possible difficulty is a word touching a coordinate whose entire
charge pair is zero. That coordinate may have zero u and arbitrary hidden
dual entries, or nonzero u and zero dual entries.

## Eliminate that difficulty at length two

Let h count the initially nonzero vector charges. Since their sum is zero,
h cannot be one. If h=0, equation (1) already proves (T) for all costs.
No word of length at most two can touch more than four coordinates, so h>4
is impossible for such a successful word.

If h=3, the three slope labels must lie in one component: a split would
leave a component containing exactly one nonzero vector charge. Two edges
connect at most three vertices in that component, so every touched vertex
has nonzero charge. If h=4, the two edges must be disjoint opposite-charge
pairs. Again every touched vertex has nonzero charge. These cases are
charge-visible and transfer verbatim.

It remains to consider h=2. Write the two opposite vector charges as y,-y.
A canonical one-addition merge sets one image coordinate to zero and
replaces their scalar charges a,b by 0,a+b. Let D_0 be the resulting global
scalar lift sum. It is separated. If a successful word of length at most
two touches only nonzero-charge coordinates, copy it as above. Otherwise
the two slope labels belong to one connected component, with two cases.

1. The component has two vertices. Its one-edge separation must be the
   canonical merge: with both initial image entries nonzero, cancellation
   forces the coefficient that zeroes the receiving image entry and
   transfers its entire dual charge. A possible second, disjoint edge
   changes the global scalar lift sum by at most three. A repeated edge on
   these two vertices touches no zero-charge vertex and was already covered.
2. The component has three vertices. Both edges are spent there, and its
   extra initial vertex has charge (0,0). Its slope restriction is nonzero.
   At the separated endpoint some slope column is therefore nonzero and
   its image entry must be zero. There are at most two nonzero scalar
   charges in this component. Their field sum is a+b. For field sums
   0,1,2, the possible integer lift sums of at most two charges are,
   respectively, {0}, {1,-2}, {-1,2}. Thus this component's scalar lift sum
   differs from lift(a+b) by at most three.

In either case the successful final global D is 1 or -2 and
|D-D_0|<=3. Therefore L(D_0)<=1. The canonical merge followed by at most one
scalar settlement addition is a passing word of length at most two in
every equal-charge instance, irrespective of hidden packets.

This proves transfer of the predicates C<=1 and C<=2. For a one-addition
successful word with h=2 the opposite slope labels must be its two endpoints,
so the canonical merge itself passes; there is no second edge or third
vertex. The C=0 criterion is already charge-only. Symmetry between the two
instances proves (T).

## Scope

This is a written all-dimension proof with finite corroboration, not a proof
kernel theorem. It applies to full affine families over F3 and the stated
free-monomial, unit-addition metric. It does not settle prices at least three,
partial guard families, other fields, added workspace, physical delivery,
restoration, the complete caller invoice or any selected framework assumption.
There is no new multiplication exponent.
