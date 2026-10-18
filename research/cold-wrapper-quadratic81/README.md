# A quadratic-phase certificate for one selected cold wrapper

**Independent finite verification; no new kappa.** For the selected #626 cold
helper 442, this package checks the exact identity

\[
T_U=L(C_4\otimes I_{32})R,
\qquad U=(268,140,45,30),\quad E=0.
\]

It occurs as recipe `0:429` in CK and `0:413` in JP8. The serialized monomials
are identical in both providers. The certificate consists of an affine support
bijection and a zero quadratic polynomial over `Z/4Z` in 13 Boolean variables.
There are **92 coefficient positions**: one constant, 13 linear and 78 quadratic.

Concurrent [PR #702](https://github.com/CrocSwap/integer-mult-bounds/pull/702),
head `27db45ac6befa99d6c06be920a93845023e81937`, checks all 14 selected cold
wrappers by direct amplitudes. It appeared during this run. This package
independently corroborates one of those identities through symbolic phase
composition and support algebra. Its code imports neither #702 nor the existing
Clifford compiler, tableau checker, or state-vector executor. The initial
all-column experiment was retired once the overlap was discovered; see
[CLAIM.md](CLAIM.md).

## Reproduce

Python 3.11+ and the standard library suffice, from the repository root:

```sh
python3 -I -B research/cold-wrapper-quadratic81/verify.py
python3 -I -O -B research/cold-wrapper-quadratic81/test_verify.py
```

Expected: `PASS_COLD_WRAPPER_QUADRATIC_CERTIFICATE 13 variables, 92 coefficient positions, 13 rejection controls`, followed by five passing tests.
`--out /tmp/cold-wrapper-quadratic.json` emits the deterministic certificate;
without `--out`, the recomputed certificate must equal `EXPECTED.json`.
All rejection checks remain active under `-O`. No source generation, compiler,
network access, solver, or Lean installation is needed.

## Operator convention and kernel

All vectors and matrix rows use little-endian bits. The source's one-bit gate is

\[
C=\frac{1+i}{2}I+\frac{1-i}{2}X.
\]

On the first four coordinates its entry from `a` to `a xor delta` is

\[
h(\delta)=2^{-4}(1+i)^{4-|\delta|}(1-i)^{|\delta|}
             =-\tfrac14 i^{-|\delta|}.
\]

A serialized monomial acts by
`M|x> = i^(phi_M + q_M(x)) |G_M x xor b_M>`, where
`q_M(x) = sum alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j (mod 4)`.
The checker validates invertibility, symmetry and the diagonal parity lifts.

The canonical completion of U is
`B = [268,140,45,30,1,2,4,8,64]` (columns of G). It is obtained here by span
membership enumeration, independently of the source's rank/elimination code.
Let `Q = I + (G^-1)^t G^-1` over F2 and let `q` be its Z4 lift using diagonal
coefficients `Q_ii`. With `K = D_q P_G`, the source convention is
`T_U = K C4 K^-1`. Consequently its support is `y xor x in span(U)` and

\[
(T_U)_{y,x}=-\tfrac14 i^{q(y)-q(x)-|c|},
\qquad (c,0,0,0,0,0)=G^{-1}(y\oplus x).
\]

This follows directly by applying `K^-1`, `C4`, then `K`; it does not use
Clifford conjugation or a claim about the zero-input column.

## Affine support certificate

Let x contain nine independent Boolean variables and delta four more. A path
through the proposed factorization is

\[
z=G_Rx\oplus b_R\oplus\operatorname{embed}(\delta),\qquad
 y=G_Lz\oplus b_L.
\]

The checker derives every output bit as an affine form and checks that the last
five coordinates of `G^-1(y xor x)` vanish identically. Its first four are

\[
c=Dx\oplus P\delta\oplus e,
\]

with little-endian row masks

- `D = [131,399,430,413]`, `e = 2`;
- `P = [4,12,5,6]`, with inverse row masks `[5,9,1,3]`.

Equivalently, for `t=P delta`,
`delta=(t2 xor t0, t3 xor t0, t0, t1 xor t0)`.
Thus each fixed x has exactly one path to each output in the canonical support.
There is no sum of multiple paths whose cancellation is being assumed.

## Quadratic phase certificate

The difference of the two path exponents is

\[
F(x,\delta)=\phi_R+q_R(x)+\phi_L+q_L(z)-|\delta|
                  -q(y)+q(x)+|c| \pmod4.
\]

For Boolean variables, an XOR has the exact lift

\[
x_1\oplus\cdots\oplus x_k
 =\sum_i x_i-2\sum_{i<j}x_ix_j\pmod4.
\]

Adding the affine constant 1 replaces this by one minus the displayed
polynomial. Higher inclusion-exclusion terms are divisible by four. Products
use `x_i^2=x_i`. Every quadratic term in a phase polynomial has an even
coefficient, so substituting affine XORs leaves degree at most two modulo four:
all cubic and quartic contributions vanish. The implementation performs the
full square-free multiplication and checks that higher-degree terms vanish.

`EXPECTED.json` preserves all six component polynomials. Their sum has **zero
coefficients at every one of the 92 possible monomials**. Combining this with
the support bijection proves equality of the finite operator entries under the
specified conventions. Linearity then extends the identity to arbitrary complex
payloads, including arbitrary values on the five spectator coordinates.

Certificate encoding: a monomial's mask selects its variables; mask 0 is the
constant. Variables 0–8 are x, and 9–12 are delta. Coefficients are residues
0–3. Affine forms use the same 13 variable bits plus bit 13 for the constant.
The certificate includes the full output forms, kernel-coordinate forms,
zero spectator forms, and inverse permutation of the four-bit delta map.

## Controls and verification boundary

Thirteen controls change either wrapper's global/linear phase or translation,
remove a wrapper, swap them, change an off-diagonal quadratic term, change the
terminal frame at fixed rank, or report the wrong width. Support failures and
phase failures are recorded separately. A nonzero phase polynomial carries a
concrete Boolean assignment where it is nonzero.

The input `Z8` control yields exactly `F=2*x8`. Its zero-input column remains
unchanged, and input 256 gives a sign error. This independently encountered
control parallels #702's `Z6` control. The existing production predicate also
checks tableaus, so this is not a reported defect in production admission.

Five test groups validate XOR lifting on all assignments for every affine form
used (and their affine complements), compare all six component polynomials
against direct phase arithmetic on all 8,192 assignments, exercise counterexample
extraction for all 276 nonzero single coefficients, replay controls, and execute
the public checker in an isolated optimized subprocess. These tests check the
symbolic implementation; the coefficient cancellation is the primary certificate.

The scope is **one finite wrapper identity**, with two source-instance bindings.
This is not a Lean proof or a formal verification of multiplication. Scalar
word correctness, tail placement, restoration of complete dirty registers,
whole-owner hosting/cost, uniform compilation, common-label/mutable-basis,
normalized residuals, precision/tape/recovery and analytic transfer remain the
selected construction's inherited obligations. The certificate adds no new
paid program, supplier saving or kappa. No search or optimality claim is made.

## Pins, attribution and validation

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
`SOURCES.json` pins the archived CK/JP8 words and recipes, selected record,
original wrapper and Clifford definitions, and existing literal Lean source.
`INSTANCE.json` is bound back to the full archived recipes and helper labels.
The OS-random seed is 81; `81 % 14 = 11` selected the lexicographic cold-recipe
index. The accepted conditional kappa at this base is
`51110230636731/31250000000000000`; it is context, not a new result here.

Credit: Chafik Boukhalfa (#626 and Clifford/wrapper lineage), Jeremy Kothe
(#622/#623 and #617), DreamingOfClouds (cold ends and wrapper adaptation),
icekylinx (native supplier lineage), Douglas Colkitt (selected review/replay),
and all predecessor notices retained in the source packages. PR #702's broader
independent amplitude audit by BigCactusLabs is credited above. PR #662's
performance adapter and PR #581's rank-one Lean identity are related distinct
contributions and are not implementation dependencies.

Joshua Snider (`jsnider3`) with substantial OpenAI Codex assistance. Apache-2.0;
no independent human peer review is claimed. Local validation and submission
status are recorded in the sprint claim's final result.
