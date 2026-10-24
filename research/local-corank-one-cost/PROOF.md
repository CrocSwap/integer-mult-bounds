# Residue corank one attains the column bound

This contribution was produced by Nick Petalas. The result is a scoped
algebraic proof in the formal right-vector alphabet. No new κ is claimed.

Let K be a field contained in the centre of an associative unital local
K-algebra R. Its nonunits form its Jacobson radical J, and D=R/J is a
division algebra. Neither finite dimension, commutativity, split residue
nor nilpotence of J is assumed. Matrices act on columns on the left.

A paid factor is I+u y^T, where u is in R^n and y is in K^n. All GL_n(K)
maps are free anywhere in a word. Singular paid factors are allowed.
Write cost(M) for the minimum number of paid factors, or infinity when no
word exists, and define

    delta(M) = min_{T in GL_n(K)} dim_K ((MT-I)K^n).

The alphabet and column bound are from Wentao Li's #4099, following #2513,
and Nick Petalas's #4243. The two-role local unit-entry theorem is #4276.
The arbitrary-role invertible local theorem is #4787, head
4b58e8cd5690bd35cf01b0018eefa2c39a298920. ToikY's #4334 explicitly leaves
singular targets outside its field-product theorem. The new theorem below
handles singular local endpoints of arbitrary role count and residue corank
one. The arguments below are self-contained and do not replay those results.
Basis extension, Gaussian elimination, Schur complements and local-ring unit
lifting are classical facts, not claimed as new here.

## The theorem

For every n>=1 and every M in M_n(R) whose residue has rank n-1 over D,

    cost(M) = delta(M) = n - dim_K M(E) <= n,
    E = {v in K^n : Mv belongs to K^n}.

Here M(E) is a K-linear subspace of K^n. In particular, the zero images in E
must not be counted as fixed directions. The formula n-dim_K(E) used for
invertible targets would be wrong for singular targets. For example,
M=diag(1,...,1,0) has E=K^n but cost(M)=delta(M)=1.

## 1. The column lower bound and its singular-target form

Move free maps to the right by conjugation. Each conjugate of a paid factor
is again paid because K is central. A word with t paid factors is P S,
where S is free and P is their product. Expanding P-I successively writes
it as a sum of t terms v_i y_i^T with y_i in K^n. Therefore its image on
K^n has K-dimension at most t. Taking T=S^{-1} proves delta(M)<=cost(M),
including singular words.

Delta is invariant under free maps on either side. For G,H free, put
T=H^{-1} U G^{-1}. Then

    (GMH T-I)K^n = G(MU-I)K^n.

Hence the minima agree. Set k=dim_K M(E). For any free T, the fixed subspace
W=ker_K(MT-I) satisfies TW contained in E and M(TW)=W, so dim_K W<=k.
Rank-nullity gives delta(M)>=n-k.

Conversely choose v_1,...,v_k in E whose images w_i=Mv_i form a basis of
M(E). The v_i are K-linearly independent, since their images are. Extend
both lists to K-bases. Let H have first k columns v_i, and let X have first
k columns w_i. Then N=X^{-1} M H has first k columns e_1,...,e_k, so
(N-I)K^n has dimension at most n-k. Free invariance proves

    delta(M)=n-k.

This identity holds over every central K-algebra, even if M is unreachable.
The upper bound on cost in the next steps uses the local and residue-rank
hypotheses.

## 2. Unit pivots before the last column

In the charts just chosen, write

    N = [[I_k, B], [0, A]],       t=n-k.

The first k residue columns are D-independent. Since rank_D(bar M)=n-1,
rank_D(bar A)=t-1. In particular k<=n-1 and t>=1.

Gaussian elimination with complete row and column pivoting on bar A
produces t-1 nonzero pivots. Make the same row and column permutations in
N, only among its last t coordinates. Each lifted pivot in the corresponding
Schur complement is outside J, hence is a unit. Eliminating a unit pivot
reduces residue rank by exactly one. Thus the first n-1 leading square
blocks of the resulting N' are invertible over R. The first k columns
remain e_1,...,e_k. No assertion is made about invertibility of N' itself.

For completeness, the induction uses the block factorization of a matrix
[[a,b],[c,F]] with unit a into invertible triangular factors and diagonal
blocks a and F-ca^{-1}b. It works without commuting any coefficients.
At each stage of a residual block of rank s-1 and size s>=2, there is a
nonzero residue entry. Permuting it into the pivot position preserves
previous leading blocks. This supplies the next unit pivot. At s=1 no
pivot or inverse is needed.

## 3. An attaining literal word

Let C_j be the matrix with its first j columns equal to those of N' and
its remaining columns equal to the corresponding identity columns.
Then C_k=I and C_n=N'. For k<=j<n, C_j is invertible: it has block form
[[L_j,0],[*,I]] with invertible leading block L_j from step 2.

For j=k+1,...,n define

    F_j = C_{j-1}^{-1} C_j
        = I + C_{j-1}^{-1}(N'e_j-e_j)e_j^T.

Every F_j is a legal paid factor with base-field right vector e_j.
All inverses occur before the last column replacement. Telescoping gives

    F_{k+1} F_{k+2} ... F_n = N'.

Undoing the free row/column charts gives M with at most t=n-k paid factors
and no auxiliary roles. This product is written in matrix multiplication
order. Applied to data, its rightmost factor acts first. Step 1 gives the
matching lower bound t, proving the theorem.

## Scope boundary

Residue corank two or greater need not permit all required intermediate
inverses. The square-zero radical obstructions in #4745/#4773/#4776 and the
cube-zero example in #4764 are separate results; this theorem does not
classify them. Nonlocal coefficient algebras need not admit the unit pivots.
No physical implementation, restoration or recursive cost is supplied.
