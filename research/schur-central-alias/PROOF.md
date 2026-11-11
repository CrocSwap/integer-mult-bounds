# The first central-class alias for sharp nilpotent Schur states

Work over any field of characteristic two. The ordered pair matters: the
state equivalence is simultaneous conjugacy of S and T, without exchanging
the two requests. Put K=S+T and Z=K^2.

## Contract and credited premises

Start with commuting idempotents P0,Q0, a size-d common identity pivot,
and sharp residuals rank(ST-TS)=2d. The compressed product is the nilpotent
matrix H. Fix the four ordered original sector dimensions r00,r10,r01,r11.
Let a=dim ker H. The nilpotent normal form and its whole-pair rigidity are
Malik Safwan / ssafwann's #5267, not new claims here. They require

    r00=d+s00, r10=d+s10, r01=d+s01, r11=d+a+s11,

with nonnegative padding. The minimal residual acts on U^3 plus F^a:

    S(x,y,z,t)=(H(x+z)+Nt, 0, (I+H)(z+x)+Nt, t),
    T(x,y,z,t)=(0, H(y+z)+Nt, (I+H)(z+y)+Nt, t).

Here im N complements im H. Add scalar pairs (0,0), (1,0), (0,1), (1,1)
with multiplicities s00,s10,s01,s11. All those statements, including
admissibility as genuine Schur residuals, are the cited predecessor model.
Ali Romman's #5287 already determines the complete central Jordan class,
and Mihir Srivastava's #5360 supplies the general-H ordered gluing theorem.
No predecessor scientific verifier is used as this contribution's evidence.

The new result is the first same-profile central-class alias, its sharp
minimum dimension, and the explicit ordered-state separator below. It is
an obstruction to an ordered-state registry using only the central class.
It does not contradict a classifier whose declared output is only Z.

## Rank information retained and discarded

Write W=I+H. It is invertible. In coordinates
u=x+y, v=y+z, w=z, t, the minimal K is

    K(u,v,w,t)=(Hu, Wu+Hv+Nt, Wu, 0).

For every j>=1, its jth power is

    (H^j u,
     (j mod 2) W H^(j-1)u + H^j v + H^(j-1)Nt,
     W H^(j-1)u,
     0).

This follows by multiplying once and induction; no division by two occurs.
The u-column image is a graph over W im H^(j-1), so has dimension
rank H^(j-1). Its intersection with the v,t-column image is zero: a zero
w component forces H^(j-1)u=0 and then every u contribution is zero.
The v,t-column image has dimension rank H^(j-1), because

    im H^j + im H^(j-1)N = H^(j-1)(im H + im N) = im H^(j-1).

The padding contributes c=s10+s01 to every positive power rank. Therefore

    rank K^j = 2 rank H^(j-1) + c,                   (1)
    rank Z^j = 2 rank H^(2j-1) + c.                  (2)

Equation (2) is also a rank-sequence restatement of #5287's credited
characteristic-two Jordan law. At fixed d and fixed original profile, c
and the total residual dimension are fixed. The multiplicity of eigenvalue
one is c and all other central blocks are nilpotent. Thus two such central
classes agree exactly when all odd positive power ranks of H agree.
In contrast, (1) retains every power rank of H. Nilpotent similarity is
determined by all power ranks. The normal-form rigidity supplies the converse
for full ordered pairs with the same H similarity class and profile.

## The collision

Take d=4, original profile (4,4,4,6), and no padding. Compare

    H_A=J3(0) direct-sum J1(0),     H_B=J2(0) direct-sum J2(0).

Both have a=2 and rank H=2. Every odd power of order at least three is zero.
Hence both fourteen-dimensional central operators have ranks

    rank Z=4, rank Z^2=0,

and full Jordan partition (2,2,2,2,1,1,1,1,1,1).
A complete central similarity class, rather than just its spectrum, aliases.
However rank H_A^2=1 and rank H_B^2=0. Equation (1) gives

    rank (S_A+T_A)^3=2,     rank (S_B+T_B)^3=0.

Simultaneous conjugacy would preserve this rank. The two ordered pairs are
therefore nonconjugate over every field of characteristic two.

## Literal original headers

The standalone checker also constructs original eighteen-dimensional
commuting projectors; it does not just trust admissibility of a residual.
In the Jordan convention H e_(i+1)=e_i, let R extract the bottom coordinate
of each block, and let W=I+H. In sector order 00,10,01,11, use

    P0=diag(0_4,I_4,0_4,I_6),  Q0=diag(0_4,0_4,I_4,I_6).
    i=(I,I,I,H,R)^T,          pi=(W,W,W,I,0).

The last sector is U plus F^2. The map i is injective, pi i=I,
pi P0 i=pi Q0 i=I, and pi P0 Q0 i=H. A basis B of ker pi is

    B(x,y,z,t)=(x,y,z,W(x+y+z),t).

Thus M=[i,B] is invertible. Conjugate P0,Q0 by M and delete the common
identity block by the literal Schur formula D-cb. This yields the two
witness pairs used by the verifier. All entries are in F2, so their exact
ranks and equations persist over every extension field of characteristic
two. The checker constructs an invertible fourteen-dimensional central
intertwiner as well as checking all stated ranks.

## Minimality

Consider any two states in this nilpotent sharp family at the same d and
same ordered original profile. Equal central classes imply equal rank Z.
By (2), their H ranks agree. At d=1,2,3, the nilpotent partitions are,
respectively,

    (1);  (2),(1,1);  (3),(2,1),(1,1,1).

Within each dimension these partitions have distinct ranks. Equal central
classes therefore force similar H and, by #5267 rigidity, conjugate ordered
pairs. This proves the pivot threshold d=4.

At d=4 the only distinct partitions sharing a rank are (3,1) and (2,2),
both with a=2. Their least possible residual dimension is 3d+a=14, attained
above. At d>=5 every nilpotent H has a>=1 and residual dimension at least
3d+a>=16. Thus fourteen is also the least residual dimension for this
same-d, same-profile nilpotent central alias. The corresponding least
ambient dimension is eighteen. These minima concern precisely this family;
no claim is made about arbitrary pairs of idempotents or nonsharp states.
