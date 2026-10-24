# Independent final native-assembly and record-product review

Prepared for Dugongue with substantial OpenAI Codex assistance. This review is independent within the four-worker AI team; it is not external human review or a kernel audit.

Reviewed assembly/NATIVE-ASSEMBLY.md at SHA-256 187fcf18a8177976ef238e97ff69ee2a2c81a9148b21147c1083ccc13288438c and record_product.py at SHA-256 6967feb00fbcb13640504f26c5e20bcea249e1dc89c41713aa8e8f161def873e. Read the actual native_convolution.py path and its root-seed call. The retained analytical sources and their exact-byte bindings were separately reviewed in FUSED-NATIVE-REVIEW.md. Later prose clarifications should be rehashed by the integrator.

No new substantive mathematical defect was found in the stated source-bound conditional assembly. This conclusion retains the explicitly identified all-input finite supplier, analytic reduction, tensor-compiler identities, fine-prime and exact-recovery source premises. It does not independently replay or establish the enormous finite supplier or a complete asymptotic native execution.

The native provider gap is strict: q = 0.00302016555 < q_C = 0.0030201656, and q_C is below the source critical saving. The chosen ε gives εq = 0.0030201655197983445 > κ = 0.0030201655. The Gaussian row is the actual fused g-axis circuit cost T d g^(-q), not the scalar T d fallback. The capped boundary uses explicit Strassen and charges both couplings and periodic closure. The fine-prime wider offline precision is paid with polynomial-size multi-limb setup; it is not mislabeled one-word arithmetic.

Native per-visit metadata is justified by sublinear-bit group keys and explicit n^o(1) tables, with word-level Benes extraction or mixed-radix/indexed gathering. Sparse-axis enumeration visits the sum of individual slab volumes, not every axis on every record of their union. These are actual random-access recipes and import no TM algorithm or tariff.

The routing rows require the following accounting interpretation: call-specific gather/restore and phase normalizers are already inside the main/fused call bills; group-specific extra passes are in the group-scan bill. Only a fixed number of additional global passes have standalone saving 1. There must not be an additional uncharged full-array scan per axis. The source assembly's intended interpretation was confirmed with the root worker.

For batched inverse stability, the right-hand-side size is the maximum infinity norm of INDIVIDUAL columns, equivalently entrywise maximum. It is never the induced row-sum norm across all R columns; R can be enormous and must not enter the precision guard. The owned BATCHED-INVERSE.md now states this explicitly. Fine-prime conditioning is polynomial in p; old special-case constants such as 8p are not asserted for the capped fine-prime matrix.

## Actual record-product check

For a record of length r = 2^j and signed Gaussian-integer components smaller than 2^p, each input complex modulus is below β = 2^(p+1). The code pads to N = 2r, uses F = 16p+16 bitlength(r)+64 fractional bits and S = 2^F, computes the two forward transforms and one inverse, and retains the 2r−1 linear-convolution coefficients. Its guarded fixed-point operations are those of native_convolution.py.

The prior FFT estimate bounds coefficient error by 216 N^6 β²/S. With bitlength(r) = j+1,

    216 N^6 β²/S
    ≤ 216 * 2^(6j+6+2p+2−16p−16j−16−64)
    = 216 * 2^(-14p−10j−72)
    < 1/4.

Thus rounding floor((x+S/2)/S) recovers the correct signed integer, including negative coordinates. The runtime separation check is an additional control; the mathematical bound supplies its sufficiency. Folding coefficient j+r with a minus sign implements reduction modulo X^r+1; the nonexistent highest term at degree 2r−1 is correctly treated as zero. Real and imaginary components are both retained.

The supplied width 16(F+16)+20 covers the root seed's private precision P = 8(F+16) and raw-product requirement 2P+20 exactly. FFT data/products need much less: F and log r are O(global p), so the declared sufficiently large fixed common word coefficient covers them. It is essential that the outer proof uses GLOBAL p-sized words, not a fresh local log(record bitlength)-sized machine.

Each product performs O(r log r) native operations after the root table has been prepared and paid. Root preparation is shared or counted in the explicit sublinear setup. The code recomputes each input kernel transform, correctly charging it to that product. Full-variable-input multiplication appears only in the independent schoolbook reference oracle, not the algorithm.

## Remaining scope

The final result should remain described as source-bound conditional native Word RAM multiplication, with no new TM exponent, no independently formalized full theorem, no practical-speed assertion and no claim of worldwide novelty. Preserve the predecessor credits already listed in NATIVE-ASSEMBLY.md and the complete source notices. A minor setup wording should allow polynomial(s_i,p), not merely polynomial(p), whenever full-axis exact rational preparations are discussed; both are n^o(1) in the stated regime.

Independent executable replay: python -I -O -B record_product.py passed 36 signed complex record products and 378 ring coefficients, with maximum raw magnitude width 51,965 bits under each explicitly computed word cap, and the overflow rejection control passed. TM_calls = 0. This is finite operational-model evidence, separate from the universal source-bound proof.
