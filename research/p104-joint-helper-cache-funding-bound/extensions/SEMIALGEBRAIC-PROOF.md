# Semialgebraic promises reduce to one common block-linear tangent

## Claim and dependency

Let `a` be the number of main fields. Fix a finite source with normalized real-linear history maps `A_e`, whole
target maps `c_e`, and linear rows `z_j` for MOVE values that are promised to
be zero. Let the helper promise be a semialgebraic set

`S ⊆ (R^D)^H`,

independent of all main inputs. Let `I` be the retained original helper fields,
and let `π_I:S→(R^D)^I` be coordinate projection. Assume `π_I(S)` contains a
nonempty Euclidean open set. Each cached whole target is assumed to be an
exact deterministic function of its fixed original history on
`(R^D)^a × S`; each `z_j` vanishes on the full main/helper product domain.

Then one real block-linear tangent space preserves every cache and every zero
MOVE simultaneously, and its projection onto the retained original fields is
surjective. The implication to the joint fine source envelope uses the
separate all-block funding theorem: it upper-bounds the tangent's optimistic
gain, and tangent projection makes its minimum debit no larger than the
actual fully debited original coordinates. This is a reduction of the
semialgebraic promise to that linear funding theorem. It makes no source
admission, physical implementation, foundational-assumption, or new-κ claim.

The proof applies to reducible, singular, nonclosed semialgebraic sets and
does not assume an initial smooth patch or a retained submersion. It does not
apply to arbitrary nonsemialgebraic promises with the same set-theoretic
projection property.

## Select a stratum that sees an open retained image

Write `n=D|I|` and identify the retained array coordinates with `R^n`. By
Tarski–Seidenberg, the image `π_I(S)` is semialgebraic. Apply the
Drusvyatskiy–Ioffe–Lewis stratification theorem (Theorem 3.4) to
`π_I:S→R^n`, choosing the target collection to include `π_I(S)`. It gives
finite analytic source and target stratifications such that:

1. each source stratum `M` is a smooth semialgebraic manifold;
2. `π_I|M` has constant rank; and
3. `π_I(M)` is a target stratum.

The target strata partition `π_I(S)`. A finite union of semialgebraic sets
of dimension below `n` has empty interior in `R^n`. Since `π_I(S)` contains
an open set, at least one target stratum inside `π_I(S)` has dimension `n`.
Because the source-stratum images cover `π_I(S)`, some source stratum `M`
maps onto such a full-dimensional target stratum. The constant-rank theorem
then gives

`rank(dπ_I(p)|T_pM)=n`

at every `p∈M`. In particular, `M` is a retained-submersion stratum. It need
not be a whole connected component of `S`; lower-dimensional and singular
parts of `S` can be left behind.

This step is the reason an open projected image matters. Surjectivity onto
the entire retained space is sufficient but stronger than needed.

## Choose one point regular for every fixed history map

For each cache `e`, let

`F_e(m,p)=A_e(m,p)`, for `(m,p)∈R^{D a}×M`.

This is the restriction of a fixed real-linear map to a smooth semialgebraic
manifold. Its differential rank has finitely many values, and the level sets
of that rank are semialgebraic: in local semialgebraic charts the relevant
Jacobian minors are semialgebraic. The union of the relative interiors of
these finitely many rank level sets is open dense in `M`. Equivalently, one
may refine `M` by the finite tuple of ranks of all `F_e`; a top-dimensional
piece is relatively open in `M` and has every rank constant.

There are finitely many history maps, so intersect their open dense
locally-constant-rank loci. Choose one `p∈M` in that intersection. The
retained projection still has rank `n` at `p`, since this selection only
restricts to a relatively open subset of `M`. Choose any main point `m`.
The full product manifold

`N=R^{D a}×M`

has tangent `W=R^{D a} ⊕ T_pM` at `(m,p)`, and every history map `F_e|N`
has locally constant rank near that point. One and the same `W` is used for
all caches and zero rows.

## Exact recovery implies tangent factorization

No smoothness of a cache decoder is needed. Let `g_e` be any deterministic
function satisfying

`c_e(x)=g_e(A_e(x))` for every `x∈N`.

Take a tangent vector `v∈ker(dA_e|W)`. The constant-rank fiber theorem gives
a smooth curve `γ` in `N`, through `(m,p)`, tangent to `v`, and contained in
the local fiber of `A_e`. Along `γ`, the observation is constant. Exact
deterministic recovery therefore makes `c_e(γ(t))` constant, so
`dc_e(v)=0`. Since `A_e` and `c_e` are ambient linear maps, their derivatives
on `W` are just their restrictions. Hence

`ker(A_e|W) ⊆ ker(c_e|W)`.

Define `B_e(A_e v)=c_e v` on `A_e(W)`. The kernel inclusion makes this
well-defined and linear; extend it linearly to the full observation space.
Thus `c_e|W=B_e A_e|W`. This argument applies at the chosen common point to
all finitely many history/target pairs, even if the original decoders are
discontinuous or nonunique away from their exact target values.

Each promised zero row `z_j` vanishes on all of `N`; differentiating its
identically zero value gives `z_j|W=0`.

The helper tangent `T=T_pM` projects onto all retained real array
coordinates. Set `U=T^⊥` in the real helper covector space. If a covector
`u∈U` restricts to zero on the fully debited helper coordinates `J=H\\I`,
then it is supported on `I`. For every `q_I∈R^{D|I|}`, submersion gives a
`v∈T` with `π_I(v)=q_I`; consequently `u(q_I)=0` for every `q_I`, and
`u=0`. Therefore restriction from `U` to the `J` columns is injective, so
the original fully debited fields contain a column basis of `U`.

The tangent retains at least the original cache and zero-MOVE benefits,
while its minimum lost-helper target price is at most the price of all
fully debited coordinates `J`. So its optimistic net gain is no smaller
than the original promise's gain. Applying the all-block funding bound to
this single tangent yields the joint fine envelope for the stated
semialgebraic class.

## Edge cases and exclusions

### Empty retained set

If `I=∅`, the target is `R^0={0}`. The open-image hypothesis is exactly
`S≠∅`; the retained differential has rank zero automatically. The tangent
argument still works, and `J=H`, so no original helper field is retained
from the funding debit. This vacuous projection case is explicit.

### Finite grids

For nonempty `I`, a finite grid projects to a finite subset of `R^n` and
contains no nonempty open set. The theorem makes no claim that such a grid is
equivalent to an open projected image or that discrete decoding can be
replaced by a tangent. When `I=∅`, a nonempty finite `S` satisfies the
vacuous open-image condition, but the debit includes every helper field.
Nonsemialgebraic encodings with an open retained projection are outside the
claim.

### Complex arrays

Treat `C^{D H}` as `R^{2 D H}`. For normalized source maps with rational-real
coefficients, their realifications are real-linear block maps and the
selected real tangent is block-linear. This deduction uses this source's common rational-real scalar maps; no generalization to arbitrary complex
normalized coefficient blocks is asserted. It does not identify a real tangent
with a complex-scalar subspace and does not invoke the scalar-linear complex theorem. The funding conclusion uses the corresponding
real block-linear funding theorem.

The result does not cover promises depending on main inputs, approximate or
probabilistic recovery, changed histories/maps, or arbitrary nonsemialgebraic
sets. A finite-grid example with positive-dimensional retained coordinates
is excluded by the open-image hypothesis; it is not a counterexample to the
semialgebraic statement.
