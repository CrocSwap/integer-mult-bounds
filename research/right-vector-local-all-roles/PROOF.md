# Exact local-algebra cost at every role count

Let K be a central subfield of an associative unital ring R. Assume the
nonunits of R form a proper two-sided ideal J. Thus R is local and R/J is
a division ring. Neither commutativity, finite dimension, nilpotence of J,
nor R/J=K is assumed. Fix n>=1.

Use the alphabet of #4099 and #4243. A paid factor is I+u y^T, with
u in R^n and y in K^n. Every GL_n(K) map is free, anywhere in a word.
The cost is the minimum number of paid factors. All matrix products below
have their usual left-action convention; the rightmost map acts first.

The predecessor #4243 gives the free-map normal form and column bound

    cost(M) >= delta(M) = min_{T in GL_n(K)} dim_K ((MT-I)K^n).

We cite this bound rather than re-audit it. Theorem D of #4276 proves
equality for invertible targets when n=2. The new claim is equality for
every n and every invertible M in M_n(R).

## A free chart with exactly delta active columns

Write pi:R^n -> (R/K)^n for the K-linear quotient map. Put

    E = {v in K^n : Mv belongs to K^n},
    s = dim_K E,     d = n-s = rank_K(pi M|_{K^n}).

Since M is invertible, its restriction E -> M(E) is injective. Choose a
K-basis of E and extend it to a basis of K^n, giving H in GL_n(K).
Extend the corresponding basis of M(E) to a second K-basis, giving
B in GL_n(K). Then N=B^{-1}MH has its first s columns equal to those of I.
Consequently

    N = [[I_s, C], [0, D]],

where D is invertible over R. Empty blocks, including s=0 or d=0, are
allowed.

For every T in GL_n(K), applying pi to MT-I gives pi MT. Its K-rank is d,
so delta(M)>=d. Conversely, let T=HB^{-1}. Then

    MT-I = B(N-I)B^{-1}.

Its K-rank is at most d, since N-I has at most d nonzero columns. Thus
delta(M)=d. This calculation of delta uses invertibility but not locality.

## Unit pivots using only a free row permutation

For every invertible D in M_d(R), some row permutation P makes all leading
square corners of PD invertible. Here is the local-ring argument, including
the multiplication order needed for noncommutative R.

If d>0, the first column of D contains a unit. Otherwise every entry is in
J, which remains true after left multiplication by D^{-1}, contradicting
the first column of I. Permute a unit a into the first position and write
the permuted matrix as [[a,b],[c,F]]. Its Schur complement is

    S = F - c a^{-1} b.

Invertible block triangular elimination gives diag(a,S), so S is
invertible. Inductively permute the rows of S to make each of its leading
corners invertible. Apply that same permutation to the bottom rows of the
original matrix. Each leading corner of size j>=2 then has unit pivot a
and invertible Schur complement equal to the leading corner of the
permuted S. It is invertible. The size-one corner is a. This proves the
claim by induction on d, with d=0 vacuous.

Apply diag(I_s,P) to N. It is a free GL_n(K) map and preserves the first
s fixed columns. Absorb it into the left free chart and call the result
N again. Its active leading corners are now invertible.

## Exactly d paid factors

Let A_0=I. For j=1,...,d let A_j have the first s+j columns of N and the
remaining columns of I. All A_j are invertible: their active leading
block is the corresponding invertible corner from the preceding lemma.
In particular A_d=N. Set k=s+j and define

    u_j = A_{j-1}^{-1}(N e_k - e_k),
    F_j = I + u_j e_k^T.

The k-th column of A_{j-1} is still e_k, so right multiplication by F_j
replaces just that column by N e_k. Hence A_{j-1}F_j=A_j and

    N = F_1 ... F_d.

Each right vector e_k is K-valued, so each F_j is legal. Undoing the two
free charts realizes M with d paid factors. With the cited lower bound,

    cost(M) = delta(M) = rank_K(pi M|_{K^n}) = n-dim_K E <= n.

When d=0, M is itself in GL_n(K) and the empty paid word suffices.
Every factor in the displayed construction is invertible because both
adjacent prefixes are invertible. No auxiliary roles are used.

## Scope and predecessor credit

This proves an exact cost in the formal alphabet. It extends the local
two-role statement of Nick Petalas #4276 and answers the invertible,
arbitrary-role local case of #4265's question. #4243 supplies the bound and
normal form, following Wentao Li #4099 and #2513. ToikY #4334 and Nick
Petalas #4601/#4749 treat distinct two-role product/semilocal extensions.
Gaussian elimination, Schur complements, basis extension and local-ring
unit arguments are classical. The new contribution is their stated exact
restricted-right-vector cost consequence.

Invertibility is essential to the chart construction. Products of local
rings need a common pivot permutation and are not covered. Native
coefficient preparation, frames, routing, reversible restoration, precision,
stock and the full recursive invoice remain unknown. This is neither a
supplier admission nor a complete multiplication theorem or a new kappa.

This contribution was produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed. Apache-2.0.
