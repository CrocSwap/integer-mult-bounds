# Independent review: endpoint-bounded C-leaf width

Target: /workspace/scratch/92c9920affc2/root-work/endpoint-width/PROOF-CANDIDATE.md

Target SHA-256: 964bd6d2251f839998713337352affb224749b110830172dac0eb7bdbf969a05.

## Decision

**Mathematical pass** for the two-endpoint bound, the all-cut sharp witness, and the w+2k component-width claim at the fixed common scale 2^k, assuming the stated #7468 integrality premise. I found no counterexample to those three claims.

This is an independent proof review with exact small-matrix corroboration, not a review of the credited scale theorem or of the physical wrapper. The w+2k result bounds scaled prefix components only; it does not bound literal kernel numerators, temporary accumulators, or the cost of scaling/unscaling.

## Proof checks

Write C_j=C^(tensor j). Every complex entry of C_j has magnitude 2^(-j/2). For even j, each entry is real or purely imaginary, so each real (and imaginary) output component has one coefficient of magnitude 2^(-j/2) per address. The component-row absolute sum is

    2^j * 2^(-j/2) = 2^(j/2).

For odd j, both the real and imaginary parts of each entry have magnitude 2^(-(j+1)/2). Each input address contributes two real components to an output component, giving row sum

    2^(j+1) * 2^(-(j+1)/2) = 2^((j+1)/2).

The inverse tensor has the same absolute row sums. Thus its exact induced component-infinity norm is 2^ceil(j/2).

For a cut S, C_S x is bounded first by applying this norm to x. Since F=C_S C_(S-complement) and the factors commute,

    C_S x = C_(S-complement)^(-1) F x.

Applying the inverse norm to the second endpoint gives the second bound. Taking the minimum is exactly 2^ceil(min(|S|, f-|S|)/2) M.

For sharpness, put d=min(|S|,f-|S|) active axes on each side of the cut. Let u=(1,1), which obeys Cu=C^(-1)u=u, and let z be 2^ceil(d/2) times the zero-address impulse on the 2d active axes, tensored with u on the remaining axes. Set x=C_S^(-1)z and y=C_(S-complement)z. Then Fx=y and C_Sx=z. On the d transformed active axes, each nonzero coefficient is a Gaussian unit times 2^(-d/2) for even d, or has real and imaginary parts of magnitude 2^(-(d+1)/2) for odd d. The chosen impulse scale makes x and y Gaussian integral with component norm one, while z has component norm 2^ceil(d/2). This works for every cut; d=0 is the invariant all-ones case.

Let r=floor(f/2) and k=ceil(r/2)=floor((f+2)/4). For every cut, ceil(d/2)<=k, so the scaled prefix has component magnitude at most 2^(2k)M. The credited premise says these scaled components are integers. At M=2^(w-1)-1,

    2^(2k) M = 2^(w+2k-1) - 2^(2k) <= 2^(w+2k-1)-1,

which fits the stated symmetric signed w+2k range. For a middle cut, the witness above, multiplied by M, attains the positive value 2^(2k)M at the impulse component after scaling. The positive maximum of a symmetric signed w+2k-1-bit field is 2^(w+2k-2)-1; the witness exceeds it by

    2^(2k)(2^(w-2)-1)+1 > 0

for every w>=2. Thus the width is sufficient and uniformly minimal **at the fixed common scale 2^k**. This does not establish that the common scale itself is minimal.

## Independent corroboration

independent_check.py uses a separate exact rational matrix/tensor implementation and imports no author code. It applies the 2-by-2 factor pairwise along axes, so it shares the candidate’s tensor-axis factorization.

    PASS_ENDPOINT_WIDTH_REVIEW norm_matrices=63 cut_witnesses=255 width_witnesses=32 controls=3
    ceil_to_floor_exponent_mutant_rejected=True
    wrong_inverse_direction_mutant_rejected=True
    one_fewer_signed_bit_mutant_rejected=True

The exact matrix checks cover every subset for f<=5; the all-cut witnesses cover every subset for f<=7; width witnesses cover f<=7 and w=2..5. The finite range corroborates, but does not replace, the algebraic proof above.

## Physical-application boundary

The final sentence about MOVE factors is valid for factors applied outside the cut, or for a proved factorization that leaves only a monomial isometry between the cut transform and complementary transform: such an isometry preserves the component norm and Gaussian integrality. The proof as written establishes the endpoint lemma for the bare F=C^(tensor f). If the literal leaf interleaves MOVE factors among individual C-axis operations, the wrapper proof must state how those factors are regrouped or prove the corresponding cut factorization; norm preservation by itself does not identify the actual intermediate prefix with C_Sx.
