# Complete outer control at the actual fixed CRT repair port

## Statement

This is a fixed-geometry finite-symbol program theorem, not an all-size CRT
or multiplication theorem. Let the six borrowed unary records G,H,K,Y,J,B
encode (2,2,6,8,2,0), using the retained `< 1^n >` representation with blank
tail. Let the borrowed ROM be `L F R`, where F is any32-bit Boolean table
satisfying F[v]=F[v xor4]. Let data contain4096 opaque symbols from the fixed
alphabet {('R',v):0<=v<4096}, framed by `<` and `>`. The data is the raw
post-S stream for the retained ten-shear compact map S, with source
f(y)=F[y mod32]. All roles are physically distinct, heads initially zero,
all owned roles are initially blank. The program installs each outer `<`
marker through a charged write, then erases it after the source cleanup. Arbitrary finite blank tails are allowed.

The fixed program returned by `assemble` has no runtime instance parameters.
It returns data in the ideal T-image order; it preserves the six unary
records and ROM, erases every consumed/private role, returns every tape
head, and resets every finite-control register. Each of the2944 bad addresses
calls the actual key exactly once; good addresses never do. It is a theorem
for arbitrary payloads in that fixed alphabet and every admitted ROM, not
an inference from the one canonical numerical fixture.

Raw S preparation and ROM construction are input contracts. This work does
not execute S, its twelve paid shuttles, a descriptor/ROM producer, a larger
geometry key, or a complete E(p,ell) evaluator. A marked-role input adapter
allocates fixed blank owned roles; it does not initialize arbitrary borrowed
dirty storage. Rejecting malformed executions have no rollback guarantee.

## Source refinement and static compilation

The retained #4208 producer, #4201 scanner and #4637 bridge contain finite
symbol tests and marker-driven loops, but execute them as Python control.
#4795 implements the key as explicit instructions while the outer caller
still has only a cell-action invoice. This package compiles those unchanged
source ASTs at assembly time and runs none of their Python functions during
execution. Source hashes are authenticated before assembly.

Each source local has a private finite register at each static inline call
site. Mutable parameters are copied before entry, preserving call-by-value
binding while tape-role values still refer to the same physical tape. Locals
are allocated before compiling conditions or either arm; loop tests and both
arms therefore name the same assigned register. Source calls are expanded
statically and recursive source calls are rejected. Each return jumps to a
static continuation. The key instructions are inserted with relocated static
PCs, a disjoint register namespace, and a fixed map for counter/stream/ROM
and its twelve private roles. Its accepting halt becomes a jump to the
unique split continuation. No runtime call stack or callable exists.

A source assignment becomes a finite-register copy. Comparisons, negation,
fixed tuple fields and fixed tuples become finite truth-table operations.
Short-circuit Boolean expressions and conditional expressions become branch
and copy sequences, preserving both evaluation order and tape-read side
effects. `while` becomes a static back edge with its test reevaluated each
time; `break` and `return` become patched static jumps. `for` is accepted only
on a statically bounded tuple, expanded at assembly time. No data-dependent
range or numeric induction variable is admitted. Tape.read/write/move become
single-cell instructions, with move restricted to +/-1. A tape-role register
ranges over the fixed finite bank; choosing a role is a finite multiplexer,
not an encoded address into data. Field projections have compile-time indices.

The source record predicate is implemented on the declared finite4096-symbol
record alphabet. The tuple representation in the emulator is a symbol name;
its numeric payload never becomes a machine address, arithmetic operand or
loop bound. Stencil atoms form a fixed finite product alphabet too. This is
not a literal binary transition table or a unit-price unbounded tuple machine:
all tuple arities, fields, role values and alphabets are bounded independently
of the input payloads. A binary encoding and its constants remain unclaimed.

Valid executions of the source producer do not take its exception handlers.
The compiler deliberately maps all raises to rejecting halts, preserving the
stated successful-domain theorem while making no source exception-cleanup
or transactional-rejection equivalence claim. Static mutation flags are
specialized to the normal program. Instrumentation callbacks/meters are
removed during assembly; the unpaid evaluate_key is replaced by the entire
literal key program, not by a host result. A verifier observer can inspect
states but its values never enter execution.

Induction on the supported expressions/statements gives equality of tape
operations and finite source state at statement boundaries. Loop induction
then lifts this relation through the retained source algorithms. The inherited
producer/scanner proof gives the actual owned stencil and mask; the retained
key theorem gives T(S^-1(q)) from the current counter and ROM; the bridge's
split/radix/reinsert proof gives the ideal payload endpoint and exact bad-only
call set. The source ownership proof, the key's cleanup, and the explicit
control initialization/final reset establish the full successful boundary.

## Complete instruction ledger

Every executed read, write, one-cell move, finite-symbol operation, branch,
jump and halt costs one. Initial register writes, outer-marker installation/disposal and final reset
are explicit instructions. The executor's heads, PC, step totals and event observations
are configuration/observer machinery, never program operands.

Cut outgoing CFG edges at each read/write/move (and halt). The checker rejects
any cycle in the remaining graph and computes its longest path length D by
a topological pass. Thus between successive charged cell actions, before the
first and after the last, the machine executes at most D instructions. For
any finite execution with C cell actions,

    T <= (D+1)(C+1).

The extra1 is deliberately conservative about whether the ending cell action
is included. This argument covers every possible branch, including branches
not taken by the calibration; the observed maximum alone is not the proof.
A control-only-cycle mutation must be rejected.

For a parameter-only bound in this fixed geometry, write M=4096,L=12,N=2944.
Exclude all inlined-key actions from the outer cell count. Counter setup has
at most10(L+1) actions. Each split/address-carry iteration has at most
20(L+1) actions. A radix pass, including last-bit search, key rotation, both
bucket rewinds, concatenation and erasure, has at most100N(L+1)+100 actions;
there are L passes. Reinsertion/counter checking has at most40M(L+1) actions.
Final erasure traverses at most a constant ten times the total
M+N(L+1)+L+10 retained cells. These estimates follow by counting the reads,
writes and one-cell moves in each unchanged source loop; no loop scans past
its marker. The22 outer-marker lifecycle writes are additional. Producer841 and scanner454830 are exact on the declared unary
geometry. Summing these charges is less than

    C_outer <= 1000 M (L+1)^2.

The retained key theorem gives T_key<=3,287,110, hence also C_key<=3,287,110,
for each admitted q,F. All actual key operations, including its append port,
are counted there; the removed host interface must not be added again. Thus

    C <= 1000 M (L+1)^2 + N*3,287,110,
    T <= (D+1)*(1000 M (L+1)^2 + N*3,287,110 +1).

This loose bound closes the finite-symbol instruction ledger; it neither
improves the source asymptotic tariff nor proves full E absorption. Exact
observed counts are separately frozen in RESULT.json. Physical storage is
bounded by the fixed source roles: two record buckets each N(L+1)+2,
keyed bad N(L+1)+2, good M-N+2, data M+2, mask M+2, stencil/counter L+2,
the eight finite unary work extents and key roles. Reusing four emptied
producer roles for good/bad/buckets is included; no live role is aliased.
Finite-control register storage is fixed and separately reset.

## Evidence and remaining questions

The actual canonical middle-layer fixture comes from h3, modulus5,
offsets[0,2,4,0]. Host arrays only construct declared raw-S/ROM inputs and
independent expected output; they do not supply the machine's mask, keys,
branches or traversals. The independent observer checks each current key
counter, exact returned key, scratch erasure and final caller ownership.
Finite tests corroborate the written refinement; they are not independent
human or proof-kernel acceptance.

Open: binary lowering of this complete alphabet; variable-geometry key
control; actual raw macro with twelve dirty-back shuttles; descriptor/ROM
production in the same lifecycle; full evaluator/native/precision/outer
admission. No selected frontier or new kappa is claimed.
