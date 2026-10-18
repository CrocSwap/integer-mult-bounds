# Complete joint three-line sub-anchor census

**The 20 unresolved shareable patterns in PR3031 cannot be realized:** each
contains a declared zero arc with odd anchor parity. A second defect in the
legacy line action generated those inadmissible configurations. The corrected
joint census has **13,449 orbits**, with exactly **seven `box = 2` shapes**;
four are unrealizable and three are Aaron Wang's already-known explicit
realizations. No realization-search remainder survives at this three-line
mask/zero-arc boundary.

This is a finite exact classification plus a rational rank/valuation argument.
It is not a proof of general F-star, a new decoder construction, a supplier
admission, or a new kappa. In particular, `box = 2` at `v = 3` meets F-star's
threshold `floor(2v/3) = 2`.

## Assignment and exact sources

Base: canonical main `18aacb215fc3717b06be8ceb9fca62aeca0d3e99`, priority 6.
This takes the explicit joint-sound-`v=3` follow-up in
[PR3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031), head
`e75906fc4e8b9f756a9877b2e467f4e564851c7d`. That source warned about per-line
total canonicalization and left 20 shareable patterns not found in its cap.
Its separate `v=5` floor is outside this audit.

[PR2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978), head
`12eb7b832de9239a314a7cddf6c6033d618cd8f2`, supplies the audited census and the
three credited decoder witnesses. Only its exact `box_search_kj.py` and
`realize-kj-receipt.json` are retained under [predecessor/](predecessor/), with
origin paths, Git blob IDs and SHA-256 pins in [SOURCES.json](SOURCES.json).
The verifier loads only its two canonicalization definitions, using AST
extraction; it never imports or runs the historical search/dependency tree.
The new census and both exact box checkers are separately implemented here.

This is a **changed** scope from catalogue card `census-pruning-audit`, whose
F7 parity-pruning starting point already has follow-ups. The handoff-first
override and stopping rule are in [TASK-CARD.md](TASK-CARD.md) and
[TASK.json](TASK.json). Fresh entry overlap checks covered 253 open PRs and
1,858 discussion records, including replies; the sparse checkout limited local
package coverage. PR3031's warning is credited, not claimed as a new discovery.

## The exact finite domain

Each of three lines has masks `(a0(t), b0(t))` in `{0,...,7}^2` with
`tau(t) = popcount(a0(t) & b0(t)) >= 1`: **37 raw line types**. The zero-arc
set `Z` is any subset of the six directed off-diagonal pairs satisfying

```text
(t,s) in Z  =>  popcount(a0(t) & b0(s)) is even.                 (SG)
```

For a kept ordered set `S`, choose `a(t) subset a0(t)` and `b(t) subset b0(t)`.
Require `a(t).b(t) = 1` on `S` and `a(t).b(s) = 0` for every zero arc whose
source precedes its target in `S`. `box` is the largest possible `|S|`.
Full unrestricted masks give `cert_max = 3` for every `Z`: the labels
`a(t) = b(t) = e_t` work even when every off-diagonal arc is zero.

The allowed symmetry is one **global** permutation of the three shared total
coordinates and one permutation of the three lines. No independent per-line
total relabeling or source/target transposition is included.

## Two distinct quotient failures

**1. Per-line total canonicalization loses the joint domain** (PR3031's
observation, now with an exact control). Compare the triples

```text
((3,3), (3,3), (3,3))
((3,3), (3,3), (5,5)).
```

Each line separately canonicalizes to `(3,3)` in both triples. The first triple
allows all six zero arcs; the second allows only `(0,1)` and `(1,0)`. No global
total permutation identifies these triples. The scope-valid inputs built from
the ten legacy per-line representatives cover only **1,446** of the **13,449**
joint orbits, omitting **12,003**. The corrected census finds `box = 3` on all
those omitted orbits; it does not uncover another `box < 3` shape.

**2. The line action also moves edges in the wrong direction** (new audit).
The old `canon_config` uses

```python
npairs[t] = pairs[perm[t]]                # pull back line data
nZ = {(perm[t], perm[s]) for (t,s) in Z} # push forward old edges
```

These conventions disagree on three-cycles. With new line `t` meaning old line
`perm[t]`, new arc `(t,s)` must mean old arc `(perm[t],perm[s])`; equivalently,
old edges must move by the **inverse** permutation. Here is a minimal control:

| | Line pairs | Zero arc | Anchor dot product at that arc |
|---|---|---|---|
| Valid input | `((1,3),(3,1),(1,1))` | `(1,0)` | `3 . 3 = 0` |
| Legacy output | `((1,1),(1,3),(3,1))` | `(0,2)` | `1 . 1 = 1` |
| Correct output | `((1,1),(1,3),(3,1))` | `(2,1)` | `3 . 3 = 0` |

Dots in this table are over `F2`. The original data obey (SG), but their old
"canonical" output violates it. Reproducing the legacy enumeration gives its
exact **3,023** keys and **27** gap candidates. **1,370** keys violate (SG),
including **20** gap candidates. Those 20 are exactly the shareable patterns
left unresolved in PR3031. [RESULTS.json](RESULTS.json) records every affected
source-receipt index and every offending arc; this is an exact exclusion,
independent of search alphabet or cap. The other one of the original 21
not-found candidates is the already-identified rank-two obstruction below.

## Complete corrected classification

[census.py](census.py) enumerates the **9,139** multisets of three raw line
types and all their legal zero-arc subsets. It minimizes the full joint pair
data under the global action, keeping every line permutation attaining the
minimum before minimizing the arc mask. Every ordered configuration is a
permutation of one such multiset, so this covers the domain.

A separate Burnside calculation uses **ordered** triples, fixed points of all
36 group elements and cycles of their action on the six directed arcs. It does
not use the canonicalizer or multiset reduction. Its identity fixed count is
**450,028** and the sum of fixed counts is **484,164**, giving
`484164 / 36 = 13449` orbits. All 36 counts are in the receipt.

On **every** orbit, an independent definition-level checker enumerates all
local `(a,b)` label pairs with odd diagonal and all six kept orders. It agrees
with the singleton/chronological checker on all **13,449** full-kept decisions:
**13,442** have `box = 3`, and the following **seven** have `box = 2`.
All seven have **complete `Z`**, with the displayed representatives:

| `a0` | `b0` | Realizability | Credited witness diagonal `M` |
|---|---|---|---|
| `3,3,3` | `3,3,3` | Impossible | — |
| `3,3,3` | `3,3,7` | Impossible | — |
| `3,3,7` | `3,3,3` | Realized in PR2978 | `8,8,12` |
| `3,3,3` | `3,7,7` | Impossible | — |
| `3,7,7` | `3,3,3` | Realized in PR2978 | `2,12,-4` |
| `3,3,3` | `7,7,7` | Impossible | — |
| `7,7,7` | `3,3,3` | Realized in PR2978 | `-16,24,16` |

Masks `3` and `7` mean binary `011` and `111`. For each row, labels `1` on
line 0 and `2` on line 1 witness `box >= 2`. One anchor side is confined to
two bits, so `K = A B^T` has rank at most two over `F2`. Keeping all three
lines under complete `Z` would make `K` triangular with unit diagonal after
ordering, giving rank three. Thus `box <= 2` also has a short written proof.

**Why the four impossible rows have no rational decoder.** Complete `Z` and
nonzero diagonal force `M` to be diagonal of rank three. In a three-total
factorization `M = P Q^T`, every column of both `P` and `Q` must therefore
be nonzero. For each column `j`, the minimum rational 2-adic valuation
`m_j = min_t v2(P_tj)` is finite and attained, hence bit `j` occurs in some
`a0(t)`. Those four rows have `union_t a0(t) = 3`, omitting bit 2: contradiction.
This argument includes PR3031's already-settled `(3,3)^3` obstruction.

**Why the parity exclusions apply to actual decoders.** For each nondegenerate
total, let `n_j = min_s v2(Q_sj)` and `gamma = min_j(m_j+n_j)`.
Every product term has valuation at least `gamma`. Its reduction after division
by `2^gamma` is odd exactly when `a0_j(t) = b0_j(s) = 1`. Thus the reduction of
`2^-gamma M_ts` is `a0(t).b0(s)` over `F2`. In particular, `M_ts = 0` forces
(SG). Degenerate totals contribute zero. This holds for rational coefficients,
including negative valuations; no bounded integer alphabet is assumed.

The three realized rows are **not new constructions**. The verifier recomputes
their `P Q^T`, column valuations, `gamma`, anchor masks and zero arcs from
PR2978's exact integer matrices. It separately checks full-support L8 witnesses
of size three, proving `cert = 3` on those three credited examples.
The classification is of anchor/zero-arc shapes, not of every rational matrix
or of every possible `cert` value within a shape.

## Reproduce and scope of verification

Python 3.10+ standard library only, no network or solver at replay time:

```sh
python3 -B research/fstar-joint-label-census/verify.py
python3 scripts/research_package.py --package research/fstar-joint-label-census --check-only
python3.12 scripts/research_package.py --package research/fstar-joint-label-census
```

Direct replay recomputes and compares the deterministic receipt without writing
it. `--write` is the explicit regeneration option. Expected principal markers:

```text
PASS_JOINT_CENSUS ordered=450028 orbits=13449 box3=13442 box2=7 brute=13449
PASS_LEGACY_AUDIT states=3023 invalid=1370 candidates=27 invalid_candidates=20
PASS_REALIZATION_CLASSIFICATION shapes=7 realized=3 impossible=4
```

Controls include both legacy quotient failures, direct versus optimized group
actions, all 384 line/arc-mask transforms, all 36 transforms of 80 deterministic
joint states, a valid diagonal witness, rejected broken-diagonal and forward-arc
witnesses, and the passing reversed-order control. The verifier uses explicit
exceptions, so checks stay enabled under Python optimization. Source pins bind
both retained predecessor files; the historical selected record and catalogue
are provenance only.

This does **not** replay PR3031's separate `v=5` proof, larger-`v` censuses,
selected suppliers, physical costs, moments, native compilers or Lean. The
`v=3` defects and exclusions do not by themselves invalidate those separate
results. Source retention and passing metadata are distinct from independent
human review or mathematical admission.

## Open next questions

1. **Independently audit PR3031's separate `v=5` enumerator and blocking proof.**
   It uses raw types, so the two `v=3` defects alone do not refute it. Inspect
   its actual group action and small definition-level controls first. That
   source/replay is outside this package; it needs its own overlap check.
2. **Larger joint domains (`v >= 4`).** Use global coordinate relabeling and
   zero-arc/column-attainment screens before a bounded census. This would test
   a remaining box-completeness boundary; it needs a new budget and does not
   follow from the three-line classification. See [TASK.json](TASK.json).

## Credit and license

F-star, `cert(M)`, L8 labels and the cost-to-certificate implication are
DreamingOfClouds' work in
[PR1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590), with the
source's stated Claude assistance. Aaron Wang (`navinor`), with opencode
assistance, supplied the anchor/box machinery and lineage, PR2978's census and
all three realized witnesses, and PR3031's per-line-canonicalization warning,
rank-two exclusion and explicit follow-up. Their source files and attribution
are preserved. This package adds the consistent global census, independent
counts and checkers, the second line-action counterexample, and exact exclusion
of the remaining 20 patterns.

Prepared by **Arham Tahir with substantial OpenAI Codex assistance**. No
independent human or Lean review is claimed. New work and retained repository
sources are Apache-2.0; the repository [LICENSE](../../LICENSE) applies.
