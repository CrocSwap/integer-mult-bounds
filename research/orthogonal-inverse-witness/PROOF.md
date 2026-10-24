# Rational orthogonal witnesses for inverse circuits

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof. The exact tests support it; they are not a proof-assistant result.

## Contract and result

Use the complete rational register grammar of Krzysztof Wójt's
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262), at
`6f92ccf1e61c4668c8ee687bd1df8b42932b8759`. Its proof and source notices are
retained in `vendor/UPSTREAM-PROOF.md` and `vendor/UPSTREAM-README.md`.
There are r independent input roles, and both programs return every role.
A scalar linear assignment reads all old values. An apply instruction uses
one named G_a or its actual inverse. A query adds c G_a^(+/-1) src to dst
from the old values, also when src equals dst. Let q count all apply and query
occurrences in both programs, including zero-coefficient queries. Put N=r+q.
Only inverses of named generators are allowed, not inverses of sums.

**Theorem.** If the two programs differ at any invertible matrix tuple over Q,
then for each rational cap 0<t0<=1/4 there is a witness with generators
O_a in SO(d,Q), d<=N, such that

    ||O_a-I||_2 <= 2 t0,    ||O_a^(-1)-I||_2 <= 2 t0,
    O_a^(-1) = O_a^T,     cond_2(O_a) = 1.

The witness is effective. It uses a shortest nonzero Magnus coefficient of
length D<N, dimension d=D+1, and at most dq+1 rational trials. Thus equality
for all such arbitrarily small orthogonal neighborhoods and dimensions up to
N is equivalent to the complete universal invertible identity for this grammar.
No least-dimension or bit-complexity claim is made.

## 1. Use a shortest failed coefficient

The source theorem constructs an N-state rational series realization of the
complete endpoint difference F at G_a=I+Y_a. It proves that a false identity
has a nonzero coefficient of length less than N. Its breadth-first producer
returns a globally shortest such word w=a_1...a_D, an input i, an output o,
and a nonzero coefficient c in block (o,i). Consequently **all** coefficients
of total degree less than D vanish. The source certificate checker alone
certifies nonzeroness, not shortestness. The construction here uses the source
producer and its shortestness proof.

Set

    K_a = sum_(0<=j<D, a_(j+1)=a) (E_(j,j+1)-E_(j+1,j)),
    O_a(t) = (I-t K_a/2)^(-1) (I+t K_a/2).

This is the classical rational Cayley transform. Each K_a is real skew
symmetric. In any product of D such matrices, a path from column D to row 0
must take D upper edges. The labels of these edges are exactly w. Hence the
(0,D) entry of K_b1...K_bD is one if b_1...b_D=w and zero otherwise.
The upper edges have sign +1.

At zero, O_a(t)-I=t K_a+O(t^2). Substitution into the endpoint series is valid
as a formal power series in the central variable t. No term below degree D
is present. Terms above degree D cannot contribute at degree D. The selected
endpoint entry therefore has expansion

    f(t) = c t^D + O(t^(D+1)).

It is a nonzero rational function. This also covers D=0: d=1, every generator
is identity, and the constant coefficient already gives the failure.

Shortestness cannot be dropped from this proof. For F(G)=G-G^(-1), the
Magnus coefficient of Y^2 is -1. On the three-vertex skew path for word AA,
F(O(t)) has zero (0,2) entry for every t. It is an odd rational function of
the bipartite path matrix, and an odd walk cannot connect these two vertices.
The lower-degree term cancels the chosen higher-degree contribution. The
shortest word A instead gives a two-dimensional witness.

## 2. Exact orthogonality and distance

For every real v and t,

    ||(I-t K_a/2)v||_2^2 = ||v||_2^2 + (t^2/4)||K_a v||_2^2.

Thus I-t K_a/2 is invertible for all real t, and its inverse has norm at most
one. The same holds with the plus sign. These two factors commute. Transpose
interchanges them, so O_a(t)^T=O_a(t)^(-1)=O_a(-t). Their determinants are equal,
so det O_a(t)=1. Rational t gives rational entries. This proves membership in
SO(d,Q), including exact condition number one.

Each row and column of K_a has absolute sum at most two. Thus ||K_a||_2<=2.
The identity

    O_a(t)-I = t (I-t K_a/2)^(-1) K_a

proves ||O_a(t)-I||_2<=2|t|. Apply the same argument to -t for the inverse.

## 3. Finite rational grid

The adjugate formula gives a numerator degree at most d for every entry of
O_a(t) and O_a(t)^(-1), with denominator degree at most d. All these
denominators are nonzero on the real line. Give all roles of one program a
common scalar denominator. A linear assignment does not increase its degree.
For each apply or query, multiply this denominator by the denominator of the
new operator. Multiply unchanged roles, and the old query destination, by
the same factor in the numerator. The maximum numerator degree increases by
at most d for that occurrence. This uses the old query source, even on alias.
Combining the two programs gives f(t)=P(t)/Q(t), with

    deg P <= L=dq,    Q(t) != 0 for all real t.

Section 1 proves P is not the zero polynomial. It has at most L roots. Try
these L+1 distinct positive rational numbers, starting with the largest:

    t_j = t0 (L+2-j)/(L+1),    1<=j<=L+1.

At least one has f(t_j) nonzero. Give role i the vector e_D and every other
role the zero vector, and execute both original programs. The difference
at coordinate zero of role o is f(t_j). This choice is a counterexample
input; it does not impose a clean-helper assumption on the universal claim.
All returned roles remain in the witness and in its literal check.

## 4. Implementation and discriminating cases

`literal.py` applies the Cayley factors by a tridiagonal solve. Its pivots
satisfy p_0=1 and p_j=1+(t/2)^2/p_(j-1) when that path edge is present;
a missing edge contributes zero. Thus every pivot is positive. The inverse
uses the opposite sign, with the same pivots. `check_witness.py` checks the
program binding, grid, dimension, full rational endpoint and nonzero selected
coordinate without importing the coefficient producer. It does not certify
minimality of the word or dimension.

A separate dense interpreter forms both Cayley factors and uses rational
Gaussian elimination. It checks inverse equals transpose, O^T O=I and det O=1.
A free-group expansion is a second oracle for small complete programs.
Nested commutators test leading degrees two through five. The G-G^(-1)
example tests the shortest-word boundary. Grid tests use

    (G-I) product_j (G+G^(-1)-alpha_j I),
    alpha_j = 2 (1-t_j^2/4)/(1+t_j^2/4),

on the two-dimensional Cayley rotation. The first one, two, four or seven
chosen grid points cancel exactly; the next point exposes the error. These
examples test multiple trials. They do not prove that L+1 is a sharp bound.

## Limits and credit

This preserves orthogonality and inverse equals transpose. It does not impose
finite order, involution, commutation, Clifford relations or a finite native
alphabet. Those extra relations can remove the witness. The theorem is over
Q; there is no finite-field or nonreal scalar extension here. Rational bit
length and a lower bound for floating-point detection are open. There is no
native tape, supplier pricing, circuit speedup or complete kappa improvement.
The selected record and all of its analytic, compiler and physical obligations
are unchanged.

[PR #5296](https://github.com/CrocSwap/integer-mult-bounds/pull/5296), at
`bab6b65d845fcc7b563d10e809f5e79c82e74ad0`, supplies the conditioned inverse
witness architecture, finite root budget and literal test harness adapted
here. The new step is the skew-path Cayley realization and its shortest-degree
requirement. [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262)
supplies the compact inverse frontend and shortest-word theorem. The retained
notices credit zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235),
the dirty-echo/tensor/phase lineage, and classical work on rational series by
Schutzenberger, Fliess and the cited authors. Cayley transforms are classical.
No new general identity-testing algorithm or global literature priority is
claimed. `SOURCES.json` records exact bytes retained in the branch history.
