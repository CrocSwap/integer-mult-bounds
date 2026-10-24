# FFT word verification scope

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I ran the seven suites below on Darwin arm64 with Python 3.12.13. I use
exact Python integers only in separate checking models. During physical
execution I disable payload decoding and retain the encoded tape
operations, fixed pools and protected-output protocol. I record final
committed-export and hosted receipts in the public PR and Discussion3664.

| Suite | Author checks |
|---|---|
| `sources` | Complete corrected PR3709 export, 26 retained files, one shared physical type cohort, actual RingProduct/Karatsuba child identities, two Gaussian source hashes, changed-archive and duplicate-runtime rejection. |
| `budget` | 8,190 finite geometry cases, strict coefficient headroom, no wrap, linear packet volume, full setup charges and exact arithmetic-power comparison. PROOF.md supplies the universal argument. |
| `plan` | 13 encoded geometries from width 2 through `2^257+7`; exact fields, preserved width port, rejection of widths 0 and 1. These are metadata-only cases. |
| `base` | 18 complete products at widths 1, 2, 3, 8, 15 and 16: zero, one and maximum operands, on one owner. |
| `codec` | 10 complete packing/carry cases through 1,024 bits, including partial digits and canonical-short zero/one inputs. I supply the normalized-product boundary with an independent integer convolution fixture. |
| `failures` | 13 malformed-input, output and allocation controls, followed by a positive packet on the same owner. |
| `fft` | Actual default FFT call at width 17, base call at 16, then the retained signed Arithmetic consumer at width 19 on the same word owner. |

## Complete FFT sequence

For width 17 I multiply `(2^17-1)*(2^17-33)`. I compare all 34 returned
bits with the exact integer product, preserve all three borrowed ports,
inspect complete owned restoration and consume the protected result.
The physical ring arithmetic executes 896 word products and 11,648
Karatsuba nodes; the new owner's peak pool use is 27 roles. The raw
bit-byte SHA256 is:

```text
62e37795a75598907558cf9780e449d61e9d704b7efa07f470a4491332b832d8
```

I then multiply `65535*65533` through the base branch on the same owner.
The 32-bit raw return has SHA256:

```text
2a68f44e8a83fa88e55b83f6db4186448898a41e06f0af18c706269bc4049ea2
```

Finally, the retained `Arithmetic.multiply` caller multiplies signed
`-1` by `2^19-15`, declaring width 19. This exercises canonical-short
input, negative sign handling, caller scope suspension, the actual
default FFT branch and complete raw-return consumption. The ring
executes another 896 word products. The caller's pool peaks at three
roles. The 38-bit magnitude representation has SHA256:

```text
ec30665633fa9c08dcbcf86d79f4049ffc76dcaf2699be106cdf6a7a2c7fad91
```

I use no reduced test cutoff or FFT-result substitution in this suite.
The ring's internal word owner remains the original Karatsuba engine.

## Separate codec and rejection coverage

The codec suite uses widths 2, 3, 5, 17, 21, 65, 257 and 1,024 with
maximum-times-near-maximum inputs, plus canonical-short one and zero
cases at widths 65 and 257. I execute physical packing and carrying,
using a separate integer convolution at the ring-return boundary.
For the 1,024-bit case the 2,048-bit result has SHA256:

```text
9b953c0abf693e0525b98a66ad337c93217d4eb7845fc6a1a2d91fc7f0d5dead
```

I reject zero width, each oversized operand, unconsumed protected output,
and dynamic physical-tape allocation during a completed macro. At the
unpack boundary I reject a nonzero imaginary component, a negative real
coefficient, excess coefficient headroom, a nonzero dummy record,
short/extra returns, a shortened output extent and nonzero final carry.
Those malformed-return fixtures check the carry consumer without
claiming another complete FFT execution.

The positive width-7 call after owner rejection tests returns SHA256
`6ef12bc0bf346df6d3fb05ce169e60013adc3ca15d1692a7c724e7f0f1f3fd5d`.
I require explicit exceptions, preserve borrowed values and inspect
scratch cleanup. The source suite also rejects a changed archive digest
and a second runtime cohort.

## Proof and remaining obligations

I prove the exact-grid identity, no-wrap condition, carry invariant,
time and space bounds in PROOF.md. The finite budget suite checks the
same inequalities over widths 3 through 8,192 and authenticates the
inherited Fourier-power calculation. It records the Gaussian arithmetic
power `9981/10000`, Fourier power `99827619697/100000000000`, and positive
gap `17619697/100000000000`.

I retain PR3709's numerical precision/recovery premises. I have not
executed a large production FFT word, implemented the Gaussian caller,
or completed the CRT/integer theorem. A reviewer must assess the
all-size proof and inherited premises apart from these finite author
checks. I leave the selected frontier unchanged.
