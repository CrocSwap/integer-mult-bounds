# Positive-definite separation of complete dirty circuits

## Statement

Use the complete linear register grammar from zxv's [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235),
head `48976daa4dce59b4867ef046da72a370e389925d`. All input and returned roles
are independent. Coefficients are central elements of Q or Q(i). Symbols have
no inverse, commutation, Clifford or other relations. Compare two finite
programs, or compare one program with an explicit polynomial endpoint.

Let F be their matrix of noncommutative polynomial differences. If F is
nonzero, let D be the largest word degree with a nonzero coefficient in any
entry. For every rational 0 < e <= 1/4, there are real symmetric rational
matrices A_a of dimension D+1 such that:

- every spectrum is contained in [1-2e,1];
- each matrix is positive definite, has operator norm at most 1, and has
  spectral condition number at most 1/(1-2e) <= 2;
- the literal complete endpoint difference is nonzero for one input role
  equal to a coordinate vector and all other roles equal to zero.

Thus identity on this class, in every payload dimension, is equivalent to
free-polynomial identity. Taking e arbitrarily small also gives witnesses
arbitrarily close to I in operator norm. This statement gives no lower bound
on numerical detectability. The nonzero discrepancy can be exponentially small.

## Construction and proof

Choose an entry (o,i) and a degree-D word w=a_1...a_D with coefficient c != 0.
Number the path vertices 0,...,D. Let S_a contain both symmetric entries
(j-1,j) and (j,j-1) exactly when a_j=a. All other entries are zero. Put

    A_a = (1-e)I + (e/2) S_a.

Each S_a is real symmetric and has absolute row sum at most 2. For every real
vector x, the inequality 2|x_j x_k| <= x_j^2+x_k^2 gives
|x^T S_a x| <= 2||x||_2^2. The spectral interval for A_a is therefore
[1-2e,1]. The same statement applies on complex payload space.

In a product of k <= D such matrices, a path from vertex 0 to vertex D must
make D steps. Each factor can stay at its vertex or move one edge. If k<D,
the (0,D) entry is zero. If k=D, each factor must move forward exactly once.
It can do so only when its letter is the corresponding letter of w. Hence

    F_(o,i)(A)_(0,D) = c (e/2)^D != 0.

There are no terms of degree greater than D. Set input i to the last basis
vector and all other inputs to zero. The first coordinate of returned role o
is exactly this discrepancy. D=0 uses a one-dimensional space; every A_a is
(1-e)I and the discrepancy is c. This proves the claim for both coefficient
fields. The generators themselves are real in either case.

The maximum degree is essential for this construction. For F(X)=X-3I/4,
the shortest nonzero word is the constant word. Its one-dimensional shifted
path is X=3I/4 and gives zero. The degree-one construction gives discrepancy
1/8 at e=1/4. The verifier checks this distinction.

## Extract the degree without expanding words

Retain the predecessor's exact acyclic coefficient machine. Let N be its
state count, U_o the initial row for output o, T_a its transitions, and V its
terminal map to input roles. A word coefficient is U_o T_w V. Every transition
strictly decreases the state index. Thus all products of N transitions vanish.

For each d, form a basis B_d of the span of all rows U_o T_w with |w|=d.
Use the original reachable rows as the basis vectors and retain their output
and word. Begin with the initial rows at d=0. Apply every T_a to B_d and use
exact elimination to select B_(d+1). Induction proves that these rows span
exactly the length-d reachable space. A nonzero degree-d coefficient exists
if and only if some selected row has a nonzero terminal projection. Keep a
nonzero projection at the last such degree. This returns an actual word and
coefficient, not a linear combination of words.

The implementation does not merge bases from different degrees. The source
compiler has N=2r+q_left+q_right states; an explicit target contributes the
sum of its displayed term lengths in place of q_right. We use at most N
layers, at most N basis rows per layer, and at most |alphabet| N candidates
per later layer. Straight exact elimination needs O(|alphabet| N^4) field
operations. This is an arithmetic bound, not a bit-complexity or wall-time
claim. D is at most the maximum unary dependency depth and at most N-1.

If all projections vanish, the argument proves equivalence. The exported
negative-witness checker deliberately accepts only nonzero literal witnesses;
use the predecessor's separate certificate checker for positive certificates.
The new checker does not rely on the producer's degree computation: it builds
the prescribed symmetric path action and executes the original program and
its reference or target separately. It checks the predicted nonzero output.

## Credit, evidence and limits

The path separation argument is an elementary constructive specialization of
free-algebra evaluation. No global literature priority or new general PIT
algorithm is claimed. The source compiler and exact scalar code are retained
byte-for-byte from zxv. Its weighted-automata foundation credits Stefan Kiefer,
[Notes on Equivalence and Minimization of Weighted Automata](https://arxiv.org/abs/2009.01217),
and Ran Raz and Amir Shpilka,
[Deterministic Polynomial Identity Testing in Non Commutative Models](https://www.cs.tau.ac.il/~shpilka/publications/RazShpilka_PIT.pdf).
The new contribution is the quantified SPD/conditioning interface, exact-degree
adapter, and independently transcribed literal diagnostic. See NOTICE.md for
retained project credit and SOURCES.json for exact pending-predecessor pins.

The source-bound wrong-order echo and random finite checks corroborate the
written proof. They do not replace its quantified argument. Python, exact
scalar arithmetic, source transcription and the mathematical proof remain in
the trust base. No independent human or proof-kernel acceptance is claimed.
No native-relation realization, nonlinear or rounded leaf, physical operation
count, complete multiplication theorem, supplier admission or new kappa is
proved. The selected frontier is unchanged.
