# Centre-path sharing: exact overhead budgets on the actual selected profiles

**Planning result for the `centre-path-sharing` card. No construction, no physical sharing is
admitted, and no new κ.**

[PR1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708) and
[PR1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748) construct the two halves of a
two-call shared centre phase at the scalar-macro level. Their open blocker is the overhead ΔH:
preparation, routing, restoration, ownership and hosting. PR1708 also screened the favorable
relaxation: sharing lifts the complex cap to about 0.00321, the bit supplier then binds, and the
whole-bound gain is at most 3.4536%.

This package prices the lever on the **actual** selected #1094 histograms (its real idle
remainder, not ideal packing). It gives sharp integer budgets for ΔH and states what the route
needs for the card's 10% target.

## Model

Sharing one centre path across `k` calls keeps every child of the selected complex histogram
except the shared rank-8 centre children. Their count goes from 1,152 to 1,152/k, and the coverage
identity becomes `72W + (64/k)N`; this is checked exactly. Overhead is modeled as extra paid
children of a single rank `r`.

The moment is linear in child counts. Each budget is therefore a **sharp integer**: that many
extra children pass the exact moment test at the stated point, and one more fails. Exact moment
enclosures come from Navinor's
[selected-suppliers-de-diagnostic](../selected-suppliers-de-diagnostic/README.md). κ uses the
retained seven-level bootstrap, with all 47 outer slacks checked, from Wronskode's
[seed81 recheck](../frontier1042-invoice-audit-seed81/README.md). Both are loaded unchanged as Git
blobs at the base.

## Results

**1. With any sharing, the complex side stops binding.** At the bit endpoint
`c = 0.001733427039589844234749`, the actual-profile residual `f(c) − 1` is:

| k | rank-8 children | centre charge per call | f(c) − 1 | Rank-1 budget (per call) | Rank-8 budget (per call) |
|---:|---:|---:|---:|---:|---:|
| 2 | 576 | 32 | −4.25·10⁻³ | 4,415 children (30.66) | 553 children (3.84) |
| 4 | 288 | 16 | −6.46·10⁻³ | 6,710 (46.60) | 841 (5.84) |
| 8 | 144 | 8 | −7.57·10⁻³ | 7,858 (54.57) | 985 (6.84) |
| 16 | 72 | 4 | −8.12·10⁻³ | 8,432 (58.56) | 1,057 (7.34) |
| 144 | 8 | 4/9 | −8.61·10⁻³ | 8,942 (62.10) | 1,121 (7.78) |

The two budget columns are overhead children (record total, then per call) that keep the full
bit-limited gain.

With `k = 2` the result is bit-limited, `κ = 865213734911801/5·10¹⁷ = 0.001730427469823602`
(+3.4536%). This reproduces PR1708's figure on the actual histogram.

**2. ΔH budget for two-call sharing.** Sharing saves 32 rank-units of paid mass per call. Of that:

* **Full +3.4536% kept:** ΔH may consume about **30.5–30.8 units per call** at any overhead rank
  from 1 to 72. For example: 4,415 rank-1, 553 rank-8 or 92 rank-48 children in total.
* **Any gain over the selected record:** ΔH must stay below about **31.9–32.0 units per call**.
* **Exact break-even control:** re-adding 575 rank-8 children still gains; 576, which recreates
  the selected histogram, does not.

The full table is in [RESULT.json](RESULT.json).

**3. Why the budget is so large.** The complex side currently binds by only **1.23–1.33 paid-mass
units per call**. Removing 177 rank-1, 23 rank-8 or 4 rank-48 children from the selected record
makes the bit side bind. Any mechanism netting that much on the complex side reaches the same
+3.45% cap.

**4. The card's stop rule triggers on its own.** Even ideal sharing gains under 10% on the whole
bound. For **+10%** (κ ≥ 1.1 × selected) with the complex side ample, the **bit endpoint must
reach `921658892752012102303/5·10²³ ≈ 0.0018433`**, 1.0634× its current value.

On the cited PR589 bit histogram (deficit 10,272, `T = 32`), that needs a net paid-mass reduction
of at least **649 units**:

* as 649 rank-1 children, about 20.3 per replica; or
* as 16 rank-42 children, 672 units.

The bad-residue surcharge is recomputed from the reduced child count. So centre sharing is
worthwhile only jointly with a bit-side mechanism of roughly that size.

**5. Scalar overhead is not the constraint.** Under the selected invoice formulas, each extra
local macro (or child) adds 16 adapters at the compiler constant, 414,949,376 primitives. The
binding finite guard is `local_primitive_bound < 2⁴⁸`, currently 10,038,040,553,630. It leaves
room for at most **654,144 extra macros per call**, before counting the new macros' own
primitives. PR1748's literal two-call reverse phase is 384 macros.

## Reproduce

Standard library and `git` (history for the base commit), from the repository root:

```sh
python3 scripts/research_package.py --package research/centre-sharing-overhead-budget --check-only
python3 -I -B research/centre-sharing-overhead-budget/verify.py
```

Expected output, after about 60 s:

```text
PASS_CENTRE_SHARING_OVERHEAD_BUDGET k2_full_gain_budget_rank8=553 bit_limited_kappa=0.001730427469824 bit_endpoint_for_10pct=0.0018433178 no_new_kappa
```

The run regenerates and compares [RESULT.json](RESULT.json); `--write` rewrites it. Controls:

* the selected complex and bit endpoints are accepted, and their next grid points rejected;
* the selected κ is recomputed;
* the bit surcharge reconstruction matches the ledger;
* the sharpness of every budget is checked;
* the break-even control above.

The script refuses to run under `-O`.

## Scope and limits

This is a favorable planning relaxation. It does not establish:

* that any selected call pair has common post-A sinks, charts or uninterrupted ownership
  (PR1748's first blocker);
* native precision or tape for fused primitives at μ+1;
* hosting or admission;
* that ΔH appears only as paid children of one rank.

Overhead that changes the idle histogram, the coverage identity or the outer recipe is outside
the model. Bit-side numbers are removals from the cited PR589 histogram at fixed `m`, `W` and
surcharge law, not a bit construction.

Inherited all-size/compiler, precision, analytic and H1–H5 obligations are unchanged. This was run
on Windows with CPython 3.14; the registered 3.12 replay was not run locally.

## Open next questions

1. **Can a bit-side mechanism net ≥ 649 paid-mass units?** That is about 20.3 per replica, or
   deficit 10,272 → ≥ 10,921.
   * *Why it matters:* together with any complex saving of ≥ 1.33 units per call (two-call centre
     sharing gives up to 32), it would reach the card's +10% target.
   * *First step:* price the bit-side levers of `bit-revision3-levers-seed03` at the endpoint
     `0.0018433` with this package's sharp-removal method.
   * *Blocked by:* no bit construction with that saving is known, and the bit copy charge and
     full-frame helper floors are scoped obstructions there.

## Credit

* **Sharing constructions:** 1337isnot1337 (PR1708) and ToikY (PR1748). This package prices
  their lever and admits neither.
* **Reused code:** Navinor (exact moment enclosure) and Wronskode (bootstrap and outer formulas),
  both unchanged.
* **Lever framing and coverage identity:** Douglas Colkitt (`complex-local-word-ceiling`) and
  PR1012.
* **Selected construction:** Rohan Arun (#1094), with the credited k8/T16 and supplier lineage.

Prepared for rtyu193-rgb with Claude Code (Anthropic Claude Opus 5.5) in one session, with no
subagents and no independent human review. Apache-2.0.
