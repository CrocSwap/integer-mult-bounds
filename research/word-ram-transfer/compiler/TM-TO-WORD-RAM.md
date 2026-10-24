# A constructive multitape-to-Word-RAM transfer

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## Exact scope

This is a classical simulation argument specialized to the project's actual
`RamStd` semantics, with an executable finite-program compiler and an independent
multitape interpreter. It is not a new RAM multiplication record. It transfers a
complete conditional multitape multiplication theorem, with all of its assumptions,
to a restricted logarithmic-word RAM. It does not discharge any missing theorem
in that antecedent or introduce unit-cost multiplication of arbitrary integers.
No Lean verification of this compiler is claimed.

The target is `Mathproof/Meta/RamStd20261007.lean`:
SHA-256 `7c9263a14360b7fe485a753bda9c35c408b768612538d092f0dff217aa4f597e`.
Memory includes register cells, starts identically zero, and all written values
and memory addresses are reduced modulo 2^w. `sub` is natural truncated
subtraction. A program is a fixed finite list; labels/program counters are
natural numbers, not memory words. `read` at EOF and `halt` return `none`;
`write` appends one word. Every successful instruction costs one word operation.
The executable compiler uses exactly this subset:

    set load store add sub and jlt jzero jump read write halt

It uses no multiply, divide, remainder, high product, wrapping subtraction,
randomness, hash table, unit-cost arbitrary-precision field element or oracle.
It even avoids shifts. The parent package separately considers packed tapes.

## Theorem 1: uniform finite compiler, arbitrary tapes and both directions

Fix positive integers k, A and Q. Let M be a deterministic k-tape machine with
alphabet {0,...,A-1}, blank 0, states {0,...,Q-1}, initial state 0, and a partial
transition table

    delta : (state, k read symbols) -> (next state, k write symbols, k moves),

where each move is -1, 0 or +1. A missing transition means genuine halt without
changing the configuration. Tape cells are indexed by all integers. Initially
all heads are 0, tape i has a supplied finite word t_i at nonnegative positions,
and all other cells are blank. Choose an output tape o in {0,...,k-1}; the output
protocol requests positions 0,...,m-1 of that tape at halt.

There is an explicitly computable fixed finite `RamStd.Program` P_M, independent
of the input lengths, time bound, actual execution and word length. Write
N = sum_i |t_i| and let T be the number of actual M transitions before halt.
Let R be the least power of two strictly larger than 8+3k, and set

    B = 2R + 4(k+1)(N + T + m + A + 2),
    C = 100(k+1)(A^k + 1) + 20(k+1)^2.

For every word length w with 2^w > B, P_M halts with exactly the m output
symbols in at most

    C(T+1) + 10(N+m+k+1)

successful instructions. All accessed addresses are below B; at most B memory
words are used. More sharply, its live tape-address envelope is
R + 2k(N+T+m+2)+k and its register region has 8+3k words. For every nonhalting
run, every finite prefix that satisfies the same address bound is simulated
faithfully; the compiler does not introduce a spontaneous halt.

Input ABI: the usual outer list-length header, followed by

    [m, |t_0|, t_0..., |t_1|, t_1..., ..., |t_(k-1)|, t_(k-1)...].

Each header and symbol fits under the displayed bound. The program consumes
exactly this valid prefix and never attempts an EOF read. An external caller may
omit the outer header with a fixed one-instruction prelude change.

### Construction and proof

Let pi(z)=2z for z>=0 and pi(z)=-2z-1 for z<0. This is a bijection Z -> N.
Store tape i cell z at the address

    addr(i,z) = R + i + k*pi(z).

Different tape/cell pairs are disjoint: reduction modulo the positive integer k
recovers i, and then injectivity of pi recovers z. All such addresses are at
least R, whereas every register address is below R. Computing this address
requires setting R+i and adding the head-index register to it k times; k is a
fixed machine constant. There is no multiplication instruction.

Store u_i=pi(head_i) in register 8+i; use the next k registers for addresses,
the next k for read symbols, and registers 0,...,7 for zero, one, two, one
scratch value, a counter, stride 2k, output length m, and parity. Zero and all
heads are initially available from the specified zero-initialized memory.

The input loop places t_i[j] at R+i+2kj, using a stride register initialized to
2k. A guarded counter guarantees that each input symbol is consumed and stored
once. No clearing pass over untouched cells is necessary: the actual target
machine starts with zero memory, agreeing with blank 0. This is a stated
machine property, not uncharged initialization of arbitrary dirty scratch.

At each state-labelled code block the compiler computes all k current addresses
and loads all k read symbols before writing any tape. It dispatches over the
finite alphabet tuples. Equality of x to a constant s is tested by setting a
scratch word to s and rejecting if x<s or s<x. A transition's k writes use the
saved addresses; hence simultaneous TM reads/writes and possible cross-tape
coordinate coincidences are correct. The known next state is a direct jump to
its fixed code label. A missing transition jumps to the output loop.

For each head, parity is obtained by `and` with 1. The exact update formulas are:

| Current u | Right move | Left move |
|---|---|---|
| u even, u=0 | 2 | 1 |
| u even, u>=2 | u+2 | u-2 |
| u odd, u=1 | 0 | 3 |
| u odd, u>=3 | u-2 | u+2 |

They follow by substituting z in the definition of pi, separately for z>=0
and z<0. All subtractions are guarded by positivity and therefore coincide
with natural `sub`; no unsigned underflow occurs. A stationary head changes
nothing. In particular neither negative head positions nor a crossing of zero
requires a supplied origin offset or a time horizon.

The loop invariant at a state label q is:

1. the label is precisely M's state q;
2. each head register equals pi of the corresponding signed TM head;
3. for every i and every z in the finite proof envelope |z| <= N+T+m+1, the RAM tape cell at addr(i,z) equals the TM tape symbol;
4. all symbols and live registers are below 2^w; register and tape cells are
   disjoint, so temporary register changes do not alter any tape symbol.

The address bound below ensures injectivity after modular reduction on this finite envelope. No claim of an injective embedding of all of Z into finite-word RAM is made. The input loops establish the invariant. The all-reads-before-writes discipline,
the dispatched literal table entry and the head formulas preserve it for one
complete macro step. Induction proves it for every finite transition prefix.
The missing-table branch occurs exactly when M has no successor. The output
loop reads the requested m positions with stride 2k, appends them in order,
and reaches a real `halt` instruction. This proves exact output and genuine
halting. A malformed ABI is outside the theorem; no correctness guarantee is
claimed for a missing header or invalid symbol code.

At prefix time t<=T, every visited head satisfies |head|<=t. Initial occupied
coordinates are below N, and output coordinates are below m. Consequently all
needed addresses, including the loops' one-past-end pointers, are bounded by
the stated envelope. Each intermediate address is a monotone sum toward that
bound. Symbol values are <A; input/output counters are <=N+m, and head codes
are <=2T+1. The larger B bounds these quantities and all constants. Thus reduction
modulo 2^w never changes any intended address or value. This argument also proves
correctness at every larger word length, without inspecting w.

A state read phase costs k(k+2) instructions. The finite dispatcher costs at
most 3k A^k comparisons/constant loads plus a final transfer; writes cost 2k,
and each head update at most 10 instructions. These costs are bounded by C.
There are T transition phases and one final halt-detection phase. Input
initialization takes at most 6N+3k+6 instructions; output takes at most 6m+2.
The claimed envelope follows. The number of code instructions depends only on
the finite table (and selected output tape), never on N,T,m or w.

## Theorem 2: no time-horizon advice and logarithmic words

Suppose the same fixed transducer halts on every valid input of total symbol
length N, with output request m(N), in time T(N), where for known fixed integer
constants d>=1 and a>=1,

    T(N) + m(N) + N + A + 2 <= a (N+2)^d.

There is a fixed integer c depending only on M,a,d for which the compiler is
correct for every w >= c(floor(log2(N+2))+1), with the time bound of Theorem 1.

Proof: put L=floor(log2(N+2))+1, so N+2<2^L and L>=1. Then
B <= [2R+4(k+1)a] 2^(dL). Choose an integer e with
2R+4(k+1)a < 2^e and let c=d+e+1. For w>=cL we have
2^w >= 2^((d+e+1)L) > [2R+4(k+1)a]2^(dL) >= B.
The program neither receives a, d, T nor a guessed horizon. They appear only
in the sufficient word-size contract. A finite set of exceptional small input
sizes can be handled by fixed lookup code, or absorbed by a larger constant a
when their halting times are finite. No online word widening/restart is needed.

**Predicate warning.** The current unrestricted `RamStd.LogWordTime` definition
quantifies over all natural-number lists, including one-element lists containing
arbitrarily large values. Its separate per-entry fit requirement makes it the
wrong direct wrapper for arbitrary-value lists at logarithmic word length.
Use an explicit admissible binary/fixed-alphabet input predicate and the same
`RamStd.step` semantics, or prove a suitable encoded-input wrapper. Do not claim
that this theorem establishes that unrestricted definition for arbitrary lists.
The symbols, length headers and output words in the present ABI do satisfy the
word-fit contract. Input bit size is Theta(N+log(N+2)) for fixed nonempty tape
count and fixed-alphabet symbols under the usual at-least-one-bit-per-symbol
encoding, so replacing N by encoded bit size changes only constants.

## Corollary 3: whole-solution transfer, preserving every conditional kappa

Let H denote the explicitly retained analytic, native physical, exact recovery,
precision, scheduling, prime and uniformity premises of one pinned integer
multiplication theorem. Suppose H implies the existence of a single fixed
multitape machine multiplying two n-bit integers, emitting its usual nonnegative product as an MSB-first binary word of at most
2n digits at a known output-tape origin, followed by a blank or explicit
end marker, in

    O(n (log(n+2))^(1-kappa))

bit/tape steps, for 0<kappa<1. Then H implies a fixed restricted `RamStd` program
for the same multiplication task in the same asymptotic number of word steps,
using logarithmic words, and no multiplication/division instruction.

Proof: translate the two input strings and delimiter conventions into the
finite-alphabet ABI above, in O(n) steps. Use fixed symbol codes: blank 0,
logical bit 0 coded as 1, logical bit 1 coded as 2 (and a separate fixed end
marker if that is the antecedent's protocol). If a different finite alphabet
was used, injectively rename its symbols in the fixed transition table.
The antecedent's O(n log n) bound is bounded by a fixed polynomial envelope,
so Theorem 2 applies. Theorem 1 adds only a machine-dependent constant factor
and O(n) input/output work. The output ABI is handled by the explicit
posttransducer below, not by treating blanks as logical zeros or appending
zeros to an MSB-first encoding. Since
n(log(n+2))^(1-kappa) >= n, the O(n) overhead is absorbed. The compiler uses
no result of the multiplication it computes. It preserves the same kappa,
not a stronger one.

### Explicit fixed-width LSB output posttransducer

Define the new binary-word output ABI to be exactly 2n logical bits, least
significant first; its represented integer is sum_j b_j 2^j. The zero product
may have the usual one-digit representation `0` or an empty canonical
representation, provided the antecedent specifies which. Both are handled.
Assume the antecedent's conventional result prefix begins at position 0 of
its designated output tape. Its machine head at halt may be anywhere: the
RAM wrapper uses explicit simulated addresses and does not move that head.
Let the requested output width m=2n be retained in register M. Let a be an
address register, L a fresh/reused count register, S the constant stride 2k,
one the constant 1 register, z the constant 0 register, and x a scratch word.
The following finite labelled instruction sequence replaces the generic
output emitter; all operations are actual members of the displayed whitelist.

    set L 0
    set a (R+o)
    scan:
        jlt L M probe
        jump reverse
    probe:
        load x a
        jzero x reverse
        add L L one
        add a a S
        jump scan
    reverse:
        jzero L pad
        sub a a S
        load x a
        sub x x one
        write x
        sub L L one
        sub M M one
        jump reverse
    pad:
        jzero M halt
        write z
        sub M M one
        jump pad
    halt:
        halt

For an explicit nonzero end marker, put one additional constant equality test
before the three `probe` updates; its cost is constant per scanned symbol.
For the blank-terminated form displayed above the successful instruction count
is at most 14m+7. Scanning is bounded by m even when the actual result has m
bits and the terminating blank lies just beyond the scanned interval.

At the beginning of `reverse`, L is exactly the number ell of payload bits,
0<=ell<=m, and a=R+o+2k*ell. Every preceding payload symbol is 1 or 2. Thus
`sub a a S` addresses the preceding valid cell while L>0, and `sub x x one`
decodes exactly the logical bit. The reverse loop emits the MSB word in reverse
order: the genuine LSB-first payload. It decrements M once for each bit emitted;
its value on entering `pad` is m-ell. The pad loop emits exactly that many
logical zero words at the high-order end of the LSB representation. Therefore
it preserves the represented integer and emits exactly 2n logical bits.
The registers used here can be the original emitter's no-longer-live counters
and scratch registers, or a fixed number of additional reserved cells. All
pointers stay within the same finite tape envelope. This gives a concrete
linear posttransducer even if unused cells after the first terminator are dirty:
they are not read. It does require the predecessor's actual output prefix/
termination contract; an unspecified output encoding cannot be silently
interpreted.

The wrapper above is implemented by `compile_tm(..., output_mode="fixed_lsb")`.
The default mode and its raw-symbol ABI are unchanged. Its separate replay
checks 9,762 emitter cases against ordinary represented-integer semantics,
including 1,364 product pairs, zero/one/two/three, empty and leading-zero payloads,
full-width payloads without an end blank inside the cap, dirty cells after an
earlier terminator, and a word-size boundary fixture. A corrupted reversal
direction in the actual emitted program rejects; the wrong MSB-append
normalization also fails the integer-value check. This emitter emits bounded
binary words, and no multiplication instruction is introduced by these tests.
The displayed loop invariant is still the all-input proof, distinct from its
finite corroboration.

This is an implication from the complete fixed-machine theorem. A finite
native tableau replay, exact recurrence certificate or source-level pseudocode
alone is not such a theorem. For the selected and pending project claims, keep
all their existing conditional assumptions: this transfer does not magically
supply a missing finite-state implementation or validate their full analytic
argument. Uniform tables/setups that have already been paid as part of the
antecedent machine are simulated like every other step, not assumed free.

The entire old tape machine can therefore serve as a correct reference backend
for a new RAM implementation. A future RAM-native rewrite can replace a tape
subroutine once it proves its input/output/refinement contract and includes its
word costs; it need not redesign the algebraic recurrence simultaneously.

## Dependency disposition

- Finite native operator identities, residual/precision estimates, mixed-child
  inequalities, prime existence and exact recovery statements are mathematical
  propositions; their truth does not depend on a tape or RAM execution model.
- Tape movement/routing/stock schedules are executable-cost premises. The
  compiler transfers their actual tape execution unchanged at constant overhead.
  It does not grant random access for free inside a tape-derived invoice.
- A RAM-native replacement may eliminate scans, routing, transpositions or
  sequential descriptor work. Each such saving needs a new complete RAM invoice;
  it cannot be credited by deleting old terms from the scalar recurrence.
- Arbitrary-height exact scalar RAM providers are distinct from bounded-word
  bit RAM. Their coefficients and arithmetic must be bit-lowered or bounded
  before they can replace a subroutine in this restricted compiler.

## Finite verification

Run `python3 -I -O -B tm_to_ramstd.py`. The checker constructs actual finite
programs, interprets individual target instructions, and compares state, signed
heads and every relevant tape cell with a separately written signed-coordinate
TM interpreter at each macro boundary. Random cases include k=1,2,3, three
symbols, three states, partial transition tables, arbitrary source contents and
stationary/negative/positive moves. Directed tests cover both zero crossings,
long one-sided walks, empty-transition immediate halting, and multiple word
lengths. A too-small word contract rejects. Nonhalting finite prefixes are
checked without labelling them as halting computations. Tests do not establish
the universal theorem; the written invariant argument does.

## Open next questions

1. Prove the compiler invariant and finite-table code generation in Lean against
   actual `RamStd.step`, using admissible-input predicates rather than the
   unrestricted logarithmic word wrapper. First milestone: one transition with
   all k reads saved before the writes and modular-address non-aliasing.
2. Replace the one-cell-per-word representation with the parent packed-tape
   theorem; compare actual memory words and IO contracts, retaining this simple
   backend as an independent semantic reference.
3. Select one fully costed native project subroutine and implement its random
   access RAM version. First compare descriptor generation, precision and data
   motion in a complete invoice; only then optimize the global recurrence.

