# Bound one-field typed compression of two public MOVEs

The exact [#7334 native word](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` contains two adjacent public MOVEs at clocks 32944 and 32945. Roles 625 and 624 both move from chart 3 to chart 117. Each old operation is rank five and both arbitrary dirty inputs must receive the full output. The [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the pinned exact Gaussian compiler and verifier. **NO VERIFIED GAIN.**

The chart operator is exactly monomial-conjugate to five C axes and has projective order four. On two fields of dimension N each, identity erasure leaves rank at least 11N/8 at every positive tensor width. A change that factors through one of the original fields has rank at most N. At width four, erasing one core and leaving any unitary monomial gives target displacement rank at least 1023N/1024. One normalized rank-1-to-6 C core can supply at most 7N/8. Both necessary inequalities fail. The optimistic two-rank-five to one-rank-six tariff is about +67.66946959214 raw before other costs. No typed child realizes it in this scope. [Proof](PROOF.md)

Use POSIX CPython 3.12 from a clean checkout:

```sh
python3.12 -I -B research/p104-two-move-typed-volume-bound/replay.py
```

The replay authenticates the exact word, compiler, input paths and receipts. It runs both methods, compares all 512 one-slice columns where applicable, checks a dropped-gate control, and recomputes the directed price and rank bounds. It uses the standard library and needs no network or prior temporary state. [Verification](VERIFICATION.md)

## Open next questions

Can an enlarged typed field or a genuinely body-dependent bypass serve both dirty-input outputs with fewer fully charged complex children? First pin one such interface and compute its admitted width, address volume, complete compatible count and directed price. A price-positive case still needs exact arbitrary-input forward and adjoint action, ownership, route and restoration, paid profile, precision, tapes, and the full recurrence. This package covers one pair and the stated erasure models.

[#7414](https://github.com/CrocSwap/integer-mult-bounds/pull/7414) supplies the exact adjacent-pair census and the independent rows for this pair. [#7245](https://github.com/CrocSwap/integer-mult-bounds/pull/7245) supplies the earlier fixed-output consolidation comparison and leaves a changed typed child open. [#7406](https://github.com/CrocSwap/integer-mult-bounds/pull/7406) supplies the separate Type B one-field displacement precedent. #7334 supplies the exact word and #7113 the signed Gaussian tools. OpenAI Codex and its subagents materially assisted the proof, implementation, independent replay and packaging.
