# Independent review of the general unit completion

I accept GENERAL-COMPLETION.md, SHA-256
`df76e7ff4b532bfab58a9aea5ce7d29493305a76013ef6cd20fb38b7ad2dde01`,
with the notation qualification below. I found no material algebraic
error. The frozen source was not changed.

## Proof checks

The construction needs a two-sided unit selected minor R_S. It does not
need K_S=R_S^-1 or RK=gI. With G=i_S R_S^-1 and D=i_U pi_U K, the
support identities LG=I, LD=BG=0 give both nilpotent shears. Expansion
gives T=I+GB-DR, so T retains every unselected row of I-KR and LT=R.
The reversed inverse factors are valid without any commutation between
B and D. Each shear has determinant one over a commutative ring. The
full query and unselected rows specify every output, so the code is
unique under those two equations.

For the converse, R onto and R=Q pi_S T imply Q onto. The codomain of Q
is finite free, so the surjection splits. The determinant of a right
inverse proves that the square Q is a unit over the commutative ring.
Thus [R;pi_U J] is a unit. The stated block row operation gives a block
triangular matrix with diagonal R_S,I. Its determinant proves that R_S
is a unit. The proof therefore covers an arbitrary linear readout Q;
it does not presume Q=R_S. Both counterexamples in the source have the
claimed effects. Surjectivity cannot be dropped, and an arbitrary unit
row repair need not supply the full query.

When RK=gI, the displayed inverse of J for unit 1-g is exact in both
orders. Conversely, I+R J^-1 K is a two-sided inverse of I-RK. For a
nonunit 1-g, reduction at a maximal ideal containing 1-g gives RK=I.
This makes K injective and KR a projection of rank dN. Hence J has
nullity dN. A unit repair is injective on that kernel, which proves
the rank and changed-field lower bounds. The construction attains the
d-field bound without the selected-K compatibility premise. This
establishes the exact 0/d distinction on the complete finite module.

The compatible repair is a projection because it is G(2R-L) and
(2R-L)G=I. This extra statement does require compatibility. The general
repair GB+K_S R need not be a projection.

For the actual source, independent reads give RR^T=56I and
R_S R_S^T=4I. Both Gaussian residue maps to F13 are valid. The matched
views preserve the full-module identities, and independent unit input
and output views preserve residue rank. A fieldwise output view retains
the support of a row repair. This transfer requires those views to be
units over the coefficient ring; it does not allow a hidden division by
13. The realification argument correctly uses both Gaussian sectors,
so it covers dyadic real-linear maps that include conjugation. The
lower bound is on changed output fields, not native children.

## Notation qualification

In the nonlinear paragraph, let U_c denote the complement of the c
changed fields. It contains n-c fields. The earlier symbol U denotes
the complement of the fixed d selected fields and contains n-d fields.
The required inequality is

    rank(pi_Uc Jbar) <= rank(Jbar) = (n-d)N < (n-c)N.

Therefore the unchanged output projection cannot be onto. This proves
the stated nonlinear extension when a surjective residue map exists.
The source author confirmed this interpretation and kept the frozen
bytes. The rank bound on T'-J remains a linear claim. No assertion is
made for rounding codes that have no such residue reduction.

## Independent checks

`check_extension.py` imports no source or producer executable. It uses
a free ordered polynomial ring in B,D,C, where C is the arbitrary
selected part of K in normalized coordinates. It checks both inverse
orders, query and unselected rows, the general repair, the compatible
projection, and a nonprojection control. It then checks all 500 scalar
cases over F5 with a unit selected minor; 400 cases have incompatible
selected K. These cases verify the formula and unit distinction. They
support the general proof and do not replace it.

The checker reads the pinned actual R directly. It verifies its two
Gram identities and both Gaussian residue images. It also checks the
two exact converse controls over the dyadic ring.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/paired-package-review/upstream-followthrough-20261015/general-completion-review/check_extension.py --repo /Users/aliromman/Projects/IntegerMultiplicationBounds --out /private/tmp/general-completion-review
```

The first line is `PASS_GENERAL_COMPLETION_EXTENSION`. No native kernel,
physical word, global controller, record owner, finite precision, or
supplier invoice was replayed in this review. Those claims remain outside
the theorem and this receipt. No publication was performed.
