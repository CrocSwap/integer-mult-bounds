# Uniform removal of bounded-word multiplication

This is a classical tabulation construction, supplied as a sufficient target-model result. It does not improve a multitape-Turing-machine κ and is not claimed to be historically new.

## Exact model

Fix a constant C. For input length n, let l=floor(log2(n+2))+1, and use virtual words of V=C*l bits, with actual RAM word width at least V and large enough for the disjoint input, working memory and table banks. The program is fixed before n and the actual width. Let b=floor(l/4), assuming l>=8; handle the finitely many smaller n by fixed code. Set B=2^b and K=8C, so K*b>=V. The target uses bounded ADD, natural SUB, Boolean operations, left/right shifts, branches and indirect memory. It does not use multiplication, division, population count or a supplied table.

The richer RamStd shiftr instruction is permitted. If using only the narrower original Lax13 fragment, a separate right-shift macro without division is needed; the following theorem does not pretend its div-based macro meets a no-division whitelist.

## Table construction

Allocate B^2 product entries. In row a, start v=0, and for j=0,...,B-1:
- store v at address base+(a<<b)+j;
- replace v by v+a.

Induction gives table[a,j]=a*j. Every stored value and intermediate v is below B^2, hence fits in at most 2b bits. No multiplication instruction occurs in the constructor. It performs O(B^2) word operations and uses B^2 words. Since 2b<=l/2, this is O(sqrt(n+2)); the input-length computation and fixed mask preparation cost O(log(n+2)) additional instructions.

The table is allocated in a fresh disjoint bank, its total footprint is included in the word-address bound, and its construction is paid once per input. It contains no advice or input-dependent mathematical constants.

## Constant-time word product

Split each V-bit operand into K radix-B digits by repeated AND with B-1 and right shift by b. Extra top digits are zero. Initialize 2K output digits to zero. For i=0,...,K-1, start carry=0 and for j=0,...,K-1 set
$$
z=c_{i+j}+\mathrm{table}[a_i,b_j]+\mathrm{carry},\qquad
c_{i+j}=z\bmod B,\qquad \mathrm{carry}=\lfloor z/B\rfloor.
$$
The remainder and quotient are AND with B-1 and right shift by b. At the end of the row put carry into c_{i+K}. This cell was still zero: all earlier rows touched indices at most i+K-1.

Every temporary obeys
$$
0\le z\le(B-1)+(B-1)^2+(B-1)=B^2-1.
$$
Every carry is below B. Therefore the actual bounded machine sees no unintended modular overflow. The ordinary radix carry identity proves by induction on the rows that the 2K digits represent the exact product of the input operands. K is a machine constant depending only on C, so this takes O(K^2)=O_C(1) word operations and O_C(1) scratch words per product.

Return low and high V-bit words by OR-ing the digit slices on each side of bit V. At most one digit straddles that boundary; split it by AND/right shift and place the two pieces on the corresponding side. These are O(K) further instructions. The masks are prepared once using repeated doubling-plus-one, avoiding an overflowing attempt to form 2^V in a V-bit word. Return both words or just the low word as required. The same construction computes exact products of fixed-many-word operands with another fixed factor.

## Consequence and boundary

A fixed program using V=O(log n)-bit ADD/Boolean/shift operations and word multiplication, polynomially many addressable cells and T(n)>=n operations has a uniform implementation without multiplication instructions in O(T(n)+sqrt(n)+log(n)) time, with the original memory plus O(sqrt(n)) table words. This statement preserves the original arithmetic and address widths; any virtual-width masking and bank relocation must be included in the caller's implementation.

For a program also using division, this theorem alone is insufficient: division needs its own implementation or a proof that the selected algorithm does not use it. Fürer's 2014 Theorem 4.1(a) gives linear multiplication in the richer log-RAM model and analyzes short integer multiplications plus simple FFT operations; a fully pinned instruction-level instantiation still must account for its complete setup and operations. Do not cite this tabulation lemma alone as a new linear multiplication algorithm or an unconditional project frontier improvement.

Primary precedent: Martin Fürer, *How Fast Can We Multiply Large Integers on an Actual Computer?*, arXiv:1402.1811v1, Section 2 and Theorem 4.1(a), https://arxiv.org/html/1402.1811v1 . The broader tabulation technique is standard; this note makes its uniform preprocessing, address footprint and bounded intermediates explicit for the RamStd migration.
