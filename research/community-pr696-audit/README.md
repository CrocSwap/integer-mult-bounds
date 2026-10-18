# Independent recount of PR #696 (complex dyadic lowering)

**Verdict: the primitive claim is confirmed. It gives no κ gain.**

Audited PR: [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)
by Sagar Thakrar (`thakrarsagar`), head
`5a3f983715027c4fd83f50bc9001d4b18463bed1`. Exact base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, which is the base of #696.
Credit for the construction and its original verifier belongs to #696.

## Reproduce

```sh
python3 -B research/community-pr696-audit/recount.py
```

Expected last line:

```text
PASS_PR696_INDEPENDENT_RECOUNT savings=55320,55352,56852,56884 percent=22.10-24.60 kappa_inputs_unchanged=True
```

The script uses Python 3.11+ and the standard library. It runs offline, writes no files and takes about 3 minutes. It does not import any #696 code. It reads only the selected PR626 programs and receipts already on `main`.

## What was checked

1. **Baseline.** The script re-derives the original cleared-work binary Horner word for each scalar macro and counts it, with two real components per macro. Each count equals the emitter's `real_component_primitive_bound` in `LOCAL-CHECKS.json`.
2. **Replacement.** The script re-implements the rule described in #696. For a nonunit coefficient, `copy W←S` replaces `clear W; W+=S`. For a unit coefficient, `T±=S; clear W` replaces the full Horner word. All four counts equal the #696 table exactly. The saving equals `2·(additions + unit additions)` in every program.
3. **Semantics.** The script replays every complete program twice per real component, using random rational inputs and dirty private work. This is separate from the symbolic replay in #696. After every macro the old and new states are equal, and `W = 0` after each addition. Every value that the new word writes to a register also occurs in that register in the old word's trace from the same state. So the inherited prefix envelope is retained.

| Program | Old | New | Saved | % |
| --- | ---: | ---: | ---: | ---: |
| CK forward | 224,938 | 169,618 | 55,320 | 24.59 |
| CK backward | 224,986 | 169,634 | 55,352 | 24.60 |
| JP8 forward | 257,232 | 200,380 | 56,852 | 22.10 |
| JP8 backward | 257,280 | 200,396 | 56,884 | 22.11 |

## Effect on κ

None. `research/complex-k492-owner-repair/code/assemble.py` computes κ from the paid rank profile, `m = 73`, `live`, the deficit and the cited PR543 bit profile. The scalar primitive bill enters only the finite per-vertex invoice (`unhosted_pervertex`, then `conservative_pervertex_used`) and the pass/fail inequalities (`local_primitive_bound < 2^48`, `logical < 2^6050`, …). All of these already pass. Across the 72 selected calls (8 CK, 64 JP8), the lowering saves 4,082,112 of 18,263,888 scalar primitives. That is 8.7·10⁻¹⁰ of the per-vertex allowance `4,711,738,180,507,680`, which is dominated by `adapters × compiler`. The paid profile does not change, so the selected κ `51110230636731/31250000000000000` cannot change.

This lowering could reduce κ only if a future cost model charged scalar primitives in the moment recurrence, or if a construction failed only on one of the finite inequalities by less than about 10⁻⁹ in relative terms. Neither is true of the selected record.

## Scope and limits

This audit checks the finite primitive counts and the exact equivalence of each macro on the four frozen programs. It does not re-run `make verify`, the cold selected replay or Lean. It does not audit the inherited geometric, compiler, hosting, precision and tape contracts. The semantic replay uses random inputs, which complements the exhaustive symbolic column check in #696 rather than replacing it. Open PR #681 also consolidates #696, but #681 was not audited here.

Rohan Guliani (@Rohansguliani), with substantial AI assistance. New files are under the repository's Apache-2.0 license.
