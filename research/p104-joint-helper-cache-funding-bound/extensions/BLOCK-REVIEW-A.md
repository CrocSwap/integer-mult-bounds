# Independent review of the finite-dimensional block lift

Review conclusion: the proposed block lifting follows under the stated
whole-job, fully debited helper, fixed normalized history hypotheses. The
proof below independently reconstructs the critical inequalities. It does
not establish native_all_columns, an implementation or a new kappa.
The reviewed draft's exact SHA256 is recorded in SOURCES.json.

Let F be an infinite characteristic-zero field, V=F^D finite-dimensional,
and give each helper's D entry-columns accounting weight f(R_h)/D. These
are artificial lower-bound weights, NOT fractional jobs or a physical
rank/dimension scaling law. Source scalar row spaces A become A tensor V*.
Let U be an arbitrary block-linear helper-relation rowspace; matrices may
mix entries and need not commute. Main arrays remain independent.

## Fully debited fields fund expanded-coordinate bases

Surjectivity onto retained whole helper arrays makes restriction of U to
lost entry-columns injective: any covector supported only on retained
entries and annihilating the domain must be zero. The lost columns span
U and every necessary W contained in U. Some expanded column basis can
therefore be chosen from those columns. Its minimum price b_D(W) is at
most the actual debit sum_h f(R_h), because all D entry weights of a fully
lost helper sum to its single original price. No fractional target credit
is inferred.

For W=A tensor V*, prefix ranks at helper target rank<=k are D times
scalar prefix ranks. Weighted-column greedy selection gives
b_D(A tensor V*)=beta_f(A). Whole zero MOVE deletion requires every one
of its D target entry covectors to lie in U, hence Z tensor V* is contained
in U for the actual whole zero set S.

## A whole new cache requires D independent directions

If c is not in P+Z, exact recovery of the WHOLE target array on the linear
domain gives, for every basis e_a of V*,

    c tensor e_a = p_a + u_a,
    p_a in P tensor V*, u_a in U.

This follows by linear kernel inclusion, even if the deterministic cache
function is nonlinear. Since u_a is helper-only, it belongs to
L tensor V*, L=(P+span(c)) intersect helper space. Tensoring finite vector
spaces commutes with these intersections (choose compatible bases).

The u_a are independent modulo Z tensor V*. If their nonzero combination
belonged there, c tensor v would belong to (P+Z) tensor V* for nonzero v.
Choose a scalar functional lambda with lambda(P+Z)=0 and lambda(c)=1.
Contraction lambda tensor Id would give v=0, a contradiction. This is
where whole-output reconstruction matters.

Thus W_E=Z tensor V*+span(u_a) has full rank D(rho+1). On each expanded
cheap-column prefix its rank is at most both D rank(Z_k)+D and
D rank((Z+L)_k). The generic scalar row u in L outside Z attains
min(rank Z_k+1,rank(Z+L)_k) simultaneously. Therefore its tensor space G
has the same full rank as W_E and at least as large every cheap prefix.

At fixed full rank R, weighted greedy price is

    alpha_9 R - sum_{k=1}^8 (alpha_{k+1}-alpha_k) rank(prefix_k),
    alpha_k=f(k)/D.

The coefficients subtracted are nonnegative. Hence b_D(W_E)>=b_D(G)
=beta_f(Z+span(u))=gamma_E. This uses prefix domination, not an assertion
that arbitrary block column matroids equal the scalar tensor matroid.
The generic scalar row is only a lower debit witness; it need not be a
physical provider or simultaneously enable several caches.

Every actual new cache supplies its own necessity; taking the maximum
of these individual gamma_E lower bounds is valid. If L is contained in
Z, that new-cache case is impossible.

## Composition and specific support refinements

The certified scalar source component spaces form a direct sum. Tensoring
preserves it. Select actual necessary W_g in each tensor component.
Their direct sum is contained in U even when U has additional constraints
mixing components. A nonzero expanded column-basis determinant, expanded
by row blocks, has a nonzero Laplace term assigning disjoint entry-column
sets to the groups. Thus b_D(U)>=sum_g b_D(W_g). Overlapping original
helper supports cause no double charge: each entry column is allocated
once and a fully lost field pays the sum of its D accounting weights.

For a support-minimum refinement, a whole new cache adds D directions
beyond Z tensor V*. If all relevant columns have rank>=a, a basis for
W_E contains a basis for Z tensor V* and D further columns, each priced
at least f(a)/D. Their extra debit is at least f(a), matching the scalar
proof. Required disjoint unit helper coordinates become disjoint D-entry
blocks with the same total prices. The scalar local inequalities thus
survive, including the largest-block refinements.

## Realification and adversarial boundaries

This native source's normalized row coefficients are rational REAL
scalars. A complex D-array can therefore be represented by2D real entries
with source maps A tensor Id_(2D). Assign f(R_h)/(2D) to each real entry;
its whole complex helper still pays exactly f(R_h). Real-linear block
relations, including conjugation, are allowed by the same proof. This
would need a different source formulation if normalized coefficients
were arbitrary nonreal blocks rather than common real scalars.

The essential boundaries are: entire original MOVEs/outputs only; fixed
original target prices; fully retained or fully debited original helper
fields; main arrays independent of helpers; unchanged source histories
and normalized scalar maps; finite D; and all original framework
assumptions retained. Partial output recovery cannot take full cache
credit. In the executed D2/D3 fixtures, D-1 relations have a basis debit
smaller than gamma_E but fail to reconstruct the missing output entry.
That is a counterexample to dropping the whole-output requirement.

Exact fixtures exercise noncommuting blocks for D2,D3, prefix domination
strictness, whole-helper funding and Laplace composition with overlapping
helper supports. They pass in normal and optimized Python. These finite
fixtures support validation; the universal argument is the proof above.
No physical provider or compiler/grid admission follows from it.
