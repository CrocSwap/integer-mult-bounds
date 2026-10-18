# KB3h - the (12,6) A-vanish tail classes of the 18-point cover question for F2^7

**Set-level finite result, no words enumerated. Outcome=partial: class (5,1) is
PROVEN impossible by a complete exact walk; classes (4,2) and (3,3) are reduced
to exact walkable forms with exact necessary budgets but are NOT decided. No
18-point cover of `F2^7` is constructed and no split is excluded outright. No
new kappa.** The pinned record at this package's base commit carries the gap
`20 <= f(7) <= 24`; the concurrent word-level correction
([PR 2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973),
Nicholas Stone, corroborated by
[PR 3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005)) moved the
recorded gap to `22 <= f(7) <= 24` after this base commit and explicitly scopes
the set-level chain PR 2773-2961 (and hence this package) as unaffected. With
`f(7) >= 22` the 18-point question is now exactly the deciding necessary
condition for `f(7) = 22`: at `L = 22` every universal word needs at least 18
distinct prefixes and their set must cover.

## Object and chain of record

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943))
a restored seven-source singleton word is universal exactly when its prefix set
`P` covers: `P + P = F2^7`. The 17-point question is closed
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870),
all Aaron Wang). [PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911)
(Aaron Wang) narrowed the 18-point question to the splits `(12,6)`, `(11,7)`,
`(10,8)`, `(9,9)` and proved that any `(12,6)` or `(10,8)` cover must have a
vanishing character off the all-ones hyperplane. With `D = p + B` inside
`E = F2^6` (PR 2911's reduction) the pair `(A, D)` covers iff `A + D = E` and
`(A+A) union (D+D) = E`; fixing the vanishing character `psi = bit 0` (WLOG
under `GL(6,2)`), both halves `H = ker(psi)` and `H'` identify with `F2^5` and
coverage is the four PR 2933 L3 lines

```text
(I)   (A0+D0) u (A1+D1) = F2^5
(II)  (A0+D1) u (A1+D0) = F2^5
(III) (A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = F2^5
(IV)  (A0+A1) u (D0+D1) = F2^5
```

([PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933), Aaron
Wang: L2 halving, L3 half-decomposition, L4 class floors, L7 Sidon pinning).
[PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) (Aaron
Wang) decided the three tightest classes - (10,8) A-vanish (7,1), (10,8)
D-vanish (8,2), (12,6) A-vanish (6,0) - and recorded the remainder this package
takes (its open question 1): the surviving non-tight (12,6) A-vanish classes
`(5,1)`, `(4,2)`, `(3,3)` (D-half splits; PR 2933 recorded their floors
`a0*a1 + d0*d1 = 36 + x*y` as 41, 44, 45 against need 32).

Every cited PR author was verified against current ground truth at writing with
`gh pr view NNN --json author,title`: PR 2542/2634/2773/2870/2911/2933/2961 are
Aaron Wang (navinor); PR 2691 and PR 2973 are Nicholas Stone (NicholasStone).
PR 2973 is the concurrent word-level correction: the L=20 census budgets were
derived for Hamming-weight parity but applied to bit-0 state groups (a
false-prune defect, with the `n=4, L=8` word `01021323` as counterexample to
the prune), and its corrected weight-parity census excludes `L = 20` entirely,
giving `22 <= f(7) <= 24` (corroborated by the independent union-support
implementation [PR 3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005),
Nick Petalas). PR 2973's own scope note records that bit 0 remains valid in
set-level searches using actual group sizes and that the set-level chain
PR 2773-2961 is scoped separately - this package is set-level only, enumerates
no words, and is unaffected by that correction.

## Verdict per class (exact integers)

| Split | Class | PR 2933 floor | Verdict here | Deciding evidence |
|---|---|---|---|---|
| (12,6) | A-vanish (5,1) | 41 >= 32 survives | PROVEN impossible | complete walk: 0 W candidates over 3,049,492,320 normalized pairs |
| (12,6) | A-vanish (4,2) | 44 >= 32 survives | classified, NOT decided | exact reduction to W 4-sets with D1 = 0,1, budgets 20/20/24 |
| (12,6) | A-vanish (3,3) | 45 >= 32 survives | classified, NOT decided | four L3 lines direct, all budgets slack, no forced structure |

Mirrors are identical by odd translation. The D-vanish classes of (12,6)
`(9,3)`, `(8,4)`, `(7,5)`, `(6,6)` and every surviving (10,8) class are out of
scope here (PR 2961's remaining open question 1 for (10,8) untouched).

## The (5,1) decision

### Exact reduction

`D1 = {d1}` is a singleton, so the two half-translations `U = A0+d1`,
`V = A1+d1`, `W = D0+d1` absorb it (each translation preserves all four L3
lines being all of `F2^5`; machine-checked on random configurations). The class
is EXACTLY the triples `(U, V 6-sets, W 5-set)` of `F2^5` satisfying

```text
(a)  V u (U+W) = F2^5
(b)  U u (V+W) = F2^5
(c)  (U+V) u W = F2^5
(d)  (U+U) u (V+V) u (W+W) u {0} = F2^5
```

with the inverse `(A0, A1, D0, D1) = (U, V, W, 0)`. The residual symmetries
`U -> U+a, W -> W+a, V -> V+b` (independent half-translations) give WLOG
`0 in U` and `0 in V` - every solution maps bijectively to a normalized one.

### Complete walk and the exact obstruction

Line (c) forces `M = F2^5 \ (U+V)` into `W`, so `|M| <= 5` and `|U+V| >= 27`.
The walk enumerates every normalized `U` (all `C(31,5) = 169,911`) and, per `U`,
every normalized `V` with `0 in V` and `|U+V| >= 27` by a monotone excess-budget
backtracking; per pair it derives `W` candidates (`W` must contain `M` and hit
the requirement translates of (a) and (b)) and tests the survivors exactly.

| Quantity | Value |
|---|---|
| normalized U walked (0 in U) | 169,911 |
| normalized pairs (U, V) walked (0 in V, |U+V| >= 27) | 3,049,492,320 |
| pairs with |U+V| = 27 | 1,439,907,840 |
| pairs with |U+V| = 28 | 1,572,086,880 |
| pairs with |U+V| = 29 | 29,998,080 |
| pairs with |U+V| = 30 | 7,499,520 |
| W candidates passing (a) and (b) and (c) | 0 |
| covering configurations | 0 |

The exact obstruction is recorded as it occurs: for EVERY normalized pair, no
5-set `W` containing `M` satisfies lines (a) and (b) simultaneously
(`w_candidates = 0` over the whole walk), so the class is unsatisfiable before
line (d) is ever relevant. By the reduction's bijectivity this proves:

**PROVEN - no covering (A, D) exists in class (12,6) A-vanish (5,1); an
18-point cover of `F2^7` cannot have that class.**

The walk is 16 shards with per-shard receipts (`AVTAIL-AV51-0..15.json`), all
`complete=true` / `budget_hit=false`; the first launch hit its 3,000 s
per-shard budget with explicit `complete=false` on all 16 shards
(partial-as-complete avoided) and was re-walked from scratch at budget 6,000 s
(4,365-4,691 s per shard).

### Why a false empty cannot hide here

The engines were validated on the smallest instances where the answer is known
by complete brute force before the `m = 5` walk:

- `solve_w` (the per-pair W search) equals brute force over all
  `C(32,5) = 201,376` 5-sets on 14 pairs including the largest-sumset pairs of
  a sampled scan; `pair_backtrack` equals brute force over all 169,911
  normalized `V` at needs 24 and 27 on sampled `U`.
- The optimized decision engine equals the independent reference engine
  (`pair_backtrack + solve_w + lines51`) on full `U` slices in the test suite
  and on 30 randomized slices in the recorded spot recheck (all equal).
- The m=3/m=4 analogue control censuses (22 classes with the singleton-D1
  shape) agree exactly between the reduction machinery and direct `A + D = E`
  coverage tests, including cover-bearing positive controls (m=4 A=(1,1)
  D=(7,1): 512 covers by both routes; m=4 A=(2,2) D=(6,1): 11,648) next to
  floor-surviving EMPTY controls (m=4 A=(2,2) D=(5,1): 0 covers), and semantic
  failure controls: dropping line (a) or line (d) changes the census counts.

## Anchors reproduced before any new number

| Anchor | Expected | Status here |
|---|---|---|
| PR 2870 OBSTRUCTION | parseval=696 allowed=504 deficit=192 | recomputed fresh |
| PR 2911 ROWS18 | 808/501/251/196 | recomputed fresh |
| PR 2911 NOVANISH | (12,6),(10,8) infeasible | recomputed fresh |
| PR 2933 CLASSIFY | 2 lines value=32 need=32 TIGHT, cases=6720 | recomputed fresh |
| PR 2961 FOURIER (7,1) | need=175 lower=239 | recomputed fresh |
| PR 2961 CLASS82 | checked=28,815,360 covering=0 | re-walked from empty receipts |
| PR 2961 CLASS60 | d_checked=169,911 d_with_transversals=0 | re-walked from empty receipts |

Receipt-validation trap handled: the anchor walks started from missing receipt
files (`fresh receipts confirmed` printed), and two shards (CLASS60 shard 0,
CLASS82 shard 2) were re-walked from deleted receipts and compared to their
originals semantically with timing fields excluded - identical
(`ANCHOR-REPRO.json`).

## (4,2) and (3,3): exact classification, not decided

- **(4,2).** `D1 = {d1, d1+delta}` normalizes to `{0, 1}` (`delta = 1` under
  `GL(5,2)`, `d1` absorbed as in (5,1)). The class is EXACTLY the triples
  `(U, V 6-sets, W 4-set)` with `(U+W) u (V+0,1) = F2^5`,
  `(U+0,1) u (V+W) = F2^5`, `(U+V) u (W+0,1) = F2^5` and the selfsum line.
  Exact necessary budgets: `|U+W| >= 20`, `|V+W| >= 20` (excess at most 4 over
  24 pairs each), `|U+V| >= 24`. The complete walk is strictly larger than
  (5,1)'s - line (c) only forces `M` into `W union (W+1)` - and was not run in
  budget. Not decided.
- **(3,3).** No singleton absorption exists. The four L3 lines apply directly
  to `(A0, A1 6-sets, D0, D1 3-sets)` with `0 in A0, 0 in A1` (or
  `0 in D0, 0 in D1`) WLOG; every line budget is slack (line (IV): 36+9 against
  32; lines (I)/(II): 36 against 32) and no forced Sidon structure exists -
  the (6,0) rigidity `A0+A1 = F2^5` does not extend. Not decided.

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-avtail-seed010d26fa/test_engine.py
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py quick
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py novanish
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py rows
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py anchors
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py m4
python3 -I -B research/f7-18point-avtail-seed010d26fa/verify.py av51
```

Expected markers: `Ran 10 tests ... OK`, `PASS_AVTAIL_QUICK`,
`PASS_AVTAIL_NOVANISH`, `PASS_AVTAIL_ROWS`, `PASS_AVTAIL_ANCHORS`,
`PASS_AVTAIL_M4`, `PASS_AVTAIL_AV51`. The walks themselves are resumable with
per-shard receipts (`run_avtail.py class71|class82|class60|av51`, then
`run_avtail.py merge <mode>`; explicit `complete`/`budget_hit` flags, one
progress section per mode). Registered replay:
`python3 scripts/research_package.py --package research/f7-18point-avtail-seed010d26fa --check-only`
passes `PASS_PACKAGE_METADATA_AND_PINS`.

## Scope and limitations

Set-level only inside PR943's abstract interface. Not checked: anything
word-level (the corrected L=20 word census and the `L = 22` versus `L = 24`
question are Nicholas Stone's and the community's word-level work, PR
2973/PR 3005; untouched here), the 19-point cover question, walk-realizability
of any cover, and any kappa, supplier, tariff or selected-frontier implication.
(4,2)/(3,3) are not decided and no claim is made about them; their recorded
reductions and budgets are necessary conditions and exact search domains, not
exclusions. The (12,6) D-vanish classes and every surviving (10,8) class are
out of scope. No construction search was run; the recorded set-level search
ceilings stay `118/128` at `k = 18` and `124/128` at `k = 19` (PR 2634's
record as quoted by PR 2961). The word-level gap recorded at this package's
base commit is `20 <= f(7) <= 24`; the concurrent correction PR 2973
(corroborated by PR 3005) records `22 <= f(7) <= 24`, under which this
package's question is the deciding necessary condition for `f(7) = 22`.

## Open next questions

1. **Decide (12,6) A-vanish (4,2).** The exact reduced form (W 4-sets with
   `D1 = 0,1`) with budgets `|U+W| >= 20`, `|V+W| >= 20`, `|U+V| >= 24` is a
   complete finite walk; extend the (5,1) walk and shard over the normalized U
   with receipts. Why it matters: clearing (4,2) forces any (12,6) A-vanish
   cover into (3,3). Blocked by: nothing structural; a few hours of sharded
   walk.
2. **Decide or identify (12,6) A-vanish (3,3).** Either the direct normalized
   walk on `(A0, A1, D0, D1)` with the four L3 lines, or a cross-line
   multiplicity identity coupling (I)/(II) with (III)/(IV). Why it matters:
   (3,3) is the last A-vanish class after (4,2). Blocked by: all four line
   budgets are slack and no forced structure exists.
3. **Find the (11,7)/(9,9) coupling identity** (PR 2961's open question 2,
   untouched here): derive the even-half coverage identity
   `(A+A) u (D+D) = E` multiplicities for the 501/196 surviving rows and check
   it against every odd-odd-split cover of `F2^5` (a complete census exists in
   PR 2933's engine) before lifting to `m = 6`. Why it matters: those splits
   carry the other half of the 18-point question.
