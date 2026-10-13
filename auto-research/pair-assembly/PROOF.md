# Interval strips and core-aware pair assembly: conditional saving 4.986133 × 10^-5

Under OpenAI's base theorem and the retained analytic, fixed finite-alphabet
and fixed multitape interfaces, the construction below gives

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\boxed{\kappa=\frac{4986133}{10^{11}}=4.986133\times10^{-5}>2^{-15}.}
\]

The exact bit saving is 4986382/10^11. The next grid value of the bit saving
fails the exact moment test, and the next κ grid value fails the assembly.

This is **6.782% above PR #57** (4669442391/10^14), **10.092% above PR #54**
(141532521/3125000000000) and **10.849% above PR #53** (4498144/10^11). It
does not use PR #57's compiler or PR #54's clones. These compare asymptotic
exponent savings, not running times. They are conditional research claims
without independent mathematical review or formal verification.

Section "Stacking with PR #57's frame compiler" below gives a second, larger
witness, κ = 5101691/10^11, that also uses PR #57's compiler.

## What changes

Only the scalar producer DAG changes, in `pair_graph.py`, together with its
pinned carrier matching, `links-{23,25}.uses`. Everything else is PR #53's
`research/skip-strips` pipeline, which is PR #48's `research/copied-fixed`
pipeline, with constants recomputed for the new DAG.

A role is a physical scratch wire. With c additions, q designated outputs and
μ retained carrier links, the role count is R = c + q − μ. A link lets a
donor addition x = u + w continue its carrier into a later consumer t of u,
when the original envelope of x lies inside the envelope of t: the common core
of t lies inside the core of x, and the cover of x lies inside the cover of t.
So R counts the additions that cannot continue a carrier, plus q.

### 1. Interval strips

The paired-exclusion recursion (icekylinx PR #18/#36) needs, for each vertex,
every leave-one-out sum of its k strip values v_1, …, v_k. PR #53 used the
skip-prefix layout s_j = A_(j−2) + (v_(j−1) + B_(j+1)). We build every cyclic
interval of the values instead, each from an interval one item shorter:

    I(a, m) = I(a, m−1) + v_(a+m−1),   2 ≤ m ≤ k−1,

and output s_j = I(j+1, k−1), with the total I(0, k−1) + v_(k−1). The interval
I(a, m) with m < k−1 has the later consumer I(a−1, m+1) of its last item
v_(a+m−1), and its cover lies inside that consumer's cover, so it can continue
a carrier. Only the k outputs and the total stay unmatched.

This costs k(k−2)+1 additions instead of about 4k. The role count still falls,
because R counts unmatched additions. In a model of one strip, an exact integer
program over every leave-one-out circuit shows that k−1 unmatched additions is
the minimum for k ≤ 8. Skip-prefix leaves 2k−3 unmatched; intervals leave k−1
or k. Intervals are used for every strip with k ≥ 3 nonzero values; smaller
strips keep PR #53's layout. Value orders are PR #53's: reversed at the top
level, sorted by (support size, ±support) below it.

### 2. Core-aware pair assembly

For groups i < j with members (a, a2) and (b, b2), let F = far[i,j] and let
Sa, Sa2, Sb, Sb2 be the strip outputs that omit the other group. Each of the
four outputs is a sum of four pieces, for example
out[a,b] = F + Sa + Sb + e(a2,b2). PR #53 computes left(a,j) = F + Sa,
then out[a,b] = left(a,j) + (Sb + e(a2,b2)). None of those ten additions can
continue a carrier. We compute

    F+Sa, F+Sa2, F+Sb, F+Sb2,
    Y1 = (F+Sb) + Sa,      Y2 = (F+Sa) + Sb2,
    Y3 = (F+Sa2) + e(a,b2), Y4 = (F+Sb2) + e(a,b),
    out[a,b]  = e(a2,b2) + Y1,   out[a,b2] = e(a2,b) + Y2,
    out[a2,b] = Y3 + Sb,         out[a2,b2] = Y4 + Sa2.

Each F+S node then has a later consumer of its strip operand whose envelope
contains its own: the same common core and a larger cover. An exact integer
program over every assembly of these nine pieces, with their actual cores and
covers, shows that 8 unmatched additions per group pair is optimal. The cores
matter: a node such as Sa + e(a2,b2) has the two-point core {c, a2}, so a
one-point-core donor cannot continue into it. Each output needs its own
addition and at least one more addition that serves only that output, and
neither can continue a carrier, so 8 is also a lower bound for this
decomposition.

### Counts

| h | v | additions c | outputs q | matched μ | roles R | loss |
|---|---|---|---|---|---|---|
| 23 | 1771 | 62294 | 5336 | 38911 | 28719 | 506 |
| 25 | 2300 | 86595 | 6925 | 55844 | 37676 | 600 |

PR #53 had R23 = 32946 and R25 = 43409. The physical constants are
m = 575, N = 4,073,300, W = 140,924,496 (PR #53: 160,799,739) and
L = 2,226,400. The complete rank is Wm − N + L = 81,029,738,300. The deficit
N − L is unchanged.

The weighted matching is pinned in `links-{h}.uses`. `optimize_matching.py`
regenerates it from Rohan Arun's PR #44 optimizer with only the graph import
changed. Its output is not trusted: `profiles.cpp` replays every pinned link,
and `producer.py` recounts every link independently.

## Why the inherited proofs apply

The new DAG enters the inherited proofs only through properties and
quantities that `producer.py` recomputes, as for PR #41, #43, #47, #48 and #53:

- **Scalar outputs.** Every addition joins disjoint supports, every node has a
  common point, and every output is the exact leave-two-out sum or retained
  total, checked on dense global supports.
- **Carrier links.** Every pinned link lies in the admissible adjacency
  (causal order and envelope inclusion), with distinct donors and uses.
- **Physical timeline.** The full physical timeline and every dirty basis
  vector are checked in both orientations at h = 23 and 25.
- **Fixed-basis profiles.** These are recomputed from the new DAGs and pinned
  matchings: 37,728 and 51,927 distinct transition matrices; 6,026 and 7,981
  of them CRT-checked; zero modular disagreements. Exactly h full center
  cleanups appear, so the copied-center replacement applies unchanged.
- **Data corners.** These do not depend on the producer. All 4,073,300 pairs
  are replayed, and the ten primary-prime failures are recovered by exact
  rational elimination.

The integer programs explain why the links exist; correctness does not depend
on them.

## Exact arithmetic

`verify.py` uses PR #43/#48's exact logarithm and exponential enclosures:

- The moment at a_b = 4986382/10^11 is below 1; at 4986383/10^11 its exact
  lower bound exceeds 1.
- Each of the following is excluded at the new bit saving by an exact lower
  bound: the complete child lists of PR #57, #54, #53, #48, #47, #46, #44,
  #43, #42, #41 and #40, and the PR #36 baseline.
- The inherited balanced assembly passes all 47 strict conditions and seven
  margins at κ = 4986133/10^11 and fails at the next grid value. Its
  parameters are β = 1/20, h = 10^-12, a_c = 717/10^7, C1 = 1 and row stock
  p^2000.

## Stacking with PR #57's frame compiler

PR #57 (eumemic, with OpenAI Codex assistance) compiles each set of nodes that
share one original envelope as a single invertible binary map, matches
retained signals to later uses, and reclaims retired roles with paid XOR
clearing. Its compiler, `scripts/experiments/binary_frame_compiler.py`, is
included unchanged through PR #57's own commit on this branch.
`frame/frame_compile.py` feeds it the hash-pinned `pair_graph.py` instead of
PR #53's graph, exactly as PR #57's driver feeds it PR #53's graph.

The compiled words give the following role counts:

| h | roles R, this graph | roles R, compiled | shared-frame regions | retained signals | reclaimed roles |
|---|---|---|---|---|---|
| 23 | 28719 | 27918 | 52473 | 37025 | 801 |
| 25 | 37676 | 36586 | 73695 | 53194 | 1090 |

With W = 137,151,806 the stacked witness gives

\[
\kappa=\frac{5101691}{10^{11}}=5.101691\times10^{-5},
\]

with exact bit saving 5101952/10^11. This is **9.257% above PR #57** and
2.318% above the plain witness above. PR #57's own result on PR #53's graph
is 4669442391/10^14.

`frame/frame_verify.py` checks, as PR #57's verifier does:

- both serialized XOR words, replayed independently on every input and dirty
  basis vector in both orientations;
- every frame transition, reconstructed from the actual XOR word;
- all fixed-basis profiles, with bounded-minor and CRT checks;
- the exact moment, the rejection of the next bit-saving grid value, the
  exclusion of PR #53's and PR #57's networks at the new saving, all 47
  strict assembly inequalities, seven margins, and the rejection of the next
  κ grid value.

This stacked witness also depends on PR #57's compiler argument, which has
the same review status as PR #57.

## Reproduce

```sh
python3 research/pair-assembly/producer.py --work-dir /tmp/pair-assembly
python3 research/pair-assembly/verify.py
python3 research/pair-assembly/frame/frame_verify.py
python3 research/pair-assembly/optimize_matching.py --work-dir /tmp/pair-opt   # optional, needs scipy
python3 research/pair-assembly/frame/frame_compile.py                          # optional, rewrites the words
```

`producer.py --record` rewrites the JSON records. Without `--record` it checks
them against fresh regeneration. `make pair-assembly-verify` runs the first
three commands and the tests.

## Scope and attribution

This is a conditional finite certificate. It covers the same written proof
obligations as PR #43–#53: the base theorem, the residual compiler, fixed-tape
recursion, the physical meaning of carrier continuations and copied centers,
the analytic/semantic/routing/recovery interfaces and eventual thresholds.
None of these are re-proved here. There is no formal verification or claim of
global optimality. The stacked witness additionally depends on PR #57's
compiler mechanism and its written argument.

The interval strips and core-aware pair assembly are new here, by Avi
Eisenberg with assistance from Claude (Anthropic). Everything else is
inherited, with all original notices:

- Avi Eisenberg PR #53: skip-prefix strips and this pipeline's adaptation.
- eumemic PR #57: the joint frame compiler, used unchanged for the stacked
  witness.
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
