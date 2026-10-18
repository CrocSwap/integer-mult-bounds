# Certified Gaussian resampling through exact integer recovery

This implements the actual Gaussian numerical path left unexecuted in
[PR2298](https://github.com/CrocSwap/integer-mult-bounds/pull/2298): periodic
Gaussian sums, nearest-coordinate selection, inverse correction, retained
permutations, forward/opposite transforms, pointwise multiplication, CRT,
integer decoding and carries. It answers that proposal's request for an
independent numerical implementation with rigorous enclosures.

The supplied certificate covers **every pair of nonnegative integers up to
14,592 bits**, with a uniform coefficient recovery error **below 2^-49**.
It uses the source box `5 x 7 x 13`, target lengths `8,16,32`, `alpha=5`,
256-bit numerical precision and 448-bit outward dyadic enclosures. The
certificate bounds the complete operators, so this claim does not depend
on exhaustive testing of the inputs. [PROOF.md](PROOF.md) supplies the
arithmetic, infinite-tail, inverse, rounding and full decoding arguments.

The output is produced through the Gaussian path. Direct odd-order Fourier
matrices certify its operators; schoolbook convolution and Python's full
integer product occur only as independent checks after the output exists.
The multiplier's recovery step requires a unique integer in each certified
enclosure before it propagates carries.

## Evidence and scope

[RESULT.json](RESULT.json) records 243 complete operator entries, 30 rounded
complex-vector checks and 289 full integer products, including maximal
14,592-bit inputs. These runs execute 10,548 Gaussian line calls and check
all 9,155 recovered coefficients independently. Controls detect incorrect
permutations/selectors, normalization, a required inverse correction,
omitted periodic windings, insufficient precision and invalid domains.
All acceptance arithmetic is integer or rational; no floating-point
agreement or unchecked transcendental oracle is used.

This is a dense reference implementation and a finite uniform correctness
certificate. It uses a conventional FFT and indexed arrays. It does not
execute the selected recursive suppliers, implement the fast Gaussian
chirp/tape algorithms, or establish their asymptotic cost. The small valid
Gaussian boxes are not the eventual outer parameter regime. **No new
kappa, selected-frontier change or all-size faster multiplication theorem
is claimed.** The artifact makes a central numerical interface executable
and independently testable; it leaves the fast implementations for review
and replacement against this oracle.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/certified-gaussian-recovery
```

The registered normal and optimized replays each end with:

```text
PASS_CERTIFIED_GAUSSIAN_RECOVERY products=289 input_bits_max=14592 uniform_error<2^-49 RECEIPT_MATCH
```

To compute an individual product through the Gaussian path:

```sh
python3 -I -B research/certified-gaussian-recovery/multiply.py 0x12345678 0x9abcdef0 --input-bits 32
```

Expected product: `0xb00ea4e242d2080`, with exactly 64 output bits. A full
source/certificate replay is separate from this command. The direct replay
is `python3 -I -B research/certified-gaussian-recovery/verify.py`; `--emit`
prints a fresh receipt without writing files. Source bytes are authenticated
before imports, and the generic package runner also checks Git provenance.

## Open next questions

1. Replace the dense Gaussian backend with the proposed fast sequential
   routines. This oracle can check their entire line outputs, rounding and
   correction terms. The first step is one completed expansion/correction
   line with an explicit tape invoice; its implementation and cost proof
   remain missing here.
2. Substitute a completed selected-layer backend for the conventional FFT.
   Compare complete rounded rounds against this implementation, including
   the retained order and normalization. The selected suppliers and their
   physical all-size proofs still require independent review.
3. Independently review or formalize the interval and uniform decoding
   proof. Start with [PROOF.md](PROOF.md) sections 3–6, especially the
   infinite tails, inverse-tail factor and the all-input rounding bounds.
   The current result has no independent human or formal-kernel review.

## Credit

Prepared by **Mason Hale**, with substantial **OpenAI Codex assistance** in
mathematics, code, verification and writing. [NOTICE.md](NOTICE.md) retains
the Gaussian and repository lineage. New material is Apache-2.0.
Coordination: [Discussion2291 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2291#discussioncomment-18940593).
