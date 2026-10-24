# Native Word RAM Gaussian adapters

This package removes TM subroutines from the arithmetic components developed
here. Its main contribution is two concrete native algorithms for the actual
Gaussian resampling maps, with paid preparation, precision and recovery bounds.
It does **not** establish a new best κ or a complete faster cyclic transform.

1. **Chirp blocks:** a centered Gaussian rectangle is a diagonal–Hankel–diagonal
   product. One explicitly paid convolution evaluates it in O(q log q) Word RAM
   operations. Whole-rectangle blocking gives the actual forward map in
   O(t log p) operations, plus shared scalar preparation, instead of visiting
   Θ(α√p) weights for every output.
2. **Reusable banded inverse:** the actual periodic near-identity matrix has an
   explicit Gaussian tail. Truncate to h = O(1 + √p/α), factor its ordinary band,
   and handle the corners with a rank-at-most-2h Woodbury correction. Uniform
   pivot and Schur bounds give O(s h²) paid preparation and O(s h) per new
   right-hand side. Nothing assumes an inverse oracle.

For T entries and d = Θ(p^ε) tensor axes with α² = Θ(d√p), reuse across the
actual parallel fibers yields Gaussian adapter work

    O(T[p^ε log p + p^(1/4+ε/2)] + n^η polylog n + n^o(1)),

where p = Θ(log n) and η > 0 is a fixed small setup exponent. See
[NATIVE-RECOUNT.md](NATIVE-RECOUNT.md) for the full hypotheses and cost proof.
This improves the adapter's arithmetic count; it does not improve the complete
multiplication exponent without the remaining transform integration.

The package also supplies a direct exact O(n) packed Word RAM multiplier with
an all-input rounding proof, generated roots, signed exponential tables, paid
constant-cost phase queries, and a finite-precision rational Gaussian kernel.
The O(n) multiplication baseline is classical, not a new bound: see
[Fürer, 2014, Theorem 4.1(a)](https://arxiv.org/abs/1402.1811).

## Model and files

All native algorithms use one sufficiently large fixed constant times log n
bits per word, with ordinary bounded-word MUL/DIV, shifts, masks and indexed
memory. Full n-bit operand multiplication is confined to independent test
oracles. Every setup cost, including roots, coefficients and fixed-kernel FFTs,
is paid. Large word constants simplify the proof; no practical speedup is claimed.

| Result | Argument | Executable evidence |
|---|---|---|
| Gaussian block and forward map | GAUSSIAN-CHIRP.md; NATIVE-RECOUNT.md | chirp_check.py; gaussian_block.py; native_convolution.py |
| Actual periodic Gaussian inverse | NATIVE-BANDED-INVERSE.md | band_solve.py; periodic_solve.py with factor reuse; gaussian_inverse.py constructs actual N entries |
| Direct exact O(n) native multiplier | PROOF.md; FFT-ERROR.md | native_fft.py, including a 65,535-bit case |
| Generated roots and exact carries/CRT | ROOTS-RECOVERY.md | root_seed.py; recover.py |
| Paid exp and phase tables | NATIVE-EXP-TABLE.md; PHASE-TABLES.md | exp_table.py; phase_tables.py |
| Rational Gaussian/Walsh kernel lowering | NATIVE-STABILITY.md | Informal source-specific proof; no new kernel replay claimed |
| Sufficient full-transform caller | NATIVE-OUTER-ASSEMBLY.md | Informal assembly theorem; faster caller not supplied |

These are informal universal arguments and finite executable controls, not Lean
proofs, emitted RamStd programs, human peer review or a certificate of the full
multiplication theorem. Python integers emulate explicitly bounded magnitudes;
Decimal and Fraction appear only in independent references. The real-grid
Gaussian executable covers a concrete block family; the periodic inverse and
actual Gaussian coefficient path have separate real-valued fixtures. General
complex-matrix elimination remains proof-level; real Gaussian N acts on complex
data by two real solves. Source bytes are authenticated before any replayed module executes.

## Reproduce

Python 3.12, standard library only; commands work on Windows and Linux:

    python3.12 scripts/research_package.py --package research/native-word-fft

Standalone, including an authenticated Git-free export:

    python3.12 -I -O -B research/native-word-fft/verify.py

VERIFY.json registers the bounded replay. TASK.json preserves the assigned
scope change; the old register-model card is provenance only. SOURCES.json
pins canonical main and the selected record. Additional source and overlap
coverage is documented in OVERLAP.md, KERNEL-PRECEDENTS.json and
RECOVERY-PRECEDENTS.json. Source inspection is not kernel verification.

## Open next questions

Connect the native adapters, rational kernel, phases, synthetic polynomial
transforms, exact record products and recovery in one complete cyclic caller.
Freeze every normalization and one common precision/memory bound, then check the
full paid recurrence before reporting any new κ. Expand the actual Gaussian fixtures into the full asymptotic parameter and
normalization regime, and connect the reusable periodic factors to every axis
of that caller. TASK.json gives
concrete first steps and their relevance.

## Credit

Prepared by Dugongue with substantial OpenAI Codex assistance, using the root
worker and three parallel workers. The Gaussian identities and inverse estimates
come from OpenAI/math's retained manuscript and Harvey–van der Hoeven. Chirp
convolution, FFT, Woodbury and diagonal dominance are classical precedents.
The rational provider is artuskg's PR #956, building on Dugongue's PR #390 and
Jacob Sussman's bridge/frame/RAM/Fourier lineage; NOTICE.md lists the relevant
PRs. PR #647 is a distinct exact-scalar precedent, not a proved finite-word
caller. PR #4535 supplies the current pending comparison; PRs #4538/#4541 are
our previous Word RAM compiler/TM-transfer work. Their TM simulation is not used
in these native constructions. Problem 1.8 limb/inversion modules and earlier
Gaussian/Machin proof notes informed the bounds; their inspected hashes are
recorded without claiming fresh Lean audits. No worldwide novelty claim is made.
