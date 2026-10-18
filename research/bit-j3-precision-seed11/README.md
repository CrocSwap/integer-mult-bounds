# One extra XOR reaches the optimal positive envelope for the restored J3 block

**Finite bit-circuit construction and exact local cost/precision frontier; no new κ.**

The restored three-helper/three-target all-ones block has the complete Pareto
frontier `(gate count, forward positive peak, reverse positive peak)`

```text
(7, 5, 5), (8, 4, 4).
```

PR [#1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306), by
@commdata2338, already establishes the minimum of seven XORs for this map.
The new result prices **every shortest word's positive lift**, rather than
retaining one word per binary endpoint. The eight-gate witness pays one extra
XOR to reach the support lower bound of four in both directions. Its positive
transfer matrices also dominate the stated seven-gate witness componentwise,
so the improvement is valid for unequal incoming nonnegative bounds.

## Model and complete bill

There are exactly six existing registers, ordered `h0,h1,h2,t0,t1,t2`, all with
arbitrary initial values over any F2 module. The required map is

```text
h_i -> h_i
 t_i -> t_i + h0 + h1 + h2       (i = 0,1,2).
```

Every ordered XOR `r_d ^= r_s`, `d != s`, costs one unit. All 30 choices are
allowed, including target-to-helper feedback. There are no extra registers,
clean ancillas, frame changes, COPY/ERASE events, recursive calls or external
observers inside this block. The construction assumes a common zero frame.
Every preparation and restoration is included in the gate count; no source
access is supplied outside the declared XOR operations.

For the positive envelope, replace each XOR by the nonnegative update
`v_d <- v_d + v_s`, starting with all six bounds equal to one. Let `F` be the
largest bound in the forward word and `B` the largest in its reversed inverse.
The updates are monotone, so their final maximum is also the prefix maximum.
This is the ADD-only restriction of the retained
[`literal_bounds`](../r439-bsection-stars-seed01/verify.py) convention. It is a
bound on this local word, not a measured machine word size or a full supplier
precision calculation.

## Construction and exact result

The witnesses below list `(destination, source)` in the register order above.
Both restore every helper and every initial target basis vector.

```text
7 gates: (0,1) (0,2) (3,0) (4,0) (5,0) (0,2) (0,1)
8 gates: (0,1) (3,0) (4,0) (5,0) (0,1) (3,2) (4,2) (5,2)
```

The first builds a three-helper sum, updates the targets, and restores the
helper. The second shares a two-helper sum, restores it, and adds `h2` directly
to each target. Its complete bill is eight XORs on the same six registers.
This is a cost/precision tradeoff, not a reduction in ADD count.

The complete shortest-word census is:

| F | B | Seven-gate words |
|---:|---:|---:|
| 5 | 5 | 108 |
| 6 | 6 | 72 |
| 8 | 8 | 36 |

There are **216** seven-gate words and no words of length at most six. None of
the 216 uses target-to-helper feedback. The no-shorter-word result independently
corroborates PR1306; it is not claimed as the new contribution.

### Why this is the complete frontier

Each nonnegative integer lift reduces modulo two to the exact binary endpoint.
Every target row of that endpoint has four nonzero entries. Its positive row
sum is therefore at least four, for any circuit length. The endpoint is an
involution, so the same argument applies to the reversed word. This proves
`F >= 4` and `B >= 4` without a bounded search.

The complete finite census proves that every seven-gate word has `F=B>=5`.
The seven-gate witness attains five, and the eight-gate witness attains the
universal lower bound four. Thus every longer circuit is weakly dominated by
the eight-gate witness, and the displayed frontier is complete **within this
six-register, unit-XOR, common-frame model**.

### Unequal input bounds and a legal local replacement

Write `J` for the 3-by-3 all-ones integer matrix and `E_ij` for a single matrix
unit, using zero-based indices. The two witnesses' nonnegative transfer
matrices, in **both** directions, are

```text
Q7 = [[I + 2 E01 + 2 E02, 0],    Q8 = [[I + 2 E01, 0],
      [J,                  I]]         [J,         I]].
```

Consequently `Q8 <= Q7` entrywise; only the `(h0,h2)` entry changes, from two to
zero. For every nonnegative incoming envelope vector `v`, `Q8 v <= Q7 v`.
Because these ADD-only bounds are monotone throughout each block, the maximum
bound within the replacement also cannot rise. Any unchanged continuation
built from nonnegative ADD/COPY operations and zeroing ERASE bounds preserves
that inequality. The same argument holds in reverse.

At the binary level both blocks implement `[[I,0],[J,I]]`; substituting one for
the other preserves a surrounding computation when there is no interior
observer or other state change and the same common frame applies. This is a
local algebraic substitution statement. Finding a physical hosted occurrence,
charging its extra XOR, and running its complete guards remain separate work.

## Reproduce and check coverage

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/bit-j3-precision-seed11
```

Expected result includes:

```text
PASS_J3_PRECISION shortest_words=216 peaks=5:108,6:72,8:36 frontier=(7,5),(8,4) controls=8 no_new_kappa
PASS_INDEPENDENT_J3_PRECISION truth_tables=64 shortest_words=216 dense_lifts=432 frontier=(7,5),(8,4)
PASS_J3_PACKAGE_CONTROLS mutations=9 independent_rejections=18
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-j3-precision-seed11 outcome=completed
```

[`verify.py`](verify.py) uses packed binary row matrices. It enumerates all
`30^4=810,000` four-gate prefixes and all `1+30+900+27,000=27,931` backward words
of length zero through three, retaining **all paths** at every binary endpoint.
For each length `L=4..7`, the fixed split `4 | (L-4)` is unique. Involutivity of
each XOR makes endpoint matching equivalent to an exact complete word.
Lengths zero through three are also tested directly. There are no symmetry,
heuristic, floating-point, cancellation or guard-based pruning rules.

[`independent.py`](independent.py) imports no primary-checker code. It instead
represents each register by its full 64-input truth table, uses the opposite
`(L-4) | 4` split, and computes positive lifts by dense nonnegative integer
matrix multiplication. Both implementations agree on the SHA256 digest of the complete sorted
seven-gate-word list, all counts and all positive classes. The digest encodes each word as seven bytes of gate indices in
lexicographic `(destination,source)` order, then concatenates the sorted words.
These are separate implementations using the same meet-in-the-middle proof,
not independent human review.

Controls reject missing restoration, a wrong source, a missing target update,
self-XOR, invalid register encodings, endpoint-only growth and the false claim
that one binary endpoint determines one positive envelope. Clean helpers hide
the omitted-restoration fault, which the dirty-input check detects. A paid
neutral pair checks that cancellation does not make two gates free.
[`test_package.py`](test_package.py) separately corrupts nine proof-relevant
certificate fields; both implementations must reject each corrupted artifact.

The positive witnesses are linear identities over every F2 module. The finite
census certifies the specified six-register search domain; it is neither a Lean
proof nor a formal verification of the full integer-multiplication theorem.

## Assignment, provenance and limits

- OS-random assignment seed: **11**, bit-supplier track. The three candidate
  scopes and selection `11 mod 3 = 2` are recorded in [TASK.json](TASK.json).
- Exact base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
- Prior gate-count certificate: PR1306 head
  `0d4c0069f1f4592833304a9ea6e61e676c566113`, `K=511`, minimum seven.
  Its Git blob and SHA256 are recorded as context in [SOURCES.json](SOURCES.json);
  neither checker imports or trusts it for the result.
- Selected context: PR1094, κ=`836330098538459/500000000000000000`, with PR589
  on PR555. The source-bound baseline says the **complex** primitive binds.
  Exact selected certificate, assembly, manifest, review and ledger pins are in
  SOURCES.json. They are historical provenance, not fresh full-replay evidence.
- Claim: [Discussion1507](https://github.com/CrocSwap/integer-mult-bounds/discussions/1507).
  [OVERLAP.json](OVERLAP.json) records the bounded overlap checks and exclusions.
- Search stopping rule: exhaust lengths through seven, check the eight-gate
  attaining word, then stop. No full supplier, native multistage or outer
  assembly replay was run. The selected record and `upstream/` are unchanged.

There is no new paid recursive profile or κ. Compiler/common-frame realization,
physical hosting, intermediate precision/tape admission, exact recovery and
analytic transfer remain unverified for any proposed supplier adoption. The
componentwise bound can justify a local replacement; it does not itself show a
strict improvement in a complete word's maximum or cover intervening observers.

## Open next questions

Does an actual pinned R439 word contain this seven-gate J3 block at a place where
its helper bound is limiting? A useful first check is to find one exact
occurrence, propagate its actual incoming envelopes through both matrices, then
replay the complete word and bill the extra XOR. A full guard improvement could
make the tradeoff useful. The blocker is that no hosted occurrence or full
invoice has been established here; no wider search is justified by this local
certificate alone. The structured question is also in TASK.json.

## Credit and license

Credit @commdata2338 for PR1306's complete minimum-XOR study and boundary model;
@woklerx for PR1194/1311's semantic-D work; eumemic and DreamingOfClouds for the
PR555/589 bit supplier; Gareth Davidson, @theon199 and Sagar Thakrar for the
helper-sharing and positive-envelope lineage; and Aaron Wang and Ross Richardson
for the phase-B predecessors retained in PR1062. Cinna Davis's [PR1341](https://github.com/CrocSwap/integer-mult-bounds/pull/1341)
is related envelope optimality for a fixed R439 quad17 integer transfer; this
package instead allows every XOR word for the different binary J3 endpoint.
The selected PR1094 review preserves the full construction attribution. No priority is claimed for XOR
sharing, elementary positive majorants or meet-in-the-middle enumeration.

Prepared by Hanson Sun (@bbMisk) with substantial OpenAI Codex assistance in
research, proof, implementations, verification and writing. No independent human
review is claimed. New work is Apache-2.0. No predecessor source was modified.
