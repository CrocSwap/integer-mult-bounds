# Proof of the clean rational-witness contract

Let each source be a signed w-bit integer and let N=sum a_i*x_i, D>0. Define B=sum|a_i|*2^(w-1), O=D*ceil(B/D), and n=max(w,bit_length(2B+D)+1).

## Exact numerator and division
For every source bitstring, |N|<=B, so 0<=N+O<=2B+D-1<2^n. Sign extension and modular n-bit addition/multiplication/subtraction therefore compute the exact nonnegative N+O. Negative coefficients use subtraction of the magnitude term.

The unsigned division loop maintains a remainder r in [0,D). Reading the next numerator bit b gives 2r+b<2D. Subtract D exactly when that value is at least D; the resulting remainder is again in [0,D). Induction gives quotient floor((N+O)/D) and remainder N mod D. Subtracting the integer O/D yields q=floor(N/D). The bound on n ensures the signed q fits in n bits.

## Validity and exact acceptance
The diagnostic is the OR of (i) nonzero remainder bits and (ii) upper q bits that disagree with the sign bit of its lowest w bits. Thus it is zero exactly when D divides N and q is a signed w-bit integer.

The target output is its input bitstring XOR the lowest w quotient bits. For signed w-bit target t, target output AND diagnostic both zero (meaning each output is zero) iff N=D*t. Fractional results whose floor matches t and out-of-range quotients that wrap to t cannot be accepted. A target mismatch remains a bitwise mismatch, not an arithmetic residual.

## Reversible realization and scratch cleanup
Each Boolean intermediate is written into a new zero bit through X, CNOT and Toffoli gates. Their controls and targets are distinct for Toffoli; duplicated AND controls use CNOT. Every gate is an involution. After computing the quotient and diagnostic, copy them by CNOT into the separate target and initially-zero diagnostic output. Reverse every internal gate in reverse order. Sources are unchanged and all internal ancillas return to zero for every input, independently of validity. Output wires are not uncomputed or discarded.

This gives a total reversible transformation. On the exact-relation domain its target/diagnostic outputs are zero and can be considered clean in this gate model. On any other domain the nonzero mismatch or diagnostic must be retained. The implementation does not authorize physical retirement of unknown outputs.

## Applying to chart-aware witnesses
A fixed rational Gaussian chart map becomes a rational matrix on real and imaginary limbs. Every output row can be written as sum a_i*x_i/D using a common positive denominator, so the construction applies row by row. Donor sources must be live, immutable during reconstruction and different from the target. A complete call additionally requires the actual physical chart convention, all rows, permitted input domain, scratch allocation and cost schedule. This package supplies neither the whole project matrix nor a physical tape compiler.

An ideal row identity R_t L_t=0 alone is insufficient after rounding: for actual state L_t*z+e_t the residual is R_t*e_t. Exact-prefix invariants or an error-kernel proof are still necessary to claim every project CLEAR is clean. Fresh helper payload is not zero-initialized scratch.

## Cost statement
Gate counts in RESULT.json are exact counts for the generated X/CNOT/Toffoli network. They are not project tape actions, optimized physical bounds, or evidence of a kappa reduction. The baseline retains intermediate Boolean bits until inverse execution; arithmetic word width is not total scratch space.

The compute-copy-uncompute method and Boolean arithmetic are standard constructions; no novelty of those general principles is claimed.

## Version 2 public example binding
The portable verifier now reconstructs the published #7669 word and evaluates all 512 complex basis columns of its chart 359-to353 map for selected real output0 at event 88937. It reuses the unchanged published native interpreter, so this is source-bound replay of that coordinate, not an independent native implementation or complete project replay. The generic iff theorem is unchanged. The extreme-width tests are implementation regressions, not an exhaustive enumeration of1076-bit inputs.
