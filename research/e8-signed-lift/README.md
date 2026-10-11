# Exact signed integer lifting on the E8-backed bit supplier

**Conditional κ = 801967436473393 / 10^18 = 8.01967436473393 × 10^-4.**

This package composes a new integer-lifted shared-donor witness with ten terminal sinks and one source-corrected early cache on PR351's compact physical bit word. It uses PR352's unchanged E8 complex coarse bound as explicit input. The full composed word, its actual bank stock, and all 47 strict outer assembly inequalities determine the result; stand-alone gains are never added.

The improvement over PR352's conditional κ is **0.11032656%**. This is an incremental, reproducible improvement and a reusable synthesis extension. It is not presented as the current leaderboard record or as a massive exponent jump.

| Quantity | Final value |
| --- | ---: |
| Bit coarse saving c | 401305552420403 / 500000000000000000 |
| Inherited E8 complex coarse saving b | 876248285600677 / 10^18 |
| Local paid rank mass | 169174 |
| Local helper registers | 7610 |
| Local unit ADDs | 358042 |
| Physical replicas | 300 |
| Banks per stage | 397002 |
| Literal stock / normalized stock | 3137010 / 627402 |
| Finite selector charge | 1806132027000 |
| Counted primitive coefficient bits / payload prefix bits | 57 / 92 |

## The contribution

The new synthesis searches for **exact signed integer relations**, rather than stopping at binary dependencies or unit-coefficient relations. For a helper r, extract its complete target response T_r and transport its initial compensation READs through the actual later target operations to obtain Q_r. At a common cold cut, the donor's future response is F_r = T_r - Q_r. The selected relation is

    Q_p = sum_d alpha[p,d] F_d.

Delete the pivot's initial READs and install the corresponding donor shears at their common admissible cap. The deleted response -Q_p and new response sum alpha F_d cancel exactly. Restore the donor shears at the final full frame. The literal emitter and admission checks account for those restorations, all frame moves and copied lifetimes.

The final selection has **171 pivots and 283 distinct donors across 48 disjoint groups**. It contains 560 nonzero terms, including sixteen coefficients of magnitude two. Each ±2 term is emitted as two ordinary ±1 ADDs at the same frame. Both additions are charged, but no additional recursive child is needed to move between frames. There are 576 setup ADDs and 1184 removed initial READs.

Donors are charged once across the pivots they serve. The selected kernel's local histogram change, beyond the sinks, is

    H1:+165, H2:+315, H3:-315, H4:+21, H5:-21.

This saves 171 rank mass: 165 is a histogram coefficient, not the pivot count. The ten sinks save 200 and the corrected cache saves 15, for a total reduction of 386 from the compact source. The complete moment and stock are recomputed afterward.

A decisive control removes the adjacent pair implementing one actual coefficient-two term. Binary semantics stay unchanged, while four exact integer target entries change by magnitude two. Thus an F2-only checker cannot certify the productive extension.

Gaussian elimination, adjoints, integer lifting, kernel identities, sinks and corrected caches are established ideas. The own contribution is this signed integer-lift/shared-donor synthesis, its new finite witnesses, and their complete physical composition. All selected donors still have T_d = 0; this is not a successful warm-donor or nonzero-total-response construction. A first-ever method across the literature is not asserted.

## Reproduce the own construction

Run from the repository root with Python 3.11 or later, a GNU-compatible C++17 compiler and Boost headers available:

```sh
python -m pip install -r research/e8-signed-lift/requirements.txt
python -B research/e8-signed-lift/verify.py /tmp/e8-signed-lift-review
```

Use a **new directory outside the package**. Existing outputs are preserved. If Boost is not on the default include path, add `--boost-include /path/to/boost/include`; `--cxx /path/to/g++` selects a compiler. Keep Python assertions enabled. On Windows, use any fresh output path and the corresponding g++/Boost paths.

The upload bundles the JSON header and the three unchanged exact pricing modules needed for the replay. It contains no executables, GPU weights, large response arrays or machine-specific dependency paths. File bytes are pinned by `MANIFEST.json`; `.gitattributes` disables text conversion for this folder.

The replay:

1. Checks the manifest and decompresses SHA-bound public source inputs.
2. Rebuilds the sinks, integer-lifted kernel and corrected cache, and requires the final literal word hash.
3. Checks all 9148800 retained signed input-to-target entries, the 9600 removed zero dirty entries, every actual clean-source operand span, and all 11450 five-stage binary formal columns.
4. Checks frame/COPY legality, both reflected ledgers, six new prime-safe frames, exact changed projector charts, and actual zero-padding-free bank allocation over 300 replicas.
5. Rejects ten separate omitted setup/restoration/scatter categories and checks the even-term control.
6. Prices the actual histogram using two independent exact rational moment engines with the full 10^-16 fallback, checks all 47 strict assembly constraints and the adjacent excluded κ, then verifies the finite-cost invoice.

The full own replay took about 90 seconds for compilation and changed-word admission on the development machine, followed by pricing/invoice checks. This is an observation, not a portable timing guarantee. Logs and generated receipts are written to the selected output directory.

## Scope and inherited inputs

The result retains the compiler, common-chart, row-restoration, selector/routing, prime-supply, precision/recovery and analytic-transfer interfaces of the underlying public construction. The E8 complex supplier is unchanged. Its published coarse certificate is an explicit pinned input; this replay does **not** redo the public complex proof or claim it as own work. Public unchanged mathematical verifiers are not rerun.

This is a checked conditional finite construction and exact assembly bound. It is not an unconditional sub-n-log-n multiplication theorem, and no new Lean certificate is asserted.

## Files and provenance

- `SOURCE.json`: PR351/352 heads and the compact source hash.
- `data/`: immutable inputs, exact literal selection, frame inventory and source/final pins.
- `code/`: deterministic construction, changed-word checks and exact price/invoice.
- `receipts/`: completed replay evidence and the initial replay input manifest.
- `notes/`: sufficient synthesis arguments and preserved successful/unsuccessful routes.
- `discovery/`: optional native discovery sources and the original exact signed selection; not needed for the fixed-witness replay.
- `vendor/`: only the unchanged pricing extract, source pins, license and attribution.

Source word:

    05df0a39669bb077a9a2fa527904023a5a9da18cf644e06429d44f2a7ea92603

Final word:

    66ba5f42081c7299bd20be713500d3cce87494851baac7e16f840a3e75ba0055

[PR351](https://github.com/CrocSwap/integer-mult-bounds/pull/351), [PR352](https://github.com/CrocSwap/integer-mult-bounds/pull/352), and [Jacob Sussman's E8 work](https://github.com/jacobalansussman/wht-power-saving-lean) supply the credited baseline. Prepared with OpenAI Codex assistance. See `NOTICE.md` and `LICENSE`.
