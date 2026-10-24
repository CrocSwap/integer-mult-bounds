# Two negative plane queries cannot complete three roles

Use the complete three-role native model from POSITIVE-FIVE-PROOF.md.
Now exactly two of the five rational rank-one ADDRESS maps have negative
determinant. The target is z I3, with z=-I2. The proof gives a contradiction
from ADDRESS subset extrema. It also reduces every candidate to the finite
family in search.py. An independent direct replay of that family found
no word. The finite search is a verification check, not a proof dependency.

## A two-query target branch is necessary

Suppose no two-query ADDRESS subset gives z. Every target branch then
selects at least three queries. The extrema argument and normal-form
reduction in POSITIVE-FIVE-PROOF.md still apply to arbitrary real nonzero
determinants. In case 124, the candidate E=-C^-2 has eigenvalues -1 and
-det(C)^-2, so it has no fixed vector even if det(C) is negative.

The two surviving forms are A,B,C,A,B and A,B,C,C B C^-1,A, with CBA=z.
The determinant quotient of the complete word gives det(A)det(B)=1 and
det(C)=1. Thus A and B have the same determinant sign, and C is positive.
Each form has either zero or four negative queries. It cannot have two.
This is a contradiction. A two-query target branch is therefore necessary.

For rank-one rational maps g and h with h g=z, the equation h=-g^-1
shows that det(g)=-1: h needs an eigenvalue one, whereas its eigenvalues
are -1 and -1/det(g). The eigenvalues of g are then 1 and -1, so g^2=I2.
The maps in the two-query branch are opposite reflections R and zR.
They must be the only two negative maps in the word.

The determinant-sign dual-number character gives N_(negative 1) plus
N_(negative 2)=0. Thus their DATA projectors are equal. Common binary
DATA conjugation sets that projector to E00.

## The three positive maps are unipotent

The opposite reflections have determinant -1. Therefore the product
of the three positive ADDRESS determinants is one. A single nonunit
positive determinant is impossible.

If exactly two positive determinants are nonunit, their magnitudes are
reciprocal. The determinant quotient of the word has only those two
queries. The identity H_M(x^-1)H_N(x)=I forces M=N, by comparison of
the distinct group terms 1 and x^-1.

If all three positive determinants are nonunit, call them x,y,w. They
obey xyw=1. The projected word gives H_B(y)H_A(x)=H_C(xy). If x and y
are distinct, compare the distinct group terms 1,x,y,xy. If x=y, compare
1,x,x^2; positive rational numbers have no nonidentity torsion. Both
cases force A=B=C. This is the exact determinant lemma proved in
../native-research/PROOF.md.

With two equal positive projectors and the equal negative projectors,
the five query images use at most three lines. A complete span of
dimension three would make the remaining singleton positive image a
coloop. This is impossible. With all three positive projectors equal,
the full image span has dimension at most two. This is also impossible.
Thus every positive ADDRESS determinant is one. The three positive
rank-one maps are nonidentity rational unipotents.

## The positive triple must also reach z

Let the two negative positions be i<j. A target ADDRESS subset has zero
or two negative maps. If the product of the three positive maps in their
actual order is not z, every target subset must contain both negatives.
Its first selected index is at most i and its last selected index is
at least j. Three distinct first indices require i>=3. Three distinct
last indices require j<=3. This contradicts i<j. Therefore the positive
triple in actual chronological order has product C B A=z.

The full five-query ADDRESS subset does not give z. To prove this, put
P equal to the ordered product of the positive maps between the negative
positions. Write the complete positive product as Q2 P Q1=z. The full
five-query product is z Q2 R P R Q1. If that product were z, it would
give R P R=-P. But P is a contiguous block of zero, one, two or three
maps from the positive triple. Its trace is respectively 2, 2, -2 or
-2. It cannot be conjugate to its negative over the rational numbers.

The negative pair and the positive triple give only two target branches.
The target coefficient has rank three, so another target branch is
necessary. A three-query mixed subset cannot give z: after the two
reflections are moved together it leaves one nonidentity unipotent.
The full five-query subset has just been excluded. Thus there is a
four-query target subset with both negatives and two positives.

The two selected positives cannot have product identity. Such a relation
would make their full three-positive product conjugate to the remaining
unipotent, which has trace two, contrary to CBA=z. In the four-query
branch, one of its selected positives must lie between the negative
positions and the other must lie outside them. Move the reflections
together. The resulting cancellation forces

    R U R=V^-1

for two distinct maps in the positive triple.

## At most one four-query target branch

The three positive maps in CBA=z are distinct. If any pair were the
same unipotent U, solving the triple relation for the remaining map
would give z U^-2. That map has trace -2 and is not a unipotent.

If two different four-query target branches existed, they would select
two different unordered pairs among the three positive maps. Those
pairs share one map U. Each branch would force conjugation by the same
reflection R to send U to the inverse of its partner. The two partners
would therefore be equal, contrary to their distinctness. There is at
most one four-query target branch.

Let S be the negative pair and T the complementary positive triple.
These are two target subsets. The only possible third target subset is
F, containing all five queries except one positive index c. A rank-three
target coefficient requires three branches, so F must exist.

The minimum selected indices of S and T are different, and one is one.
For the minimum selected index of F to differ from both, F must omit
index one. Thus c=1. The maximum selected indices of S and T are
different, and one is five. For the maximum selected index of F to
differ from both, F must omit index five. Thus c=5. This is impossible.

The two-negative five-query case is therefore excluded directly. No
free-group theorem, group representation extension, finite projector
search, or ADDRESS conjugacy classification is needed for this conclusion.

## A finite verification family

Use cyclic names so that the swapped positive pair is A,B and CBA=z.
The common rational conjugation from POSITIVE-FIVE-PROOF.md puts them in
the form

    A=[1 2; 0 1],       B=[1 0; -2 1],       C=[3 2; -2 -1].

A rational reflection has the form R=[x y; w -x], with x^2+yw=1.
The relation R A R=B^-1 gives R E12 R=E21. Its entries give x=0 and
w^2=1. The determinant condition gives yw=1. Therefore R is plus or
minus J=[0 1; 1 0]. The opposite negative map is the other sign of J.

The same finite family covers the other ordering of the swapped pair.
In that ordering the third map is C'=z B^-1 A^-1. Conjugation by
K=[0 1; -1 0] exchanges A and B, sends C to C', and sends J to -J.
Thus it only exchanges map labels in the complete five-map set.

The five literal maps in search.py are the same conjugacy class. The
basis matrix T=[1 1; 1 -1] gives T^-1 U T=A, T^-1 V T=B and T^-1 W T=C.
It gives T^-1 R1 T=-J and T^-1 R2 T=J. All 120 map orders are included
in the search, so cyclic naming and exchange of the negative labels
remove no candidate.

## Exact finite DATA replay

The two negative DATA projectors are equal and can be fixed to E00 by
one common binary conjugation. There are 28 binary rank-one idempotents
on three roles. The three positive projectors start with all 28^3
choices. Full span and absence of image and covector coloops retain
492 ordered triples.

All 120 map orders are checked. Forty have one target ADDRESS subset,
sixty have two, and twenty have three. A rank-three endpoint needs at
least three rank-one branch coefficients, so only the last twenty orders
need DATA replay. All 20 times 492=9,840 words were replayed in the full
rational binary group algebra. None reaches z I3.

The independent checker uses literal binary matrices and direct group
coefficient dictionaries. It imports no search code or transition table.
It agrees on every order, every retained projector triple, every complete
terminal coefficient and the receipt hash. It also checks the six-call
coordinate control and every single-call omission.

The finite replay agrees with the direct proof. This packet does not
claim an integer-multiplication lower bound,
an eight-query three-coordinate lower bound, or a kappa gain. AI
assistance was used. No global novelty claim is made.
