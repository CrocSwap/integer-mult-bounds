# A packed finite-alphabet multitape baseline on Word RAM

Prepared for Dugongue with substantial OpenAI Codex assistance. Informal sufficient simulation theorem; no Lean formalization and no claim of novelty for classical finite-control tabulation.

## Theorem and model

Fix a deterministic machine M with k tapes, a fixed finite alphabet of size s >= 2, and fixed finite control. Each step reads/writes one symbol per tape and moves each head by at most one. Let T(n) be a supplied time horizon, with n <= T(n) <= n^d for a fixed d, covering the execution in question. For every fixed rational 0 < alpha < 1 (or a rational interior choice below any proposed real exponent), a uniform standard Word RAM with sufficiently large fixed word width w = C log(n+2), unit bounded-word arithmetic, Boolean operations and both logical shifts simulates M on a packed n-bit input in

    O(T(n)/log(n+2) + n/log(n+2) + n^alpha polylog(n+2))

word operations and O((T(n)+n)/log(n+2) + n^alpha) words of owned storage. The input/output conversion, exact early halt, head movements and tape changes are included. A work/output tape of length at most T+n can be scanned and decoded within the same bound. For multiplication with an explicitly designated O(n)-bit output, its final packed output cost is O(n/log n). No unbounded-integer instruction, nonuniform advice table, or free initialized dirty arena is used.

The finitely many small n below the tabulation threshold use a direct simulator. Construction and evaluation of the supplied time horizon are charged separately; a polynomial-time bound does not automatically give its value for free. For a fixed explicit elementary time bound, its usual O(polylog n) evaluation is absorbed by the displayed setup. Alternatively the theorem can take a valid horizon as an explicit input parameter. The result is a fixed-k, fixed-alphabet theorem; neither k nor s may grow silently with n.

## Table construction

Put h = ceil(log2 s) and b = max(1,floor(alpha log2(n+2)/(2kh))) above a sufficiently large fixed cutoff. Encode each tape in blocks of b symbols, occupying bh <= w bits per word. Each head is stored as a block address plus an offset in [0,b). This representation avoids division for address updates.

A macro reads a length-(2b+1) window centered at each tape head. During its next b transitions, no head can leave its own window, and no symbol outside these windows can be read or modified. The finite lookup key consists of the source control state and all k windows, with the heads understood to start at the central position b. Its bit length is

    kh(2b+1) + O(1) <= alpha log2(n+2) + O(1).

Enumerate every key, reject invalid alphabet codes, and directly execute at most b source transitions on each valid key. Store the final control state, the rewritten k windows, each head displacement in [-b,b], and the number of transitions actually performed before a halt. An already halted state performs zero transitions and changes nothing. Each entry has O(b) bits; for sufficiently large n it fits in a fixed number of words (indeed one after enlarging the cutoff for the fixed alpha). Each key is a word-addressable table index. Building and initializing the dense table costs O(2^(kh(2b+1)) poly(b)) = O(n^alpha polylog n) native operations. The direct enumeration algorithm depends only on M and the numeric n, not on an input-dependent oracle.

Equivalently, valid-key count is |Q| s^(k(2b+1)) = O(2^(2kb log2(s))); the dense h-bit encoding includes a constant-exponent allowance for invalid codes. The choice using h pays that allowance explicitly.

## Reading and rewriting across block boundaries

A centered window intersects at most four b-symbol blocks: its first symbol may be at any offset, and its length is 2b+1. Read those O(1) words, concatenate their relevant fields using a fixed number of shifts, masks and Boolean operations, and concatenate the k fixed windows into the key. If concatenating four blocks spans more than one word, use a fixed-size limb tuple and the usual carry-free cross-limb shifts; no wide integer operation is unit cost. The final table key and window fit a fixed number of words. No per-symbol loop occurs online.

The table supplies the full rewritten windows. Update each of the same O(1) blocks by a masked write that replaces only its intersection with the window. All symbols outside that window remain literal old symbols, including in the first and last intersected blocks. Head displacement has magnitude at most b; update the offset by this signed displacement and adjust the block address by at most one in either direction. A displacement plus an offset in [0,b) lies in [-b,2b), so a constant number of comparisons and additions suffices. Registers can use an explicit sign/magnitude or biased representation; negative natural subtraction is never assumed to wrap.

Because k is fixed, each complete macro uses O(1) word operations. The instruction set must include logical right shift directly if division is excluded; a right shift derived from division cannot be reused in a purported division-free simulation.

## Memory, initialization, input and output

Reserve a physical tape window large enough for the n-symbol input plus T moves and 4b guard symbols at each end. Its logical origin is offset by T+4b; the same bounded-address offset is applied to all head operations. It contains O(T+n) symbols per tape and hence O((T+n)/b) packed words. Explicitly initialize every owned word to the blank-symbol block; this costs O((T+n)/log n). Exterior memory remains arbitrary and is never accessed. Near either end of the reserved region, the extra 4b-symbol guards ensure every final macro window and its four whole containing blocks are physically readable even if the machine halts or reaches its horizon during that macro. For an exact horizon stop at a nonmultiple of b, either tabulate every remaining duration 0 through b (a polylog n setup factor) or directly execute the final fewer than b steps; O(log n) extra work is absorbed by setup.

Use an auxiliary b-bit conversion table to map packed input chunks to h-bit tape-symbol blocks and decode the output blocks. Its size is at most 2^b poly(b), already within n^alpha polylog n. Read/write n bits in O(n/b) chunks; conversion is not charged once per bit. For a fixed input syntax with separators or several operands, their fixed number of offsets and boundary fragments take O(n/b) work as well. All table and tape addresses fit in O(log n) bits because the horizon is polynomial; choose the fixed coefficient C to cover d, the constant number of tapes, setup tables and scratch. An allocation of n^d words is not charged as one operation: the actual O((T+n)/log n) owned words are initialized as above.

## Correctness and genuine halt

Relate a source configuration to its exact tape symbols in the packed arena, its control state, and its recorded head block/offset pairs. The window locality observation proves that the table's bounded execution uses exactly the same transition sequence as the global machine. Masked writeback preserves all unobserved cells and applies exactly the changed cells. The head and state updates are literal. Induction over macros proves exact configuration correspondence. If the source halts after j < b steps, the entry records that halt and j, preserves the resulting tape, and stops immediately after this macro lookup; no fictitious post-halt transitions occur. Thus the simulation gives both the correct output and genuine source halt. A final partial horizon is treated separately as above.

## Fair comparison with a native multiplication claim

Suppose a conditional fixed-tape multiplier has T(n) = O(n (log n)^(1-kappa)) for fixed 0 < kappa < 1, with a fixed alphabet and an ordinary packed binary input/output interface. The theorem gives a conditional Word RAM multiplier in

    O(n/(log n)^kappa).

Indeed T/log n has that order, n/log n is smaller, and for every fixed alpha < 1, n^alpha polylog n = o(n/(log n)^kappa). The simulation preserves whatever mathematical hypotheses the original multiplier needs; it does not verify those hypotheses independently.

Consequently a direct native implementation attaining exactly this same kappa may have valuable operational, proof-dependency or instruction-set advantages, but its exponent alone does not strictly beat the best TM-derived Word RAM baseline. A fair strict-improvement claim must exceed the actually transferred comparator or strengthen a clearly stated model/assumption contract. This note supplies a positive explicit baseline algorithm; it is not a universal impossibility result about native multiplication or future improvements.
