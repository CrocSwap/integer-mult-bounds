# Fixed-paid P104 chart-1089 split bound

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On independently reproduced [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, test whether one rank-nine helper can split into ranks three and six using the same paid MOVE schedule. The only affected eligible pivot at chart 1089 is role 1081, with endpoints chart 3→127. The twelve tested cuts are immediately before events 44588 through 44599 in the emitted helper-319 block.

Two independent walks agree that every cut has public bank `[85,319,1081]` and an empty owned bank. The support gate grants the full 615-role endpoint cohort and all three public chart rows, including protected role 319 as a local relaxation. Exact rational elimination gives exterior prefix rank three. The independent replay reconstructs a nonzero 3×3 minor for every key, with all used denominators invertible modulo 1,000,003. Thus no pure prefix exists. All twelve keys are resolved and no suffix or construction is needed. [Proof](PROOF.md).

The complete signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) price for a hypothetical 3+6 split is `T3+17,T6+17,T9−17`, with all paid stock fixed. The complete comparator remains κ `0.00364665195644`, and the optimistic one-edit credit is about 0.3528183420760684 raw. A single added paid rank-one position eliminates the price through the retained BIT cap. The exact prefix obstruction reduces compatible savings to zero in this scope.

## Replay

Use CPython 3.12 with assertions and the standard library. From a clean checkout:

```sh
python3.12 -I -B research/p104-chart1089-split-bound/replay.py
python3.12 -B scripts/research_package.py --package research/p104-chart1089-split-bound
```

Use `--out` with a fresh output path to retain all three receipts. The command authenticates the exact #7334 compressed word and its Git blob, rebuilds the signed directed price, compares exact rational and modular prefix certificates, and rejects changed compressed input. [Source and replay details](VERIFICATION.md).

## Open next questions

Can a different cut bank support a fixed-paid split of this exact endpoint cohort? Pin the next chart and scope, reprice the full signed invoice, and test its exterior prefix before exact pairing. This result covers only the affected 1081 pivot in the literal chart-1089 interval. Other pivots, changed paid paths, changed owner contracts and newly installed physical interfaces are open.

Credit #7339 for the exact cohort, earlier occupancy receipts and pairing code; #7334 for the emitted word; #7113 for the signed caller; #7298 for the directed tariff; and #5599, #7121, #7130 and #7332 for earlier split, basis and cohort methods. OpenAI Codex and subagents materially assisted.
