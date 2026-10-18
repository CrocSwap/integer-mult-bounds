# Helper-donor kernel census on the #1297/#1305/#1324 words (no new κ)

**Scoped negative result.** The census uses #1297's two local words, which #1305, #1324 and #1319's T74 exact fill use byte-identically. #1305 and #1324 were later withdrawn by their author, because their idle overlays move axes across Z4 families that the retained recipes fix. On these words, neither the #1274/#1297 two-shock helper-donor family nor exact re-timing of early reads improves the frames. The surrogate optimum is certified, and revision 2 adds a rigorous true-moment bound: no candidate can lower the per-call moment at b by more than 1e-6 cost units. The search covers **all 306 helper pivots read before their first B write**; #1297 searched four. #1305's idle overlay is the exact optimum of the donor-star class its own verifier admits, which is now a statement about a withdrawn class. No construction is proposed and no selected-record change is suggested.

Kernels in richer families were later found on these same words: #1625's pivot-566 kernel (this author) and #1672's pivot-554 kernel. Both lie outside the two families searched here, consistent with the scope below.

Coordination: [discussion #1314](https://github.com/CrocSwap/integer-mult-bounds/discussions/1314) (claim and results).

## Starting point (validated)

These validations predate the withdrawal of #1305 and #1324; they are kept as historical records.

- **#1305 head `a96a5d95`** (jeremykothe2): its `verify.py` was run locally from a fresh checkout. It covers fresh native replays of both words, local controls, literal owner construction and strict global admission with the idle overlay. Result: `PASS_GLOBAL_MIXED_X54_IDLE_EXCHANGES_NATIVE_AND_STRICT_ADMISSION 0.001677162029073474` (127 s, macOS/Python 3.14, no Boost).
- **#1324 head `43c19465`** (jeremykothe2, posted 22:40Z while this census ran): its `verify.py` was also run locally from a fresh checkout, with fresh native replays and strict admission. Result: `PASS_GLOBAL_MIXED_X54_IDLE_EXCHANGES_NATIVE_AND_STRICT_ADMISSION 0.001677380107853623` (156 s). The #1186 pricer reproduces this κ exactly from #1324's profile: H39=1530, H42=244, H45=1477, H48=1568, H51=6555 replace #1305's idle part.
- **Independent pricing:** the #1186 `kappa.kappa(H, 37)` pricer reproduces 0.001677162029073474 from #1305's profile, and 0.001676854978651125 (#1297) without the overlay.
- **Words:** `inputs/BASE-WORD.json.gz` (125 calls) and `inputs/EXTRA-WORD.json.gz` (208 calls) are #1297's `gauge44-word.json.gz` / `extra-word.json.gz`, which are the same blobs in #1305. `inputs/CONTROL-WORD.json.gz` is #1297's input base word, before pivots 555/567 were given kernels. Pins are in [inputs/PINS.json](inputs/PINS.json).

## Searched families and results

Pricing uses PR #1186's harness, pinned at revision 3 (head `c37dfb07`; its pricing code is revision 2's, `3855fd41`):
- the auditor's static program rules;
- an exact program-map screen;
- an unchanged derived compensation;
- recomputed cone caps, tail-mutable surrogate-optimal frames and cut equality;
- `audit_local` on every negative delta;
- per-rank weights at b = 0.001679979627113687, which is #1305's certified complex lower endpoint.

Repricing the 61 + 292 + 803 base-word candidates at #1324's endpoint, 0.001680198439292940, gives identical verdicts and profiles. `ok` means the surrogate optimum is certified: zero integer duality gap for the floored weights `floor(2^40 · lo_r(b))`. A screen rejection is exact: a dyadic map that differs modulo an odd prime differs over Q. `infeasible` means there is no legal frame assignment in the model. Both words give identical tallies.

| Family (per word) | Pivots with matches | Candidates | Neutral (`ok`, Δ = 0) | Frame-infeasible | Inexact | Gains |
|---|---:|---:|---:|---:|---:|---:|
| #1297 two-shock relation, restore at end of early cleanup (`--restore tail`, the #1297 rule) | 25 | 61 | 32 | 8 | 21 | **0** |
| Same relation, helper restored just before the pivot's first write (`--restore first`, exact by construction) | 43 | 292 | 52 | 240 | 0 | **0** |
| Exact re-timing of early reads within the target's suffix segment (single moves to three slots plus the joint move per pivot; the 152 pivots with a positive deletion price) | — | 803 | 635 | 168 | 0 | **0** |

**True-moment bound (revision 2).** The surrogate certificate alone does not establish true-moment optimality: each jump's floor rounding can hide up to one unit. Revision 2 therefore prices every candidate again with PR #1186 revision 2's interval certificate. Of the 1,438 neutral candidates (the `ok` rows above, both words), none can lower the per-call moment at b below the base word's frames by more than **1e-6 units**; one unit is 2^-40 of the per-call moment. The exact rational bounds are about 1e-11 units and are rounded up to the 1e-6 grid. Each of these candidates leaves the paid profile unchanged, so its realized true delta is exactly 0. Every verdict, delta and profile equals revision 1's evidence. `infeasible` and `inexact` rows involve no cost and need no bound.

**Positive control.** On the control word, `census.py` reproduces #1297's five hooks for each of pivots 555 and 567, including its committed donors 620 and 628 with partners 383 and 399. Every hook is priced at −11,707 surrogate units, which is H1 −3, H3 +1: the realized #1297 kernel, worth 2.616e-7 κ over 333 calls. Its true realized delta is −11,707.88 units, a certified gain, and `audit_local` passes all ten hook words.

**Deletion screen, a heuristic and not a bound.** `deletion.py` prices the word with every early read of one pivot deleted and no compensation. 152 pivots have a positive price. The largest are:

| Pivots | Surrogate price (units) | Notes |
|---|---:|---|
| 439, 444 | −67,944 | the X=439/444 slot sites of #1195's fusions |
| 438, 440 | −62,316 | |
| 230, 238, 226, 228, 231, 232, 236, 434, 436, 446 | −51,648 each | read early by two helpers and one output |
| 12 further pivots | −44,075 each | |

Under exact pricing, a −51,648 profile change (H1 −12, H2 +4, H3 −4, H4 +4 per call) would be worth +1.16e-6 κ.

This is **not** an upper bound on kernels. On the control word the uncompensated deletion of 555 or 567 is frame-infeasible, yet the exact kernels are feasible and gain. Deletion changes the map-derived constraints that compensation restores. Use the screen only to choose where richer compensations are worth attempting.

**Idle overlay of #1305 (historical: #1305 was withdrawn).** `idle_optimum.py` reruns #1305's group enumeration over 3,687 (replica, port) groups and 11,374 eligible children. Each group has at most four completely idle rank-48 non-owner children. Unlike #1305's builder, it picks axis triples by exact backtracking rather than greedily. The optimum equals #1305's selection in every group: 3,251 donors and 5,025 receivers. No size-4 group admits one donor serving three receivers, and 963 groups admit no exchange. A further idle gain therefore needed a larger class, not a better selection. #1324 supplies one: simultaneous axis reassignments inside each group, with its own operator check. Its 4-child groups reach (51,51,51,39), so this part is superseded as a frontier statement and remains a closure statement for #1305's class.

## What is and is not established

- **Established:** finite exhaustive results for the families above, on these two fixed words, in #1186's frame model, at b:
  - surrogate optimality certified;
  - true-moment gains bounded by 1e-6 units.

  Census replays are exact rational arithmetic, standard library only.
- **Not established:**
  - exact true-moment optimality: the bound is 1e-6 units, not 0, and holds at the stated b only;
  - anything about other compensation families: three or more shocks, window donors on helper readers, or cleanup-side corrections. #1625 and #1672 later found kernels in such families;
  - other words, other owner maps or hosting changes;
  - any impossibility theorem.
- **Not run, since nothing is admitted:** native replay and strict admission of candidates.
- The idle statement holds only inside `verify_idle_overlay.py`'s admitted class.

## Reproduce

Standard-library check, about 30 s. It replays every census exactly, binds every priced record to a census match, recounts all evidence against [RESULT.json](RESULT.json), runs the positive control, and checks that four failure controls are rejected:

```sh
python3 -B research/frontier1305-kernel-census/verify.py
python3 scripts/research_package.py --package research/frontier1305-kernel-census
```

**Coverage.** `verify.py` recounts and binds the stored evidence. It does not rerun the frame optimization or the interval certificates. `regenerate.py` reruns all of them; it needs PR #1186's toolkit at revision 3 (head `c37dfb07`) and checks the toolkit's pinned `MANIFEST.json` and every file it lists. With 12 workers it takes about 10 minutes. Two consecutive regenerations reproduced `evidence/` byte for byte. Against revision 1's evidence, 8 of 15 files are byte-identical. The other 7 differ only by the added bound fields: no verdict, delta or profile changed.

```sh
python3 -B research/frontier1305-kernel-census/regenerate.py \
  --toolkit <checkout of PR #1186 at c37dfb07>/research/exact-frame-toolkit --out /absolute/new/dir --workers 12 \
  [--idle-run <#1305 verify work dir> --idle-owners <#1305 package>/OWNERS.json.gz]
```

## Revision 2 (2026-10-14)

This revision answers the maintainer's review continuation point: supply a rigorous rounding or separation bound, or narrow
the optimality claim to the integer objective.

- **Rigorous bound.** Every census and re-timing candidate is re-priced with PR #1186 revision 2's interval certificate
  (`bounds.py`, `price.py`, `retime.py`). The bound and the positive control's true delta are recorded in `RESULT.json`
  (`true_moment_bound`, `tallies.intervals`, `tallies.control`), and `verify.py` checks them, with a new forged-bound control.
- **Narrowed wording.** "Exactly optimal" now reads as surrogate-optimal plus the stated true-moment bound.
- **Coverage.** The distinction between the recount (`verify.py`) and the full regeneration (`regenerate.py`) is stated.
- **Frontier text.** It records the withdrawal of #1305 and #1324.

## Revision 3 (2026-10-14)

PR #1186 revision 3 (head `c37dfb07`) made the toolkit portable. It changed only timeouts, memory readings, the worker
start method and text encoding; `frames.py` and the pricing code are unchanged. This revision follows it, so that
`regenerate.py` keeps working if #1186 merges as is.

- `regenerate.py` now pins revision 3's `MANIFEST.json`.
- `deletion.py` used the harness's private SIGALRM handler, which revision 3 replaced with `compat.deadline`. It now
  uses `deadline` and `Timeout` from the toolkit's `compat.py`.
- `verify.py` and `regenerate.py` now refuse to run under `-O`. Before, `verify.py`'s guard was itself an `assert`,
  which `-O` strips, and `regenerate.py` had none.
- A fresh regeneration with revision 3 (12 workers, about 8 minutes) reproduced all 16 evidence files byte for
  byte. No verdict, price, bound or tally changes; `RESULT.json` changes only in its toolkit pin.

## Open next questions

- **Do three-shock or window-donor relations exist for the high-screen pivots** (438/440 and the ten −51,648 pivots)? #1625's pivot-566 and #1672's pivot-554 kernels show that such richer relations do exist on these words.
  - *Why it matters:* their screens are four to five times a realized kernel. The two-shock family is now exhausted on these words.
  - *First step:* extend `census.py`'s dictionary from output-read donor pairs to windows `x += c·q … x −= c·q` on any register x, closing before the pivot's first write. Solve d as a sparse dyadic combination of at most three terms, then price with `price.py`.
  - *Blocker:* each pivot has roughly 2,500 distinct suffix vectors, so the search needs support-guided enumeration rather than all triples.
#1324 has since answered the idle question that was here: a larger simultaneous-swap class does admit (51,51,51,39) groups.

## Credit

The words, relation rule and edit format are from rohanarun's #1297 (`search_relations.py`), built on Jeremy Kothe's #1274 helper-donor kernel mechanism. Jeremy Kothe's #1305 and #1324 contribute the idle overlay compositions and strict packages, after Gonzalo-Mier's #1252 idle exchanges. The lineage also includes #1218/#1193/#1148/#1195. Prior saturation sweeps on the #1218 words are Wronskode's #1288, and the idle ceiling on #1094 is PatatePatatePatate's #1276. The pricing harness is #1186. See [NOTICE.md](NOTICE.md).

Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
