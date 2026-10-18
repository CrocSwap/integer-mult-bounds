# Bit-side revision-3 levers: certified budgets for the PR589 bit supplier at a = 1/99

**Scoped obstructions plus a screening table. No new κ; the selected record is unchanged.**
- **Track:** 00–19 (bit supplier); assignment seed 3 (OS CSPRNG via Python `secrets`).
- **Card:** `bit-helper-contract`, scope **changed** (see [TASK.json](TASK.json)).
- **Base:** `bce54fb3`, where the selected record is frontier1094: κ = 0.001672660197076918, with the complex side binding.

## Question

The **proposed** priority revision 3 (open #1272, stacked on open #1240) aims effort at three
levers: the centre path, the rank shape and the coverage law. It quantifies them for the complex
supplier only, and says a large jump also needs the bit side to move. This package asks how those
levers price on the selected **PR589 bit** supplier:
- Which of them can reach the planning target a = 1/99?
- How many full-frame helpers does a given per-call copy charge leave room for?

## The model and its premises

Every number is an exact rational interval, computed by [levers.py](levers.py) with the standard
library only (ln by atanh prime chains, exp by Taylor with a remainder bound, outward dyadic
rounding). No repository engine is imported.

The per-call bill at saving a is B(a) = (1/w) Σ n_r (r/m)^(1−a). This is the bit side of #1240's
coverage-law relaxation, and it rests on these premises:

- **Coverage law (checked on the record).** Per call, the paid rank mass is (m − u)·w + cst, with
  m = 64, w = 888/9 live families per call, u = 1 unpaid coordinate and a copy charge cst = 63
  (nine rank-7 copies). So mass = 63W + 63N = 1,808,352 and D = W − 63N = 10,272.
  - This is format-limits (Dfc), checked there in A.4 and in our #1023. It is the bit analogue of
    the coverage identity in our open #1012.
- **Local children.** Either the replayed word, or the most favorable in-window shapes:
  - every data register is a single rank-7 climb (sources run 1 → 8 and targets 0 → 7, so each
    climbs 7);
  - every helper is a single climb of rank equal to its width.

  All remaining mass goes to idle children at one rank R, with fractional counts allowed.
- **Copy charge.** The copy charge is carried as rank-7 copies. This is a premise, not a favorable
  step: format-limits (Bat) allows copies up to h = 8. The receipt shows that rank-8 carriage
  changes no conclusion (O1 at cap 45: 0.006794 → 0.006805; the O2 width-8 boundary stays 104).
- **The idle cap R is a premise tied to the halving depth.**
  - `global_k.py` does not cap children; it raises the halving depth HD until 2·maxchild^HD <
    m^HD. HD is limited by the invoice's row-coefficient bound, row < 20161.
  - The record uses HD = 2 under the PR510 bound (`assemble9.py`: row = HD·(m² + 1) + 10161 =
    18355). HD = 3 would already exceed the bound, so the record's cap is R = 45.
  - The merged elementary-cover bound (`r740-hosted-eleven/code/row_bound.py`, which the PR589
    eleven-stage entry uses) admits HD ≤ 4 at this size, so R ≤ 50 (HD = 3) or R ≤ 53 (HD = 4).
  - Results are therefore reported at caps 45, 50 and 53. Cap 63 is a robustness bound that neither
    invoice admits.
- **Surcharge.** The surcharge is omitted.

Each relaxation step lowers the bill:
- cost per unit mass r^(−a)·m^(a−1) decreases in r, so idle mass is cheapest at the cap;
- r^(1−a) is subadditive, so merging a register's climbs is cheaper;
- the counts enter linearly, so fractional counts form a superset;
- the surcharge is positive.

`test_package.py` checks one instance of each step. Consequently, a certified **fail** rules out
every construction that satisfies the premises, while a **pass** is only a target that a real
mechanism must meet with its full paid budget.

**Relation to the merged `research/format-limits`.** The scopes are complementary, not nested.
- Format-limits argues, with every number checked, that under its axioms the bit saving is at most
  X(9) = 4.6072·10⁻³ at s = 9, and X* = 6.0005·10⁻³ over all s.
- This model keeps (P), (Dfc) as the coverage law, the (Bat) caps and the s = 9 data climb of 7.
- It drops (Sch) and slot domination.
- It adds the halving-depth idle cap and rank-7 copy carriage.
- Its O1 ceiling (0.006794 at cap 45) is therefore weaker than X(9), but it prices joint budgets on
  the actual word.
- Format-limits A.7's star-scope multiplier (×2.79 at s = 9) is an independent check of the
  centre-free row below (×2.771).

## Results ([RESULT.json](RESULT.json); certified at a = 1/99)

### Lever table (cap 45)

| Lever (bit, PR589 word) | Root a (bracket in receipt) | × ceiling | At 1/99 |
|---|---:|---:|---|
| Word as shipped, ideal idle packing (**packing ceiling**) | 0.001955918756 | 1 | fail |
| Centre path free (no rank-7 copies, cst 0) | 0.005419644435 | 2.771 | fail |
| Centre path shared by two calls (cst 31.5) | 0.003686367065 | 1.885 | fail |
| Two unpaid coordinates per family | 0.007312036734 | 3.738 | fail |
| Rank-8 children (window h = 8) | 0.003211353255 | 1.642 | fail |
| Rank-16 children (beyond the window) | 0.004730915412 | 2.419 | fail |
| Centre free + rank-8 children | 0.008938289238 | 4.570 | fail |
| Centre free + rank-16 children | 0.01316705483 | 6.732 | pass |
| Centre free + two unpaid coordinates | 0.01075873179 | 5.501 | pass |
| Two unpaid + ideal in-window shapes (copies kept, 439 rank-8 helpers) | 0.01179413211 | 6.030 | pass |
| Centre free + ideal data + 332 width-8 helpers (in window) | 0.01010213059 | 5.165 | pass |

The first seven rows also fail at caps 50, 53 and 63.

The packing ceiling **reproduces our merged #1023's width-8 free-concentration relaxation**
(0.0019559187537, cap 45), here in independent fractional-count arithmetic. #1023 already shows that
no realizable width-8 re-hosting moves the endpoint. Two related values in open #1293:
- its certified D/E value, 0.0017386, bounds the fixed full histogram;
- its screening extremum, 0.0161, ranges over all rank-mass-preserving repackings, including the
  local word.

**What the table says, and what it does not say.**
- **With the shipped local word fixed (439 helpers), centre free + in-window children fails.**
  Reaching 1/99 that way needs rank-16 children or a second unpaid coordinate.
- **That is a statement about the shipped helper mass, not about the window.**
  - With ideal data shapes and at most 332 width-8 helpers (cap 45), centre free reaches 1/99
    inside the window. The k = 332 / 333 boundary is certified.
  - A second unpaid coordinate with in-window ideal shapes reaches 1/99 even at the full copy
    charge.
  - Fewer helpers or a changed coverage law can therefore substitute for a wider window.

### O1 (copy charge 63)

Take no helpers, every data register as a single rank-7 climb, and the nine rank-7 copies. The bill
then exceeds 1 at a = 1/99 at caps 42, 45, 50, 53 and 63:

| Idle cap | 45 | 53 | 63 |
|---|---:|---:|---:|
| Helper-free ceiling | 0.006794 | 0.007944 | 0.009665 |

Cap 63 leaves only a 4.3% margin. Under the premises, **no helper design, data shape or idle packing
reaches 1/99 while the bit copy charge stays at 63 per call.**

### O2 (centre path shared by two calls, copy charge 31.5, full-frame width-8 helpers)

The table gives the largest helper count that still reaches 1/99. Each count k is certified: k
passes and k + 1 fails.

| Idle cap (halving depth) | 45 (HD 2, the record) | 50 (HD 3) | 53 (HD 4) |
|---|---:|---:|---:|
| Max width-8 helpers | 104 | 131 | 145 |

The comparison uses the design-free floors of format-limits section D. They apply to full-frame
helpers in its drop-free monotone-chain model and are cited as argued premises: at least 138 strict
and at least 212 sink-only.
- **Sharing the centre path is not enough for full-frame helpers at halving depth ≤ 3**, because
  104 and 131 are both below 138.
- **At halving depth 4, which the merged elementary-cover row bound admits, the count is 145 ≥ 138**,
  so the strict-floor obstruction no longer holds there.
- The sink-only floor (212) is out of reach at every admissible cap.

Narrower helpers are listed in the receipt as budget counts only. The floors are width-free for
full-frame helpers, and narrower helpers face their own (higher) cover floors, so no floor
comparison is made for them.

### Joint surface (width-8 helpers)

This table gives the most helpers (including totals) that still reach 1/99. Each cell shows the
three admissible caps, 45 / 50 / 53, and "none" means no helper count reaches it.

| Copy charge per call | 0 | 7 | 14 | 21 | 28 | 31.5 | 35 | 42 | 49 | 56 |
|---|---|---|---|---|---|---|---|---|---|---|
| Ideal data | 332/346/353 | 281/298/307 | 230/250/260 | 180/203/214 | 129/155/168 | 104/131/145 | 78/107/122 | 28/59/75 | none/11/29 | none |
| Shipped data shapes | 215/236/246 | 164/188/200 | 113/140/154 | 63/92/107 | 12/45/61 | none/21/38 | none/none/15 | none | none | none |

For shipped data ladders, format-limits D raises the full-frame floor to 222. Even with the centre
path free, the shipped-shape row stays below 222 at cap 45 (215). It exceeds 222 only at caps 50
and 53.

### The complex side and #1272

The same code reproduces #1240's complex ceiling, 0.0016900541090 (m = 73, w = 896/9, cst 64,
cap 51), and prices #1272's combined lever.

| Complex lever | Root a | At 1/99 |
|---|---:|---|
| Centre free + rank-16 children (#1272's ×6.5) | 0.011008 | pass, but needs children beyond the stage window h = 9 |
| Centre free + rank-9 children (in window) | 0.008128 | fail |
| Centre free + two unpaid coordinates (shipped word) | 0.009410 | fail |
| Two unpaid + rank-9 children (in window) | 0.010911 | pass |

So #1272's headline combination relies on rank-16 children. In-window alternatives exist: a second
unpaid coordinate with rank-9 shapes, or, on the bit side, fewer helpers.

## Bindings and replay

**Bindings (B1–B5).**
- A record names the frontier1094 certificate: the selected record, or a checkpoint once the
  frontier moves.
- The certificate pins `PR589-EXPECTED.json` (`b9f0e5ca…`). That record pins the bit word
  (`e3e301e6…`), the profile, the endpoint, the halving depth and the row coefficient.
- The following source lines are required verbatim:
  - the PR510 row formula and guard (`assemble9.py`);
  - the elementary-cover row bound (`row_bound.py`);
  - the adaptive halving depth (`global_k.py`).

**Positive control (P1).** With the inherited surcharge, the full selected profile accepts
0.001733427039589844234749 and rejects the next 1e-24 point. Without the surcharge, the next point
would pass.

**Replay (R1–R3).** Each register's frame itinerary is replayed through D, A, B and C, with
rational ranks of the E8 lines; every change is a climb.
- The local histogram equals the record: `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, mass
  5,129.
- The class split:
  - sources and targets, mass 777 each;
  - 430 helpers, mass 3,440;
  - 9 retained totals, mass 72;
  - 9 rank-7 copies.
- The profile equals 288 local words plus the idle children.

## Controls ([test_package.py](test_package.py): 15 tests, < 2 s)

- **Interval engine.** Its intervals contain the float values.
- **Selected endpoint and neighbours.** Includes the case without the surcharge.
- **Relaxation steps.** One instance each of merging climbs, idle mass at the largest rank, and the
  surcharge.
- **Guards.** The coverage-law and rank guards hold, and the halving-depth cap table is checked:
  - caps 45/50/53/55 for halving depths 2–5;
  - only depth 2 is admissible under PR510;
  - depths 2–4 are admissible under the elementary-cover bound.
- **O1.** It fails at every cap.
- **O2 boundaries.** 104/105 at cap 45, 131/132 at cap 50 and 145/146 at cap 53.
- **Centre free in window.** 332 helpers pass and 333 fail.
- **Tampering.** A tampered replay gate is rejected, and so is a tampered record histogram.
- **Receipt.** The receipt values are checked.

## Reproduce

```sh
python3 -I -B research/bit-revision3-levers-seed03/verify.py           # ~13 s; PASS_BIT_REVISION3_LEVERS (RESULT.json byte-identical)
python3 -I -B -m unittest discover -s research/bit-revision3-levers-seed03 -p test_package.py
python3.12 scripts/research_package.py --package research/bit-revision3-levers-seed03
```

## Scope and what is not claimed

- **Relaxation, not construction.** This is a relaxation, not a construction, and κ is unchanged. A
  pass row is only a target.
- **Conditions on the fail rows.**
  - All fail rows hold under the coverage law, the in-window child shapes, rank-7 copy carriage and
    the stated idle cap.
  - O2 also needs format-limits D's argued floors for full-frame helpers, and holds only at halving
    depth ≤ 3.
  - O1 holds at every cap, including 63.
- **Rank-16 children** lie beyond today's stage windows (h = 8 bit, h = 9 complex). Using them is a
  different architecture.
- **Inherited conditions.** The inherited all-size/compiler, hosting, precision/tape,
  analytic-transfer and PR589 H1–H5 conditions are untouched.

## Overlap and credit

**Overlap**
- **#1240** (Mister-Meeseeks; prepared by Douglas Colkitt): the complex local-word ceiling and
  `levers.py`. This package is the bit-side analogue, in independent code.
- **#1272**: the proposed revision 3.
- **#1293** (navinor): proof and certification of Colkitt's a < D/E diagnostic, plus a bit
  screening extremum. Reconciled above.
- **Merged `research/format-limits`**: sections A, A.4, A.7 and D.
- **#974** (avirazza): PR589 interface budget and bit headroom, including COPY deletion.
- **Our merged #1023**: the packing ceiling reproduced above, plus width-7 hosting. It models
  windows; only the timing of hosting is unchecked.
- **#1281** (mightyOil): partial width-7 optima.
- **The card's helper-interface question** is saturated by #1194, #1311, #1179, #1253 and #1128.
- **The register-model card** is done in PR #1333 (bitplane; claim #1317).

**Credit**
- DreamingOfClouds (PR589, and format-limits) and eumemic (PR555): the bit supplier.
- DaysSky and the PR510/PR442 template and hosting lineage.
- The elementary-cover row bound authors.
- Douglas Colkitt (#1240, #1272) and navinor (#1293).
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via
  Claude Code. Parallel read-only scout and judge subagents ranked the question. A post-PR
  adversarial review found the halving-depth error and two overclaims, all corrected here. New
  material is Apache-2.0.

## Open next questions

1. **At which halving depth does a concrete bit construction run, under which row bound?** O2 holds
   at depth ≤ 3 and flips at depth 4.
   - First step: price the selected profile's row coefficient under the elementary-cover bound at
     depths 3 and 4, and check the other finite guards.
2. **Can a centre-path-sharing mechanism keep every data register a single rank-7 climb, with at
   most 104–145 full-frame helpers?**
   - First step: replay a two-call shared-centre toy on a small E8 sub-word.
3. **What does each in-window alternative to rank-16 children cost?** The alternatives are a second
   unpaid coordinate, or fewer helpers (≤ 332 with the centre free).
   - First step: price a second unpaid coordinate in format-limits' (Dfc)/(Win) accounting, together
     with its invoice.
