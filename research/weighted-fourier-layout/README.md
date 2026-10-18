# Exact convolution boundary for phase-weighted Fourier layouts

**Mathematical audit / scoped interface theorem; no new kappa.** A shared
phase-weighted Fourier routine cannot preserve the retained convolution
identity merely by conjugating that routine for the final pass, unless
**every phase is 1** and its read permutation is a self-adjoint group
automorphism. Phases cannot repair a translated or non-self-adjoint shared
layout under this contract.

With separately chosen forward and inverse weights, affine layouts do work.
The theorem below gives all of them, including the exact character factors
and the necessary agreement of the two forward address maps. It extends
[Ross Richardson's PR #940](https://github.com/CrocSwap/integer-mult-bounds/pull/940)
from unweighted permutations to three monomial maps. The unweighted result
and Fourier duality are predecessor work, not new claims here.

The source's stated coordinate multipliers satisfy the criterion. There is
no counterexample to its actual lemma and no change to the selected result.
This supplies an admission boundary for proposed phase/address changes;
it does not price or implement physical routing.

## Exact statement

Let `G = product_i Z/q_i`, `q_i >= 2`, `N = |G|`, with pairing

\[
\chi(x,y)=\exp\left(2\pi i\sum_i x_i y_i/q_i\right).
\]

Both Fourier signs are normalized by `1/N`:

\[
(F^\pm u)(x)=\frac1N\sum_y\chi(x,y)^{\pm1}u(y).
\]

Use **read** permutations `(P_pi f)(y)=f(pi(y))`, and diagonal maps
`(D_alpha f)(y)=alpha(y)f(y)`. The weights `alpha`, `beta`, `omega`
are arbitrary complex functions of modulus one, not necessarily roots of
unity or characters. Let `pi`, `sigma`, `rho` be permutations of `G`.
Convolution `*` is unnormalized. We ask when, for every `u,v in C^G`,

\[
D_\omega P_\rho F^+
 \left[(D_\alpha P_\pi F^-u)\cdot(D_\beta P_\sigma F^-v)\right]
 =\frac{u*v}{N^2}.                                      \tag{1}
\]

**Theorem.** (1) holds if and only if there are a group automorphism `L`,
offsets `a,b in G`, and a unit complex scalar `gamma` such that

\[
\begin{aligned}
\sigma(y)=\pi(y)&=L(y)+b, &\rho(x)&=L^\dagger(x)+a,\\
\alpha(y)\beta(y)&=\gamma\chi(-a,y),
 &\omega(x)&=\gamma^{-1}\chi(x,b).                       \tag{2}
\end{aligned}
\]

Here the adjoint uses the actual product-group pairing:
`chi(L^dagger(x),y)=chi(x,L(y))`. On unequal cyclic factors it is generally
not an ordinary matrix transpose. The forward weights can split their
specified product arbitrarily: every unit function `h` gives the same
result after `alpha -> h alpha`, `beta -> h^-1 beta`.

### Proof

Write `f=F^-u`, `g=F^-v`. They range independently over all complex
functions because `F^-` is invertible. The normalized convolution rule is
`F^+(f · g)=(u*v)/N^2`, with a pointwise product inside the transform.
The coefficient of `f(pi(y))g(sigma(y))` in output coordinate `x` on the
left of (1) is

\[
N^{-1}\omega(x)\alpha(y)\beta(y)\chi(\rho(x),y),         \tag{3}
\]

which is nonzero. If `pi(y) != sigma(y)`, the right side has zero coefficient
for this off-diagonal monomial. No other `y` can cancel it because `pi`
is injective. Consequently `sigma=pi` is necessary.

Put `q(y)=alpha(y)beta(y)`. Comparing the remaining diagonal coefficients
after writing their common address as `pi(y)` gives precisely

\[
\omega(x)q(y)\chi(\rho(x),y)=\chi(x,\pi(y))
\quad\hbox{for every }x,y.                              \tag{4}
\]

Let `b=pi(0)`, `a=rho(0)`, `gamma=q(0)`. First set `y=0` in (4), then
`x=0`. These force

\[
\omega(x)=\gamma^{-1}\chi(x,b),\qquad
q(y)=\gamma\chi(-a,y).
\]

After cancellation, (4) becomes

\[
\chi(\rho(x)-a,y)=\chi(x,\pi(y)-b).                     \tag{5}
\]

Define `L(y)=pi(y)-b`. Multiplicativity of the left side in `y` implies
`chi(x,L(y+z)-L(y)-L(z))=1` for all `x`. Nondegeneracy forces additivity.
Since `pi` is bijective, `L` is an automorphism. Equation (5) then forces
`rho(x)-a=L^dagger(x)`. The adjoint exists uniquely because every character
of the product group is `chi(w,.)` for a unique `w`; composition with an
automorphism permutes these characters. This also makes the adjoint an
automorphism. This proves necessity. Substituting (2) into (4), then
reversing the coefficient calculation, proves sufficiency.

### Shared routine and conjugate inverse

Suppose both forward passes use `A=D_w P_pi F^-`, and the final routine
is obtained by conjugating input and output: `bar(A)=D_conj(w) P_pi F^+`.
In (4), set `alpha=beta=w`, `omega=conj(w)`, `rho=pi`, and then `y=x`.
Symmetry of the pairing cancels the character factors and leaves
`conj(w(x))*w(x)^2=1`. Since `|w(x)|=1`, **`w(x)=1` at every address**.
The theorem now gives `a=b=0` and `L=L^dagger`, exactly PR940's unweighted
criterion. Conversely those conditions suffice.

A minimal failure is `G=Z/4`, `pi=id`, `w=i`, `u=v=delta_0`: the output
is `i delta_0/16`, whereas (1) requires `delta_0/16`. Even a global phase
does not cancel across these three passes. The receipt records numerators
`4i` and `4` over their common denominator `64`.

The asymmetric contract has a simple positive contrast. On `Z/4`, set
`pi(y)=sigma(y)=y+1`, `rho(x)=x+1`, `alpha(y)=1`, `beta(y)=i^-y`,
`omega(x)=i^x`. Equation (4) holds exactly. All sixteen input basis pairs
are checked in the tests. Thus the negative corollary does not prohibit
affine layouts with the correct separate phases.

## Source and scope

- Base: `410026dc5513b87db92ae98571d1d5984c69a983`.
- Audited source: [07-resampling.tex](../../upstream/build/sections/07-resampling.tex),
  `lem:chirp-permutation`, specifically `eq:source-permutation-cancel`;
  original `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
- Predecessor: Ross Richardson's PR940 at
  `fccac36fa9bcc063c4fda733299a22349ce10e56`. Its proof was inspected;
  no pending code is imported or needed for replay.
- The selected record at the base is PR1094's conditional
  `836330098538459/500000000000000000`, with complex supplier binding.
  The selected review, source manifest, actual T16 package and assembly
  were followed. `research_baseline.py` passed source bindings only.
- [SOURCES.json](SOURCES.json) pins live source bytes and historical
  selection/task provenance separately. [TASK.json](TASK.json) records
  OS seed **71**, three candidates, scope, stopping rule, credit and the
  [coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1463).

The theorem is exact complex algebra. It supplies no rounded Gaussian
implementation, tape schedule, saved operation, paid recurrence, supplier
adoption, improved kappa, or full multiplication proof. Arbitrary phase
weights preserve coordinate magnitudes, but their calculation and application
are not free. Both read permutations and both required character factors
must be included in any proposed implementation's cost and error budget.
The all-size/compiler, hosting, precision/tape and analytic obligations of
the selected construction remain inherited.

## Reproduce and inspect the evidence

From the repository root, using Python 3.12 and only the standard library:

```sh
python3.12 scripts/research_package.py --package research/weighted-fourier-layout
```

Expected: `PASS_WEIGHTED_FOURIER_LAYOUT`, eleven passing test groups, and
`PASS_REGISTERED_RESEARCH_PACKAGE research/weighted-fourier-layout outcome=completed`.
The direct checker also works in an offline source export with this package
and its two pinned upstream inputs:

```sh
python3 -I -O -B research/weighted-fourier-layout/verify.py
python3 -I -O -B research/weighted-fourier-layout/test_verify.py
```

The registered metadata check additionally requires Git history to resolve
historical provenance. The direct checker compares the complete regenerated
receipt to [EXPECTED.json](EXPECTED.json). `--write /path/to/new.json`
instead creates a fresh receipt and refuses overwrite. It performs the
mathematical checks but does not compare to the committed expected receipt.

For the finite census let `M=lcm(4,q_1,...,q_d)` and restrict weights to
`M`th roots of unity. For every pair `pi,rho` and every product phase vector
`q`, the `y=0` coefficient of (4) forces a unique `omega`. This is the
explicit reduction used for the following complete finite domain; arbitrary
complex weights are covered by the written proof, not a finite search.

| Group | M | Reduced candidates | Accepted | Shared-routine candidates | Accepted |
|---|---:|---:|---:|---:|---:|
| Z/2 | 4 | 64 | 16 | 32 | 1 |
| Z/3 | 12 | 62,208 | 216 | 10,368 | 2 |
| Z/4 | 4 | 147,456 | 128 | 6,144 | 2 |
| (Z/2)^2 | 4 | 147,456 | 384 | 6,144 | 4 |
| Total | | **357,184** | **744** | **22,688** | **9** |

Two classifications agree everywhere: literal scaled-integer character
coefficients, and affine reconstruction from generator images with rational
turns and a weighted adjoint. Digests bind the ordered classification streams.
An independent [oracle.py](oracle.py) evaluates both forward transforms,
the product, the final transform, and direct convolution in exact cyclotomic
rings. It does not call either admission classifier. It checks:

- All input basis pairs for the 744 accepted reduced cases, choosing a
  deterministic split of each product phase, plus five larger/unequal-factor
  fixtures: **10,662 basis pairs**, and five dense integer pairs in total.
- All **1,136 unequal forward-permutation pairs** in the census domain,
  using explicit character inputs with zero desired convolution and nonzero
  computed output. The written nonzero-coefficient argument handles arbitrary
  phases and inverse maps; these finite witnesses use fixed deterministic ones.
- **Nine semantic counterexamples**: constant/shared character phases,
  phase-compensated shared translation, wrong inverse character sign,
  forward linear map in place of its adjoint, an uncompensated operand phase, different forward
  addresses, the wrong inverse Fourier sign, and a missing normalization.

[test_verify.py](test_verify.py) additionally checks all **32,768 unreduced
two-point cases** (all three permutations and all three independent phase
vectors) against literal convolution; exactly **256** pass. It checks all
256 reciprocal phase vectors on Z/4, the translated positive example,
exact root fields and normalization, wrong classifiers in both directions,
nonbijective inputs, source relocation/drift/missing files and overwrite
rejection. This validates the finite reduction with an unreduced domain.
Assertions are not used for acceptance, so checks remain active under `-O`.

The fixed domain is exhausted; this is not a heuristic search. The written
universal argument and its finite checks are separate. Neither has been
verified by a proof assistant or an independent human reviewer. No numerical
FFT, full supplier cold replay or benchmark is claimed.

Local validation passed on macOS arm64: the registered Python 3.12.13 replay
and all eleven tests, optimized isolated Python 3.14.2 execution, and an
offline export without Git in a path containing spaces. Deliberately changed
source bytes and a false expected certificate were both rejected. The selected
record check passed. On refreshed main
`e6f9716621f4e01fc190617934cdfaf072bd976f`, both live source inputs and the
selected kappa were unchanged. The final overlap snapshot covered 829 open
PRs and all paginated discussion records, with no retrieval warnings; its
coverage limits and the credited PR940 overlap are retained in TASK.json.
Hosted CI is separate from these local results.

## Open next questions

Can an existing physical Fourier schedule absorb a permitted affine shift
and its two character factors without additional paid work? This could make
the algebraic admission result useful to a recursive boundary change. A
bounded next step is to choose one actual source schedule and one nonzero
offset, realize both read maps and both character factors, and price the
complete forward/product/inverse wrapper. No such candidate schedule or
interface is constructed here; that is the present blocker. The structured
question is also in [TASK.json](TASK.json).

## Credit

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in mathematics, implementation, verification and prose.
Credit **Ross Richardson** for PR940's unweighted criterion and proof,
**OpenAI** for the original manuscript, and **Douglas Colkitt / CrocSwap**
for the retained construction and normalization audit. No literature-priority
claim is made for elementary character or monomial-map algebra.
New material is Apache-2.0. Original source files and licenses are unchanged.
