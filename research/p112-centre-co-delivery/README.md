# P112 tetrad centre co-delivery

**Exact coefficient and native-label result; no selected-κ improvement is claimed.** The input-side correction from the P112 consumer audit can be emitted by the same tetrad terms as the fused port update. The selected native centre frames supply a source-bound assignment for the eight omitted P112 labels, and under that assignment all 56 augmented terms have support-pair rank one.

## Scope and evidence

For one selected P112 tetrad, let `E` be its eight-by-four signed coordinate matrix, `K = E E^T`, `U` the pinned unimodular four-kernel-row change, `S` the selected gauge44 centre reader, `H` the hybrid reader, and `C = S - H`. Put `M = U E`. The existing exact identities give

```text
M E^T = U K
H^T U K = S^T K
J = C^T U K
```

Factor the correction through the same four product values:

```text
J = (C^T M) E^T.
```

Thus each term `E[:,k]^T x` can emit both `M[:,k] E[:,k]^T x` to the eight port roles and `-(C^T M)[:,k] E[:,k]^T x` to the eight centre roles. Their sum over four terms is `(U K x, -J x)`. With an arbitrary dirty port baseline `d`,

```text
S^T(d + U K x) - J x = S^T(d + K x).
```

This removes the need for a separate source of `Jx` at the coefficient-identity level. It does not claim that the resulting child terms have a physical COPY schedule or that their scalar outputs are free.

The selected port map identifies the 112 live-root labels. Pairing each omitted P112 frame root with those ports determines its unique nine-bit label, in frame order:

```text
97, 127, 76, 82, 25, 7, 52, 42
```

Each selected native centre slot is bound to `word["center_frames"][slot]`. Those eight native frames have rank eight in the nine-bit label space, so each has a unique nonzero orthogonal label. This derives the centre-slot-to-omitted-root permutation `[7, 5, 4, 6, 3, 1, 0, 2]`; it is not inferred from register IDs. Exhausting all `8!` assignments finds this as the unique minimum-rank assignment.

| Decoder / assignment | Rank profile | Rank mass |
|---|---:|---:|
| Existing local P112 masked decoder | `{2: 56}` | 112 |
| Co-delivery with frame-order labels (control) | `{1: 24, 2: 32}` | 88 |
| Co-delivery with selected native centre binding | `{1: 56}` | 56 |

The co-delivery matrix `C^T M` has 92 nonzero centre coefficients across all fourteen tetrads, including 19 on the first three. The corresponding `J` matrices have support 288 overall and 64 on those first three. These are exact coefficient-support counts, not a scalar-add invoice. The augmented support-rank certificate prices each whole term by the binary rank of its selected input/output label-pairing matrix; it does not construct the matching native program.

This does not contradict the retained COPY112 floor for a complete masked decoder on P112. The port-only output `U K` has four zero rows per block and is not that decoder's required diagonal/orthogonal-pair matrix. The missing effect is carried in eight output channels outside the 112 live-root set. Co-delivery changes the consumer endpoint and pays for those augmented supports; it is not a cheaper decoder for the original P112 target.

Without a separate charge for the output correction, the hypothetical rank-32/two-unpaid complex profile changes from `{1:192, 2:56, 32:166}` (local mass 5,616; ideal κ cap 0.0137876681081) to `{1:248, 32:166}` (mass 5,560; ideal cap 0.0141093063394). This is the coefficient-only ceiling. The `a=1/99` target passes with two unpaid coordinates, but the one-unpaid control fails.

A bounded exact screen then tested all 70 standard-coordinate complements on each tetrad (56 are unimodular), followed by all 24 elementary input shears `I ± E_ij` for each valid complement: 784 completions and 18,816 shears. Every shear preserves the exact product factorization and all four rank-one augmented terms. The minimum centre-support vector is `[2, 7, 7, 2, 7, 6, 6, 7, 7, 7, 2, 7, 7, 2]`, totaling 76 coefficients, down from 88 for complements alone and 92 for the original completion. Under a sensitivity charge of one rank-one unit per nonzero centre coefficient, the local cost is 132 versus the 112-copy control. The resulting profile `{1:324, 32:166}` has mass 5,636 and ideal complex κ cap 0.0134440084459, below the baseline cap 0.0137876681081. This remains a conditional sensitivity, not a physical scalar tariff, admitted supplier, joint invoice or achieved κ. The selected κ remains **0.001672660197076918**.

## Limits and next work

The exact result answers the local label-binding question and shares the source correction across the same 56 product terms. It leaves the central research obligations open:

- No term-level native COPY constructor has been bound to the augmented supports. Build one tetrad at the selected pre-B frame-zero window, including input forms, port and centre outputs, adapters, arbitrary dirty inputs, scratch lifetimes and restoration; price every scalar operation.
- The complex ceiling assumes two unpaid coordinates. The corresponding bit-side endpoint contract and the complete joint invoice are not proved. A full endpoint replay must retain the `a=1/99` target after all source, centre and restoration costs.
- No selected record, frontier value or multiplication theorem changes here. Stop further construction expansion if the one-block invoice or either side's two-unpaid contract fails.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/p112-centre-co-delivery --check-only
python3.12 scripts/research_package.py --package research/p112-centre-co-delivery
```

The replay first runs the selected centre native-lift and P112 consumer verifiers, then checks all fourteen co-delivery identities, native label complements, the complete eight-slot permutation census, exact support-rank profiles, and the conditional complex ceiling. Source commits, blob IDs and SHA256 pins are listed in [SOURCES.json](SOURCES.json); the replay contract is [VERIFY.json](VERIFY.json).

## Open next questions

1. **Can one augmented tetrad term family be implemented as a chronological native COPY program on arbitrary dirty ports and centre channels?** This decides whether rank-one co-delivery is attainable. First step: realize the first tetrad in the existing frame-zero window and replay every source and destination role. The blocker is the missing term-level COPY constructor and complete scalar/endpoint invoice.
2. **Can both selected suppliers justify two unpaid coordinates under the resulting complete endpoint contract?** This decides whether the conditional complex profile can support κ above 0.003. First step: replay the exact full-call coverage identity on both sides with restoration. The blocker is the unadmitted bit-side contract and joint endpoint.

## Credit

The P112 root geometry and local decoder retain the attribution in [p112-tetrad-local-decoder](../p112-tetrad-local-decoder/README.md). The selected port bijection comes from [PR #3566](https://github.com/CrocSwap/integer-mult-bounds/pull/3566); the dirty-state consumer and input-side correction continue [PR #3604](https://github.com/CrocSwap/integer-mult-bounds/pull/3604). The native centre-role/frame binding retains [selected-centre-native-lift](../selected-centre-native-lift/README.md) and its predecessors. Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. Apache-2.0.
