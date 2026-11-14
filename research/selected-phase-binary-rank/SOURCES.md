# Exact source and mathematical dependencies

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
`SOURCES.json` pins canonical provenance; `DEPENDENCIES.json` authenticates five retained inputs. The three canonical scientific files were directly re-extracted with `git show` and compared byte-for-byte.

- `inputs/BILATERAL-LDU.md`, canonical `research/native-kappa-30201655/modern-sources/BILATERAL-LDU.md`: Statement gives the exact `G_jk` coefficient used here; section 4 defines its periodization on `0 <= j,k < s`. This package deletes aliases by its declared object; it does not identify `G` with the full periodized matrix.
- `inputs/FINE-PRIME-PADDING.md`, same canonical modern-source directory: section 1 gives distinct original odd source primes, dyadic target sides, the fine interval and source scale; section 2 gives common integer `alpha` and `a=pi alpha^2`. Original side lengths are retained; local capped lengths do not replace them.
- `inputs/PHASE-CELLS.md`, canonical `references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md`: exact nearest-grid and phase-cell definitions, with the physical cells at the period ends kept separate. Its older quantitative inverse/precision regime is not used.
- `inputs/A9-PROOF.md`, published [arbitrary-order binary Gaussian rank theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/085b30f8e036f69421d5953d0993ac4974ec3f24): nonzero per-order matching minors and inverse/reversal identity.
- `inputs/A10-PROOF.md`, published [pointwise fine-prime core theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/da06a3d10e06870a0279e33dd5056ded8d7e7a38): even-path trimming, common-base CRT specialization, exact source-normalization warning and classical input. Both predecessor proofs retain their original bytes. Primary matching-path and polynomial helpers are adapted from A10's credited verifier; they are not claimed as independent reimplementation.

## Classical input

A. Gelfond, *Sur le septieme probleme de Hilbert*, Izvestiya Akademii Nauk SSSR, Seriya Matematicheskaya (1934), no. 4, pp. 623-634. [Official record and full-text link](https://www.mathnet.ru/eng/im4924). The logarithm-ratio theorem on printed p. 628 was read in the original PDF, also independently in the predecessor review. It implies that any value of `a^b` is transcendental when `a` is algebraic, `a != 0,1`, and `b` is algebraic irrational. Here `a=-1`, the chosen logarithm is `i pi`, and `b=i alpha^2/S`; all premises are explicit. This is commonly the Gelfond-Schneider theorem; Schneider's independent work is credited. No numerical transcendence test is supplied or claimed.

CRT, elementary finite-field root counting, determinant expansion, path perfect matchings and Schur complements are classical. The new scoped step is the positive count of actual source starting indices whose two directed exponent numerators separate the bounded box, followed by pointwise specialization of the per-order minors with phase/chirp retained.

## Attribution

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The lead proposed the source-phase approach and the all-residue strengthening; the worker derived the exact source mapping, polynomial specialization, selector bill and bounded primary checks. A separate AI worker reviewed the proof, original source grid and independent exact checks. No human or formal-kernel acceptance is claimed.

Credit Chafik Boukhalfa's [fine-prime work, #1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786), Vlado Vojdanovski's [phase-cell work, #1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), IdeaOuter's fractional-shift work credited in [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758), Jeremy Kothe and the retained bilateral/source package lineage, and Douglas Colkitt/OpenAI's framework. Original source notices and the Apache-2.0 license remain unchanged. No historical source contribution is claimed as new.
