This composition admits **κ = 0.001600682403612293**, an increase of **0.0384302%** over the pinned PR569 value 0.001600067494703216. The conservative recurrence, retaining the complex bad-residue surcharge, admits **0.001600682400830496**. This is a modest constructive improvement, not the materially larger gain sought by the broader research pass.

[RESULT.json](RESULT.json) records the result and proof counts. A fresh [portable replay](portable-replay/RESULT.json) rebuilt the new provider, replayed both scalar orientations and every phase edge, reconstructed physical owners, and ran the full invoice and outer admission in 18 stages. Its [receipt](portable-replay/RECEIPT.json) binds all 94 output artifacts and all 18 stage logs. The complete 9.4 MB replay is retained, with no Python caches.

The construction combines three independently useful changes:

1. PR568's multi-cut kernel relations use donors at different frame epochs, including two already-scattered output targets for each of four new odd-pivot relations. Three of its seven added relations overlap PR569; four are additional. PR567's extra relation is already present and supplies no separate improvement.
2. PR569's 32 entrance promotions still apply to the PR568 word. They change 96 gate frames while preserving the scalar operations. This alone does not guarantee a gain after physical hosting.
3. The joint-basis nomination replaces the old 69-gate A prefix with 57 gates, using 40 entrances instead of 44. [compose_prefix.py](compose_prefix.py) checks the exact unchanged suffix and fixed fields before combining that prefix with the new B word. Complete native, phase, and omission checks establish the resulting word independently of the prefix optimizer's optimality claim.

The resulting local paid profile is `{1:2352, 2:580, 3:336, 4:192, 5:56, 6:56, 8:8}`. Its ordered helper widths have inventory `{9:288, 8:128, 7:32, 5:48, 4:8}`, matching PR569. Relative to the old width-seven provider, the paid-profile difference is `-12 H2 + 8 H3`. For every positive moment exponent b, this changes the rank-weighted moment by `24*((73/3)^b - (73/2)^b) < 0`.

[relabel_owners.py](relabel_owners.py) realizes the matching inventory by four helper-label swaps: `299 ↔ 271`, `301 ↔ 283`, `375 ↔ 295`, and `377 ↔ 307`. All physical families, call times, owners, children, ports, widths and offsets remain the same as PR569. The 63 selected calls use the new provider; nine calls retain the already verified plain four-cold provider. The historical registry key `width7_eight` names the new composed provider in this package.

The final profile is `{1:169056, 2:40428, 3:26472, 4:13824, 5:4032, 6:4032, 7:48, 8:576, 48:1808}`. Fresh physical replay checks 36,288 helper roles, 6,390 actual charts, 27,468 cross-replica roles, live stock 7,168, physical stock 7,682 and rank mass 520,704. The invoice independently counts 11,614,452 real-component primitives and 5,751,322 coefficient-work primitives. All nine finite inequalities pass.

The new local proof checks all 728 columns in both orientations, all 3,004 directed phase edges and 224 endpoint adapters. It rejects 135 kernel-omission cases, eight rank-five omission cases, 11 independent local mutations, five wrapper mutations, 16 physical-owner mutations and 93 assembly mutations. Timing-only phase changes are accepted for both providers; substantive phase changes are rejected. Both exact rational moment engines agree on consecutive 10^-24 endpoints. Both recurrence models pass all 47 outer inequalities and seven bootstrap rounds.

To reproduce from the repository root, use Python's standard library and explicit paths to the pinned PR564 source and three complete prior replays:

```sh
python3 -B research/structural-gain/frontier-composition/reproduce.py \
  --source /path/to/pr564/research/complex-allcold \
  --baseline /path/to/complete-pr564-replay \
  --prior-providers /path/to/complete-pr569-provider-replay \
  --prior-global /path/to/complete-pr569-global-replay \
  --work /path/to/fresh-composition-replay
```

The output directory must be new. The driver validates the source manifest, complete prior stage lists, logs and artifact inventories before reuse. It rebuilds the PR568 word, applies the 32 frame promotions, composes the retained literal prefix, and runs every new local and global proof stage. It compares the rebuilt word and deterministic local artifacts with frozen hashes; phase timing is excluded only from the semantic digest. No optimizer or network access is needed. This replay took 149.5 seconds locally, including about 101 seconds for exact phases.

The prior replay commands are documented in [the provider driver](../../larger-gain/providers/README.md) and [the global package](../../larger-gain/global/README.md). PR564 source commit is `c18417b02b80594b2ca1c8c21185d28befafc935`. PR569's mathematical source was pinned at `f1db606a1416359229f944946667338305208064`; packaging commit `1424da81263a5305b35e4cf74ef686c275f03f3f` adds seven previously ignored logs with unchanged manifest hashes. [SOURCE-PINS.json](SOURCE-PINS.json) and [REPRODUCTION-PINS.json](REPRODUCTION-PINS.json) record recipe, code and artifact bindings. Retained `.log` files are proof artifacts and must be included when packaging despite the repository's general ignore rule.

Earlier exploration is retained with narrower scope. `compacted-nomination/` simply shortened residuals in old bins and priced below PR569. The expanded MILP produced an aggregate allocation whose literal expansion failed; `repacked-nomination-expanded/WINDOW-SOLUTION.json` is not an admitted owner plan. The capacity-ceiling receipts are relaxations, not physical admissions. `global-replay/` records the first complete admission; `portable-replay/` records the fresh end-to-end reproduction used by the final result.

The result remains conditional on the inherited all-size compiler, common-label and mutable-source realization, whole-call hosting, precision and tape bounds, and analytic-transfer assumptions H1–H5. The unchanged PR543 bit supplier is cited and repriced, not rebuilt. No unconditional multiplication theorem, complete Lean certification, or general worst-case O(1) indexing theorem is claimed. This research package does not modify or publish changes to PR569.
