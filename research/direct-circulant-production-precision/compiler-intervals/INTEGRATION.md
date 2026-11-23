# Relative intervals after the published complete-gate result

The remote base `e040fedfd8fcc51480d2468f3fa07562c8bacbf0` preserves the complete-gate result first published at `0a1c14499407b103ae964f36551b0e9c11400197`. It contains
the accepted complete-gate source theorem under `../compiler-cuts/`.
That entire subtree is retained byte-for-byte. Its proof hash is
`162dd4bb7a020dfb72dd3c80cb9a1de37212cc7f812f36fd4365d487d49b341b`.

This directory contains a separately frozen recovery proof and review,
relocated by directory name only. Its proof hash is
`e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07`.
Result A overlaps the already published complete-gate extension and is
corroborating source context. The additional mathematical claim is Result B:
for nested completed downsets, one common legal linearization cancels the
shared normalized perturbation prefix, giving interval and exact inverse cap
`B^2*H^2/(1-theta)<2*B^2*H^2` instead of the conservative `K_Full^2`.
The later spectral-downset consumer explicitly uses this proof and review.

Both source constants must satisfy `lambda>=1` and `Q>=1` individually,
as already stated in this frozen proof. Stored inverses, whole-gate cuts,
source conditioning, rank, phase and per-atom coefficient errors retain
their existing meaning. No physical intermediate-output or scratch-state
claim is added.

Nick Petalas's #5940 (`b709a6adb6a9543247260900b108166a4d469f6f`) already
supplies sharp conditioned matching interpolation and unitary no-loss.
Armin Pourshafeie / apoursh's #5240
(`6d0a6043120880c696d0850e9242a16e6fb980a5`) already supplies the rounded
event/component-width discussion and singular coordinate-write swap control.
Those results and controls are credited precedents, not new claims here.
Brian/JoyboyBrian's #4755/#4976/#4977 and Nick Petalas's #4852 retain the
distinct attribution recorded in the proof and origin manifest.

The unchanged `PROOF.md`, `README.md`, author evidence and independent
review retain their historical wording for byte identity. This integration
note supplies the publication chronology and overlap clarification. The
parent replay now runs the added checks in isolated copies and retains all
existing verification methods and published receipts.

For the remaining implementation boundary, the canonical
`research/integer-rounded-gate` package already supplies Nick Petalas's
once-rounded supplied-coefficient arithmetic construction with
`W=B+4C+2`. Its pinned README is retained as provenance in the parent source
manifest. We do not import or re-audit that proof here. What remains is the
exact caller binding and complete live-word, coefficient-delivery, cleanup,
instruction and tape-cost accounting, not construction of that local kernel.
