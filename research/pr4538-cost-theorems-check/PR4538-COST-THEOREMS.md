# Streaming Word RAM costs for the native layout layer

These are constructive sufficient results for a Word RAM port. They establish
primitive semantics and costs. They do not establish a new multiplication bound,
a new κ, or a complete port of the analytic/recursion/compiler chain.

## Model and representation

The baseline instruction set has bounded-word ADD, truncated SUB, AND, NOT,
left shift, indirect LOAD/STORE, conditional/unconditional jumps, and literals.
Words and addresses have w bits, with w >= 6 so the fixed program and registers fit. Multiplication and division of words are not
used by the constructions below. They remain legitimate optional instructions
in the richer `Lax13.Ram` model; an n-bit input-sized unit multiplication is not
being introduced. XOR and MOV are macros taking at most 4 and 2 instructions
respectively in that existing model. JNZ expands to at most 2 instructions.

A record consists of L >= 1 arbitrary words, stored at stride K = 2^s, where
L <= K < 2L. Let N = 2^r and r <= w. The two record buffers, the column tables,
and a constant register/scratch region are disjoint and lie strictly below
2^w. This is stronger than r <= w; in particular r = w cannot fit these two buffers. No address calculation wraps. Initial values outside the
written payload cells are arbitrary. The source is preserved.

The supplied affine map has columns c_0,...,c_(r-1) in F_2^r, assumed linearly
independent, and offset b in F_2^r. Preparing/checking supplied metadata is a
separate caller action, not an uncharged gate-list compiler. Invertibility can
be checked by ordinary word-packed elimination in O(r^2) word operations.
A straightforward gate-word metadata compiler may instead cost O(m r^2) for m
gates; no bound on that cost is hidden in the streaming theorem.

## Theorem 1: affine permutation with a linear word count

There is one fixed program that, from the above data, writes

    destination[(A x XOR b)*K + j] = source[x*K+j]

for every 0 <= x < N and 0 <= j < L, preserves every source/table cell and every
untouched destination padding cell, and uses at most

    8 N L + 40 N + 8

expanded instructions. This count starts from preloaded buffers and parameters;
input deserialization and final output serialization are caller costs.

Proof. Start with x = 0 and y = b. Copy the L-word payload to destination record
y. To advance x, visit exactly the bit positions flipped by binary increment,
XORing c_j into y for every flipped bit j. Thus the invariant y = A x XOR b
holds initially and after every increment, by linearity over F_2. Invertibility
makes the N destination indices distinct, so every destination payload is
written exactly once. The buffers are disjoint, so no source read is invalidated.
No instruction writes a source, table, or padding address.

For each bit j, binary increment between 0 and N-1 flips that bit exactly
N/2^j - 1 times. The total number of flips is therefore

    T = sum_(j=0)^(r-1) (N/2^j - 1) = 2N - r - 2,

including r = 0, when T = 0. The displayed fixed program has 30 macro
instructions, with loops but no instruction depending on r, L, or the input
values. Its charged expansion count is

    8 N L + 9 N + 11 T + 3
      = 8 N L + 31 N - 11 r - 19
      <= 8 N L + 40 N + 8.

The r = 0 case costs 8L + 12 and satisfies the same formulas. Destination base
addresses use y << s; multiplication is unnecessary. All masks, counters,
indices, payload values, and effective addresses fit in a word by the stated
bounds. This proves both semantics and the instruction bound. ∎

`streaming_affine.py` is an executable fixed-program model. Its macro costs are
upper bounds on `Lax13.Ram` expansions, rather than a claim that Python runtime
measures Word RAM time. The model is not itself a Lean proof or a complete
emitted `Lax13.Ram.Program`; resolving macro labels in such a compiler remains
an integration task.

## Theorem 2: all quadratic Gaussian phases in linear streaming time

Let a_j be in Z/4, and let B be a symmetric binary r-by-r matrix with zero
diagonal. Define

    q(x) = sum_j a_j x_j + 2 sum_(j<k) B_jk x_j x_k  (mod 4).

Suppose the r columns of B are packed as r-bit words. All N phases q(x), in
ordinary binary x order, can be generated in O(N + r) Word RAM operations with
O(r) metadata and O(1) scratch words. There is no parity instruction, population
count, right shift, word multiplication, or word division in this algorithm.

Proof. Maintain q(x) and the packed gradient g = B x over F_2. Initially x = 0,
q = 0, and g = 0. When coordinate j flips, its old value is x_j. Let

    d = (a_j + 2 g_j) mod 4.

The new phase is q+d if x_j = 0 and q-d if x_j = 1, modulo 4. Indeed, only the
linear term at j and quadratic terms incident to j change. Their total forward
difference is a_j + 2 sum_(k != j) B_jk x_k. Replacing the sum by its parity
changes the result by a multiple of 4. The reverse difference has the opposite
sign. Update g by XORing column j of B. The zero diagonal ensures that the
old g_j supplies the incident-term sum used in this update.

Read g_j by AND with the same bit mask already used by the binary increment;
branching on zero avoids extracting a numeric bit. Load a_j and column j using
j as an address offset. Reduce a_j+2 by AND with 3. For reverse differences use
(q+4-d) AND 3, whose subtraction never underflows. All these are constant-many
word instructions when w >= 3. There are T < 2N bit flips by Theorem 1, and the
metadata initialization takes O(r) instructions. The phase and gradient
invariants therefore prove the result. ∎

## Theorem 3: exact monomial Clifford action on limb records

Let each coefficient be a pair of integers (u_x,v_x), represented modulo
2^(kL) by L little-endian limbs of k bits, where 1 <= k <= w-2. For invertible
A, offset b, and q as above, the map

    (u+iv)_x -> i^q(x) (u+iv)_x at index A x XOR b

can be evaluated by a uniform additive/Boolean Word RAM in O(NL + N + r)
operations, preserving the source, using two disjoint padded output buffers
and O(r) metadata words. All real/imaginary source and destination buffers and scratch cells must fit together below 2^w. This statement uses precomputed A,b,a,B metadata.

Proof. Theorems 1 and 2 maintain the destination index and phase in constant
amortized work per coefficient. Multiplication by i^q uses only a swap of the
real/imaginary destinations and zero, one, or two integer negations:

    q=0: (u,v); q=1: (-v,u); q=2: (-u,-v); q=3: (v,-u).

To negate an L-limb residue, complement each digit within base beta = 2^k and
add a carry initially equal to 1. At digit a, form beta-1-a+carry; store its
residue modulo beta and set the carry to 1 exactly when this value is beta.
Every temporary is at most beta, hence fits in a word; each digit takes
constant-many instructions. The standard radix identity proves this is
negation modulo beta^L. Copying, swapping destinations, and up to two such
negations take O(L) instructions per coefficient. The disjoint-buffer argument
from Theorem 1 proves the frame property. ∎

The residue width here is exactly kL bits: no unmasked partial top limb is permitted. If a caller starts with B bits not divisible by k, it must pad to kL and establish the signed interpretation at that full width, or supply a separately proved top-mask operation.

If the intended coefficients are signed integers strictly between
-2^(kL-1) and 2^(kL-1), interpret the residues by signed decoding. Negation and
Gaussian-unit phases then agree with ordinary integer arithmetic, provided the
endpoint excluded above does not occur. In fact, an absolute-value headroom
bound is invariant under these phases. This does not justify arbitrary
finite-precision rounding or multiplication by roots other than Gaussian units.

## Theorem 4: uniform metadata compiler, with global phase retained

For a word of m gates from X_j, S_j, Z_j, CNOT_(j,k), SWAP_(j,k), and CZ_(j,k),
there is an exact uniform metadata constructor using O((m+1)(r+1)^2) Word RAM
operations and O(r) words of live metadata. It returns A,b,c,a,B such that

    literal_word |x> = i^(c+q(x)) |A x XOR b>.

The exponent c is retained modulo 4, including global phase; it is not discarded
as physically irrelevant. The combined metadata compiler and streaming evaluator
therefore costs O((m+1)(r+1)^2 + NL). This is a fully specified sufficient
construction for monomial segments, not an assumed metadata oracle.

Proof. Initially A is identity, b=0, c=0, a=0, and B=0. Maintain the stated
identity after every appended gate. X_j toggles bit j of b. CNOT_(j,k) toggles
bit k in every affine column whose bit j is set, and does the same to b. SWAP
swaps those bits in every column and in b. These update the output affine map
without changing the phase polynomial.

For phase gates, write output coordinate j as b_j XOR u dot x, with u the
j-th row of A. Its value modulo 4 is

    b_j + (1-2*b_j) sum_l u_l*x_l
        + 2 sum_(l<t) u_l*u_t*x_l*x_t.

This follows from the parity expansion modulo 4: terms of degree at least 3
have coefficient divisible by 4. Appending S_j therefore adds b_j to c,
(1-2*b_j)*u_l to a_l, and toggles B_lt when u_l*u_t=1. Appending Z_j adds
2*b_j to c and 2*u_l to a_l, with no quadratic change.

For CZ_(j,k), let u,v be rows j,k and let their offsets be b_j,b_k. Since
this gate contributes twice the product of those output bits, compute the
product over F_2. Its constant is b_j*b_k; its linear coefficient at l is

    b_j*v_l XOR b_k*u_l XOR u_l*v_l;

its coefficient at x_l*x_t, for l<t, is

    u_l*v_t XOR u_t*v_l.

Add twice the constant and linear coefficients to c and a, and toggle the
corresponding B edges. These exact formulas preserve the invariant.

Each affine gate takes O(r) word work and each phase gate O(r^2) work. Store
A and B by their r packed columns and a by r words. Bit tests require only
AND with a left-shifted mask and a zero branch; the Python reference's use of
right shifts for readability is not an additional machine instruction premise.
All mod-4 signed updates can use an added constant before truncated subtraction,
then AND with 3. Initializing the metadata is O(r) work. Thus the stated bound
holds. Symmetry and zero diagonal of B are maintained by toggling both endpoint
bits for each unordered pair. Gate-by-gate induction proves correctness. ∎

Theorem 2 extends to c+q by initializing its phase to c instead of 0. Theorem 3
then evaluates the result from this compiler with the same asymptotic count.
`monomial_metadata.py` contains this constructor and an independent literal
basis-state gate interpreter. It rejects H explicitly, because Hadamard leaves
the monomial class. Its replays include a control requiring the nonzero global
phase of X followed by S to remain present.

## Direct scope for the integer multiplication port

These theorems cover binary-linear coordinate relabelings, XOR translations,
and quadratic Gaussian-unit phase diagonals: the monomial Clifford layer.
A monomial is NOT an arbitrary symplectic/Fourier transformation. Hadamard and
nonmonomial Fourier kernels still need their own numerical execution and error
bounds. Likewise, a pre-existing long gate word must actually be compiled to
this metadata and its compiler cost charged before the theorem can replace it.

If a transfer contains m separate permutations of the same L-word coefficient
records, executing them separately costs O(mNL). Composing their metadata and
then materializing once costs O(NL + composition cost), provided intermediate
stages do not observe or modify the intermediate layouts. This is a sufficient
fusion rule, not permission to skip paid transforms across intervening ADDs.

This gives a concrete RAM-specific port component beyond generic Turing-machine
simulation. It does not imply a superior κ. The richer log-RAM model with word
multiplication already has O(n)-time multiplication results, with n denoting
input bits; comparison with such results must name the instruction model and
input/output representation. See Fürer (2014), Theorems 4.1 and 4.2:
https://arxiv.org/html/1402.1811v1 .

## Reused project facts and evidence limits

* `Problem18RAMLax13Ram20261001.lean`: `Lax13.Ram.Instr` and the uniform
  bounded-word/indirect-memory semantics; macro expansions for XOR and MOV.
* `MpLimbs20261007.lean`: `lv`, `lv_dig`, `addCode`, `add_run`, `mapCode`,
  `map_run`, `copyIn_run`, `copyOut_run`, `compileC_sim`. In particular,
  `add_run` gives exact limb addition in `40*L+20` IMP steps under explicit
  array frame, operand, and no-overflow premises. These are predecessor facts,
  not discoveries of this deliverable.
* `Problem18TensorGatherRefinement20261002.lean`:
  `parameters_at_entry`, `cells_tensorCoordinates`, `tensor_gather_run`, and
  `source_tensor_gather_run`. All six tensor coordinate orders have literal
  serialized semantics; the concrete gather bound is `210*(a*b*c*e+1)` IMP
  steps. The new affine primitive generalizes the relevant binary-coordinate
  layout operations, while supplying a separate amortized accounting argument.
* `MpSparse20261007.lean` and `Problem18RAMRootLog20261007.lean`:
  `tdWidth`, `allFormatRootRAMLog` provide the existing trans-dichotomous
  short-word route. Its stated runtime is polynomial with unspecified degree,
  so that theorem alone does not transfer the multiplication exponent sharply.
* `Problem18Lax13BitCost20261007.lean`: `runCost_le` and `runsTo_bitCost`
  give bit-cost accounting for existing bounded-word runs. This is an abstract
  instruction charge, not an independently implemented gate-level simulator.

The project sources above were read and SHA-256 pinned; no Lean process was
started here, so these citations are current-source inspection, not a fresh
kernel/axiom audit. The shared source/DAG lexical query for `WordRAM` found the
registered external `formal-math-3sum-apsp` collection; a precise query for
`Problem18RAMRootBitCost` returned no entries although that source is present.
No claim of complete current-source DAG coverage is made. The root team is
reconciling whole-catalog coverage separately.

The affine enumeration, radix arithmetic, and quadratic phase identities are
standard mathematics. The contribution is a concrete sufficient interface and
cost proof for this port, with executable replays, rather than a claim of
historical priority for those identities.
