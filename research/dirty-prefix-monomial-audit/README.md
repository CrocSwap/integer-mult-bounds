# Sharp coefficient growth in the balanced dirty commutator

**Research audit; no new kappa.** The unchanged PR628 balanced word has a
sharp coefficient row bound of `ceil(log2 n)+2` at every ideal leaf boundary,
for prefixes and inverse prefixes in either direction. This improves
PR905's sufficient bound `2*3^ceil(log2 n)`.

The new invariant is stronger: each matrix entry is zero or a single signed
ordered monomial. [PROOF.md](PROOF.md) gives an induction through every
recursive phase and an attaining identity-factor family. The mathematical
statement covers every positive factor count. Finite replays support the
proof; they are not formal verification or independent human peer review.

Substitution into PR905's existing sufficient precision formula reduces its
radix-64 example from **1,162,553 to 1,162,523 fractional bits**, with
target precision 128 and initial magnitude at most `2^20`. It preserves the
4,000 leaf calls and six borrowed arrays. This is a comparison of conservative
proof budgets, not a runtime improvement. The asymptotic cubic guard and
selected multiplication exponent are unchanged.

## Reproduce

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 -I -O -B research/dirty-prefix-monomial-audit/verify.py
python3 -I -O -B research/dirty-prefix-monomial-audit/test_package.py
```

The first command checks source pins and the complete deterministic receipt
without writing artifacts. Expected output:

```text
PASS_DIRTY_PREFIX_MONOMIAL traces=168 boundaries=1184622 budgets=1242 controls=10 kappa=unchanged
```

The second command runs eight package tests, including a read-only relocated
replay using only declared dependencies and rejection of a changed receipt.

The exact evidence comprises 168 signed traces at 84 factor counts through
257; every prefix and inverse prefix; literal comparisons with the pinned
dispatcher; 32 abstract induction cases; 430 dense noncommuting matrix
boundaries with 44 independent Gauss-Jordan prefix inversions; 1,242 exact
precision comparisons; and ten mathematical controls. The frozen domain,
OS assignment seed **72**, stopping rule, and three candidate tasks are in
[DOMAIN.json](DOMAIN.json). In particular, this is additional invariant
coverage rather than an extension of PR905's existing search domain.

## Pins, scope, and credit

Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
[SOURCES.json](SOURCES.json) pins every consumed source by SHA256 and Git blob,
with predecessor heads and original locations. [VALIDATION.json](VALIDATION.json)
records the executed checks and their limits.

Credit Chafik Boukhalfa for PR628's dispatcher and PR905's ordered-prefix
lemma and cubic analysis; Gareth Davidson for PR877's prefix/perturbation
method; PR862 for the common-isometry subset bound; and 0xkilgore's PR663
for the exact leaf count. Their source notices remain intact. PR896 covers
nonlinear restoration. Concurrent PR1057 changes dirty-register allocation
under an exact-additive interface; this result keeps PR628's reserved-depth
allocation. No code from PR896 or PR1057 is consumed.

The operator and precision consequences inherit the common immutable
isometry, distinct mutable arrays, deterministic inverse, leaf error,
coefficient preparation, and phase-access assumptions. Internal leaf
growth, integer guards, restoration, routing and all paid costs remain
charged. No rounded kernel, physical compiler, full transform or multiplication
reduction is newly implemented or audited here. The selected construction
and `upstream/` are unchanged. No literature-priority claim is made.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in derivation, coding, verification and writing. New material
is Apache-2.0, under the repository license.
