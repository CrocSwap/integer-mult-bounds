# Seven-stage retimed P104 price candidate

The retimed native scheduler from [PR #8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042) admits an exact **candidate invoice at κ = 0.003890115286594460** when extended to seven ordinary stages. The candidate is above the previously studied six-stage fixed-word ceiling. Its source price, complete stage recurrence, signed margins and activation arithmetic are executable. **It is not yet a certified new multiplier bound:** an independent reader found no counterexample to the written role accounting but did not discharge the exhaustive all-size binding from the seventh dispatcher to the physical scratch inventory. The proposed clock and stock conclusions depend on that additional bridge as well as the five inherited scientific premises.

At its fixed binary trial `c=4484997569314581/2^60`, #8042's retiming retains the same 36-call binary productive and paid labels. With the same `249/250` recurrence, its ideal six-stage limit is approximately `0.0038901152865944444484`. Its seven-stage ideal limit is approximately `0.0038901152865944603186`. The fixed trial and recurrence cannot reach `0.00389046`, but this does not exclude a changed raw word, coupling, stage rule, or other architecture.

The candidate uses binary rank logarithms `10^12*16^i` for `i=0,…,6`, numerical logarithm `36000`, `eta=39/10000` and stop gap `g=10^-20`. It checks all seven strict stage prices, the full `7/(2H_i)` binary debit, the numerical debit `1/(5H_M)`, and all 54 strict and four functional signed inequalities. Its final stage limit is approximately `0.0038901152865944600965768`; its ordinary booking `κ+5g` is lower by approximately `4.65768e-20`. The reproducible [exact receipt](RESULT.json) includes the complete price history, signed margins, connected entrance and conditional clock bounds. The [proof note](PROOF.md) identifies the new bridge and its proposed argument.

## Sources and reproduction

The exact retimed predecessor is Ali Romman's [#8042 head `3d33cb0c8a523b66d91e8de8250b85d0a436eb35`](https://github.com/aliromman/integer-mult-bounds/tree/3d33cb0c8a523b66d91e8de8250b85d0a436eb35/research/retimed-native-multiplier). Its 48 small source files are stored once in [source-8042.tar.gz](source-8042.tar.gz), with per-file Git blob IDs and SHA-256 values in [SOURCE-8042.json](SOURCE-8042.json). The exact, byte-identical #8030 predecessor archive is stored separately once as [predecessor-8030.tar.gz](predecessor-8030.tar.gz), Git blob `e00a6bfe8328b4c982bf0689c4d55c8207515514` and SHA-256 `769d5a05cc1373fa22ed5956af636992fcd19d7e5c1753a32033a73c358cd31c`. The verifier checks every source byte and applies the original signed-margin overlay and original #8042 patch before the additional local profile and guard edit. These byte checks do not prove Git ancestry or independently validate the predecessor's mathematics.

With CPython 3.12 and Git on PATH, from the repository root run:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-seven-stage-retimed
```

The six registered cases separately check original #8042 prices and the seven-stage invoice; real recipe initialization, seven threshold choices, and stop-policy propagation; inherited finite chronological loans; inherited physical word and precision controls; inherited fenced slab controls; and a feasible signed product bound to the actual new profile. The signed control uses a reduced rank and local positive path. It does not execute production-sized cohorts. On the preparation host the final rank logarithm exceeds `sys.maxsize`, and attempting its actual `1 << H_7` allocation raised `MemoryError`; even the bits alone need more than two exabytes. Neither a practical crossover nor full physical execution is asserted.

## Open next questions

1. Can every seventh-stage source role and its lifetime be exhaustively injected into the proposed conservative interval inventory, including nested stage entries, true high packets, pending/answer pages, and non-native positive calls? First independently trace `ordinary_carrier.stage_body`, `Receiver`, and their common arena constructors against the sevenfold argument in [PROOF.md](PROOF.md). This bridge blocks a same-premise seven-stage multiplier theorem.
2. Can the original retimed source's all-column physical action, owner erasure, uniform transfer, numerical/tape precision and analytic recovery be independently reviewed? The finite controls execute selected instances and do not discharge these inherited assumptions.
3. Can a changed word or a different fully funded ordinary architecture reach `0.00389046`? The fixed-trial calculation does not exclude such a change; first derive its complete native and signed invoices and physical ownership.

## Credit

Ali Romman's #8027, #8030 and #8042 supply the paired physical words, native caller, and unpowered chronological transport and clock. Clear1nsight's #8033 and #8035 supply the tilted tariff and signed-margin extension. The seven-stage arithmetic, proposed role accounting and package were prepared for Clear1nsight with substantial OpenAI Codex assistance. This is a separate research candidate; upstream review or selection is not implied. See the predecessor source's own `NOTICE.md` in the pinned archive for the full chain.
