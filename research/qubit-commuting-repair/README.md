# Sharp commuting repair for a Hermitian qubit triple

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite corroboration.
It answers the dimension-two case of David Ganz's explicitly unproved
[atlas B099](../pure-math-atlas-400/volumes/02-geometry.md#b099),
[PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849).
The new result is an exact repair formula, every minimizer, and the sharp
square-root constant for this case. Global literature priority and independent
human and formal proof-kernel review are unclaimed.

## Result

Let A_1,A_2,A_3 be arbitrary two-by-two Hermitian contractions. Use the atlas
normalization ||M||_(2,2)^2 = Tr(M* M)/2, and put

$$
\delta^2=\sum_{i<j}\|[A_i,A_j]\|_{2,2}^2,\qquad
E^2=\min_{\substack{B_i=B_i^*,\ \|B_i\|\le1\\[B_i,B_j]=0}}
           \sum_{i=1}^3\|A_i-B_i\|_{2,2}^2.
$$

Write A_i = a_i I + v_i dot sigma, with a_i real, v_i in R^3 and
sigma = (X,Y,Z) the usual Pauli matrices. Let
S = sum_i v_i v_i^T have eigenvalues lambda_1 >= lambda_2 >= lambda_3 >= 0.
Then

$$
E^2=\lambda_2+\lambda_3,\qquad
\delta^2=4(\lambda_1\lambda_2+\lambda_1\lambda_3+\lambda_2\lambda_3),
\qquad E\le 3^{-1/4}\sqrt\delta.
$$

Every minimizing triple is

$$
B_i=a_i I+(v_i\cdot n)(n\cdot\sigma),
$$

where n is a unit vector in the top eigenspace of S. The formulas include
S=0. For a noncommuting triple equality in the bound holds exactly when
S=r^2 I for some r>0, equivalently when the three v_i are mutually orthogonal
and have equal length r. The constant 3^(-1/4) is best possible even for
arbitrarily small positive delta. No exponent greater than one-half can
replace one-half with a constant uniform over these qubit triples near delta=0.

## Proof

The Pauli matrices are orthonormal for normalized Hilbert-Schmidt inner product.
Their multiplication identity gives

$$
\|aI+v\cdot\sigma\|_{2,2}^2=a^2+|v|^2,\qquad
[v\cdot\sigma,w\cdot\sigma]=2i(v\times w)\cdot\sigma.
$$

The eigenvalues of A_i are a_i +/- |v_i|. Thus the contraction condition is
|a_i|+|v_i| <= 1, and two Hermitian qubit matrices commute exactly when their
Pauli vectors are collinear. This elementary representation is classical.

Any commuting Hermitian triple has the form b_i I + t_i n dot sigma for one
unit vector n. The all-scalar case allows any n. Orthogonal projection gives

$$
\sum_i\|A_i-B_i\|_{2,2}^2
=\sum_i(a_i-b_i)^2+\sum_i|v_i-t_i n|^2
\ge\operatorname{tr}S-n^TSn
\ge\operatorname{tr}S-\lambda_1.
$$

For any top unit eigenvector n, choose b_i=a_i and t_i=v_i dot n. Both
inequalities are then equalities. These choices are contractions because
|a_i|+|v_i dot n| <= |a_i|+|v_i| <= 1. This proves the exact minimum without
relaxing the feasible contraction set. Conversely, equality in the displayed
sum forces b_i=a_i and t_i=v_i dot n. Equality in the Rayleigh bound forces n
to belong to the top eigenspace. This proves the minimizer classification.
The rank-one approximation step is classical; the contribution applies it to
the precise atlas repair contract and determines the sharp constant below.

The cross-product identity yields delta^2 = 4 sum_(i<j) |v_i cross v_j|^2.
Expanding the trace of S^2 shows that twice this latter sum is
(tr S)^2 - tr(S^2), so the claimed eigenvalue formula follows. Finally,

$$
\begin{aligned}
\delta^2-3E^4
&=4(\lambda_1-\lambda_2)(\lambda_2+\lambda_3)
 +(\lambda_2-\lambda_3)(\lambda_2+3\lambda_3)\ge0.
\end{aligned}
$$

All factors are nonnegative. If the triple does not commute, lambda_2>0.
Both terms vanish exactly when lambda_1=lambda_2=lambda_3. If lambda_2=0,
all vectors are collinear and E=delta=0. With three vectors, positive
S=r^2 I also implies V V^T=r^2 I for the matrix V with rows v_i, proving
the stated orthogonality characterization.

For sharpness take (A_1,A_2,A_3)=(rX,rY,rZ), 0<r<=1. The matrices are
contractions, E^2=2r^2 and delta^2=12r^4. Hence E^4/delta^2=1/3 at every r.
For any alpha>1/2 the ratio E/delta^alpha is a positive constant times
r^(1-2alpha), which tends to infinity as r decreases to zero. This proves
both sharpness claims. It completes the written proof; finite checks below
corroborate its identities rather than establish its real universal quantifiers.

## Evidence and reproduction

From the repository root, use CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -Werror -B research/qubit-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -Werror -B research/qubit-commuting-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/qubit-commuting-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/qubit-commuting-repair --check-source-history
```

The interpreter path is specific to the contribution environment. Elsewhere
substitute a CPython 3.12 executable. The standalone verifier emits
PASS_QUBIT_COMMUTING_REPAIR and a receipt bound to the five package-file hashes.
It writes no files. No receipt is hand-written or committed.

The checker uses exact rational realifications of literal complex matrices.
It checks 729 ordered matrix pairs, all 19,683 triples of integer vectors in
{-1,0,1}^3 for the covariance identity, and 1,000 explicit spectral repairs.
The latter include zero, rank-one, rank-two, repeated-eigenvalue and distinct
positive spectra, noncoordinate rational frames, and nonzero scalar parts.
The two-by-two observable pair fixtures scale the integer vectors by 1/4.
There are 150 noncommuting equality fixtures among the spectral repairs.
It also checks 32 scaled Pauli attainers and eleven rejection controls.
The controls reject invalid contractions, wrong eigendirections, wrong norms,
noncommuting repairs, shifted scalar parts, suboptimal scalar repairs and a
false stronger constant. These are finite counts, not a census of all inputs.

## Scope and sources

B099's all-dimension universal constant is still unresolved here. This is a
fixed-dimensional side result. It does not give a paid native decoder, an
integer-multiplication supplier, new kappa or a selected-frontier change.
Physical routing, dirty restoration, compiler, stock, precision/tape and the
complete supplier bill remain outside scope. No selected cold replay, Lean
build, Docker replay or predecessor scientific suite was run.

Credit David Ganz for atlas B099, its exact normalization and the simultaneous
repair question. Classical Pauli coordinates and best rank-one approximation
retain their standard credit. Islam Faisal, Anand Natarajan and Alexander
Poremba's [qubit rounding work](https://arxiv.org/abs/2605.26096), sections 3.1
and 3.2, supplies related pinching and scalar-rounding context. It is not used
as a proof premise or claimed as this result. Their two-local Hamiltonian
problem and operator-norm bill differ from the exact normalized-HS triple
minimum computed here. Lev Glebsky's [normalized-HS work](https://arxiv.org/abs/1002.3082)
is background on dimension-uniform qualitative repair. No claim that this
short qubit calculation is new to the literature is made.

The base, selected record, original card and exact atlas bytes are recorded in
SOURCES.json and TASK.json. Existing source and contributor credit are unchanged.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147024)
records the bounded target and overlap coverage. Search coverage includes live
open/account PRs, active Discussions, latest handoffs, targeted main-package
and merged-PR searches, and the cached card scan. It excludes unpublished work
and a complete historical code-diff or literature audit.

## Implementation bounds

The verifier has no recursion, network, subprocesses or external dependencies.
All loops run over the fixed grids above, matrices have dimensions at most four,
and no function exceeds 60 lines. Explicit require checks remain active under
optimized Python. Warnings are errors in both registered commands. The package
runner checks the declared source hash; the standalone theorem checker imports
no predecessor executable.

Power-of-ten rule 3 has a bounded managed-runtime deviation in verify.py.
CPython integers, Fractions and tuples allocate during checking, so fixed
allocation after initialization cannot be met. At most one triple and its
matrices are processed at a time; grids hold 27 vectors and five frames, and
integer/rational inputs and all iteration counts are fixed in the source.
No candidate history accumulates. The normal and optimized full replays verify
these bounded paths. Revisit this choice if externally supplied dimensions or
grids are added. The standard-library dataclass only defines the eight-field
immutable witness record; all verification branches and calls remain explicit.
No external static analyzer was installed. Warning-strict execution and AST
syntax/function-size inspection passed; the longest function has 28 lines.

## Open next questions

1. Does this sharp constant extend to triples with a known common invariant
   decomposition into blocks of dimension at most two? Such a result would
   give a dimension-uniform structured case of B099. Start by combining the
   proved qubit repairs with the normalized-HS block weights. A proof must
   account for global normalization and distinguish a constructive upper bound
   from the globally optimal repair, which could mix blocks.
2. What bound holds for general three-by-three Hermitian contractions? This
   is the next fixed dimension beyond the Pauli collinearity argument. Start
   with a specific spectral clustering rule and the complete summed repair
   error. The current exact reduction relies on dimension two and does not
   supply a qutrit formula.
