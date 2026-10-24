# Independent check of #4626: helper621 chart change, census delta and arithmetic

This is a scoped check of hexapode's (Pierre-Loic Doulcet's) [#4626](https://github.com/CrocSwap/integer-mult-bounds/pull/4626), head
`e4413c43eeaacdd20be123fdd7d7add53427f028`. #4626 claims conditional κ 0.00302152 → 0.003021569.
It does so by moving helper621's entrance and first scalar contact into the chart A = span{30,429}
on top of the frozen #4610 checkpoint `4b4c75bc`. **No new κ is claimed here.**

## Questions

1. **Ledger.** Is the chart move legal in the native word's own frame bookkeeping? Does it produce exactly the claimed
   paid census, helper census and whole cost change 18(H1 + 2H2 − H3 − H4 − H7 + H9)?
2. **Arithmetic.** Do the raw crossing, κ selection, strictification quotients and finite compiler exponent
   follow from the full paid profile?

## Method

`verify.py` uses only the standard library and runs in about 2 s. It imports nothing from #4626.

**Inputs.**

- **Word.** The checkpoint word is vendored as `PR4610-CHECKPOINT-ACTUAL-WORD.json.gz`. Its git blob is
  `79dad65b`, which is the same blob as #4610's `research/warp-interface-20261022/ACTUAL-WORD.json.gz` at
  `4b4c75bc`, #4626's `predecessor/ACTUAL-WORD.json.gz` and #4614's vendored copy. Its SHA256 is pinned in
  the verifier.
- **Main evaluators.** Two files from main are used: `joint-helper-lattice/CONTROLLER.json`, read as JSON,
  and `clifford_exact.py`, used only to evaluate exact Clifford ranks. Both are pinned in `SOURCES.json`.

**Native side (own frame walker).**

- **Walker test.** Every paid climb is re-derived from the scalar and warp events. On the checkpoint word in
  both orientations, the result reproduces all 3,290 shipped climbs as a multiset, plus the census
  {1:2201, 2:412, 3:506, 4:135, 5:36, 8:8}.
- **Patch.** The patch is then applied (start[621] := A, frame(event 12704) := A) and the word is re-walked.

**Arithmetic.**

- **Precision.** All values are computed in 80-digit Decimal.
- **Root method.** The crossing is found by Newton iteration. #4615 used bisection.
- **Endpoint signs.** The margin sign is checked at both endpoints of #4626's bracket. Each margin exceeds
  1e-60 in absolute value, far above the accumulated rounding error.

## Result: every checked claim reproduces, with two small findings

**Legality.**

- **First contact.** In both orientations nothing touches L621 before event 12704: no scalar, warp, climb,
  adapter or centre event. Helper621 starts at ZERO and ends at FULL9.
- **Partner.** L514's previous contact is at ZERO.
- **Next contacts.** L514's next contact is at frame 797 = span{429,70,30}, and L621's is at frame 4329 =
  span{25,30,96,426}.
- **Nesting.** A is nested in both. In fact **A equals their intersection**, so it is the largest chart that
  both next contacts allow.
- **Scalars.** The scalar opcode and coefficient sequence is unchanged.

**Census delta (both orientations).**

- **Climbs.** Removed: 514: 0→797 (r3) and 621: 0→4329 (r4). Added: 514: 0→A (r2), 514: A→797 (r1) and
  621: A→4329 (r2).
- **Paid change.** This gives ΔP = H1 + 2H2 − H3 − H4.
- **New census.** {1:2202, 2:414, 3:505, 4:134, 5:36, 8:8}. All five changed edges have exact Clifford rank
  equal to their climb rank.

**Helper census.**

- **Two methods.** All 408 relative helper ranks are computed both by the nested-dimension count and by the
  exact Clifford rank of C_final C_start⁻¹, using main's evaluator.
- **Checkpoint.** {4:28, 7:7, 8:47, 9:326}.
- **Patched.** {4:28, 7:8, 8:47, 9:325}. Only helper621 changes, from 9 to 7.

**Whole profile.**

- **Histograms.** The whole paid and target histograms equal #4626's `ARITHMETIC.json`: 64,422 paid calls,
  10,928 fields and rank-mass surplus 752.
- **Cost change.** The difference of the whole moment margins equals 18(H1 + 2H2 − H3 − H4 − H7 + H9) to 1e-60.
- **PROOF.md value.** At a = .00302156 the change is −0.004016704251714083738. This lies inside PROOF.md's
  interval.

**Finding 1 (cosmetic).** The PR body says the change is "≈ −0.00401665923 at the tested exponent". That
value is attained at a = 0.00302152, the predecessor κ. At the tested exponent .00302157 the value is
−0.0040167155066. PROOF.md's number is correct, and sign and magnitude are unaffected.

**Raw crossing.**

- **New root.** 0.00302157135763930442, inside (0.0030215713, 0.0030215714).
- **Control.** The checkpoint root 0.00302155511144603 reproduces #4610 and #4615.

**κ and compiler.**

- **Tested saving.** It is .00302157, the root floored to 1e-8, and lies only **1.36e-9** below the root.
- **κ.** κ = tested − 1e-9 = 0.003021569.
- **Strictification.** α, γ and δ reproduce all 30 digits #4626 displays. α clears its 1 − 1e-9 threshold
  by only 4.15e-10.
- **Compiler exponent.** With step 7·10⁹, j = 48,264 is the least j with (step·j + 1)^1000 < 2^j, checked
  in exact integers. Hence H = 337,848,000,000,000.

**Finding 2 (attribution of the gain).** #4626 changes two things: the native profile and the κ-selection
rule.

| Rule | Checkpoint (#4610 `4b4c75bc`) | With helper621 (#4626) |
|---|---|---|
| #4610's rule: ⌊root·10⁸⌋ − 3, gap 1e-8 | 0.00302152 | 0.00302154 |
| #4626's rule: ⌊root·10⁸⌋ − 1e-9, gap 1e-9 | 0.003021549 | 0.003021569 |

Of the +4.9e-8, about +2e-8 comes from helper621. The other +2.9e-8 comes from the compiler-gap retune, which
would apply equally to the checkpoint. The retune spends compiler headroom: tested sits 1.36e-9 below the
root, where #4610 left ≥ 2e-8. That trade is legitimate only if the outer ledger accepts it. Its 54 + 4
outer checks are **not** re-verified here.

**Context.** #4610's own later head claims 0.00302176 from a different joint change on the same checkpoint.
Whether #4626's helper621 move composes with it is not checked here.

## Controls (each must fail)

- **Non-nested chart.** span{30,1} is not nested in the next-contact frames.
- **Entrance only.** Moving the entrance without its contact leaves an A → ZERO edge.
- **Smaller chart.** The 1-dimensional chart span{30} gives a different census.
- **Old helper credit.** The census {…, 7:7, 9:326} is rejected.
- **Wrong κ selection.** #4610's κ rule does not give #4626's κ selection.
- **No idle charges.** Dropping the idle charges moves the root far above the bracket.
- **Wrong exponent.** j = 48,263 does not win.

Local mutation tests of the claims also fail as expected: a wrong chart, the old helper credit, a shifted
bracket, exponent 48,265, and the tested-exponent ΔC value in place of the body's.

## Not covered

- native literal replay of the 632 arbitrary input columns;
- absolute phases and the monomial normalizers of the rank-7 helper target. This check covers the rank only;
  the phases are #4626's `verify_native.py` claims;
- the backward-orientation semantics beyond the frame census;
- the 54 strict and 4 functional outer checks, η, and the BIT supplier;
- Lean;
- whether a relative rank-7 helper target with an arbitrary input in chart A is admissible under the supplier
  contract. That is the maintainers' call, as for #4610's generator substitution.

## Reproduction

```sh
python3.12 -B research/pr4626-helper621-check/verify.py
python3.12 scripts/research_package.py --package research/pr4626-helper621-check
```

## Open next questions

1. **Supplier contract.** Is the κ-selection retune (gap 1e-8 → 1e-9, tested 1.36e-9 below the raw root)
   accepted by the 54 + 4 outer ledger independently of #4626's vendored engine? First step: rerun
   `pr4359-p7-padding/.../endpoint.py`'s ledger with an independent parameter derivation. If it is accepted,
   the same retune applied to #4610's checkpoint gives 0.003021549 with no native change.
2. **Composition with #4610's later head.** Does helper621's chart move compose with #4610's later joint change
   (κ 0.00302176)? First step: check whether that head changes helper621's start, event 12704 or frames
   797 and 4329.
3. **Other helpers.** Are there other ZERO-start helpers whose first contact partners' next-contact frames
   intersect non-trivially? This chart move would apply to them in the same way. First step: scan all 408
   helpers with the frame walker in this package.

## Credit

hexapode / Pierre-Loic Doulcet ([#4626](https://github.com/CrocSwap/integer-mult-bounds/pull/4626)), intqwq /
Cao Yifan ([#4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610)), Cinna Davis
([#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)) and the credited predecessor chain.
pinterbanget's [#4614](https://github.com/CrocSwap/integer-mult-bounds/pull/4614),
[#4615](https://github.com/CrocSwap/integer-mult-bounds/pull/4615) and
[#4616](https://github.com/CrocSwap/integer-mult-bounds/pull/4616) checked #4610's checkpoint. This package
reuses #4615's controller-histogram recipe, reimplemented here.

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
