# Fixed-paid rank-five prefix bounds on chart 3→233

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to independently reproduced conditional κ = `0.00364665195644` on #7334 at `aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. [Comparator #7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) · [Signed caller #7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)

All 17 frozen public banks for productive roles 289 and 1052 fail the necessary prefix test for a fixed-paid 2+3 or 3+2 split. The banks occupy intermediate charts 329 and 340 with no owned fields. Both prime-field engines produce full exterior prefix rank on every bank. The primary minor's coordinate set remains nonzero at the independent prime in every case. There are no unresolved keys in 3→233. Fourteen keys on endpoint groups 712→127 and 714→127 remain outside this replay. [Exact per-key agreement](receipts/AGREEMENT.json)

The directed one-edit saving upper is about 0.207666506667591 raw at the comparator crossing. The compatible two-role upper is 0.415333013335181, with all 110,519 paid positions held fixed. The tested scope produces zero verified saving. [Complete price and proof](PROOF.md)

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-rank-five-chart233-prefix-bound/replay.py
```

The standard-library replay authenticates the pinned #7370 manifest, price and geometry, as well as the exact #7334 word. It reconstructs the directed price, freezes all 17 keys, checks the primary minors at both primes and rejects altered selection and geometry. Add `--out fresh-directory` to retain the four receipts. The replay runs with no Git metadata, network, external input root or prior temporary state. [Verification](VERIFICATION.md) · [Provenance](PROVENANCE.json) · [Path-keyed pins](LOCAL-PINS.json)

## Open next questions

Can either seven-key group on 712→127 or 714→127 supply a pure prefix and suffix with nonzero unit pairing? Start with the remaining key list in the regenerated selection, price one cohort on the full signed invoice and screen its exterior rank. Any positive support still needs an exact signed construction and complete verification.

## Credit

#7370 at `a41edc3ae92332a7a1f1ba90e9ea4901d0530185` supplies the complete catalogue and price. #7373 at `f390469548c0f7a44465bf80476ad7bc5a8e20f5` supplies the two-prime replay workflow and covers the separate 3→238 cohort. [Catalogue #7370](https://github.com/CrocSwap/integer-mult-bounds/pull/7370) · [Predecessor #7373](https://github.com/CrocSwap/integer-mult-bounds/pull/7373)

#7338 supplies the complete signed invoice, #7298 the directed arithmetic and #7319 the exact helper census. #5599 supplies the common-frame split method, #7367 the exterior proof on a different cohort and #5994 the earlier broad census on another word. [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) · [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) · [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319) · [#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) · [#7367](https://github.com/CrocSwap/integer-mult-bounds/pull/7367) · [#5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994)

OpenAI Codex and subagents materially assisted proof, implementation, independent verification and packaging.
