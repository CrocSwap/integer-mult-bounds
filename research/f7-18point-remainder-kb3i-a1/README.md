# KB3i — the 18-point cover remainder for F2^7: (4,2)/(3,3)/(11,7)/(9,9)

**Set-level finite result, no words enumerated. Outcome = partial (narrowed
remainder). No 18-point cover of `F2^7` is constructed and no surviving split
is excluded outright; no new kappa.** The single most tempting shortcut to
excluding the two both-odd splits `(11,7)`/`(9,9)` — a parity rule forcing
both covering halves even — is **PROVEN false** by a complete census, so it
cannot be used to kill them. The m=5 "even-splits-only" ground truth is
**established and its obstruction localized per split**, and is shown to be
scale/mechanism-specific (it does not lift as a parity rule). The exact
rho²/identity frontier for `(11,7)`/`(9,9)` is reproduced and pinned.

## Object and chain of record

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943))
a restored seven-source singleton word is universal exactly when its prefix
set `P` covers: `P + P = F2^7`. The 17-point question is closed
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870)).
[PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) narrowed
the 18-point question to the splits `(12,6)`, `(11,7)`, `(10,8)`, `(9,9)` (+
mirrors) and proved any `(12,6)`/`(10,8)` cover must have a vanishing
character off the all-ones hyperplane. [PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933)
classified the vanishing configurations and recorded the class floors.
[PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) decided
the three tightest classes and fully excluded `(10,8)`.
[PR 3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023) killed
`(12,6)` A-vanish `(5,1)` and recorded the remainder this package takes:
**(12,6) A-vanish (4,2) and (3,3), plus the both-odd splits (11,7) and (9,9)
which carry no vanishing character.** This package is strictly SET-level.

With `D = p + B` inside `E = F2^6` (PR 2911's reduction) the pair `(A, D)`
covers iff `A + D = E` and `(A+A) u (D+D) = E`. Both halves of `A`, `D`
identify with `F2^5` and coverage is the four PR 2933 L3 lines. Every split
`(s,t)` of 18 has `s` and `t` of equal parity (18 is even), which is exactly
the case the PR 2870 squeeze does not reach (its hypothesis is opposite
parity). `(12,6)` and `(10,8)` are both-even; `(11,7)` and `(9,9)` are
both-odd, and PR 2933 proved both-odd splits carry no vanishing character — so
the Fourier/odd-coverage route that killed the other splits is closed to them.

Record chain authors, all verified against current ground truth with
`gh pr view NNN --json author,title` at writing: PR 2542/2634/2773/2870/2911/
2933/2961/3023 are Aaron Wang (navinor); [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691)
and [PR 2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) are
Nicholas Stone (NicholasStone); [PR 3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005)
is Nick Petalas (petalas). PR 2973 (merged) and PR 3005 are the concurrent
WORD-level line (`22 <= f(7) <= 24`, a false-prune correction to the word
census budgets); PR 2973's scope note explicitly leaves the SET-level chain
PR 2773-3023 unaffected. This package is set-level only and enumerates no
words.

## Verdict per class (exact integers)

| Split | Class | PR 2933 floor | Status here | Deciding evidence |
|---|---|---|---|---|
| (12,6) | A-vanish (4,2) | 44 >= 32 | NOT decided (walk-ready) | exact reduction D1 = 0,1 under GL(5,2); budgets 20/20/24; walk too large |
| (12,6) | A-vanish (3,3) | 45 >= 32 | NOT decided (walk-ready) | four L3 lines direct; all budgets slack; no forced structure |
| (11,7) | both-odd, no vanishing char | — | NOT excluded; parity shortcut DEMOTED | both-odd covers exist at m=3 (complete census); frontier E_o = 13, min sum rho^2 = 17 |
| (9,9) | both-odd, no vanishing char | — | NOT excluded; parity shortcut DEMOTED | both-odd covers exist at m=3 (complete census); frontier E_o = 17, min sum rho^2 = 19 |

No class is decided here. The (4,2)/(3,3) reductions and budgets are necessary
conditions and exact finite search domains (PR 3023's classification,
reproduced), not exclusions.

## Route (b): the parity shortcut is PROVEN false (DEMOTED)

The cleanest way to break `(11,7)`/`(9,9)` would be a parity rule: *a
covering pair `(A,B)` of `F2^m` (i.e. `A+B = F2^m` and `(A+A) u (B+B) = F2^m`)
must have `|A|` and `|B|` both even.* Then the both-odd splits `(11,7)`/`(9,9)`
would be excluded and the 18-point question would collapse to `(12,6)`/`(10,8)`.

**This is false.** A complete enumeration of the reduced covering problem in
`F2^3` (all `2^8 x 2^8` subset pairs) finds covering pairs in every both-odd
split `(3,5)`, `(3,7)`, `(5,3)`, `(5,5)`, `(5,7)`, `(7,3)`, `(7,5)`, `(7,7)`
— for example `(5,5)` has 3136 covers and `(7,7)` has 64. So there is **no
dimension-free parity obstruction**, and none can be used to kill `(11,7)`/`(9,9)`.
(The complete m=3 census: `(3,3)` is the only small both-odd split with zero
covers; `(5,5)`, `(7,7)` are non-empty.) This is a PROVEN negative on the
shortcut, not on the splits themselves.

## The m=5 ground truth and its obstruction (route b, "why at m=5")

The recorded ground truth — *`F2^5` covers exist only in splits `(2,8)`, `(4,6)`,
`(6,4)`, `(8,2)`* — is a statement about the reduced problem in `F2^4` with
`|A| + |B| = 10`. It is **confirmed** by complete enumeration (see
`verify.py full`), and the both-odd emptiness is localized to three distinct
mechanisms:

| m=4 split | covers | why empty (both-odd) |
|---|---|---|
| (2,8) | > 0 (even) | — (witness `A=[0,1] B=[0,2,4,6,8,10,12,15]`) |
| (4,6) | > 0 (even) | — (witness `A=[0,1,2,3] B=[0,1,2,4,8,15]`) |
| (1,9) | 0 | counting: `st = 9 < 16`, so `A+B` never covers (self covers for all 183,040 pairs) |
| (3,7) | 0 | cross never covers: `st = 21 >= 16` but `A+B != F2^4` for every pair |
| (5,5) | 0 | self never covers when cross covers: all 4,085,760 cross-covering pairs have `|A+A|,|B+B|` in `{8,11}` and `|(A+A) u (B+B)| <= 15 < 16` |

So the "even-splits-only" pattern at m=5 is a genuine fact, but its mechanism
is split- and scale-specific (counting / cross / self), **not a parity rule**.
Because both-odd covers exist at m=3 and the `(5,5)` self-sum bound is
scale-dependent, the m=5 obstruction does **not** lift to a valid exclusion of
`(11,7)`/`(9,9)` at m=6. No parity or self-sum-size argument is available
there. (DEMOTED: the lift.)

## The (11,7)/(9,9) identity frontier (reproduced, quantified)

Both splits survive the rho²/identity layer; the exact remaining conditions
(PR 2961's, reproduced here) are:

| Split | odd excess E_o | even-half bound | min sum rho^2 (partition) | effective min (post PR 2961) | squeeze (opposite-parity) |
|---|---|---|---|---|---|
| (11,7) | 13 | 42 | 13 | 17 (all-ones and (2,1^11) excluded) | inapplicable (s+t even) |
| (9,9) | 17 | 34 | 17 | 19 (all-ones excluded) | inapplicable (s+t even) |

`E_o = s*t - 2^6`; the even-half bound is `max(f_hat^2 + g_hat^2)` off the
all-ones hyperplane from the self-sum half of coverage
(`s + t + 2*P - 2^7`, `P = C(s,2)+C(t,2)`). The PR 2870 Parseval squeeze uses
only odd coverage and requires opposite parity; its hypothesis fails for every
18-point split (all have `s + t = 18` even), so its deficit argument reaches no
contradiction here (`deficit < 0` on both sides). Breaking `(11,7)`/`(9,9)`
requires pushing the **even-half (self-sum) coverage** multiplicities at the
501/196 surviving rows (PR 2911) — the direction PR 2870 did not use. This is
PR 2961's open question 2, untouched by any prior PR and **not** settled here.

## Route (c): bounded construction search (no cover found)

A bounded, seeded local search (route c) finds no covering 18-set:

| search | best coverage | record ceiling |
|---|---|---|
| direct k=18 on F2^7 (3 seeds) | 118 / 128 | 119 / 128 (PR 2634) |
| reduced (12,6), (11,7), (10,8) on F2^6 | 118 / 128 | — |
| reduced (9,9) on F2^6 | 117 / 128 | — |

Seed-invariant best 118/128; no cover reached. A failed bounded search is a
scoped search failure, never an exclusion. The search ceiling is unchanged.

## Anchors reproduced before any new number

| Anchor | Expected | Status here |
|---|---|---|
| PR 2870 OBSTRUCTION | parseval=696 allowed=504 deficit=192 | recomputed fresh |
| PR 2911 ROWS18 | 808/501/251/196 | recomputed fresh |
| PR 2911 NOVANISH | (12,6),(10,8) infeasible | recomputed fresh |
| PR 2933 CLASSIFY | 2 lines value=32 need=32 TIGHT, cases=6720 | recomputed fresh |
| PR 2961 FOURIER (7,1) | need=175 lower=239 | recomputed fresh |
| PR 2961 CLASS82 | checked=28,815,360 covering=0 | read from PR 3023 receipts |
| PR 2961 CLASS60 | d_checked=169,911 d_with_transversals=0 | read from PR 3023 receipts |
| PR 3023 AV51 | u_checked=169,911 uv_pairs=3,049,492,320 covering=0 | read from PR 3023 receipts |

The light anchors are recomputed live from the byte-vendored engines; the heavy
walk anchors (CLASS82/CLASS60/AV51) are read back from PR 3023's per-shard
receipts (PR 3023 re-walked them from empty receipts; reproduced values match
exactly).

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-remainder-kb3i-a1/verify.py quick
python3 -I -B research/f7-18point-remainder-kb3i-a1/verify.py full
python3 -I -B research/f7-18point-remainder-kb3i-a1/verify.py search
```

Expected markers: `PASS_KB3I_QUICK`, `PASS_KB3I_FULL`, `PASS_KB3I_SEARCH`.
`quick` reproduces the anchors, the complete m=3 parity-demotion census and the
(11,7)/(9,9) frontier numbers in well under a second. `full` re-runs the
complete m=4 sum-10 censuses and the (5,5) self-obstruction localization
(minutes). `search` re-runs the bounded construction search. Standalone
probes: `parity_census.py m3|m4`, `split_census.py <m> <a> <b> [stop]`,
`self_obstruction.py <m> <a> <b>`, `fourier_probe.py [--full]`,
`construct_search.py`.

Registered replay: `python3 scripts/research_package.py --package
research/f7-18point-remainder-kb3i-a1 --check-only` passes
`PASS_PACKAGE_METADATA_AND_PINS`.

## Scope and limitations

Set-level only inside PR943's abstract interface. Not checked: anything
word-level (PR 2973/PR 3005's corrected word census and `L = 22` versus
`L = 24` are word-level work, untouched here), walk-realizability of any cover,
and any kappa, supplier, tariff or selected-frontier implication. **(4,2),
(3,3), (11,7), (9,9) are all undecided here**; nothing in this package excludes
any of them, and the parity-shortcut demotion is a negative result about the
*method*, not about the splits. No construction search found a cover (route c
is a scoped search failure, not an exclusion). The recorded set-level search
ceilings stay `118/128` at `k = 18` (this run) / `119/128` (PR 2634 record) and
`124/128` at `k = 19`. The word-level gap is `22 <= f(7) <= 24` (PR 2973/3005);
under it this package's question is a necessary condition for `f(7) = 22`. All
arithmetic is exact Python integers (int bitmasks); no floats are used. Frozen
predecessor packages are unchanged; the six vendored engines are byte-exact
with SHA-256 pins (see `NOTICE.md`/`SOURCES.json`).

## Open next questions

1. **Push the even-half (self-sum) coverage identity for (11,7)/(9,9)** (PR
   2961's open question 2): derive the self-sum multiplicities at the 501/196
   surviving rows and check them against every cover of `F2^5` (PR 2933's
   census) before lifting to `m = 6`. This is the one direction the PR 2870
   odd-coverage squeeze did not use. Why it matters: these two splits carry the
   other half of the 18-point question.
2. **Decide (12,6) A-vanish (4,2)** with PR 3023's recorded reduced form (W
   4-sets, `D1 = 0,1`) and budgets `|U+W| >= 20`, `|V+W| >= 20`, `|U+V| >= 24`:
   a complete sharded walk with generous per-shard budgets and per-shard
   receipts. Why it matters: clearing (4,2) forces any (12,6) A-vanish cover
   into (3,3). Blocked by: nothing structural; a few hours of sharded walk
   (strictly larger than (5,1)'s 3,049,492,320-pair walk).
3. **Decide or identify (12,6) A-vanish (3,3)** via the direct normalized walk
   or a cross-line multiplicity identity. Blocked by: all four line budgets are
   slack and no forced structure exists.
4. **Find a valid lift of the (5,5) self-sum obstruction** to (9,9): the m=4
   mechanism (`|A+A| <= 11` for cross-covering `(5,5)`) is scale-dependent and
   fails at m=3; determine the exact `m`/split threshold, if any, at which a
   self-sum-size bound forbids a both-odd self cover.

## Credit

PR 2542/2634/2773/2870/2911/2933/2961/3023 (Aaron Wang): the 17-point
exclusion chain, the KB3b search ceilings, the pair-representation rows, the
odd-coverage Fourier/Parseval identity, the (A,D) reduction and
vanishing-character restriction, the class floors, the tight-class decisions,
and the (5,1) decision whose open question 1 records the (4,2)/(3,3) remainder
this package takes. PR 943 (Ross Richardson): the prefix-walk model. PR 1185
(Mister-Meeseeks, per current ground truth): the pinned `f(5)=12`, `f(6)=16`
record. PR 2691/2973 (Nicholas
Stone) and PR 3005 (Nick Petalas): the word-level census line and its
correction (recorded state; PR 2973 leaves the set-level chain intact). The
PR 2961/2773 engines (`tight.py`, `cover18.py`, `vanish.py`,
`agent64_cover17.py`, `agent64_search17.py`, `anchors.py`) are vendored
byte-exact with SHA-256 pins and credited in `NOTICE.md`/`SOURCES.json`.
