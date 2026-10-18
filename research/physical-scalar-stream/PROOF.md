# Sequential scalar packets with fixed local word roles

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement sequential access and local lifetime around PR3078's literal
scalar recipes. I retain PR3090's conditional capacity argument and PR3091's
signed tape arithmetic. Nick Petalas supplies the guarded reversible Boolean
caller in PR3094. I use the inherited unit-step tape model,
including charged writes and erasure; I coordinate that distinction in the
linked claim and do not claim his circuit or whole-caller result.

## 1. Compiled program and input contract

Compile a finite catalogue of at most 96 ADD/SCALE literals before numerical
input. Each literal includes its original integer numerator/denominator and
one of the inherited scratch, source-walk or target-walk policies. I retain
negative-denominator spellings. The frozen lowerer limits the reduced
numerator magnitude to 255, the dyadic denominator to 4096 and the recipe
to at most I=32 instructions per real component. I also bound the original
literal integers before compilation.

The instruction alphabet is signed ADD, COPY, CLEAR, NEG, DOUBLE and HALF
on local ports 0=target, 1=source, 2=initially-zero scratch. Binary operands
must differ. I check the inherited symbolic macro identity and require a
formally zero COPY destination at each compilation prefix. This is the COPY
contract used by PR3090's integer interpreter.

Supply canonical Count tapes for component width h>=2 and Gaussian count
N>=1, and complete aligned target/source streams at their local origins.
Each Gaussian value occupies h real bits followed by h imaginary bits,
least significant bit first in signed two's-complement notation. Use one
common caller-supplied grid. Write V=2hN for each operand's length.

ADD receives distinct target/source streams. SCALE has no source operand;
I use logical zero for its unused local source role. The input and protected
output ports are distinct. The caller supplies matching component order and
frame/scale interpretation. Equal lengths alone do not establish alignment.

On success I preserve borrowed inputs and descriptors, return the complete
target output at its origin, and erase owned work and markers. The caller
consumes that protected output before selecting another compiled recipe or
reusing the engine. I guarantee cleanup for the named arithmetic/contract
errors below on otherwise admitted input. I do not promise rollback for
arbitrary malformed extents or interruption.

## 2. Execute the literal unit instructions

I keep the three local words, one work word and one constant-zero word at
exactly h bits. I never normalize signed words as unsigned Counts. I retain
high zero bits and distinguish a logical h-bit zero word from blank storage.

For ADD and subtraction I use PR3091's encoded-width finite-carry routine,
including its extra sign-bit check. For NEG I apply the same subtraction
routine to the constant-zero word and the target. Its guard excludes the
most-negative input whose negative cannot fit. The routine preserves its
input words and writes the candidate result into the work role.

For DOUBLE I emit a low zero and the first h-1 source bits. I require the
discarded old sign bit to equal the preceding bit, which becomes the new
sign. This is necessary and sufficient for signed multiplication by two to
fit the original width. For HALF I require the low bit to be zero, emit the
remaining h-1 bits, then append the old sign. This gives exact signed division
by two at the same width and on the same grid.

COPY first scans its destination and requires h zero bits, then copies h
source bits. CLEAR writes h actual zero bits. For each non-CLEAR instruction
I clear the old target body, copy back the h-bit work result and clear the
work body. I retain active leases during these body resets. Each operation
returns the local word heads to their origins.

Induction over a fixed recipe gives its exact signed integer microstates
whenever the guards succeed. I preserve literal order. For example, SCALE
(-1)/2 executes NEG before HALF and rejects the most-negative input even
though its final mathematical half-negative would fit. A target walk may
overflow at DOUBLE and later return to range; the earlier failure still
rejects the call. Final endpoint representability cannot replace these
prefix conditions.

## 3. Interchange the component and instruction loops

Each unit operation acts within one real component and has no access to a
different record or component. I can therefore execute a complete recipe on
component 0, then component 1, and so on, instead of allocating full packet
registers and traversing the packet once per instruction.

For each of the 2N components, `ScalarEngine.run` loads its target word and
its source word, or a zero source for SCALE. I initialize the local scratch
and constant-zero word. I execute the compiled recipe, require scratch to
equal the h-bit zero word and check the local source's restoration. I append
the completed target word to the protected output, then erase all five local
word bodies before advancing the encoded component counter.

The inherited symbolic recipe certificate supplies, for arbitrary t,s,

    ADD:   (t,s,0) -> (t+q*s,s,0),
    SCALE: (t,0,0) -> (q*t,0,0).

The unit refinement and induction over components lift these identities to
the full Gaussian packet. The source, target and scratch may have correlated
values; I need no independence assumption. Processing real and imaginary
components at different times preserves the componentwise bounds in PR3090.
No other macro observes this invocation until its complete return.

This loop interchange permits one h-bit scratch word. Unstarted components'
logical scratch values are zero, and completed components' scratch values
are zero again. A unit instruction never requests another component's
scratch, so I need not materialize an entire zero packet. I still charge
initialization, checks and erasure for each component.

## 4. Borrowed source and local restoration

I load every ADD source component into owned register 1. A source walk writes
that private word. It never writes the borrowed source stream. I nevertheless
execute the inherited inverse shifts and check that register 1 returns to
its initial value before disposal.

After loading a source component the borrowed cursor lies immediately after
it. `restored_source` moves back exactly h cells, compares those h cells with
the local source word, then advances exactly h cells to resume the input.
It never rereads an earlier component or decodes a packet offset. This check
costs O(h), not a scan of the preceding packet prefix. At the end I require
both borrowed streams to be exhausted and rewind them to their origins.

PR3090's source-write count describes logical port 1. In this implementation
those writes target the private component copy; they do not count writes to
the borrowed physical input. Target-walk recipes retain their logical
read-only-source property, while both policies use the same charged input
and return convention here.

For nested calls I suspend the parent allocation scope and pass physical
`borrowed_tape`/`borrowed_count` views. I resume the parent scope after return,
copy the protected result into a parent lease, then clear the scalar output
and marker. I test this exchange with live parent Counts and payload leases.

## 5. Complete cost and storage

Each unit instruction costs at most K_op*h for a fixed constant K_op,
including arithmetic, result replacement, rewinds and clearing. ADD/NEG
use finite carry; HALF/DOUBLE use fixed-width scans. COPY includes its
zero-destination check; CLEAR includes h writes. Counter initialization
costs O(log h), which the subsequent complete traversal pays.

Outside the I unit instructions, each component incurs O(h) for input loads,
the private source copy, zero initialization, source/scratch checks, output
append and local disposal. The encoded 2N counter costs O(N+log N) over its
full traversal. Initial/final input and output head restoration costs O(V).
Thus, including I=0, I obtain

    T_macro <= K*(I+1)*V, V=2hN.

K is uniform in h,N and the admitted data; the compiled catalogue and source
preparation contribute fixed costs outside numerical execution. The code
does not decode h or N into host loop bounds. Its host-side register indices,
instruction lists and policy tags belong to the compiled finite vocabulary.

For multiple macro invocations I sum `K*(I_j+1)*V_j`. If h and N are common
through PR3090's covered scalar subsequence, I obtain

    O(hN*(U+9992)), U=57710,

where U counts instructions for both real components. I retain caller
alignment, routing and other excluded operations as additional obligations.
This upper bound does not establish a `7072*hN` time saving. Such a comparison
needs opcode-specific constants, actual widths and identical entry/return
conventions for both policies. PR3078's 9,760 count covers a different interval.

The code needs at most nine live pool leases: three persistent Count/Counter
roles (`two`, `components`, `remaining`), five word roles, and one temporary
Counter during a word operation. Literal-constructor duplication occurs
before the five word roles exist. I preallocate 128 scratch tapes and one
protected output before numerical input.

Local occupied contents satisfy

    5h+O(log N+log h+128)=O(h+log N).

Add the V-bit protected output and two borrowed V-bit inputs for ADD, or
one borrowed input for SCALE. No pool role holds a complete packet. Fresh
backing has the same local asymptotic bound because pool capacity is fixed.
Reused roles retain their historical maximum extent: erasure blanks cells
without shrinking the simulator's backing arrays. Neither N nor I multiplies
the number of physical roles. I keep simulator counters and Python object
bookkeeping outside the tape program's numerical control.

## 6. Named rejection and conditional capacity

`ScalarContractError` subclasses the inherited `CoefficientDomainError`.
The enclosing handler therefore covers inexact HALF, signed overflow,
nonzero required scratch and failed local source restoration. The unit
routine clears its partial work word. The engine rewinds borrowed inputs,
clears its five word roles, closes Counts/Counters, checks the empty pool,
erases markers, closes the invocation and erases any partial protected output
before rethrowing. This costs O(V+h+log N) beyond completed work and preserves
borrowed contents and descriptor heads, including a late-component failure.

PR3090 proves a conditional D=7, h=P+20 capacity for its actual correlated
prelude/A rows and frame hypotheses, P>=3. Its strict bound is
`4896*128=626688<2^20`. I inherit that argument as a capacity premise and
match its literal unit checkpoints. I do not assign its 84-bit guarantee
to arbitrary 84-bit operands. I do not repeat its normalized-row audit or
claim actual residual adapters, centres or native/recursive interiors here.

## 7. Source binding and finite evidence

I authenticate the unchanged PR3090/3091 archives before import, preserving
their nested source notices. The binding checker recompiles both frozen
provider words, checks inherited program hashes, extracts the prelude/A
scalar events, and compares the recipe hashes/counts with PR3090's receipt.
I omit its capacity propagation and frame census.

Each of the four streams has 9,992 scalar macros and 29 literal templates;
the union has 31. Scratch, source-walk and target-walk counts are respectively
32,391, 28,855 and 28,855 instructions per component. The two providers share
those literal programs but have different canonical frame payloads. Template
equality does not establish identical physical entrance values.

I execute all 31 templates under all three policies on complete seven-value
84-bit Gaussian packets. A separate integer interpreter checks each recipe
prefix, exact division and signed fit. I also exhaust 4,440 small-width
ADD/SCALE cases and check 612 HALF/DOUBLE cases through width 65.

The event-109/110 fixture composes the actual literal SCALE(-1/2) and
ADD(+1/2) programs on aligned test packets. I do not reconstruct the original
632-input prelude values in that fixture. Further checks cover later-field
rejection, valid policy retry, nested parent return and eight injected
source/shift/scratch/ownership failures. Finite evidence complements the
quantified refinement; I claim no formal machine or independent human review.
