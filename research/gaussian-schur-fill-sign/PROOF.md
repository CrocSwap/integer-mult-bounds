# Noncancellation and signs of truncated Gaussian Schur fill

This contribution was produced by Nick Petalas.

## Statement

Let n>=1 and b>=1 be integers, and let 0<t<=1/3 be real. On the
linearly ordered indices 0,...,n-1 define

    G[i,j] = t^((i-j)^2) if |i-j|<=b, and 0 otherwise.

For any eliminated set E, every principal pivot G[E,E] has positive
determinant, with the empty determinant defined as one. Thus the Schur
complement S on V={0,...,n-1}\E exists.

Its diagonal entries are positive. For i<j in V, form the ordered chain
consisting of i, all elements of E strictly between i and j, and j.

* S[i,j] is nonzero exactly when every successive chain gap is at most b.
* In that case sign S[i,j] = (-1)^|E intersect (i,j)|.

The same statements hold after independent positive row and column
scalings of G. In particular positive diagonal similarities, including
positive exponential chirps and linear shift gauges, preserve this support
and these signs.

This is a scoped written mathematical proof. It gives an actual real-entry
attainment statement for the generic fill support discussed by Ryanson
Jonathan in PR4407. It neither rechecks his finite-field census nor assumes
its numerical results. It does not assert that a particular Gaussian caller
has t<=1/3, or treat periodic distances, rounding or complex phases.

## 1. A polynomial with distinct negative roots

Define the degree-2b polynomial

    P(z) = sum_(h=-b)^b t^(h^2) z^(h+b).

For j=-b,...,b evaluate at z_j=-t^(-2j). Dividing by the jth term gives

    P(z_j) / [(-1)^(j+b) t^(-j^2-2jb)]
      = 1 + sum_(h != j) (-1)^(h-j) t^((h-j)^2).

The absolute value of the sum on the right is at most

    2 sum_(r>=1) t^(r^2)
      <= 2 sum_(r>=1) t^(2r-1)
       = 2t/(1-t^2) <= 3/4 < 1.

Consequently P(z_j) has sign (-1)^(j+b). The 2b+1 evaluation points
are distinct, ordered negative reals, and their signs alternate. Each of
the 2b disjoint consecutive intervals contains a root by continuity.
Since the degree is 2b, these roots are all the roots and are simple.
Write them as -lambda_1,...,-lambda_(2b), with every lambda_r>0. Then

    P(z) = t^(b^2) product_(r=1)^(2b) (z+lambda_r).

This elementary sufficient range is all that is needed. No optimal
root-realness threshold is claimed.

## 2. Exactly which ordered minors are positive

Consider the same kernel on all integer indices. Let T be the shift with
T[i,j]=1 when i=j+1. Its formal Laurent polynomial representation is

    G = t^(b^2) T^(-b) product_r (lambda_r I + T).

Every entry involves only 2b steps, so this identity requires no convergence
or infinite matrix multiplication. A path starts at column c, takes 2b
steps, each staying put with weight lambda_r or increasing by one with
weight one, and finishes at row r+b. All weights are positive.

For increasing row and column lists R=(r_1,...,r_d) and C=(c_1,...,c_d),
expand det G[R,C] as a signed sum of path families. Families with an
intersection cancel in pairs: choose their first intersection by a fixed
ordering and exchange the two path tails. This preserves their weight,
reverses the endpoint permutation and is an involution. A family without
intersections preserves the order of its starts and ends, so it contributes
with positive sign. Therefore the minor is nonnegative.

Such a family can exist only if

    -b <= r_l-c_l <= b for every l.                 (1)

Conversely suppose (1) holds. At time s=0,...,2b give path l position

    x_l(s) = max(c_l, r_l+b-(2b-s)).

It starts at c_l and ends at r_l+b. Every increment is zero or one.
For each fixed s the positions strictly increase with l, since both
arguments of the maximum strictly increase. These paths never intersect.
Their positive weight proves the exact minor criterion

    det G[R,C] > 0 iff |r_l-c_l|<=b for every l;
    otherwise det G[R,C] = 0.                     (2)

The cancellation argument and bidiagonal path factorization are classical
techniques; no claim of their invention is made here. The proof above is
included so that the specific strictness and support conclusions do not
rely on a quoted total-positivity theorem.

Taking R=C in (2) proves positivity of every principal determinant,
including all eliminated pivots.

## 3. Schur entries and their signs

List E in increasing order, and append i to its row list and j to its
column list. The block determinant formula gives

    S[i,j] = det G[(E,i),(E,j)] / det G[E,E].

Sorting both appended lists changes the numerator sign by

    (-1)^(#{e in E:e>i} + #{e in E:e>j}).

For i<j this is (-1)^|E intersect (i,j)|. The denominator is positive.
The sorted row and column lists agree outside [i,j]. Within it they are
respectively

    (i,e_1,...,e_k) and (e_1,...,e_k,j),

where e_1<...<e_k are precisely the eliminated indices between the endpoints.
Criterion (2) is exactly that each successive gap in this chain be at most
b. This proves both the zero criterion and the sign formula. For i=j the
numerator is a principal determinant, so S[i,i]>0.

The chain condition is equivalent to structural fill in the bandwidth-b
path graph. If it holds, the chain itself is a path with eliminated internal
vertices. If a gap is larger than b, no such path can cross the cut between
these consecutive available vertices, even using eliminated vertices outside
the endpoint interval. Thus every structurally possible fill is present,
without any generic-entry qualification, in this restricted real Gaussian
family. This supplies the missing actual-entry conclusion; the structural
bandwidth formulas of PR4373/4407 remain predecessor results.

## 4. Positive gauges

For H=D_left G D_right with positive diagonal factors, direct substitution
into the Schur formula gives

    Schur_E(H) = D_left[V,V] S D_right[V,V].

Every multiplier on an entry is positive. This proves the stated gauge
corollary without bounding any gauge's condition number or physical cost.

## Scope and first example

For n=12, b=3, t=1/3 and E={4,5,6,7}, the entry between 1 and 10 is
exactly 1/9170703360, at survivor-order distance five. The four intervening
eliminated vertices give positive sign. This is a new Gaussian fixture,
not a replay of James Reed's equal-weight path.

Only the restricted real kernel and its positive scalings have been proved.
The unrestricted t range, a concrete caller's admissibility, periodic
kernels, finite-precision stability, physical routines and supplier admission
remain outside this theorem. No new kappa or selected-frontier change.
Independent human and formal proof-kernel review are unclaimed.
