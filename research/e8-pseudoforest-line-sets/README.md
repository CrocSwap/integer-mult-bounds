# A Hall obstruction in the extremal 96-line E8 complement

The particular 96-line complement proposed in open question 1 of
[DreamingOfClouds's #6854](https://github.com/CrocSwap/integer-mult-bounds/pull/6854)
has no realisation of inner dimension `8k`, over any field and for any `k >= 1`.
It contains an explicit 14-line configuration with six pair lines supported on
five gauge coordinates. The inherited Hall rank argument gives `6k <= 5k`.

This is a scoped written proof supported by an exact finite certificate of the
configuration. It answers the concrete complement case. Existence for other
96-line sets remains open here. No new kappa, word, invoice or supplier is claimed.

## Hypothesis and exact set

Use the label pattern of #6846 and #6854. For each line `T` in a set `S` of the
120 E8 root lines, let `U_T, W_T` be `k by d` matrices over a field `F`. Require
`W_S U_T^T = 0` for distinct non-orthogonal root lines and require each
`W_T U_T^T` to be invertible. The two matrices may differ. Non-orthogonality is
defined by the real root coordinates, including when `F` has characteristic 2.
This pattern is a hypothesis, not a property proved for a physical program.

Index the roots as in the pinned `p104-e8-rank8-closure/check.py`. First list the
roots `2 a e_i + 2 b e_j`, with `i < j` lexicographic and `a, b` in `(1,-1)`.
Then list the sign vectors in `(1,-1)^8` with an even number of minus signs.
Retain the first representative of each pair `r, -r`. Coordinates are doubled,
so every root has squared norm 8. Set

```text
D24 = [0,1,2,3,12,13,14,15,24,25,34,35,
       36,37,38,39,40,41,44,45,46,47,50,51]
S96 = {0,...,119} minus D24.
K   = [4,6,8,10,56,72,88,104].
```

`K` is a forced-zero clique inside `S96`. For a line `t` outside `K`, let
`A_K(t)` be the positions of the members of `K` orthogonal to `t`. Positions
are numbered 0 through 7, in the displayed order of `K`. The following lines
are also in `S96`.

| Pair line `t` | `A_K(t)` |
|---|---|
| 90 | {2,5} |
| 92 | {1,5} |
| 96 | {0,5} |
| 106 | {2,4} |
| 108 | {1,4} |
| 112 | {0,4} |

Their supports form `K_{2,3}` with parts `{4,5}` and `{0,1,2}`. Two of these
lines sharing a position are forced zero and share exactly one position.
The coordinate construction and every entry of this table are checked directly.

## Proof

The gauge and rank-sum mechanism below are due to DreamingOfClouds's #6846 and
#6854. The new step is the explicit configuration in `S96`, where the 13-line
family of #6854 is absent. No novelty is claimed for Hall's condition or the
general star-configuration method.

Suppose a realisation with `d = 8k` exists. Multiply each block row `W_T` on the
left by `(W_T U_T^T)^{-1}`. This preserves all required zeros and makes every
diagonal block `I_k`. Stack the eight gauge rows as square matrices `W_K, U_K`.
They satisfy `W_K U_K^T = I_{8k}`, so both are invertible. Replacing
`U_T` by `U_T U_K^{-1}` and `W_T` by `W_T U_K^T` preserves every pairing and
makes `U_K = W_K = I_{8k}`.

Divide the coordinates into eight blocks of width `k`. For a line `T` outside
`K`, a forced zero with the gauge line at position `c` now says both
`U_T[c] = 0` and `W_T[c] = 0`. Thus these matrices are supported on `A_K(T)`.

Let `O` be the six displayed pair lines. For each of the five used coordinates
`c`, stack the matrices `W_T[c]`, and separately `U_T[c]`, over the lines
`T` whose supports contain `c`. The product of these two stacks is block
diagonal. Its off-diagonal blocks vanish because two such lines are forced
zero and their supports meet only at `c`. It factors through `k` dimensions,
so

```text
sum over T incident to c of rank(W_T[c] U_T[c]^T) <= k.
```

For each `T` in `O`, its diagonal block is the sum of its two coordinate
products and is invertible. Rank subadditivity gives

```text
k <= sum over c in A_K(T) of rank(W_T[c] U_T[c]^T).
```

Summing over six lines and then over their five used coordinates gives
`6k <= 5k`, impossible for `k >= 1`. Restriction of a realisation on `S96`
to `K union O` would give the forbidden realisation. This proves the claim.

## Finite geometry and controls

The verifier enumerates all **192** forced-zero eight-cliques contained in
`S96`. At each gauge, the pair-line graph of `S96` is exactly `K_{4,4}`.
In particular it contains `K_{2,3}`, but no `K_4` minus an edge. Every 13-line
witness of #6854 consists of a gauge plus pair lines forming `K_4` minus an
edge. Thus this census also explains why that family misses `S96`.

For the displayed `K_{2,3}`, the verifier enumerates all 64 subsets of its six
edges and searches at most 64 endpoint assignments per subset. Exactly the 63 proper
subsets admit distinct serving coordinates. Giving each pair line the unit
vector at its serving coordinate and each gauge line its own unit vector
produces `U = W` with unit diagonal and the required zeros over the integers.
The checker multiplies these vectors exactly. Tensoring with `I_k` gives a
realisation in dimension `8k` over every field for each such proper subset.
Consequently the displayed obstruction disappears after removing any one of
its six pair lines while retaining `K`. No minimum size over all obstructions
is claimed.

This endpoint test has the standard pseudoforest interpretation. A simple
graph admits an injection from edges to their incident vertices exactly when
every component has at most as many edges as vertices. The 64-subset check
compares both criteria. Necessity follows by counting within a component.
For sufficiency, root each tree and assign its edges to their child vertices;
in a unicyclic component, also assign cycle edges cyclically to their heads.
The all-`k` negative claim comes from the written
rank proof, not from finite-field searches.

Three rejecting controls detect a singular diagonal, a nonzero forced-zero
pair and an incomplete `K_{4,4}` fixture.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error -X dev research/e8-pseudoforest-line-sets/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e8-pseudoforest-line-sets
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e8-pseudoforest-line-sets --check-source-history
```

Any CPython 3.12 can replace the displayed interpreter. The terminal line is

```text
PASS_E8_S96_HALL gauges=192 witness_lines=14 repair_subsets=63 no_new_kappa
```

Both registered commands run the full verifier, normally and with `-O`.
Explicit exceptions keep all checks active in both modes. The verifier reads
the predecessor's `D24` assignment as data after checking the source SHA256;
it does not execute or replay the predecessor. Exact source commits, blobs
and hashes are in [SOURCES.json](SOURCES.json).

## Limits and implementation bounds

The conclusion concerns this specific complement, not every 96-line set or
a new universal cardinality threshold. The minimum hitting set for a larger
obstruction family is not computed. No largest realisable line set is claimed.
Ranks strictly between `8k` and `9k`, other masks, physical words, prices and
the full multiplication theorem are outside the result. No Lean, Docker,
solver or selected-frontier replay is required or claimed.

The checker uses no recursion, network, subprocess, file writes or mutable
cache. Fixed dimensions bound the root construction by 240 roots and the
mask by 120 squared entries. Clique enumeration has a 2,000,000-pop limit,
a 960-entry worklist cap, depth eight and a 10,000-clique storage cap; exhaustion
fails explicitly. Endpoint matching has at most 64 choices for each of 64
subsets. Every function is shorter than 60 lines. The registered warning and
development modes provide the available Python diagnostics; no external
static analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates objects during this one-shot
checker. The fixed domains and explicit worklist/storage caps bound live data;
all data is released at process exit. Normal and optimized replays run within
these caps without leaving runtime files. A future steady-operation native
implementation would need preallocated storage to remove this deviation.

## Sources, scope and credit

The package was produced by Nick Petalas. Credit DreamingOfClouds for #6846,
the label pattern, Hall rank argument, explicit `D24` and open question in
#6854. The general window and star bounds of #6933 and open #7114 are prior
work. This package adds the explicit `S96` geometry and its concrete
14-line witness; it does not improve those general bounds. The related #7129
studies stronger bounds on other star configurations and is not used here.

The base is `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
The changed scope of `complex-rank-shape-decoder` is recorded in [TASK.json](TASK.json).
This is a side result about a possible label set, not a decoder or paid-budget
gain. The selected record is historical provenance and is unchanged.
The advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19529936)
named the 96-line question. The delivered scope is its specified complement;
no global hitting-set optimum or largest construction is supplied.
New work is Apache-2.0.

## Open next questions

1. Can another 96-line set avoid both the 13-line family and these pair-line
   Hall deficiencies? This is the unsettled part of #6854's question. First
   step: classify the 24-line hitting sets of that family and inspect one
   representative complement from each class. The classification is not
   provided here.
2. What is the largest subset of the 120 E8 lines with an `8k` realisation
   under this mask? Start with explicit candidate subsets and inspect all
   gauges they contain. Passing every pair-line Hall condition is only a
   necessary test and does not construct a realisation.
