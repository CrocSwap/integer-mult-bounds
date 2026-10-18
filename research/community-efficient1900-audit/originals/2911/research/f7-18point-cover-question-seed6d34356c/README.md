# KB3e — the 18-point cover question for `F2^7`: narrowed to an exact finite remainder (outcome=partial)

**Set-level finite result, no words enumerated. Question NOT decided: no
18-point cover of `F2^7` was constructed and no parity split was excluded.
Every counting-feasible split `(12,6)`, `(11,7)`, `(10,8)`, `(9,9)` survives
each exact layer this package builds, and each is recorded below with its
exact obstruction status. Two new PROVEN structural constraints: any
`(12,6)` or `(10,8)` cover must have a vanishing character off the all-ones
hyperplane. No new kappa; the gap `20 <= f(7) <= 24` is unchanged.**

## Object and chain of record

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943)),
a restored seven-source singleton word is universal exactly when its prefix
set `P` covers: `P + P = F2^7` — every mask of `F2^7` is a pair-sum `a + b` of
two elements of the set (self-pairs `a + a` cover mask `0`; the sumset is
translation-invariant, so WLOG `0 in S`). [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542)
by Aaron Wang (navinor) excludes length 18 and claims "No 17-point set covers
`F2^7`"; [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773)
by Aaron Wang audits it split-by-split; [PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870)
by Aaron Wang closes the recorded remainder rows `(5,1),(6,0)` with an exact
odd-coverage Fourier/Parseval identity (`696 > 504`, deficit `192`), so all
six counting-feasible 17-point splits are excluded.

This package asks the immediate successor (PR 2870's open question 1): **does
any 18-point set cover `F2^7`?** With 17-point covers excluded, `|P| = 18` is
the set-level frontier for universal words at `L = 20/22`; an 18-point cover
would keep the `L = 22` route alive and supply its needed prefix set, while
excluding 18-point covers would kill `L = 22` outright. A parity split
`S = A u B` has `A` in the even coset `E` (s points) and `B` in the odd coset
`O` (t points), `s + t = 18`; the counting-feasible splits are `(12,6)`,
`(11,7)`, `(10,8)`, `(9,9)` and their mirrors (identical by odd translation).
**Every 18-point split has `s` and `t` of equal parity — exactly the case the
PR 2870 squeeze does not reach.**

## Verdict per split (exact integers throughout)

| Split | `E_o` | PR 2870 squeeze | Parseval remainders (A, B) | Allowed per side | Deficit | Profile system | Rows after floors | Search best /128 |
|---|---:|---|---:|---:|---:|---|---:|---:|
| `(12,6)` | 8 | none (equal parity) | 1248, 696 | none (vanishing possible) | non-positive | feasible (16 `S`) | 808 | 118 |
| `(11,7)` | 13 | none (equal parity) | 1166, 798 | 21294 | -20128, -20496 | feasible (22 `S`) | 501 | 118 |
| `(10,8)` | 16 | none (equal parity) | 1080, 896 | none (vanishing possible) | non-positive | feasible (50 `S`) | 251 | 118 |
| `(9,9)` | 17 | none (equal parity) | 990, 990 | 36414 | -35424, -35424 | feasible (31 `S`, partly undecided) | 196 | 117 |

Controls: the same profile system reports `(11,6)` infeasible (reproducing PR
2870's exclusion, whose squeeze numbers `696/504/192` this package's
`squeeze_numbers` reproduces exactly) and `(10,7)` infeasible (consistent with
PR 2773's census exclusion), and accepts the split `(4,6)` of a real 10-point
cover of `F2^5` with no false contradiction.

## The four layers

**1. Reduction lemma (PROVEN).** Fix an odd mask `p` and set `D = p + B`, a
subset of `E`. Then `S = A u B` covers `F2^n` iff (i) `A + D = E` and
(ii) `(A + A) u (D + D) = E`. Checked exhaustively over all 256 subsets of
`F2^3` and on the real `F2^5` cover. Every split `(s, t)` becomes a two-set
covering problem in the even group `E =~ F2^6`.

**2. Fourier/Parseval re-derivation with tracked deficit (PROVEN bookkeeping;
no exclusion).** PR 2870's odd-coverage identity squeezes the even-cardinality
side's characters to `{0, ±2, ...}` only when `s, t` have opposite parity. At
18 points they never do, and the tracked deficits are non-positive on every
split (table above). The identity is DEMOTED as an 18-point exclusion
mechanism; PR 2870 predicted this (`E_o >= 8` there).

**3. Per-character profile system (CHECKED; two PROVEN consequences).** A
second exact layer: character parities; the odd-half identity
`f_hat(u) g_hat(u) = rho_hat(u)` with `|rho_hat(u)| <= E_o` and
`rho_hat(u) == E_o (mod 2)`; the even-half bound
`f_hat(u)^2 + g_hat(u)^2 <= s + t + 2 P - 2^n` (`P = C(s,2) + C(t,2)`);
Parseval on both sides; and the exact attainable sums of squares of
`rho` (partition square sums). Its constraints hold on every real cover of
`F2^3`/`F2^4` (exhaustive witness battery) and `F2^5`. It excludes no
18-point split, but the **no-vanishing sub-case is infeasible for `(12,6)` and
`(10,8)`** (PROVEN): e.g. for `(12,6)` a no-vanishing spectrum is forced to
24 / 8 / 31 characters of shapes `(2,2) / (2,4) / (4,2)`, giving
`sum rho^2 = 46`, which no integer `rho >= 0` of total 8 attains (attainable:
`8, 10, 12, ..., 40, 50, 64`). So any `(12,6)` or `(10,8)` cover must have at
least one character `u` off `{0, all-ones}` with `f_hat(u) = 0` or
`g_hat(u) = 0`.

**4. Pair-representation rows with census floors (CHECKED).** PR 2773's rows
`(e_ex, b_ex, c)` extended to the four splits (its byte-vendored shape/draw
primitives with a contingency-table pairing-sums replacement — the vendored
`O(m!)` pairing loop cannot run at 18-point row sizes; the replacement is
validated equal to it wherever it terminates). Floors: `floor(6..9) = 0`
(Sidon k-sets exist; PR 2773 receipts `k7 = 34,122,816`, `k9 = 17,776,640`),
`floor(10) = 3` (fresh-proven here: `k10 budget-2 = 0` walk plus excess-3
examples), `floor(11) = 5` (reproduced `k11 budget-4 = 0` walk), `floor(12) = 3`
(counting: `C(12,2) = 66 > 63`). Remainders: `(12,6)` 808 rows over 120
distinct `(e_ex, b_ex)` pairs; `(11,7)` 501/36; `(10,8)` 251/28; `(9,9)`
196/45. At 17 points two rows survived; at 18 the remainder is large — the
"small finite remainder" expectation is DEMOTED, and the exact row lists are
the finite remainder.

**5. Bounded construction search (CHECKED; scoped search failure).** The
smallest falsifying instance for "no 18-point cover exists" is one covering
set; it was searched first. Direct seeded local search at `k = 18` (200
restarts) tops out at 118/128 covered masks; the structured `(A, D)` searches
per split (60 restarts each, the one bounded pivot after the direct search
failed) top out at 118/118/118/117; a `k = 19` probe is similar. Non-vacuity:
the identical machinery finds 20-point covers in 10/10 short runs — matching
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634)'s
recorded abundance of 20-point covers and its own failure to find 19-point
covers in 200 restarts (max 124/128). A failed bounded search is evidence
about the searched domain, never an exclusion.

## Reproduce

Standard library only, CPython 3.12, from the repository root:

```sh
python3 -I -B research/f7-18point-cover-question-seed6d34356c/test_engine.py
python3 -I -B research/f7-18point-cover-question-seed6d34356c/verify.py quick
python3 -I -B research/f7-18point-cover-question-seed6d34356c/verify.py fourier
python3 -I -B research/f7-18point-cover-question-seed6d34356c/verify.py rows
python3 -I -B research/f7-18point-cover-question-seed6d34356c/verify.py search
```

Expected markers: `Ran 21 tests ... OK`, `PASS_F7_18POINT_QUICK`,
`PASS_F7_18POINT_FOURIER`, `PASS_F7_18POINT_ROWS`, `PASS_F7_18POINT_SEARCH`.
The heavy census anchors are recomputed by the byte-vendored PR 2870 driver
(resumable, per-sub-shard receipts in `ANCHOR-PROGRESS.json`, one section per
mode):

```sh
python3 -I -B research/f7-18point-cover-question-seed6d34356c/anchors.py k10b3
python3 -I -B research/f7-18point-cover-question-seed6d34356c/anchors.py k11b4
```

Observed in-session from empty receipts: `PASS_ANCHORS_K10B3 count=149990400
total_hist={'3': 149990400} shards=62` and `PASS_ANCHORS_K11B4 count=0
total_hist={} shards=62` (about 35 minutes each cold on this host).

## Recorded anchors (reproduced before any new number)

| Anchor | Value | Status here |
|---|---|---|
| PR 2542/2634 REPRO tiers | `945/31`, `10395/49`, `945945/59` (records SHA-256 match) | recomputed (PR 2773 verify.py on the byte-exact vendored engine) |
| PR 2542 length-18 census | `15,775,992` nodes, `312,064` cycles, `0` universal | recomputed (same run) |
| PR 2870 OBSTRUCTION | `parseval=696 allowed=504 deficit=192`, both parity orders | recomputed (PR 2870 verify.py/test_engine.py; again in `squeeze_numbers`) |
| PR 2773 row table | `(11,6)/(6,11)` remainder `(5,1),(6,0)` | recomputed |
| n=5 set controls | `0` nine-point covers (max 29/32), `99,200` ten-point covers | recomputed |
| PR 2773 `k10 budget-3` | `149,990,400` (every leaf at exact excess 3) | recomputed in full (fresh empty-receipt walk, 62/62 sub-shards) |
| PR 2773 `k11` levels 3-4 | `0`, `0` | recomputed in full (fresh empty-receipt walk, 62/62 sub-shards) |

`ANCHOR-REPRO.json` records commands, observed outputs and one correction: an
earlier `PASS_ANCHORS_*` print from the extracted PR 2870 package was receipt
validation (its committed receipt pre-filled all sub-shards), not a re-walk;
the anchors recorded here started from an empty receipt. The four zero shards
(`k10` budgets 0/1/2, `k11` budget 2) are receipt-validated, not re-walked;
the fresh `k10 budget-2 = 0` and `k11 budget-2 = 0` walks independently
confirm the two load-bearing zero facts.

## Scope and limitations

Set-level only inside PR943's abstract interface. Not checked: everything
word-level (the repeated-state `L = 20` word census is Nicholas Stone's
concurrent claim,
[discussion 1166 comment 18954844](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954844),
whose splits `(10,9)/(10,8),(9,9)` are WORD objects; this package's row
tables cover the `(10,8)/(9,9)` set-level part and `(10,9)` is a 19-point
object untouched here), the 19-point cover question, walk-realizability of any
cover, and any kappa, supplier, tariff or selected-frontier implication. The
profile system is a source of necessary conditions: its feasibility is never
a construction, and its step cap (reached for some `(9,9)` spectra) is
recorded as undecided, never as a proof. The gap `20 <= f(7) <= 24` is
unchanged.

## Open next questions

1. **Do 18-point covers of `F2^7` exist (is `r((C2)^7) = 20`)?** Why it
   matters: it is the deciding set-level object for the `L = 22` route (a
   cover keeps `L = 22` alive; exclusion kills it). First step: attack one
   split through the `(A, D)` reduction in `F2^6` under the forced character
   vanishings — for `(12,6)`, enumerate 6-sets `D` and solve the
   translate-hitting problem `A + D = F2^6` (`|A| = 12`) jointly with
   `(A + A) u (D + D) = F2^6`. Blocked by: the joint `(A, B)` tree growth and
   the absence of stabilizer canonical forms (PR 2773's recorded blocker).
2. **Does combining the forced vanishings with the even-half multiplicities
   exclude `(12,6)` outright?** Why it matters: it would settle a quarter of
   the question by exact integers alone. First step: add the even-half
   multiplicity constraints (`tau = A_x + B_x - 1` on `E \ {0}`) as a second
   layer to the profile system and enumerate the joint profiles. Blocked by:
   nothing structural; the solver step cap must be lifted or the lattice
   solved directly.
3. **Handoff to the concurrent `L = 20` word claim** (Nicholas Stone): the
   set-level splits `(10,8),(9,9)` of the claim admit the row remainders
   recorded here (251 and 196 rows), so neither is excluded at the set level;
   the 19-point split `(10,9)` is untouched. Blocked by: nothing; a handoff
   note.

See [NOTICE.md](NOTICE.md) for attribution and licenses,
[TASK.json](TASK.json) for the task card and scope change,
[SOURCES.json](SOURCES.json) for pins and credit,
[CERTIFICATE.json](CERTIFICATE.json) for the labelled result record, and
[ANCHOR-REPRO.json](ANCHOR-REPRO.json) for the in-session anchor
reproductions.
