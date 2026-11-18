# Fixed-tape execution of the half-sum CLEAR

This package gives a stored-program execution service for the exact circuit
in PR #7721. At signed width 1076, it uses 589841 unit data instructions,
5308569 program bits and 11206982 interpreter steps. This bill includes work
initialization, output copy, reverse computation, work retirement, all data
head returns and the full program scan and return. It is an execution upper
bound, not an optimality result. No new kappa is claimed.

## Exact entrance and exit

Let `w>=1`, `n=w+3`, and let `x0,...,x7` be arbitrary signed w-bit integers.
Put `N=x0+x1+x2+x3-x4-x5-x6-x7` and `q=floor(N/2)`. The service leaves each
donor unchanged. It XORs the low w bits of q into an arbitrary w-bit target.
It XORs `N mod 2 OR q<-2^(w-1) OR q>=2^(w-1)` into an arbitrary diagnostic.

There are 25 data tapes and one read-only program tape. Every tape uses the
same five symbols: `0`, `1`, `<`, `>` and blank. Data heads start on their
left marker `<`. Tapes 0 through 7 hold the donors, tape 8 holds the target,
and tape 9 holds the diagnostic. Each external bit block has a right marker.
The 14 tapes numbered 10 through 23 hold the seven successive result/carry
pairs, with lengths n and n-1. Tape 24 holds the four flags. The 15 work tapes
have a left marker and blank reserved cells at entrance. Their bit cells and
right-marker cells must return blank. All external markers remain unchanged.

The input program is the marked binary string in PROGRAM-1076.bits.gz for
width 1076, or the output of compile_tape for another width. Its head starts
on `<`. The interpreter has two temporary bits A and B, initially zero, and
a fixed finite decoder state. It returns both temporary bits and all 26 heads
to their entrance states. The program is unchanged. The program is an input
resource: this result does not implement its physical generation or loading.

The tape machine has a fixed number of tapes, a fixed alphabet and a
width-independent finite control. This is a classical multi-tape transition
model. No claim of transition-level reversible control is made. The specified
external XOR map is reversible, and the work and temporary data are restored.
This distinction is required before any use in an owned-erasure supplier.

## Source circuit and address layout

SOURCE-PINS.json binds all six unchanged source files and the source license.
The source README proves its complete arithmetic contract for every w. Its
range bound `abs(N)<=4*(2^w-1)` fits in signed n bits. Seven fresh ripple stages
compute N modulo 2^n; this is its exact signed value. Two top-bit comparisons
and two Boolean ORs compute the invalid flag. Copying bits 1 through w and
the invalid flag, then reversing the internal gates, restores every work bit.
The internal gates do not access the target or diagnostic.

The circuit allocates its wires in exactly the tape order above. Each wire
has one fixed tape and one fixed cell. Sign extension uses the donor sign
cell repeatedly; it does not allocate or assume extra input bits. The gate
controls and target are distinct. The compiler checks the complete address
range. It emits every move needed to reach each cell from the head's current
position. Thus gate lookup is not an unpriced random-access operation during
execution: the resulting program contains only unit physical operations.

## Instructions and interpreter

Each instruction has nine bits. The first four bits name one of ten
operations; the last five name one of 25 data tapes. Unused codes are invalid.
LEFT and RIGHT move that tape head one cell. XORA and XORB XOR the current
cell into A or B. FLIPA toggles the current cell when A is one. FLIPAB toggles
it when both A and B are one. INIT changes blank to zero, RETIRE changes zero
to blank, MARK changes blank to `>`, and UNMARK changes `>` to blank. The
four conversion operations require the stated input symbol. Each operation
is one multi-tape transition after the instruction has been decoded.

To execute a CNOT, read its control into A, visit and toggle the target, then
visit the control again and clear A. For a Toffoli, read both controls, toggle
the target, then visit the controls in reverse order and clear B and A. The
controls do not change. Thus each source gate has the same action, and both
temporary bits are zero at every gate boundary. This also covers controls
and targets on the same tape: each visit has its own emitted head movement.

For every work tape, initialization writes each zero, writes its right
marker, then returns the head. Execute the forward gates, output copy and
reverse gates. Return all data heads. Retirement removes each work right
marker, changes each restored zero to blank, then returns its head. Source
correctness and gate simulation prove the complete endpoint for all input
bits, including invalid numerators and arbitrary initial output bits.

One initial step moves the program head to its first bit. Each of L
instructions uses nine read/move steps and one data-operation step. Its
decoder can use finitely many states for all binary prefixes of length at
most nine; this number does not depend on w. At the end marker, one step
selects the return state. Exactly `9L+1` left moves return the program head.
The last move can enter the halt state. Thus the full bill is `19L+3` steps.
The simulator's array bounds are checks on the emitted trace, not a machine
oracle or a charged address lookup. Valid execution stays in the proved
reserved intervals. Program bytes are decoded in order, including in tests.

## All-width execution and stock bounds

The source has `59w+153` CNOTs and `28w+46` Toffolis. For each forward ripple,
the CNOT count is `3n-1`; a subtraction adds `2n-3`. The flag stage has eight
CNOTs and two Toffolis. The forward Toffoli count is `7*(2n-3)+2`.
Doubling these counts and adding w+1 output CNOTs gives the stated totals.
Consequently gate read/toggle operations cost
`A=3*(59w+153)+5*(28w+46)=317w+689` unit instructions.

Let `W=14w+39` be the number of work bits. For a work bank of length l,
initialization costs `2l+2` moves and `l+1` writes. Retirement costs the same.
There are 15 work banks, so both phases cost `6W+90=84w+324` instructions.

Each of the 14 forward or reverse ripple passes accesses at most four tapes.
The first access to each costs at most n moves. Within a pass, consecutive
accesses on each tape differ by at most two cells: columns are consecutive,
the carry accesses use adjacent columns, and sign extension clamps at the
last donor cell. Reverse order preserves this distance bound. The first
accesses therefore cost at most 56n; all remaining ripple movement costs
at most 2A. This overcounts non-ripple operations and is a valid upper bound.

The two flag passes contain 20 gates. At most five cell visits per gate,
each of distance at most n, cost at most 100n. The output copy has four first
head accesses and two monotone bit scans, costing at most `4n+2w<=6n`.
The final data-head return costs at most 25n. The four-cell flag tape also
fits these bounds because `n>=4`. Thus all gate and final-return movement
costs at most `187n+2A`. Adding bit operations and allocation gives
`L<=187n+3A+84w+324=1222w+2952`. Therefore
`steps<=23218w+56091` for every positive w. This is a proof from the column
loops and access distances, not a fit to finite measurements.

The data stock is `9w+1+W=23w+40` bit cells plus at most 50 markers.
The 15 work right-marker cells are initially and finally blank. The program
stock is `9L+2` cells, including its two markers. Two control bits and the
finite decoder are constant state. At width 1076, the bit stock is 24788,
of which 15103 are work bits. Program stock is 5308571 cells. Reserved blank
regions, origin markers and the marked input program are entrance resources.
They are not established by this local execution result.

## Verification and limits

The unchanged source verifier runs first. The new checker then decodes and
executes the tape program against direct signed-integer arithmetic. It checks
every cell, all heads, both control bits, instruction counts and retained
program bytes. Width one covers all 1024 donor/target/diagnostic combinations.
Width two covers all 65536 donor tuples with varied output bits. Width 1076
uses the source's 32 published cases. Arbitrary output bits at every width
are justified by the source's XOR-only output interface, not by finite cases.
Seven widths check emitted stock and bounds. The all-width claim uses the
proof above. Bit-plane batching changes only test throughput, not the trace.

Five changed streams are rejected: omitted initialization, omitted retirement,
omitted head return, malformed bits and a wrong target-toggle operation. A
valid extra right/left detour preserves the endpoint and costs exactly 38
more interpreter steps. Thus endpoint equality cannot conceal an unpriced scan.
Normal and optimized Python runs use explicit exceptions, not assertions.

The caller-to-row identification at event 88937 is inherited from PR #7687.
It was read but not rerun here. Program generation/loading, global blank-bank
provision, complete reset and stock budgets, rounded producer reachability,
native admission and complete caller integration remain open. No selected
assumption is discharged. The selected kappa .00363005817 and all five
framework assumptions remain unchanged. No full selected cold replay, Lean
or Docker check is included. These are source-aware author checks, not blind,
independent human or formal-kernel acceptance.
