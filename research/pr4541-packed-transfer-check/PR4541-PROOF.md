# A complete packed-input simulation bound

Prepared by Dugongue with substantial OpenAI Codex assistance and three parallel agents. Apache-2.0. This is an informal universal construction proof, supported by finite exact operational-model checks. It is not a Lean theorem or a complete emitted RamStd program.

## Theorem and conventions

Fix a deterministic finite-alphabet k-tape Turing machine M with Q states, blank 0 and finite transition table. k, Q and the alphabet are fixed before the input; they are not additional variable-size inputs. One transition reads all tapes, writes their new symbols and moves each head by -1, 0 or 1. A missing transition is genuine halt. Let the total binary input length be n, let the requested binary output cap be m, and suppose the actual execution halts after T transitions. Assume fixed constants a>=8, d>=1 give

    T+n+m+16 <= 2^(a-4) (n+2)^d.

The machine receives packed binary input in power-of-two chunks as specified below. Its conventional TM input protocol uses two nonblank bit symbols distinct from blank, at fixed tape origins; its output is an MSB-first binary word at a fixed origin, terminated by blank or occupying the whole m-cell cap. A fixed alphabet relabeling and ordinary linear-time TM protocol conversion can arrange this standard interface. Such conversion time is part of T, not an uncharged oracle.

There is a uniform finite-program Word RAM algorithm, fixed before n and independent of actual T and physical word width, with word width w >= C_M (floor(log2(n+2))+1), that produces exactly the same integer output in fixed-width packed LSB form. It uses only literal assignment, indirect LOAD/STORE, ADD, natural SUB, Boolean operations, shifts, branches and word input/output. It uses no multiplication/division instruction, supplied lookup table, advice string, randomization or unit-cost exact complex cell. Its total cost is

    O_M((T+n+m)/log(n+2) + (n+2)^(1/16) log(n+2)).             (1)

All constants and the fixed program may depend on M and the chosen envelope constants a,d; the M subscript below includes those fixed constants. Every address and intermediate value fits in a word. A nonhalting TM computation is not converted to a halt by an artificial epoch boundary: every finite prefix within the same numerical envelope is simulated faithfully. The halting theorem itself assumes the stated finite T.

The RAM memory starts identically zero, as in the actual Problem 1.8 RamStd model used in PR #4538. All newly allocated table, tape, IO, descriptor and scratch arenas are disjoint. The numeric span of memory is polynomial in n; zero initialization of that model is not a clearing algorithm for arbitrary dirty storage.

## 1. Uniform parameter choice and complete setup

Let lambda=floor(log2(n+2)), ell=lambda+1. Choose c, a fixed power of two, large enough to encode the fixed alphabet, and c>=2 so blank and the two bit codes fit. Let K be the least power of two at least k and s=max(1,ceil(log2 Q)). Define

    q = floor(lambda/(64 K c));
    r = largest power of two <= max(1,q);
    B = 4r;  L = 2r+1.

Because 64Kc is a power of two, q is obtained by a right shift; r is obtained by a doubling loop. lambda is computed by repeatedly right-shifting n+2. This costs O(log(n+2)) word operations. r is Theta_M(log(n+2)), with the small-input cutoff absorbed in machine-dependent constants; in particular r >= lambda/(128Kc) when lambda>=1.

The local table has one row for every bit pattern consisting of a state field and k windows of L consecutive c-bit symbols. Its key size is

    b = s + kc(2r+1).

For lambda >= max(64Kc,64s), we have r>=1, 64kcr<=lambda and 64s<=lambda. Since 2r+1<=3r,

    16b <= 16s + 48kcr <= lambda.

Thus all 2^b rows, including invalid/unreachable state or symbol patterns, number at most (n+2)^(1/16). The finitely many smaller inputs have a fixed table-size bound depending only on M. No universal statement about an arbitrary Q is inferred from the Q=3 parameter tests; the state-bit cutoff is explicit.

For each row, place each local head at offset r in its window and simulate up to r literal M transitions, stopping at the first missing transition. Save the terminal state, a true-halt flag, elapsed transition count, all k updated windows, and the k final local head offsets. Missing transitions on invalid patterns may be defined as halt; valid runs never use invalid encodings. Dispatch over the fixed finite transition table costs a machine-dependent constant per local step. Construction therefore costs O_M(r 2^b) operations. Store each row in a fixed power-of-two stride of at least 2k+3 words, so its address is formed by a shift and an addition. Every entry is generated during the run from M and r; no table is supplied for free.

The binary codec tables in PACKED-IO.md contain O(2^r+2^(cr)) rows and take O(r 2^(cr)) setup. Their exponent is smaller than b, so they fit the same startup bound. This pays setup for every input, without amortizing over an unspecified batch of inputs.

## 2. Ordinary coordinates, packed words and address safety

Use a fixed polynomial origin

    H = 2^(a+d*ell).

This is computed by a shift whose exponent uses fixed-constant repeated addition. The program knows a,d as machine constants; it does not receive T or a time-horizon advice string. A signed TM coordinate z is represented at nonnegative position H+z. The envelope implies H is more than sufficient for every visited position and the margin r; no truncating subtraction of a left window origin changes its intended value.

A tape word stores B fields. Take a fixed power-of-two interleaving stride J>=k. Tape i, block u, is stored at

    dataBase + J*u + i.

The table base is a fixed machine-dependent power of two above every reserved register/scratch cell (at least 512 in the model); the data base lies above all table and reserved cells. This remains valid for large fixed k, rather than assuming a 512-cell prefix suffices for every machine. Dividing a position by B and reducing it modulo B are right shift and AND because B is a power of two. Different tapes and blocks have different addresses; all metadata, rows, IO buffers and descriptors have separate arenas.

A window of L<=B consecutive cells spans at most two packed words. If its first word supplies a fields, read its suffix and, only if needed, the low L-a fields of the next word. Shift, OR and mask these fields into one word. To write it back, clear only the corresponding field masks and OR in the two fragments. The Boolean identities prove preservation of every neighboring field and every unused high bit, with arbitrary dirty values there. This is a constant-size additive/Boolean operation sequence per tape, even when a window crosses a packed block boundary. The implementation provides generalized bounded-length chunks for input/output as well.

This ordinary-coordinate representation matters: a signed interval is not a contiguous bitstring under the unpacked compiler's zigzag mapping. No strided gather, negative-bank reversal or arbitrary bit permutation is assumed to cost one operation.

To see a logarithmic width suffices globally, note that key bits are at most s+3kc+lambda/32 for all inputs, table row size is fixed, H has a+d*ell+1 bits, and every visited coordinate lies within the supplied polynomial envelope. Multiplying a block index by the fixed interleaving stride is a shift. Adding all IO/descriptor arenas and margins still has polynomial numeric span. A sufficiently large fixed C_M bounds all these exponents and literals. For example, uniform_parameters in tabulated_tm.py uses the conservative coefficient a+d+s+rowLog+strideLog+4kc+32 for its table/tape envelope; a caller includes its fixed IO arena constants in C_M. Word width also exceeds 4cr+1, so masks, reservoirs and all shifted fields fit. At every greater physical word width, the same intended operations and output are obtained. This is bounded-word computation, not an unbounded-register simulation.

## 3. One macro step and genuine halt

Maintain the invariant: the saved state is M's state, head i is H plus its signed TM position, and every represented tape field equals its TM symbol. Initially encoded input fields establish the invariant, and every uninitialized field is blank because RAM memory is zero.

At a macro boundary, fetch all k windows centered on the current heads before performing any tape writes. Form their concatenated key with the current state and fetch the generated row in O_M(1) word operations. Apply every updated window at its old position and set

    newHead_i = oldHead_i + savedLocalHead_i - r.

All subtractions are safe under the polynomial-origin bound. During r TM transitions a head moves at most r, so it never reads or writes outside the supplied 2r+1-cell window; the final move may reach an endpoint, still inside the window. The local table's literal transition simulation and the all-reads-before-writes discipline therefore preserve the full invariant, including distinct tapes at coincident coordinates. Applying a returned complete window also preserves every cell outside it.

If a missing transition is seen before r successful transitions, the true-halt flag is set and elapsed counts only actual transitions. If the r-th transition reaches a halting configuration, the next macro detects that missing transition with elapsed zero. Thus at most floor(T/r)+1 macro calls are needed for a halting run. An epoch completing r transitions without a flag does not itself halt. This proves both exact halting semantics and O_M(T/r+1) simulation cost.

The operational model records its displayed primitive operations, not exact fully emitted RamStd instruction counts. All source loops are over fixed k or the explicit bounded table/epoch counters. Fixed-size dispatch, register assignment and branch lowering alter only machine-dependent constants. No local table lookup is counted as a whole TM step oracle: the complete table construction is explicit and charged above.

## 4. Packed external ABI, including partial chunks

Let each operand arrive as exactly ceil(length/r) little-endian r-bit digit words, with unused high bits zero; the logical lengths are supplied as bounded headers. The physical list-length prefix is also paid and fits in a word. For w=Theta(log n), this is an ordinary constant-density packing of the binary input. The format is determined by n, not by the unknown physical w, so it works at all sufficiently large word widths. Input bit length n is the declared padded binary length, not the number of list entries or the numerical value of an all-zero operand.

The codec explicitly tabulates expansion from binary r-bit chunks into c-bit codes 1/2, and decoding from c-bit chunks to binary values with prefix lengths and validity. It handles reversed chunk order for MSB input and reversed output descriptors for fixed LSB output. Read, store, reverse and masked-insert O(n/r) chunks. Separate operands may use separate tapes. If they share a tape, use one continuous reservoir across operands and delimiters; concatenating separately padded partial chunks would insert blank cells and is incorrect. A fixed binary length header costs only O(log n) cells and fits the startup allowance.

The output decoder reads at most ceil(m/r) coded chunks, stops at the first blank or cap, reverses the retained descriptors, writes exactly ceil(m/r) LSB digit words, and pads only high bits with zeros. This preserves the numeric value even for leading zeros, zero itself and a short terminated prefix. A full-width output need not expose its following terminator. No bit-by-bit external IO pass costing Theta(n) is hidden here. The detailed reservoir and first-blank proofs are in PACKED-IO.md.

Counting generated setup, simulation, input and output now gives

    O_M(r 2^b + log(n+2) + T/r + (n+m)/r + 1),

which implies (1). The total buffer footprint and the polynomial numeric address envelope were included above. Arbitrary dirty reuse would require separately paid initialization; the theorem does not silently change the zero-initialized RamStd model.

## Corollary: the supplied multiplication bound

Suppose a fixed deterministic multitape machine multiplies two padded n-bit integers in

    T(n) = O(n (log n)^(1-kappa)),       0<kappa<1,

under explicitly retained hypotheses. Apply the construction with total input length 2n and output cap 2n. Replacing n by 2n changes constants only. Polynomial-time and O(n) output bounds supply the fixed address envelope. Formula (1) gives

    O(n/(log n)^kappa + n/log n + n^(1/16) log n)
      = O(n/(log n)^kappa)

bounded-word RAM operations. Every input's table construction and codec work is included. Output consists of exactly ceil(2n/r) packed LSB digits. With one-bit-per-word external IO the bound is instead O(n+T/log n); the stronger corollary genuinely needs the stated packed ABI.

The admitted selected TM parameter 0.0023 therefore gives this same conditional RAM saving; the stronger pending TM claim 0.003020165 can be substituted only with all of its complete antecedent and retained assumptions. Neither substitution is an independent proof of that antecedent. No new numerical TM kappa is derived here, and adding one to kappa by changing the normalization would not be a TM frontier improvement.

## Precedent and scope

Hopcroft, Paul and Valiant's 1975 Section 4 supplies the classical logarithmic TM-to-RAM simulation idea. Their stated theorem requires T>=n log n because its input scan costs n. We use the method as precedent and supply the packed-input/packed-output construction explicitly for the sub-n-log-n regime; that theorem's original hypothesis is not simply dropped. PR #4538 supplies this project's exact bounded-word machine and packed-field refinement precedents. The current proof and code do not claim to have invented tabulation or established worldwide priority for the corollary.

Sources and inspected overlap are recorded in OVERLAP.md and OVERLAP-SOURCES.json. The finite implementations check the displayed model; an emitted complete RamStd program, formal compiler refinement, isolated Linux execution and a new TM paid-profile witness are separate future work. They are not assumed as hidden mathematical gadgets in the algorithm above.
