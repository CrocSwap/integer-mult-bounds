# Fixed-paid rank-five prefix bounds on chart 3→238

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to independently
reproduced conditional κ = `0.00364665195644` on
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

A fixed-paid 2+3 or 3+2 split would replace one rank-five
productive target of the chart 3→238 cohort, roles 325 and 1087.
This exhausts the 18 frozen public banks on intermediate charts
370 and 375 that [#7370](https://github.com/CrocSwap/integer-mult-bounds/pull/7370)
left outside its support scope. Both exact prime-field engines
exclude all 18 by full exterior prefix rank. Every primary
minor's coordinate set also gives a nonzero determinant at the
independent prime. No selected bank remains unresolved.
The other 31 representatives from #7370's outside-support list
are still outside this test.
[Exact per-key agreement](receipts/AGREEMENT.json).

The directed one-edit upper is about 0.207666506667591 raw.
The optimistic two-role upper is about 0.415333013335181.
All 110,519 paid positions stay fixed. [Proof and complete price](PROOF.md).

## Replay

From a clean checkout, use CPython 3.12 with assertions:

```sh
python3.12 -I -B research/p104-rank-five-chart238-prefix-bound/replay.py
```

The standard-library replay authenticates the exact #7370
manifest, price, geometry, and #7334 word. It recomputes the
directed price with the exact tariff, freezes all 18 keys,
replays both primes and checks the primary minor coordinates
at the independent prime. Altered selection and geometry
inputs reject. Use `--out fresh-directory` to retain all four
receipts. No Git metadata, network, external root or prior
temporary state is needed.
[Provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json).

## Open next questions

Can a different fixed-paid rank-five cohort supply two-sided
support? The #7370 geometry lists 17 representatives for
chart 3→233, roles 289 and 1052. Freeze that one group and price
its complete invoice before a bounded prefix/suffix replay.
This contribution tests only chart 3→238.

## Credit

[#7370](https://github.com/CrocSwap/integer-mult-bounds/pull/7370)
at `a41edc3ae92332a7a1f1ba90e9ea4901d0530185` supplies the exact
geometry and directed productive split stock.
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact native word and signed caller.
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
supplies the admitted full invoice, and
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
the rational directed tariff.
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supplies the inherited exact helper census.
[#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
supplies the common-frame split method,
[#7367](https://github.com/CrocSwap/integer-mult-bounds/pull/7367)
the same-word exterior proof method on another cohort, and
[#5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994)
the earlier broad census on a different word. OpenAI Codex and
subagents materially assisted proof, implementation, independent
verification and packaging.
