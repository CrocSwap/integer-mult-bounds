# The simple-word parity-capacity filter and its repeated-prefix boundary

The `Engine::capacity` predicate in conorholds' retained
[connector-covering-code](../connector-covering-code/README.md) is a **necessary
condition for a simple restored universal word**, under its four-low-coordinate,
three-high-coordinate projection. The proof below includes repeated **low**
vertices and binds every rejection to the actual source. A separately implemented
position-pair oracle agrees with the compiled predicate on **791,827 declared gap
cases**, with **53,379 accepted**. Accepted gaps are not constructed words.

The simplicity premise matters. The credited universal word
`010201030102010345464546` has 24 steps and 23 distinct prefixes. The actual
predicate rejects its projection: nine positions at low vertex zero represent
only eight distinct high states. Thus it is not a necessary condition for
arbitrary restored words; applying it to repeated-prefix length-22 candidates
would need an additional argument. This is an explicit boundary control, **not an
error in the predecessor**, whose length-22 path engine is explicitly restricted
to simple words and handles repeated-prefix cases separately.

This is a scoped proof and finite implementation audit. It does not reprove
`f(7)=24`, rerun either complete seven-label census, admit a supplier, or change
kappa. The new evidence concerns one predicate in the newer length-22 argument.
The reconstruction of #2973's old counterexample is credited calibration.

## Source boundary

The audited source is `cycle_search.cpp` at main introduction
`e67ca5f26351e09c5bb314821633e511212f88ec`, SHA256
`597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1`.
The package base is `463113d675af7410ac91d53a4fed51ec6494eb9a`.
The claim is in [discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19001874).
[SOURCES.json](SOURCES.json) pins the exact old Python/C engines, callers,
corrected #2973 engine, and successor source. Frozen sources are unchanged.

[audit.cpp](audit.cpp) includes the original C++ file with its entry point
renamed and calls `Engine::capacity` directly. It does not copy or alter that
predicate. Its oracle lists individual time positions and then every unordered
pair; it does not use the source's aggregated products, `low_points`, or parity
routine. The source generates the 5 A and 77 B low templates for this finite
comparison. Completeness of that template generator is **not** established here.
A further Python oracle checks separately specified inputs and actual universal
words against the compiled predicate.

## Necessary-condition proof

Write a full prefix as `(a,h)` with low component `a in F2^4` and high
component `h in F2^3`. Rotate a restored word to end in a low step and translate
its starting prefix to zero. Let `a_i` be the low prefix before low step `i`,
and let `g_i` be the number of preceding high steps since the previous low step.
Block `i` contributes exactly `g_i+1` nonclosing prefix positions, all at `a_i`.
The terminal closing prefix is not an additional position.

Each high singleton step flips the Hamming parity of `h`; a low step leaves it
unchanged. Consequently the high-parity sequence in block `i` starts at

```
p_i = (g_0 + ... + g_(i-1)) mod 2
```

and alternates for `g_i` steps. With `s_i=g_i+1`, its even and odd position counts
are `floor((s_i + [p_i=0])/2)` and the remainder. This is exactly the source's
`high_parity` update and its `even` expression. Summing over **every** block
with the same `a_i=a` gives `E_a,O_a`, and `S_a=E_a+O_a`.

For a **simple** full word, these positions are distinct full states, including
between different blocks at the same low vertex. There are only eight high
states, so `g_i<=7` and `S_a<=8`. Restoration requires an even total number of
high steps. These justify the source's first three rejection conditions. The
word need not have distinct low prefixes.

For each low difference `d`, count unordered pairs of distinct full positions
whose high difference has parity `epsilon`. Their exact counts are

```
C(0,0) = sum_a (choose(E_a,2) + choose(O_a,2))
C(0,1) = sum_a E_a O_a
C(d,0) = sum_{a<b, a+b=d} (E_a E_b + O_a O_b)       (d != 0)
C(d,1) = sum_{a<b, a+b=d} (E_a O_b + O_a E_b)       (d != 0).
```

The first two expressions include pairs from **different blocks at the same
low vertex**. Summing separate within-block counts would omit those pairs.
These four formulas are the source's `even_zero`, `odd_zero`, `even`, and `odd`.

A universal prefix set must cover all `(d,h)` differences. In `F2^3` there are
four high states of each parity, including high zero among the even states.
For `d=0`, omit the all-zero difference: it needs no distinct-position pair.
Every pair produces only one difference, so universality requires

```
C(0,0) >= 3;   C(0,1) >= 4;
C(d,0) >= 4 and C(d,1) >= 4 for each d != 0.
```

Every source rejection is therefore necessary. Collisions may make these
conditions too weak; passing is not sufficient for a lift, an endpoint join,
a simple word, or coverage. The proof applies to every nonnegative gap vector
in this source contract, beyond the bounded vectors exercised below.

### Which parity changes preserve this test?

For any `lambda in F2^4`, replace high parity by
`wt(h) + lambda dot a (mod 2)`. A pair at low difference `d` changes its parity
by the fixed bit `lambda dot d`. Thus it merely swaps the two buckets for that
`d`. For `d=0` no swap occurs; for `d!=0` both thresholds are four. All sixteen
choices give the same verdict. Full-word time parity is the choice
`lambda=(1,1,1,1)`; it is a valid alternative **for this particular test**.
Resetting high parity independently at each block is not this transformation.
Nor can a single high coordinate be inferred from the number of high steps.
This explains the precise parity premise rather than declaring every change
of partition valid or invalid.

## Finite evidence and controls

[RESULT.json](RESULT.json) is compared with a fresh run, not trusted as an input
certificate of successful execution. The declared native domains are:

| Domain | Gap vectors per source template | Templates | Cases | Predicate accepts |
|---|---|---:|---:|---:|
| A core | `0<=g_i<=3`, eight gaps summing to 14 | 5 | 33,640 | 1,924 |
| B core | `0<=g_i<=2`, ten gaps summing to 12 | 77 | 520,905 | 51,305 |
| A boundary | At most two nonzero gaps, each in `1..8` | 5 | 9,285 | 0 |
| B boundary | At most two nonzero gaps, each in `1..8` | 77 | 227,997 | 150 |

These are complete **predicate-input** domains, not complete word searches.
Boundary domains include out-of-contract gaps of eight to test rejection.
Their exact sizes are independently computed in Python by generating-function
coefficients or `1+8b+64*choose(b,2)`. The oracle records the first failed bound;
there are no source/oracle disagreements.

The controls also include:

- The retained simple universal 24-step fixture, directly checked for 24 distinct
  prefixes and all 128 differences. All 176 eligible three-high-coordinate
  projections, orientations and low-step endings pass the actual predicate.
  Of these, 120 have repeated low prefixes. All sixteen parity changes above
  are checked on each: 2,816 exact bucket permutation checks.
- A separate Python/source comparison on both complete binary-gap cubes for low
  words `01021323` and `0001021323`, plus two discrimination fixtures: 1,282
  queries. The universal projections and repeated-prefix boundary are additional
  source queries.
- Resetting parity at each block changes 1,148 B-core verdicts; dropping pairs
  between equal-low blocks changes 542. The explicit fixtures are
  `0001021323 / 0101202222` and `0001203231 / 1111111122`, respectively. Both pass
  the correct capacity predicate and fail the mutation. Their complete pair
  profiles are recorded: reset changes `C(6,1)` from 4 to 3, and omission
  changes `C(0,0)` from 6 to 2. **They are gap fixtures, not universal-word witnesses**.
- The nonsimple universal word above, projected with high coordinates `{0,1,2}`,
  gives low word `0012131213` and gaps `(7,7,0,0,0,0,0,0,0,0)`. At low zero,
  nine positions but eight distinct high states make the simplicity-specific
  guard fail. Removing this premise would invalidate the proof.
- #2973's `01021323` calibration: prefixes `0,1,3,2,6,4,12,8`, all 16
  differences, weight split `(4,4)`, bit-0 split `(6,2)`, bit-0 excess 8,
  balanced budget 5, and valid actual-size bit-0 budget 9.

All acceptance checks remain active under Python `-O`; no `assert` is used.
Source digests are checked before compilation. Native builds and runs are serial,
time-limited, and use a temporary directory removed on exit. No word CSP is run.
The registered failure-control command changes private copies of the actual
native predicate: a parity reset flips the first discrimination fixture, and
relaxing the fiber bound to nine admits the repeated-prefix control. Altered
source hashes, a corrupted receipt and a truncated native query all reject.

## Which predecessor exclusions need replacement evidence?

| Evidence | Exact affected implication | Status within this audit |
|---|---|---|
| #2542 `search.py` length-18 call | `cyclic_census(7,18,budget=9,simple=True)` groups by `nq & 1`, not the time-balanced weight classes used to derive 9 | Old zero-hit receipt cannot certify that exclusion. #2973 supplies a corrected length-18 receipt; #3005 reports separate replacement enumeration. Neither full enumeration is rerun here. |
| #2634 `census20.py` and vendored engine | The same Python engine is byte-identical; the length-20 call substitutes budget 27 | Its partial word traversal and inherited length-18 replay do not establish completeness. They need corrected evidence wherever relied upon. |
| #2691 `f7_census.c` | The C traversal uses `nq & 1` and `BUDGET=27` | Completing all shards reproduced the same invalid filter. Its old 6,305,209,079-node exclusion is not repaired by cross-language agreement. #2973/#3005 provide separate length-20 evidence. |
| #2973 corrected engine and #3005 union-support engine | Distinct weight-parity sets, valid target budgets, complete split coverage | Existing replacement evidence; this package pins #2973's partition and credits #3005. No new full replay or admission. |
| `connector-covering-code` simple length-22 branch | Actual high-parity pair capacity after the four-plus-three projection | This one predicate's necessity and repeated-low bookkeeping are checked here. Remaining path tables, propagation, symmetry reductions and complete enumeration are not checked. |
| That successor's repeated-prefix branch | Exclusion of shorter words with non-simple prefix walks | Requires its separate minimum-cover/classification and support arguments. The universal 24-step control disproves an unrestricted extension of this predicate; it does not disprove a length-22 exclusion. Those separate arguments are not checked here. |

The correction does not itself revoke the old counting identity, explicit
witnesses, or later set-level #2773/#2870/#2911/#2933/#2961 arguments. Their
hypotheses and evidence are separate. The actual-size set-enumerator question
is separate from this successor audit. No retained old package is edited and
no final seven-source bound is declared false by the tiny counterexample.

## Reproduce

From the repository root, Python 3.12 and a C++17 compiler are sufficient:

```sh
python3 -I -B scripts/research_package.py --package research/connector-capacity-parity-audit
```

The registered ordinary and optimized commands each print:

```text
PASS_CONNECTOR_CAPACITY_PARITY cases=791827 accepted=53379 positive_projections=176 gauges=2816 python_queries=1282 repeated_prefix_control=1 no_full_census
```

The third registered command prints
`PASS_CAPACITY_FAILURE_CONTROLS source_pin=1 native_mutants=2 malformed_query=2 receipt=1`.
All four native domain rows also passed an AddressSanitizer/UndefinedBehaviorSanitizer
build with identical counters and no diagnostics; this development check is
recorded in TASK.json and is not required by the portable replay.

Direct replay is `python3 -I -B research/connector-capacity-parity-audit/verify.py`.
`--write-receipt` explicitly regenerates the receipt; ordinary replay never
rewrites it. [TASK.json](TASK.json) records environment and completed checks.

## Open next questions

An independent implementation of the complete B length-22 path exclusion would
close a different remaining computational obligation. Start by checking its
endpoint, disjointness and conditional-coverage propagation against explicit
path-domain tuples, with planted feasible controls, before proposing a full
82-orbit run. This package gives neither completeness of those rules nor a
resource budget for that search. Published coding/classification premises and
the non-simple branch likewise remain separate obligations. Replaying the old
unsound counts again would not resolve any of these questions.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

conorholds supplied the successor, the native predicate and the simple 24-step
fixture. Nicholas Stone supplied #2691 and the #2973 correction and tiny
counterexample; Nick Petalas supplied #3005's independent union-support replay.
Aaron Wang supplied the #2542/#2634 census and later set-level lineage. Ross
Richardson supplied the #943 prefix-walk model; Douglas Colkitt supplied #1185
and the retained Gray upper witness. jwr's `f7-bit0-false-prune` already checks
the tiny counterexample and a small word domain; this calibration is not claimed
as new. The substantial AI reviews credited by the predecessor are retained as
prior evidence, not represented as independent human review.

New derivation, code, checking and writing used OpenAI Codex. Apache-2.0;
predecessor attribution is preserved. No independent human or formal-kernel
review is claimed.
