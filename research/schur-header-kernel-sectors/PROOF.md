# Original-header formulas for the sharp Schur kernel sectors

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a written all-field result with exact finite corroboration.

## Contract and statement

Let P0,Q0 be commuting idempotents on V over any field F. Their ordered joint
sectors V00,V10,V01,V11 have dimensions r00,r10,r01,r11. Let U=F^d and take a
split i:U->V, pi:V->U with pi i=I and pi P0 i=pi Q0 i=I. Thus a header
[i,B], with B a basis of ker pi, has the common identity pivot I_d. Let S,T
be the Schur complements, acting on W=ker pi, and put

    H=pi P0 Q0 i,    K=ST-TS,    Z=(S-T)^2.

Assume rank K=2d. This is the same sharpness hypothesis as the predecessors.
For a,b in {0,1}, let Eab=ker(S-aI) intersect ker(T-bI).

**Theorem.** In the original space V, the four joint residual sectors are

    E00 = (I-i pi)V00,
    E10 = V10 intersect ker pi,
    E01 = V01 intersect ker pi,
    E11 = V11 intersect ker pi.                              (1)

The first displayed map is injective on V00. Consequently

    (dim E00,dim E10,dim E01,dim E11)
       = (r00,r10-d,r01-d,r11-d).                            (2)

These four spaces give a direct sum decomposition of ker K. No division by
two is used. H need not be nilpotent, and I-H need not be invertible. Empty
or rank-deficient 00 factors are allowed.

In particular, the opposite-sector count required by
[PR #5287](https://github.com/CrocSwap/integer-mult-bounds/pull/5287) is

    a1 = r10+r01-2d
       = rank P0 + rank Q0 - 2 rank(P0Q0) - 2d.              (3)

Thus that predecessor's complete central-class construction takes H and the
original joint-sector profile directly. It no longer needs a full residual
kernel calculation. This statement does not classify the full ordered pair
(S,T) or determine later-guard behavior.

## 1. Credited sharp-sector criterion

Write E_j for each original joint projector, Y_j=E_j i and X_j=pi|V_j.
The identity-pivot equations imply

    X00 Y00=H-I,    X10 Y10=X01 Y01=I-H,    X11 Y11=H.        (4)

The sharp-sector criterion of Nick Petalas's
[PR #4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746) states
that rank K=2d is equivalent to each of Y10,Y01,Y11 being injective and each
of X10,X01,X11 being onto, under these same hypotheses. The specialization
is retained in ssafwann's
[PR #5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267), in
`vendor/NILPOTENT-SOURCE.md`. The criterion itself does not require nilpotent
H. This is a credited theorem used here, not a new sharpness criterion.
The finite verifier separately checks the literal commutator rank.

There is no full-rank requirement on X00 or Y00. In particular, when H has
an eigenvalue-one part, that sector can differ from the full-rank nilpotent
models. The proof below keeps it unrestricted.

## 2. Residual maps in the original space

For v in W, the Schur residual maps have the basis-free formulas

    S v = P0 v - P0 i pi P0 v,
    T v = Q0 v - Q0 i pi Q0 v.                             (5)

For example, in header coordinates P=[I b;c D], the first expression has
lower coordinates (D-cb)v and zero pivot coordinates. Hence (5) is the
actual Schur action, not the leading compression or just its central image.

Since T v lies in im Q0, T v=v implies v in im Q0. Conversely if v is in
im Q0 intersect W, then pi Q0 v=pi v=0, and (5) gives T v=v. The same
argument applies to S and P0. This proves

    E11 = im P0 intersect im Q0 intersect W = V11 intersect W.

If T v=v and S v=0, put a=pi P0 v. The first equality places v in im Q0;
the second says P0 v=P0 i a. Its V10 coordinate is 0=Y10 a. Injectivity of
Y10 gives a=0, so P0 v=0 and v lies in V01. The converse follows at once
from (5). Thus E01=V01 intersect W. Exchange P0 and Q0 to obtain E10.

It remains to determine E00. If S v=T v=0, put a=pi P0 v and b=pi Q0 v.
Equation (5) gives P0 v=P0 i a and Q0 v=Q0 i b. Their common V11 component
gives Y11 a=Y11 b, so a=b. The vector w=v-i a then lies in V00. Since
pi v=0, pi w=-a, and therefore v=w-i pi w. This proves one inclusion in
E00=(I-i pi)V00. For w in V00, substitute v=w-i pi w in (5); the two
terms cancel for both maps. This proves the other inclusion.

If (I-i pi)w=0 with w in V00, then w=i pi w. Its V10 component is
Y10 pi w=0. Injectivity gives pi w=0, hence w=0. The map on V00 is injective.
The 00 sector is therefore a projection of V00, not generally V00 intersect W.

## 3. Dimensions, completeness and central class

Surjectivity of X10,X01,X11 gives the last three dimensions in (2).
Injectivity just proved gives the first. Distinct joint eigenvalue pairs
give independent subspaces over every field, including characteristic two.
They lie in ker K, and their dimensions sum to

    n-3d = (n-d)-2d = dim ker K.

They therefore exhaust ker K. This proof also makes each basis constructive:
project an original V00 basis by I-i pi, and take kernels of the three
small observation maps X_j for j!=00. `kernel_bases` implements these maps
in original V coordinates; it does not build S or T to find those kernels.

For commuting idempotents, rank P0=r10+r11, rank Q0=r01+r11 and
rank(P0Q0)=r11, which proves (3). This is a rank formula, not a trace formula
that could lose dimension information in positive characteristic.

The unchanged theorem of PR #5287 reconstructs the complete similarity class
of Z from H, m=n-d and a1 under sharpness. It uses the credited commutator
image action of ssafwann's
[PR #5256](https://github.com/CrocSwap/integer-mult-bounds/pull/5256), extends
its endpoint nilpotent chains, and retains the non-endpoint primary operator.
Substitute (3) into that theorem. `central_from_header` makes precisely this
substitution into the unchanged classifier. It handles repeated and nonsplit
primary factors through that predecessor, rather than through eigenvalue
samples. The original header profile is a required input or a separately
computed datum; its acquisition is not assigned zero physical cost.

## 4. Necessary boundaries

Sharpness cannot be removed. Take d=1 and one original coordinate in each
sector. Choose i and pi entirely in V11. Both pivot blocks are one and H=1,
but K=0. The residual has one 00, one 10 and one 01 coordinate. Formula (2)
would incorrectly predict (1,0,0,0). The factor-rank gate rejects this input.

H and residual dimension alone are insufficient. For H=0 over F2, padding
two original 00 directions or padding one 10 and one 01 direction gives
the same residual dimension, but changes a1 from zero to two. The complete
central classes differ. Original profile data supply the missing information.

The formulas concern joint eigensectors on ker K and the complete central
operator. They do not assert that the four spaces split as invariant direct
summands of all of W, that Z determines (S,T), or that central classes give
unconditional header probabilities. No native realization, selection/emission
cost, later-guard transition, supplier admission or complete kappa change is
proved. The selected frontier remains unchanged.

## Evidence and credit

The verifier constructs original sector factors, a complete header and both
full commuting projectors. It checks the original identity pivot, compressed
H and sharp Schur rank. It then compares each explicit original-space basis
with separately computed full residual joint kernels and the complete
central similarity invariants. Cases include empty V00, unequal X00/Y00
ranks, changes of original sector bases, characteristic two, eigenvalue-one
chains and repeated nonsplit factors. Finite exact checks support the written
proof; they are not independent human or proof-kernel acceptance.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Exact source
and retained-history pins are in SOURCES.json. Credit Nick Petalas for #4746
and the ordered factor lineage; ssafwann for #5256/#5267 and the source matrix
helpers; Ali Romman's #5287 for the central classifier; and codyw912, MatShep,
Ryanson Jonathan and the contributors retained in NOTICE.md. The central
classifier and independent invariant oracle are unchanged. General projector,
kernel and Schur-complement facts are classical; the new result is the explicit
original-header sector formula and its complete central-class binding.
