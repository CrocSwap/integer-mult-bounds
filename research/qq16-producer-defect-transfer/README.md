# QQ16 producer errors through the zero-retention decoder

This package supplies a conditional stability bridge for approximate F0 and
B_1_2 execution. It closes the error-propagation question left outside the
[exact-producer entry contract, PR2959](https://github.com/CrocSwap/integer-mult-bounds/pull/2959).
It does not implement the producer or admit a supplier.

Let F be the reviewed F0 data map, B the reviewed B_1_2 data map, and
D = F^-1 B^-1 the fixed PR2707 zero-retention decoder. Write every field in
its represented logical coordinates. Use the maximum, over all data fields
and cover owners, of the payload Hilbert norm. The inherited physical charts
are payload unitaries, and cover maps permute owners with unitary payload
translations. Thus passage between these physical and logical coordinates
preserves this norm, at every positive common tensor depth.

Suppose completed approximate producer stages satisfy

```text
v1 = F v0 + eF,       ||eF|| <= epsF,
v2 = B v1 + eB,       ||eB|| <= epsB.
```

The second defect is relative to B applied to the actual first-stage output.
Errors may be arbitrary, coherent, state-dependent and correlated across stages.
If the implemented decoder differs from D v2 by at most epsD, its original-array
output error is at most

```text
49 epsF + 1923 epsB + epsD.                         (1)
```

The F0 inverse constant **49 is sharp** for this completed-output error model.
The decoder constant **1923 is a certified upper bound**, without an optimality
claim for the actual chart routes. These are endpoint sensitivities, not
all-cut magnitude bounds or bounds on faults inside producer instructions.
Outputs are the original logical arrays represented in F17; a later endpoint
adapter or consumer is outside the statement.

## Why the two stage errors have different prices

Keep the noncommuting order. Linearity and the inherited exact inverse give

```text
D v2 - v0 = F^-1 B^-1 [B(F v0 + eF) + eB] - v0
           = F^-1 eF + D eB.
```

Applying the two certified operator bounds and then the decoder's own error
proves (1). Charging an F0 error as if it were independently injected after B1
loses the correlation created by B. Treating both stages as having unit error
amplification is also unjustified.

The following row bounds are recomputed from pinned inputs. A,T are the two
eight-port selected sets and U is the 96-port complement.

| Inverse and output field | A | T | U |
| --- | ---: | ---: | ---: |
| F^-1, X | 47 | 2 | 3 |
| F^-1, Y | 49 | 4 | 2 |
| D, X | 1921 | 1358 | 81 |
| D, Y | 1923 | 1360 | 1 |

For F^-1 these are exact absolute row sums of its scalar 224 by 224 matrix.
Every row at a given port class has the displayed value. To attain 49, choose
the 224 F0-output errors to be a common unit payload multiplied by the signs
of the coefficients in an attaining Y_A row. The resulting output has norm 49
with input maximum norm one. Chart unitarity makes these legitimate physical
endpoint errors as well. This is a completed-output witness, not an exhibited
rounding failure of a particular finite producer.

For D, represent each logical chart map by an involution g_(s,p). Expand exact
rational coefficients while retaining ordered products of these generators.
Cancel equal adjacent generators using g_(s,p)^2=I; combine equal reduced
words, including their signs. Do not commute different generators. Every
remaining word is a composition of isometries, so the sum of coefficient
absolute values bounds its operator norm. Additional relations between actual
route products can only lower this bound, by combining more terms.

This uses the source proof that a native line changes a field's physical
chart while preserving its represented logical value, and that an affine
cover map acts by the corresponding logical g. It does not replace a physical
map with a payload-only permutation, drop a tensor factor, or reprove the
native semantics. Involutivity and these isometry properties are inherited
assumptions checked in the predecessor native work.

## One sufficient original-input error budget

Suppose ||v0|| <= H with H>0, and beta is a nonnegative integer. The following
completed output tolerances suffice:

```text
epsF <= H 2^(-beta-8),
epsB <= H 2^(-beta-13),
epsD <= H 2^(-beta-1).
```

The resulting error is at most `7587/8192 * H * 2^-beta`, strictly below the
target `H * 2^-beta`. These reserves are sufficient, not minima.

The existing decoder's state-relative defect theorem can furnish epsD under
its own completed ADD/line/map assumptions, exact owned CLEARs and exclusive
workspace. It needs a bound on the **actual** supplied v2, not the exact
producer's state. Here is one conservative such bound, requiring no input grid:

```text
||F|| <= 58,       ||B|| <= 312,
||v2|| <= 18096 H + 312 epsF + epsB < 2^15 H.
```

To verify these coarse forward bounds, each R row has four signed entries in
A, four in T and 48 in U; every K=R*/4 row has absolute sum one. For F, its
X_A/X_T/X_U bounds are 4/56/57 and Y bounds are 6/58/58. For B with input
norm L, `a=ell_(1,T)x` has norm at most 4L. The logger
`u=E_2 y` has A bound 53L and off-A bound L. Consequently `b=R_1 u` is
bounded by 264L. The B output bounds are X_A/X_T/X_U = 55/312/2 and
Y_A/Y_T/Y_U = 53/309/5. The source geometry checker verifies the support
and section premises; the triangle inequalities establish these all-depth
forward bounds. They are not producer-interior range certificates.

Apply [PR2736's completed-defect theorem](../qq16-zero-retention-defects/PROOF.md)
to actual input bound Bhat = 18096H+312epsF+epsB. Its parameter
`b=beta+16` gives decoder error strictly below `H*2^(-beta-1)` if its
completed relative defect parameter satisfies `u <= 2^(-beta-38)`.
For beta=64, one sufficient triple is F0 output error `H*2^-72`, B1 output
error `H*2^-77` and decoder completed relative parameter `u<=2^-102`.
This is not a component width. A common dyadic input grid and finite-format
realization remain separate obligations.

## Reproduce and evidence

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-producer-defect-transfer
```

The primary checker authenticates the source inventory and five inputs,
then interprets the exact 3,823-event logical word. It separately starts the
suffix after the inverse-B1 checkpoint on 224 independent F0-output symbols.
The full decoder has 286,376 final polynomial terms, of degree at most four.
RESULT.json stores each of the 448 rows' exact norm, term count and canonical
polynomial digest. Default replay is read-only; `--write` creates an absent
receipt and refuses to overwrite it.

The independent checker derives the polynomials from the ordered inverse
equations in PR2681's proof, using R/K and the port partition. It neither reads
the literal word nor imports primary/predecessor executable code. All 448
row summaries must match, including coefficients and route order through
their digests. This independently checks the arithmetic certificate; the
inherited ideal native semantics remain outside both implementations.

The tests exercise coherent stage errors on four noncommuting toy cover
owners, the sharp 49 witness, source/receipt failures, optimized execution,
dirty-scratch initialization and a changed scalar operation. These finite
fixtures support the quantified argument; they do not establish an actual
physical caller or native implementation.

## Scope and decision

The milestone is a conditional interface lemma. The exact source equations,
native/chart semantics and PR2736 completed-error theorem are inherited.
This package does not verify producer child interiors, dirty-helper range,
helper restoration, a legal common grid, overflow, physical movement/hosting,
storage, cleanup, a consumer invoice, an all-size compiler or multiplication.
No frontier or child tariff changes. The selected cold replay is unrun because
the selected construction and frozen inputs are unchanged.

Family decision: narrow and stop.

## Open next questions

The new test for a finite producer is to
derive its two completed output defects in this norm, including arbitrary
dirty helpers and any correlations. Start with a pinned literal producer,
completed native-child contracts and an intermediate magnitude ledger. That
implementation and its paid physical cost are the blockers, rather than
another inverse or decoder precision constant. The caller must still consume
F17 outputs affordably. Unknown costs remain unknown.

Scientific base is main `318ba71b8927f81141f41a89c1af74323586f253`, priority
revision 5. TASK.json records the task-card scope change, live overlap and
submission freshness. The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18975580)
tracks this exact implication.

New result and checks by Nick Petalas, Apache-2.0. Credit Ali Romman and the
joint-query team for the reviewed F0/B1 maps; Arham Tahir/PR2681 for the ordered
inverse; ywz65/PR2707/2540 for the physical decoder; Nick Petalas/PR2736/2959
for the numerical and exact-entry predecessors; and starship-s, Sagar Thakrar,
Ross Richardson and the native/geometry lineage retained in those sources.
Substantial automated assistance was used. No independent human or formal-kernel
review is claimed.

Build the Lever led to a replayable polynomial certificate. Prove It Works led
to two distinct reconstructions and the public-command checks. Test Behavior,
Not Implementation led to injected coherent errors and rejecting CLI controls.

Power-of-Ten deviations: managed Python arithmetic and collections allocate
during verification, bounded by fixed 224 inputs, 3,823 events, degree four,
50,000 terms per row and 600,000 live state terms. The independent arena caps
2,048 allocated rows; primary summary construction temporarily retains the
F0 rows alongside its full replay. A map replacement may temporarily retain
both its input and output rows. Files are capped at 1 MiB, decompression at
12 MiB, inventory at 16 KiB and JSON objects at 4,096 keys. Rational numerator
and denominator limits are enforced in primary arithmetic; independent
arithmetic has the same fixed authenticated coefficients and finite degree.
Python/JSON allocator overhead is not profiled. JSON's duplicate-key callback
and test-only source loading are bounded dynamic-dispatch deviations. Warning
diagnostics and local Ruff checks cover new code; no fixed-allocation machine
or static type-checker proof is claimed. A variable-size service or physical
implementation requires a separate resource and diagnostics review.
