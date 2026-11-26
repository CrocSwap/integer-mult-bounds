# Exact Walsh scalars without a per-record modular inverse

The adaptive normalized Walsh transform can use a single modulus whose predecessor is divisible by every individual scalar denominator. On each record a fixed eleven-tape program then implements a signed rational scalar in at most

\[
  2048(K+B+3)(B+3)\text{ transitions},\qquad 7K+6B+28\text{ visited cells}.
\]

Here the residue and modulus have \(K\) digits and the two short inputs have at most \(B\) digits each. These bounds include word allocation, head returns and clearing the working digits. The physical distribution of coefficients and records uses the separate [NW routing schedule](foundations/nonstationary-rational-walsh.md).

## One divisor for all defect sets

Use the admitted numerical arity \(m=2^y-1\), \(y\ge6\). Write \(W=2^y=m+1\) for the number of predictor seeds, \(s_0=W/16\) for the paid check width, \(d=2\lceil 2\sqrt m\rceil+1\) for the Newton degree, and \(t=L_F/2\) for the source rectangle degree. The Fourier shape guards give \(2\le L_F\le m\). We have \(d\le m\) for this domain. An inadmissible width uses direct butterflies.

For a defect set \(J\subseteq\{0,\ldots,W-1\}\), \(j=|J|\le s_0\), the row of \(V_J^{-1}\) indexed by \(i\in J\) consists of the coefficients of

\[
    \prod_{u\in J\setminus\{i\}} \frac{W X-u}{i-u}.
\]

The absolute denominator product divides \(i!(W-1-i)!\). On each side of \(i\) the distances occur at most once, and range through positive integers at most \(i\) or \(W-1-i\), respectively. The binomial coefficient \(\binom{W-1}{i}\) shows that this product divides \((W-1)!\). Consequently \((W-1)!V_J^{-1}\) is integral for **all** subsets \(J\). No inverse-table enumeration is required. The empty defect set uses the zero map.

Let \(G_m\) be the product, with multiplicities and with empty product one, of the nonzero magnitudes

\[
 \left|\gamma\sum_{h=0}^d(-2)^h {c-u_0\choose h}-z\right|,
 \qquad 0\le c\le m,\quad \gamma,z\in\{-1,1\},
 \qquad u_0=\lfloor m/2\rfloor-\lceil2\sqrt m\rceil.
\]

The set includes each actual nonzero discrepancy. Therefore every entry of
\(V_J^{-\mathsf T}\operatorname{diag}(1/g_i)V_J^{-1}\) has reduced denominator dividing \(G_m((W-1)!)^2\). Indeed, after multiplication by that number every term in every entry is integral. Taking signed differences of the two check inputs and duplicating the output with sign preserves this divisor.

For the remaining maps set

\[
 D_m=2\,(2^t t!)\,(2d!)\,W^{s_0}\,((W-1)!)^2\,G_m .
\]

The first factor covers a direct normalized four-point transform. In the source binary geometry the free weight is \(-p(k)\), where \(p(k)=(\prod_{h=1}^t(2h-k))/(2^t t!)\). Thus \(2^t t!\) clears its denominator. The charged weights are the coefficients in the binomial basis in \(L_F-k\). Each is an integral finite difference of the sampled values, so the same denominator clears them. The Newton update on the old row uses only the denominator \(2h\) for \(1\le h\le d\), apart from integral scalars. The fixed check and lift entries \((i/W)^h\) for \(0\le h<s_0\) have denominators dividing \(W^{s_0}\). The source phases are signs, the indices and basis changes are binary permutations, and paired normalized child transforms supply all powers depending on the spatial width. Execute a rectangle weight and a Newton weight as separate scalar instructions if the source displays their product. This keeps the same spatial children. These cases account for the scalar types in the rational predictor with its two finite conversion phases. [Newton and repair, §§3–5](foundations/pairwise-newton-division.md) · [Source Fourier kernel](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/build/kernel.tex) · [Normalized binary schedule](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/build/binary.tex)

Compute \(U=2\prod_i D_{m_i}\) over the actual arities on the one numerical width chain. Every individual reduced denominator \(b\) divides \(U\), including in a repeat at the same arity. For selected size \(s\), signed input magnitude width \(w\) and global address width \(k\), take

\[
       M=1+2^{k+w+s+2}U.
\]

Then \(M\equiv1\pmod b\) for *each* applied scalar. The old prime-support argument proves a unit property. The integer multiple proved here pays for a stricter physical instruction with no extended Euclidean calculation. Arbitrary composed expressions may have larger denominators. The matrix identities specialize because all the individual scalars are units where required.

## Width at the integer caller

An elementary uniform estimate is

\[
  \log_2 D_m < 5W^2(y+2),\qquad
  B_m=8W^2(y+2)
\]

where \(B_m\) bounds the ordinary bit lengths of the reduced numerator magnitude and denominator of *every* elementary scalar above, including a full entry of the spectral repair.

For a gap, every generalized-binomial numerator factor has magnitude at most \(2m\), since \(0\le u_0,c\le m\) and \(d\le m\). Each gap therefore has magnitude at most \(1+(d+1)(4m)^d\) and logarithm at most \(W(y+2)\). There are at most \(4W\) factors. The two factorials outside the squared factorial, the explicit powers of two, and the squared factorial together contribute at most \(2+ m(1+y)+my+s_0y+2my<W^2(y+2)\) to the logarithm. For an inverse Vandermonde row the sum of the absolute coefficients of its numerator polynomial is at most \((2W)^{j-1}\), and its absolute integer denominator is at least one. A spectral-table entry has magnitude at most \(j(2W)^{2(j-1)}\), including either signed input arm. Multiplying by \(D_m\) bounds the reduced numerator. The free rectangle values are bounded by \((2m)^t\) in magnitude. A finite difference introduces at most \(2^t\). The fixed check values have magnitude at most one. The Newton scalar magnitudes are at most \(\max(4m,2^d)\). These estimates, with one extra digit for the bit length and at least one digit for zero, give \(B_m\).

Put \(X=\lceil\log_2(k+2)\rceil\) and \(Y=\lceil(X^2\lceil\log_2(X+2)\rceil)^{1/3}\rceil\). At every adaptive width \(y\le Y\). The width chain contains at most \(X\) arities, since every remaining positive child is at most half the parent. Hence

\[
   \log_2 U < 1+5X\,2^{2Y}(Y+2).
\]

For a concrete range take \(X\ge2^{24}\). Then \(\lceil\log_2(X+2)\rceil\le 2\log_2 X\le X/2^{18}\), since \((\log X)/X\) decreases there. Thus \(Y\le X/64+1\le X/32\). Also \(8X(X+2)\le2^{X/8}\). It suffices to use \(8X(X+2)\le16X^2\) and \(4+2\log_2 X\le X/8\), true at the left endpoint with increasing slack. Therefore \(\log_2 U < 1+2^{3X/16}\) and \(B_m\le2^{3X/16}\). As \(2^{X-1}<k+2\), this gives \(\log_2 U<k\) and \(B_m\le k^{1/3}\) throughout the range. For the second inequality use \(k\ge2^{X-2}\) and \(3X/16\le(X-2)/3\).

For example, choose a common boundary grid of \(72k\) fractional bits. Each real or imaginary input component at a Walsh call has magnitude at most \(2^{13k}\). Its mantissa fits \(w=85k+1\) magnitude bits. With \(s\le k\), \(K=\operatorname{bitlength}(M)\le96k\) at the displayed range. This grid suffices for the source's per-phase \(2^{-70k}\) rounding and for the Walsh boundary's \(2^{-50k}\) Euclidean tolerance. Generating the coefficients of the outer phases and establishing the complete multiplier clock have their own bills. [Source tolerances](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/The-logarithmic-exponent-of-integer-multiplication-on-tapes-November-24-2026/build/integers.tex)

## Physical record and invariant

All four input words are nonempty, separately marked and low digit first. Modulus and canonical residue have width \(K\), and positive \(b\) and numerator magnitude have widths at most \(B\). High padding is allowed. The successful-call precondition is \(M\ge2,\ 0\le x<M,\ b\mid M-1\). A finite control bit supplies the numerator sign. All word heads start on their low digits. Compute \(z=Ax\bmod M\) by the two separately reduced shift/add steps of the pinned head program and optional canonical negation. For \(b=1\) copy \(z\). Otherwise compute \(h=z\bmod b\) and set \(r=0\) if \(h=0\), else \(r=b-h\). As \(M\equiv1\pmod b\),

\[
  z+rM\equiv0\pmod b,\qquad 0\le z+rM<bM.
\]

The exact quotient \(v=(z+rM)/b\) is the unique residue \(0\le v<M\) satisfying \(bv\equiv Ax\pmod M\). No gcd, short inverse, or long reduction of \(M\) is executed. The long path has four input tapes, three long banks of lengths \(K+1,K+1,K\), two short banks of length \(\operatorname{width}(b)+1\), and two banks of length \(K+\operatorname{width}(b)+1\). Two boundary cells per tape give the displayed \(7K+6B+28\) bound. The short path only uses the two homes of each dormant tape. Repeated calls overwrite current extents. The union on each tape is the largest extent reached. All heads return to their first digit and non-output working digits are cleared. On a stream the separate input and output array banks remain charged to its caller.

The [program](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/sessions/2026-11-26-S008/walsh-aligned-scalar.mjs) uses the original single-symbol loops, whose Git blob is checked before the replay. In the following table a width counts data digits. A single read, write or unit head move can be one ordinary multitape transition while the other tapes stay. All temporary digit/flag values have fixed finite ranges. Inline the bounded call graph, unroll the fixed lists of tapes and eliminate head-free branches after the preceding read. Each data-dependent loop tests a symbol. This yields a fixed finite transition function with the displayed primitive count and at most 16 extra transitions for initialization and return. All home markers can be installed simultaneously.

| Routine | Upper bound in primitive transitions | Reason |
|---|---:|---|
| Allocate, erase, zero/one test, copy, compare, add/subtract, shift | \(32u\) apiece | \(u=2+\max\) of involved widths, including the target allocation. Per digit at most six symbol actions in the main scan, three for a remaining high part, and two per word's rewind. Allocation scans at most two input length words, whose total length is at most the target width. |
| Reduce once | \(64u\) | One comparison and at most one subtraction. |
| Long division with optional quotient | \(160(d_0+2)u\) | For each of \(d_0\) dividend digits, shift remainder, compare, possibly subtract and write one quotient bit. At most \(96u+5\) actions a digit. The initial clear, high-end seeks, final low-digit returns and all loop tests fit the stated allowance. Here \(u=2+\max(\text{divisor width},\text{remainder width})\). |
| Long-by-short multiply | \(256(d_0+2)u\) | Each of \(d_0\) factor digits uses a shift, up to two reductions and one addition. At most \(192u+4\) actions per digit, plus clear and factor seek/return. Here \(u\) uses the maximum width of the long operands, modulus and target when present. |

Set \(Q=K+B+3\) and \(D=B+3\), so \(D\ge4\). There are two multiplications costing together at most \(512QD\) and two divisions costing at most \(320QD\). All simple invocations outside those routines, including every allocation, input test, negation, correction, exact-remainder test, copy to output and final cleanup, number at most 32. Together they cost at most \(1024Q\). Adding the 16 entry/return steps gives less than \(2048QD\). All records at the numerical range above therefore cost at most \(2^{18} k(B+3)\) steps. On the full padded port \(K=100k\), \(B\le k^{1/3}\) gives \(K+B+3\le128k\), and \(2048\cdot128=2^{18}\). This prices the application of a supplied coefficient. Preparation from the address, exception routing, and the number of such instructions need separate physical bounds.

## Verification

`node walsh-aligned-scalar.mjs` compared 8,062 head executions with the unique modular congruence, including 1,148 calls with a wider padded coefficient. The test checks input preservation, output canonicity, head homes, work erasure, visited extents and the conservative transition cap.

The checkpoint’s finite scalar check compared the signed integer polynomial compiler with independently inverted rational Vandermonde matrices at 294 actual spectral keys of arities 63, 127 and 255. It checked 1,066 repair entries and 1,066 scaled Lagrange entries, covered empty and up to four simultaneous real defects, and tested 36 further arbitrary node sets. A real arity-63 coefficient with denominator divisible by 73 was applied on the eleven tapes at the newly constructed 7,650-bit modulus.

The [first Lean module](../S008/WalshAligned.lean) proves the simultaneous factorial divisor for every subset, the reduced-denominator divisor of the two-sided inverse table for arbitrary integer polynomial numerators and nonzero gaps dividing the supplied gap product, the short correction identity, and the original rational `Port.Token` for the resulting quotient. These are algebraic properties. The state-transition counts above and the algebra-to-tape correspondence are written proofs. Run `bash walsh-check-lean.sh PATH_TO_OPENAI_MATH PATH_TO_PINNED_MATHLIB` with the pinned Lean 4.34.1 release and the imported dependencies of Mathlib commit `d13f23b723b8a846827a245b89c10fc7d3f11612` available. The [build script](../verify.py) identifies the checked source and the narrowed import of the unchanged token declarations.



The [actual interpolation module](../S008/WalshInterpolation.lean) also proves the full correction recovery and the exact integer compiler formula, through the original rational scalar token, without assuming that an unidentified matrix is an inverse. Its registered theorem names and exact builds appear in the same script. The [compiler verification](walsh-repair-compiler.md#exact-correspondence-to-the-check-table) includes the unreduced 7,393-bit physical coefficient.

The [binary shift and gap proof](../S008/WalshShift.lean) further discharges the actual bad-row capacity and gap-product divisibility assumptions for every source key and numbered binary seed. It uses the real Newton predictor and the genuine product over the \(4(m+1)\) candidate gaps. The final [midpoint module](../S008/WalshRounding.lean) certifies the unique signed-magnitude rounding specification at the integer root. The formal scope still excludes the complete adaptive tape transition system.
