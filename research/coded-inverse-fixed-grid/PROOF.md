# Finite inverse recoding on a signed dyadic grid

This is a scoped classical bit/tape theorem. It is conditional on access to the 112 owners in one common coordinate system. It does not establish the physical thin-stage substitution in PR4940. All source pins are in `SOURCES.json`; PR4933 supplies the factorization and exact-real prefix bounds, which are predecessor results rather than new bounds here.

## Representation and contract

Fix a precision integer P, an integer H >= 0, and N >= 0 scalar components per owner. Real and imaginary parts are separate scalar components. Each of the 112 owner tapes contains N little-endian two's-complement words of the same width W, each followed by a delimiter, then an end marker. A word a represents a*2^-P and satisfies |a| <= H. The readonly bound tape contains H in W bits. Put L=56H+2 and W=bit_length(L)+1, so 2^(W-1)>L. Tape identities, word geometry and the fixed source matrix are part of the ABI, rather than data-dependent pointer aliases. The Python entry point additionally rejects aliases, malformed words, wrong incidence and out-of-range owners.

There are eight owned mode words and one owned division word, each W bits plus its delimiter. Their initial data bits may be dirty; initialization writes zero to all nine words. No borrowed helper tape appears in the program. Owner tapes start and finish at their first data position; all owned scratch heads return to their first data position and every owned data bit is zero on return. Owner contents are the output. There is no separate output stream or uncharged input/output copying.

The source `NORMALIZERS.json` gives eight length-112 columns m_k with coefficients 0,+1,-1. Each column has 56 nonzero entries, each owner row has four, M^T M=56I, A=I-MM^T/4 and A^-1=I-MM^T/52=(A+12I)/13. The verifier binds all 12,544 entries to the pinned `CODE.json`, independently of the numerical kernel. The fixed finite program hardwires these coefficients; it does not read a variable-size matrix or use a free matrix oracle.

For each scalar component, the literal program is:

```text
validate |x_i| <= H for all 112 owners
t_k = sum_i M[i,k] x_i               # 448 exact signed word ADDs
q_k = nearest_away(t_k / 52)          # eight bounded bit transducers
y_i = x_i - sum_k M[i,k] q_k          # 448 exact signed word ADDs
write zero into the eight owned mode words
advance all owner heads to the next component
```

All mode accumulation finishes before any owner is overwritten. The mode and division words are reused at the next component. The component order introduces no dependence between different physical coordinates, so the proof applies at every N, including spectators represented by additional components. It does not prove that a Gaussian caller can legally provide this coordinate layout.

## A literal denominator-13 transducer

The kernel copies the signed word into its division buffer, saving the sign during the forward copy. A conditional complement-plus-carry scan gives its unsigned magnitude u. Save the two low bits l in finite control and process the remaining bits most significant first. For a remainder r in {0,...,12} and a bit b, put z=2r+b in {0,...,25}; emit the quotient bit [z>=13] and replace r by z-13[z>=13]. These are 26 fixed finite-control transitions. No arbitrary-integer division, multiplication or remainder operation is a primitive.

After all W-2 high bits, floor(u/4)=13q+r. Thus u=52q+4r+l, with 0<=4r+l<52. Increment q exactly when 4r+l>=26, then restore the saved sign by a complement-plus-carry scan. The 52-way final decision is finite control. Finally overwrite all division-buffer bits with zero. The produced q is nearest integer to t/52 with ties away from zero, for either sign. In particular +26 maps to +1 and -26 maps to -1. The residue and carry control states are reset before returning; they do not retain uncharged numerical words.

The executable implementation uses bit arrays as tape witnesses. Its additions and conversions are bit loops with one-bit carry. Integer expressions inside the division loop are bounded by 51 and can be replaced by the displayed finite tables. Python list indexing is the reference interpreter's representation of an identified tape cell, not the claimed target-machine instruction. The following explicit sequential sweeps supply the tape implementation and tariff.

## Error, range and guards

Write q_k=t_k/52+e_k. The preceding remainder invariant gives |e_k|<=1/2, so

```text
y - A^-1 x = -M e,
|y_i - (A^-1 x)_i| <= 4*(1/2) = 2 integer grid units.
```

The bound is attained on the actual source matrix: x=26e_0 makes its first four mode numerators 26, so q=(1,1,1,1,0,0,0,0). At owner 0 the finite output is 22, while the exact rational output is 24. The negative fixture gives -22 versus -24. This is a sharp local worst-case bound for the stated rounding convention, not a propagation bound through a paid child.

Mode accumulations satisfy |t_k|<=56H. Since |q_k|<=14H/13+1/2, every owner-update prefix is bounded by H+4*(14H/13+1/2)=69H/13+2<=56H+2=L. The predecessor's exact 56-prefix and 69/13 output bounds are consistent with this estimate and are not claimed as new. Every signed ADD therefore has a representable mathematical result; its modular ripple implementation equals the ordinary integer result. Magnitude conversion is also representable as an unsigned W-bit quantity. No modular wrap is being reinterpreted as an approximate real operation.

In real units the local error is at most 2*2^-P. For a target grid 2^-p choose P=p+g with g>=1; the error is at most 2^(1-g) target-grid units. More generally, to allocate eta target-grid units to this call, it suffices to choose an integer g>=0 with 2^(1-g)<=eta. The output retains all P fractional bits. Rounding it back to p bits would add another 2^(-p-1) error and is not performed here. If the represented input already has error epsilon in component infinity norm, the inherited ||A^-1||_infinity=69/13 gives total error at most (69/13)*epsilon+2*2^-P. Signed permutation wrappers preserve these component bounds only if their separate physical ABI is established.

## Complete sequential bit/tape tariff

Use a fixed classical machine with 122 tapes: 112 owner tapes, eight owned mode tapes, one owned division tape, and one readonly H tape. Delimiters let loops stop without an unbounded word-size counter. The owner/mode indices and mode signs are fixed finite control. Every transition reads/writes the current finite-alphabet symbols and moves each head by at most one cell. A returned head is at the same word start unless an explicit advance is listed.

| Primitive | Sequential transition upper bound | Construction |
| --- | ---: | --- |
| signed ADD/SUB | 2W+4 | One LSB-first ripple scan and return sweep; subtraction complements the source and starts carry at one. |
| owned word CLEAR/INIT | 2W+4 | Write every bit and delimiter, then return. This is paid irreversible writing. |
| validate one owner against H | 8W+16 | Copy to division word, conditional magnitude scan, MSB-first compare with H, clear the division word; four returned sweeps. |
| signed ROUND52 | 24W+64 | Copy signed mode, magnitude scan, clear destination mode, aligned MSB-first /13 scan, rounding increment, sign restoration, division-buffer clear; offset-two alignment/return is included. |
| advance aligned owner heads | W+1 | Move all 112 heads across one record together; owned heads stay put. |
| final owner rewind | N(W+1)+2 | Return every owner head to its initial position together. |

For ROUND52 the six returned full-word scans other than division cost at most 12W+24. The quotient scan plus all alignment and returns costs at most 4W+16. Thus 16W+40 suffices before fixed framing, and the stated 24W+64 safely includes it. The two zero-writing scans inside each ROUND52 are charged there. Saving the sign occurs during the copy; the low two bits and a remainder below 13 are finite control. No direct jump to a word endpoint is assumed.

Initialize all nine owned words once. For each of N components pay 112 validations, 896 signed ADDs, eight ROUND52 calls, eight final mode CLEARs and one owner advance. Pay the final rewind and 62 additional framing transitions. The resulting bound, including both bit arithmetic and data motion, is

```text
T(N,W) <= 9(2W+4)
        + N[112(8W+16) + 896(2W+4) + 8(24W+64) + 8(2W+4) + W+1]
        + N(W+1) + 64
       = N(2898W+5922) + 18W+100.
```

There are at most 122T individual head moves, at most 122T symbol reads and at most 122T symbol writes. Data space is 112[N(W+1)+1] owner cells, 9(W+1) owned scratch cells and W+1 readonly bound cells, plus fixed framing. In addition to nine initial zeroing scans, every component pays 112 range-check buffer clears, 16 internal division clears and eight final mode clears: 136N+9 full W-bit zero-writing scans. None of these is assigned zero cost. Recursive calls and query rank added by this arithmetic kernel are zero. A conjugated physical C^-1 call additionally needs its actual K_i wrappers and movement; none is included in this scalar-only tariff.

## Cleanup is classical and irreversible

This implementation deliberately has a classical overwrite contract. The pinned `TM-TO-WORD-RAM.md` defines a TM transition by arbitrary finite-alphabet write symbols, and the actual `MACHINE-INTERFACE.md` permits memory stores and wrapping values. Both support destructive writes to explicitly owned scratch. The tariff above pays for every such write and restores its bits to zero. A zeroed owned word is not being called a reversible uncomputation.

The rounded owner map is noninjective: for x=M[:,0], M^T x=56e_0, round(56/52)=1 and y=x-M[:,0]=0. The distinct input x=0 also maps to zero. This collision is a required executable fixture. The erased mode q_0=1 cannot in general be reconstructed from the returned owner values. Consequently this kernel does not satisfy a reversible or information-preserving physical cleanup ABI. It cannot be inserted into a caller requiring that stronger contract without an additional retained-input/history construction and its costs. Nor is it an exact inverse of a rounded forward code or of a rounded Gaussian child.

Under the stated classical ABI, the only changed borrowed state is the intended 112-owner output. The 408 native helpers are absent from the tape inventory, never addressed and never used as scratch or erased. If legal common-coordinate access, classical owned erasure or global precision funding is unavailable in the eventual caller, this local theorem remains conditional and supplies no complete construction or new kappa.
