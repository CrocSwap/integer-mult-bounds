# Bit-supplier helper-deletion ladder (d = 0..6)

**Bit headroom only. No new κ. No word is built here.** The selected record is complex-bound. Rows with d ≥ 1
price hypothetical words that have d fewer width-8 helpers, under a declared local-profile model. d = 1 is PR1043's
R438 word (open, not admitted) with PR2423's re-hosting. PR1250 (seed11) found that helper 470 is the only removable
helper of the fixed word, so d ≥ 2 needs changed words. This ladder prices what those words would be worth.

## Result

R = 439 − d. S = 3996 − 9R width-8 slack units per replica. The endpoint c is accepted at c and rejected at
c + 1e-24 by both pinned engines.

| d | R | S | certified optimum (unique) | window splits | c TEMPLATE | c RANK1 | c RANK7 | % vs PR589 (T/R1/R7) |
|---|---|---|---|---|---|---|---|---|
| 0 | 439 | 45 | 9×(42,5) | 10/10 | 0.001733427039589844234749 | (same) | (same) | 0 / 0 / 0 |
| 1 | 438 | 54 | 10×(42,5)+1×(42,4) | 22/22 | 0.001734802047828389852783 | 0.001735999416922188281944 | 0.001734846264120199151475 | +0.0793 / +0.1484 / +0.0819 |
| 2 | 437 | 63 | 12×(42,5)+1×(28,3) | 26/26 | 0.001736238589146810207048 | 0.001738638963216633253344 | 0.001736327170598942735353 | +0.1622 / +0.3007 / +0.1673 |
| 3 | 436 | 72 | 14×(42,5)+1×(28,2) | 30/30 | 0.001737652736279473456500 | 0.001741261678825470976241 | 0.001737785828526572282621 | +0.2438 / +0.4520 / +0.2515 |
| 4 | 435 | 81 | 16×(42,5)+1×(14,1) | 34/34 | 0.001739118212671177105905 | 0.001743941623958466180686 | 0.001739295973174498110179 | +0.3283 / +0.6066 / +0.3386 |
| 5 | 434 | 90 | 18×(42,5) | 19/19 | 0.001740604775296424266918 | 0.001746648581745032521636 | 0.001740827361879356617556 | +0.4141 / +0.7627 / +0.4269 |
| 6 | 433 | 99 | 19×(42,5)+1×(42,4) | 40/40 | 0.001741991196114600260000 | 0.001749260420895977867718 | 0.001742258732839957487271 | +0.4941 / +0.9134 / +0.5095 |

The local-profile models below add their delta once per deletion to PR589's R439 profile
{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}. Each delta removes rank mass 8, and the script checks this.

- **TEMPLATE**: d·{1:−2, 2:+2, 3:−1, 7:−1}, PR1043's measured delta.
- **RANK1**: d·{1:−8}.
- **RANK7**: d·{7:−1, 1:−1}.

**Increments.** Steps per deletion, in % of PR589's c, for d = 1..6:

- TEMPLATE: 0.0793, 0.0829, 0.0816, 0.0845, 0.0858, 0.0800.
- RANK1: 0.148–0.156.
- RANK7: 0.082–0.088.

The ladder is close to linear, at about +0.082% per deletion for TEMPLATE. The steps alternate because the
partial-slot layout changes with S mod 5. The prior float screen gave about +0.079% per deletion. That figure is the
d = 1 TEMPLATE step, and later steps are slightly larger.

**Labels.** Neither alternative model is an envelope. RANK1 is not an upper envelope: with the same mass, {1:-10, 2:+1} gives c = 0.0017361170 and {1:-64, 7:+8} gives c = 0.0017452803 at d = 1, against RANK1's 0.0017359994 (adversarial reviewer). "RANK7" is not a lower envelope. With mass held fixed, removing {7, 1} is worth more than the TEMPLATE
delta, because g(r) = r(64/r)^c is concave, so 2g(2) > g(1) + g(3). TEMPLATE is the lowest of the three models in
every row. It is not a lower bound over arbitrary local changes either. Lowering eight rank-7 children by one each
(mass −8, no count change) would be worth less still. That case was not computed.

**Layouts.** The optimum stays "fully idle 42-slots first". The leftover S mod 5 units go to a single partial slot:
(42,4) for residue 4, (28,3) for 3, (28,2) for 2 and (14,1) for 1. Runner-up gaps in moment units are all
positive, between 5.9e-8 and 3.3e-7.

## What was checked (all in `deletion_ladder.py`, receipt `RECEIPT.json`)

1. **DP.** PR2423's `certify_optimum` (exact top-3 interval DP) runs in a fixed-point loop. A candidate from the DP
   at c0 + 1e-24 is priced, and the DP at the row's own c + 1e-24 must return the same layout. It does in every row.
   The optimum and the runner-up are certified unique. Every one of the 21 rows is cross-checked by PR2423's
   branch-and-bound `exhaustive_topk`. Layouts covered per d are 3,160,688; 10,556,685; 30,058,381; 75,757,148;
   173,394,328; 367,063,269; and 728,466,365. Each count equals an independent generating-function count, which
   also reproduces PR2423's counts at S = 45 and 54. The exhaustive pass was tractable for every d (about 5 s at
   S = 99), so it was not dropped anywhere.
2. **Windows.** Every split of each (capacity, u) count over the two children of its capacity class was tested
   (10–40 per d). seed72 `maxflow_assign` and PR2423's all-subsets `hall_check` agree on every split, and all splits
   are feasible at every d. For the all-in-children-6/7/8 split, an explicit placement of 9R occurrences per
   replica was built and checked:
   - built with seed14 `allocate` (R set on that module instance only);
   - equal slot for slot to PR442 `hosting_core.expand`;
   - audited by seed14 `placement_audit` and `owners_for_replicas` and by PR2423's `audit_slots`;
   - remainders equal to the DP optimum.
   At d = 1 its slot-list sha256 equals PR2423's placement.
3. **Endpoints.** PR1023 `packing.endpoint` (both engines plus the inherited surcharge) runs for 21 rows. The
   hosted rank mass is invariant at 1,808,352, and there is one idle child per slot.
4. **Controls (88 negative, plus the positive ones below).**
   - d = 0 gives PR589's c in all three models, and the layout is PR589's selection.
   - d = 1 TEMPLATE local equals PR1043's certified profile, and c = 0.001734802047828389852783.
   - d = 1 RANK7 local equals PR2423's transported-word profile (b), and c = 0.001734846264120199151475 = PR2423's c_b.
   - PR2423's `verify_rehost.main` is replayed end to end (PASS, 29 controls) and agrees with c_a, c_b, the S = 54
     DP certificate and the placement hash.
   - Negative controls (each must be rejected):
     - Wrong slack S + 1 and S − 1, at every d. Rejected by the hosted-rank-mass check and by the window-demand total.
     - R + 1 supply into the optimum.
     - A DP with the optimum's rarest move dropped, compared against the exhaustive pass.
     - The runner-up claimed optimal.
     - c + 1e-24 accepted, for each of the 21 rows.
     - A local model with mass −7.
     - A local model with negative counts.
     - Tampered vendored bytes.

## Not verified / scope

- **No word exists for d ≥ 2.** The local models are declared, not derived. Real changed words could have other
  local deltas (see Labels above), other A-side costs, or fail PR1043-style legality and replay checks.
- **Fixed inputs.** W = 28416 (live stock 2KvT) and the PR589 frame, schedule, windows and capacities are held fixed
  for every d. This is the same assumption PR2423 makes at d = 1.
- **Slot model scope.** The optimum is over the PR1023 no-bank, width-8-only slot model. Width-7 conversions, banks
  and changes of slot capacities are out of scope. Window feasibility is shown a posteriori for the slot-model
  optimum, and it holds, so no window-constrained re-optimisation was needed.
- **Engines.** Python stdlib engines only. The native C++17/Boost lane, which PR1043's review requests, was not run.
- **Runtime.** About 77 s on CPython 3.14.4, Linux x86_64, no network. Deterministic: `--check RECEIPT.json` passes
  byte for byte. The script refuses `python -O`.

## Reproduce

From the repository root, CPython ≥ 3.10, standard library only, about 80 s:

    python3 -I -B research/bit-deletion-ladder/deletion_ladder.py --check research/bit-deletion-ladder/RECEIPT.json

The expected final line starts with `PASS_BIT_DELETION_LADDER d=0..6 exhaustive=21/21 windows_feasible=7/7`. All
results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Open next questions

- Is there any changed word with a second removable helper? PR1250 says not on the fixed word. Pricing (d = 2) is
  worth about +0.083% c over d = 1 under TEMPLATE.
- What is the true worst-case local delta per deletion, given the word's legal local moves? That would give a
  certified lower envelope instead of three models.
- None of this moves κ unless the complex side stops binding. Bit headroom at d = 6 is still above complex.

## Credits and licence

- PR1043 (Ali Romman): the R438 deletion and its certificate (vendored).
- PR2423 (this author): the re-hosting DP, windows, placement and transport, vendored with pins.
- PR1023: the slot model and `g_interval`.
- seed72 and seed14 packages: windows, allocation and audits.
- PR589 / PR555: the selected bit word.
- PR1250 / `bit-source-substitution-seed11`: the result that only helper 470 is removable.

Prepared by Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). An AI builder
agent and an adversarial AI verifier were used. The verifier independently recomputed all 21 rows (layouts by
exhaustive enumeration, endpoints by Decimal bisection, windows by a 512-subset Hall test) and matched every
digit. No independent human review is claimed. Apache-2.0.
