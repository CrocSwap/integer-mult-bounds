# All-dyadic parent coefficients cannot improve the X4 target-forest floor

**Scoped negative result; no new kappa.** For the pinned historical PR799 X4
compensation matrix, the minimum cost of a restored single-parent target forest
remains **10,883 primitives per real component** (21,766 across both components),
even when every parent coefficient may be an arbitrary nonzero dyadic rational.
This extends PR932's signed-unit forest floor to a strictly larger circuit class.

This concerns one zero-frame compensation panel and its original independently
paid binary-Horner lowering. It is not an arbitrary-circuit optimum. The current
selected U8/T21 witness at this contribution's base remains
**kappa = 0.001661957774647029**; no selected record or supplier is changed.

## Reproduce

From the repository root, Python 3.10+ with the standard library; offline:

~~~sh
python -I -O -B research/complex-x4-dyadic-forest-seed31/verify.py
~~~

Expected final line:

~~~text
PASS_X4_DYADIC_FOREST coefficients=1086 ordered_pairs=12432 cases=13501152 nonunit_root_gains=970 dominating_units_or_roots=all floor=10883 no_new_kappa
~~~

The command checks source hashes, recomputes the complete certificate, compares
all per-coefficient statistics and witnesses with the independent implementation,
runs 12,544 tree-cycle inequalities, independently recomputes the signed-unit
floor with Prim, and runs literal-primitive and endpoint controls. It writes
nothing. Add --json for the compact evidence receipt. --write-new NEW_PATH
also exports the verified certificate and refuses an existing output path.

Additional adverse controls:

~~~sh
python -I -O -B research/complex-x4-dyadic-forest-seed31/test_package.py
~~~

This passes nine tests. The independent checker can also be run alone with
python -I -O -B research/complex-x4-dyadic-forest-seed31/independent.py;
it prints its full JSON evidence and does not write files by default.

## Evidence and the distinction that matters

For a target row C_i, parent row C_j, and coefficient lambda, the exact bill is

~~~text
E(i,j,lambda) = H(C_i - lambda*C_j) + 2 H(lambda),
H(n/2^d) = 3 + floor(log2(abs(n))) + popcount(abs(n)) + d,
H(0) = 0; row prices are sums of entry prices.
~~~

The two boundary shears, every source addition, work clear, doubling, halving,
and target accumulation are paid. The transformed circuit is prepared from
leaves to parents and restored in reverse order, so it implements
T^-1(Ty+TC h)=y+C h for arbitrary targets and helpers. It introduces no helper,
copy, frame transition or recursive child. Unchanged work outside the panel
is irrelevant to this local exclusion and is not discounted.

The [proof](PROOF.md) reduces every dyadic outside the finite core to a
strictly more expensive alternative that leaves the child as a root. The core
is all nonzero multiples of 1/8 with absolute value below 68. For this matrix:

| Check | Exact result |
|---|---:|
| Target rows / active helper columns | 112 / 216 |
| Core coefficients / ordered target pairs | 1,086 / 12,432 |
| Complete coefficient-pair comparisons | 13,501,152 |
| Nonunit comparisons | 13,476,288 |
| Nonunit edges beating their original root row | 970 |
| Nonunit edges tying their original root row | 34 |
| Nonunit edges beating or tying the best root or same-parent signed-unit alternative | 0 |
| Minimum finite-core replacement gap, per real component | 56 |
| Signed-unit and all-dyadic forest minimum, per real component | 10,883 |

The 970 individually profitable edges occur only at lambda=-5,-3,3,5. They
are not new forest improvements: a signed-unit edge to the same parent is
cheaper. The minimum replacement gap is attained at lambda=2, child 125,
parent 139. The value 56 is only a finite-core minimum, not a uniform claim
about the infinite tails.

Replacing each nonunit edge by the cheaper root or same-parent unit option
preserves a forest, including all descendants' prices. Hence the exact
signed-unit floor is also the all-dyadic floor. The known unit forest attains
it. Applying an undirected MST directly to nonunit directed edges would be
invalid; the exchange argument removes them first.

[CERTIFICATE.json](CERTIFICATE.json) stores every core coefficient's extrema,
witnesses and counts, plus an attaining unit tree. The primary checker uses
Fraction prices and Kruskal. [independent.py](independent.py) uses integer
reduction, literal Horner words and dense Prim; it imports no primary checker
or predecessor implementation. Both bind the same original source bytes.
The expanded independent census SHA-256 is
69d56df08131e475882bab07c54c2fa91456c0ae20d2785c38651611a79ebc53.

Controls reject omitted preparation/restoration, wrong signs, incorrect
traversal order, unpaid tree boundaries, a valid but nonminimal all-root
forest, incomplete or mistyped certificates, and changed sources. A
helper-only check deliberately misses omitted preparation, while arbitrary
target columns detect it. A synthetic quarter-grid example makes lambda=3
strictly beat both units, establishing that this result depends on the actual
X4 matrix. These are exact finite controls; the universal tails are justified
by the written inequalities, not by sampling large coefficients.

## Search scope and provenance

Exact base: **018418fd789ce12a8c176279fe012138713ff53d**.
[CLAIM.json](CLAIM.json) records OS assignment seed 31, the complex-supplier
track, three candidate tasks, the local scope claim and its evidence-driven
refinement. Seed31 initially set the odd-numerator screen through 31; the
derived tail reduction justified replacing it with complete finite coverage.
No randomness or time cutoff limits the final census. The stopping rule is
completion of all 1,086 coefficients and all 12,432 ordered pairs. Equal pair
histograms are evaluated once with exact multiplicities; all pairs remain
covered. This is not a reopened signed-power-of-two pair search: nonunit
coefficients such as 3 and 5 and overlapping single-parent forests are admitted.

[SOURCE-PINS.json](SOURCE-PINS.json) pins the immutable source archive,
decompressed word, native lowering and predecessor proof/recipe sources.
The archive is the accepted PR799 replay, not a current PR title or an
unverified pending construction. Its source head is
80e6463157cfc80b85af09e7e2f14748fe2dac60.

Credit Ross Richardson's [PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932)
(c5b5b30279bdda513e97017587806a0b9f0ca850) for the X4 unit forest and floor;
ToikY's [PR909](https://github.com/CrocSwap/integer-mult-bounds/pull/909)
(5896f6fce48ee1d507722cc91eb1dcccc878670d) for signed-power-of-two disjoint-pair
exclusion; @dd-hemant PR816, Oscar Fennell PR759 and Sricharan Vagvala PR749
for restored forest/pair predecessors. Credit Jeremy Kothe PR799, Chafik
Boukhalfa PR741, icekylinx and the retained supplier/compiler/cold-helper
lineage. The new census implementations do not import their code. Source
artifacts and upstream/ remain unchanged; repository Apache-2.0 terms apply.

Prepared for [@woklerx](https://github.com/woklerx), with substantial OpenAI
Codex assistance in research, implementation, proof, checking and writing,
including separate bounded workers for the independent checker and mathematical
review. No independent human review is asserted.

## Limits and handoff

Excluded: multiple parents, helper-basis changes, arbitrary sequential shears,
shared coefficient work, another scalar lowering, folded boundary work, changed
frames and other source matrices. This extends only the stated forest family.
The precision, realization, compiler, whole-call hosting, tape and analytic
obligations inherited by the multiplication result remain open. No full Lean
multiplication proof, new practical speedup, or new kappa is claimed.

[VALIDATION.md](VALIDATION.md) records executed checks and unrun integration
suites. This package installs no candidate, so a new native supplier replay is
not claimed. Any future integration must retain the existing physical and
precision obligations and the attaining forest's source bindings.
