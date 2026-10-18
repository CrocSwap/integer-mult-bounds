# Mixed double transpositions keep the six-call bill in S4

For three arbitrary dirty roles over \(\mathbb F_2[S_4]\), the heterogeneous
target

\[
\operatorname{diag}([(13)(24)],[(12)(34)],[e])
\]

has exact minimum **six** paid adjacent-transposition calls in the alphabet
\(\{(12),(23),(34)\}\), even with free scalar \(GL_3(\mathbb F_2)\) mixing.
The direct word costs four calls for the first target and two for the second.
A complete formal group-algebra meet excludes all four-call words. A sign
quotient excludes odd lengths, and the target element \((13)(24)\) has
adjacent-transposition length four, so no shorter length was overlooked.

## Why this target

The target pair consists of two distinct commuting double transpositions in
the Klein four subgroup of (S_4). In the broader rank-one-displacement
alphabet of [PR #1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333),
the two active entries each have displacement rank two, so the optimistic
lower-cost screen is four. With only adjacent transpositions, the direct bill
is six. The question was whether rank-one coupling across the dirty roles can
meet that four-call floor.

The nearest predecessor is [PR #1734](https://github.com/CrocSwap/integer-mult-bounds/pull/1734),
which uses the same S4 group, paid alphabet and role count for the repeated
target \(\operatorname{diag}([(13)(24)],[(13)(24)],[e])\), whose direct bill
and exact minimum are eight. This package changes the target relation to the
distinct pair \(((13)(24),(12)(34))\), with direct bill six. PR #1720 treats
two identical 4-cycles; Discussion #1740 / PR #1749 treats distinct
noncommuting 3-cycles. Current overlap details are in `OVERLAP.json`.

## Exact evidence

The complete alphabet has 84 factors: three adjacent transpositions times 28
binary rank-one idempotents. The verifier forms all 7,056 ordered pair words,
with 4,698 distinct products, then checks all 7,056 target-relative joins.
This excludes all 49,787,136 four-call words. Pair-state digest and exact
counts are in `RESULT.json`; the proof and parity argument are in `PROOF.md`.

Positive controls are the exact six-call mixed word and the found/replayed
four-call word `D_E00(s3), D_E11(s3), D_E11(s1), D_E00(s1)` for
\(\operatorname{diag}([(12)(34)],[(12)(34)],[e])\). The
repeated \((13)(24)) target is a negative control. Python recomputes the
formal algebra independently of the C++ search.

## Reproduce

From the repository root, with Python 3 and a C++17 compiler:

```sh
python3 -I -B research/s4-mixed-v4-double-transposition-seed0cdbb4/verify.py
```

Expected prefix:

```text
PASS_S4_MIXED_V4_DOUBLE_TRANSPOSITION
```

`VERIFY.json` registers this command. The local replay was run with CPython
3.14.7 and GCC 16.2.1. Python 3.12 was unavailable locally. Exact base pins,
the selected record, review and source manifest are listed in `SOURCES.json`.

## Relation to the selected bound

The current selected record remains the complex-bound conditional construction
and keeps the PR589 rational-address bit supplier. This finite nonabelian
address result has no exact simulation into that supplier and makes no paid
moment or \(\kappa\) change. It is a scoped register-model result only.

## Open next questions

Can a different generating set in (S_4) realize this same heterogeneous
target in four fully charged calls? The first step is to price the new label
set against its direct word and repeat the complete pair meet; any resulting
word still needs a source-bound supplier map before it can affect the selected
conditional bound.

## Credit

The target search, exact implementations, proof and package were prepared with
substantial OpenAI Codex assistance. PR #1333 and PR #1734 are credited as the
rank-bound and nearest group-model predecessors. No predecessor code is
imported, and no independent human review is claimed.
