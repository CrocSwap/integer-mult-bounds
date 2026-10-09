# source-assisted-v4-layer

**Complex saving 7.0861·10⁻⁴ (no new κ).** PR #194's source-assisted complex word with this package's physical
layer (PR #200's descent, seeded from PR #168's frames) certifies

    a_C = 3543063/5000000000 = 7.0861260·10⁻⁴       (PR #194: 7.0091844·10⁻⁴, +1.10%),

through PR #184's flow, exact lift and contract and PR #194's assembly, which with PR #200's bit supplier gives
κ = 6768823/10¹⁰ (the bit branch binds, as in PR #202). The complex cap of this lineage and the exact-DFT exponent
saving (`research/exact-dft-transfer`) rise to 7.0861·10⁻⁴. [PROOF.md](PROOF.md) states what changes and what is
checked.

## Verify

    python -m pip install numpy==2.3.5 scipy==1.17.0
    python3 -B research/source-assisted-v4-layer/verify.py        # about 80 seconds; -O is refused

The script rebuilds the 308 pinned files of PR #202 (`8d8d67b`) from `baseline-pr202.tar.gz` after checking every
sha256 in `SOURCE.json`, regenerates the PR #168 v4 cache and the aligned word, installs the physical layer of
`witness/`, admits it with PR #200's complete complex checker, runs the frame flow with the package's kernel pairs,
the exact lift, the contract (with the package's physical and kernel pairs as the frozen witnesses) and the assembly,
and compares with `certificate.json`. `--write` regenerates the certificate; `--temp-root` chooses scratch storage.

## Files

`verify.py`, `certificate.json`, `SOURCE.json`, `baseline-pr202.tar.gz`, `witness/physical-frames.json`,
`witness/physical-pairs.json`, `witness/kernel-pairs.json`, `discovery/` (the descent that found the layer; not run
by the verifier), `PROOF.md`, `NOTICE`. `.github/workflows/source-assisted-v4-layer.yml` runs the verifier on
Python 3.11 and 3.13.
