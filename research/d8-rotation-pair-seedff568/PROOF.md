# Exact finite argument

Let `G=D8={r^i s^e : i in Z/4, e in F2}` with multiplication

`(i,e)(j,f) = (i + (-1)^e j mod 4, e+f mod 2)`.

Set `s=(0,1)` and `t=(3,1)`. Then `s^2=t^2=1`, `st=(1,0)=r`, and
`ts=(3,0)=r^-1`.

## Paid factors and free scalar maps

For a rank-one idempotent `N=u v^T` over `F2^2`, define
`F_g(N)=I+([g]+1)N`. The pairs `u,v` with `u!=0`, `v!=0`, and `v^T u=1`
are exactly the six rank-one idempotents. Therefore the complete paid alphabet
has 2*6=12 factors.

Suppose free `GL2(F2)` matrices are interspersed with paid factors. Moving a
free matrix rightward across one paid factor conjugates its idempotent:
`M F_g(N) = F_g(M N M^-1) M`. Conjugation preserves the rank-one idempotent
class. After moving all free maps to the right, augmentation sends every paid
factor to `I` and sends the target `diag([r],[r^-1])` to `I`; hence the remaining
free product is `I`. The normalized twelve-factor word model is complete.

## Exhaustive coefficient check

Represent a group-algebra coefficient by an eight-bit mask, one bit for each
`r^i s^e`. Matrix multiplication uses the displayed multiplication rule and
XOR for coefficient addition. The search tests every length-n word in the
12-factor alphabet for n=0,1,2,3. The word counts are exactly

`1, 12, 12^2=144, 12^3=1728`.

The independent verifier recomputes every product by generic group-algebra
convolution and 2x2 matrix multiplication. It finds no target word through
length three. The four-factor word

`F_s(E11) F_t(E11) F_t(E22) F_s(E22)`

is checked coefficient-for-coefficient to equal `diag([r],[r^-1])`. Thus the
exact minimum in this finite model is four.

## Rank relaxation

In the left regular representation over `F2`, left multiplication by a
reflection has four 2-cycles, so `rank(L_s-I)=rank(L_t-I)=4`. Left
multiplication by `r` or `r^-1` has two 4-cycles, so each difference has rank
six. Since `rank(A tensor N)=rank(A)rank(N)`, a paid factor changes rank by
four. For invertible `A,B`,

`rank(AB-I) = rank(A(B-I)+(A-I)) <= rank(B-I)+rank(A-I)`.

The target difference has block-diagonal rank `6+6=12`, so at least three
calls are necessary. This relaxation leaves three calls feasible; the exact
coefficient enumeration proves that three do not suffice.
