# KB3f - the vanishing-character restriction pressed against the four surviving 18-point splits

**Set-level finite result, no words enumerated.  Outcome=partial: the
18-point cover question for `F2^7` is narrowed, not decided.**  PR 2911
(Aaron Wang) proved that any `(12,6)` or `(10,8)` cover must have a vanishing
character off the all-ones hyperplane.  This package classifies those
vanishing configurations exactly and tests each class against coverage of the
remaining masks: **six classes are PROVEN impossible**, the two tight classes
are pinned to exact forced Sidon structure, and for `(11,7)/(9,9)` the
restriction provably cannot press at all (no character can vanish there).
No 18-point cover was constructed and no split was excluded outright; the
gap `20 <= f(7) <= 24` is unchanged.

## Object and chain of record

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943))
a restored seven-source singleton word is universal exactly when its prefix
set `P` covers: `P + P = F2^7`.  A parity split `S = A u B` has `A` in the
even coset `E` (s points), `B` in the odd coset `O` (t points), `s + t = 18`;
with `D = p + B` inside `E = F2^6` the PR 2911 reduction (PROVEN there) says
`S` covers iff `A + D = E` and `(A+A) u (D+D) = E`.  Record chain, all
authors verified against current ground truth with `gh pr view NNN --json
author,title` at writing:
[PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870),
[PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) by
Aaron Wang (navinor); [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691)
by Nicholas Stone (NicholasStone) is the concurrent `L = 20` WORD census -
recorded state only; this package stays strictly on the SET level.

## Verdict per split (exact integers throughout)

| Split | Forced vanishing (PR 2911, reproduced here) | Vanishing classes after the floors | Verdict |
|---|---|---|---|
| `(12,6)` | yes | `A`-vanish `(6,0)(5,1)(4,2)(3,3)` survive; `D`-vanish `(12,0)(11,1)(10,2)` **PROVEN impossible**; `D`-vanish `(9,3)(8,4)(7,5)(6,6)` survive | narrowed, not excluded |
| `(11,7)` | no vanishing exists (L2) | none | restriction does not press |
| `(10,8)` | yes | `A`-vanish `(8,0)` **PROVEN impossible**; `(7,1)` tight; `(6,2)(5,3)(4,4)` survive; `D`-vanish `(10,0)(9,1)` **PROVEN impossible**; `(8,2)` tight; `(7,3)(6,4)(5,5)` survive | narrowed, not excluded |
| `(9,9)` | no vanishing exists (L2) | none | restriction does not press |

A class is (vanishing side, forced split of that side, split of the other
side) across `ker(psi)` for one nontrivial character `psi` of `E = F2^6`;
mirrors `(6,12)/(7,11)/(8,10)/(9,9)` are identical by odd translation.

## The classification (PROVEN lemmas, machine-checked)

**L2 (halving).**  `char_sum(A, psi) = 0` iff `A` splits `|A|/2 + |A|/2`
across `ker(psi)`.  So `A`-vanishing needs `s` even and forces `(s/2, s/2)`,
`D`-vanishing needs `t` even and forces `(t/2, t/2)`.  At `(11,7)` and
`(9,9)` both sides are odd: **no character can vanish**, so PR 2911's
restriction is vacuous exactly on those two splits.

**L3 (half-decomposition).**  With `H = ker(psi)`, `H' = E \ H` and the
induced splits `A = A0 u A1`, `D = D0 u D1`, coverage is equivalent to
`(A0+D0) u (A1+D1) = H`, `(A0+D1) u (A1+D0) = H'`,
`(A0+A0) u (A1+A1) u (D0+D0) u (D1+D1) = H`, `(A0+A1) u (D0+D1) = H'`.
Checked exhaustively over all `256 x 256` pairs of `F2^3` and 4,000 random
pairs of `F2^5`.

**L4 (class floors).**  Exact union-size bounds on L3's `H'` even line:
`a0*a1 + d0*d1 >= 2^(m-1) = 32` (and the three sibling floors `F2/F3/F4`
of the `H` even and both odd lines).  In character language `F1` is
`f_hat^2 + g_hat^2 <= s + t + 2*P - 2^n` and `F3+F4` is
`|f_hat*g_hat| <= E_o` - i.e. the floors re-derive PR 2911's two profile
bounds in split language; the class verdicts are their forced-split
consequences.  A class whose forced splits violate a floor is impossible:
no cover realizes it.  Six classes die this way (table above).  At the two
tight classes (`(10,8)` `A`-vanish `(7,1)` and `D`-vanish `(8,2)`) the floor
holds with equality.

**L5 (multi-vanishing structure).**  If `A` vanishes at two distinct
characters `psi1, psi2`, its counts across the four parts of the
`(ker(psi1), ker(psi2))` grid are `(x, y, y, x)` with `x + y = |A|/2`.
Exhaustive at `F2^3`.

**L7 (equality analysis).**  Whenever `a0*a1 + d0*d1 = 32` and the pair
covers, `|A0+A1| = a0*a1` and `|D0+D1| = d0*d1` (both Sidon: all cross sums
distinct) and the two cross sumsets are disjoint with union the whole odd
half.  Exhaustive at `F2^3`.  So the tight classes are pinned to exact
forced Sidon structure, e.g. `(10,8)` `D`-vanish `(8,2)`: `A1` is a pair
whose two translates of `A0` are disjoint (`A0 n (A0 + delta) = 0`), and
`D0, D1` are 4-sets forming a Sidon pair with `|D0+D1| = 16`.
The `(12,6)` `A`-vanish `(6,0)` class forces `|A0+A1| = 32` (the whole odd
half; 36 pairs, excess 4) together with `A0 + D = H` and `A1 + D = H'` full.

## Ground-truth census: which classes actually occur

Complete enumeration at the two smallest cover-bearing instances (all exact
integers; independent enumeration route - every subset resp. every 10-set,
not the predecessor's fixed-0 engine):

- **`F2^4`**: all 65,536 subsets scanned; **41,341 covers** `S + S = F2^4`;
  classified by split and vanishing type (full table in the replay log).
- **`F2^5`**: all `C(32,10) = 64,512,240` ten-sets scanned;
  **317,440 covers** total.  The covers through `{0}` number exactly
  **99,200**, reproducing PR 2773's recorded n5 control value (its engine
  fixes `0`; `99,200 * 32 / 10 = 317,440` is the un-normalized count, and
  shard 0 of this enumeration is the `{0}` slice).
  Exact split support: `(2,8)` 15,360; `(4,6)` 143,360 = 35,840 type
  `(k_A,k_D) = (12,0)` + 107,520 type `(6,6)`; `(6,4)` 143,360 (mirrored);
  `(8,2)` 15,360.  **No 10-cover of `F2^5` has split `(5,5),(3,7),(7,3)` or
  `(1,9)`**, and every cover has vanishing characters on at least one side.
- **Soundness**: across all 358,781 covers of both censuses **no cover hits
  a dead class** - the floors reject no real configuration.

## Bounded class-restricted search (CHECKED; scoped search failure)

Smallest falsifying instance first: one covering pair `(A, D)` in a surviving
class.  Seeded first-improvement local search restricted to each surviving
class (bit-0 `psi`, WLOG under `GL(6,2)`), 30 restarts each, all 16 classes:
**no cover found**; best scores `115..119` of 128 (per-class exact numbers
in the replay log), consistent with PR 2911's unrestricted best `118/128`.
Non-vacuity: the identical machinery finds `F2^5` `(4,6)` covers instantly
both free (`A=[9,12,13,14], D=[3,5,8,9,10,11]`) and inside the
census-nonempty class `A`-vanish `(2,4)`.  A failed bounded search is
evidence about the searched domain, never an exclusion.

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-vanishing-seedfc618722/test_engine.py
python3 -I -B research/f7-18point-vanishing-seedfc618722/verify.py quick
python3 -I -B research/f7-18point-vanishing-seedfc618722/verify.py novanish
python3 -I -B research/f7-18point-vanishing-seedfc618722/verify.py classify
python3 -I -B research/f7-18point-vanishing-seedfc618722/verify.py search
```

Expected markers: `Ran 14 tests ... OK`, `PASS_F7_18POINT_QUICK`,
`PASS_F7_18POINT_NOVANISH`, `PASS_F7_18POINT_CLASSIFY`,
`PASS_F7_18POINT_SEARCH`.  The heavy PR 2773 census anchors are re-walked
from empty receipts by the byte-vendored driver (per-sub-shard receipts in
`ANCHOR-PROGRESS.json`, one section per mode):

```sh
python3 -I -B research/f7-18point-vanishing-seedfc618722/anchors.py k10b3
python3 -I -B research/f7-18point-vanishing-seedfc618722/anchors.py k11b4
```

Re-invoke to continue a partial walk; `run_anchors_all.py` loops both modes
to completion.  Recorded in-session from empty receipts: `PASS_ANCHORS_K10B3
count=149990400 total_hist={'3': 149990400} shards=62` and
`PASS_ANCHORS_K11B4 count=0 total_hist={} shards=62` (see ANCHOR-REPRO.json).

## Recorded anchors (reproduced before any new number)

| Anchor | Value | Status here |
|---|---|---|
| PR 2542/2634 REPRO tiers | `945/31`, `10395/49`, `945945/59` (records SHA-256 match) | recomputed (PR 2773 verify.py on the byte-exact vendored engine) |
| PR 2542 length-18 census | `15,775,992` nodes, `312,064` cycles, `0` universal | recomputed (same run) |
| PR 2870 OBSTRUCTION | `parseval=696 allowed=504 deficit=192`, both parity orders | recomputed (PR 2870 verify.py; again in this package's `squeeze_numbers`) |
| PR 2911 SQUEEZE table | `(12,6)` `1248/696`; `(11,7)` `1166/798` vs `21294`; `(10,8)` `1080/896`; `(9,9)` `990/990` vs `36414` | recomputed (vendored `cover18.squeeze_numbers`) |
| PR 2911 NOVANISH lines | `(12,6)`,`(10,8)` infeasible: vanishing forced | recomputed (vendored `cover18.fourier_profile_feasibility`, `verify.py novanish`) |
| PR 2911 ROWS18 | `808/501/251/196` | recomputed (PR 2911 `verify.py rows`) |
| PR 2773 n5 set controls | `0` nine-point covers (max 29), `99,200` ten-point covers through `{0}` | recomputed twice (PR 2773 verify.py; independent full `C(32,10)` census here) |
| PR 2773 `k10 budget-3` | `149,990,400` | re-walked in full (fresh empty receipts, 62/62 sub-shards) |
| PR 2773 `k11` levels 3-4 | `0`, `0` | re-walked in full (fresh empty receipts, 62/62 sub-shards) |

## Scope and limitations

Set-level only inside PR943's abstract interface.  Not checked: anything
word-level (the repeated-state `L = 20` word census is Nicholas Stone's
concurrent claim,
[discussion 1166 comment 18954844](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954844);
this package stays strictly on the set-level object), the 19-point cover
question, walk-realizability of any cover, and any kappa, supplier, tariff
or selected-frontier implication.  The surviving classes are not proved
nonempty or empty: the class floors and the Sidon pinning are necessary
conditions, and the class-restricted search failures are bounded search
failures.  The tight classes' exact decision (enumerate the forced Sidon
pairs jointly with the odd-half multiplicities) is the open step.  The gap
`20 <= f(7) <= 24` is unchanged.

## Open next questions

1. **Decide the two tight classes exactly** (`(10,8)` `A`-vanish `(7,1)` and
   `D`-vanish `(8,2)`, and the full-sumset class `(12,6)` `A`-vanish
   `(6,0)`).  First step: enumerate Sidon pairs `D0, D1` of 4-sets in
   `F2^5` (`|D0+D1| = 16`) and solve the disjointness/translation conditions
   of L7 against the odd-half `A + D = E` multiplicities.  Blocked by: the
   joint pair enumeration size; no structural blocker known.
2. **Combine several vanishings (L5's grid) with the floors at their product
   characters.**  First step: enumerate the four-part counts `(x, y, y, x)`
   of surviving classes at two characters and intersect the three floor
   systems.  Blocked by: nothing structural.
3. **A different identity for `(11,7)/(9,9)`.**  The vanishing route is
   provably vacuous there (L2); the row remainders `501/196` of PR 2911 are
   untouched by this package.  Cross-sum multiplicities or the even half in
   PR 2870's language remain the named candidates.

See [NOTICE.md](NOTICE.md) for attribution and licenses,
[TASK.json](TASK.json) for the task card and scope change,
[SOURCES.json](SOURCES.json) for pins and credit,
[CERTIFICATE.json](CERTIFICATE.json) for the labelled result record, and
[ANCHOR-REPRO.json](ANCHOR-REPRO.json) for the in-session anchor
reproductions.
