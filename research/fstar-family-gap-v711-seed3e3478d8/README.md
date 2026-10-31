# fstar-family-gap-v711-seed3e3478d8

**KB5h: the remaining search space of open problem F-star's family gap - the
v = 7..11 sub-decoder census and the box-completeness attack (no kappa, no
frontier change).** Open problem F-star of `research/root-unit-decoder-lemmas`
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance),
section 7, OPEN) asks whether `cert(M) >= floor(2v/3)` holds for every exact
3-total rational decoder `M = sum_{j<=3} p_j q_j^T`. [PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914)
(Aaron Wang, agent-72) lifted the family gap on the realized domain and
recorded the exact remaining gap: **box-completeness (`cert = box-max` for
`tau >= 1`) plus the box floor, or the matched-pivot floor, at general v**,
with **v = 7..11 unenumerated**. This package closes that enumeration and
attacks box-completeness. **F-star itself is not proved and not refuted
here.** Every claim below is labelled PROVEN, CHECKED or DEMOTED.

## Verdict

1. **CHECKED (exhaustive on the declared domain, witnesses replayed):** the
   v = 7..11 range is enumerated: 1638 sub-decoder records of the two
   canonical fixtures (complete at `tied_min` v = 9..11, deterministic
   strides elsewhere), 113 deep records and 126 synthetic instances. The
   falsifier criterion (exact `cert < floor(2v/3)`, or an admissible pairing
   `B` with chain cost below threshold) was armed on every record and never
   fired; it is in fact **PROVEN inoperative on the whole domain**:
   `named_lo = max(MP, reach) >= floor(2v/3)` on all 1638 records (minimum
   ratio 5/7), and each `named_lo` is a replayed certificate value, so the
   proven chain `cost >= cert` leaves no admissible `B` below threshold.
   `MP >= floor(2v/3)` alone holds on all 1638 records (0 records below).
2. **CHECKED (exhaustive both sides): the first gap-2-or-more instance below
   v = 12 is at v = 7.** `cex_min_1|0,1,2,5,6,8,15` has `cert = 7` (= v,
   exact) and `named_lo = 5` (MP = 5 exhaustive, reach = 5): the gap to the
   cheap rung is exactly 2. 38 records witness gap >= 2 against the cheap
   rung (`cert` or `box` witness minus `named_lo`), all `cex_min_1`
   sub-decoders, at v = 7..11. But the **family gap** `cert - named` is 0 on
   both v = 7 gap-2 records (`named = 7` exact): the gap-2 there is a gap to
   the cheap rung only.
3. **CHECKED (exhaustive both sides): the family gap is nonzero from v = 7.**
   `tied_min|0,1,2,5,6,8,10` and `tied_min|2,3,4,7,9,10,11` (v = 7) have
   `named = 6` exact (Lemma MX construction space of 823543 exhausted) and
   `cert = 7` exact: `gap_named = 1`. 17 deep records carry a CHECKED exact
   `gap_named = 1` (v = 7..10); the maximum exact family gap below v = 12
   is 1. `gap_named = 2` below v = 12 is **excluded on every enumerated
   record except the 12 `tied_min` v = 11 sub-decoders**, where `named` is
   scan-only (Lemma MX construction product 1,977,326,743 - the exact
   obstruction) and the gap is in `{0,1,2}`. The minimal instance with an
   exact `gap_named = 2` remains `tied_min` at v = 12 (PR 2901/PR 2914
   record).
4. **CHECKED (scoped negative): box-completeness is not refuted.** `box =
   cert` on all 113 deep records (exact equality, or ceiling/in-box
   equality), on both fixtures (PR 2914: 11/11, 18/18), on all 21 PR 2914
   exact records, and on all 11 `tau >= 1` synthetic instances; every
   recorded attaining witness is box-valued. The single candidate where a
   hill-climb left `box` one below `cert` (`tied_min|0,1,2,3,4,5,6,7,8,10,11`
   at v = 11) dissolved: its attaining cert witness is itself a box witness.
5. **PROVEN: the `tau >= 1` hypothesis is necessary.** An explicit exact
   3-total rational decoder on v = 2 lines with `tau = (1,0)` has `cert = 2
   > box = 1` (below); without the hypothesis, box-completeness fails at the
   smallest possible size. On all 115 synthetic instances with a `tau = 0`
   line, `box = #{t : tau(t) >= 1}` exactly (CHECKED pattern).
6. **DEMOTED (retained, no new evidence): the matched-pivot floor.** PR 2914
   demoted route (a): MP is strictly weaker than `cert` on the fixtures
   (9 < 11, 16 < 18). This package adds the data point that `MP >=
   floor(2v/3)` on all 1638 census records and all 113 deep records
   (witnessed, 0 records below threshold with MP alone), which is evidence,
   not a proof; nothing here resurrects `named = MP = cert`.

The exact remaining search space after this package: **(i) box-completeness
for `tau >= 1` at general v** (open; every realized instance agrees, the
projection lemma below states exactly what a counterexample must do);
**(ii) the family gap on the 12 `tied_min` v = 11 sub-decoders** (`gap_named`
in `{0,1,2}`, blocked by the Lemma MX construction product ~2e9); **(iii)
the matched-pivot floor** (PR 2747 open question 1, still unproved).

## The object and the inherited ladder

An exact 3-total rational decoder on v lines is `M = sum_{j=1..3} p_j q_j^T`
over Q with `M_tt != 0` on every line. Row support `pi(t) = {j : p_j(t) !=
0}`, column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) = pi(t) intersect
sigma(t)` (nonempty). An L8 labelling is F2 vectors `a(t)` supported in
`pi(t)` and `b(t)` supported in `sigma(t)`, `K_ts = a(t) . b(s) mod 2`;
`cert(M)` is the largest `|S|` admitting an order with `K_tt = 1` on S and
`K_ts = 0` at every incidence `M_ts = 0` with t before s. The proven chain
`cost >= sum_j r_j >= cert(M)` is from `research/root-unit-decoder-lemmas`;
this package does not restate it.

The canonical reduced normalization (Lemmas SC/SG of
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869), Aaron
Wang) fixes anchor labels `a0(t)`, `b0(t)` with `K0_ts = 2^{-gamma} M_ts mod
2`; `S_gamma` is the anchor reach, `C` the cancellation lines, `tau(t)` the
tie number of Lemma CT ([PR 2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901),
Aaron Wang). The ladder measured per instance (PR 2914's rungs, extended
here to v = 7..11):

| rung | label class | value | status here |
|---|---|---|---|
| `named_lo` | Lemma SG anchor + Lemma MP matched pivots | `max(MP, \lvert S_gamma\rvert)` | exact (MP exhaustive at v <= 11: product <= 3^11 = 177147) |
| `named` | all four named families (SG, MX repairs, MP, CL3 mixings) | max construction value | exact where the MX product fits 3,000,000; seeded scan otherwise |
| `box` | sub-anchor pairs `a` subset of `a0(t)`, `b` subset of `b0(t)`, `K_tt = 1` | `ab_value` inside `b0` | exact where enumerated; witnessed elsewhere |
| `cert` | every L8 labelling | exact-completion DP (PR 2717 engine) | exact where enumerated; witnessed elsewhere |

The engine is PR 2914's, vendored byte-exactly at `predecessor/pr2914/`
(SHA-256 pins in `predecessor/PREDECESSOR-PINS.json`, verified at replay).

## Priority (1): the v = 7..11 census - CHECKED

Sub-decoders `M[S,S]` of both canonical fixtures (restriction of an exact
decoder is exact: rank <= 3 and the nonzero diagonal are preserved; every
sub-decoder inherits fixture-density zero digraphs, the exact generator
obstruction PR 2901 recorded). Smallest instance first; deterministic
strides (`subsets_smallest_first` of the vendored engine), recorded per cell:

| fixture | v = 7 | v = 8 | v = 9 | v = 10 | v = 11 |
|---|---|---|---|---|---|
| `tied_min` | 240 of 792 | 240 of 495 | 220 of 220 (complete) | 66 of 66 (complete) | 12 of 12 (complete) |
| `cex_min_1` | 240 of 50388 | 200 of 75582 | 160 of 92378 | 140 of 92378 | 120 of 75582 |

Every record carries the identity controls (Lemma CT tie parity, the scope
identity), exhaustive MP (product <= 177147 at v <= 11), `named_lo`, the
threshold and falsifier screens, and replayed `cert`/`box` witness
hill-climbs (seeded, bounded). Totals (replayed by `verify.py`):

| quantity | value |
|---|---|
| records | 1638 |
| trivial gap-0 closures (`named_lo = v`, so `cert = named_lo = v`) | 946 |
| witnesses independently replayed | 1384 |
| records witnessing gap >= 2 vs `named_lo` | 38 |
| records with gap-2 potential (`v - named_lo >= 2`) | 70 |
| records with `named_lo < floor(2v/3)` | 0 |
| records with `MP < floor(2v/3)` | 0 |
| falsifiers | 0 |
| minimum `named_lo / v` | 5/7 (at v = 7) |

**The falsifier criterion is armed and dead.** Its decisive branch needs
either exact `cert < floor(2v/3)` or an admissible `B` with chain cost below
threshold; on every record a certificate of value `named_lo >= floor(2v/3)`
replays, and the proven chain `cost >= cert >= named_lo` excludes every such
`B`. This is a scoped statement about the enumerated domain, not a
non-existence theorem.

**The first gap-2-or-more instance below v = 12 (PROVEN).** `cex_min_1
|0,1,2,5,6,8,15` at v = 7: `MP = 5` (exhaustive over 8 pivot maps), reach 5,
so `named_lo = 5`; `cert = 7` = v with a replayed witness, hence exact. The
gap to the cheap rung is exactly 2. Its family gap is 0 (`named = 7`, Lemma
MX product 11907 exhausted): MX repairs close the cheap-rung gap. The
companion record `cex_min_1|0,6,7,8,11,15,18` is identical in shape.

**Family gap by v (deep tier, 113 records).** Exact `named` (Lemma MX + CL3
construction spaces exhausted) and exact `cert` (enumeration, or ceiling via
a replayed witness of size v) wherever the products allow:

| v | PROVEN exact `gap_named` | gap-2 status |
|---|---|---|
| 7 | 1 (first nonzero below v = 12; 2 `tied_min` records), 0 elsewhere | excluded (both sides exact on all 12 deep v = 7 records) |
| 8 | 1 (2 `cex_min_1` records), 0 elsewhere | excluded |
| 9 | 1 (3 `cex_min_1` records), 0 elsewhere | excluded |
| 10 | 1 (2 `cex_min_1` records), 0 elsewhere | excluded (the v = 10 candidate settled: `named = 10` exact) |
| 11 | none exact | **open exactly on the 12 `tied_min` v = 11 sub-decoders** (`gap_named` in `{0,1,2}`) |

The v = 11 residual: all 12 `tied_min` v = 11 sub-decoders have `tau = 2` on
every line and 11 of 11 cancellation lines; their Lemma MX construction
product is 1,977,326,743 (exhaustive enumeration is ~2e9 `mx_eval` calls,
far past any bounded run), so `named` is a seeded scan (value 9) and
`gap_named = cert - named` stays in `{0,1,2}` (cert in `{9,10,11}`). The
`cex_min_1` v = 11 scans have `v - named_scan = 1`, which excludes gap 2
there without exactness.

**The scan pitfall, quantified (CHECKED).** PR 2914's lineage caution is
real: on 3 of the 10 records settled by `settle_named.py` (raised 3M cap,
exhaustive), the seeded 20,000-iteration Lemma MX scan had under-reported
`named` by 1..2 (the v = 10 gap-2 candidate's scan value 8 is exactly 10).
Scanned `named` values are lower bounds and must not be read as the family
value; every PROVEN `gap_named` above uses an exhausted construction space.

## Priority (2): box-completeness - NOT PROVEN, NOT REFUTED, hypothesis pinned

PR 2914's open question 1: is `cert(M) = box-max(M)` whenever every line has
`tau(t) >= 1`? The sub-anchor box is the label space `a(t) subset of a0(t)`,
`b(t) subset of b0(t)` with `K_tt = 1`; Lemma SB (PR 2914, PROVEN there)
says a box pair certifies t iff `|a intersect b|` is odd among tied bits, and
a `tau(t) = 0` line has no certifying box pair at all.

**Evidence for completeness (CHECKED):** `box = cert` on all 113 deep
records (exact equality, or equality through a replayed attaining witness of
size v in the box), on both fixtures (PR 2914: 11/11 and 18/18 given PR
2111's recorded limits), on all 21 PR 2914 exact records, and on all 11
`tau >= 1` synthetic instances below. Every recorded attaining witness in
the package is box-valued (PR 2914 observed the same on its domain). The one
candidate where a box hill-climb sat one below cert (`tied_min
|0,1,2,3,4,5,6,7,8,10,11`, v = 11: box witness 10, cert witness 11) is
resolved: the stored 11-witness is itself in the box (`cert_witness_in_box`),
so `box = cert = 11`.

**The hypothesis `tau >= 1` is necessary (PROVEN).** Smallest instance
first: the explicit v = 2 decoder

```text
P = [[1, 0, 1], [2, 1, 0]]     Q = [[1, 0, 0], [1, 0, 1]]
M = [[1, 2], [2, 2]]           gamma = 0    tau = (1, 0)
```

(all three totals used; `D(0) = {0}`, `D(1) = {0}`; the tie and scope
identities are machine-checked on it). Line 1 has `tau(1) = 0`: its only
total has `v2(p_0(1)) + v2(q_0(1)) = 1 > gamma`. Then `cert = 2`: keep both
lines with `a = b = {0}` on each (the pair on line 1 uses a high total and is
not a box pair), and there are no zero arcs to constrain the order. But
`box = 1`: line 1 has `a0(1) = {1}`, `b0(1) = {0, 2}`, so no sub-anchor pair
gives `K_11 = 1` (Lemma SB (iii)); line 0 certifies in the box. Hence
`cert = 2 > box = 1` and unrestricted box-completeness fails at v = 2, the
smallest possible size.

**The `tau = 0` mechanism, measured (CHECKED).** On all 115 synthetic
instances containing at least one `tau = 0` line, `box = #{t : tau(t) >= 1}`
exactly (cert = v on all of them): the box loses precisely the `tau = 0`
lines, matching Lemma SB (iii). This is a pattern over the declared
generator, not a theorem.

**Lemma BPP (box projection parity) - PROVEN.** Let `(a, b)` be any L8
labelling and `(a', b')` its sub-anchor projection `a'(t) = a(t) intersect
a0(t)`, `b'(t) = b(t) intersect b0(t)`. Then for every pair `(t, s)`:

```text
K'_ts = |a(t) intersect b(s) intersect (a0(t) intersect b0(s))| mod 2
K'_ts = K_ts + |(a(t) intersect b(s)) \ (a0(t) intersect b0(s))|  (mod 2)
K'_tt = |a(t) intersect b(t) intersect (a0(t) intersect b0(t))|  (mod 2)
```

*Proof.* Set algebra mod 2: `|X| = |X intersect Y| + |X \ Y|` for
`X = a(t) intersect b(s)` and `Y = a0(t) intersect b0(s)`. `QED`

So a witness keeping S in some order projects to a box witness keeping S in
the same order **if** (i) every kept line's `a(t) intersect b(t)` contains an
odd number of tied bits and (ii) every forward zero arc among kept lines has
`|(a(t) intersect b(s)) \ (a0(t) intersect b0(s))|` even. A box-completeness
counterexample must therefore violate (i) or (ii) on every attaining
witness: certify some kept line purely through non-tied shared bits, or land
an odd shared-high-bit parity on some forward zero arc. Naive projection is
not a proof of completeness; the parity terms above are exactly what blocks
it, and no realized instance needs them.

**Synthetic sweep (CHECKED).** 126 deterministic random exact 3-total
decoders at v = 4..7 (seed 20261016), exact `cert` vs exact `box` on each:
11 have `tau >= 1` everywhere and all satisfy `box = cert` (all with
`cert = v`); the 115 with a `tau = 0` line follow the pattern above; 0
counterexamples. Random decoders never produced a hard (`cert < v`)
`tau >= 1` instance - fixture-density zeros are needed for that (PR 2901's
generator obstruction), and those are the census records above.

## Priority (3): the matched-pivot floor - DEMOTED (retained)

PR 2914 DEMOTED route (a) and this package does not resurrect it: MP is
strictly weaker than `cert` on the fixtures (9 < 11, 16 < 18, PR 2901/2914
records), so `named = MP = cert` fails and a proof of `MP >= floor(2v/3)`
would close F-star only through `cert >= MP`. New data in favor of the
statement, none of it a proof: `MP >= floor(2v/3)` holds on all 1638 census
records and all 113 deep records (0 records below threshold with MP alone;
minimum `MP / v` = 5/7 at v = 7). The exact obstruction to a proof is
unchanged from PR 2914's record: the floor is a statement about realizable
rank-3 patterns (Lemma RK (c) constrains every arc), fixture-density zeros
resist random construction, and no analytic route was found.

## What is proved, what is checked, what is demoted

- **PROVEN (written proofs in this README):** `tau >= 1` is necessary for
  box-completeness (the explicit v = 2 decoder, argument in prose); Lemma
  BPP (projection parity) with its exact obstruction; the falsifier
  criterion is inoperative on the enumerated domain (the chain plus the
  replayed `named_lo` certificate witnesses); `named_lo = v` forces
  `cert = named_lo = v`.
- **CHECKED (exhaustive machine computation, both sides exact):** the first
  gap-2-or-more instance below v = 12 is at v = 7; the family gap is 1 (not
  0) from v = 7; `gap_named = 2` is excluded below v = 12 outside the 12
  `tied_min` v = 11 sub-decoders.
- **CHECKED (machine, `verify.py`, stdlib, deterministic, 58.5 s,
  certificate digest `a4525ee97862ba34`):** predecessor pins (11 files
  byte-exact); PR 2914's controls and every recorded anchor
  (`PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22
  reach=0/12,8/19`, PR 2914 certificate digest `031927ba33ed45a0`
  reproduced); all 1638 cheap records (identities, 1384 replayed witnesses,
  gap bookkeeping, MP recomputed on a sample + every gap-2 record); all 113
  deep records (products recomputed, exact-rung reproduction on a bounded
  sample incl. both v = 7 `gap_named = 1` records and the settled v = 10
  candidate); the box-attack core (the v = 2 demonstration and the first 100
  sweep instances re-run value-by-value).
- **CHECKED (receipts, not recomputed in the registered run):** the full
  126-instance sweep's v = 6,7 cells; deep-rung values outside the
  reproduction sample (each has a replayed witness or a recorded exact-rung
  value; the heavy census itself is a resumable checkpoint run with periodic
  receipts, `data/census_v711/`).
- **DEMOTED / OPEN:** F-star for general rational decoders is **not** proved
  and **not** refuted. Box-completeness for `tau >= 1` is **not** proved
  (Lemma BPP states exactly what a counterexample must do; none is known).
  `gap_named = 2` below v = 12 is **not** excluded on the 12 `tied_min` v =
  11 sub-decoders (Lemma MX product 1,977,326,743). The matched-pivot floor
  is not proved. The fixture certificate limits 11 and 18 rest on PR 2111's
  recorded CP-SAT optimality (CHECKED (recorded), not re-verified here). The
  thinning at `tied_min` v = 7..8 and all `cex_min_1` cells is recorded per
  cell; "no falsifier" is a scoped statement about the declared domain.

## Open next questions

1. **Box-completeness for `tau >= 1` at general v** (PR 2914 open question
   1). Why it matters: it reduces F-star to the finite sub-anchor label
   space and makes the family gap exactly the box interior the named forms
   miss. First step: prove or refute Lemma BPP's sufficient conditions are
   without loss - i.e. show every witness can be massaged (line by line
   re-pairing, not projection) into one satisfying (i)+(ii) at no value cost,
   or find the smallest instance where that fails (the 12 `tied_min` v = 11
   sub-decoders are the current minimal candidates; both sides exact there
   needs a better `named`/`box` algorithm than product enumeration).
2. **The family gap on the 12 `tied_min` v = 11 sub-decoders.** Why it
   matters: it is the exact remaining search space for "gap 2 below v = 12".
   First step: a DP over the Lemma MX construction space (the value
   `|A| + |U| + sum MAS(classes)` is additive under the hypothesis
   constraints) instead of the 2e9-product enumeration. Blocker: the
   hypothesis checks couple A/U/T choices across zero arcs.
3. **The matched-pivot floor** (PR 2747 open question 1), unchanged from PR
   2914's record: a SAT/CP construction of rank-3 patterns minimizing
   `max_c sum_i MAS(Z[C_i])`. Blocker: needs a constraint solver, not random
   search.

## Reproduce

Python 3.10+, standard library only, from the package directory (or with the
package path as cwd):

```sh
python3 -B research/fstar-family-gap-v711-seed3e3478d8/verify.py
python3 scripts/research_package.py --package research/fstar-family-gap-v711-seed3e3478d8 --check-only
```

Expected markers in order: `PASS_KB5H_PINS files=11`, `PASS_FG_CONTROLS`,
`PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22
reach=0/12,8/19`, `PASS_KB5H_CENSUS records=1638 trivial-gap0=946
gap1-witnessed=452 gap2-witnessed=38 gap2-potential=70 falsifiers=0
below-threshold=0 mp-below-threshold=0 min-named-lo-ratio=0.7143
witnesses-replayed=1384`, `PASS_KB5H_DEEP records=113 gap-named-proven>=17
gap-named-proven-max=1 gap-named-ge2-stored=5 gap2-open-scan-only=12
box-violations=0 reproduced=24`, `PASS_BOX_ATTACK tau0-demo-cert2-box1
sweep-replayed=100/100 sweep-total=126 tau-ge1=11 box-violations=0
tau0-pattern=115/115`, `PASS_FSTAR_FAMILY_GAP_V711 no-falsifier-in-domain`,
and `CERTIFICATE.json` with digest `a4525ee97862ba34` (observed 58.5 s on the
authoring host).

The heavy runs are resumable checkpoint jobs with receipts and are NOT part
of the registered replay (their evidence is the receipt set under
`data/census_v711/`, digested in `CERTIFICATE.json`):

```sh
python3 -B research/fstar-family-gap-v711-seed3e3478d8/census_v7_11.py --fixture tied_min.json --size 7 --cap 240 --mode cheap --hill-iters 60
python3 -B research/fstar-family-gap-v711-seed3e3478d8/run_deep_batches.py
python3 -B research/fstar-family-gap-v711-seed3e3478d8/settle_named.py
python3 -B research/fstar-family-gap-v711-seed3e3478d8/box_attack.py
```

(10 cheap cells, 10 deep cells, the named-settlement pass and the 126-instance
sweep; about 25 minutes total on the authoring host.) `make` is not
installed on the authoring host; the commands above are the underlying ones.

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
sub-anchor box, Lemma SB/LB and the v = 3..6 census this package extends are
Aaron Wang's
[PR 2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914). All
authors above were verified at current ground truth with `gh pr view
--json author,title` on 2026-10-16. This package does not claim their
results; the new content is the v = 7..11 census and its verdicts, the
exact-residual classification (12 `tied_min` v = 11 sub-decoders), the scan
pitfall quantification, the v = 2 `tau = 0` demonstration, Lemma BPP and the
synthetic sweep.

The engine is PR 2914's package extracted byte-exactly with the shared
toolkit (`pr-tree-extract 2914 research/fstar-family-gap-seed1c25f56f`, PR
head `3f7781efccdf10fa61a1e0a6f11c191579b21280` at extraction) and vendored
at `predecessor/pr2914/` with SHA-256 pins in
`predecessor/PREDECESSOR-PINS.json` (verified at every replay). PR 2914's
reproduction was run first from a pristine temp copy and reproduced every
recorded anchor and its certificate digest `031927ba33ed45a0`.

Freshness: base `5a0dc2c0f4685b02bef7776bc196c7c1231cbac1` is current
canonical `origin/main`, fetched and pinned at entry (2026-10-16 10:45 UTC,
unchanged at the pre-computation refresh). Pair-collision checks (toolkit
`disc-comments --grep`, discussions 1317 and 1166, nested replies, at entry
2026-10-16 10:45-10:47 UTC and the refined pre-computation re-run 11:21 UTC)
found no live claim on this object: the only F-star family activity in the
last hours is KB5g's FINDING/DONE/RELEASED (PR 2914 itself, 10:40:51 UTC),
which this assignment explicitly extends. Overlap surveys (`find_overlap.py`
with the object's proper names and synonyms, complete pagination: 494 then
496 open PRs, 1588 then 1597 discussions, 2026-10-16 10:45 and 11:21 UTC)
found only the known F-star lineage and unrelated board traffic.

Prepared by **Aaron Wang**, with help from opencode (substantial AI
assistance; no model named; no independent human review claimed). New work
in this package is Apache-2.0.
