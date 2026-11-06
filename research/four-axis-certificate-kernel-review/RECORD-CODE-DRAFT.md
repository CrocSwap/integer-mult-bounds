# PR6574 finite-certificate to integer-map code review

Qualified written PASS, conditional on the original successful finite construction and complete certificate. I found no material gap in the reviewed implication from those predicates to the all-integer bijection, sum and error statements, or in their association with the actual forward/inverse kernel. This is not a fresh construction, matching, certificate check, fixture replay, new sharp constant, physical implementation or formal-kernel acceptance.

## Exposure and exact scope

Target is Nick Petalas's PR6574 at 48e312ff18d5b66b0969148f615fdf5ce0f92edd, research/four-axis-reversible-grid. I authored B13 session07 SCOUT-FOUR-AXIS.md and read the actual source proof, construction, kernel and verifier in that orientation. This role is source-aware, not source-proof-unexposed, blind, human or independently rediscovered mathematics. In this assignment I reread the exact local INPUTS copies of README.md, PROOF.md, construction.py.txt, kernel.py.txt and verify.py.txt. No current peer or coordinator draft was read before this note's first seal.

Core Git blobs are construction c80d588ef9ca33494ca78b8abd737e6e8722b4c4, kernel 883c1c317d2d4394f534e785a5d46b443549db9a, verifier c5057740a3fa15d8169669fdb8e984eb4e88be8f, proof fc3baa1e271cd89acabcb40248fb5e17dfdfac59 and README 93fad26d02f1a5c2691af1a3ad21639fcbe59b7a. Source files are text only here. No source or new scientific program was imported, executed or compiled; no quotient enumeration, correction generation, matching, certificate, fixture, fault, NumPy, native or proof kernel ran.

The source owns the codec, matching, finite counts, claimed 3,072-byte packing, sharp squared error eight and original fixture/control outcomes. Successful existence and certification of the actual complete table are inherited, not proved by reading an algorithm that may reject. This audit covers the finite-predicate-to-all-integer implication and code association only. It excludes new fourth-power, covariance, inward-norm, dirty-caller, numerical whole-caller and physical billing claims.

## 1. Complete quotient, not a finite-box extrapolation

Let W be the actual Walsh16 matrix, W_rs=(-1)^popcount(r&s), so W is symmetric and W^2=16I. Every integer z has class q=Wz mod4. Python's remainder with positive four gives the intended residues 0,1,2,3 even for negative and arbitrarily large integers.

For sign vectors, the identity ab=a+b−1 mod4 gives column_s = column_0 + sum_{j:bit_j(s)=1}(column_(2^j)−column_0) mod4. Each difference has order dividing two and column_0 has order four. Thus every class has a representative a(t,b) with a_0=t−sum b_j, a_(2^j)=b_j and other coordinates zero, where t is mod4 and b is a four-bit vector. Conversely row0 of W a recovers t, and row_(2^j) recovers t−2b_j, so these representations have distinct keys. This gives the whole quotient for all signed integers; it does not infer coverage from endpoint samples.

construction.quotient_keys starts at zero and repeatedly includes all four multiples of each actual Walsh column. Mathematically this is the complete column span modulo four. Its capacity guards and final size guard are conditional checks on that exact generation, not an existence proof when unrun. The actual code has no separate function named classify: classification occurs through quotient_keys, verify.representatives and the key computed in kernel.real_map.

verify.representatives independently writes the displayed representative formula and applies direct_walsh. Distinctness guards plus the formula provide complete quotient coverage. certify requires the forward and backward key sets to equal that complete set. The separate source methods therefore have a valid association, but neither was executed in this review.

## 2. Actual construction and decisive certificate predicates

The constructor's candidate subset has the required offset congruence: for odd keys, base entries −1/+1 at residues1/3 are negated triples without changing residues; for even keys, residues2 receive either +2 or −2 and residues0 receive zero. It filters both real weights of D_j=(-i)^popcount(j), obtains We divisible by four, maps each candidate edge to p=(We/4) mod4, and keeps a least-norm candidate for each reached edge. It makes no exhaustive closest-vector claim. The augmenting routine supplies a proposed complete matching; build_tables requires both all target assignments and distinct source assignments, then writes forward[q]=e and backward[p]=−We/4.

Correctness does not depend on search completeness, a proof that its matching must succeed or the chosen tie order. The actual certify checks the complete finite predicates after construction: exact complete key sets; each forward offset of length16 with genuine Python ints; e≡−q mod4; We divisible by four; pairwise distinct targets p; the backward offset at that target equal to −We/4; both offsets' squared norms at most64; both real components of the D-weighted sum zero; target surjectivity; and both zero-key offsets zero. Its maximum==64 guard associates the source's claimed attained real norm with its returned table, conditional on success.

The backward equality forces every stored inverse offset to be exactly the derived sixteen-integer tuple. Complete target surjectivity makes this cover all backward keys. Thus the proof needs neither an unverified lookup permutation array nor an assumption that a mere norm bound implies injectivity. build_tables' graph offsets can exceed a desired bound in principle; certify's explicit bound is indispensable rather than an automatic consequence of a successful arbitrary matching.

This path uses valid generated dictionaries and fixed integer tuples, not an advertised hostile table-packet API. For example, generic Python dictionary key equality does not distinguish bool from equal small integers, and real_map trusts offset length while zipping. Those are not gaps in the conditional theorem for these constructed/certified tables. They would require additional admission rules if arbitrary adversarial tables became an interface.

## 3. Both inverse directions on the complete lattice

Write e_q for the forward offset and A=W/4. Define R(z)=(Wz+e_q)/4 with q=Wz mod4. Offset congruence gives integrality. Because W e_q is divisible by four, the key of y=R(z) is

    W y mod4 = (4z + W e_q/4) mod4 = p(q).

The target permutation therefore determines q uniquely. Set f_(p(q))=−W e_q/4, exactly as the constructor and paired-inverse guard do. Then Rminus(y)=(Wy+f_(Wy mod4))/4 is the backward formula. Substitution for y=R(z) gives Rminus(R(z))=z, since A^2=I and f=−A e.

The reverse composition needs its own argument, rather than only a left inverse. For arbitrary integer y, its key p=Wy mod4 is in the complete quotient. Select the unique q with p(q)=p. Since f_p≡−p mod4, z=(Wy+f_p)/4 is integral. Also Wz=4y+Wf_p/4=4y−e_q, hence Wz mod4=−e_q mod4=q. Applying the forward rule therefore gives (Wz+e_q)/4=y. This proves both directions for every integer y, not only outputs of tested forward inputs.

For real norms, W/4 is orthogonal, so ||f_p||=||e_q||. The explicit certificate bounds make both errors at most8/4=2. Checking inverse offsets' norms separately is harmless extra evidence, not a substitute for this algebra. Divisions in real_map are exact quarter shifts guarded by divisibility; signed floor division is exact on those multiples, so no positive-only argument or floating arithmetic is hidden here.

## 4. Phases, global sign and actual adjoint order

Let D_j=(-i)^popcount(j). Entrywise,

    D_r W_rs D_s = i^(4−popcount(r xor s)).

This is the actual C^tensor4 entry for C=[[i,1],[1,i]]. Because (1+i)^4=−4, the ideal operator is U=−D W D/4, with the leading minus sign retained. Its adjoint is U*=−D^-1 W D^-1/4; symmetry/realness of W and unitary diagonal D justify this order. The ideal_numerator verifier independently uses the same Hamming-distance phase and leading minus; toggling inverse conjugates the phase, rather than removing that minus.

kernel.rotate maps (a,b) successively to z, iz, −z, −iz according to exponent mod4. Negative exponents are canonical modulo four. In block(forward), pre-rotation by −popcount is D, the two real_map calls use the forward table, and post-rotation of the negated pair by −popcount is −D. The returned map is exactly

    F(x)=−D R_C(Dx).

In block(inverse), the negated input is rotated by +popcount, giving −D^-1 y; both real parts use the backward table; post-rotation by +popcount gives D^-1. Its returned map is exactly

    Fminus(y)=D^-1 R_Cminus(−D^-1 y).

These formulas are mutual inverses because the middle real maps are mutual inverses and the diagonal/global factors cancel in reverse order. No ideal square, exact fourth power, involution or covariance identity of the rounded F is used. The inverse direction compares with U*, not with U or an independently rounded uncompute formula.

## 5. Weighted sum is a separate property from error and invertibility

Each real correction has squared norm at most64, so separate real and imaginary corrections in the complex map give total squared error at most(64+64)/16=8. Diagonal unit phases and a global sign preserve that norm. The same argument holds for the adjoint direction through f and D^-1. Norm bounds alone establish neither sum conservation nor injectivity.

For forward sum preservation the error is −D(e_real+i e_imag)/4. The two WEIGHTS vectors in construction and certify are exactly the real and imaginary parts of D, so the checked weighted equalities make its complex sum zero. U itself preserves the complex sum: C/(1+i) is unitary with row sum one, is symmetric, and so has column sum one; its tensor power has the same property. Hence F preserves the exact complex sum. Its bijective inverse then preserves that sum as well. Alternatively, for a real f, the checked D-weighted zero equality conjugates to the D^-1-weighted equality needed in the inverse formula. This keeps the weighted invariant separate from orthogonal norm preservation.

The zero-key offsets zero make both real maps fix zero, hence F and its inverse fix zero. No dependence on the finite endpoint fixtures is needed for these all-input deductions.

## 6. Sharpness association and integer API boundary

The source's witness x=(2+2i,0,...,0) has ideal forward column −D_j(1+i)/2, whose real and imaginary components are all half-integers. Any Gaussian integer output is at squared distance at least1/4 in each of32 real components, totaling8. Replacing D by D^-1 gives the same argument for U*. This hand implication associates the existing lower-bound witness with the actual phase convention; it does not freshly execute its fixture or invent a new error value. Together with the conditional certificate upper bound it supports the source's sharp theorem.

The mathematical formulas quantify over all Gaussian integers, using arbitrary precision and exact operations. Literal block validates exactly sixteen tuple/list pairs of genuine Python ints, rejects bool components, caps input component bit_length at4096 and requires inverse to have genuine Boolean type. It constructs new tuples and never writes input or table values. Its input cap is not asserted to be an invariant finite hardware state space: output is not capped, and the image of all valid4096-bit inputs need not be valid as the next invocation's input.

For the recommended at-most4090-bit components, put M=2^4090−1. Quarter Walsh sums have absolute component at most4M, and either real correction contributes at most2 because each offset coordinate has magnitude at most8. Thus every output component has magnitude at most4M+2<2^4092 and comfortably satisfies the4096-bit input guard for the inverse. The same estimate applies when beginning with the inverse. The literal API round trip is therefore justified on the stated headroom domain, not on every bounded-register state.

Minor source fixture-label precision: endpoint_checks' loop parameter bits=4090 constructs (1<<4090)±j. Some such components have bit_length4091, despite prose shorthand calling these4090-bit components. They still lie safely inside the API cap; this neither changes the all-integer proof nor invalidates the4090-bit headroom recommendation. Those source fixture outcomes remain unreplayed. This observation is not a mathematical failure or a new large-word experiment.

## 7. Written weakening controls — UNEXECUTED

1. Keep offset congruence/norm but remove complete-key coverage: a legal unrepresented lattice class can fail lookup, so finite fixtures alone cannot replace the quotient proof.
2. Keep bounded offsets but allow two forward classes the same target: output quotient no longer selects a unique inverse partner. Distinct and surjective target guards are decisive.
3. Store f under the original key instead of the target p(q), or omit its minus sign: the cancellation Rminus(R(z))=z is no longer the paired-inverse identity.
4. Keep the quotient permutation but violate e≡−q mod4: the forward output can be nonintegral; truncation cannot replace exact quarter division.
5. Keep congruence/permutation but remove the D-weighted sum checks: orthogonal error control alone does not establish exact complex-sum conservation.
6. Replace inverse pre/post phases by the forward phases, drop the global minus or compare with U rather than U*: a norm-only argument may miss the literal inverse/ideal association.
7. Extrapolate basis or large-word fixtures to all integer inputs without proving complete quotient coverage and both composition identities: such an extrapolation is unjustified.
8. Claim the4096-bit accepted set is a permutation domain. For example, in a hypothetical all-integer evaluation choose Dx=M times the all-ones vector with4096-bit M. Its zero-class Walsh image contains4M, which can exceed that input cap. Output validation of a subsequent call is a separate contract.
9. Turn dictionaries with malformed offset shapes or equality-aliased keys into a hostile packet API without new validation. The reviewed generated/certified-table path does not supply that expanded admission service.

These are written hypothesis/association challenges, not executed faults. The source already has extensive finite certificate, fixture and rejection checks. Their source-owned outcomes were neither missing nor reproduced here.

## Verdict, credit and remaining obligations

Qualified PASS for the all-integer implication and actual-code association, conditional on the source's successful complete finite table/certificate. No material correction is requested. The single descriptive fixture bit-count qualification above should remain distinct from the real4096/4090 API guarantee.

Credit Nick Petalas6574 for the matching/codec/proof/certificate and all source counts and constants; Ali Romman6536 for the larger-block question and three-axis predecessor,6534/5821 for earlier Gaussian constructions; David Ganz/Dugongue5815 for Gaussian conventions/Smith work; JoyboyBrian5485 and4743/native lineage and all retained source notices. Walsh finite-quotient algebra, bipartite matching and exact inverse substitution are classical. ToikY/OpenAI Codex supplies this source-aware external written implication audit.

The extra contracts of6536, including its fourth-power/port statements, are not inherited. Source6619's inward-norm obstruction assumes a different extra condition and neither invalidates nor certifies this codec. Full physical lookup/transforms with restored workspace, dirty-bank caller integration, tensor scheduling, actual whole-caller error/invoice, selected assumption discharge, phase covariance, exact fourth power, global memory optimum, human/kernel acceptance and κ/frontier/adoption remain outside this result. No original construction or scientific check ran here.
