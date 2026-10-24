# Independent final arithmetic review

Reviewed the package at `root/repo/research/native-word-fft` without editing its sources. The reviewer owns only this arithmetic review. No correctness defect was found in the inspected Gaussian block, actual Gaussian coefficient, periodic Woodbury, or rounded diagonal-dominance arguments, under their stated precision, near-identity and common-word-width hypotheses.

## Concrete checks and mathematical scope

A fresh optimized-mode replay of `gaussian_block.py` passed 12 blocks and 45 outputs at absolute tolerance 2^-60. The executed family is a=1/16, u=v=1, q in {1,2,4,8}, and integer shifts c in {-1,0,1}; the universal block decomposition is a separate mathematical result. The reversed source and convolution index x+q-1 implement the diagonal-Hankel-diagonal identity correctly. With transform length 4q, source length q and kernel length 2q-1, there is no cyclic aliasing. General Convolver callers must themselves supply a prepared transform of the same length and sufficient zero padding; the Gaussian caller does so.

A fresh replay of `gaussian_inverse.py` passed the 3 systems (s,t)=(13,14),(17,19),(25,27), alpha=2, h=4, over 55 output rows at tolerance 2^-100. The maximum finite-reference residual was approximately 4.604745e-51. Its reference sums only periodic copies -3 through 3 using Decimal; this is finite validation, not an independent proof about the infinite sum.

The actual coefficient numerator is correct: shifted=t(i+d)-s*q_i represents s*(r*d+beta_i), while beta[(i+d) mod s] supplies the periodic column label. Keeping i+d unwrapped in shifted and wrapping only the label is necessary and is implemented. Machin pi uses table.S=2^P; querying the resulting argument with fraction_bits=P has the correct scale. Negative exponential cutoff is explicit. Its omitted error must be charged separately, at most (2h+1)*exp(-C*ell) per row in this finite-band implementation; the fixed test parameters have ample margin. Arbitrary caller precision choices must enforce this budget, as well as the infinite Gaussian tail and pi/exponent-formation errors.

The periodic reduction uses literal A=A0+UV with V selecting the first and last h columns. Stored X=A0^-1 U and S=I+VX have the correct scales; the correction Xz is divided by 2^p once. Boundary columns are distinct when s>2h. All 2h ordinary band solves, the dense small factorization and final correction are present. The executable contract is real coefficients with ||A-I||_infinity<=1/8, narrower than the universal proof's complex 1/4 interface. In particular, its exact small Schur matrix differs from I by at most 1/7, leaving room for the real BandSystem's 1/4 acceptance check when the advertised guard precision is used.

## Universal rounded band proof

The exact row diagonal-dominance margin does not decrease under Schur elimination; its active row sum does not increase. Rounded updates perturb each active row in at most h elimination steps with at most 2(h+1) entries per step. The stated 6(h+1)^2*u allowance closes the row-sum/pivot induction. Expanding the actually stored factor updates gives a local residual bound without multiplying successive errors exponentially. The removed pivot-column residual includes multiplier rounding times its pivot. The h=0 case is directly diagonal; for h>=1 the displayed residual constant dominates (H+2)(2H+1).

The factor norm identities then bound both triangular inverses. Leading-prefix forward bounds follow from principal factor pairs. Backward suffix inverse bounds also follow by taking the corresponding principal submatrix of the full upper-triangular inverse. Exact fixed-point dot accumulation followed by one coordinate rounding gives the displayed solve residual equations and conservative final error constant. A fixed number of logarithmic-width limbs covers products, complex division and dot accumulation when the specified integral and fractional guards are allocated.

For the actual periodic Gaussian, the tail inequality follows from |r*d+beta_i|>=|d|-1/2 and |beta_j|<=1/2. The wraparound Woodbury reduction and its constant inverse-norm bounds are valid under the credited source estimate ||N-I||<=1/8 and sufficiently small coefficient/rounding error. Dense small-s handling and the complex extension are proof-level branches, not executed features of these real examples.

## Model and attribution limits

Production code obtains roots through the finite Machin/Taylor implementation and exponentials through the paid finite table. Decimal and Fraction are check-only references. Inspected arithmetic products are bounded-coordinate, bounded-parameter or bounded-index products checked against an explicit word limit; there is no unit-cost multiplication of the entire input integer. Python remains an executable bounded-word model rather than an emitted register-machine program, and its operation counters are accounting instruments rather than a formally verified compiler cost certificate. Global caller blocking, requested error budgets and a common word width remain explicit assembly hypotheses.

This review establishes no new global multiplication bound, no numerical kappa improvement and no novelty priority. Classical FFT, diagonal dominance and Woodbury arguments, upstream Gaussian resampling and its cited Harvey-Hoeven work retain their predecessor credit. Source identities and localization/contraction results must remain pinned and credited in the integrated proof.

## Reviewed SHA-256 values

- native_convolution.py: A62A4CB5A1DA458E31C90EA881A1146B59E9FD7CCBF317C1C9836C19BC7FA2C6
- gaussian_block.py: EB967DDE22E1989EF68057F7644BFF9519C0426137054E2517766FDDEE9D24DF
- gaussian_inverse.py: 08616D26652C7C656ED8928A2C47A0A150A8CFB35BCC7F121CE5A729908E4A35
- periodic_solve.py: D3940B0D48BA4BBF81A0F2D05BDAC29E3B998AD746771DCF01B03CAC03680393
- band_solve.py: F4E4471679CC89BBB01AB0B26E807B0DACDC6188AB95BA924FC57243369407BB
- NATIVE-BANDED-INVERSE.md: 1259B4242EBF6AC7F14BFE72E371AFB8DC530B2755D1FD82228D9DC6F01634BA
- exp_table.py: E617B40D499F423A7861B4483BDACDB7DB28232FADF7468EFE871ADAE557FA35
