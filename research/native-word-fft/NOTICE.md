# Attribution and license

New exposition and executable models: Dugongue, with substantial OpenAI Codex
assistance from the root worker and three parallel Codex workers. Apache-2.0;
see LICENSE. Independent agent review means an additional AI review of the
stated source bytes, not human peer review or formal kernel certification.

The actual Gaussian resampling identity, the definition N = C T D, and its
near-identity estimate are predecessor facts from OpenAI/math's manuscript,
retained in this repository at upstream/build/sections/07-resampling.tex, with
its citations to David Harvey and Joris van der Hoeven's integer-multiplication
work. The original OpenAI source/license attribution in the repository remains
in force. No retained upstream file is modified by this package.

Classical algorithmic antecedents: Cooley–Tukey FFT; Bluestein's chirp filtering
(DOI 10.1109/TAU.1970.1162132); Rabiner–Schafer–Rader's chirp z-transform
(DOI 10.1002/j.1538-7305.1969.tb04268.x); Woodbury low-rank inversion;
row-diagonal-dominance elimination; Machin's formula; and standard digit
convolution/carry recovery. Fürer, arXiv:1402.1811, already establishes a linear
logarithmic-word RAM multiplication baseline. None is presented as our discovery.

The rational native provider comes from artuskg's PR #956 at
fa4df77c9dfdbac93368d95dcb361e69b3b65464. Retain its credit to Dugongue's PR #390,
its retained contributors, Jacob Sussman's bridge/frame/banking/RAM/Fourier work
and P193 supplier; PRs #363/#373/#375, #377/#381, #397, #401 and #430; and
OpenAI/math's preceding exact-width, sector, CRT/chirp and root-order sources.
PR #647 (artuskg) is a separate exact-scalar construction and remains credited.
The finite-word lowering here does not assert its unproved cyclic conditioning.

Comparison only: hexapode's pending PR #4535, and the selected PR #4359 lineage.
Their exact heads and scope are in OVERLAP.md. Dugongue's PRs #4538/#4541 supplied
previous Word RAM compiler/transfer packages; this package does not call their
TM simulator. Existing public attribution and source notices remain authoritative.

Inspected Problem 1.8 limb/inversion proofs, Gaussian expansion notes and a MUB6
Machin/rounding note are listed by source hash in RECOVERY-PRECEDENTS.json.
Those are source-inspection precedents, not a new formal proof or novelty audit.
