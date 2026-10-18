# Independent re-solve of PR #2979's fixed-capacity stage caps

**Partial positive audit. No new κ, no supplier admission.** The selected
result stays κ = 0.001672660197076918.

[PR #2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)
(head `be191346`) certifies its fixed-capacity packing caps from stored optimal
bases. This package re-solves the same relaxation **without any stored basis**:
its own pattern enumeration, its own two-phase simplex (numpy floats, Bland's
rule) to locate a basis, then an exact Fractions inverse and `mpmath.iv`
interval enclosures for the root and every reduced cost. No code from the
audited package is imported or run. The relaxation model is re-implemented from
its docstring (`tools/relax.py`), so this check shares the model, not the code.

## Result

All four shipped brackets are reproduced exactly on the 10⁻²⁵ grid, with the same
idle histograms:

| words | cap (lower, 10⁻²⁵ grid) | patterns | basis identical to shipped |
|---|---|---:|---|
| parent (PR #2942) | 0.0017228172707428495209099 | 1,163 | no (alternative optimum) |
| stage 1 | 0.0017262265796413098725813 | 2,551 | yes |
| stage 2 | 0.0017278107473204236839366 | 2,551 | no (alternative optimum) |
| final | 0.001729035764875516181444 | 2,551 | no (alternative optimum) |

Three optimal bases differ from the shipped ones but give the same idle profile
and root, so the LP is degenerate there. The cap does not depend on the choice.

**New coverage: each stage-one group is priced alone with a certified cap.**
The source's single-versus-joint argument uses an approximate width guide of
2,091,300 units per freed width unit, which [the frame audit](../rank7-joint-frame-audit/README.md)
notes is not a certified tariff. Here each group's change is applied alone to
the parent words and the cap is re-solved. Local deltas come from the frame audit's
`RESULT.json`; width changes come from #2979's README.

| change on the parent | certified cap | vs parent cap |
|---|---|---:|
| V45 (4 helpers 8→7) | 0.001723368262870964843035 | +5.510e-7 |
| A (331 8→7; 450, 451, 508, 509 7→6) | 0.001723827833046096748741 | +1.0106e-6 |
| B (299 8→7; 448, 449, 484, 485 7→6) | same as A | +1.0106e-6 |
| C (452, 453, 532, 533 7→6) | 0.001723233298297402658193 | +4.160e-7 |
| D (454, 455, 556, 557 7→6) | same as C | +4.160e-7 |
| V45 edits, k = 0 lowered | 0.001720993847503899547275 | −1.8234e-6 |
| V45, k = 1 | 0.001721586837582425406796 | −1.2304e-6 |
| V45, k = 2 | 0.001722180236554225593479 | −6.370e-7 |
| V45, k = 3 | 0.001722774044842483001525 | −4.32e-8 |
| V45, k = 4 | equals the V45 row | +5.510e-7 |

So each group raises the fixed-capacity cap by itself. For V45 only the full joint
lowering does so, and each of 1, 2 or 3 lowered endpoints lowers the cap. The
signs agree with the source's guide margins (−53,141, −27,770, −2,399, +22,972).
The five group gains sum to 3.4042e-6 against a joint stage-one rise of
3.4093e-6, so the groups are nearly additive under the cap as well. This answers
the open question in [rank7-v45-shipped-invoice](../rank7-v45-shipped-invoice/README.md):
the cap rise is attributable to each group, V45 included, within this relaxation.

Nearest parallel work: [PR #3237](https://github.com/CrocSwap/integer-mult-bounds/pull/3237)
(commdata2338, head `9881b9d5`, open) certifies that widening V45 endpoints on
the **final** words fails the complete budget. This package instead prices the
original **stage-one** groups and subsets on the parent words and re-solves all
four shipped caps; the two are complementary and neither imports the other.

## Controls

`RESULT.json` records five checks:

- one basis column replaced (singular);
- the stage-2 basis applied to stage-1 inputs (infeasible);
- a feasible basis that is optimal at b = 1/2 (rejected by the reduced-cost sign);
- one extra rank-1 child (rejected by the rank-mass identity, 65,088 per replica);
- the stage-2 local profile with the final inventory, which gives a strictly lower cap.

The inputs are authenticated by SHA256 before use.

## Scope and limits

This is the **fixed-inventory fractional relaxation** only. It ignores source
windows, per-call family exclusion and integrality, so a cap rise is an upper
bound on what a chronological fill can reach, not a realized saving. The group
controls fix the parent's other words and the source-declared width changes.
They use the frame audit's checked local deltas and do not re-derive frames.
The model's bin shape (`{8:672, 16:448, 32:448, 48:448}` per replica, one idle
child per bin) is the source's and is not re-justified here. Native/phase,
physical storage, precision, the literal T74 allocation and the outer release
remain unverified by this package.

## Reproduce

From the repository root, with numpy and mpmath (via sympy):

```sh
python3.12 -B research/rank7-stage-cap-resolve/verify.py
python3 scripts/research_package.py --package research/rank7-stage-cap-resolve --check-only
```

`verify.py` recomputes everything (about 20 s) and requires byte-equal agreement
with `RESULT.json`. `python -B research/rank7-stage-cap-resolve/run.py` prints it.

## Open next questions

Does PR #2987's chronological owner and packing evidence attain these caps for the
stage-one words, or is part of each group's rise unreachable once windows and
family exclusions apply? This decides whether the certified cap rise becomes a
supplier saving. A first step is to price a chronological fill of the stage-one
inventory against the stage-one cap. Native/phase, storage and precision bindings
still block admission. Another lowering census is not justified by this result.

## Credit

Marius-Paul Dumitrean (#2979, #2942) supplied the construction, words and
relaxation model. Jeremy Kothe (#2957 rewrites and frame/cleanup lineage), Mason
Hale (#2917) and Jeremy Diviney (#2908) supplied the extraction chain. Nick
Petalas's independent frame audit supplied the checked group deltas used here.
Ross Richardson's #2960/#2974/#2987 audits and the retained relaxation lineage
(PR2857/PR2930) keep their credit. New check written by Claude (Anthropic) via
Claude Code, in a session donated by Mark. Apache-2.0. No human or formal review
is claimed.
