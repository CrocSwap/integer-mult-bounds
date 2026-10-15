# The MAS edge form of Theorem B2 (iii) is false: two exact counterexamples

**Scoped negative result; no kappa, supplier, certificate or frontier claim.** The
selected record, both suppliers and `upstream/` are unchanged.

This package answers the open next question 1 of the CR2/B2 audit
([PR 2293](https://github.com/CrocSwap/integer-mult-bounds/pull/2293)), itself the
follow-up of **item 2** of the open independent-check request
[discussion comment 18934590](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590):
does the *edge* reading of `MAS(W[F])` hold, that is

```text
cost(B) >= v - |H| - |F| + masE
```

for every rank-3 decoder configuration and every admissible pairing `B`, where
`masE` is the largest acyclic edge subset of the wild digraph `W[F]`? The printed
proof of [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162)
(Theorem B2 (iii)) yields only the *vertex* form with `masV` (PR 2293 finding 4).

**Answer: no.** The edge form is false. Two exact counterexamples are given
below (five and six lines, all full support). The vertex form survives every
instance of this package's domain. The model, statements and license are
DreamingOfClouds's; this package imports no predecessor implementation.

## Source pins

| Item | Pin |
|---|---|
| Base main | `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` |
| Audited source | [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162) head `113a718265c62aec301c5695f4bfb9c421bef7ab`, `research/char2-jets/README.md` (25888 bytes, SHA-256 `60beed587a355b6b04e61053fc123fb8ebe5d0d75d9dbd065f24138c55a2e437`) |
| Predecessor audit | [PR 2293](https://github.com/CrocSwap/integer-mult-bounds/pull/2293) head `6bc48613ed1c71e5d2e88994235e9e8629129b9c`, `research/cr2-b2-audit-seed4f435ab7/` |

The predecessor files are PR-head-only (not in the base tree), so they are pinned
here and in `TASK.json` by head hash rather than in `SOURCES.json`, which resolves
blobs at the base commit. The verifier is self-contained.

## Model (PR 2162 section 1, re-derived)

A configuration is `v` lines with rational vectors `p(t), q(t)` in `Q^3`,
`p(t) . q(t) != 0`. An admissible pairing `B` is a 0/1 matrix over `F2` with unit
diagonal and `B_ts = 1` (`t != s`) only where `p(t) . q(s) = 0`.
`cost(B) = sum_j rank_F2 B[R_j, A_j]` over the three coordinate supports
(`R_j = {t : p(t)_j != 0}`, `A_j = {s : q(s)_j != 0}`). `H` is the set of harmonic
lines, `F` the lines with both supports full, `W` the wild incidences (a wild pair
forces both endpoints into `F`). `masV` is the largest `A subseteq F` with `W[A]`
acyclic (vertex count); `masE` is the largest acyclic edge subset of `W[F]`
(edge count, the literal reading of "maximum acyclic subset").

## Counterexample 1 (smallest in the declared domain): v = 5, all full support

```text
p(0) = (-1, -1,  3)    q(0) = (1, 1, 2)
p(1) = ( 1, -3,  1)    q(1) = (1, 2, 1)
p(2) = ( 3, -1, -1)    q(2) = (2, 1, 1)
p(3) = ( 1, -3,  1)    q(3) = (1, 2, 1)
p(4) = ( 3, -1, -1)    q(4) = (2, 1, 1)
```

All supports are full, so `F = {0,1,2,3,4}` and `H = {}` (`|D| = 3` on every
line). Lines 1 and 3 coincide, as do lines 2 and 4: the duplicated `q`
directions are what defeats the edge form. Exact computed data (two independent
rank implementations agree):

| Quantity | Value |
|---|---:|
| wild pairs in `W` (both directions counted) | 16 |
| admissible free pairs | 16 |
| `masV` | 2 |
| `masE` | 8 |
| vertex RHS `v - |H| - |F| + masV` | 2 |
| edge RHS `v - |H| - |F| + masE` | 8 |
| exact minimum of `cost(B)` over all `2^16` admissible `B` | 6 |

The exact minimum `6` is attained by the admissible pairing with rows
`10110, 01001, 10110, 10110, 01001` (bit `s` of row `t` is `B_ts`), recomputed by
the independent list-of-lists rank implementation. Every admissible `B` has
`cost(B) >= 6` (complete enumeration), while the edge form demands `>= 8`:
**the edge form fails with gap 2**. The vertex form holds trivially here
(`6 >= 2`).

Since all supports are full, `cost(B) = 3 rank_F2(B)` (three identical blocks).
The counterexample is therefore also a statement about ranks: an admissible
unit-diagonal `B` of rank 2 exists while `masE = 8 > 6 = 3 rank_F2(B)`.

## Counterexample 2: v = 6, all full support

`twin_q_v6#138` (same direction-class family; data frozen in the digest):
`masE = 11`, edge RHS `11`, exact minimum of `cost(B)` over all `2^22`
admissible pairings `9`. Gap 2 again. The witness is re-minimised exhaustively
and recomputed independently by `verify.py` at every run.

## Why the edge form fails, and what survives

`masE` counts forward wild edges in an acyclic order. Between two lines with the
same `q` direction every wild partner is shared, so both directions of a pair
can contribute to different edge sets while the block ranks of `B` pay for the
pair only once. The X-form of Theorem B2 (the printed proof) optimises over
acyclic *vertex* sets and is not affected; the machine-checked identity
`xbest = v - |H| - |F| + masV` holds on all 139 instances.

Two positive statements, proved in `verify.py` and the arguments below:

**P1 (complete pairs are impossible at `v >= 4` in `Q^3`).** If
`p(t) . q(s) = 0` for all `t != s` then every triple of the `q(s)` is linearly
dependent (else the `p(t)` orthogonal to that triple would be zero), so all four
or more `q`'s lie in a plane `P`; the three `q`'s of any `t` either span `P`
(then `p(t) . q(t) = 0`, contradiction) or are all proportional (then all `q`'s
are proportional and the same contradiction follows). Consequently `B = J` is
inadmissible and every admissible `B` at `v >= 4` all-full has
`rank_F2(B) >= 2`. This is machine-checked on every all-full instance with
`v >= 4` in the domain (`p1_no_complete_pairs_v_ge_4`).

**P2 (the edge form holds for all-full `v <= 4`).** For all-full configurations
`H = {}`, `cost(B) = 3 rank_F2(B)` and `masE <= v(v-1)/2`. At `v <= 3`:
`cost(B) >= 3 >= masE`. At `v = 4`: `rank_F2(B) >= 2` by P1, so
`cost(B) >= 6 >= masE`. So the edge form is true exactly on the small side and
fails first at `v = 5`, consistent with the search (no all-full falsifier below
`v = 5`).

**P3 (`masE` can exceed `|F|` over `Q^3`).** The hub/coplanar-`q` family
(`gen_hub`) realises `masE = 5 > 4 = |F|` at `v = 4`, with nine directed wild
edges; the direction-class family realises `masE - |F|` up to 5 in the declared
domain. So the edge form, when it holds, can demand strictly more than
`v - |H|`; it is not a weakened restatement of the no-harmonic baseline.

**Concurrent work.** While this package was being written, ROTl24 independently
falsified the same edge reading with a nine-line tripartite construction
(`cost(B) = 21 < masE = 27`) and a parametric odd-`k` family with unbounded gap
`3(k-1)(k-2)`:
[PR 2334](https://github.com/CrocSwap/integer-mult-bounds/pull/2334),
[discussion 2331](https://github.com/CrocSwap/integer-mult-bounds/discussions/2331).
Both answer PR 2293's open question 1 and were claimed independently. This
package contributes the smaller counterexample (minimum-size among
all-full-support configurations by P2), two complete minima from a second
independent engine, the 139-instance vertex-form screen, and P1/P3.

## Machine evidence

`verify.py` re-implements the model independently (exact integers, F2 bitsets,
second rank implementation, symbolic-free) and screens both readings of (iii)
smallest-instance-first over a declared deterministic domain (seed `20261015`,
entries in `{-2,-1,1,2}`, `v = 3..8`): random all-full configurations, random
mixed-support configurations, cross-product dense-3 cores, hub/coplanar-`q`
cores, and direction-class (twin-`q`) near-dense wild cores. Every instance at
`free <= 15` is minimised exhaustively, as are the first four instances up to
`free = 20` and every falsifier whatever its size; the two largest instances
(`free = 21, 22`) are screened heuristically first, and any candidate `B` is
always scored exactly.

```text
PASS_B2_EDGE_SCREEN instances=139 exact=137 heuristic_only=2 max_free=22
BOUND iii_edge: FALSIFIER v=5 free=16 mincost=6 edge_rhs=8 masE=8 name=twin_q_v5#137
BOUND iii_edge: FALSIFIER v=6 free=22 mincost=9 edge_rhs=11 masE=11 name=twin_q_v6#138
BOUND iii_vertex: no falsifier in declared domain
IDENTITY xbest=vertex_rhs: ok on 139/139
CONTROLS ok {...}
SUMMARY tight_edge=6 tight_vertex=1 masE_gt_masV=63 masE_gt_absF=31 max_masE_minus_absF=5
```

Controls (all pass, each with a failure mode it must exhibit): fixture with
analytic minimum 2; the dense three-line fixture of PR 2293 (`masE = 3 >
masV = 1`, exact minimum 3, tight for the edge form); the hub fixture
(`masE = 5 > |F| = 4`, `masV = 2`, exact minimum 6); harmonic-line
classification; a strengthened edge bound `+1` falsified on a fixture
(sensitivity); a mutated configuration changing the free-pair set (sensitivity);
the two-rank-implementation cross-check; and P1 over the domain. The summary and
an instance digest are frozen in `RECEIPT.json` and compared at every run.

**What this establishes.** In the declared domain, the edge reading of
`MAS(W[F])` in Theorem B2 (iii) is refuted by two exactly checked
configurations; the vertex reading (what the printed proof gives, PR 2293
finding 4) has no falsifier, and the identity `xbest = v - |H| - |F| + masV`
holds throughout. PR 2293's open question 1 is therefore resolved negatively:
the printed gloss should be corrected to the vertex form rather than upgraded to
the edge form.

**Not checked.** `v > 8`, entries outside `{-2..2}`, `T != 3`, Lemma VCR2,
Corollary J, Theorem T-prime, Lemma F, the split min-max of PR 2162 section 3,
target (A) itself, and any kappa/supplier implication. Two instances at
`free = 21, 22` were not exhaustively enumerated before the falsifier
confirmation step (both falsifiers were). This is a finite counterexample claim,
not an impossibility theorem for repaired edge-type bounds.

## Reproduce

From the repository root, standard library only (CPython 3.12 registered):

```sh
python3 -B research/b2-mas-edge-form-seed3609249d/verify.py
python3 scripts/research_package.py --package research/b2-mas-edge-form-seed3609249d --check-only
```

Expected: the block above, ending `RECEIPT_MATCH` (about two to five minutes;
the falsifier confirmation re-runs the `2^16` and `2^22` enumerations).

## Open next questions

1. **What is the strongest rank-aware replacement for `masE`?** The counterexamples
   suggest collapsing twin `q` directions before counting acyclic edges (both
   falsifiers come from duplicated `q` directions). Why it matters: a corrected
   edge-type term could still strengthen Theorem B2 (iii) beyond `masV`.
   First step: re-run this domain with `masE` computed on the `q`-direction
   quotient and test `cost(B) >= v - |H| - |F| + masE_quotient`. Blocked by
   nothing; a small successor screen.
2. **Is the vertex form itself attainable-tight on wild-cycle cores at larger
   `v`?** PR 2293's open question 2 stands: a violation would falsify Theorem
   B2's X-form, which no instance of either package does. First step: targeted
   `v = 8` structured cores with exact enumeration past `free = 22`.
   Blocked by the `2^free` exhaustive cost; a SAT/DRAT encoding like
   [PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206) is the
   natural next tool.

## Credit

Prepared by Aaron Wang, with help from opencode (substantial AI assistance; no
independent human review claimed). The model, the statements of Lemma CR2 and
Theorem B2 and the configuration families audited here are DreamingOfClouds's
work in [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162) /
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) /
[PR 2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125). The MAS
gap, the vertex-form identity and the 58-instance audit are Aaron Wang's in
[PR 2293](https://github.com/CrocSwap/integer-mult-bounds/pull/2293); this
package answers that audit's open question 1. Context: request items 1 and 4
were closed by [PR 2193](https://github.com/CrocSwap/integer-mult-bounds/pull/2193)
and [PR 2176](https://github.com/CrocSwap/integer-mult-bounds/pull/2176), item 3
by [PR 2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272).
New work in this package is Apache-2.0.
