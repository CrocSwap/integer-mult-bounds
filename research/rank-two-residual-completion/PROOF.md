# Rank-two residual completion

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

This proof answers part of the higher-rank question in Nick Petalas's
[PR6494](https://github.com/CrocSwap/integer-mult-bounds/pull/6494).
Krzysztof Wojt's PR5097 supplies the displacement-plus-nullity lower bound
and the zero-form algorithm. Nick Petalas's PR5085 supplies the residual
form and two-turn cutoff. Brian / JoyboyBrian's PR5051 supplies the signed
partial-contract setting. These results retain their credit.

## Contract and result

Let V be a finite nondegenerate symplectic space over F2, with pairing w.
Let h:U -> V be an injective linear isometry. Put d=h+I, K=ker d,
D=d(U), r=dim D, and b(d(u),d(v))=w(u,d(v)). Assume rank b=2.
Let L(h) be the least number of nonzero-axis transvections in an extension
of h to V. T_a(v)=v+w(v,a)a. No dimensions or clean ancillas are added.
Any spectator that must remain fixed must be included in U with h(v)=v.

1. If b is not alternating, **L(h)=2r-2**.
2. If b is alternating, **2r-2 <= L(h) <= 2r-1**.
3. In case 2, let R=rad b and U_R=d^-1(R). If U_R is not contained in
   K+D, then **L(h)=2r-2**. A linear-system construction gives the word.
4. At r=2 in case 2, **L(h)=3**, as already proved in PR5085.

The new bounds hold in every ambient dimension. At r>=3, failure of the
condition in item 3 does NOT determine which endpoint is attained. Section
"Sharp controls" supplies exact examples for both outcomes. The executable
returns a lower and an upper bound, and retains a gap when it has no optimum
certificate. It never treats the upper bound as a proved minimum.

This is an unsigned label-word tariff. It is not Gaussian paid rank or
physical work. The result can remove unnecessary formal turns from candidate
native completions, but a profitable signed caller still needs its full bill.

## Retained facts and the one-turn reduction

The source proofs are retained byte for byte under inputs/. They show that
K is orthogonal to D, that b is well-defined, and that

    b(x,y)+b(y,x)=w(x,y),             L(h)>=2r-rank b.       (1)

For completeness, an extension S has W=im(S-I) and a nonsingular Wall form
B((S-I)v,z)=w(v,z) on W. The left radical of b injects into (W/D)* through
B. Thus dim W>=r+nullity b. A word of t turns has rank(S-I)<=t. This
proves (1). The credited zero-form construction uses exactly 2r turns.
It fixes one more source direction with at most two turns at each step and
preserves the full currently fixed subspace. It solves only linear equations
in V. PR6494 proves the exact 2r-1 tariff when rank b=1.

Choose a in D with b(a,a)=1. For h'=T_a h,

    d'(u)=P(d(u)),       P(x)=x+b(a,x)a.

The kernel of P is <a>, and its image is E=ker b(a,-). Hence the new
displacement dimension is r-1. On E, the new residual form is b|E.
In a basis that starts with a and continues in E, the old matrix is

    [ 1  0 ]
    [ c  B ].

Its rank is 1+rank B. Thus every such pivot decreases both r and rank b
by exactly one. When rank b=2 and b is not alternating, a pivot exists;
the remainder has rank one. Its optimal word has 2(r-1)-1 turns. Append
T_a. The resulting 2r-2 turns attain (1). A quadratic form over F2 has
a nonzero value on a basis vector or a sum of two basis vectors whenever
it is not identically zero, so the search for this pivot is polynomial.

This argument does not assert the same rule for arbitrary nonalternating
rank. A nonzero alternating remainder can block the next pivot. Binary
symplectic exceptions are classical: see David Callan, *The Generation of
Sp(F2) by Transvections*, Journal of Algebra 42 (1976), 378-390,
[author-hosted paper](https://pages.stat.wisc.edu/~callan/papers/transvections/transvections.pdf).
No classification theorem from that paper is required here.

## Two turns for an alternating residual form

Now let b be alternating of rank two. It is symmetric; (1) implies that
D is totally isotropic. Select a nonradical p in D and a lift u in U.
Then u is outside K+D: if u=k+z with z in D, its pairing with D would
vanish, contrary to b(p,-) being nonzero.

Choose a in (K+D)-perp with w(u,a)=1. Nondegeneracy of V and u outside
K+D make these linear equations consistent. If there is a radical lift
v outside K+D, also impose w(v,a)=1. These two prescribed values are
consistent: u+v cannot lie in K+D, since its pairing with D equals the
nonzero functional b(p,-). A basis of radical lifts is enough to find v.

For x=d(z), set k(x)=b(p,x) and l(x)=w(z,a). The latter is well-defined
because a is orthogonal to K. Since a is orthogonal to D, the commuting
turns with axes a and a+p give the new displacement

    F(x)=x+k(x)a+(l(x)+k(x))p.                            (2)

Both axes are nonzero: they pair to one with u. Their mutual pairing is
zero. Also l(p)=1 and k(p)=0. Therefore F(p)=0. The axis a can lie in D.
The following argument treats both cases.

The kernel of F is exactly <p>. If a is outside D, (2) first forces k=0
and then x=l(x)p. If a is in D, then k(a)=w(u,a)=1. Applying k to (2)
gives k(F(x))=0. If F(x)=0, then x is in <a,p>; substitution gives
F(a)=a+a+(l(a)+1)p=p, because l(a)=w(lift(a),a)=b(a,a)=0.
Thus again ker F=<p>. The new displacement rank is r-1.

For x,y in D, the new residual form, expressed through their images, is

    b'(F(x),F(y)) = b(x,y)+k(y)l(x)+k(x)l(y)+k(x)k(y).    (3)

To check (3), use b'(F(x),F(y))=w(lift(x),F(y)), and then
w(lift(x),p)=k(x). This directly gives b(x,y)+k(y)l(x)
+(l(y)+k(y))k(x). It also shows that (3) is independent of a lift.

Choose q with b(p,q)=1, and a basis z_1,...,z_(r-2) of R. The vectors
p,q,z_i form a basis of D. In the basis F(q),F(z_i), formula (3) is

    [ 1  t ]
    [ t' 0 ],             t_i=l(z_i).                   (4)

This matrix has rank one when t=0 and rank two otherwise. It is always
nonalternating. If every radical lift lies in K+D, then t=0 for every
allowed a. Otherwise the extra equation on v ensures t!=0. The rank-one
or nonalternating rank-two result now completes h' optimally. Reversing
the two correction turns gives respectively

    2+[2(r-1)-1]=2r-1, or 2+[2(r-1)-2]=2r-2.

This proves all stated bounds. It also proves that the radical-lift test
is independent of the chosen lift and basis. All operations are on the
original space. A final whole-contract replay checks every prescribed
source, including every fixed spectator.

## Sharp controls and the limit of the sufficient condition

Write e_i for the low bits and f_i for the high bits, with w(e_i,f_j)
=delta_ij. The following exact fixtures distinguish the claims.

* In dimension six take U=<f2,f1,e1> and prescribe displacements e1,e2,e3.
  The residual matrix is H2 direct-sum zero, where H2 has off-diagonal
  entries one. The radical lift e1 lies in D. The returned word, in
  execution order and packed coordinates, is (12,8,1,3,2). Its length is
  five. A complete two-turn ball from each endpoint has no intersection,
  so no word of length at most four exists. This exact finite certificate
  proves L=5; it is not a universal obstruction for the closed case.
* In dimension eight take U=<f2,f1,f4> with the same displacements.
  The radical lift f4 is outside K+D. The word (12,9,11,10) has four
  turns and attains the lower bound. The method constructs it directly.
* In dimension eight take U=<f2,f1,e4,e3+e4> and displacements e1,e2,e3,e4.
  Every radical lift lies in D, but the six-turn word
  (69,71,70,76,136,140) attains 2r-2=6. Thus the sufficient condition
  has no converse. The generic constructor reports [6,7] for this input;
  the separate six-turn certificate proves its optimum.

The last word also extends to the full symplectic map with ordered images
(1,2,8,12,18,33,192,64) on (e1,e2,e3,e4,f1,f2,f3,f4). This gives a
second, full-basis check. Neither adding unused dimensions nor changing
unspecified spectators is free in a caller; these fixtures state their V.

## Verification and open obligations

The verifier generates all rank-two binary matrices at displacement ranks
three and four, embeds each as a valid partial isometry, and checks the
returned word with a separate scalar-bit pairing and matrix interpreter.
It includes alternating, zero-diagonal nonalternating, conjugated, larger
and fixed-spectator contracts. A separate complete Cayley BFS in dimension
four checks all full maps restricted to all subspaces. Exact meet-in-the-
middle balls certify the five-turn example. Damaged sources, invalid
contracts and removed turns must reject. RESULT.json records actual counts.

The all-size claim rests on this written proof; finite replay corroborates
it. The remaining alternating closed case has a one-turn gap in the generic
algorithm. Its exact classification, signed native cost, absolute phase,
actual caller, owner cleanup, precision, stock, physical routing, compiler
and outer admission remain open. All five selected assumptions remain.
No new kappa, selected-frontier change, independent human acceptance or
proof-kernel acceptance is claimed.
