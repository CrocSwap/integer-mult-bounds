# A pathwise inverse for the literal paired DDG

Fix `(a,b)=(1,1)` before reading any fair bits. Use exactly `make(1,1)` in
zxv's retained PR6072 source. It has 312 internal states `(p,j)`, phase
`p in Z/156`, and four tagged leaves. This note proves a logical clean
lifecycle for every **terminating** path. Probability and expected-draw
claims reuse the predecessor's product-law/depth-count argument; no physical
reversible machine or complete multiplier is asserted.

## 1. The actual transition is locally injective when phase and bit survive

At phase p let `d_i = floor(2*(w_i*2^p mod169)/169)`, for weights
`w=(144,12,12,1)`. Every digit is 0 or1. Put `D=sum_i d_i` and
`c_i=sum_{h<i}d_h`. For old node j and coin u, the source constructor forms
`q=2j+u`. It returns leaf i exactly when `d_i=1` and `q=c_i`; otherwise
it returns internal `(p+1 mod156, q-D)`.

Consequently, given p,u and the target, reconstruct q by:

* internal node j': `q=j'+D`, with the required next phase;
* leaf i: require `d_i=1`, then `q=c_i`.

Require `q mod2=u` and a valid old node `j=(q-u)/2`. This gives the unique
predecessor. The source stores leaves as `312+i`; internal IDs are the
lexicographic enumeration of `(p,j)`. The verifier checks this formula on
all624 literal source transitions and rejects the opposite bit for each.
No table regeneration at a neighboring residue pair is used as evidence.

Phase is essential at a leaf: source states0 and1 both return leaf0 with
coin0, but lie at phases0 and1. An overwrite retaining only leaf and coin
is not injective. Retaining p, or deriving it from the stopping counter,
repairs that collision. The known start phase alone does not repair it.

## 2. Complete transcript/controller lifecycle

Inputs are fixed parameters, an immutable binary tape, a known start cursor s,
and a disjoint two-bit accumulator A. The tape is initially independent fair
bits for the exact product-law assertion. Pathwise reversibility itself holds
for every binary tape having a finite terminating prefix. The caller owns
that resident transcript until cleanup ends; no tape cell is overwritten.

Owned call registers begin `(state,phase,t,cursor)=(0,0,0,s)` plus clean
scratch. A forward step reads the current tape bit u, performs the source
transition, increments phase modulo156, increments t, and moves cursor right.
The loop ends on its first leaf `312+i`, at random stopping time T. Thus
`phase=T mod156`, `t=T`, `cursor=s+T`.

Perform reversible output retention `A <- A XOR i`. The leaf remains in the
controller during this copy; the accumulator is not the sole cleanup record.
Then, while t>0, read the bit at cursor-1, decrement phase modulo156, and apply
the inverse from section1 to the current target and that predecessor phase.
Move the cursor left and decrement t. The forward relation checks that the
computed predecessor regenerates the target, enabling scratch uncomputation.

Induction backwards on t recovers the exact preceding controller on each
step. At t=0 it returns `(state,phase,t,cursor)=(0,0,0,s)`, with scratch clean,
tape unchanged and accumulator `A_initial XOR i`. Both the stopping counter
and owned phase register are cleared by this reverse walk. There is no
per-step state history and no retained final T. Storage of the counter during
the call is still necessary in this construction. Never stop reversal merely
on seeing state0: a surviving path can revisit phase0/root after156 steps.
The counter distinguishes that visit from the beginning. Phase wrap does not
invalidate the inverse formula or its induction.

To realize a single state update reversibly, compute the next state into a
clean nine-bit scratch register using an XOR oracle, swap state and scratch,
and erase the old state with the inverse XOR oracle while phase and coin are
still available. Reverse the two oracles for a backward step. Counter,
phase and cursor updates are invertible increments/decrements. The table
oracles extend to total reversible XOR maps, but cleanup correctness and loop
termination are claimed on the valid-path invariant only. The Python verifier
is an exact reference interpreter, not itself a bit-level reversible circuit.

## 3. Costs that this construction does and does not pay

The chosen realization keeps nine state bits, nine scratch bits, eight phase
bits, O(1) bounded lookup/work flags, and `ceil(log2(T+1))` stopping-counter
bits at maximum occupancy. The cursor and known start address belong to the
tape interface; a numerical address implementation must additionally pay its
address storage/arithmetic. The consumed T bits remain resident throughout;
no new per-step state log is stored. There is no finite worst-case T or
worst-case storage bound. Counter allocation itself is a physical obligation;
the space expression describes occupied logical bits, not a free allocator.

Precisely T forward and T reverse transitions and one two-bit XOR retention
are required, with 2T accesses to the resident transcript. There are T cursor
moves in each direction. From the retained source,

`E[T]=9960277917013927549978/4649714690825496825793 < 9/4`.

Thus expected traversed transitions are `2E[T] < 9/2`; cleanup doubles the
logical traversal count but draws **no new randomness**. It does not make the
T used random bits independent of the retained result.

An explicit conditional implementation can scan every one of the624 edge
records for each oracle, XORing the target or predecessor under equality of
its key. Store source phase alongside each record (or compute it with a paid
fixed decoder). At most two scans implement each reversible state transition,
so forward-plus-reverse uses **2496T record visits**. This is a deliberately
conservative concrete lookup tariff, not a free RAM assumption. It requires
paid reversible equality/XOR/scan movement at the fixed record widths. The
original5616-bit packed target table does not include these phase records,
scan positioning machinery, or controller scratch: storing an eight-bit phase
per edge adds4992 bits in this simple layout, for10548 data bits total, before
any physical routing/control overhead.

If a record visit costs K and counter update at occupied length ell costs
C(ell), the additional conditional bill is `2496KT + O(T*C(log(T+1)))`
plus tape movement, addressing, phase updates and one output copy. With a paid
ripple-style increment/decrement tariff C(ell)=O(ell), counter work is
O(T log(T+1)); this is not charged as constant time. The source bound
`Pr(T>k)<=3/2^k` ensures finite expectation for that polynomial-logical work,
but a bounded physical tariff is not supplied by the Python experiment.
No runtime speedup follows from expected fair-bit savings alone.

## 4. Quantifiers and remaining boundaries

The inverse algebra applies to any binary-digit DDG with this same ordered
leaf allocation, subject to its valid-node recurrence. The source binding,
resource counts, path fixtures and exact mean here cover only `(1,1)`;
all144 denominator13 configurations are deliberately not replayed.

A fresh call after this cleanup may not treat the restored consumed bits as
fresh conditional randomness once the output is retained or used adaptively.
The proof restores the original tape, not its independence from outputs.
Actual reached residue pairs, nonadaptive batching, overflow, table selection,
physical random-bit/tape service and outer error bounds remain open. No
selected frontier, deterministic inverse, supplier admission or framework
assumption is changed. No formal proof-kernel or independent human review is
claimed.
