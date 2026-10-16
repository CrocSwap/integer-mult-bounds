# fstar-family-gap-seed1c25f56f

**Closing the family gap of open problem F-star: the sub-anchor-box
decomposition of the attaining certificates, and a smallest-first
sub-decoder census at fixture density (no kappa, no frontier change).**
Open problem F-star of `research/root-unit-decoder-lemmas`
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590),
section 7, OPEN) asks whether `cert(M) >= floor(2v/3)` holds for every exact
3-total rational decoder `M = sum_{j<=3} p_j q_j^T`. [PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901)
settled the cancellation-line residue on both canonical fixtures and
isolated the residual obstruction as the **family gap** `named(M) <
cert(M)`: the matched-pivot family certificate reaches 9 and 16 on the
fixtures while `cert` is 11 and 18 (recorded), a gap of exactly 2 on each.
This package (kappa-blocker **KB5g**) attacks that gap: it either lifts the
named families to `cert`, proves the gap harmless at the threshold, or
characterizes exactly what the named families miss and how small the gap
gets before it appears. **F-star itself is not proved and not refuted
here.** Every claim below is labelled PROVEN, CHECKED or DEMOTED.

## Verdict

**The family gap is harmless on the entire realized domain, and its exact
content is characterized: it is the interior of the sub-anchor box.**

1. **CHECKED (exhaustive both sides):** on all 21 exact sub-decoder records
   (`v = 3..6`, smallest-first, deep rungs) `cert = box = form_r = named`
   **exactly** (gap 0), and `cert = max(MP, |S_gamma|) + 1` exactly. Every
   attaining label pair lies in the sub-anchor box.
2. **CHECKED (given PR 2111's recorded certificate limits):** on both full
   fixtures the sub-anchor box attains `cert` exactly (`box = 11 = cert` on
   `tied_min`, `box = 18 = cert` on `cex_min_1`), and every attaining label
   pair lies in the box. The recorded family gap 2 is reproduced against the
   named families (`named = 9` and `16`), and its per-line content is
   classified: the witnesses use REPAIR-form pairs plus strictly interior
   box pairs `a` proper subset of `a0(t)`, `b` proper subset of `b0(t)`,
   `K_tt = 1`, that belong to no named form.
3. **CHECKED (scoped negative):** no threshold counterexample and no
   sub-threshold record exists in the searched domain: `named_lo =
   max(MP, |S_gamma|) >= floor(2v/3)` on all 1410 census records and on both
   fixtures (9 >= 8, 16 >= 12), so by the proven chain `cost >= cert` no
   falsifier can exist there at all. The falsifier criterion was evaluated
   on every record and its decisive branch was never reached.
4. **DEMOTED:** the matched-pivot floor alone (assignment route (a)) is
   strictly weaker than `cert` on the fixtures (9 < 11, 16 < 18), so
   `named = MP = cert` fails; `MP >= floor(2v/3)` itself is witnessed
   everywhere but not proved. A general additive lifting bound (route (b))
   of the form `cert >= named + f(k, v)` is contradicted by the data's
   shape: the gap is 0 on records with up to 3 cancellation lines and 2 on
   `tied_min` with 12 of 12, so it is not a function of the cancellation
   count or of `v`. A realized threshold counterexample (route (c)) was not
   found; the minimal realized gap-2 instance in the searched domain remains
   `tied_min` at `v = 12` (no gap >= 2 at any `v <= 6` record).

The exact remaining gap to a proof of F-star: **prove the sub-anchor box
complete** (`cert = box-max`, at least when every line has `tau(t) >= 1`)
and then prove the box floor `box-max >= floor(2v/3)`, or prove the
matched-pivot floor `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` (which would
close F-star despite being weaker than `cert`). Both remain OPEN here.

## The object and the ladder

An exact 3-total rational decoder on `v` lines is `M = sum_{j=1..3} p_j
q_j^T` over Q with `M_tt != 0` on every line. Row support `pi(t) = {j :
p_j(t) != 0}`, column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) =
pi(t) intersect sigma(t)` (nonempty). An L8 labelling is F2 vectors `a(t)`
supported in `pi(t)` and `b(t)` supported in `sigma(t)`, `K_ts = a(t) . b(s)
mod 2`; `cert(M)` is the largest `|S|` admitting an order with `K_tt = 1` on
`S` and `K_ts = 0` at every incidence `M_ts = 0` with `t` before `s`. The
proven chain `cost >= sum_j r_j >= cert(M)` is from
`research/root-unit-decoder-lemmas`; this package does not restate it.

In the canonical reduced normalization (Lemma SC/SG of
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869), Aaron
Wang; `alpha_j = -m_j`): `a0_j(t) = [v_2(p_j(t)) = m_j]`, `b0_j(t) =
[v_2(q_j(t)) = gamma - m_j]`, with the scope identity `K0_ts = 2^{-gamma}
M_ts mod 2`; `S_gamma = {t : v_2(M_tt) = gamma}` is the anchor reach, the
cancellation lines are `C = {t : v_2(M_tt) > gamma}`, and `tau(t)` is the
tie number of Lemma CT (PR 2901).

This package measures five rungs per instance, each an exact or bounded
maximum of the best certificate value a label class can build:

| rung | label class | value function | status |
|---|---|---|---|
| `named_lo` | Lemma SG anchor plus Lemma MP matched pivots | `max(MP, \lvert S_gamma\rvert)` | exact (MP exhaustive) |
| `named` | all four named families (SG, MX repairs, MP, CL3 mixings) | max construction value | exact on deep records; seeded bounded scan on fixtures |
| `form_r` | every named-form pair: `(a0,b0)`, `(a*, b0)` repairs, `(e_c,e_c)` pivots | `ab_value` (exact for fixed labels) | exact on deep records; bounded on fixtures |
| `box` | every sub-anchor pair `a` subset of `a0(t)`, `b` subset of `b0(t)`, `K_tt = 1` | `ab_value` inside `b0` | exact on deep records; witnessed on fixtures |
| `cert` | every L8 labelling | exact-completion DP (PR 2717 engine) | exact on deep records; witnessed/recorded on fixtures |

Here `ab_value(a, b)` is the exact certificate value of one fixed label
assignment: the largest kept set with `K_tt = 1` whose conflict digraph is
acyclic (subset DP). The ladder facts below hold in general.

## Lemma SB (the sub-anchor box) - PROVEN

Write `a0(t)`, `b0(t)` for the anchor labels of the canonical reduced
normalization.

> **Lemma SB.** (i) `a0(t) intersect b0(t)` is exactly the set of totals
> attaining the tie number `tau(t)`, so `|a0(t) intersect b0(t)| = tau(t)`.
> (ii) A sub-anchor pair (`a` subset of `a0(t)`, `b` subset of `b0(t)`)
> certifies line `t` (`K_tt = 1`) if and only if `|a intersect b|` is odd,
> which requires `tau(t) >= 1`; for `tau(t) = 1` the unique tied bit lies in
> both `a` and `b`; for `tau(t) = 2` exactly one of the two tied bits lies
> in `a intersect b`. (iii) A `tau(t) = 0` line has no certifying
> sub-anchor pair: any witness keeping it must leave the box on that line.

*Proof.* (i) `j` lies in `a0(t) intersect b0(t)` exactly when `j` is in
`D(t)`, `v_2(p_j(t)) = m_j` and `v_2(q_j(t)) = gamma - m_j`, that is when
`v_2(p_j(t) q_j(t)) = gamma`, which is the definition of being counted by
`tau(t)`. (ii) For sub-anchor labels `a intersect b` is a subset of
`a0(t) intersect b0(t)`, and `K_tt = |a intersect b| mod 2`; odd
intersection needs a tied bit, and the two case statements read off (i).
(iii) is (ii) with `tau(t) = 0`. `QED`

On `tied_min` every line has `tau = 2` and on `cex_min_1` the tie numbers
are 1, 2 and 3; Lemma SB explains the shape of every witness pair found
below (each certifying box pair picks an odd number of tied bits).

## Ladder bounds - PROVEN

> **Lemma LB.** (a) `named(M) <= form_r(M)`: every certificate the named
> families carry uses Form-R label pairs per line, and `ab_value` is the
> exact maximum for fixed labels. (b) `box(M) <= cert(M)` by definition of
> the label classes. (c) On any instance where `S_gamma` is empty the Lemma
> CL3 mixing equals the matched-pivot value (the anchor label pair has
> `K0_tt = 0` on every line and certifies nothing), so `named = max(MP,
> MX)` there.

*Proof.* (a) Each named family (Lemma SG anchor, Lemma MX repairs, Lemma MP
pivots, Lemma CL3 mixings) assigns each line one of the three Form-R pairs;
its carried certificate is a certificate of that assignment, whose exact
value is `ab_value`. (b) is the identity of label spaces. (c) with
`S_gamma` empty, `A` is empty in every named construction and the remaining
constructions are matched pivots (Lemma MP) and their Lemma MX variants.
`QED`

Part (c) makes `tied_min`'s named value exact: `named = max(9, 9) = 9` (MP
exhaustive over 4096 pivot maps; MX exhaustive 9 per
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747), Aaron
Wang, reproduced by the seeded scan here). `cex_min_1`'s named value 16 is
PR 2747's exhaustive MP/MX record (reproduced by seeded scans here; the
CL3 rung is a bounded scan, PR 2901's caveat retained).

## Fixture settlement: the box attains cert exactly - CHECKED

Both canonical fixtures of [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111)
(DreamingOfClouds) settle inside the sub-anchor box. Every number is
recomputed by `verify.py` in one run except the certificate limits 11 and
18, which are PR 2111's recorded CP-SAT values (CHECKED (recorded), not
re-verified here).

| quantity | `tied_min` (12 lines) | `cex_min_1` (19 lines) |
|---|---|---|
| threshold `floor(2v/3)` | 8 | 12 |
| cancellation lines | 12 of 12 | 11 of 19 |
| anchor reach `S_gamma` | 0 | 8 (lines 0, 4, 5, 6, 8, 11, 14, 15) |
| `named_lo` = max(MP, reach) | 9 (4096 maps, exhaustive) | 16 (6144 maps, exhaustive) |
| `named` (PR 2901 record, reproduced) | 9 | 16 |
| `form_r` (bounded) | 10 (hill-climb) | 15 (hill-climb; not a bound) |
| `box` | 11 (witnessed) | 18 (stored witness) |
| `cert` | 11 (recorded, witnessed) | 18 (recorded, witnessed) |
| family gap `cert - named` | 2 | 2 |
| box gap `cert - box` | 0 | 0 |
| chain engine (stored pairing) | cited 12 (PR 2379) | 22 (reproduced, 10+6+6) |

So the recorded family gap 2 is exactly the distance from the named
families to the sub-anchor box, and the box closes it on both fixtures
(box >= 11 and 18 by the replayed witnesses; box <= cert = 11 and 18 by
PR 2111's recorded limits). The Form-R rung shows one further split: on
`tied_min` Form-R labels reach 10 of the 11 (bounded hill-climb over a
space of 13,841,287,201 assignments; whether Form-R alone reaches 11 is
OPEN), so at least one of the two missing lines needs strictly interior box
pairs there.

**What the families miss, per line (PR 2901 open question 2 / PR 2747 open
question 3, first step).** The attaining witnesses classify as follows
(`verify.py` diff tables; ANCHOR = `(a0,b0)`, REPAIR = `(a*, b0)`, PIVOT =
`(e_c,e_c)`, BOX-INTERIOR = strictly interior box pair):

| witness | ANCHOR | REPAIR | PIVOT | BOX-INTERIOR | outside box |
|---|---|---|---|---|---|
| `tied_min` 11-witness (engine re-found) | 0 | 5 | 1 | 5 | 0 |
| `tied_min` 11-witness (calibration run) | 0 | 5 | 0 | 6 | 0 |
| `cex_min_1` 18-witness (stored, replayed) | 2 | 10 | 1 | 5 | 0 |

Every attaining label pair lies in the sub-anchor box on both fixtures and
on all 21 exact records (CHECKED). The strictly interior pairs are exactly
the pairs Lemma SB (ii) describes: on a `tau = 2` line they pick one of the
two tied bits in `a intersect b`, dropping the non-tied bits of `a0`/`b0`;
this is the label space no named family enumerates (the named forms fix
`b = b0(t)` on A/U lines or force `a = b` unit vectors on pivots).

## Smallest-first sub-decoder census - CHECKED (scoped negative)

Every sub-decoder `M[S,S]` of a fixture is an exact 3-total decoder
(restriction preserves rank <= 3 and the nonzero diagonal; CHECKED control)
and inherits the fixture-density zero digraphs by construction - the exact
recorded generator obstruction of PR 2901 (its k-axis generators cannot
realize them; Lemma RK (c) forces `|pi(t) intersect sigma(s)| >= 2` at
every arc). The census enumerates subsets smallest-first (sizes 3 to 6,
deterministic strides recorded per size in `CERTIFICATE.json`), computes
the cheap rungs on every record, and the exact rungs (`named`, `form_r`,
`box`, `cert`, all exhaustive) on every flagged record until the deep
budget (21 records) is spent.

| family | domain | records | deep exact | falsifiers | below threshold |
|---|---|---|---|---|---|
| sub-decoders of `tied_min` | `v = 3..6`, sizes 3 complete, 4-6 strided | 760 | 0 flagged | 0 | 0 |
| sub-decoders of `cex_min_1` | `v = 3..6`, strided | 650 | 21 | 0 | 0 |

Totals: 1410 records, 0 falsifiers, 0 below-threshold records, minimum
`named_lo/v = 2/3` (exactly at the threshold ratio). On all 21 exact deep
records (all of them `cex_min_1` sub-decoders, each with 1 to 3
cancellation lines): `cert = box = form_r = named` **exactly**, `cert =
named_lo + 1` exactly, every witness in the box. In particular the family
gap is **0** on every exact record and never reaches 2 below `v = 12` in
the searched domain; the gap is not a function of the cancellation count
(gap 0 with `k_cancel` up to 3; gap 2 at `k_cancel = 12`).

**Falsifier criterion, armed on every record:** exact `cert < floor(2v/3)`
where exhaustive a-enumeration terminates, or an explicit admissible `B`
with chain cost below threshold (the proven chain of
`research/root-unit-decoder-lemmas`). It never fired; in fact its decisive
branch was never reached, because `named_lo >= floor(2v/3)` on every record
and the named witnesses are replayed certificates: by `cost >= cert` no
admissible `B` below threshold can exist on any searched record. This is a
scoped statement about the searched domain, not a non-existence theorem.

**Exact obstruction of the remaining search space (recorded).** Sizes
`v = 7..11` of both fixtures and all but the recorded strides at sizes 4-6
were not enumerated (compute cap). The gap-2 phenomenon needs either those
sizes or the full fixtures; no generator is claimed to realize it at
smaller `v` (an unrealizability claim would need a proof this package does
not have).

## Assignment routes (a), (b), (c) - disposition

- **(a) the family certificate meets the threshold (`named = MP >=
  floor(2v/3)` for every exact 3-total decoder): DEMOTED.** `MP >=
  floor(2v/3)` is witnessed on all 1410 census records and both fixtures
  (9/12, 16/19) but not proved; and the identity `named = cert` fails on
  the fixtures (9 < 11, 16 < 18). A proof of the MP floor would still close
  F-star (cert >= MP); the exact obstruction to proving it here: the floor
  is a statement about realizable rank-3 patterns (Lemma RK (c) constrains
  every arc), the fixture-density zeros resist random construction (PR
  2901's recorded generator obstruction), and no analytic route was found;
  the observed feedback-vertex sums `v - MP` are 3 and 3 against ceilings
  `ceil(v/3) = 4` and 7, with no monotone argument in sight.
- **(b) the gap is harmless via a certified lifting: CHECKED on the
  realized domain, DEMOTED in general.** On all 21 exact records the
  lifting is exact (`named = cert`, gap 0); on both fixtures `box = cert`
  exactly (given the recorded limits) with the missing labels classified
  per line. A proved additive bound of the form `cert >= named + f` is
  DEMOTED: the realized gaps (0 at `v <= 6` with cancellation lines, 2 at
  `v = 12` with 12 of 12) fit no additive function of `k_cancel` or `v`
  the analysis produced, and Lemma SB shows the box can certify nothing on
  a `tau = 0` line, so no uniform per-cancellation-line surplus can hold.
- **(c) the first realized threshold counterexample: NOT FOUND.** The
  strict form (`cert < floor(2v/3)`) and the threshold form (`named <
  floor(2v/3) <= cert`) are both unrealized in the searched domain; the
  minimal realized gap-2 instance remains `tied_min` at `v = 12`, and its
  gap content is exactly the interior-box labels above.

## What is proved, what is checked, what is demoted

- **PROVEN (README, written proofs):** Lemma SB (the sub-anchor box
  structure: `a0 intersect b0` = tied totals; certifying box pairs pick an
  odd number of tied bits; `tau = 0` lines have no certifying box pair);
  Lemma LB (the ladder bounds `named <= form_r`, `box <= cert`, and `named
  = max(MP, MX)` when `S_gamma` is empty, making `tied_min`'s named value
  exactly 9).
- **CHECKED (machine, `verify.py`, stdlib, deterministic, about 230 s,
  certificate digest `031927ba33ed45a0`):** controls 5 groups (brute-force-
  from-definition agreement 3/3 at `v = 3`, corrupted-witness rejection
  2/2, `ab_value` soundness against completion 10/10, restriction exactness
  with the Lemma CT and scope identities, diagonal-style decoder sanity);
  the recorded-anchor calibration (MP 9/16 exhaustive over 4096/6144 pivot
  maps; `tied_min` hill-climb witness 11; `cex_min_1` stored witness 18
  replayed; chain 22 on the stored pairing; reach 0/12 and 8/19); the
  fixture ladder with the per-line label diffs and `box = cert` at 11/11
  and 18/18; the 1410-record census with 21 exact deep records at
  `named = cert` exactly; 0 falsifiers, 0 below-threshold.
- **DEMOTED / OPEN:** F-star for general rational decoders is **not**
  proved here and **not** refuted. The matched-pivot floor (PR 2747 open
  question 1) is not proved. The sub-anchor-box completeness (`cert =
  box-max`) is CHECKED on the realized domain only; `tau = 0` lines are the
  only structurally excluded case (Lemma SB (iii)) and no `tau = 0` line
  occurs in the fixtures. Form-R completeness on `tied_min` (does Form-R
  reach 11?) is OPEN (space of 13,841,287,201 assignments, hill-climb
  10). The fixture certificate limits 11 and 18 rest on PR 2111's recorded
  CP-SAT optimality, not re-verified here. The CL3 rung on `cex_min_1` is a
  bounded scan (PR 2901's caveat retained). The census thinning is recorded
  per size; "no falsifier" is a scoped statement about the declared domain.

## Open next questions

1. **Sub-anchor-box completeness.** Is `cert(M) = box-max(M)` whenever
   every line has `tau(t) >= 1`? Why it matters: it reduces F-star to a
   finite per-line label space (at most 24 certifying pairs per line) and
   makes the family gap exactly the interior of that box. First step: search
   for the smallest instance where an attaining certificate must leave the
   box (all 21 exact records and both fixtures are box-valued; `tau = 0`
   lines are the only excluded case by Lemma SB). Blocker: none; analysis
   plus a bounded exact search.
2. **The matched-pivot floor (PR 2747 open question 1).** Is `max_c sum_i
   MAS(Z[C_i]) >= floor(2v/3)` for every realizable rank-3 pattern? Why it
   matters: Lemma MP alone would prove F-star with no anchor. First step: a
   SAT/CP construction of rank-3 patterns minimizing the floor (the
   fixture-density zeros resist random construction; Lemma RK (c) forces
   `|pi(t) intersect sigma(s)| >= 2` at every arc). Blocker: needs a
   constraint solver, not random search.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-family-gap-seed1c25f56f/verify.py
python3 scripts/research_package.py --package research/fstar-family-gap-seed1c25f56f --check-only
python3.12 scripts/research_package.py --package research/fstar-family-gap-seed1c25f56f
```

Expected markers: `PASS_FG_CONTROLS`, `PASS_FG_CALIBRATION
tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22 reach=0/12,8/19`,
`PASS_FG_CENSUS records=1410 exact=21 exact-named=21 gap1=49 gap2=0
below-threshold=0 falsifiers=0 max-gap-named=0`,
`PASS_FSTAR_FAMILY_GAP no-falsifier-in-domain`, and `CERTIFICATE.json` with
digest `031927ba33ed45a0` (observed 217-229 s on the authoring host).
`make` is not installed on the authoring host; the commands above are the
underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged
`research/root-unit-decoder-lemmas` package
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance)).
The rank-3 configuration model, the named instances `tied_min` and
`cex_min_1`, their recorded one-copy certificate limits (11 and 18, CP-SAT,
CHECKED (recorded)) and the tied-minima obstruction are DreamingOfClouds'
work in [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111)
and [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162);
`data/tied_min.json` and `data/cex_min_1.json` are byte-identical copies of
their data files (sha256
`670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`); the
stored cost-22 pairing is `data/cex_min_1.B22.json` (sha256
`15f5039069a175831f92c4ffe023a23a6f6e6bd6665f0ca2c2734bbe672b51ef`) and the
stored 18-witness `data/cex_min_1.witness.json` (sha256
`153f4d2e8dc262f547a91f2daff9724cab88beb4d45c399497efc68a8ed2c933`) is from
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)'s
package. The residue statement, Lemmas SF/MP/RK/AN and the exact-completion
engine design this package adapts are Aaron Wang's work in PR 2717; Lemma
MX and the exhaustive MP/MX fixture values (9 and 16) are Aaron Wang's
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the
zero-digraph machinery is Aaron Wang's
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774);
Lemmas SC/SG and the canonical reduced normalization are Aaron Wang's
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869); the
chi(Z) machinery is Aaron Wang's
[PR 2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890); the
family-gap definition and record are Aaron Wang's
[PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901). The
exact cost 12 of `tied_min` is Aaron Wang's
[PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the
exact cost 21 of `cex_min_1` is Nick Petalas'
[PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). All
authors above were verified at current ground truth with `gh pr view
--json author,title` on 2026-10-16. This package does not claim their
results; the new content is Lemma SB, Lemma LB, the sub-anchor-box
machinery and decomposition, the exact named/Form-R/box/cert ladder on
small instances, the per-line classification of the attaining witnesses,
and the sub-decoder census at fixture density.

Freshness: base `ba3de47290c3882cbbe406db1f657578f7ecda69` is the frozen
assignment pin (kept intentionally). Pair-collision checks
(discussions 1317 + 1166, nested replies, 2026-10-16 08:58-09:00 UTC and
the pre-submission re-run) found no live claim on this object; the last
F-star activity on the board is KB5f's FINDING/DONE/RELEASED at 2026-10-16
08:53:52 UTC. Entry overlap survey 2026-10-16 09:01 UTC and the refined
pre-submission re-run (complete pagination) found only the known F-star
lineage and unrelated traffic.

Prepared by **Aaron Wang** with help from opencode (substantial AI
assistance; no model named; no independent human review claimed). New work
in this package is Apache-2.0.
