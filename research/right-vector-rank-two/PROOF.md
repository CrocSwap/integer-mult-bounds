# Exact rank-two classification on two roles

Let K be a field, m>=3 and R=M_m(K). Paid factors are
P(u,y)=I_2+u y^T, with u in R^2 and y in K^2. Free maps are
GL_2(K), acting as S tensor I_m, anywhere in a word. Rank below means
ordinary rank over K. Let M have rank two, and choose a rank factorization

    M = A B,   A = [A_1; A_2],   B = [B_1 B_2],

where A is 2m by 2 and injective, B is 2 by 2m and surjective,
A_i is m by 2 and B_j is 2 by m.

**Theorem.** The exact cost is three if and only if both conditions hold:

1. B_1=c_1 b and B_2=c_2 b for one nonzero row b in K^(1 by m)
   and a basis c_1,c_2 of K^2.
2. For every nonzero (s,t) in K^2, the matrix s A_1+t A_2 has rank two.

Every other rank-two target has exact cost two. In particular, all these
targets are reachable. The conditions are independent of the chosen rank
factorization.

This answers the rank-two, two-role part of Open next question 1 of Nick
Petalas's #4772. The two-factor criterion is Corollary C of Nick Petalas's
#4276 and retains its credit. Rank factorization and the elementary
rank-one pencil argument below are classical linear algebra. The new claim
is their exact-cost classification in this alphabet and the attaining words.

## Lower bound and predecessor criterion

A paid factor fixes (ker y^T) tensor K^m, so its rank is at least m.
Free maps preserve rank. Since rank M=2<m, zero or one paid factors cannot
attain M. This is the rank-loss bound used in #4772.

By #4276, two factors suffice exactly when some nonzero row phi and column
v over K give

    rank ((phi tensor I_m) M)
      = rank ((phi tensor I_m) M (v tensor I_m)).             (1)

Set A_phi=phi_1 A_1+phi_2 A_2 and B_v=v_1 B_1+v_2 B_2.
Since B is surjective, (1) becomes

    rank A_phi = rank (A_phi B_v).                           (2)

If any B_v has rank two, it is surjective onto K^2, and (2) holds for
every phi. Such a target has cost two.

## The only deficient B pencil

Suppose every B_v has rank at most one. Neither B_1 nor B_2 can be zero,
since B is surjective. Write B_i=c_i b_i with nonzero factors. The columns
c_1,c_2 are independent, again because B is surjective. If b_1,b_2 were
independent, B_1+B_2 would have rank two: the map with rows b_1,b_2 is
surjective, followed by the isomorphism with columns c_1,c_2. Thus b_2 is
a nonzero multiple of b_1. Absorb that multiple into c_2 to obtain
condition 1. Conversely, condition 1 makes every nonzero B_v rank one.
This argument uses only v=e_1,e_2,e_1+e_2 and works over F_2 as well.

Now suppose condition 1 holds. If A_phi has rank zero, (2) holds. If it
has rank one, write A_phi=a ell with ell a nonzero row on K^2. Choose v
so ell(v_1 c_1+v_2 c_2) is nonzero. This is possible because c_1,c_2 are
a basis. Then A_phi B_v has rank one, so (2) again holds.

If condition 2 also holds, A_phi is injective for every nonzero phi,
while every B_v has rank one. The two sides of (2) are then two and one
for every pair. No two-factor word exists, including arbitrary free maps.
This proves exactly which targets cost at least three.

A different rank factorization has the form A H, H^(-1) B for H in
GL_2(K). Right multiplication by H preserves each rank in condition 2;
left multiplication by H^(-1) preserves the common-row property and the
independence of c_1,c_2 in condition 1. This proves independence of the
rank factorization.

## Attaining the exceptional class with three factors

For an exceptional target, put a=A_1 c_1 and d=A_2 c_1. Condition 2 gives
a!=0. Choose L in M_m(K) with L a=d, for example

    L = d e_h^T / a_h,   where a_h!=0.

Since M_11=a b and M_21=d b, we have L M_11=M_21. Set
D=M_22-L M_12. Then the literal product is

    [[I,0],[L,I]] [[I,M_12],[0,D]] [[M_11,0],[0,I]]
      = [[M_11,M_12],[M_21,M_22]] = M.                       (3)

Each displayed matrix differs from the identity in one block column,
so each is a legal paid factor. Their right vectors in algebraic product
order are e_1,e_2,e_1. Chronological execution on column data is from
right to left. There are no auxiliary roles or free internal-coordinate
changes. Together with the lower bound, (3) proves exact cost three.

For a nonexceptional target, #4276 gives an attaining two-factor word:
choose free G,H taking a passing phi,v to the first output row and input
column. For N=G M H solve N_11 C=N_12, then use

    N = [[N_11,0],[N_21,I]] [[I,C],[0,N_22-N_21 C]].          (4)

Undo G,H at the free endpoints. The existence of C is precisely the
column-space equality in (1). This attaining formula is predecessor
credit, not a new two-factor theorem.

## One explicit exception over every field

For m>=3, take

    A_1=[e_1 e_2], A_2=[e_2 e_3],
    c_1=(1,0)^T, c_2=(0,1)^T, b=e_1^T.

The columns of s A_1+t A_2 are s e_1+t e_2 and s e_2+t e_3.
If s!=0, their first two rows have determinant s^2; if s=0, their
last two displayed rows have determinant t^2. Thus condition 2 holds
over every field. In matrix-unit notation the target is

    M = [[E_11,E_21],[E_21,E_31]],   cost(M)=3.

Its ordinary rank is two. Formula (3) specializes to L=E_21 and
D=E_31, since E_21^2=0. Hence the three factors are explicit over every
field and every permitted block size.

## Scope

The assertion concerns formal overwriting factors on two roles and m>=3.
At m=2 a rank-two target can cost one, for example diag(0,I_2), so that
boundary is excluded. Other ordinary ranks and more than two roles are
unclassified here. Coefficient preparation, reversible restoration, routing,
precision, stock and a complete supplier invoice are not supplied.
No new kappa or complete multiplication theorem follows.
