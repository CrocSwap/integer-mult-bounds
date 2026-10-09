# exact-dft-transfer

**No new κ.** The complex suppliers of this repository transfer to the exact discrete Fourier transform: in the
exact complex-arithmetic model of OpenAI's *An explicit power saving for the exact discrete Fourier transform*
(25 September 2026), eumemic's batched tensor recursion (`eumemic/exact-dft-bounds`) turns each certified complex
moment root `a` into

    exact DFT of every length, and exact complex convolution, in  O(n (log n)^(1−a) (log log n)^(3+a)).

| Supplier | a | θ = 1 − a |
|---|---:|---|
| PR #144 (main) | 4.856·10⁻⁴ | eumemic's published value |
| PR #200 | 6.654·10⁻⁴ | +37% |
| **PR #194 (source-assisted)** | **7.009·10⁻⁴** | **+44%** |

[PROOF.md](PROOF.md) states the transfer and the three supplier propositions (by reference). The same two new
propositions are eumemic/exact-dft-bounds pull request #1.

## Verify

    python3 -B research/exact-dft-transfer/verify.py --check     # stdlib only, about 20 seconds; -O is refused

The script checks every pin in `SOURCE.json` (the main certificate of PR #144 and the vendored certificates of
PR #200 and PR #194, byte for byte as `git show <commit>:<path>`), rebuilds the three child histograms from those
certificates, checks the ledger identities (rank sum, deficit = Wm − rank = 2v − 3ℓ, largest child < m), certifies
the batched moment at each claimed saving in exact rational arithmetic, rejects the next 10⁻⁷ grid point for each,
and compares with `expected.json`. `--write` regenerates the certificates.

## Files

`verify.py`, `scripts/moment.py` (the exact bounds, adapted from eumemic's `verify_moment.py`),
`certificates/network-children-*.json` and `certificates/moment-*.json`, `references/pr200-certificate.json`,
`references/pr194-certificate.json`, `SOURCE.json`, `expected.json`, `PROOF.md`, `NOTICE`.
`.github/workflows/exact-dft-transfer.yml` runs `--check` on Python 3.11 and 3.14.
