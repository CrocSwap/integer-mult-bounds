# KB3j - the (4,2)/(3,3) A-vanish classes and the even-half self-sum direction of the 18-point cover question for F2^7

**Set-level finite result, no words enumerated. Outcome=partial: no class is
decided and no false kill is made.** The (12,6) A-vanish (4,2) decision walk
is validated end to end, sized honestly and run to a budget-honest partial
(29/2048 shards, 249,244,455 normalized pairs, `w_candidates = 0` on every
walked pair); (3,3) gets its complete small-space ground truth and no forced
structure; the even-half (self-sum) direction at (11,7)/(9,9) is pressed to a
complete classification of the m=3 both-odd covers and the m=4 both-even
covers, and the scale-dependent self-sum bound lift is DEMOTED with a
quantified contrast. No 18-point cover of `F2^7` is constructed. No new
kappa.

## Object and chain of record

In the PR943 prefix-walk model
([PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943), Ross
Richardson) a restored seven-source singleton word is universal exactly when
its prefix set `P` covers: `P + P = F2^7`. The 17-point question is closed
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870));
[PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) narrowed
the 18-point question to `(12,6)`, `(11,7)`, `(10,8)`, `(9,9)`;
[PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933)
classified the vanishing configurations; [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961)
fully excluded `(10,8)` and decided the three tightest classes;
[PR 3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023) killed
`(12,6)` A-vanish `(5,1)` and reduced `(4,2)`/`(3,3)` to exact walkable
forms; [PR 3034](https://github.com/CrocSwap/integer-mult-bounds/pull/3034)
demoted the parity shortcut, localized the m=5 obstruction and recorded the
remainder this package takes.

Every cited PR author was verified against current ground truth at writing
with `gh pr view NNN --json author,title`: PR
[2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870),
[2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911),
[2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933),
[2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961),
[3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023),
[3034](https://github.com/CrocSwap/integer-mult-bounds/pull/3034) are Aaron
Wang (navinor); [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691)
and [PR 2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) are
Nicholas Stone (NicholasStone); [PR 3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005)
is Nick Petalas (petalas); [PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185)
is Mister-Meeseeks.

Concurrent word-level state, recorded honestly: PR 2973 (merged) records
`22 <= f(7) <= 24` (a false-prune correction to the word-census budgets) and
PR 3005 corroborates it; PR 2973's own scope note records the set-level chain
as unaffected. This package is strictly SET-level and enumerates no words.
Under `22 <= f(7) <= 24` the 18-point question is the deciding necessary
condition for `f(7) = 22`.

## Verdict per class (exact integers)

| Split | Class | Status here | Deciding evidence |
|---|---|---|---|
| (12,6) | A-vanish (4,2) | NOT decided (walk partial) | 29/2048 shards, 249,244,455 pairs, w_candidates=0; complete walk sized ~608 core-hours |
| (12,6) | A-vanish (3,3) | NOT decided (no forced structure) | complete k=3 shape census: (3,3) class has 296,352 covers; low classes kill at (I)/(II)/(III) or (IV)-only |
| (11,7) | both-odd | NOT excluded (route c pressed) | m=3 both-odd self-sum profiles classified; self-sum-bound lift DEMOTED |
| (9,9) | both-odd | NOT excluded (route c pressed) | same; frontier unchanged (E_o=17, min sum rho^2=19) |
| (d) | construction | no 18-set found | no new search run; ceilings 118/128 (PR 3034 run), 119/128 (PR 2634 record) stand |

## (4,2): exact reduction, validated walk, budget-honest partial

PR 3023's exact reduction extends: `D1 = {d1, d1+delta}` normalizes to
`{0, 1}` (`delta = 1` under `GL(5,2)`, `d1` absorbed by global translation).
The class is EXACTLY the triples `(U, V 6-sets, W 4-set)` of `F2^5` with

```text
(a)  (U+W) u (V+D1) = F2^5
(b)  (U+D1) u (V+W) = F2^5
(c)  (U+V) u (W+D1) = F2^5
(d)  (U+U) u (V+V) u (W+W) u (D1+D1) = F2^5
```

The four lines are invariant under `(U+a, V+b, W+a+b)` (co-translation of
each line's two summands) and the mirror `U <-> V`, so `0 in U`, `0 in V`
WLOG (machine-checked, test_engine.py). Line (c) forces
`M = F2^5 \ (U+V)` into `W u (W+1)`, so `|U+V| >= 24`; per pair the complete
W search branches on the M clusters `{m, m+1}` and the requirement
translates of (a),(b). Budgets: `|U+W| >= 20`, `|V+W| >= 20`, `|U+V| >= 24`.

**Sizing (CHECKED).** A 12-U probe walked 1,216,422 pairs in 154.6 s
(7,866 pairs/s); extrapolated complete walk = 1.722e10 normalized pairs,
about 608 core-hours at the measured rate. The complete decision is far
outside one session.

**Walk (CHECKED, PARTIAL).** 29 of 2048 shards complete (per-shard receipts
with explicit `complete`/`budget_hit` flags, generous 3,600 s budgets, actual
1,411-1,583 s per shard): 2,407 U slices, 249,244,455 pairs
(`|U+V|` histogram 24:89,073,054 25:71,435,214 26:45,702,660 27:20,350,656
28:22,151,421 29:425,160 30:106,290), `w_candidates = 0` and
`covering_configs = 0` on every pair, 42,667.82 core-seconds total. Shard 1
was re-run from an emptied receipt: identical counters (the receipt-
validation trap). The zero counts are facts about walked pairs only.

**The kill shape (CHECKED; mechanism not isolated).** Every walked pair has
zero W candidates passing (a),(b),(c) - the same shape that decided (5,1)
(PR 3023: zero candidates over 3,049,492,320 pairs). The (5,1) counting
shortcut is DEMOTED for (4,2): its requirement/capacity window (26 per side
against 30, with `W = M` forced at `|M| = 5`) is tighter than (4,2)'s
(20-21 per side against 24). A structural contradiction for (4,2) is open.

**Small-space ground truth (PROVEN, complete).** k=3 halves (8-point space):
576 classes, 484 with covers, 86 pair-killed; e.g. `(2,2,2)` pair-killed,
`(2,2,3)` line-(d)-only (32 candidates, all fail (d)), `(2,2,4)` 80 covers
of 322 candidates, `(4,4,4)` 75,572 covers. k=4 halves (16-point space,
floor-surviving grid): 96 classes, 10 with covers, 79 pair-killed. The shape
is satisfiable at small scale, so the F2^5 zero counts cannot be a
broken-machinery false empty.

## (3,3): complete small-space map, no forced structure

No singleton absorption exists; the four PR 2933 L3 lines apply directly
with `0 in A0`, `0 in A1` WLOG. The complete k=3 census (64 classes,
44,166,408 normalized configurations) maps the shape: the matched `(3,3)`
class has 296,352 covers of 1,382,976 configurations; `(2,3)` and `(3,2)`
are IV-only kills (2,688 / 6,048 configurations pass (I),(II),(III), none
passes (IV)); the eight classes `(1,1)`, `(1,2)`, `(1,3)`, `(1,4)`, `(2,1)`,
`(2,2)`, `(3,1)`, `(4,1)` fail (I)/(II)/(III) outright. Exactly 10 of the 64
classes have zero covers (total covers 40,185,156). So there is no
small-instance contradiction to lift: PR 3034's "no forced structure" is
confirmed at the smallest scale and the class remains walk-ready but larger
than (4,2).

## Route (c): the even-half self-sum structure at (11,7)/(9,9)

For a reduced covering pair `(A, B)` define the even-half multiplicity
`mu(p) = [p in A+A] + [p in B+B]`, `mu2 = |(A+A) n (B+B)|`. Complete
enumerations at the two testable scales give (PROVEN):

| Scale | Split | Covers | Self-sum profile (all covers) | Self-union |
|---|---|---|---|---|
| m=3 | (5,5) | 3,136 | (8,8,8) unique | 8/8 (full) |
| m=3 | (7,7) | 64 | (8,8,8) unique | 8/8 (full) |
| m=3 | (3,5)/(5,3) | 2,688 each | (4,8,4)/(8,4,4) unique | 8/8 |
| m=3 | (3,7)/(7,3) | 448 each | (4,8,4)/(8,4,4) unique | 8/8 |
| m=3 | (5,7)/(7,5) | 448 each | (8,8,8) unique | 8/8 |
| m=4 | (2,8) | 15,360 | (2,15,1) unique | 16/16 |
| m=4 | (4,6) | 143,360 | (4,13,4) x 35,840 and (7,16,4) x 107,520; mu2=4 all | 16/16 |

The m=4 (5,5) self-obstruction (PR 3034: 4,085,760 cross-covering pairs,
self_when_cross = 0, max self-union 15/16, `|A+A| in {8,11}`) is the
contrast: at m=3 every both-odd cover has FULL self-union and full selfsums
at (5,5)/(7,7). The self-sum-bound lift is therefore DEMOTED
quantitatively - the mechanism is scale-dependent in the opposite direction
from a lift.

What survives scaling (CHECKED at both scales): `mu2` is constant per split
in every complete census here (m=3 all splits; m=4 `(2,8)` = 1, `(4,6)` = 4).
This per-split constancy of the even-half overlap is the narrowed condition
to carry to the 501/196 surviving rows (PR 2911) before lifting to m=6; it
is not proven at m=6 and no identity is claimed.

## Anchors reproduced before any new number

| Anchor | Expected | Status here |
|---|---|---|
| PR 2870 OBSTRUCTION | parseval=696 allowed=504 deficit=192 | recomputed live |
| PR 2933 CLASSIFY | 2 TIGHT, cases=6720 | recomputed live |
| PR 2961 FOURIER (7,1) | need=175 lower=239 | recomputed live |
| PR 2961 CLASS82 | checked=28,815,360 covering=0 | read back from PR 3023's pinned receipts |
| PR 2961 CLASS60 | d_checked=169,911 d_with_transversals=0 | read back from PR 3023's pinned receipts |
| PR 3023 AV51 | uv_pairs=3,049,492,320 covering=0 | read back from PR 3023's pinned receipts |
| PR 3034 m=5 table | (2,8)=15360 (4,6)=143360; (1,9)/(3,7)/(5,5)=0 with (5,5) cross=4,085,760 self=0 max_self_union=15/16 | read back (re-derived live earlier this session via PR 3034's verify.py full, PASS_KB3I_FULL seconds=267.8) |

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-av42-kb3j-b1/test_engine.py
python3 -I -B research/f7-18point-av42-kb3j-b1/verify.py quick
python3 -I -B research/f7-18point-av42-kb3j-b1/verify.py walks
```

Expected markers: `Ran 9 tests ... OK`, `PASS_KB3J_QUICK`,
`PASS_KB3J_WALKS`. The walk itself is resumable
(`run42.py av42 --shards 2048 --shard k --budget 3600`, then
`run42.py merge av42 --shards 2048`); the small censuses re-run with
`run42.py k3` (196 s) and `run42.py k4` (3,923 s) and the route-(c)
classification with `selfsum_classify.py`. Registered replay:
`python3 scripts/research_package.py --package research/f7-18point-av42-kb3j-b1 --check-only`
passes `PASS_PACKAGE_METADATA_AND_PINS`.

## Scope and limitations

Set-level only inside PR943's abstract interface. Not checked: anything
word-level (PR 2973/PR 3005 hold `22 <= f(7) <= 24`; untouched here),
walk-realizability of any cover, the (12,6) D-vanish classes
`(9,3)/(8,4)/(7,5)/(6,6)`, the surviving (10,8) classes, the 19-point
question, and any kappa, supplier or selected-frontier implication.
`(4,2)`, `(3,3)`, `(11,7)`, `(9,9)` are all undecided here; nothing in this
package excludes any of them. The (4,2) walk's zero counts cover 2,407 of
169,911 U slices (1.42%) and prove nothing beyond the walked pairs. The
route-(c) profile facts are complete at m=3/m=4 only. All arithmetic is
exact Python integers (int bitmasks); no floats are used. Frozen predecessor
packages are unchanged; the ten pinned files are byte-exact with SHA-256
pins.

## Open next questions

1. **Complete the (4,2) walk** (resume `run42.py av42` from shard 29;
   ~605 core-hours remain at the measured rate; the receipts make it
   resumable and deterministic). Why it matters: clearing (4,2) forces any
   (12,6) A-vanish cover into (3,3). Blocked by: compute only.
2. **Isolate the w_candidates=0 mechanism** at `|U+V| = 24` (`|M| = 8`: W
   must be independent with `W u (W+1) = M` exactly, at most 16 candidates).
   Why it matters: a pair-level contradiction would decide the class without
   the remaining walk. Blocked by: the (5,1) counting shape does not
   transfer; the observed kill's mechanism is not isolated.
3. **Decide or identify (3,3)** via a new reduction (no singleton
   absorption) or a cross-line multiplicity identity coupling (I)/(II) with
   (III)/(IV). Blocked by: all four line budgets are slack; no forced
   structure at any scale tested.
4. **Lift the mu2 per-split constancy** to the 501/196 surviving rows (PR
   2911) and then to m=6 as an exact even-half identity, or find where it
   breaks. Blocked by: constancy is CHECKED at two scales only; no coupling
   identity between odd-line cross-sum multiplicities and even-line
   selfsums is known.

## Credit

PR 2542/2634/2773/2870/2911/2933/2961/3023/3034 (Aaron Wang): the 17-point
exclusion chain, the search ceilings, the pair-representation rows, the
odd-coverage Fourier/Parseval identity, the (A,D) reduction and
vanishing-character restriction, the class floors, the tight-class
decisions, the (5,1) decision and its walk engine, and the KB3i remainder
(parity demotion, m=5 obstruction localization, identity frontier) this
package takes. PR 943 (Ross Richardson): the prefix-walk model. PR 1185
(Mister-Meeseeks): the pinned `f(5)=12`, `f(6)=16` record. PR 2691/2973
(Nicholas Stone) and PR 3005 (Nick Petalas): the word-level census line and
its correction (recorded state; PR 2973 leaves the set-level chain intact).
The vendored engines (`tight.py`, `cover18.py`, `vanish.py`,
`agent64_cover17.py`, `agent64_search17.py`, `anchors.py`, `parity_census.py`,
`self_obstruction.py`, `split_census.py`) are byte-exact with SHA-256 pins
and credited in `NOTICE.md`/`SOURCES.json`.
