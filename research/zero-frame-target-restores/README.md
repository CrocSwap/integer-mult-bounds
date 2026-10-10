# Zero-frame target restores on PR271’s PR272-based helper cleanup

Conditional finite saving:

```
kappa = 8921126351038225858611 / (125 * 10^23)
      = 0.00071369010808305806868888
```

This retimes three connected blocks of nine target-to-target restoration ADDs on PR271's exact word after its PR272-based helper cleanup. The 925 kernel pivots, 217 target groups and PR271’s shortened helper endpoints/bank stock stay unchanged; the target retiming preserves PR271’s scalar/COPY stream and rank mass. Twenty-seven ADDs use the already available zero frame. Twelve pairs of rank-20/rank-1 recursive moves become twelve rank-21 moves, eliminating twelve local recursive children.

Exact gain over freshly reproduced PR271 `ebc1defe8c13f39f86e5901c3437c1be52886a2b` is `27951693448094147889/10^27`, about 0.00391666%. PR271's 99-helper cleanup was published while this target-frame selection was being prepared on PR272; the selection was rebound by unique full instruction content, then composed and fully checked. No priority, global optimality or unconditional theorem is claimed.

## Reproduce

The package is additive to main `3b6b66891c0ac888521cf591fe306c6286601d4f`. It does not copy either pending predecessor package. Obtain separate checkouts at pinned PR271 `ebc1defe8c13f39f86e5901c3437c1be52886a2b` and pinned PR272 `4d23d0ee5682c99b792614bae4bc5330da19ff13`, then use Python 3.11+, SymPy 1.14.0, C++17 and Boost, as the predecessor requires:

```sh
python3 -B research/zero-frame-target-restores/verify.py \
  --base /path/to/pinned-pr272/research/filtered-kernel-target120 \
  --cleanup-base /path/to/pinned-pr271/research/cleanup-sandwich-272 \
  --output /tmp/zero-frame-restores-replay
```

Use a fresh output outside the source packages. Optional `--cxx g++-16 --boost-include /opt/homebrew/include` selects an existing toolchain. No network is used by the verifier; no installation is part of it. The workflow retrieves the pinned source in a separate checkout and uses the predecessor's declared Python dependencies.

All ten cleanup package file hashes and the base manifest SHA256 are pinned, the predecessor verifier freshly regenerates PR249 sources and compiles all nine native checkers, and its exact baseline receipts must reproduce. The pinned cleanup verifier then reproduces its 99-helper result on that freshly computed baseline. The target rewrite is bound to the exact cleanup final word SHA256. It checks exact nesting, scalar/COPY projection, rank mass and the actual histogram delta. The 99 shortened helper endpoint charts and exact bank tiling are recomputed on the actual final word. A separate target-role audit verifies all 27 ADDs are pure target restores and the chosen frame is the exact zero subspace. The original exact integer source-span audit, seven unchanged native acceptance stages and independently authored bitset/census audit run on the final word. Exact expected kappa and word hash are compared only after those computations. Each stage is bounded to 600 seconds within a one-hour limit.

See `PROOF.md`, `AUDIT.md`, `NOTICE.md`, `expected.json` and `evidence.json`. This local discovery scanned 26591 equal-frame components and found three candidates using existing adjacent frames; all three have disjoint target roles and were selected deterministically. No random seed, paid compute or new local installation. The baseline replay took 128.95 seconds wall and peaked at 1551433728 bytes RSS; candidate scan/rewrite/span/native-plus-independent checks together took 16.65 seconds wall, peaked below 810 MB and had zero swaps. The original PR272 target-only packaged replay passed in 145.15 seconds wall. PR271 replay reused the verified baseline and passed in 20.42 seconds; composition checks passed in 12.63 seconds, and the 396 endpoint/connector chart and bank recheck took 10.74 seconds. These peaked below 815 MB with zero swaps. The final fresh composed-package replay passed in169.39 seconds wall,181.88 seconds CPU, peak RSS1630765056 bytes and zero swaps (`evidence.json`). Preflight CPU and download bytes were not measured.

The inherited `make entrance-bank-verify` passed in 55 seconds. A broad `make verify` was stopped at its explicit 600-second cap during recycled-bit integration: it is **incomplete**, not reported as a pass. All witness-specific stages listed above must pass.

## Scope

Retains the public uniform all-size compiler, common weighted chart, restored-row, routing, prime supply, precision/recovery, complex correctness and analytic interfaces. Kernel and endpoint identities are over F2; source signs and geometry remain separately checked. Native checkers share predecessor provenance, and certificate success is not formal verification of the full integer-multiplication theorem, a practical runtime benchmark or a proof of linear time.

The inherited target is O(n(log n)^(1-kappa)). This retained assembly has a<b<1/32 and kappa<a/(1+a), hence kappa<1/33. Removing the logarithmic factor would require new transfer/assembly mathematics and uniform correctness/cost proofs. This scoped interface ceiling is not a general lower bound for integer multiplication.
