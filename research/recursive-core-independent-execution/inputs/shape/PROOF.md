# Literal child grants at a whole-high batch edge

This is an implementation of a particular missing physical interface, not a new
arithmetic theorem, cover, allocation theorem or Gaussian supplier. Ali Romman's
PR5829 supplies the whole-high address map, child divisor and ancestor-weight
independence. PR6719 supplies the physical split/return tables and the retained
one-edge codec/continuation fixture. David Arias's PR2776 supplies the finite
assembler, machine alphabet and binary-to-unary converter, unchanged here.
The generic arithmetic/descriptor predecessors are distinguished below.
New glue/code: thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.

## Quantified physical contract

Fix an integer L>=2 before runtime. Put A=A_parent, R=R_parent. The three
inputs are positive canonical LSB-first binary A,H,R on distinct physical
tapes, with LEFT at0, body at1,...,ell, RIGHT atell+1 and heads at1. Require
that A is divisible by L*H. There are nine fixed tapes: these three inputs,
two delivered outputs, three unary guides and one reused conversion work
tape. Outputs and work start blank at their own local origin0. No execution
allocates a tape or observes a host head, coordinate, counter or decoded word.
Extra inaccessible backing is charged as K_entry; it is not deallocated.

`producer.build(L)` emits one finite table, depending only on L. On the stated
domain it returns canonical positive binary

    A_child=A/(L*H),  R_child=H*R,

with their heads at1. It preserves all three input bytes/markers and heads,
erases all visited guide/conversion cells and their installed markers, and
returns the four scratch heads to0. The output descriptors are owned copies
with explicit storage/retirement cost and no productive credit.

For the actual #5829 complete batch, fix B,N,q and let

    L=B*|GL_N(F_q)|, H=q^(N^2*(w-1)),
    A=T*(L*H)^(D-j-1), R=H^(j+1)*R_body.

When both parent and child split, D>=j+2. Hence
A_child=T*(L*H)^(D-j-2) and R_child=H^(j+2)*R_body. The producer accepts
the real common H header and parent A/R headers. It does not yet generate
H from q,N,w, the root reserve, or an arbitrary production descriptor.
Those are separate preprocessing obligations, not host arithmetic hidden
inside this table. H is the cardinality of a complete fresh high fiber,
not an individual data-dependent high matrix h.

## Exact grant generation

The unchanged counter converts each input into UNIT^x RIGHT on a distinct
guide. It restores the original binary descriptor and leaves its reused
binary work empty. Their local LEFT markers are installed by emitted
instructions, rather than being assumed newly available for free.

The quotient loop scans L complete copies of the H guide, advancing the A
guide once per H mark. L is finite unrolling in the compiled program. A
complete group consumes exactly L*H A marks and increments the binary output
once. A partial group rejects when A's RIGHT is met too early. By induction,
after k complete groups exactly k*L*H A marks are consumed and the output
equals k. On the promised divisibility domain it finishes after A/(L*H)
groups, which is positive. No unit-cost division or variable-width tape index
enters the execution.

The product loop visits every pair of an H-guide mark and an R-guide mark.
For each pair it increments the other binary output once. The inner guide
is physically rewound for every outer mark. After h full outer scans and r
marks of the next scan, the output is h*R+r. It finishes at H*R.

Both outputs initially consist of RIGHT at body position1, representing a
temporary zero. Each increment replaces trailing ONEs by ZEROs until the
first ZERO or RIGHT, writes the new ONE, grows RIGHT only when necessary,
and physically rewinds to1. Returned outputs are positive and canonical.
If t is the number of trailing ONEs, a nongrowth costs7t+6 instructions and
a growth costs7t+11. Across k increments the trailing-ONE sum is
k-popcount(k), with ell(k) growths. Thus the standard amortized count is

    C_inc(k)=13k-7popcount(k)+5ell(k) <=18k.

This is ordinary binary-counter amortization, not claimed as a new result.

At completion every unary guide head is at its RIGHT marker. A literal
backward pass erases RIGHT, all UNIT marks and LEFT, stopping at local origin0.
The reused binary work has only its LEFT marker left, which is also erased.
Clearing a symbol never removes its position from the visited-space bill.

## Direct literal connection to the actual child router

`linked_split(L)` appends the unchanged PR6719 split instruction table at
compile time and replaces the descriptor table's halt by one fixed jump.
Every branch destination is statically relocated and every router port
statically mapped. There is no runtime Python callback between the tables.
This program has L+11 tapes. It reuses the now-erased descriptor guides/work
as the router's unary/conversion scratch. The two generated outputs are the
router's binary A/R input ports, so no host value supplies those ports.

Its payload input is exactly ONE parent split bank, of length A*R. It is not
the full parent volume V=L*A*R. The equality

    A*R=A_child*L*R_child=V/L

makes it a valid child source. Each child bank is returned with exactly the
unchanged router's (a_child,r_child) order, for arbitrary payload bits.

The address binding is stronger than matching volumes. Write

    a_parent=(a_child*L+l_child)*H+h_child.

Then, on any fixed parent low bank,

    a_parent*R+r_parent
      =(a_child*L+l_child)*R_child+h_child*R+r_parent.

Thus the high coordinate and all earlier ancestor/body coordinates stay in
their exact addresses. The following child split removes only l_child. Its
merge would restore that coordinate, retaining the high field in the address.
This is the inherited #5829 map specialized to contiguous physical streams.

`retire_delivered(L, linked=...)` is a separate finite consumer table. It
erases the delivered grants and, in linked mode, every copied child bank,
then their LEFT/RIGHT markers, returning those heads to0. A production caller
can instead retain the grants until its matching merge; their lifetime remains
owned storage. The finite replay includes actual consumer instructions and
their cost, rather than clearing Python dictionaries.

## Complete coarse local bills

Write S=A+H+R and K=H*R. The retained counter proof gives c(x)<=44x.
The table installs output/work markers in22 instructions. The quotient scan
uses at most12A instructions for H-guide scans/rewinds, at most18A_child
for increments, and at most2A_child+1 group control. The product scan uses
at most24K+10H+4 instructions, including all R-guide returns and increments.
Guide/work retirement and halt use4S+19 instructions. Therefore

    T_producer <=48S+32A+10H+24K+46.

The descriptor consumer uses
7(ell(A_child)+ell(K))+15 instructions. Since S>=4,
ell(A_child)<=A and ell(K)<=K, a conservative bound, including that actual
consumer, is

    T_descriptor+consumer <=200(S+K).

Every visited local extent lies in the nine explicit marked tape intervals.
Their sum is at most

    S +ell(A)+ell(H)+ell(R)+ell(A_child)+ell(K)
      +max(ell(A),ell(H),ell(R))+18 <=10(S+K).

For V=L*A*R, the divisibility premise gives A>=L*H. Consequently
A<=V/2, H<=V/4, R<=V/4 and K<=V/4. In particular S+K<=5V/4.
The actual child router adds at most94(V/L) instructions. Its child-bank
consumer adds at most14(V/L), since the L copied banks contain V/L bits
and V/L>=L. Adding the isolated descriptor and router visited bounds is a
valid overestimate, even though several scratch roles are reused. Thus the
following deliberately coarse bounds cover every valid execution, setup,
source restoration, scratch erasure and delivered-copy consumption:

    T_linked+consumer <=1000V,
    visited_local_cells <=100V,
    retained_backing <=K_entry+100V.

The constants are proof bounds, not a fitted census or a new supplier tariff.
They depend on no runtime H,A,R or depth. Only the finite tape inventory and
compiled table depend on fixed L. Input parsing/production outside the stated
marked-positive ABI and numerical weight work are not silently included.

## One actual codec/continuation boundary

`bridge.GrantBridge(L)` executes the literal nine-port producer through the
unchanged PR6719 stateless3-bit codec. Its fixed physical port map is parent
A, common H header, parent R, the two originally external grant relays, and
four BASE scratch tapes. The input parent A/R and H heads start at logical
body1 and are restored. Outputs are actual encoded logical LEFT/binary/RIGHT
packets. Rewinding to BASE makes them directly consumable by the existing
copy-to-child routine, including their encoded LEFT codewords.

Logical BLANK is000, so after the logical table erases its scratch, the
adapter physically scans and erases all four coded backing strings. It also
charges the extra copy/return/clearing work. No logical zero is treated as a
physically absent tape cell.

The one new physical fixture uses a real small complete-cover shape:
B2,N1,q3,w2, |GL_1(F_3)|=2, L4,H3,D2,j0,T=R_body=1. The parent has
A12,R3,V144; the generated child grants are A_child1,R_child9, so each
parent bank is a complete36-bit child input. None is supplied as a host value
to the executed producer. The retained Pipeline then performs its root split,
two sequential genuine child continuations, bit-complement leaves and return.
Each changed child output is saved before pop and returned to its original
occupied parent bank. An independent observer checks complete parent bytes
and heads at both pops and forbids child access across each segment delimiter.
That observer never supplies a runtime branch, address or value.

There are K+12 fixed physical tapes, K=max(16,L+8): the retained K+7 tapes,
one readonly H header and four producer scratch tapes. L4 uses28. The finite
receipt includes grant generation, physical coded-scratch erasure, both child
returns, all Pipeline work, delivered root-output consumption and final grant
erasure. It checks that original data, parent A/R, H and depth inputs are
preserved, every owned copy/work region is physically erased and all heads
are restored. The generated grants receive no productive credit.

This generation occurs before the root's first suspension. It is one
unequal edge, not an arbitrary-depth production of nested descriptors. The
extra common H/scratch/grant lifetimes would have to be bound at every later
production edge. No per-depth tape or implicit unlimited grant cache is claimed.

## Overlap and numerical-weight boundary

The whole-high shape and induction are already #5829. The finite counter and
assembler are #2776. The source `selected-binary-control` by Jose Manuel already
implements binary multiplication/division, Good/Pair/unit generated weights,
modular inversion, ancestor indices and a complete selected ADD callback using
single-symbol/unit-head word routines. It explicitly leaves a flattened full
transition table and the complete recursive-child connection open.
`r437-binary-divisor-realization` already implements a physical binary quotient
and power construction for its Count ABI. Reimplementing generic arithmetic
or saying that ancestor weights are computable would not be a new theorem.

The bounded new contribution is the emitted child-shape ABI, its direct literal
connection to the actual #6719 router, and the physical codec/stack replacement
of previously supplied child grants. This is useful implementation glue; no
world-priority or original generic-arithmetic claim is made.

Numerical ancestor weights are NOT generated by this package. A shape header
does not contain the full ancestor chart, pivot vector, atom orientation or
mixed Good/Pair descriptor. Inherited weights may vary with all exposed high
ancestor coordinates while remaining independent of fresh child fields.
Their existing preparation and execution charges must remain. For example,
the pinned mixed-descriptor proof retains a direct evaluator cost
O(2^D poly(w,log n_root,D)) and only absorbs preparation under its specified
stopping relation, with an adapter bill of the form

    N_slots*V*(C+2E_max/q^w).

The pinned binary-control package gives a source-specific polynomial allowance
under its own root coupling. Neither is a zero-cost oracle or automatically
the full final-template evaluator. H-from-width production, full generated
ancestor controls, local ordinary BIT-space binding, routes/fallbacks,
Gaussian children, production traversal and precision remain obligations.
There is no changed paid profile, kappa, selected-frontier update, complete
multiplier, human scientific acceptance or proof-kernel claim.

## Finite evidence

The readonly checker authenticates all predecessor bytes before import and
compares a stable RESULT. Twelve arithmetic/linked cases include real GL1
H3/H9 shapes, distinct depths and one GL2 H81 descriptor-only case. It does
not execute that enormous full GL2 parent payload. Four semantic controls
reject a partial L*H divisor, too-small A, occupied output and noncanonical
input. One actual codec/stack case checks the complete144-bit root endpoint
and physical ownership described above. All checks use explicit exceptions,
including under optimized Python. The all-size proof is the loop induction
and explicit bound, not an inference from those finite cases.
