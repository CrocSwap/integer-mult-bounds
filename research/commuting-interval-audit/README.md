# Commuting factors: a linear subset-budget interval bound

**Research audit / all-size lemma. No new kappa.**

PR1244 leaves open whether shared deeper scratch permits a bound linear in
the subset norm budget for commuting factors. This package supplies a
six-case induction for the unchanged PR628 balanced dirty word.
For every factor count n >= 1, every pair of leaf-boundary cuts, and both
word signs, each surviving free-algebra monomial uses every factor index
at most once. The theorem retains the actual reuse of deeper scratch.
It does not require the factors themselves to be invertible.

If the factors commute and every subset product has norm at most G >= 1,
then every interval has norm at most `C^2 G`, where
`C=2*3^ceil(log2 n)` is PR905's coefficient bound.
The generic PR905 estimate was `C^2 G^2`.
PR1244's noncommuting obstruction remains valid and passes as a control.
The full [argument](PROOF.md) also states the resulting conditional error
transport inequality. It does not assert a new rounded cyclic precision
formula, a physical construction, or a multiplication exponent.

The useful new step is the all-size treatment of two cuts in different
occurrences of the same child. Their overlapping factors reduce to a
child interval plus a disjoint-support rank-one term. A larger finite
census alone would not establish this fact.

## Reproduce

From a checkout, using the Python standard library:

```sh
python3 -I -O -B research/commuting-interval-audit/test_package.py
```

Expected: `PASS_COMMUTING_INTERVAL_PACKAGE`.
The nested receipt has status `PASS_COMMUTING_INTERVAL_AUDIT`.
The mathematical verifier also runs alone as `verify.py`.
Use `verify.py --write NEW_PATH` to create a fresh receipt for comparison.
The verifier refuses to overwrite an existing output.

Evidence covers 2,154,828 intervals for n=1..24, both signs, and 108 seeded
two-cut cases at n=31,32,33,63,64,65,127,128,129.
All symbolic calculations use free words with repetitions retained.
No squarefree quotient or commuting simplification hides a repeated factor.
The independent traversal matches 57 executions of the pinned dispatcher.
A separate dense rational model uses full matrix multiplication and
Gauss-Jordan inversion: 144 scalar cases and nine noncommuting block cases.
Five mathematical controls detect repeated factors, connector aliasing,
the missing commutation premise, the retained wrong-order interval, and
an omitted restoration leaf.

A third model constructs no recursive word. It checks 108 induction
identities on constrained child matrices with noncommuting two-dimensional
blocks and one, two, or three shared scratch registers.
This directly checks the six phase formulas and the three nontrivial
reverse formulas without importing the polynomial verifier.

The actual source `compose` AST executes with instrumented leaves and
its admission checks. Numerical leaf code does not run. Both traversals
and both arithmetic models are AI-assisted; they are separate code paths,
not independent human review. The written induction supplies the all-size
claim; tests support it without proving the multiplication theorem.

## Sources and scope

Research base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.
[CLAIM.md](CLAIM.md) records seed 64, the three candidates, the bounded
scope, overlap coverage, and the originating task.
[SOURCES.json](SOURCES.json) binds every retained input to SHA256, original
paths and Git blobs. Vendored source bytes and notices remain unchanged.

Credit Chafik Boukhalfa for PR628/905, Hanson Sun for PR1244's open question
and PR1085's prefix audit, and Gareth Davidson for PR877's error analysis.
The displayed coefficient uses the retained PR905 bound. We do not need
PR1085's sharper count to prove the stated interval estimate.

Only this package changes. Setup, leaf arithmetic, phase access, source
routing, copies, restoration, recursive calls and assembly costs remain
paid under their inherited contracts. This audit does not implement or
price a replacement supplier. Selected PR1094, `upstream/`, all-size/compiler,
hosting, precision/tape, exact recovery and analytic-transfer obligations
remain unchanged. This package does not claim a full supplier cold replay or hosted CI pass.

Prepared for Charles Bethin with substantial OpenAI Codex assistance in
proof, code, validation and writing. Apache-2.0. No literature-priority,
external human-review, or proof-assistant claim.

## Open next questions

Apply the transport lemma to one actual target-dependent rounded leaf
contract, preserving its inverse-preimage magnitude bound.
This matters because a better abstract interval bound alone does not
supply a valid working precision. First substitute the exact constants
from pinned PR1054. The blockers are coefficient preparation, nonlinear
local errors and internal leaf magnitudes. Avoid changing its admission
or charging model without a separate complete audit.

A second useful question asks for the sharp coefficient row bound of
an interval. The present proof reuses a conservative prefix bound.
First derive a recurrence from the six phase cases. No optimality claim
follows from the retained finite maximum values.
