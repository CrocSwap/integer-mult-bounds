# Exact boundary for moving truncation across a linear frame

We characterize the complex linear maps that commute with componentwise
truncation toward zero. Each output must select one input, multiplied by
one of `1, -1, i, -i`, or equal zero. For a unitary square map this means a
permutation with those four phases. We also give exact unitary counterexamples
and a family whose discrepancy, in grid units, grows with dimension.

The retained transform proof uses signed coefficient permutations and satisfies
this criterion. We report no defect in that proof and no new kappa.

## Source and downstream use

In `upstream/build/sections/06-transforms.tex`, the author defines `Q_p` at
`eq:transform-truncate` and moves it across `J_E` in the forward-round argument
after `eq:combined-twiddle`. The author uses this equality to charge one
truncation after the exact contraction round. A researcher replacing `J_E`
must establish that equality or account for the extra error. Unitarity alone
does not establish it, even for a scalar phase that preserves the maximum norm.

We pin that source and the prior layout audit in [SOURCES.json](SOURCES.json).
The prior audit in `research/synthetic-layout-independent` excludes `Q_p`
truncation from its scope. Our positive controls implement the source's
negacyclic monomial by two separate exact recipes. We do not replay its complete
layout, suppliers or analytic reduction.

## Quantified statement and proof

Fix an integer `p >= 1`, put `h = 2^-p`, and define

`Q_p(z) = h (trunc(Re(z)/h) + i trunc(Im(z)/h))`,

with truncation toward zero. Apply this definition to each coordinate.
For a complex matrix `A` of size `m` by `n`, the following are equivalent:

1. `Q_p(Ax) = A Q_p(x)` for every `x` in `C^n`.
2. The same equality holds for every `x` with `max_j |x_j| <= 1`.
3. Each row of `A` is zero or has exactly one nonzero entry in `{1,-1,i,-i}`.

**Proof.** Implication 1 to 2 follows by restriction. To prove 2 to 3, choose
`x = h e_j`. Since `Q_p(x) = x`, each entry of `A e_j` must have integer real
and imaginary parts. Thus every matrix entry is a Gaussian integer.

For any row write its entries as `a_j + i b_j`, with integers `a_j,b_j`.
Set

`x_j = (3h/4) (sgn(a_j) - i sgn(b_j))`, with `sgn(0)=0`.

Each real and imaginary input component has magnitude below `h`, so
`Q_p(x) = 0`. Also `|x_j| <= 3 sqrt(2) h/4 < 1`, as `p >= 1`.
The real component of this row's output is

`(3h/4) sum_j (|a_j| + |b_j|)`.

If the integer sum is at least two, that component is at least `3h/2`;
its truncation cannot be zero. This contradicts 2. The sum is therefore at
most one, giving precisely 3. Finally, toward-zero truncation is odd and
commutes with swapping real and imaginary parts. It therefore commutes with
the four phases, coordinate selection and duplication, proving 3 to 1.

For a square unitary `A`, each row has norm one and distinct rows are
orthogonal. Condition 3 then forces one unit entry per row in distinct
columns. Conversely, those monomial matrices are unitary and satisfy 1.

This proof also constructs a witness for any rejected matrix: use a grid
basis input if an entry is not a Gaussian integer; otherwise use the signed
subgrid input above for an offending row. The rational verifier implements
this witness construction. The written proof covers arbitrary complex entries;
the finite census alone does not prove that extension.

We quantify over every disk input. A researcher who proves a narrower set of
reachable intermediate states may establish commutation on that set for other
maps. This classification does not exclude such a restricted-state argument.

## Two unitary counterexamples

**A scalar maximum-norm isometry.** Take `p=1`, `x=1/2` and
`u=(3+4i)/5`. Then

`u Q_1(x) = 3/10 + 2i/5`, but `Q_1(u x) = 0`.

Both `x` and `ux` belong to the unit disk. The discrepancy has modulus `1/2`.
Thus even a disk-preserving unitary map can invalidate the exact rounding move.

**Dimension-dependent discrepancy.** Let `k>=2`, `n=4^k`, and let `H` be the
Sylvester matrix of order `n`, with entries
`H[a,b]=(-1)^popcount(a & b)`. Pairing each nontrivial binary character with
a coordinate on which it is nonzero gives zero row sums; hence
`H H^T=n I`. The rational matrix `U=H/2^k` is orthogonal.

For any `p>=k`, put `x_j=3h/4`. Then `Q_p(x)=0`, whereas

`Ux=(3*2^(k-2) h, 0, ..., 0)`.

Its first component is on the grid, so `Q_p(Ux)=Ux`. Both input and output
are disk arrays: their largest magnitudes are at most `3/4`. The discrepancy
is exactly `(3/4) sqrt(n)` grid units. No dimension-independent constant
times `h` bounds this commutation error over such unitary maps.

This family concerns Euclidean unitarity. Dense `U` is not a contraction in
the source's maximum norm on every input. We verify disk membership for the
displayed witnesses; we do not claim that `U` meets the source's full round
contract. The scalar example already defeats the weaker isometry inference.

## A charged replacement for exact commutation

A researcher can bound the error without exact commutation. For any complex
matrix `A`, let `M = max_i sum_j |A[i,j]|`, its induced maximum norm.
Write the commutator as

`Q_p(Ax) - A Q_p(x) = (Q_p(Ax) - Ax) + A(x - Q_p(x))`.

Using the source's component-truncation bound on each term gives

`||Q_p(Ax) - A Q_p(x)||_infinity < sqrt(2) h (1+M)`.

For a unitary matrix of order `n`, Cauchy-Schwarz gives `M <= sqrt(n)`.
The Hadamard family proves that this square-root dependence cannot be
replaced by a dimension-independent bound. For a true maximum-norm
contraction, the bound is instead less than `2 sqrt(2) h`.

For example, a researcher who can carry both computations on a finer grid
can choose `g = ceil(log_4 n) + 2` extra fractional bits. Since
`2^ceil(log_4 n) >= sqrt(n)`, the unitary commutator at precision `p+g`
is less than one original `p`-grid unit. This bounds only the commutator
at the finer grid. It does not equate the original coarse-grid outputs,
prove that a rounded inverse restores dirty data, or pay for wider arithmetic,
additional storage, or other errors in a complete round. We make no
production precision recommendation without those charges.

## Reproduce and evidence

Use Python 3.10 or newer with the standard library:

```sh
python3 -I -O -B research/truncation-frame-transport/verify.py
python3 scripts/research_package.py --package research/truncation-frame-transport --check-only
python3.12 scripts/research_package.py --package research/truncation-frame-transport
```

The verifier checks input SHA256 pins before arithmetic and writes no files.
Its explicit checks remain active under `-O`. Reviewers can expect:

- 2,401 two-entry complex rows over real/imaginary alphabet
  `{-2,-1,-1/2,0,1/2,1,2}`: nine admissible rows and 2,392 rows with exact
  constructed counterexamples, each at precisions 1 and 3. For every admitted
  row, we check 2,401 complex input pairs at each precision.
- 372 signed monomial cases at lengths 2, 4, 8 and 16, including negative
  exponents, zero displacement, split/merge agreement and inverse recovery.
- Rational Hadamard cases in dimensions 4, 16, 64 and 256. Direct character
  sums and a separate butterfly implementation agree. The discrepancies are
  1, 3, 6 and 12 grid units; the first case also covers the floor boundary.
- Six failure controls: arbitrary unit phase, integer amplification,
  fractional contraction, coordinate sum, real/imaginary mixing, and
  substituting floor for toward-zero truncation.
- The charged error bound on the 4,784 row witnesses and the integer
  guard-width inequality for dimensions 1 through 4,096.

We ran the registered replay on macOS arm64 with CPython 3.12.13 and obtained
`PASS_REGISTERED_RESEARCH_PACKAGE`. Optimized CPython 3.14.6 produced identical
JSON bytes. We also passed the selected-record integrity check. We report
hosted CI separately in the PR.

We use finite arithmetic to check witnesses and proof sensitivity. The
all-dimension statement rests on the proof above. We do not claim Lean
formalization, a complete cold replay, a production precision change,
physical frame realization, runtime improvement or an unconditional
multiplication theorem.

## Task, overlap and attribution

We started at main `410026dc5513b87db92ae98571d1d5984c69a983` under priority
revision 2. [TASK.json](TASK.json) records the assignment and refined scope.
We coordinated in [Discussion #1462](https://github.com/CrocSwap/integer-mult-bounds/discussions/1462).
Our entry search covered 818 open PRs and 154 Discussion records, with complete
pagination, at 2026-10-14 00:56 UTC. The search excludes code diffs and some
nested files, so its empty exact-scope result does not establish novelty.
Our final refresh at 01:06 UTC covered 824 open PRs and 159 Discussion records
with complete pagination. We found our own claim and distinct surrounding
work; main and the recorded nearby heads remained unchanged.

We credit OpenAI's retained source, Douglas Colkitt's dependency audit, and
Philipp (@mightyOil) for the preceding synthetic-layout-independent audit.
The source authors credit Nussbaumer, Quandalle, Harvey and van der Hoeven
for the transform lineage.
Gareth Davidson's [PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282)
studies exact signed-prefix norms and excludes roundoff. His
[PR1255](https://github.com/CrocSwap/integer-mult-bounds/pull/1255) addresses chart
phases; Hanson Sun's [PR1430](https://github.com/CrocSwap/integer-mult-bounds/pull/1430)
addresses Neumann accumulation. We import no pending-PR code and claim no priority
for the classical signed-permutation or Hadamard facts.
Artus Krohn-Grimberghe's
[PR371](https://github.com/CrocSwap/integer-mult-bounds/pull/371), at
`988ef67986c313445936fc7103908b6163b9d47e`, addresses final-grid rounding in a
Gaussian block enclosure. We claim no priority for the general warning that
changing the placement of rounding can change a result.

Prepared for @jmbarrancoidener with substantial OpenAI Codex assistance in
derivation, code and prose. One exploration subagent located the source
statement and prior work. No independent human has reviewed this contribution.
New work follows Apache-2.0; we retain the original source files and licenses.

## Open next questions

A researcher proposing a nonmonomial frame can keep truncation at its original
physical location and derive a complete error bill for that implementation.
The first step is to supply the frame and complete round, then propagate its
maximum-norm bound and rounding error. This could admit a useful replacement
without exact commutation. We have no such candidate; a concrete replacement
is the blocker. [TASK.json](TASK.json) records the same bounded handoff.
