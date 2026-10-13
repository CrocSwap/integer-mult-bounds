# Skip-prefix strips: conditional saving 4.498144 × 10^-5

Under OpenAI's base theorem and the retained analytic, fixed finite-alphabet
and fixed multitape interfaces, the construction below gives

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\boxed{\kappa=\frac{4498144}{10^{11}}=4.498144\times10^{-5}>2^{-15}.}
\]

This is about **9.21% above PR #48** (411862541/10^13). The exact bit saving
is 4498347/10^11; the next grid value fails the same exact test, and the
next κ grid value fails the assembly. These compare asymptotic exponent
savings, not running times. They are conditional research claims without
independent mathematical review or formal verification.

## What changes

Only the scalar producer DAG changes, in `skip_graph.py`, together with its
pinned carrier matching, `links-{23,25}.uses`. Everything else is PR #48's
`research/copied-fixed` pipeline, with constants recomputed for the new DAG:

- original envelope labels;
- Rohan Arun's PR #44 weighted carrier matching, pinned and replayed;
- both fixed local bases I+J, with complete CRT-checked profiles;
- copied centers;
- reversed data corners, with exact rational recovery of the ten
  primary-prime failures;
- the balanced assembly;
- the complex side.

The producer computes, in each common-point context, every leave-two-out sum
of the pair inputs. The paired-exclusion recursion (icekylinx PR #18/#36)
needs, for each vertex, its *strip* values: the vertex's star sums over all
groups except one excluded group j. That is a leave-one-out family
s_j = Σ_{i≠j} v_i over the vertex's group values v_1, …, v_k.

Earlier producers form it as s_j = A_{j-1} + B_{j+1}, with prefix sums A and
suffix sums B (PR #48 additionally reorders the values). Then the two
consumers of every prefix A_i are A_{i+1} and s_{i+1}. Their point covers are
incomparable, because A_{i+1} contains group i+1 and s_{i+1} does not. So the
second use of every prefix, and likewise of every suffix, needs a fresh role.

We use the **skip-prefix** layout

\[
 s_j = A_{j-2} + \bigl(v_{j-1} + B_{j+1}\bigr).
\]

The consumers of A_i become A_{i+1} and s_{i+2}, with
cover(A_{i+1}) ⊆ cover(s_{i+2}). The new node v_{i-1} + B_{i+1} has cover
contained in cover(B_{i-1}), the later consumer of v_{i-1}. These are the
nested envelopes, in causal rank order, that the inherited carrier matching
may join. Each join turns a fresh role into a continuation of a retained
carrier. The layout costs one more addition per strip value; the role count,
not the addition count, drives the cost.

Details of the layout:

- **Top level:** the layout runs on the reversed value list.
- **Deeper levels:** it runs on the values sorted by (support size, support),
  following PR #48's sorting idea. The support order is ascending at h=23 and
  descending at h=25. Outputs are restored to their original indices.
- **Totals:** these fold in reverse input order at h=23 (PR #48's rule) and in
  descending (support size, support) order at h=25 (PR #43/#48's rule).
- **Point order:** the global pair order is RaD / hipotures's PR #41
  alternating order.
- **Zero values:** these are omitted, and their leave-one-out value is the
  total, exactly as in the inherited code.

| h | v | additions c | outputs q | matched | roles R | loss |
|---|---|---|---|---|---|---|
| 23 | 1771 | 40329 | 5336 | 12719 | 32946 | 506 |
| 25 | 2300 | 53475 | 6925 | 16991 | 43409 | 600 |

PR #48 has R23 = 36432 and R25 = 48329.

The physical constants are m = 575, N = 4,073,300, W = 160,799,739 (PR #48:
177,530,859) and L = 2,226,400. The complete rank is Wm − N + L =
92,458,003,025. The deficit N − L is unchanged.

The weighted matching is pinned in `links-{h}.uses`. `optimize_matching.py`
regenerates it from PR #44's optimizer with only the graph import changed;
it maximizes Σ c_t t ln t over all maximum-cardinality matchings. Its output
is not trusted: `profiles.cpp` replays every pinned link. It checks that each
link lies in the admissible adjacency (causal order and envelope inclusion)
and that donors and uses are distinct. `producer.py` then recounts every link
independently.

## Why the inherited proofs apply

All of the following are checked by the inherited code on the new DAGs:

- **Scalar outputs.** Every addition joins disjoint supports, every node has a
  common point, and every output is the exact leave-two-out sum or retained
  total. The scalar identity [|S∩T|=1] + |S∩T| ≡ [S=T] (mod 2) and JLV = I are
  unchanged.
- **Physical timeline.** The full physical timeline and every dirty basis
  vector are checked in both orientations at h = 23 and 25 by
  `original_timeline.py`.
- **Fixed-basis profiles.** These are recomputed from the new DAGs and pinned
  matchings, with the inherited exactness bounds:
  - 61,461 and 82,606 distinct transition matrices;
  - 5,642 and 7,434 of them CRT-checked;
  - zero modular disagreements.

  Exactly h full center cleanups appear, so the copied-center replacement
  applies unchanged.
- **Data corners.** These do not depend on the producer. All 4,073,300 pairs
  are replayed, and the ten primary-prime failures are recovered by exact
  rational elimination. Every pair therefore uses 9 singletons + 21 + 17 + 481.

## Exact arithmetic

`verify.py` uses PR #43/#48's exact logarithm and exponential enclosures:

- The moment at a_b = 4498347/10^11 is below 1.
- Each of the following is excluded at this new bit saving by an exact lower
  bound: the complete child lists of PR #48, #47, #46, #44, #43, #42, #41 and
  #40, and the PR #36 baseline.
- The inherited balanced assembly passes all 47 strict conditions and seven
  margins at κ = 4498144/10^11. Its parameters are β = 1/20, h = 10^-12,
  a_c = 717/10^7, C1 = 1 and row stock p^2000.

## Reproduce

```sh
python3 research/skip-strips/producer.py --work-dir /tmp/skip-strips
python3 research/skip-strips/verify.py
python3 research/skip-strips/optimize_matching.py --work-dir /tmp/skip-opt   # optional, needs scipy
```

`producer.py --record` rewrites the JSON records. Without `--record` it checks
them against fresh regeneration.

## Scope and attribution

This is a conditional finite certificate. It covers the same written proof
obligations as PR #43–#48: the base theorem, the residual compiler, fixed-tape
recursion, the physical meaning of carrier continuations and copied centers,
the analytic/semantic/routing/recovery interfaces and eventual thresholds.
None of these are re-proved here, and there is no formal verification or
claim of global optimality.

The skip-prefix strip layout is new here, prepared with assistance from
Claude (Anthropic). Everything else is inherited, with all original notices:

- Chafik Boukhalfa PR #43/#46/#48: pipeline, recovery, the sorting idea and
  verification code.
- Rohan Arun PR #44: weighted matching; also PR #37/#39/#40/#42/#47.
- RaD / hipotures PR #41: alternating order and changed DAGs.
- Dominik Scholz PR #35/#38.
- James Chang PR #34.
- icekylinx PR #18/#24/#32/#36.
- Zhihao Chen PR #21/#23/#29.
- Paureel / Aurel Prosz, Swapnil Jain, Douglas Colkitt, OpenAI, and
  Harvey–van der Hoeven.

Apache-2.0.
