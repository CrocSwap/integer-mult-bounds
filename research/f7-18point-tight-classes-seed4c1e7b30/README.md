# KB3g - the tight classes of the 18-point cover question for `F2^7`, and the identity gap at (11,7)/(9,9)

**Set-level finite result, no words enumerated. Outcome=partial: the 18-point
question is not decided, but its three tightest classes are.** The two PR 2933
TIGHT classes of the (10,8) split, `A`-vanish `(7,1)` and `D`-vanish `(8,2)`,
and the full-sumset class `(6,0)` of (12,6) are each **PROVEN impossible** -
no cover realizes them - by an exact Fourier contradiction plus complete
enumeration of the L7-forced Sidon equality configurations. The `(11,7)/(9,9)`
identity gap is pressed with the cross-sum multiplicity identity: it yields
PROVEN new necessary conditions (`sum rho^2 >= 17` resp. `>= 19`) but no
contradiction, so those two splits' row remainders `501/196` stand. No
18-point cover was constructed; the gap `20 <= f(7) <= 24` is unchanged.

## Object and chain of record

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943))
a restored seven-source singleton word is universal exactly when its prefix
set `P` covers: `P + P = F2^7`. A parity split `S = A u B` has `A` in the even
coset `E` (s points) and `B` in the odd coset (t points); with `D = p + B`
inside `E = F2^6` the PR 2911 reduction (PROVEN there) says `S` covers iff
`A + D = E` and `(A+A) u (D+D) = E`. Record chain, all authors verified
against current ground truth with `gh pr view NNN --json author,title` at
writing: [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542),
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634),
[PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773),
[PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870),
[PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911),
[PR 2933](https://github.com/CrocSwap/integer-mult-bounds/pull/2933) by Aaron
Wang (navinor); [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691)
by Nicholas Stone (NicholasStone) is the concurrent `L = 20` WORD census -
recorded state only; this package stays strictly on the SET level. This
package executes PR 2933's open questions 1 and 3.

## Verdict per class (exact integers throughout)

| Split | Class | PR 2933 status | Verdict here | Deciding evidence |
|---|---|---|---|---|
| `(10,8)` | `A`-vanish `(7,1)` (tight 32=32) | pinned to Sidon | **PROVEN impossible** | Fourier contradiction `175 < 239`; zero Sidon 5-pairs exist |
| `(10,8)` | `D`-vanish `(8,2)` (tight 32=32) | pinned to Sidon | **PROVEN impossible** | all 28,815,360 equality configurations fail all three coverage lines |
| `(12,6)` | `A`-vanish `(6,0)` (full odd half) | pinned to full sumset | **PROVEN impossible** | no 6-set `D` of `F2^5` has any 6-set `X` with `X + D = F2^5` (all 169,911 normalized `D` walked) |
| `(11,7)` | (no vanishing possible) | row remainder 501 | narrowed: `sum rho^2 >= 17` PROVEN | cross-sum multiplicity identity; no contradiction |
| `(9,9)` | (no vanishing possible) | row remainder 196 | narrowed: `sum rho^2 >= 19` PROVEN | same identity; no contradiction |

Surviving after this package: `(12,6)` `A`-vanish `(5,1)(4,2)(3,3)` and
`D`-vanish `(9,3)(8,4)(7,5)(6,6)`; `(10,8)` `A`-vanish `(6,2)(5,3)(4,4)` and
`D`-vanish `(7,3)(6,4)(5,5)`; `(11,7)/(9,9)` with their row remainders plus
the new multiplicity conditions.

## The (7,1) class: an exact Fourier contradiction, and empty enumeration

PR 2933's L7 (PROVEN there; the equality chain is a general pigeonhole valid
at `m = 6`) pins every cover of the class to `|A0+A1| = 25` with `|A0| =
|A1| = 5` (all 25 cross sums distinct) inside `F2^5`. Let `f = 1_A0`,
`g = 1_A1`, `h = 1_S` on `S = A0+A1` (`|S| = 25`, multiplicity exactly 1).
Fourier over `F2^5` gives `h_hat(v) = f_hat(v) g_hat(v)` for every `v`, so
Parseval gives `sum_{v != 0} h_hat^2 = 32*25 - 625 = 175` while
`sum_{v != 0} f_hat^2 = sum_{v != 0} g_hat^2 = 32*5 - 25 = 135`. Both sizes
are odd, so every `f_hat(v)` is odd and `f_hat^2 >= 1` pointwise; from
`(f_hat^2 - 1)(g_hat^2 - 1) >= 0`,

    f_hat(v)^2 g_hat(v)^2 >= f_hat(v)^2 + g_hat(v)^2 - 1   (v != 0),

whence `sum h_hat^2 >= 135 + 135 - 31 = 239 > 175`. Contradiction - the
class is empty. The `m = 4` analogue (`|A0| = 7, |A1| = 1` in `F2^3`)
computes `need = lower = 7` exactly (no contradiction), matching the 512
real covers of that analogue class in the `F2^4` control - the identity is
tight exactly where covers exist.

Independently, the complete enumeration of normalized Sidon 5-pairs (`0` in
both sets, `Delta(A0)` disjoint from `Delta(A1)`) finds **zero** pairs; the
backtracking is validated against full brute force at `m = 4`
(`5040 = 5040`), against plain inner loops on `m = 5` slices, and the
`F2^5` hill-climb tops out at `|A0+A1| = 23`. Coverage in the class is
independent of the free parameter `d1` (each H'-valued line translates by
`d1` as a whole), so there is no hidden parameter: **no (10,8) A-vanish
(7,1) cover exists**.

## The (8,2) class: 28,815,360 equality configurations, all failing

L7 pins the class to `|A0+A1| = 16` and `|D0+D1| = 16`, disjoint with union
the whole odd half. Normalizing `0` in `D0`, `0` in `D1` and `delta = 1`
(WLOG under `GL(5,2)`; half-translations preserve all four coverage lines -
machine-checked), the `A`-side is parametrized by `w` (32 values) and one
choice element per `{x, x+1}` pair inside the complement `C` of `D0+D1`
(256 choices when `C` is 1-invariant), and coverage is independent of `w`.
Complete walk: 4,287,920 normalized Sidon 4-pairs `(D0, D1)`, of which
112,560 have `C` 1-invariant; all 28,815,360 `(pair, choice)` configurations
fail **all three** translated coverage lines simultaneously
(`fail_hist = {("I","II","III"): 28815360}`), zero covers. The reduction is
validated end-to-end at `m = 4`: the four L3 lines and a DIRECT
`S + S = F2^5` cover test agree on all 4,096 analogue configurations
(512 covers accepted by both routes).

## The (6,0) class: no full-sumset pair of 6-sets exists in `F2^5`

The class forces `A0+A1 = F2^5` (36 pairs, excess 4) and `A0 + D = A1 + D =
F2^5` with `|D| = 6`. Two exact layers:

1. **Multiplicity classification (PROVEN).** For any 6-set pair `X, Y` with
   `X + Y = F2^5`, write `r = 1 + rho`, `sum rho = 4`; then
   `rho_hat(v) = f_hat(v) g_hat(v) in {0, +-4}` on `v != 0` (both Walsh
   values even, product bounded by `sum rho = 4`), and `|V22| =
   2 sum rho^2 - 1` with `V22 = {v != 0: |f_hat| = |g_hat| = 2}`. Exactly
   two multiplicity patterns survive the Walsh constraints: `rho = 2+2` on
   two points, and `rho = 1+1+1+1` on an affine 2-flat
   `{p1, p2, p3, p1+p2+p3}`; the patterns `4 delta_p`, `3+1` and `2+1+1`
   are PROVEN dead (`2^{5-r} - 1` is never 11; `+-2` occurs for `3+1`;
   Parseval forces `156 = 124 + (36a+16b)` with `|Vf| = 0` for `4 delta_p`).
2. **Complete transversal walk (PROVEN).** `X + D = F2^5` says `X` hits all
   32 translates of `D`. Normalizing `0` in `D` and `0` in `A1` (the class
   forces `D1` empty), all 169,911 normalized 6-sets `D` were walked with a
   complete branch-on-uncovered search: **every** `D` has zero 6-set
   transversals. Hence lines (I'')/(II'') are unsatisfiable and **no
   (12,6) A-vanish (6,0) cover exists**. Positive control: the same search
   recovers real transversals at `m = 3` (4+2 pairs); a miniature cross-check
   finds no 3+3 full pair in `F2^3` either (all 3,136 pairs scanned).

## The identity gap at (11,7)/(9,9): pressed, not cut

One bounded pivot on the named next identity (cross-sum multiplicities; the
vanishing route is vacuous there by PR 2933's L2). With `A` an `s`-set and
`D` a `t`-set covering `A + D = E = F2^6`, `r = 1 + rho` with
`sum rho = s*t - 64`; both `s, t` odd make both Walsh transforms odd, so the
same pointwise inequality yields the exact necessary condition

    64 sum rho^2 - (s*t - 64)^2 >= (64 s - s^2) + (64 t - t^2) - 63.

At (11,7): `sum rho^2 >= 17` (excess 13); at (9,9): `sum rho^2 >= 19`
(excess 17). Both bounds are attainable by integer multiplicity patterns, so
the identity does **not** contradict coverage: it is **DEMOTED** as an
exclusion mechanism for these splits (the excess 13 resp. 17 is too large for
the rigidity that killed (7,1)). What it does give is PROVEN new necessary
conditions: the all-ones excess pattern is impossible on both splits, and at
(11,7) also the single-double pattern `(2, 1^11)`. The identity is validated
positively on every odd-odd-split cover of `F2^4` (soundness). The row
remainders `501/196` stand.

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/test_engine.py
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/verify.py quick
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/verify.py novanish
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/verify.py rows
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/verify.py classes
python3 -I -B research/f7-18point-tight-classes-seed4c1e7b30/verify.py anchors
```

Expected markers: `Ran 13 tests ... OK`, `PASS_TIGHT_QUICK`,
`PASS_TIGHT_NOVANISH`, `PASS_TIGHT_ROWS`, `PASS_TIGHT_CLASSES`,
`PASS_TIGHT_ANCHORS`. The class walks are resumable with per-shard receipts
(`TIGHT-PROGRESS.json`, one section per mode; `run_tight.py class71|class82|
class60 [--shard k] [--progress F]`); `run_tight.py merge60` merges the eight
per-shard `TIGHT-C60-*.json` receipts of the class60 walk. A replay against
committed receipts validates those receipts; delete them (or pass `--progress`
to a fresh path) to re-walk. The heavy PR 2773 anchors were re-walked from
**empty** receipts (`anchors.py k10b3|k11b4`, resumable per sub-shard in
`ANCHOR-PROGRESS.json`, one section per mode).

## Recorded anchors (reproduced before any new number)

| Anchor | Value | Status here |
|---|---|---|
| PR 2870 OBSTRUCTION | `parseval=696 allowed=504 deficit=192` | recomputed (vendored `cover18.squeeze_numbers`) |
| PR 2911 SQUEEZE table | `(12,6)` `1248/696`; `(11,7)` `1166/798` vs `21294`; `(10,8)` `1080/896`; `(9,9)` `990/990` | recomputed |
| PR 2911 NOVANISH | `(12,6)`, `(10,8)` infeasible: vanishing forced | recomputed (`verify.py novanish`) |
| PR 2911 ROWS18 | `808/501/251/196` | recomputed (`verify.py rows`) |
| PR 2933 CLASSIFY lines | both `(7,1)/(8,2)` `value=32 need=32 -> survives TIGHT`; L7 `m=3 cases=6720` | recomputed (vendored `vanish.py`) |
| PR 2773 n5 control | `0` nine-point covers; `99,200` ten-point covers through `{0}` | recorded state (PR 2933 census; not re-walked here) |
| PR 2773 `k10 budget-3` | `149,990,400` | re-walked in full from empty receipts (62/62 sub-shards) |
| PR 2773 `k11` levels 3-4 | `0`, `0` | re-walked in full from empty receipts (62/62 sub-shards) |

`ANCHOR-REPRO.json` records commands and observed outputs. Receipt trap
recorded there: a resumed walk against a committed receipt silently "passes" -
the two heavy anchors here started from a missing `ANCHOR-PROGRESS.json`
(`run_anchors_all.py` printed `fresh receipts confirmed`), and the extracted
predecessor package's own `quick` mode prints receipt lines from its committed
receipts, which is receipt validation, not recomputation.

## Scope and limitations

Set-level only inside PR943's abstract interface. Not checked: anything
word-level (the repeated-state `L = 20` word census is Nicholas Stone's
concurrent claim,
[discussion 1166 comment 18954844](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954844);
this package stays strictly on the set-level object), the 19-point cover
question, walk-realizability of any cover, and any kappa, supplier, tariff or
selected-frontier implication. The surviving classes `(5,1)(4,2)(3,3)`,
`(9,3)(8,4)(7,5)(6,6)`, `(6,2)(5,3)(4,4)`, `(7,3)(6,4)(5,5)` are not decided:
their floors hold with slack and their equality structure is not pinned by
L7; no claim is made about them. The (11,7)/(9,9) multiplicity conditions are
necessary, not sufficient; no row of the PR 2911 remainder is excluded by
them. The `m = 4` analogue controls validate the reduction chain but are not
a proof at `m = 6`; the `m = 6` results rest on the exhaustive enumerations
(13 machine tests, byte-pinned engines) and the exact identities. The gap
`20 <= f(7) <= 24` is unchanged; in particular the (10,8) and (12,6) splits
remain open through their surviving classes, and (11,7)/(9,9) remain open at
their recorded row remainders.

## Open next questions

1. **Decide the surviving non-tight classes.** Why it matters: `(12,6)` and
   `(10,8)` each retain seven classes; excluding them settles two of the four
   18-point splits. First step: press L5's multi-vanishing grid (two
   characters at once, counts `(x, y, y, x)`) against the class floors at the
   product characters for `(5,1)` and `(6,2)`. Blocked by: nothing structural;
   a bounded joint enumeration.
2. **Find the sharper (11,7)/(9,9) identity.** Why it matters: those splits
   carry the other half of the 18-point question and the vanishing route is
   vacuous there. First step: combine the `sum rho^2` conditions with the even
   half `(A+A) u (D+D) = E` multiplicities (PR 2870 used only odd coverage) as
   a second layer on the 501/196 rows. Blocked by: no known coupling identity
   between the odd-line multiplicities and the even-line self-sums.
3. **Search for an 18-point cover outside the vanishing classes.** Why it
   matters: a construction keeps the `L = 22` route alive regardless of the
   exclusions. First step: seeded search over the (11,7)/(9,9) row remainder
   profiles with the new multiplicity constraints as admissibility filters.
   Blocked by: nothing structural; a failed bounded search is not an
   exclusion.

See [NOTICE.md](NOTICE.md) for attribution and licenses,
[TASK.json](TASK.json) for the task card and scope change,
[SOURCES.json](SOURCES.json) for pins and credit,
[CERTIFICATE.json](CERTIFICATE.json) for the labelled result record, and
[ANCHOR-REPRO.json](ANCHOR-REPRO.json) for the in-session reproductions.
