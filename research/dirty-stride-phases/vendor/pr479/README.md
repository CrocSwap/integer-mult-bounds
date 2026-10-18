# Streamed chirp phases

The retained chirp generator computes one exponential per coefficient, but
charges d index calculations at full p-bit width. The indices have only
ell-bit width, with d*ell=O(p). Accounting for those widths removes a factor
d. The accompanying additive generator independently obtains the exact same
phase residues with fewer than 2T axis-record visits over a T-entry stream.

The chirp/scalar row becomes `O(T*p^(1+delta))`, with normalized saving
`1-delta` rather than `1-epsilon-delta`. The scalar exponential, phase sign,
denominator, disk-grid error, pointwise products and tensor order are retained.
Polynomial-ring products are separate and unchanged.

**No new kappa is claimed.** The Gaussian margin is no larger than the old
scalar margin, so the current overall minimum is unchanged. This follows
#475's removal of two FFT costs by removing a further independent scalar cost.

Run with Python 3.11+ and the standard library:

```sh
python -B research/streamed-chirp-phases/verify.py /absolute/new/output
```

Finite controls cover 319 complete streams and 587,020 phase entries;
191,592 exact chirp/Fourier coefficient identities; 60 bounded distant-state
probes with control words up to 522 bits; exact complete-period restoration;
adjacent-record traversal counts; narrow arithmetic widths; six mutations;
and the unchanged outer minimum. Distant probes do not claim execution of
their enormous prefixes.

The verifier does not execute the retained high-precision exponential or a
full multiplication machine. It proves equality of the integer arguments
passed to that unchanged routine. The all-size fixed-tape bound is the
written transfer in [PROOF.md](PROOF.md), not a Python runtime measurement.

SOURCE.json pins the manuscript and inherited arithmetic. Original files
are unchanged. New implementation and accounting by chafreaky with OpenAI
Codex assistance. The chirp formula and scalar interfaces belong to the
source authors; no literature priority for elementary finite differences is
claimed. Apache-2.0.
