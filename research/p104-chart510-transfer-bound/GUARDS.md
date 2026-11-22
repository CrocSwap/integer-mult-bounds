# Joint Boolean-guard transport for the paired BIT word

This is a conditional **raw-price obstruction** for a particular support-based billing model. It does not install a modified powered selector or prove an upper bound on model-wide κ.

## Checked local alternatives

The graph and caller are the pinned #8027 paired word as carried by the #8030 standalone source. They have 36 local calls. In each call, clock 10036 is the rank-one MOVE of the 2337 readout and clock 10039 the rank-one MOVE of the 2335 readout. Each of the two moves can individually be replaced by the corresponding chart-1 `INIT` and cocharted `ADD` readout. The four exact lists are `READOUTS` in `joint_verify.py`. The verifier symbolically replays every original input as an independent field, validates every chart and private owner lifetime, and checks that each individual change preserves all outputs whenever its corresponding residual helper fields are zero. Other public inputs remain arbitrary. Each replacement removes exactly one rank-one MOVE; all 3,433 original private clear sites and their charts remain. The retained clock 11015–11017 path is unchanged. This is a local source check; arbitrary private clear payloads still require the ordinary erasure service.

For each local call let `D` be the conservative old paid support and let `R46` and `R90` be the independent helper-coordinate sets in the two alternative readout residuals. Their sizes are listed below. Every listed helper is a productive occurrence of rank 8. Intersections below also apply to all 36 calls, with the proper call index on each helper.

| Original clock | `R46` size | `R90` size | `D ∩ R46` | `D ∩ R90` | `D ∩ R46 ∩ R90` |
| --- | ---: | ---: | --- | --- | --- |
| 10036 | 18 | 56 | 365, 367, 459 | 251, 334, 365, 367, 386 | **365, 367** |
| 10039 | 29 | 34 | 428, 437, 445, 452 | 428, 437, 445, 452 | **428, 437, 445, 452** |

The coordinate numbers identify helper inputs of the pinned local graph, not whole-run indices. The verifier reconstructs all support sets and asserts the last column, independently for all 72 changed labels. `R46` and `R90` are sufficient individual zero premises for the displayed readouts. More general linear residual cancellation can exist and is not ruled out.

## Ordered transport and its scope

For each original paid label `j`, define `S_j = D_j` except at the 72 positions in the table, where `S_j = D_j ∩ R46_j ∩ R90_j`. Let `k_i` and `r_j` be the full original productive and paid ranks. Set `c0 = 0.003890115286594461129996943` and `t0 = 1 − c0`.

The checked nonnegative transport is from all 18,906 productive occurrences to all 104,904 original paid occurrences, aggregated only when rank and `S_j` agree. Each target has outgoing mass at least `k_i^t0`, each paid occurrence receives at most `r_j^t0`, and every used arc satisfies `i ∈ S_j` and `k_i ≥ r_j`. Outward rational rounding is applied per paid occurrence before identical groups are added. There are 86,802 groups, 6,729,066 allowed ordered dependencies, and 114,405 nonzero certified edges. At scale 10^30 the rounded capacity exceeds rounded demand by 103,186,566 ticks. The witness digest is `1286d70972e70431abfc4433858429a58c6602ff834bf8cad64e3c94ef1476c2`. Replay checks every amount and dependency and rejects a one-tick corruption.

For `c0 ≤ c ≤ 1`, scaling each target row by `k_i^{-(c-c0)}` preserves target coverage and paid capacities because every used edge has `k_i ≥ r_j`. Tensor products preserve these inequalities. Thus, for any finite power and retained set `A` of productive tuples, a hypothetical billing rule that charges the **full product rank** of every paid tuple whose Cartesian set `∏ S_j` meets `A` cannot achieve a strict positive raw rank-moment surplus at `c ≥ c0`.

If a chosen Boolean selector is known to bill whenever a retained tuple witnesses all its old-support and chosen residual-support conditions simultaneously, then a witness in `∏ S_j` also witnesses those conditions for either alternative, including coordinate-wise choices between the 46 and 90 readouts. The transport is therefore an obstruction for that explicitly stated full-rank Boolean model. A path that uses the original operator is also covered when its billed support contains `D_j`. Split full ranks cannot lower the `t`-power bill for `0 ≤ t ≤ 1`.

The intersection is used only as a **sufficient witness of simultaneous support membership**. Its emptiness does not imply that the literal paid field or the residual field is zero: different retained tuples can independently meet `D_j` and a residual set. Conversely, a conservative support hit does not establish a physically nonzero field when algebraic cancellation is permitted. The theorem neither installs nor validates the chronological powered implementation, a tensor-aware selector, partial-rank billing, cancellations, changed helper coordinates, or the complete signed application. Those require separate transfer and economics proofs. In particular, the fixed rank-8 helper cutoff can justify fresh-zero components at a root suffix, but the original powered interpreter synchronizes full paid requests and deeper requests can acquire nonzero fields.

## Replay

```sh
python3 -IB joint_verify.py
```

The default input graph, caller and compressed witness are adjacent; `--graph`, `--caller` and `--certificate` override paths while retaining the same hash requirements. The program uses only the Python standard library. The log/exp interval arithmetic is copied from #8030's `independent_binary_price.py`. The conservative support regeneration is from #8034's `zero_support.py`.
