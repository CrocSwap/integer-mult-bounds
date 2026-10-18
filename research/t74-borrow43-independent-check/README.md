# Independent check of record candidate PR #2269 (T74 borrow43)

**Status: independent verification. The construction claims reproduce, so no counterexample was found. Evidence,
metadata and accounting defects are listed below. No new κ, no frontier change, and no endorsement of the claimed κ
beyond what is checked here.**

PR #2269 (Jeremy Kothe, head `b479fc5567bc09ab9185bffe89b62594f36d74e5`, `research/gmx-t74-borrow43/`) claims the
conditional κ = 0.0016962471390584742…, which is +1.4% over the selected record. It adds 43 borrowed-helper
aliases, taken from Cinna Davis's anticipatory dirty borrowing (#2226), to the T74 pivot-566+554 local words. It then
re-fills the 666-call hosting and prices the result under the PR1673 capped phase-cell fusion outer.

When this check started (2026-10-15 03:50 UTC), nothing committed checked the *new* 437-helper fill independently.
The package's `evidence/INDEPENDENT.json` describes a different, pre-borrowing 480-helper fill.

This package rechecks the new construction with fresh standard-library code. It imports, executes and copies no code
from #2269, #2226 or #2260. A reviewer measured the longest shared token run against 19 PR scripts at 27 tokens.
Every input (40 blobs) is pinned by its git blob id and SHA-256 at the head commit.

## What reproduces exactly

| Check | Script | Result |
|---|---|---|
| **Words** (both `BORROW-WORD-43base/extra`) | `words_check.py` | Each of the 43 warps has an invertible G over GF(2), dim U = dim E and G·span U = span E. Each symplectic K_G maps L_U to L_E, so its Fourier rank is 0. All aliases are "high" (no anticipatory terms). Frame climbs are nested. An exact replay over ℚ⟨F₄₃⟩ with every live register arbitrary (dirty) gives Yᵢ ← Yᵢ + Xᵢ and restores the other 549 live registers and the 76 zero buffers; the dual orientation also replays. The recounted paid profiles are 43base `{1:2351,2:501,3:414,4:129,5:42,8:8}` and 43extra `{1:2339,2:509,3:418,4:125,5:42,8:8}`, with mass 5385, 437 helpers and widths `{4:36,5:9,7:36,8:116,9:240}`. |
| **Fill** (`OWNERS.json.gz`, 291,042 rows) | `fill_check.py` | There is exactly one role per (call, live helper) over 666 × 437, and none of the 43 removed helpers appears. Widths equal the word widths. 1,332 windows are rebuilt from the event stream and equal PLAN's, and every role is strictly inside its window. Families are correct, no role lands on the caller's active pair, and each family hosts at most one helper per call. On 149,184 bins slices are disjoint, within rank and prefix-filled. The recounted idle remainders `{1:23976,3:8673,5:813,7:150,48:24479}` equal CONSTRUCTION/SPEC. |
| **Price** | `price_check.py` | The global profile is composed from *our* recounts as 249·P_gauge44 + 417·P_extra + idle, and equals `PROFILE.json`. Mass is 4,816,512 = 73·66304 − 23680. The moment root is bracketed exactly to width 10⁻¹³⁰ with a fresh certified atanh/exp evaluator on a 2⁻⁸⁰⁰ grid. The claimed b lies inside the bracket and `complex_lower` + 10⁻⁹⁰ is rejected. κ = ⌊(1−2·10⁻¹⁰⁰)(b−10⁻¹⁰⁰)⌋₁₀⁻¹³⁶ − 10⁻¹¹² holds as arithmetic, and the strict-assembly κ is ≈ b/(1+b) = 0.0016933747…. |
| **Positive controls** | | The unborrowed canonical words reproduce the old profiles (`{5:82}`, masses 5590 and 5594) and equal the pinned 566 words under relabelling. The pre-borrowing T37 parent fill reproduces its SPEC, PLAN and PROFILE (159,840 roles). |

Each script has targeted negative controls, 3 to 12 per script, including:
- dropping a warp or an inverse warp;
- perturbing a coefficient;
- charging a warp as a climb;
- duplicating a helper;
- overlapping slices;
- moving a role outside its window;
- tampering with idle;
- moving the moment root by ±10⁻⁸⁰.

Each control is rejected by the check it targets. The gain attributable to borrowing is
Δb = 1.64922·10⁻⁵ over #2044's b = 0.0016797549561255445….

## Defects and open obligations found (none changes b as checked)

1. **No admission receipt for the borrowed supplier.** Eight files are byte-identical to the pre-borrowing #2044
   package: `evidence/INDEPENDENT.json`, `evidence/ASSEMBLY.json`, `evidence/FULL-ADMISSION.json`, `PRICE.json`,
   top-level `SPEC.json`, `evidence/ADMISSION-CONTROLS.json`, `evidence/GEOMETRY-CONTROLS.json` and
   `evidence/OUTER-DISCOVERY.json`. `INDEPENDENT.json` pins an OWNERS file (`cdfdcdec…`) that is not in the tree. The
   "fresh receipt" exists only as PR-body text. The top-level `PLAN.json` is the borrowed version, despite the README's
   "unchanged" wording, so the top-level PLAN and SPEC disagree. `new/SPEC.json` and `new/PLAN.json` are the
   consistent pair.
2. **Unpriced zero buffers.**
   - Each call's cleanup uses 76 private zero buffers outside the 437-helper inventory. #2269's own emitter
     (`new/code/borrow/bw_emit.py`) allocates all of them up front, giving a peak of 437 + 76 = **513 fields**,
     against 480 unborrowed. Lazy allocation would give 481 forward and 485 in the dual orientation.
   - `code/assemble.py` charges `physical = data + R + 8 + 2` with no buffer term. #2260 did charge its 75 buffers,
     and #2226 PROOF §4 lists buffer allocation as an open pricing obligation.
   - Charging the 76 as dedicated families leaves the stock bits (2644) and the row coefficient (≤ 19547 < 20161)
     unchanged.
   - Only a model that hosts the buffers inside idle children would move b, and that model was not evaluated.
3. **X2 not checked: disjoint pending axes across children sharing a physical family.** 37,408 of the 54,145 hosted
   families carry slices of two or more children. The 7,300 actual 73-column charts are not checked either. An X2
   failure would force a repack and change the idle profile, and with it b. The package attests this only through its
   own pipeline; `DATA-PHASES.json` is shipped only inside a vendored tarball.
4. **Metadata errors.**
   - `CLAIM.json` has `"construction_improvement": false`, but the gain is a profile change.
   - The status string is inherited.
   - `gain_over_claimed_leader` (1.28346·10⁻⁵) is an outer-ledger gain set against the strict-assembly κ (gain
     9.962·10⁻⁶).
   - The README's lineage section mislabels the new strict κ as the old package's.
   - "8 width-4, 35 width-5" and "5590 → 5385" hold only for the gauge44 word. The extra word removes `{4:4, 5:39}`
     and goes 5594 → 5385. Helpers 533 and 554 widen from 7 to 8.
   - Stale numbers remain in the edited outer notes. The vacuous `or True` assertions found by #2286 persist; those
     blobs are byte-identical to #2044's.

## Not checked

- **Outer stack.** κ = b depends on PR1673's capped phase-cell fusion outer, with PR1758 gauge-free interiors, PR1786
  fine-prime padding and the union schedule. All are open PRs. Only the arithmetic map b → κ is checked here. Their
  written side conditions were inventoried at #2044's point in #2286; `outer/check_ledger.py` and `vendor/` are
  byte-identical here, but the point moved (r₀ = 10⁻¹⁰⁰), so that inventory was not re-run.
- **Native level.** Not checked: the native lowering (`run_native_borrow.py`, warp recipes, both orientations,
  wrappers, precision/tape, prefix bits, invoice, controller, the Lemma G label stage) and the exact Clifford lifts and
  phases of K_G. Only K_G's binary-symplectic image, which fixes the Fourier rank, is checked. The whole borrowing gain
  rests on the rank-zero K_G handoffs: charging the warps as plain frame changes would give local mass 5581 rather
  than 5385.
- **Assembly.** The 47 strict inequalities and the 39-step bootstrap are not recomputed.
- **Cost conventions** are taken as the specification: cleanup at FULL is free, rank-zero warps are free, and the
  COPY rule. The positive controls show these scripts agree with the package's convention; they do not validate it.
- **Inherited premises** of the T74/PR1319 lineage and the PR589 bit supplier.
- **Successor #2288** (exact frame refit of the borrowed gauge44 word) changes the gauge44 word, so the word checks
  here do not carry over to it.
- **Successor #2281.** It reuses byte-identical words, OWNERS and PROFILE, so the word and fill checks carry over; its
  10⁻³⁰⁰⁰ endpoint is not certified here.

## Reproduce

The inputs are in the open PR, not on main. From a checkout of this repository, Python 3.10+ standard library and
`git`, in about 35 s:

```sh
python3 -I -B research/t74-borrow43-independent-check/check_all.py --fetch
```

`--fetch` downloads `refs/pull/2269/head` only if commit `b479fc55` is absent; every input is still verified against
its pins. Alternatively, pass `--blob-dir DIR` for an exported copy (`git archive b479fc55 research/gmx-t74-borrow43`).

Expected last line:

```text
PASS_T74_BORROW43_INDEPENDENT_CHECK words=PASS fill=PASS price=PASS runner_controls=3 commit=b479fc5567bc mode=git
```

The receipts `*_check.receipt.json` and `check_all.receipt.json` are deterministic. `--out` regenerates them.

## Open next questions

1. **X2 and the 73-column charts for the 437-helper fill.** *Why it matters:* it is the one unchecked fill condition
   that could change b. *First step:* extend `fill_check.py` with the T74 template's `port_restriction` and the
   PR558/T74 `DATA-PHASES` pending axes. *Blocked by:* the phase data ships only inside a vendored tarball.
2. **Price the cleanup buffers.** *Why it matters:* the emitter's eager 513-field peak is unpriced. *First step:* a
   `physical_stock_identity` with a buffer term, or a lazy-allocation emitter with an explicit 481/485 peak bound.
   *Blocked by:* an author or maintainer decision on the buffer model.
3. **Fresh admission receipt.** *Why it matters:* the shipped evidence describes the pre-borrowing supplier.
   *First step:* commit the `verify_release.py` receipt for `b479fc55`. *Blocked by:* the author.

## Credit and provenance

- **Checked work:**
  - Jeremy Kothe (PR #2269, T74 lineage, previous records).
  - Cinna Davis / 1337isnot1337 (PR #2226 anticipatory dirty borrowing, the alias rule and K_G handoffs).
  - Dugongue (PR #2260, selective borrowing with buffer pricing).
  - PR1319/PR1625/PR1297, mdumitrean and others (the T74 lineage).
  - icekylinx (checker lineage).
- **Related:** Josie Elliston's seed67 owner auditor, an example rule set that was not reused. #2311 (same account,
  a separate session) independently audits the different #2260/#2265 T8 selective-borrowing supplier. It is
  complementary and shares no code with this package.
- **Base and assignment:** base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Sprint track 75–84
  (independent verification), OS seed 76. No pinned coordination issue existed, so the claim was recorded locally.
- **AI assistance:** prepared for Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic). Separate
  agents wrote the word, fill and price checks. Two adversarial reviewers checked independence and claim coverage,
  and fixed one overstated diagnostic and one tautological control. The main session reran every command.
  Apache-2.0.
