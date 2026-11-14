# Lifting joint funding to arbitrary finite array dimension

**Written block-linear extension, checked by two separate adversarial reviews.**
The scalar derivation is lifted below to arbitrary finite array dimension.
This draft assigns fractional accounting weights to scalar columns solely
to lower-bound the cost of fully lost original helper fields. It does not
create fractional productive jobs or permit unpriced target decoding.

Let F be an infinite field of characteristic zero, let V=F^D, D>=1, and let
all native input variables be full vectors in V. Original normalized source
maps have scalar rational coefficients, so the covector space belonging to
a scalar source-row space A is A tensor V*. Let U now be an arbitrary linear
subspace of helper covectors H tensor V*. In particular, its matrices may
couple different array entries and need not commute. The helper promise is
ker U; original retained helper vectors indexed by I remain jointly arbitrary.

## Expanded-coordinate funding

Each original helper field h has D entry-columns. Assign each such column
the accounting weight f(R_h)/D. A fully lost helper field pays the total
weight f(R_h). Surjectivity onto retained whole helper vectors forces
restriction of U, and every necessary subspace W within U, to the lost
entry-columns to be injective. Thus the lost fields contain a column basis
for W. Their actual target debit is at least the minimum expanded column-basis
weight, denoted b_D(W).

If W=A tensor V*, each target-rank prefix has rank D times the scalar prefix
rank. The ordinary weighted-column greedy formula therefore gives

    b_D(A tensor V*) = beta_f(A).

This exact identity includes all whole zero-MOVE constraints. For an actual
zero set S, the necessary subspace is Z tensor V*, where Z=span(S).

## A whole newly enabled cache forces D new directions

Suppose a cache E is not enabled by the zero constraints alone:
`c_E notin P_E+Z`. Exact deterministic reconstruction of the entire target
vector from the original history on the linear domain implies, for each
basis covector e_a of V*,

    c_E tensor e_a = p_a + u_a,
    p_a in P_E tensor V*,  u_a in U.

The helper-only condition on u_a places it in L_E tensor V*, because
intersections of finite-dimensional subspaces commute with extension by V*.
The D vectors u_a are independent modulo Z tensor V*. Indeed, a nontrivial
combination would give `c_E tensor v` in `(P_E+Z) tensor V*` for nonzero v.
A scalar separating functional annihilating P_E+Z but taking c_E to one
would then send that inclusion to `v=0`, a contradiction.

Therefore

    W_E = (Z tensor V*) + span(u_1,...,u_D)

has rank D(rank Z+1). On the expanded target-rank prefix C_k tensor V*, its
rank is bounded by both D rank(Z|C_k)+D and D rank((Z+L_E)|C_k). Hence

    rank(W_E | expanded C_k)
      <= D min(rank(Z|C_k)+1, rank((Z+L_E)|C_k)).

Take the generic scalar row u in L_E outside Z from the scalar proof.
The space `(Z+span u) tensor V*` attains all these upper bounds and has the
same full rank as W_E. Larger cheap-prefix ranks make a minimum basis no
more expensive. Consequently

    b_D(W_E) >= beta_f(Z+span u) = gamma_E.

One can prove the price comparison directly by summation by parts: at fixed
full rank, the greedy price is the largest-rank price times full rank minus
the sum of each increasing price gap times the corresponding prefix rank.
This avoids assuming that special and generic block column matroids coincide.

Every newly enabled cache supplies its own D-direction necessity. The actual
debit is at least the maximum of the individual gamma_E values. It is not
necessary for their generic witnesses to be simultaneously realizable.

## Local bounds and global composition

The largest and two six-zero block proofs also lift. Their zero relations
become tensor spaces; their required disjoint unit coordinates become
D-dimensional disjoint coordinate blocks. Appending a new cache adds D
dimensions, with each additional column priced at least f(a)/D when the
entire relevant support has rank at least a. The resulting extra debit is
at least f(a), exactly the scalar bound. The smaller blocks use the gamma_E
inequality above. Thus every local scalar upper profile remains valid.

The exact scalar group decomposition is a direct sum. Tensoring with V*
preserves that direct sum. Select the necessary zero and cache relation rows
within each tensor group and apply Laplace expansion to an expanded-column
basis determinant. The disjoint column partition in a nonzero term pays
at least the sum of local minimum expanded basis weights. Overlapping whole
helper supports do not double-count target credit: their D separate entries
carry weights summing to the single whole helper price.

This proves the same fine envelope for arbitrary finite D and arbitrary
block-linear helper promises, including noncommuting matrix coefficients.
The source frame/phase/whole-job contract is still inherited; this argument
does not itself establish the selected native_all_columns assumption.

## Boundaries that must remain explicit

- Only entire original MOVEs are deleted or replaced. A proposal that splits
  a MOVE into partially cached subjobs needs its own productive and paid types.
- Only fully retained original helper fields receive the original target price.
  Other fields are fully debited. New decoded target prices are not inferred.
- Main arrays remain arbitrary independently of helpers. Original source rows
  and earlier information sets are unchanged, though processing may use any
  linear operators or deterministic functions compatible with the linear domain.
- This is finite-dimensional for every D; no infinite-dimensional limit or
  topological duality is invoked.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Classical tensor-space, duality, weighted-matroid and determinant facts are
not claimed as new. Separate independent algorithmic/mathematical reviews are included under extensions/.
Neither independent human nor formal proof-kernel acceptance is claimed.
