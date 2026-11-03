# Direct return after an initial ONE

## Exact contract

Use the eleven source objects in SOURCE-PINS.json. The baseline decrement is
Nick Petalas's PR6495 cached-borrow routine. The entry is a positive canonical
private Counter: head at its first digit, LEFT at0, little-endian binary x>0,
RIGHT after the significant digits, blank exterior, and finished=False.
Allocated cells beyond RIGHT may remain from padding or an earlier larger
value. Their contents are BLANK; allocated length need not be minimal.
Constructor and close are unchanged. This is a source logical-tape contract,
not equivalence on arbitrary malformed heads or data.

After the shared initial digit read, the new routine specializes ONE:

    write ZERO; step right; read the next symbol;
    if it is RIGHT: set finished=True;
    step left; return.

The initial-ZERO branch retains the entire cached-borrow body literally.
Only fixed-symbol/boolean control is used. No numeric head, length, runtime
cardinality, extra tape, new alphabet, or unbounded host state is introduced.

## State equivalence and the zero boundary

For even x the initial digit is ZERO. The new branch performs no tape operation,
and the baseline path follows on the same digit and tape. Thus its entire
primitive trace, final cells, head and finished flag are unchanged.

For odd x the initial digit is ONE and no borrow movement has occurred. The
common write changes that first digit to ZERO, and the following step/read
places the head exactly at the second cell. If x>1, another significant digit
exists, so this cell is not RIGHT. Subtracting one leaves the same width and
all other cells unchanged. The baseline rewinds; the new single left step
returns to the first digit. Both leave finished=False and identical cells.

If the second cell is RIGHT, canonicality and positivity force x=1. The new
routine leaves ZERO at1, the existing RIGHT at2, and every higher allocated
cell unchanged, sets finished=True and returns to1. The baseline temporarily
blanks RIGHT, moves to LEFT, then rewrites the already-zero digit and RIGHT
before rewinding. These writes extend no backing allocation: both cells
already exist. Therefore the final entire bytearray, its length, head and flag
are identical, including after a larger counter has shrunk to1.

The source constructor normalizes high padding by changing delimiters and
blanking old cells without shortening the backing array. The unchanged even
path handles width shrinkage. Induction consequently preserves the stated
whole-array invariant, rather than just the decoded number. N=0 is constructed
finished; decrement still rejects before reading, and close is unchanged.
Identical final states make all constructor/disposal traffic identical too.

## Exact local and complete-countdown traffic

In the pinned ABI each read, write and unit step increments its own meter.
Tape.rewind first steps left, reads/moves until LEFT, then steps right.
For odd x>1, the baseline's rewind from the second cell has two reads and
three moves. The direct return has no reads and one move. The saving is

    (reads,writes,moves) = (2,0,2).

At x=1, all work after the common write/step/read consists in the baseline of
three reads, three writes and seven moves. The new work is one left step.
Its saving is (3,3,6). Even x saves (0,0,0).

A countdown from N>0 encounters c=ceil(N/2) odd positive values, exactly one
of which is1. Including unchanged constructor and disposal, the additional
saving relative to PR6495 is therefore

    (2c+1, 3, 2c+4),       total 4c+8.

N=0 saves zero. This is in addition to PR6495's credited N-read saving relative
to the older uncached algorithm. No repeated claim to that saving is made.

Arham Tahir/PR2877's complete invoice, as cited by6495, gives for input digit
width d>=max(2,bit_length(N)) the6495 total14N+14d-5popcount(N)+36 for N>0.
Subtracting the new proved trace difference yields

    14N+14d-5popcount(N)+28-4ceil(N/2),   N>0.

The cited zero invoice14d+40 is unchanged. These scalar invoices inherit the
predecessor's exact model and range; they are not a new independent audit of
that earlier total. The new vector difference does not rely on its formula.

## Complete retained sign caller

The literal source sign_address has M>=2, B>=1 outer rows, and S>=1 suffix bits.
Replace the method on the common Counter class reached by every imported alias.
State equivalence above preserves every caller decision, input value, payload
copy, source position and cleanup. Only private-counter primitive counts differ.
In particular, unchanged word/Arena arithmetic is not treated as free.

Its inventory is one counter of valueB, two counters of valueM-2 per row,
one counter of valueM-1 per row,4B(M-2) counters of valueS for source moves,
and BM more valueS counters when S>1 for payload copying. At S=1 the literal
one-bit shortcut allocates none of those final suffix counters. At M=2 the
zero block counters are still constructed/closed and save nothing.

Define

    K = B(4(M-2)+M*1_{S>1}),
    P = 1+B+2B*1_{M>2}+K,
    C = ceil(B/2)+2Bceil((M-2)/2)+Bceil((M-1)/2)+Kceil(S/2).

P counts positive countdowns; C sums their odd positive steps. The exact
complete-call additional saving is

    (reads,writes,moves) = (2C+P, 3P, 2C+4P),
    total = 4C+8P.

This is an all-parameter trace substitution/inventory proof. Any unexecuted
full-caller scope is explicitly identified in README/VALIDATION; a formula
alone is not described as an observed complete-call replay. The oracle can
independently check the changed private-counter delta and inventory without
being a second complete implementation of unchanged Arena/Unsigned billing.

## Credit and limits

Nick Petalas/6495 owns cached borrow termination and its conformance; Arham
Tahir/2877 owns earlier full countdown/sign invoices; David Arias/2753 owns
linear sign; Jose Manuel/2697 owns Counter and the marked tape library. PR3611
has a different left-origin/top-digit return ABI and remains related context.
All copied source bytes and notices are retained; no author verifier is run.

The result is exact read/write/unit-move traffic under this source ABI. It
does not prove optimality, wall-clock speedup, a finite-state machine compiler,
current complete-supplier adoption, arbitrary dirty restoration outside this
contract, a native/precision/stock/tape/compiler/outer invoice or new kappa.
All five selected assumptions and frontier retain their status. Separate AI
implementation/review is not independent human or formal-kernel acceptance.
