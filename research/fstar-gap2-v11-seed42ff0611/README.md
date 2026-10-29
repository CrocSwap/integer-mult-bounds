# fstar-gap2-v11-seed42ff0611

**KB5i: the twelve open `tied_min` v = 11 sub-decoders settled exactly —
`gap_named = 2` EXISTS below v = 12 (no kappa, no frontier change).** Open
problem F-star of `research/root-unit-decoder-lemmas`
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance),
section 7, OPEN) asks whether `cert(M) >= floor(2v/3)` holds for every exact
3-total rational decoder `M = sum_{j<=3} p_j q_j^T`. The family-gap line
([PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901),
[PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914),
[PR 2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936), all
Aaron Wang) recorded exactly one computation-blocked cell: the TWELVE
`tied_min` v = 11 sub-decoders, where `named` was a seeded scan at Lemma MX
construction product 1,977,326,743 and `gap_named` stayed in `{0,1,2}`. This
package replaces the scan with an exact computation and settles the verdict.
**F-star itself is not proved and not refuted here.** Every claim below is
labelled PROVEN, CHECKED or DEMOTED.

## Verdict

1. **PROVEN (exact both sides): `gap_named = 2` EXISTS below v = 12 — on
   ALL 12 `tied_min` v = 11 sub-decoders** (the complete v = 11 family of the
   v = 12 fixture). `named = 9` exactly (Lemma MX construction space settled
   by the DP below, with replayed construction witnesses; `MP = 9`
   exhaustive; `CL3 = MP = 9` exactly at even tau) and `cert = 11` exactly
   (replayed ceiling witnesses of size v). Hence `gap_named = cert - named =
   2` on 12 of 12 records. **The minimal exact gap-2 instance drops from
   `tied_min` v = 12 (the PR 2901/2914 record) to `tied_min` v = 11.** PR
   2936's record excludes gap 2 on every enumerated record below v = 11 (its
   exact records at v = 7..10 and its scan lower bounds elsewhere), so v = 11
   is the minimal size; within v = 11 every sub-decoder carries the gap.
2. **CHECKED (cross-check with correction): PR 2936's stored `cert` values
   under-report on 7 of the 12 records** (stored 9 or 10; true `cert = 11`,
   replayed). The named-scan pitfall PR 2936 quantified has a cert-side
   companion: the seeded cert hill-climbs under-report too. Every stored
   value in `predecessor/pr2936/receipt-tied_min-s11-deep.json` is
   reproduced or corrected with a replayed witness in
   `data/named-v11-receipt.json`.
3. **CHECKED (exhaustive both rungs on the weak cell): `box = cert = 11`
   exactly on all 12 records.** This closes the four records PR 2936 left at
   `box, cert in {10,11}`, and every attaining witness stored here is
   box-valued. Box-completeness is **not refuted** anywhere; it is still
   **not proved**.
4. **CHECKED (new synthetic family): `box = cert` on 60 fixture-density
   `tau >= 1` instances at v = 4..6** (GL_3(Z) column transforms of both
   fixtures plus restrictions — the generator PR 2936's random sweep lacked;
   both rungs exact; 0 violations, 0 hard instances at these sizes).
5. **PROVEN (Lemma BPP obstruction is real): projection strictness at
   `tau = 0`.** On the smallest instance (the v = 2 decoder
   `P = [[1,0,1],[2,1,0]]`, `Q = [[1,0,0],[1,0,1]]`) a replayed attaining
   witness of value 2 projects to value 1 exactly because Lemma BPP condition
   (i) fails — the parity terms cannot be dropped. **CHECKED (bounded): at
   `tau >= 1` no strict projection drop was found** among 21 escaping
   witnesses at v = 3..5 (consistent with PR 2936's "no realized instance
   needs them"; not a proof that the conditions are without loss).
6. **DEMOTED (retained, no resurrection): the matched-pivot floor.** `MP = 9
   < cert = 11` on all 12 records — twelve new exact counterexamples to
   `named = MP = cert`. `MP >= floor(2v/3) = 7` holds on every record
   (evidence, not a proof). Nothing here changes PR 2914's demotion.

## The exact named computation (priority 1)

The rungs per instance (PR 2914's ladder, PR 2936's record):

| rung | label class | value | status here |
|---|---|---|---|
| `named_lo` | Lemma SG anchor + Lemma MP matched pivots | `max(MP, \lvert S_gamma\rvert)` | exact (MP exhaustive at v = 11) |
| `named` | all four named families (SG, MX repairs, MP, CL3 mixings) | max construction value | **exact here** (was: seeded scan) |
| `box` | sub-anchor pairs `a` subset of `a0(t)`, `b` subset of `b0(t)`, `K_tt = 1` | `ab_value` inside `b0` | exact (replayed ceiling witnesses) |
| `cert` | every L8 labelling | exact-completion DP (PR 2717 engine) | exact (replayed ceiling witnesses) |

The 12 sub-decoders share one shape (all lines: `pi(t) = 7`, `a0(t) = 7`,
`b0(t) = D(t)` in `{3,5,6}`, `tau(t) = 2`, `gamma = 0`, all 11 lines
cancellation lines, zero digraph 60 of 110 arcs, `MAS(all) = 4`). Per line
the Lemma MX construction options are the anchor `A` (forbidden: `tau = 2`
is even), 4 repairs `U(a*)`, and 2 pivots `T(c)` — product
`7^11 = 1,977,326,743`, PR 2936's obstruction.

**The DP (this is PR 2936's open question 2).** The construction value
`|A| + |U| + sum_c MAS(class_c)` does not depend on the repair labels `a*`,
and the two Lemma MX hypothesis sets (A-first / T-first) factor per U line
given only the coarse kinds (A / U / T(c)): A-first feasibility is "each
`u` in U keeps an `a*` orthogonal to `b0(s)` at every zero arc `u -> s`
with `s` in `A+U` and to the pivot bit of every T out-neighbour, plus
`a0(t)` orthogonal to every T out-neighbour of each `t` in A"; T-first
feasibility is "each `u` keeps a U-U-orthogonal `a*`, plus every T line's
pivot bit orthogonal to `b0(s)` of its `A+U` in-neighbours". So

```text
MX = max over coarse assignments (kind per line) of
     |A| + |U| + MAS(class_0) + MAS(class_1) + MAS(class_2)
     subject to A-first or T-first feasibility,
```

which is `3^11 = 177147` coarse assignments per record (A is dead at
`tau = 2`), feasibility checked only when a candidate beats the running
best. The optimum value is 9 on every record, with a replayable witness
(combo + repairs + mode) re-evaluated by a faithful port of the engine's
`mx_eval`. **The port is pinned to the engine's own semantics** by agreement
tests: exact equality with the engine's exhaustive product enumeration on 72
small fixture sub-decoders (v = 4..6) and 12 random decoders
(`test_named_exact.py`).

**CL3 = MP exactly at even tau (PROVEN).** In a CL3 form assignment, anchor
pairs have `K_tt = |a0 intersect b0| = tau(t) mod 2 = 0`, so kept lines are
exactly the pivot lines `(e_c, e_c)`; their conflict arcs are the zero arcs
with `c(t) = c(s)`. The value is therefore `sum_c MAS(class_c intersect P)`
for the pivot set `P`, maximized at `P = all lines` by monotonicity of MAS —
which is exactly Lemma MP's objective, and all-pivot forms lie in the CL3
space. Hence CL3 = MP = 9 needs no separate enumeration; the identity is
machine-checked against brute force on the targets.

### The twelve records (all values exact)

| label | named | cert | box | gap_named | PR 2936 stored cert |
|---|---|---|---|---|---|
| tied_min\|0,1,2,3,4,5,6,7,8,9,10 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|0,1,2,3,4,5,6,7,8,9,11 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|0,1,2,3,4,5,6,7,8,10,11 | 9 | 11 | 11 | 2 | 11 |
| tied_min\|0,1,2,3,4,5,6,7,9,10,11 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|0,1,2,3,4,5,6,8,9,10,11 | 9 | 11 | 11 | 2 | 11 |
| tied_min\|0,1,2,3,4,5,7,8,9,10,11 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|0,1,2,3,4,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 11 |
| tied_min\|0,1,2,3,5,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 11 |
| tied_min\|0,1,2,4,5,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|0,1,3,4,5,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 11 |
| tied_min\|0,2,3,4,5,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 10 |
| tied_min\|1,2,3,4,5,6,7,8,9,10,11 | 9 | 11 | 11 | 2 | 9 |

(The label pipe character is part of PR 2936's label format `fixture|S`;
`cert = box = 11` follows from replayed witnesses of size `v = 11`, the
ceiling for both rungs. The stored PR 2936 column is its witnessed
lower bound; `gap_named` uses the exact values.)

Consequences for the family-gap record: the family gap reaches 2 already at
v = 11 on the whole `tied_min` family; the excess of 2 points lives inside
the sub-anchor box (box = cert = 11 while named = 9), i.e. the named forms
miss exactly 2 points that sub-anchor pairs realize. The minimal exact
gap-2 instance is now `tied_min|0,1,2,3,4,5,6,7,8,9,10` (v = 11), and
`tied_min` v = 12 is no longer minimal.

## Box-completeness under Lemma BPP (priority 2)

PR 2914 open question 1: `cert(M) = box-max(M)` whenever every line has
`tau(t) >= 1`? Lemma BPP (PR 2936, PROVEN there) gives the exact obstruction
to the naive projection argument: a witness projects to a box witness of the
same value iff (i) each kept line's `a(t) intersect b(t)` has odd tied-bit
overlap and (ii) every forward zero arc has even off-anchor shared parity.

**What this package establishes (CHECKED, exhaustive where stated):**

- On the weak cell of PR 2936's sweep — its 12 gap2-open scans — both rungs
  are now exact: `box = cert = 11` on 12 of 12, every attaining witness
  box-valued. The four previously open records are closed with replayed
  ceiling witnesses.
- On 60 new fixture-density `tau >= 1` instances at v = 4..6 (GL_3(Z)
  column transforms `P -> P U`, `Q -> Q U^{-T}` of both fixtures, which fix
  `M` and its zero digraph while changing the anchor data, then restrictions,
  filtered to `tau >= 1` everywhere, seed 20261016): exact cert vs exact box
  (the vendored tolerant wrapper of PR 2936) — `box = cert` on all 60, 0
  violations, 0 hard instances (all `cert = v` at these sizes; the hard
  `cert < v` instances live at v = 11).
- The BPP obstruction is **PROVEN real** at `tau = 0` (smallest instance
  first: the v = 2 decoder, attaining witness 2, projection 1, condition (i)
  failing exactly as the lemma predicts) and **CHECKED absent** at
  `tau >= 1` in a bounded search (21 escaping witnesses at v = 3..5, no
  strict drop).

**Status: NOT PROVEN, NOT REFUTED.** A counterexample must certify some kept
line purely through non-tied shared bits or land odd off-anchor parity on a
forward zero arc on every attaining witness (Lemma BPP); none is known, and
every realized attaining witness on the enlarged domain (12 + 60 + PR
2936's 113 deep + 126 synthetic + PR 2914's records) is box-valued. The
without-loss question (can every attaining witness be massaged into (i)+(ii)
at no value cost?) is unchanged and remains the exact blocker.

## The matched-pivot floor (priority 3) — DEMOTED

Unchanged from PR 2914/2936's record and not resurrected: `MP = 9 < cert =
11` on all 12 records adds twelve exact data points against `named = MP =
cert`; `MP >= floor(2v/3)` holds on every record this lineage has measured
(0 below threshold), which is evidence only. The exact obstruction to a
proof is unchanged (the floor is a statement about realizable rank-3
patterns; fixture-density zeros resist random construction).

## What is proved, what is checked, what is demoted

- **PROVEN (written proofs in this README + replayed witnesses):**
  `gap_named = 2` on all 12 `tied_min` v = 11 sub-decoders (exact `named`
  by the coarse DP with replayed construction witnesses; exact `cert` by
  replayed ceiling witnesses); the DP decomposition of the Lemma MX space
  (value independent of repairs; hypothesis sets factor per U line); CL3 =
  MP at even tau; BPP projection strictness at `tau = 0` (v = 2: 2 -> 1).
- **CHECKED (machine, deterministic, stdlib):** the port agrees with the
  engine's exhaustive `mx_eval` on 72 small sub-decoders + 12 random
  decoders; `box = cert = 11` exactly on all 12; `box = cert` on 60 new
  fixture-density `tau >= 1` instances at v = 4..6 (exact rungs); PR 2936's
  stored values reproduced or corrected (7 of 12 stored cert values
  under-report); no strict projection drop at `tau >= 1` among 21 escaping
  witnesses.
- **DEMOTED / OPEN:** F-star for general rational decoders is **not** proved
  and **not** refuted. Box-completeness for `tau >= 1` is **not** proved
  (Lemma BPP is the exact obstruction; no counterexample). The
  matched-pivot floor is **not** proved and stays demoted. The fixture
  certificate limits 11 and 18 rest on PR 2111's recorded CP-SAT optimality
  (CHECKED (recorded), not re-verified here). "No counterexample" remains a
  scoped statement about the declared domains.

## Open next questions

1. **Box-completeness for `tau >= 1` at general v** (PR 2914 open question
   1). Why it matters: it reduces F-star to the finite sub-anchor label
   space and makes the family gap exactly the box interior the named forms
   miss. First step: prove Lemma BPP's conditions (i)-(ii) without loss on
   attaining witnesses (the bounded tau >= 1 search found no strict
   projection drop, so a proof route may exist), or find the smallest
   instance where an attaining witness cannot be massaged. Blocker: naive
   projection is PROVEN strictly lossy at tau = 0 (v = 2).
2. **Characterize the 2-point excess.** Why it matters: `gap_named = 2` is
   now exact on the whole v = 11 `tied_min` family, so the question becomes
   constructive: which label kinds carry the excess (diff_labels classes
   ANCHOR/REPAIR/PIVOT/BOX-INTERIOR/BOX-ESCAPE on the stored attaining
   witnesses), and what is the minimal extension of the named families that
   realizes 11? First step: classify `data/named-v11-receipt.json`'s
   witnesses against the named forms. Blocker: none, analysis only.
3. **The matched-pivot floor** (PR 2747 open question 1), unchanged and
   demoted: a SAT/CP construction of rank-3 patterns minimizing
   `max_c sum_i MAS(Z[C_i])`. Blocker: needs a constraint solver; MP is
   strictly weaker than cert (9 < 11 on all 12).

## Reproduce

Python 3.10+, standard library only, from the repository root (or with the
package path as cwd):

```sh
python3 -B research/fstar-gap2-v11-seed42ff0611/verify.py
python3 scripts/research_package.py --package research/fstar-gap2-v11-seed42ff0611 --check-only
python3 -B research/fstar-gap2-v11-seed42ff0611/test_named_exact.py
```

Expected markers in order from `verify.py`: `PASS_KB5I_PINS files=14`,
`PASS_FG_CONTROLS ...`, `PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19
mp=9/16 chain=22 reach=0/12,8/19`, `PASS_KB5I_NAMED records=12
named-exact=12 named=9x12 gap2-proven=12`, `PASS_KB5I_CROSSCHECK
stored-under-reports=7`, `PASS_KB5I_BOXREPLAY in-box=12/12`, `PASS_BOX_SEARCH
bpp-strict-tau0=yes bpp-strict-tau1=no tau-ge1=60 hard=0 box-violations=0`,
`PASS_FSTAR_GAP2_V11 gap2-below-v12-confirmed`, and `CERTIFICATE.json` with
digest printed at the end. The registered replay recomputes the exact named
values from scratch on all 12 records (it does not trust the receipts) and
independently replays every stored witness.

The checkpoint runs that generated the receipts (NOT part of the registered
replay; their evidence is `data/named-v11-receipt.json` and
`data/box-search-receipt.json`, digested in `CERTIFICATE.json`):

```sh
python3 -B research/fstar-gap2-v11-seed42ff0611/run_named_v11.py
python3 -B research/fstar-gap2-v11-seed42ff0611/box_search.py
```

(about 16 minutes and about 3 minutes on the authoring host;
`run_named_v11.py` is the deterministic multi-seed witness regeneration
whose replays every stored witness passes.) `make` is not installed on the
authoring host; the commands above are the underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged
`research/root-unit-decoder-lemmas` package
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance)).
The rank-3 configuration model, the canonical fixtures `tied_min` and
`cex_min_1`, and their recorded one-copy certificate limits 11 and 18
(CP-SAT, CHECKED (recorded) here, not re-verified) are DreamingOfClouds'
work in [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
The residue statement, Lemmas SF/MP/RK/AN and the exact-completion engine
design are Aaron Wang's
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); Lemma
MX and the exhaustive MP/MX fixture values (9 and 16) are Aaron Wang's
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the
zero-digraph machinery is Aaron Wang's
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774);
Lemmas SC/SG and the canonical reduced normalization are Aaron Wang's
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869); the
chi(Z) machinery is Aaron Wang's
[PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890); the
family-gap definition and record are Aaron Wang's
[PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901); the
sub-anchor box, Lemmas SB/LB and the engine are Aaron Wang's
[PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914); the
v = 7..11 census, the box-completeness attack, Lemma BPP, the tolerant
`tau = 0` wrapper and the recorded 12-sub-decoder remainder are Aaron Wang's
[PR 2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936). All
authors above were verified at current ground truth with `gh pr view
--json author,title` on 2026-10-16 (PRs 2717/2747/2774/2869/2890/2901/2914/
2936: Aaron Wang (navinor); PR 2111: DreamingOfClouds). This package does
not claim their results; the new content is the exact named computation and
its DP, the `gap_named = 2` verdict at v = 11, the cert cross-check with
corrections, the exact box = cert closure of the weak cell, the
fixture-density synthetic family, and the BPP strictness demonstration.

The engine is PR 2914's package extracted byte-exactly with the shared
toolkit (`pr-tree-extract 2914 research/fstar-family-gap-seed1c25f56f`, PR
head `3f7781efccdf10fa61a1e0a6f11c191579b21280` at extraction) and vendored
at `predecessor/pr2914/`; the PR 2936 remainder (its `tied_min` v = 11 deep
receipt and `box_attack.py` with the tolerant wrapper) is extracted
byte-exactly (`pr-tree-extract 2936 research/fstar-family-gap-v711-seed3e3478d8`,
PR head `f0ef06f13e4de3e50c211c880bdc6891c09620a1` at extraction) and
vendored at `predecessor/pr2936/`. SHA-256 pins for every vendored file are
in `predecessor/PINS.json` and verified at every replay; the nested engine
copy the vendored wrapper loads is byte-identical to
`predecessor/pr2914/verify.py` (asserted at pin generation and at replay).
Both predecessors' own recorded anchors were reproduced first from pristine
copies (PR 2914: `PASS_FG_CENSUS records=1410 exact=21 exact-named=21 gap1=49
gap2=0 below-threshold=0 falsifiers=0 max-gap-named=0`, certificate digest
`031927ba33ed45a0`; PR 2936: `PASS_FSTAR_FAMILY_GAP_V711
no-falsifier-in-domain`, certificate digest `a4525ee97862ba34`).

Freshness: base `991c50d1ea8ddb7cf88c1b4a45c7b409c02d38fb` is current
canonical `origin/main` at entry (2026-10-16 12:40 UTC). Pair-collision
checks (toolkit `disc-comments --grep`, discussions 1317 and 1166, nested
replies, 2026-10-16 12:40-12:45 UTC) found no live claim on this object: the
only family-gap activity in the last hours is KB5h's FINDING/DONE/RELEASED
(PR 2936, 12:34:18 UTC), which this assignment explicitly extends. The
overlap survey (`find_overlap.py` with the object's proper names and
synonyms, complete pagination: 471 open PRs, 1622 discussions, 2026-10-16
12:41 UTC) found only the known F-star lineage and unrelated board traffic.

Prepared by **Aaron Wang**, with help from opencode (substantial AI
assistance; no model named; no independent human review claimed). New work
in this package is Apache-2.0.
