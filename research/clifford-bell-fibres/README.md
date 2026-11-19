# Exact Gaussian-dyadic Clifford recovery at width 13

For the full four-qubit projective Clifford alphabet, **13 is the minimum tensor width for exact coefficient recovery over the Gaussian dyadics**. At width 13 an explicit left inverse of the normalized tensor map uses only coefficients in `Z[i,1/2]`. Tensoring each output row with its target's unit-norm single-copy functional extends it to every larger width. Ali Romman's complex rank obstruction at width 12 supplies the lower bound. The construction resolves all four widths left open by #7798. [Proof](PROOF.md) · [Complex threshold #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766) · [Width-17 handoff #7798](https://github.com/CrocSwap/integer-mult-bounds/pull/7798)

The observation is an arbitrary linear combination of `(vec(U)/4)^(tensor f)`, with one fixed Gaussian-dyadic representative per Clifford scalar coset. The proof constructs a linear decoder on the whole observation space and proves exact recovery on the image. It also implies full column rank after reduction modulo every odd Gaussian prime. The established width-17 threshold for all eight-qubit stabilizer rays concerns a larger alphabet.

## Construction

1. Use six Bell pairs to read which symplectic transformations carry one ordered tuple of labels to another. The thirteenth copy retains a matrix. A known Weyl correction removes phases depending on the chosen Pauli lift, exposing the sum of the unknown matrices over eight symplectic transformations.
2. Translate these sums to isolate one symplectic transformation at a time. The certificate checks all 1,024 characters of the binary symmetric shear group. For 576 characters, the subgroup average acts as the identity on the character component. For the other 448, a change of symplectic coordinates gives one quarter of that component. Multiplication by four completes the same reconstruction over the dyadics.
3. Within each recovered matrix, a normalized trace against each of its 256 possible Clifford representatives returns that representative's coefficient.

Conditional on #7772's uniform spectral enclosure, the exact dyadic iteration from #7798 yields an inverse with Euclidean operator norm **below 3.021 at every width f ≥ 13**. This controls arbitrary additive observation error. The canonical least-squares map has odd denominators at width 13. The two decoders agree on the noiseless image and may differ on arbitrary observations. The physical cost of implementing either the initial decoder or the 8,192 iterations used for the norm bound remains open. This contribution makes no change to κ. [Stability proof](PROOF.md#5-stability-on-the-normalized-observations) · [Spectral bounds #7772](https://github.com/CrocSwap/integer-mult-bounds/pull/7772) · [Canonical obstruction #7792](https://github.com/CrocSwap/integer-mult-bounds/pull/7792)

## Reproduce

Run from the repository root with CPython 3.12 and the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-bell-fibres
```

- `verify.py` constructs binary symplectic matrices, checks the eight-element stabilizer among all 64 candidate shears, and verifies every character identity using literal matrix conjugation. It also checks the Fourier resolution, failure controls and the numerical margins for the stability corollary.
- `independent_check.py` uses separate computational-basis four-qubit matrices. Three calibration frames cover 297 operator instances with different global phases and 6,144 within-fibre coefficient checks. A second experiment passes an actual mixture with 80 nonzero coefficients through the Bell measurements. It recovers all 2,048 coefficients on the restricted alphabet, including 1,968 zeros and deliberate cancellations.
- Both checkers run normally and under optimized Python. The proof supplies the full-alphabet statement. No full tensor matrix, production multiplier, external spectrum replay, human proof certification or formal-kernel check is included. [Replay commands](VERIFY.json) · [Pinned research inputs and context](SOURCES.json)

## Credit and coordination

Prepared by **apoursh** with substantial OpenAI Codex and separate agent assistance, under Apache-2.0. Ali Romman's work supplies the original complex threshold, spectral enclosure, Bell-sector analysis and canonical obstruction. The Pauli and character-theoretic lineage includes alephnan and Nick Petalas. The starting question and the dyadic stabilization iteration are from #7798. Projective Clifford actions, finite Fourier analysis and group-algebra idempotents are classical. The exact width-13 upper bound in Sections 1–4 has its own proof. [Bell-sector predecessor #7789](https://github.com/CrocSwap/integer-mult-bounds/pull/7789) · [Research claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19753161) · [Task scope and overlap](TASK.json)

## Open next questions

1. What does one transported Bell block cost at a named caller? Include coordinate access, precision, movement, workspace and cleanup before summing the cost of the full decoder.
2. Can a sparse, exact width-13 implementation reach a useful noise bound with fewer Gram applications? Start with the character sum for one output coefficient and quantify cancellations at a fixed input layout.
