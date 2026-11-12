# Bound Type A late-mask permutations at cut 1741

**Outcome** — Scoped exclusion. The complete bound is unchanged.

On the exact #7334 caller, balancing a pair of productive ranks can raise the productive moment without changing paid stock. At cut 1741, 60 of the 630 Type A root transpositions improve this optimistic price, 282 tie, and 288 worsen. The required seam fails phase-evenness at two legal signed sectors for every profitable pair. For simultaneous permutations, the signed constraint gives four invariant classes of sizes 2, 16, 10 and 8. Each class fixes either the early or late body count, so any within-class permutation leaves the productive rank histogram unchanged. The optimistic gain is at most zero for every 0<κ<1, even with a free seam.

For the control pair 0/9, the ranks 137 and 9 would become 73 and 73. The directed relaxed gain is less than 24 raw moment units across 96 Type A ports. The signed seam matrices differ in 100 entries, including entry (0,0) with difference 4. The other 59 profitable pairs each have an exact signed witness in both independent receipts. [Proof](PROOF.md), [verification](VERIFICATION.md)

## Replay

From a clean checkout, use CPython 3.12 with assertions and its standard library.

```sh
python3.12 -I -B research/p104-type-a-late-mask-permutation-bound/replay.py
```

The replay authenticates the bundled inputs by path, derives the seam using independent forward and reverse calculations, compares every pair and both whole-family upper bounds, and rejects a deliberately corrupted caller. No external checkout, network or prior scratch data is needed. Expected final line is `PASS_P104_TYPE_A_LATE_MASK_PERMUTATION_BOUND`.

## Open next questions

- Does a different seam cut preserve the separation of the early and late body variables while producing a different signed prefix comparison? Pin one exact cut, verify the variable partition, then bound the maximum compatible productive price before attempting a build.
- Can a phase-sensitive seam pay its way? Derive the full four-phase action for one profitable pair and charge every additional paid call, ordinary operation, ownership move and restoration. This needs a different premise from the fixed phase-even family tested here.

## Predecessors

- Clear1nsight’s exact #7334 head `aaeec8c0acf01e99a5f331ef363a698d9c084ace` supplies the comparison, κ = 0.00364665195644. [Exact comparison PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
- Rohan Arun’s exact #7113 head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the retained literal Type A/B caller and its physical signed child. The source blobs and SHA256 bindings are recorded in `PROVENANCE.json`. [Signed caller PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- #7362 supplies the exact directed comparator-price receipt from head `5eec7ed633dcf9b9bbc95552aa653da296f863fb`. The rational tariff implementation is retained from `c522451caf287bb3c16eaece72be4c263315dca4`. [Price receipt PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7362), [pricing implementation](https://github.com/CrocSwap/integer-mult-bounds/blob/c522451caf287bb3c16eaece72be4c263315dca4/research/adjacent-owned-add-exchange-bound/pricing.py)

This contribution derives the fixed-cut seam condition and independently checks its full single-transposition family and proves a zero ceiling for all simultaneous phase-even permutations. OpenAI Codex and subagents materially assisted the proof, implementation and independent replay.
