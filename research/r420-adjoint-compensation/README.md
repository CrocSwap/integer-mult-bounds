# Ten optimal dirty-input tests for R420 compensation faults

Ten fixed dirty-helper assignments detect every nonzero change of at most
three coefficients in each target row of the selected R420 word's D
compensation. No set of nine nonadaptive binary assignments can give that
guarantee. This package supplies the assignments, an elementary optimality
proof, two independent execution methods, and a four-coefficient error that
all ten assignments miss.

This is an independent-verification research note, with no new circuit or
kappa. The ten tests do not replace the full symbolic checker.

## Reproduce

From the repository root, with Python 3.9 or later and its standard library:

```sh
python3 -I -B research/r420-adjoint-compensation/verify.py
python3 -I -B research/r420-adjoint-compensation/independent_check.py
```

The first command must print:

```text
PASS_R420_COMPENSATION_SUITE tests=10 optimal=10 radius=3 targets=120 blind_weight=4 controls=129
```

The second independently replays all ten Boolean inputs and reports success.
Both commands are offline and read-only. `verify.py --emit` prints the complete
deterministic certificate. The default compares every field with `EXPECTED.json`.

## Fixed map and fault model

The word is `research/e8-bit-r420/data/bitE8mut-r420.json.gz`. Registers
0 through 119 hold x, 120 through 239 hold y, and 240 through 659 hold arbitrary
helper dirt s. The ordered raw A/scatter/B target map over F2 is

```text
W0(x,y,s)_targets = x + y + K s,    K: 120 by 420.
```

Initial D adds Ks to y. Suppose only that correction changes to K+E; A,
scatter, B and C remain fixed. The raw target-to-target block is the identity,
so the final target error is exactly Es. C does not write targets. Repeated
source operands count modulo two. Fault weight therefore means changed matrix
coefficients, not the number of edited source-list entries.

The guarantee covers any nonzero E whose nonzero rows each have weight at
most three. Multiple rows may be faulty simultaneously. Outputs are observed
exactly, with each target separately visible, and inputs are fixed in advance.
Changes to the raw word, state-dependent faults, physical frame errors and
arbitrary higher-weight errors are outside this model.

The primary checker independently confirms the baseline map using backward
covectors. For a gate `z[d] ^= sum(z[s])`, its transpose adds the old
destination coefficient to each listed source coefficient. Transposes execute
in reverse gate order. Scatter indices resolve through `ret`, and operand
multiplicities are retained. All 120 target rows are checked on all 660 input
coordinates. The helper block must equal D; pulling the raw rows back through
D must leave exactly x_t+y_t.

This confirms J=I, V=I and K=D for the pinned scalar word and all 2^660 scalar
assignments, by linearity. K has 19,922 nonzero entries. Its 50,400 row-major
binary entries, encoded as one byte 0 or 1 each, have SHA-256
`c833a715013f78e383ca95a684d26c000db5cba0dc848221bb05e5db6e63d4ed`.
This baseline corroborates existing work. The new result is the optimal
test suite and its exact fault boundary.

## Construction and proof

Assign helper-relative coordinate j, from 0 through 419, the ten-bit column

```text
h[j] = 1 | (j << 1).
```

Test k sets helper j to bit k of h[j], for k from 0 through 9. Source and
target inputs are zero. The first test sets all helpers to one; the other
nine use the binary digits of j. For a changed coefficient support S in
one target row, the vector of ten errors is the XOR of h[j] over j in S.

- One or three coefficients give low bit one, hence a nonzero syndrome.
- Two distinct coefficients give distinct columns, hence a nonzero XOR.

This applies independently to every target row. The primary checker checks
420 distinct odd columns and all 87,990 pairs, then executes the actual word
under all ten assignments. Three additional packed executions put respectively
one, two and three coefficient changes into every target row and check all
120 exact syndromes. The odd-column invariant proves coverage of all
12,259,940 triples without enumerating them. This covers 12,348,350 nonempty
supports of size at most three per target.

For optimality, consider any q nonadaptive binary assignments and their
420 q-bit helper response columns. Detecting singles requires nonzero columns;
detecting pairs requires distinct columns; detecting triples forbids three
distinct columns a,b,c with a+b=c. If A is their set and a is in A, the sets
A and a+A are disjoint. An intersection would give a forbidden triple; cases
with repeated members require a zero column. Therefore

```text
2 |A| <= 2^q, so 420 <= 2^(q-1), hence q >= 10.
```

Our construction attains ten. Varying source or target inputs cannot improve
this bound in the stated model, because Es depends only on helper inputs.
The bound does not cover adaptive experiments or other observation channels.

## Exact limit, certificate and controls

Toggle D's four coefficients for absolute helpers `[240,241,242,243]` at
absolute target 201. Their labels XOR to zero, so all ten tests pass.
Yet helper input s_0=1 with every other input zero gives error one at target
201. Both facts are checked by literal scalar execution, and the full
covector check rejects this mutant's D parity. This is a deliberately changed
D, not a defect in the accepted word. These coordinates form a kernel vector
of the test matrix; no claim is made that they form a kernel vector of K.

`EXPECTED.json` contains `suite.pattern_hex`: ten 420-bit assignments,
each a 105-digit hexadecimal integer. Bit j selects helper 240+j. The
certificate also records the fault radius, counts, column rule and blind
witness. It contains no regenerated compressed artifact.

The 129 primary rejecting controls include one omitted D operand per target,
plus omitted D, a duplicate operand, exchanged D destinations, reversed A,
reversed B, wrong scatter helpers, a missing scatter operand, a source read
in D, and self-aliasing. Row t's omitted operand has index
`(81+t) % len(D[t].sources)`. Positive controls preserve duplicate-pair
parity and distinguish transpose propagation on a two-gate example.

The independent checker uses forward support sets for the baseline and ten
separate Boolean executions. It imports neither the primary checker nor
supplier code. It also checks the four-error blind witness and malformed
test suites. The fixed coverage and proof above are the stopping rule.
This is not an exhaustive arbitrary-mutation search. The elementary
optimality proof is not machine-formalized.

## Concurrent work and provenance

The initial queue refresh ended at PR725. During implementation Joshua
Snider's [PR731](https://github.com/CrocSwap/integer-mult-bounds/pull/731),
at `cf5ff54a358b400a7e69abe941d1d0ad0944b25e`, submitted the same backward
compensation reconstruction, rank/right-inverse evidence and further kernel
results. Those baseline findings are credited to that concurrent submission.
This package then pivoted to the ten-test optimum and four-error blind
witness. PR731's kernel concerns K; our blind witness concerns the separate
ten-by-420 test matrix. No PR731 code or certificate is consumed, and its
additional kernel claims are not audited here.

PR612 at `ce37f3ce35ba8891771e01492b3a21978763bebb` supplies typed R420
boundaries and B-XOR semantics. This Python check does not close its open D
parity formalization. PR737 concerns R420 frame geometry; PR745 concerns
complex JP8 private-input restoration. Neither is a dependency.

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- PR543: `2065fe4f72a914d907f1046603f5a36f17018535`.
- Selected PR626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- Selected conditional kappa: `51110230636731/31250000000000000`.
- Native word Git blob: `0c63ca62759dc63d302be6552aeeee1ede70350f`,
  identical at the base and PR543 commits.

`SOURCES.json` pins all consumed source/context files, including compressed
and decompressed word hashes. The verifier also binds the word to the selected
source manifest and PR543 dependency. Scope references are not imported.

The selected frontier and `upstream/` are unchanged. Frame legality,
COPY/ERASE realization, source/helper restoration, common-label and
mutable-basis interfaces, hosting, paid profiles, moments, precision, tapes,
exact recovery, all-size compilation and analytic transfer remain outside
the result. The independent checker's ten scalar endpoint examples do not
prove general restoration.

## Attribution

Credit eumemic's PR543 word and checker, including its disclosed Anthropic
Claude assistance; eumemic's PR493 skeleton; Dylan Crow's PR370 format and
decoder; Jacob Sussman's E8 unit; DreamingOfClouds' PR503/510 lineage;
Zhihao Chen's PR425 scalar-interface lemma; and icekylinx's mutable-source
carryover. The full predecessor notice remains in the pinned R420 package.
The selected context also credits Jeremy Kothe's PR622 construction and
Chafik Boukhalfa's PR626 allocation. Credit Joshua Snider's concurrent PR731
and the PR612 authors' typed boundary work.

Prepared for Sagar Thakrar (@thakrarsagar) with substantial OpenAI Codex
assistance, including a separate Codex worker's forward implementation and
proof review. Independent implementation is not independent human peer
review. New files use Apache-2.0. No predecessor code is copied here.
