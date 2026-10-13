# T16 on the U8 word

The sixteen-replica construction is Hao Yan's (@FanPUYen) [#858](https://github.com/CrocSwap/integer-mult-bounds/pull/858). Its proof (`research/complex-double-replica-owners/PROOF.md`) covers the same steps used here: the replica-local projection, whole-invocation hosting across groups, the actual windows, the direct-sum parent and the prefix/row reserves. This note records only what changes when the supplier is the U8 word instead of #799's X4 word.

## What is inherited unchanged
- **Owner interface.** U8's T8 owner map is #799's (`99d1c4ca…`, the #685/#741 map). U8's PLAN windows equal #799's: same order, same window keys, capacities and times. U8's width inventory is `{4:80, 5:32, 7:54, 8:122, 9:216}`, with the same width at every helper index. #858's eleven moves therefore apply with their source locations and widths checked (`t16/own16.py`). The result is byte-identical to #858's T16 owner file `1c3a8924…`.
- **Idle trade.** Two copies of U8's T8 remainders `{1,3,44}` become `{48:4793, 44:1, 2:1, 1:2}`. The change is `H48 − H44 + H2 − 2·H3` at zero rank mass; `(48,2,0)` strictly majorizes `(44,3,3)`. The local paid profile is U8's, `{1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}` per invocation, doubled to 144 invocations. The full profile is `{1:366914, 2:48673, 3:64224, 4:23328, 5:10368, 8:1152, 44:1, 48:4793}`, with rank mass 1041408 = 73·14336 − 5120.
- **Reserves.** U8's native replay gives B = 72 (both orientations), the same as X4. The prefix is therefore 72 + 37 + 144 + 144 + 4 = 401 < 512, and the invoice recounts the same 401. The physical row coefficient is 2·2642 + 9909 + 252 + 2·512 = 16469 < 20161. The maximum child is 48, and 73² = 5329 > 2·48² = 4608.
- **Code.** #858's exact adapter list, plus the two glue edits named in the README.

## Result
κ = 415489074974971/2.5·10¹⁷ = 0.001661956299899884 (conservative 0.001661956297017522). The complex endpoint is b = 1664722996771957673401/10²⁴ and binds; the PR589 bit endpoint is unchanged. This is +7.6047·10⁻⁹ over U8 at T8 (0.001661948695165034). The gain matches #858's on X4 (+7.6019·10⁻⁹), as expected: the idle trade is the same and only the local profile differs.

## Packing remark (not used by the proof)
On the T16 geometry, every slack unit can be in an empty bin, `{48:4794}`, only if the aggregated relaxation below has a zero-cost solution. The relaxation has, per window class, integer pattern counts restricted to full bins and (cap 48) empty bins, plus any bin with gap ≤ 8 charged by its gap. It also has role counts Z[class,time,width] with Σ_w Z ≤ #bins and exact supply. Its LP bound is 96/37 > 0, so `{48:4794}` is infeasible. The best conceivable improvement over `{44,2,1,1}` is `{44,4}`, about +2.2·10⁻⁹. Exact pattern-flow re-solves that released the four defect classes together with their two bridging classes 100/101 (classes 88, 89, 108, 113, 100, 101; 32k variables, optimal) found no gain. No optimality is claimed.
