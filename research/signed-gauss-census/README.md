# Exact signed quadratic Gauss census

Independent finite verification of the general binary residual normal form in
[`notes/endpoint-gauge-complex.tex`](../../notes/endpoint-gauge-complex.tex),
first subsection. **No new kappa and no defect found in the tested identity.**

The historical [endpoint tests](../../tests/test_endpoint_gauge.py) exercise
four embedded bases. This package checks every symmetric binary polarization
matrix and every normalized Z4 quadratic refinement in dimensions **0 through
4**, including nonalternating forms, all diagonal sign choices, and singular
boundaries. It imports no predecessor code and uses Gaussian integers
represented by pairs of Python integers: no floating-point or complex-number
arithmetic, numerical tolerance, third-party package, or downloaded toolchain.

## Reproduce

From the repository root, using Python 3.10+ and its standard library:

```sh
python3 -I -B research/signed-gauss-census/verify.py
python3 -I -O -B research/signed-gauss-census/verify.py
python3 -I -B research/signed-gauss-census/test_verify.py -v
python3 -I -O -B research/signed-gauss-census/test_verify.py -v
```

Both checker modes must print:

```text
PASS_SIGNED_GAUSS_CENSUS refinements=16933 nonsingular_refinements=7411 singular_refinements=9522 kernel_entries=1849609 sampled=24 controls=11 pins=2
```

The test module runs six tests, including a fresh optimized replay in a minimal
relocated tree whose path contains spaces. `--output /new/path.json` writes a
checked receipt exclusively after source and arithmetic validation; an existing
file is never overwritten. Normal and optimized receipts have identical bytes.
`EXPECTED.json` records rank counts, fourth-root phases, coverage, controls, and
the larger cases' input digests. It is compared with type-sensitive canonical
JSON, so `true` cannot replace the integer `1`.

## Proposition and exact checks

Let `B` be a symmetric binary `r` by `r` matrix. For each binary vector `l`, set

```text
q(x) = sum_i (B_ii + 2 l_i) x_i + 2 sum_(i<j) B_ij x_i x_j  (mod 4).
W(s) = sum_z i^q(z) (-1)^(s dot z).
```

These are exactly the refinements with `q(0)=0` and polarization
`q(x+y)-q(x)-q(y) = 2 x^T B y (mod 4)`: values on basis vectors determine
the diagonal lifts, and repeated polarization determines every remaining
value. Each coefficient choice is distinct. Thus the declared enumeration has
`2^(r(r+3)/2)` refinements, not a sample of presentations.

For invertible `B`, the source statement, with `G=B^-1`, is

```text
W(x+y) = W(0) i^(-q(Gx)) (-1)^(x^T G y) i^(-q(Gy)).
W(0) ((1-i)/2)^r is in {1, i, -1, -i}.
```

The common kernel denominator `2^r` cancels in the first check. The second
check multiplies by `(1-i)^r` and compares against four integer pairs scaled
by `2^r`. Every `x,y` is checked. Zero dimension is included.

The weakest essential assumption here is nondegeneracy. For singular `B`, let
`R=ker B`. A direct character sum gives

```text
|W(s)|^2 = 2^r |R|  if q(u) = 2 s dot u (mod 4) for every u in R,
           0        otherwise.
```

Indeed, substituting `z=w+u` in `W(s) conjugate(W(s))` cancels the sum over `w`
unless `Bu=0`. On the radical, `q/2` is a binary linear functional, so its
remaining character sum is either `|R|` or zero. Its affine support has
`2^rank(B)` elements. The checker verifies this support and every squared
magnitude for every singular case. A singular form therefore cannot be
silently treated as a flat full-rank Walsh child. This is a boundary of this
normalization, not an obstruction to other kernels or constructions.

The complete-square argument and block classification establishing the
nonsingular identity in arbitrary dimension already appear in the credited
source. This package supplies implementation evidence, not a new proof of
that theorem. The derivation above explains the separately checked singular
boundary; it is ordinary mathematics, not a machine-checked formal proof.

## Coverage and independence

| Dimension | Refinements | Nonsingular | Singular | Full kernel entries |
| --- | ---: | ---: | ---: | ---: |
| 0 | 1 | 1 | 0 | 1 |
| 1 | 4 | 2 | 2 | 8 |
| 2 | 32 | 16 | 16 | 256 |
| 3 | 512 | 224 | 288 | 14,336 |
| 4 | 16,384 | 7,168 | 9,216 | 1,835,008 |
| Total | 16,933 | 7,411 | 9,522 | 1,849,609 |

For every form, a Walsh butterfly is compared with a separate direct sum
that counts the four phases. The exhaustive domain uses **4,227,601 direct
sum terms** and the same number of polarization comparisons. The inverse
matrix is obtained by enumerating its map on vectors, without elimination.

The six tests add two independent coverage checks: all possible normalized
Z4 truth tables through dimension three are filtered by the definition of
bilinear polarization; all binary matrices through dimension four are
filtered by symmetry and classified by a separate XOR row elimination.
Both recover exactly the declared census. All 34 signed Hamming realizations
of the four historical source fixtures are also checked against the general
coefficient representation.

The OS-random seed **`d207afb6a1a4565a4812f3e58a38ad45`** generates eight
additional symmetric forms at each of dimensions 5, 6, and 9 using SHAKE256.
These 24 cases contain seven nonsingular forms (535,552 further kernel
entries) and seventeen singular forms. They are explicitly samples, not
exhaustive larger-dimensional coverage. The seed does not filter the complete
0–4 census. This sprint selected the restricted 75–84 verification track;
it did not use the original uniform 00–99 track lottery.

Eleven mathematical controls reject an omitted Gauss factor, a wrong global
fourth-root phase, `B` substituted for `B^-1`, conjugated endpoint phases, a
missing bilinear phase, a discarded signed refinement, missing Walsh stages,
singular full-rank normalization, a nonzero constant, wrong polarization, and
a nonsymmetric matrix. Tests also reject malformed/noninteger presentations,
detect proof-source drift, and preserve output on failure.

## Sources, overlap, and limits

Exact baseline: **`2921874911956718fcaaaf9396fe8267b3cfa9f0`**.
`SOURCES.json` records SHA256 and Git blob identities for the proposition and
historical tests, which are checked at runtime. Its separate `context_at_base`
inventory records the related census description and selected-result context;
these are historical references, not executable inputs or moving-main checks.
No historical source or certificate is modified.
The selected conditional frontier at this base remains PR942 at
`1661960547713947/10^18`. Its full cold replay is `make frontier942-verify`.

Publication recheck against main
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6` on 2026-10-14 found both
mathematical source files unchanged. At that checkpoint, the selected
conditional result is PR1094 on PR1087 at `0.001672660197076918`, with
review `docs/research/community-batch1099-review.md` and cold replay
`make frontier1094-verify`. This census does not validate that construction;
the original base and historical context pins above are preserved.

[PR831](https://github.com/CrocSwap/integer-mult-bounds/pull/831), Maximooch,
head `66c3bc5c2eb5a2c066b1119310b29d26350e1dde`, already checks 452 nonsingular
alternating refinements in dimensions 2 and 4 as part of an F4 interface
audit. That subset is deliberately corroborated here; no priority is claimed
for it. This package adds **6,958 nonalternating refinements**, the zero case,
the **9,522 singular boundaries**, independent completeness checks, and a
different butterfly/counting comparison. It does not reproduce the F4
Hermitian census or import pending PR831 code.

[PR911](https://github.com/CrocSwap/integer-mult-bounds/pull/911), ToikY,
checks embedded subspaces, orthonormal residuals, and signed Hamming phases.
This package instead checks the general quadratic normal form, which also
admits nonzero alternating residuals. Neither result replaces the other.
[PR24](https://github.com/CrocSwap/integer-mult-bounds/pull/24), icekylinx,
supplies the endpoint normal form and its construction context. Credit also
Douglas Colkitt's maintained tests, the original OpenAI manuscript, and the
predecessor contributors retained in the repository's notices.

No current supplier word, physical frame schedule, owner assignment, costs,
all-size compiler, precision/tape implementation, or analytic transfer is
admitted by this census. There is no full multiplication theorem, Lean build,
speedup claim, or new kappa. Full `make verify`, a cold construction replay,
and hosted CI are outside this isolated mathematical-test contribution.

## Open next questions

Can the arbitrary-dimension radical support criterion and nonsingular Gauss
normal form be checked in a proof assistant with an explicit correspondence
to the credited source statement? This would address the dimension limit of
the finite evidence here. A feasible first step is to formalize the
translation identity for `W(s)` along a radical vector and derive the support
condition `q(u) = 2 s dot u (mod 4)` for every radical vector `u`. Then prove
the squared-magnitude formula before treating the nonsingular phase factor.
The blockers are a checked source-to-statement translation and suitable
finite-field and Gaussian-number library support; no formalization has been
attempted in this package. This would formalize existing mathematics, not
establish a new supplier or multiplication theorem.

Prepared for **yssite** with substantial **OpenAI Codex assistance** in research,
implementation, verification, and writing. No independent human review is
claimed. New material is **Apache-2.0** under the repository license; all
predecessor attribution is retained.
