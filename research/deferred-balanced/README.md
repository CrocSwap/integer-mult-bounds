# Balanced transfer of the deferred signed networks

Conditional **κ = 63978919675787/10¹⁸ = 6.3978919675787×10⁻⁵**, **0.0204901262% above PR97's stated bound**. This composes Zhihao Chen's PR97 integration of Swapnil Jain's physical networks with the balanced positional layout already retained in this repository, and sharper exact moment enclosures.

Two results are certified separately:

| Transfer | κ |
|---|---:|
| PR97 as published | 6.3965813×10⁻⁵ |
| Same original-prefix transfer, refined moments/backoff | 6.3974826635492×10⁻⁵ |
| Inherited balanced positional transfer | **6.3978919675787×10⁻⁵** |

The bit saving becomes **15995753310011/250000000000000000**. The complex saving used by the assembly remains PR97's **36926111/500000000000**. No gate, frame, endpoint, phase correction or child multiplicity changes. Both tensor connectors, copied centers, gauged exits and the inverse rank-one phase correction remain fully charged.

The balanced result uses an additional inherited layout argument: group common low-coordinate FFT axes after handling their extra top bits, using the paid coordinate router and retaining complete spectator/control/row fields. Its prefix-work margin is 1−ε. The original 1−ε(1+c) remains a positive geometric requirement. A negative control rejects imposing the original prefix cost at the stronger balanced parameters. This is a physical transfer hypothesis, not a deletion of an accounting term; see [PROOF.md](PROOF.md).

The imported PR97 checkout omitted four logs that its manifest required. Fresh frame, lifted, staircase and negative-control replays recover those artifacts. The original manifest and expected hashes are preserved here; only the corresponding log hashes are refreshed. Original physical and analytic source bytes are unchanged. The original failed invocation and fresh replay receipts are retained, without representing it as a passing run.

Verification complete: the full `make verify` passed on research commit `3dbe4e1` (78 isolated test modules and 20 historical patch checks). The following package replay then failed only on its accidentally pinned, ignored Python bytecode cache. After the existing cache-only fix at `ae56b9f`, the complete package/native geometry replay and all six controls passed in 809.215 seconds. Both invocations and their exact hashes are recorded in [validation.json](validation.json); the original monolithic invocation is correctly recorded as failed. All 42 GitHub checks passed on the corrected research head. Neither run changed source files. The earlier missing-SymPy setup failure is retained; the validated environment used SymPy 1.14.0.

```sh
python3 -m pip install sympy==1.14.0
python3 research/deferred-balanced/verify.py --replay-own
python3 research/deferred-balanced/test_controls.py
python3 research/deferred-balanced/verify.py --replay
make verify
```

**Credit:** Zhihao Chen (jacklightChen) supplies the explicit reflected schedules, commuting fan-order clarification, nonzero entrance/exit gauge proof, signed complex phase controls and correction, and integration with retained semantic interfaces, with Codex assistance. Swapnil Jain supplies the deferred readouts, V leaves, lifted frames, paired complex producer, flag/staircase family and frozen inputs, retaining the original Claude disclosure. The balanced layout is inherited from James Chang/PR34, RaD/hipotures and subsequent contributors; exact refinement follows PR65. Also credit Avi Eisenberg/ikeboy, icekylinx, Aurel Prosz/Paureel, Chafik Boukhalfa, Dominik Scholz, Rohan Arun and all original authors. Licenses and source notices are preserved.

This composition was prepared by Rohan Arun with OpenAI Codex assistance. All-size compiler, routing, recovery, fixed-tape and analytic hypotheses remain assumptions. There is no unconditional theorem, new Lean proof, practical speedup or global-optimality claim.
