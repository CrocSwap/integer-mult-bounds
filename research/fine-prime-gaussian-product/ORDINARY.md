# Physical dispatch of the compact436 ordinary interchange

## Source contract

Fix the prime $q=213\,2^{80}+1$, dimension 64, and maximum child rank 42.
The prime certificate is $7^{(q-1)/2}=-1\pmod q$. Its odd multiplier
213 is smaller than $2^{80}$, so Proth's theorem applies. Let
$N=|\mathrm{GL}_{64}(\mathbb F_q)|$,
$K=269241600\,Nq^{4096(w-1)}$, and $c=1/574$. The compact436 word
has 658 ordinary owners and a distinct private owner. Its data family
count is 28416, its stock multiplier is 9475, and their product is
269241600. The price charges 900416 calls and a positive fallback
term for each call.
The caller uses a unit-weight ROOT and the corresponding completed reversed
interchange. The outer wrapper uses both independent applications, input
padding, output restriction, and the signed ADDs specified by the physical
ordinary construction. The logical source establishes the root identity
also for arbitrary dirty input columns. Its fresh-row and root hypotheses
are supplied by the outer controller. [Compact436 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/4a850f3e1444fe6b71d50a57b00c45de2cf963d7/research/bit-compact-carrier-retirement/PROOF.md)
[Physical wrapper](https://github.com/CrocSwap/integer-mult-bounds/blob/840016ebe911ed1d81e367349c2f9520cd7b5435/research/physical-ordinary-interchange/PROOF.md)
[Prime certificate](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/bit2234-stock-threshold/README.md)

## Finite source cursor

The old compiler appended one Python instruction for each low class before
it accepted input. Here $N$ has 359362 bits. The new compiler collects
one chronological skeleton for each of the nine source stages and numbers
the remaining operations arithmetically. It assigns separate fixed intervals
to the replicas and low classes of a local sweep. Inside each packet it
keeps the original gather, accepted local instructions, COPY start, residual,
MOVE into the private slot, destructive scatter, and final CLEAR operations.
For each replica it obtains the actual family from its own source call.
Bridge and exchange slots index the original pair, side and port. Idle slots
index source family before low class. The checkpoint follows the completed
global event, including an idle phase with no owners. The compact producer
checks all replica stages have the same event and request sequence and
translated families. Thus Euclidean division selects the same operation as
the original nested loops. [Physical compiler](https://github.com/CrocSwap/integer-mult-bounds/blob/61f4d7ce898fcb64e89c55519f5b3a340e8e7368/research/selected-bit-physical-caller/macro_code.py)

For each common or native operation the same source specification, exact
projector, good/fallback test and chronological plan are computed. A residual
interval starts with BEGIN and ends with END. In between, position and
three-way stage use the original cursor. A good plan has three blocks. For a
fallback put $t=2m\le128$. Elimination has at most $t$ row swaps and
$t(t-1)$ shears. Each contributes at most three commands, and there are
at most $2(t-1)+1$ terminal commands. Hence $4t^2+4t+8$ command slots
suffice. A call parks the actual successor. It resumes after all unused
labels, with no extra payload scan. The returned macro retains the same
source code and individual child width. The prior block closes its residual
geometry before recursive suspension. During adjacent blocks the two-entry
definition cache preserves the original identity guard. Fixed-size source
caches can evict and recompute a plan. Its data depend only on the fixed
prime, source request, orientation and low matrix. [Cursor](https://github.com/CrocSwap/integer-mult-bounds/blob/61f4d7ce898fcb64e89c55519f5b3a340e8e7368/research/selected-bit-physical-caller/residual_blocks.py)
[Elimination and plan](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/plan.py)

For a partially fixed row the old compiler counts $T=q^s$ completions
for each next residue before independence exclusions. After an inconsistent
constraint there are no exclusions. With a new free constraint pivot,
all residues have $T-q^{h-1}$ admissible completions, where $h$ is the
current nullity. With a forced residue only that residue loses $q^h$
completions. Counting the completions before a residue therefore gives its exact rank contribution.
Division within the interval inverts the sum. This computes the precise
source lexicographic GL rank and unrank for every ordinal. In particular
a residue or low-class ordinal never needs a Python-sized list or index.
All these counters, matrix arithmetic and tables have fixed finite bounds
in terms of the compiled prime and 64. They can be evaluated on a finite
number of sequential bit tapes by ordinary binary arithmetic and scans.
Regenerating a source plan or route costs a finite constant depending on
the fixed source per dispatched block. Packing the continuation costs at
most the fixed 359399 program-counter bits and the other fixed fields on
each call. No completion interval is traversed to find the next operation.
[Source rank counts](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/low_codes.py)

## Four physical buckets

For a single radix digit the complete tape has order
$[P][q][G][q][S]$. Put $B=2^{\lceil\log_2q\rceil}<2q$.
Insert zero suffix records in the missing rows and columns. For bit $j$,
stream each complete suffix to one of four buckets, selected by
$(a_j,b_j)$. Read back in the same scan order, selecting the bucket
$(b_j,a_j)$. Inside each bucket the projection on all other coordinates
preserves lexicographic order. The output therefore exchanges just the two
chosen bits at all addresses, including with arbitrary spectators. Repeating
for each bit exchanges the two complete digits. An address with an invalid
digit then still has an invalid digit. The final scan checks each discarded
bit for zero and copies every valid suffix. The original, intermediate,
bucket and result heads follow the original borrowed/owned convention.

The largest field has at most $B^2/q^2<4$ times the original payload.
Each pass reads and writes through individual sequential tape heads, including
reset and disposal. A separately encoded extent $L\ge1$ costs
$O(1+\log L)$ to initialize a countdown and $O(L)$ cumulatively to
exhaust it by binary ripple. The reset cost is at most the records in that
counter's own complete interval. This also applies when suffix length is one
and when $P,G,S$ differ. Only two fixed-control digit labels temporarily
range over $B$. Each step on them costs $O_q(1)$. One bit pass therefore
costs $O_q(Pq^2GS)$ time and space, and there are a fixed
$\lceil\log_2q\rceil$ such passes. For an atom modulo $q^w$, the source
executes exactly $w$ digit exchanges. The retained $O_q(wV)$ atom tariff
pays all of them. Unit ADD and the linear sign routine retain their own
source implementations and charges. The primitive interpreter is the
source's closed packet interpreter. The parent intercepts a child before entry when its encoded width is at least
the source cutoff. A below-cutoff leaf checks the source, width,
depth, both positions and direction at return. Only ADD, sign and atom swap
can occur between the two leaf events. [Packet interpreter and sign](https://github.com/CrocSwap/integer-mult-bounds/tree/61f4d7ce898fcb64e89c55519f5b3a340e8e7368/research/selected-bit-physical-caller/inputs/pr2753)
[Atom decomposition](https://github.com/CrocSwap/integer-mult-bounds/blob/61f4d7ce898fcb64e89c55519f5b3a340e8e7368/research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/bitstream.py)

The previous $q^2+24$ stream-role path has a current and a following
payload, four buckets, and at most three countdowns for the current suffix
record. The other named roles in that path total at most 24 by the physical
source count. All other root paths use at most 32 roles, including coefficient
descriptor preparation. The inner pool reserves 256 slots. The ordinary
wrapper reserves 512 of its own slots, including the predecessor's fewer than
64 outer roles, plus the elementary path. The binary adapter retains its
distinct 96-slot pool. Numerical matrices retain two fixed banks with
$2^{24}$ permanent labels per root. The outer numerical contexts have their
four separate banks. A dormant numerical port has head one, an empty body and
a shared marker phase. Source access to a new port constructs the view at
that prescribed slot. The physical word shape and arithmetic on the view
are exactly the permanent numerical word operations. The phase becomes
blank after erasure and LEFT after rearm. The used slots keep stable
identities across parking. In the sequential realization each numerical
slot may instead have a permanent tape. Clearing or initializing all of
their origins costs a fixed number of moves. No new numerical label and no
fresh physical tape is needed at a recursive cut. Family and private role
banks, eight handoff streams, physical parking headers, payload restoration,
and the distinct result port retain the original commit/park/restore code.
[Allocation and recursive refinement](https://github.com/CrocSwap/integer-mult-bounds/blob/61f4d7ce898fcb64e89c55519f5b3a340e8e7368/research/selected-bit-physical-caller/PROOF.md)

## Outer high and remainder fields

The fitted ordinary schedule has two additional atom exchanges outside its
two root calls. The optional remainder moves first. Its prefix has length
`P * R * B`, its intervening count is `G * R * B`, and its suffix is
`S`, where `R` is the high row count and `B` is the whole body-field
size. After the body identity, the mandatory high exchange has prefix `P`,
gap `B * J * G` and suffix `B * J * S`, where `J` is the remainder
field size. Each operates on the complete original-volume rectangle.
The explicit fitted adapter uses the predecessor's encoded numerical
contexts, unit ROOT, two padded calls, and shape generator. It calls the
four-bucket primitive on both outer fields using the outer owner's pool.
The original signed body calls only ADD and linear sign. Its padding
implements row insertion and restriction. In each recursive root, the
peel and child-block primitives use the inner owner's four-bucket path.
The outer elementary fallback uses the outer pool. The binary adapter
does four rectangular padding/restriction scans around the native call.
Consequently each reachable atom exchange has a prescribed pool and the
old radix-squared allocation has no production call site. The remainder
costs $O_q(\ell V)$ and the high field costs $O_q(kV)$, with separately
charged encoded preparations and resets. The legal fitted condition
$0\le \ell<w$ places the remainder in the wrapper's existing width bill.
[Authenticated outer schedule](https://github.com/CrocSwap/integer-mult-bounds/blob/b00b58e0db823643364f705b530faac254e7b05b/research/selected-outer-borrowing-wrapper/outer.py)
[Physical context and ROOT setup](https://github.com/CrocSwap/integer-mult-bounds/blob/840016ebe911ed1d81e367349c2f9520cd7b5435/research/physical-ordinary-interchange/ordinary.py)

## Complete exponent and finite thresholds

The physical source locally charges $O_q(V(n+w))$ and reserves
$O_q(V)+F_q$. The compact profile proof gives head and width moment slack
at $b=.00174481>1/574$. With positive stopped costs a smaller saving
increases the volume-contraction exponents and preserves the strict moment.
The independent verifier also checks the source census plus fallback by
exact rational upper bounds at $c=1/574$. Thus the compact physical C0
bound per input bit is $O_q(n+n^{1-c}w)$, including source/route
binding, all numerical coefficients, signed reuse, parking and cleanup.
Any finite compilation constant added per macro is absorbed into the
paid local toll. The complete stock formula and the two independent calls
of the physical outer wrapper yield per-bit
$O_q(n+n^{1-c}w+k+w)$ for a radix width $e$.
Here $w=\lceil e^c\rceil$, stock is $K^{D(e)}$,
$D(e)\le2\lceil\log_2e\rceil$ at $e\ge2$, and $k$ is its ceiling
logarithm to base $q$. Thus $k=O_q(w\log e)=o(e)$.
The encoded controller tests $2k<e$ and $n=\lfloor(e-k)/w\rfloor\ge64$.
Both hold eventually. Below that cutoff the same signed physical digit
algorithm is total. Only finitely many radix widths use the elementary
branch. For the fitted widths $n\le e/w$, hence the complete ordinary
per-bit tariff is $O_q(e^{1-c+c^2})$. For binary width $E$ the wrapper
pads only its two fields to the least $q^e\ge2^E$, with
$q^e<q2^E$. It charges the four complete rectangular scans, retains
$e\le E$, and obtains the saving $c(1-c)=573/574^2$ for arbitrary
spectator rectangles. The earlier published sharp stock cutoff used
$c=17/10000$. The new width is at least that earlier width. Thus
$e\le w^{10000/17}$ and the original index needs at most
$\lceil\log_2 e\rceil+2$ bits. At every internal node the chronological
history satisfies $h+1\le D(e)$ and $2^{h+1}\le8e^2$. In particular
$17(h+1)\le20051w$. These are the source bounds that pay for directory
generation and the fixed bank capacity. This argument proves eventual fit
for the new width.
[Physical outer accounting](https://github.com/CrocSwap/integer-mult-bounds/blob/840016ebe911ed1d81e367349c2f9520cd7b5435/research/physical-ordinary-interchange/PROOF.md)
[Source width and history conditions](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/selected-bit-physical-caller/inputs/pr2753/PROOF.md)

## Executable checks and machine scope

`verify_compact_control.py` compares all 483 reduced-source opcodes to the
materialized predecessor. It tests the seven radix permutations with all
independent input-column signatures. With `--physical` it sends 1024
independent columns through the two complete reduced physical roots (1536
padded columns per root), then reuses the same machine for 192 columns with
nonunit spectators. The predecessor's provenance and cleanup tests execute
on those returns. With `--source PATH` the checker opens the generated
compact436 backend at the actual prime, selects the final GL64 class at the
final replica, executes its route and residual compilation, round-trips a
359399-bit physical header and evaluates the genuine unit ROOT at
$n=64,w=1$. With `--truncated-ingress`, the selected NODE accepts the 359390-bit
compatible row count, checks its quotient 9475, and rejects the first
missing physical input bit. The finite checks did not run a full GL64 payload.
Even one radix digit on both axes needs $q^2>2^{174}$ bits. The arbitrary
input and full orbit results use the structural refinement and source proof.

`verify_compact_outer.py` rejects the original raw digit primitive during
complete fitted executions and independently tracks every payload column.
It tests the lower wrapper's zero and one-digit remainder cases, including
both completed physical roots. The reduced one-digit-tail fixture sets
the remainder width equal to its one-digit atom width to keep the full
payload small. A separate call through the public encoded selector at
width 101 reaches the actual remainder with $w=2$, $\ell=1$, $k=40$ and
30 body atoms. It rejects its deliberately empty input at the first
remainder payload read. A 23-by-23 field with a two-way spectator executes
all 1058 independent columns using 13 leased scratch roles. For each of
these controls, the programmed relation supplies the expected permutation;
the four-bucket executor produces every tested output. The negative
control reinstates the authenticated predecessor's fitted driver and
checks that the test detects its original radix-squared route.

At the production prime the original high-field primitive exhausts all
512 leases before its first input bit. The compact primitive rejects that
same truncated input at the first absent bit, with peak 9. The optional
`--odd-body` check follows 4,096 independent columns through both
roots, eight inner peel swaps and 960 child-block swaps. The binary
adapter also erases the marker of each temporary header tape after it
copies the runtime extent into its owned count.

The stated costs count symbols moved by sequential bit tapes. Each unbounded
operand, spectator, size, or recursion depth is stored on a sequential tape.
Fixed-source control is finite and effective. Host lists, byte buffers, the
interpreter and actual memory have ordinary data-size limits. The certified
predecessor loader uses scoped allocation-site specialization for its own
leased Tape constructors and restores the namespace on return. The compiler
and primitive adapters above use explicit source interfaces. This argument
does not establish a wall-clock speedup on Python or construct an expanded
finite transition table in machine code. Existing source mathematics,
including the compact logical signed-word and GL fallback estimates, remains
part of the proof dependency. A complete root execution on the reduced
grammar and a source-Q coefficient check have different evidentiary scope.
