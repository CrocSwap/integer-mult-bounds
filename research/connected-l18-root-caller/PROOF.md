# Exact root and caller argument

Matrices act on columns; event order multiplies on the left. The field has
characteristic zero. D_j commute and are algebraically independent. A coordinate
mask is the diagonal idempotent on its listed roles.

## Complete sign header

For g in {3,9,18}, use n=2g+2 coordinates A,F_0,...,F_(g-1),
H_0,...,H_(g-1),E and N=n+1 pairs (X_i,Y_i). `generate.py` gives the integral
formula. Left units have X_i=A+F_i+2 sum_(j<i) F_j, Y_i=A*-F_i*;
right units have X_m=-A+H_m+2 sum_(l>m) H_l, Y_m=A*+H_m*.
Three explicit middle units connect the arms and E. A determinant-one basis
change in each block of three F and H coordinates uses columns
(1,1,1),(1,1,0),(0,1,1).

Exact checks establish Y_i X_j=sign(i-j) for all N^2 entries and
rank X=rank Y=n. Every unit is nilpotent; every two unit directions are coupled.
There is no nontrivial decomposition into blocks preserved by all units:
each rank-one unit would have to lie in one block, but every off-diagonal
pairing is nonzero and X spans. This is the connectedness claimed here.

For the bare endpoint, let B be the N by N strictly lower triangular all-ones
matrix and A0=I+2B. The Gram is G=YX=A0-11^T. Since N is odd,
A0^-1 1 is the alternating vector v=(1,-1,...,1), spanning ker G=ker X.
In the ordered application of I-2X_iY_i, the scalar reads z satisfy
A0 z=Y w. The endpoint is I-2X A0^-1 Y. But
X A0^-1 Y X=X A0^-1 G=X; since X is surjective, X A0^-1 Y=I.
Thus the endpoint is -I. At S=+1 all units I+(S-1)X_iY_i are identity,
so the bare root is S I modulo S^2-1. This mechanism is prior work.

The g=9 source control reverses the block basis change and compares every
pair to the even-index units on the first twenty coordinates of retained
#6936 root_A.json. The g=18 chain uses parity-correct middle units; it does
not borrow the source's second independent chain.

## Stage masks and all-stage operator

A host uses consecutive units u,v=u+1. Its rank-two projector is
H=X_uY_v-X_vY_u. The coordinate mask E_j contains both X directions and
Y supports, so E_j H=H E_j=H; E_j-H is an idempotent of rank rank(E_j)-2.

Left masks contain A and the complete blocks of three F coordinates through
the pair's last unit. Right masks contain A and complete suffix blocks of H.
The middle mask contains A,E and the first new coordinate of every block on
both arms. Exact checks establish that each mask commutes with the prefix
immediately before and after its hosted pair.

For the middle mask, the raw left prefix sends

a' = (-1)^g a + 2(-1)^(g-1) sum_i (-1)^i f_i,
F' = -F + 2 a' (1,...,1).

In each three-block, the last two new basis vectors have alternating sum zero;
the first is the all-ones vector. The complement is acted on by -I and has no
cross terms with the middle mask. Left masks follow from prefix support.
Right masks follow by writing a prefix as minus the inverse of its remaining
suffix. These explain the finite exact commutator checks.

Each stage multiplies by D_j on its whole E_j: the hosted rank-two piece plus
all rank-one idle directions of E_j-H. Prefix commutation moves this multiplier
to exactly E_j in initial coordinates. All E_j are diagonal and commute.
At S=+1 the full word is diag(prod D_j); at S=-1 it is minus that diagonal.
Thus the full formal operator is S diag(prod D_j) modulo S^2-1, with no
specialization or sampling of D variables.

L18 mask ranks are
4,7,10,10,13,16,16,19,14,19,19,16,13,13,10,7,7,4,
summing to217. Every coordinate has a nonempty mask. Hosts supply36
dimensions and residuals181 separate rank-one idles. Units0,17,20 are thin.
L3 has joint dimensions {1:2,2:1,3:1,4:2,6:1,7:1}, agreeing with the two
retained #6937 roots under its recovered projector decoder and #6842 ordinary
normalization. This is a mask-pattern statement, not parameter equivalence.

## Emitted caller and Q4 lift

Choose a host basis beginning X_u,X_v, then im(E_j-H), then standard vectors
outside E_j. In this basis Y_u=-e_1* and Y_v=e_0*. The pair product is

    [[1,1-S],[S-1,2S-1]] = L [[1,S],[-S,0]] P,
    P=[[1,1],[0,-1]], L=[[1,0],[-1,-1]].

The middle matrix is supplied HOST_S before common D_j. P,L and basis changes
are emitted ADD/SCALE/SWAP. Each residual basis coordinate has one IDLE_ONE;
none are fused. A thin unit uses a basis starting X and v with Yv=1, then
ADD(-1) and QUERY_S, giving I+(S-1)XY. All basis changes act on arbitrary
live roles, with no zero or owned scratch.

For Q^4=1 put lambda=((1+i)+(1-i)Q^2)/2 and R=lambda Q. Then
lambda^2=Q^2 and R^2=1. QUERY_R is LAMBDA(source,+), QUERY_Q,
LAMBDA(source,-). HOST_R is LAMBDA(first,-), HOST_Q, LAMBDA(first,+).
Final LAMBDA(-) on each role changes R diag(prod D) to Q diag(prod D).
Every operation occurs in the frozen word. Four exact character evaluations
are complete for Q^4-1 over Q(i); D exponents remain formal. Independent
reverse replay uses the quotient ring directly.

This proves caller algebra given HOST. It does not prove a physical HOST at
its required price, or accepted ordinary, LAMBDA, precision and outer tariffs.
