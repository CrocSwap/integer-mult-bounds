# Independent adversarial review of the finite block lift

Conclusion: the block extension in the reviewed draft is valid under its
stated hypotheses. I found no counterexample. In particular, it covers
arbitrary finite-dimensional block-linear helper promises, with operators
that mix entries and need not commute, while retaining the scalar fine
funding ceiling. This is conditional source algebra and funding, not a
physical construction, an attained kappa, or an all-column admission proof.
The exact draft and source-proof hashes appear in `RESULT.json`.

Let the scalar covector space split into main and helper coordinates, and
let V have finite dimension D. Original source row spaces become A tensor
V*. This is essential: the operators in the changed helper promise may be
arbitrary, but original source operations and observations remain the
normalized common-scalar maps. The promised domain is all mains times ker U
for a helper covector space U. The retained whole original helper arrays I
are jointly arbitrary. Lost fields are fully debited; no decoded target
credit or fractional physical job is inferred.

## Funding and the full-array information condition

If restriction of a necessary W contained in U to all lost entry-columns
were not injective, a nonzero covector supported only on I would vanish on
every retained input. Surjectivity onto I excludes this. Hence some column
basis of W lies in lost entry-columns. Giving each entry of helper h price
f(R_h)/D makes the total price of all its D entries exactly its original
field price. The actual lost credit therefore bounds the minimum expanded
column-basis price b_D(W) below. These fractional weights are only a lower
bound on a whole-field debit.

Whole zero deletions require Z tensor V* contained in U. Tensor prefix
ranks multiply by D, so the ordinary greedy formula gives exactly
b_D(Z tensor V*)=beta_f(Z).

Suppose c is not in P+Z, but a whole cache becomes reconstructible on the
linear domain. Deterministic recovery, even nonlinear processing, forces
every output covector c tensor e_a to vanish on the observation kernel.
Finite-dimensional annihilator duality gives

    c tensor e_a = p_a + u_a,
    p_a in P tensor V*, u_a in U intersect (L tensor V*),
    L=(P+span(c)) intersect helper covectors.

This is a kernel implication for a linear domain; it does not assume the
processing itself is linear. Intersections commute with tensoring here by
choosing bases of finite-dimensional subspaces. The u_a are independent
modulo Z tensor V*. Otherwise a nonzero v would satisfy
c tensor v in (P+Z) tensor V*. A scalar linear functional annihilating P+Z
and taking c to one contracts that inclusion to v=0, a contradiction.

Thus W=(Z tensor V*)+span(u_a) has D(rank Z+1) dimensions. On every cheap
helper-rank prefix C_k its projected rank is at most

    D min(rank(Z restricted C_k)+1,
          rank((Z+L) restricted C_k)).

Both bounds are necessary: appending D rows increases rank by at most D,
and W is inside (Z+L) tensor V*. Generic scalar u in L outside Z attains
all the scalar prefix maxima simultaneously. Each missed maximum is a
proper linear condition on u, and a finite union of proper linear spaces
cannot cover an infinite field. The tensor generic space has the same
full rank as W and no smaller cheap-prefix ranks.

At fixed full rank, the weighted greedy price is largest-column-price
times rank minus the nonnegative price gaps times the cheap-prefix ranks.
Consequently b_D(W) >= gamma_E, the scalar generic lower debit. This needs
no equality of block and tensor matroids. Taking the maximum of individual
gamma_E lower bounds for several actual new caches is valid; simultaneous
attainability of their generic minimizers is unnecessary.

## Local refinements and composition

If the full enlarged space has all support ranks at least a, any column
basis of W contains a column basis of Z tensor V*, leaving D extra columns.
Each costs at least f(a)/D. This yields the same extra f(a) debit as the
scalar proof. The support condition must apply to the entire enlarged
space; checking only an appended row would be insufficient. The draft and
source-specific scalar proof use the former condition. Required disjoint
unit zero rows lift to disjoint D-entry blocks; their exact tensor basis
prices and already-enabled-cache conditions are unchanged.

The certified scalar component spaces form a direct sum. Tensoring
preserves it, and actual necessary local spaces remain inside those tensor
components. A global basis determinant expanded by row groups has a
nonzero Laplace term partitioning its columns into local bases. Its price
is therefore at least the sum of local minimum basis prices. Overlapping
helper supports cause no double debit: distinct entry-columns in that
partition are paid only once. Additional cross-component relations in U
cannot remove the selected necessary direct-sum subspace.

Because normalized source coefficients are rational real scalars, viewing
complex arrays as twice as many real entries preserves the common-scalar
source form. The same proof then includes real-linear operators such as
conjugation. This relies on that actual source property. It does not prove
an extension to arbitrary nonreal source blocks or infinite-dimensional
spaces, and it supplies no separate smooth/discrete-domain extension.

## Exact executed fixtures and limitations

`fixtures.py` independently constructs D=2 and D=3 examples with histories
y_i=m+X_i, zero relation X1-X2=0, and target m. Let A be the superdiagonal
shift, K=diag(2,...,2,0), B=K-A, C=Id-K. The extra relation is
A X1+B X2+C X3=0. Since A+B+C=Id, the full target is recovered as
A y1+B y2+C y3. A and B do not commute. The enlarged relation space has
rank 2D, while its prefix on helpers1 and2 has rank 2D-1, strictly below
the scalar generic tensor prefix 2D. This gives an actual non-tensor test
of the inequality, rather than merely tensor examples.

For all nine min(r,k) tariffs, exhaustive expanded-column basis enumeration
agrees with greedy pricing and bounds the block debit below by scalar
gamma. With helper ranks1,2,4, the dimension-linear block prices are4 for
D2 and11/3 for D3, versus scalar gamma3. The generic scalar witness need
not be a physical preparation. A valid lost-field set {X1,X3} passes the
surjectivity rank condition; the cheaper set {X1,X2} fails it. Actual whole
field loss can therefore exceed the fractional accounting minimum.

Two further adversarial controls matter. With only D-1 appended entry
relations, exactly D-1 target entries can be recovered, and the expanded
debit is below scalar gamma; the whole-output validator rejects that
proposal. For two independent tensor groups supported on the same helpers,
exhaustive pricing confirms the Laplace lower bound. Repeating the same
group instead is dependent and would permit a double spend; the direct-sum
validator rejects it. The tests execute in normal and optimized Python,
with identical logical results after omitting runtime.

The universal proof is the dimension/rank/greedy/Laplace argument above;
finite fixtures are controls for its hypotheses and inequalities. The
conclusion remains conditional on the actual fixed source histories,
whole original MOVE credit, original whole helper prices, independent
arbitrary mains, and every foundational physical assumption. Changed
producer histories, partial cache jobs, decoded productive targets, or
promises on a discrete grid alone are outside this review.
