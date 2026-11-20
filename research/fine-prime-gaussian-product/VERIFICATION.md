# Execution and proof coverage

The registered replay takes two binary strings through the emitted catalogue. Both full products start with the integer 741503 and the integer 466013. The width declared by the strings is part of the input. The second case has leading zeros and selects a different admitted geometry.

| Property | 20-bit entry | 145-bit entry |
| --- | ---: | ---: |
| Source sides | 5, 7 | 31, 29 |
| Padded sides | 8, 8 | 32, 32 |
| Digit / fractional bits | 8 / 128 | 4 / 96 |
| Complete dyadic restoration Γ | 9 | 12 |
| Generated catalogue, bits | 487,352 | 10,076,160 |
| Independent pre-carry coefficient checks | 35 | 899 |
| Nonzero coefficients, low to high | 11811, 10996, 4152, 868, 77 | 195, 166, 215, 164, 280, 164, 137, 46, 77 |
| Output integer | 345550037539 | 345550037539 |
| Output width | 40 bits | 290 bits |
| All-input rounding radius | <2⁻⁶³ | <0.000247 |
| Observed largest complex distance to the independently checked integer | <5.19 × 10⁻²² | <2.26 × 10⁻⁹ |
| Head movement recorded on the numerical tapes | 759,467,396 bits | 47,737,571,880 bits |
| Signed word products, including the final residual check | 74,655 | 2,673,183 |
| Numerical payload bits still live at return | 0 | 0 |

The squared complex residuals use integer numerators on the actual recovery grid. The verifier independently constructs every true coefficient from the input digit streams after the product returns. The pointwise, ring and sparse operations use the production word interface. Both complete runs stay below the fixed short-word threshold and take the bounded Walsh branch. The numbers in the movement row are instrumented model events. All other program costs including setup, cross-stage serialization and nested scalar execution are charged in the proof. These counters do not report elapsed time or resident memory. [Public entry](product.py) · [Original regression](verify_product.py) · [Interior regression](verify_interior.py)

The verifier also exercises zero, leading zeros, unequal lengths, long carries, the maximal pair at 144 bits, and the finite elementary branch. On the first source and target geometry the unchanged dense Gaussian oracle uses its own admitted α=6, 128 fractional bits and 320 enclosure bits. Its 36 line executions agree on the product and all 35 coefficients. The historical p48 diagnostic packet is rejected. The old physical caller and its production gate are preserved. [Dense implementation](../certified-gaussian-recovery/gaussian.py) · [Historical admission](../physical-tensor-crt-sandwich-recovery/sandwich.py)

## Independent checks of the construction

| Check | What was compared |
| --- | --- |
| Original coordinates and CRT | Direct group destinations on seven shapes with 947 source columns in total. Sixty-four signed permutations, 4,080 phase signs and 766 dirty Gaussian holes distinguish the suffix convention, ordinary padding and genuine original-coordinate extraction. [Verifier](verify_routes.py) |
| Coefficients and band solve | Outward interval comparisons on every padded pair for 31/32 and 61/64 axes, including reversed-kernel controls. Nineteen cyclic and bordered systems use an independent rational matrix inverse and 5,640 signed word products. [Pure blocks](verify_blocks.py) · [Border solve](verify_solve.py) |
| Middle | Byte agreement with the published eight-point cached-chirp example. Eight complete Fourier comparisons cover both signs with independent interval roots on four tensors. There are 372 additional root-enclosure checks. [Verifier](verify_middle.py) |
| Native butterflies | Four full recursive runs on checked words, including a three-output word, interleaved supports, and zero-padded productive rows. A rank-13 literal branch returned every Walsh coefficient. An exact global-phase mutant that agrees at one column is rejected. [Verifier](verify_c_word.py) |
| Ordinary and sparse movement | Exceptional-key repair and complete dirty spectators include 6,144 records, 16 ordinary transitions and 2,688 repairs in one fixture. Nested C runs produce outer-row counts 1, 2 and 6. A third dirty reservoir and a literal tail both execute. [Verifier](verify_shears.py) |
| Scalar primitive | Twenty-six signed cases through 8,192 bits. A separate 17-bit signed call crosses the retained engine's FFT threshold on its real word tapes. [Verifier](verify_words.py) |
| Compact436 and physical dispatch | Fresh producer, 28,138 canonical requests, 2,701 charts, 540 split bases, 81 erase conditions, 197,892 chronological event checks over the nine stage types, and the full 900,416-call paid profile. The source-Q worker compiled a late owner and residual and round-tripped a 359,399-bit continuation. On a reduced grammar 483 instructions matched the old materialized word. Two fitted physical roots operated on all 1,024 independent columns. A second call reused the worker on 192 columns with nonunit spectators. [Source and price check](verify_ordinary.py) · [Physical control check](verify_compact_control.py) |

The registered outer check sends 1,024 and 4,096 independent columns through both physical roots. It verifies the optional remainder and mandatory high field with the old digit primitive disabled. At the actual source prime the same truncated high-field input uses all 512 scratch roles on the old primitive and reaches the first missing input bit with nine roles on the new one. On a complete 23-by-23 exchange with a two-way spectator, all 1,058 columns return using 13 roles. A separate public-selector test reaches a proper one-digit remainder at atom width two. [Outer regression and negative control](verify_compact_outer.py)

The first optional check below enters the selected large-prime physical node with its genuine compatible row count and rejects the first missing payload bit. The last check also runs an odd-sized body through both reduced physical roots. The complete selected orbit and eventual funded finite C word were not materialized. Source algebra, payment for all stopped children, stock and all-size scalar arithmetic enter the complete-rate statement. Independent model-assisted adversarial reviews and code-disjoint finite oracles supply error checks. Human scientific acceptance and proof-kernel verification remain open. [Complete proof](PROOF.md)

```sh
python3.12 -I -B research/fine-prime-gaussian-product/compact_source.py /tmp/compact436-gaussian-source.gz
python3.12 -I -O -B research/fine-prime-gaussian-product/verify_compact_control.py --source /tmp/compact436-gaussian-source.gz --truncated-ingress
python3.12 -I -O -B research/fine-prime-gaussian-product/verify_compact_outer.py --odd-body
```
