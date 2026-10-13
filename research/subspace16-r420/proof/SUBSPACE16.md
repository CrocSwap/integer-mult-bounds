# A strict paid-cost improvement from new intermediate subspaces

The baseline is the complex component of PR548 at `66dbc2bffc1bfa8d50b3f9a2ac7ccba8fd9f6f36`. Its construction, frame-lift provenance, cold-dirt correction and complete owners are retained explicitly. The R420 bit supplier is PR543 at `2065fe4f72a914d907f1046603f5a36f17018535`.

## Observable pruning

For a linear operation `x_d += a x_s`, its contribution to final target coordinates is `a R_d x_s`, where `R_d` is the exact suffix response of destination d. If `R_d=0`, deleting this operation leaves every observed target coordinate unchanged for every initial register value. Backward propagation updates `R_s += a R_d`. Identity scales may also be removed. Applying this exact rule deletes 238 preparation operations and no delivery operations from the baseline. Fixed prefix operations and advertised center-frame boundaries are preserved.

Cleanup is regenerated as the literal reverse inverse of every remaining background operation. Background registers therefore return to their arbitrary initial values. The independent auditor recomputes the entire target preconditioner and cold-dirt compensation, then checks all 728 formal columns in both orientations. The pruning alone leaves the paid histogram unchanged. We make no numerical gain claim for these deletions.

## Frozen frame assignment

The 63 replacements in `data/RECIPE.json` change only frame labels of the sliced scalar word. Each gate still has a common frame on its operands; each physical register follows a nested chain from its prescribed start through its central boundary to its prescribed endpoint. The inherited coalescing compiler applies to these checked chains. We do not require a replacement frame to contain its predecessor assignment: legality is checked against the actual neighboring events of the resulting program.

The recipe was found by a bounded search using random one-dimensional extensions and hyperplanes, closure propagation, neutral moves and outward rational moment comparisons. Search is not part of replay and no optimality is claimed. Replay reconstructs the word from primitive inputs, checks each old frame, applies the frozen recipe, and independently establishes legality and the actual paid profile.

The profile difference is exactly

    ΔH = 16(e1 - e2 - e3 + e4).

Child count and rank mass are unchanged. For every 0 < b < 1, the function f(x)=x^(1-b) is strictly concave. Its derivative is strictly decreasing, so f(2)-f(1) > f(4)-f(3), and hence f(1)+f(4)-f(2)-f(3) < 0. The new profile therefore strictly improves the local moment throughout this interval. The fallback charge is unchanged because it depends on child count.

## Literal global accounting

Helper entrance frames and ordered widths are identical to PR548, so its complete owner placement remains applicable. The actual controller is nevertheless re-emitted and independently audited; applicability is not inferred from a histogram alone. There are 72 local invocations, so the complete global profile changes by 1,152(e1-e2-e3+e4). Stock remainders, physical owner identities, call windows, and banks are unchanged.

The complete global histogram is `{1:165600, 2:32128, 3:35907, 4:13248, 5:4032, 6:4032, 7:208, 8:576, 39:1, 48:1660}`. It has live stock 7,168, 7,682 physical registers, 36,288 helper roles, and rank deficit 2,560. The finite scalar invoice is regenerated from the changed program.

Both independent rational moment engines accept b = 0.001594507308884431019637 and reject the next 10^-24 grid point. They also reprice the freshly replayed R420 bit supplier. Six exact bootstrap steps and all 47 inherited strict outer inequalities admit κ = 0.001591968902833346. Four outer rejection controls remain enabled.

## Verification boundary

All 2,929 local Clifford phase edges and 224 endpoint adapters are recomputed cold. The static44 construction's 44 omission controls, independent scalar/local/wrapper checks, seven physical-owner corruptions, R420 native/interface and global mutation controls are retained. These finite checks do not discharge all-size realization, fixed-tape implementation or analytic transfer. In particular, the existing outer architecture still cannot reach κ = 1 merely by tuning these suppliers.
