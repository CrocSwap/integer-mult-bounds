# Exact scope of retained source-permutation cancellation

**Mathematical audit / scoped negative result; no new κ and no defect in the
stated source lemma.** The retained convolution identity is valid for the
source's coordinate multipliers. Extending it to a shared arbitrary layout,
or even to an arbitrary group automorphism, is not valid when the inverse
pass is obtained just by conjugating the same forward routine.

This note gives the precise condition, a short all-group argument, and exact
finite evidence. For the usual character pairing on a product of cyclic
groups, the same permutation works on the forward and conjugate passes
**if and only if it is a self-adjoint group automorphism**. An arbitrary
automorphism works with its *adjoint* on the conjugate pass. The adjoint is
generally different from both the original permutation and its inverse.

The concrete contribution is an explicit admission criterion and failure
witnesses for this retained-layout interface, not a claim of novelty for
Fourier duality. A shared layout still commutes with pointwise products;
that fact alone does not establish the complete convolution identity.

## Source and reproducibility

- Repository base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
- Mathematical source: OpenAI's `openai/math` at
  `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, retained at
  [`upstream/build/sections/07-resampling.tex`](../../upstream/build/sections/07-resampling.tex),
  `lem:chirp-permutation`, specifically `eq:source-permutation-cancel`.
- The read convention is `(R_c z)_j = z_(c j)`, not the push convention.
- [SOURCE.json](SOURCE.json) pins the actual source bytes and original
  manifest as required inputs. The prior audit and accepted-result hashes
  are historical context, not dependencies or gates on later frontiers.
  No pending PR code is imported.
- The selected conditional value at this base was
  `κ = 1661634653669567 / 10^18 = 0.001661634653669567`, from #799 with #589.
  Before submission, main advanced to
  `47481c89fd30a43f8f882eb4b391e89c29273fd0`, selecting #890 at
  `κ = 0.001661957774647029`. The audited source and its manifest are
  byte-identical there. This package changes neither selected construction.

From the repository root, with Python 3.10 or later and no third-party packages:

```sh
python3 -B -I -O research/source-permutation-audit/verify.py
```

Expected result:

```text
PASS_SOURCE_PERMUTATION: 127616 permutations; 2960 census basis pairs; 205 dense adjoint pairs; 8 exact counterexamples; 1 admission rejection; 4 positive controls
```

The command checks source SHA-256 pins, recomputes the whole bounded domain
and compares every field with [EXPECTED.json](EXPECTED.json). No floating
point, transform library or supplier code is used. To write a fresh receipt
without overwriting the committed one, use `--write /tmp/permutation-replay.json`.

## Statement and proof

Let `G = ∏_i Z/q_i`, `N = |G|`, and use the symmetric, nondegenerate pairing

\[
\chi(x,y)=\exp\left(2\pi i\sum_i x_i y_i/q_i\right).
\]

Write `F−` and `F+` for the negative- and positive-sign Fourier transforms,
each normalized by `1/N`. For a permutation `π` of `G`, define the read map
`(P_π f)(x) = f(π(x))`. Convolution here is the **unnormalized** group
convolution. For two permutations `π, ρ`, consider the identity

\[
(P_\rho F^+)\left[(P_\pi F^-u)\cdot(P_\pi F^-v)\right]
=\frac{u*v}{N^2} \qquad\text{for all }u,v\in\mathbb C^G. \tag{1}
\]

**Claim.** (1) holds exactly when `π` is a group automorphism and
`ρ = π†`, where the adjoint is defined by

\[
\chi(\pi^\dagger x,y)=\chi(x,\pi y). \tag{2}
\]

In particular, setting `ρ = π` is allowed exactly for self-adjoint
automorphisms.

**Reduction to one operator.** Every permutation commutes with pointwise
multiplication, and normalized Fourier inversion gives

\[
F^+[(F^-u)\cdot(F^-v)]=(u*v)/N^2.
\]

The products `(F−u)·(F−v)` span all of `C^G`: fix `u = δ_0`, whose
transform is the nonzero constant `1/N`, and vary `v`, using invertibility
of `F−`. Thus (1) is equivalent to

\[
P_\rho F^+P_\pi=F^+. \tag{3}
\]

The coefficient at row `x`, column `z` on the left of (3) is
`χ(ρ(x), π⁻¹(z))/N`. Substitute `z = π(y)`. Equality of all entries is
therefore exactly

\[
\chi(\rho(x),y)=\chi(x,\pi(y))\quad\text{for every }x,y. \tag{4}
\]

**Necessity.** Set `y = 0` in (4). Nondegeneracy gives `π(0) = 0`.
For any `y,z`, multiplicativity of the left side in its second argument
implies

\[
\chi(x,\pi(y+z))=\chi(x,\pi(y)+\pi(z))\quad\text{for every }x.
\]

Nondegeneracy gives `π(y+z) = π(y)+π(z)`. A bijective homomorphism is an
automorphism. For such `π`, (4) determines `ρ(x)` uniquely, namely (2).
Existence follows because every character on the product group is
`χ(w, ·)` for a unique `w`; composition with `π` preserves characters.
The adjoint is itself an automorphism, since composition with a bijection
permutes characters. This also proves there is no output permutation `ρ`
of this form that repairs a nonadditive `π`.

**Sufficiency.** For an automorphism and its adjoint, (4) holds by
definition. Reversing the entry calculation proves (3), hence (1).

For unequal cyclic factors, ordinary integer matrix symmetry is not the
criterion. If `a_i = π(e_i)` are the generator images, self-adjointness is

\[
\frac{(a_i)_j}{q_j}=\frac{(a_j)_i}{q_i}\pmod 1.
\]

Both representatives lie in `[0,1)`, so the checker compares the exact
integer cross-products `(a_i)_j q_i = (a_j)_i q_j`. It separately checks
the generator orders and reconstructs the image of every group element.

**Why the retained source is valid.** Its `R` has
`π(x)_i = t_i x_i mod s_i`, with `gcd(t_i,s_i)=1`. This is a diagonal
automorphism and
`Σ_i (t_i x_i)y_i/s_i = Σ_i x_i(t_i y_i)/s_i`. It is self-adjoint, even
when it is not involutive. This argument applies to all the stated source
moduli; the finite census is not needed for the universal implication.

**Different inverse-layout contract.** For *any* permutation `π`, including
nonadditive layouts, the inverse routine `F+ P_π⁻¹` always undoes the layout
before the inverse transform. The theorem above concerns replacing this
routine with `P_ρ F+`. These operators coincide precisely in the case
just proved. In particular, this audit does not challenge a physical
schedule that explicitly implements the matching inverse layout.

## Exact experiment and controls

Assignment seed **68** selected the audit track and the third of three
narrow candidates. [CLAIM.json](CLAIM.json) records the alternatives,
overlap check, base, method, scope and stopping rule. The complete domain
is all permutations of the eleven group presentations below. It includes
isomorphic groups with different product presentations deliberately.

| Cyclic factors | Permutations | Automorphisms | Same-layout admissible |
|---|---:|---:|---:|
| 2 | 2 | 1 | 1 |
| 3 | 6 | 2 | 2 |
| 4 | 24 | 2 | 2 |
| 5 | 120 | 4 | 4 |
| 6 | 720 | 2 | 2 |
| 7 | 5,040 | 6 | 6 |
| 8 | 40,320 | 4 | 4 |
| 2, 2 | 24 | 6 | 4 |
| 2, 3 | 720 | 2 | 2 |
| 2, 4 | 40,320 | 8 | 4 |
| 2, 2, 2 | 40,320 | 168 | 28 |

For every permutation, two algebraically different calculations agree:
the literal entries of `P_π F+ P_π` match `F+` exactly when reconstruction
from generator images gives a self-adjoint automorphism. Every rejected
permutation has a differing character-matrix entry; its two root powers
are also checked to remain distinct in the exact cyclotomic ring. A digest
binds the entire classification stream for each presentation.

A separate direct Fourier/convolution implementation executes all 2,960
ordered basis pairs for accepted layouts, and one seed-68 dense integer
input pair for each of the 205 automorphisms with its computed adjoint.
It constructs polynomial values in `Z[ζ_L] = Z[z]/Φ_L(z)` and carries the
three transform normalizations as the common denominator `N^3`. It does
not call the character-table test or structural classification to decide
whether the resulting convolution is correct. Integer inputs suffice for
these exact algebraic tests; no disk-grid numerical routine is executed.

The source's multiplier family additionally passes all 1,425 unit choices
on cyclic moduli `2 ≤ q ≤ 68`. Four positive controls add 186 direct basis
pairs, including unequal moduli and an automorphism with a distinct adjoint.
These are algebraic test parameters, not a claim that each tuple meets the
Gaussian resampling feasibility conditions.

The receipt includes eight actual differing convolution coefficients:

1. A translation on `Z/3` does not cancel.
2. Bit reversal `(0,2,1,3)` on `Z/4` is zero-fixing and involutive but
   nonadditive. With `u=δ_0, v=δ_1`, output coordinate 1 is
   `(2−2i)/64`, whereas the required coefficient is `4/64`.
3. The involutive shear `(x,y) ↦ (x+y,y)` on `(Z/2)^2` is an automorphism
   but is not self-adjoint.
4. On `(Z/3)^2`, using that shear's inverse in place of its adjoint fails.
5. On `Z/5`, incorrectly inverting the valid source multiplier `c=2` fails.
6. Omitting conjugation of the Fourier sign fails.
7. Normalizing the convolution by `N` rather than `N^2` fails.
8. Normalizing it by `N^3` rather than `N^2` fails.

A ninth, separate **admission** control rejects multiplication by 2 modulo
6 because it is not a permutation. It is not counted as a convolution
counterexample. The positive controls show that involutivity is unnecessary,
weighted adjoints matter, and replacing the non-self-adjoint shear by its
correct adjoint on the conjugate pass repairs every tested basis pair.

Enumeration stops after the fixed domain is exhausted; there is no timeout
or incomplete search. The bounded census is finite evidence. The written
character argument proves the general criterion; it has not been checked
by a proof assistant or an independent human reviewer.

## Verification of this package

The main receipt agrees on macOS arm64 with CPython 3.14.6 and 3.12.12,
including optimized isolated execution. The supplementary command is

```sh
python3 -B -I -O research/source-permutation-audit/test_verify.py
```

Its seven passing tests include five deliberately faulty implementations:
wrong permutation direction, admitting every automorphism, unweighted
symmetry, wrong normalization, and a missing Fourier sign. They also check
source relocation/corruption and known cyclotomic polynomials with exact
character orthogonality. All failure checks remain active under `-O`.

The main command also passed from an isolated, relocated source closure
whose path contains spaces; a corrupted expected receipt was rejected.
The four existing `test_finite_identities.py` tests and
`make selected-record-check` passed at the exact base. Full `make verify`,
supplier cold replay, proof-assistant checking and remote CI are not claimed:
no existing supplier or generator is changed. The result is a separately
checkable research package confined to this directory.

## Dependencies, limitations and credit

This is a restriction on one exact algebraic interface. It does not charge
or eliminate a physical permutation, construct a fixed-tape implementation,
or certify the numerical Gaussian routines. All inherited compilation,
mutable-source/common-label, hosting, precision, tape and analytic
assumptions of the selected result remain. There is no new cost recurrence
or κ claim, and no counterexample to the source's actual hypotheses.

Credit OpenAI for the original manuscript and Douglas Colkitt / CrocSwap
for the retained dependency and normalization audit. Related concurrent
work is explicitly separate: Chafik Boukhalfa's [#479](https://github.com/CrocSwap/integer-mult-bounds/pull/479)
audits exact streamed chirp phases; Philipp / mightyOil's
[#879](https://github.com/CrocSwap/integer-mult-bounds/pull/879) checks physical
transform schedules and their matching inverse layouts. Their exact
inspected heads are recorded in SOURCE.json. Neither contribution is
replayed, imported or contradicted here. The already-covered packed-bit
and signed-extraction candidates were not reopened.

Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance** in task selection, mathematics, implementation,
verification and writing. New material is Apache-2.0 under the repository
license. No original source or license is changed. No priority claim for
the elementary Fourier-adjoint characterization is intended.
