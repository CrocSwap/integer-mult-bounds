# Phase-sensitive Type A late-mask reassignment at J9

**NO VERIFIED GAIN.** The comparator is exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with the signed caller [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Its independently reproduced κ is 0.00364665195644.

Can an arbitrary late-mask permutation at Type A cut 1741 be absorbed into the existing paid J9 at clock 3058? Allow phase-sensitive action inside the four original J9 roles (9,0,18,27) and keep the remaining caller word and paid positions fixed.

The optimistic roots 0/9 swap would change ranks 137 and 9 to 73 and 73 across 96 ports. At q=+1, the forced replacement has 16 coefficients outside the four-role block, including (10,0)=4. At q=−1, it has eight, including (0,10)=−2. Either legal unit-body specialization excludes the swap.

For the whole fixed-host family, the two signed prefix comparisons force 35 exact role classes. All are singletons except {9,27}. Those two roles have identical full diagonal words, with q⁻¹ and only body 9. Every permutation that can pass the unit-body host support gate preserves the exact productive histogram. The whole-family optimistic gross is [0,0]. No permutation search was required and no key remains unresolved in scope.

From a clean checkout use POSIX CPython 3.12 with assertions.

```sh
python3.12 -I -B research/p104-type-a-j9-late-mask-bound/replay.py
```

The Git-free command authenticates the pinned caller and exact predecessors, verifies the signed physical specializations, regenerates six deterministic receipts, and rejects a changed source receipt. Use `--out fresh-directory` to keep the regenerated outputs. See [proof and price](PROOF.md) and [verification](VERIFICATION.md).

[#7410](https://github.com/CrocSwap/integer-mult-bounds/pull/7410) at `ae41a5abb02fd18d3e270ee2ab4822b651902d0d` supplies the original late-mask setup, price, and signed prefix evidence. Its separate gate concerns a fixed phase-even seam at cut 1741. [#7412](https://github.com/CrocSwap/integer-mult-bounds/pull/7412) at `4dfa0a393fd12101af5ffed161ed1bc5aa045f11` supplies related fixed-host support methods for QUERY demotion. #7334 and #7113 supply the exact native word and caller, #7362 the signed rank stock, and #7298 the directed tariff. OpenAI Codex and subagents materially assisted. Apache-2.0.

## Open next questions

A different host clock, more exposed host roles or another paid schedule remains open. Start by pinning and pricing one exact alternative. Recompute its exterior fingerprints before trying all-body identities or a native implementation.
