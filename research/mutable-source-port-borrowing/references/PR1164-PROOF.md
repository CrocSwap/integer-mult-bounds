# Four-way additive echoes with a fixed dirty pool

This extends the specific allocator of Gareth Davidson's PR1057 to arity four,
using the already known multiway echo from Koroffstrogov's PR758 and its
predecessors. Neither higher-arity optimization nor constant-register algebra
is new. The contribution is their source-bound combination, an explicit
56-factor witness and a complete conditional resource comparison.

## Interface and exact restoration

Each factor A_i is an exact additive endomorphism of an abelian group V.
A leaf on distinct rows s,t performs t += q A_i(s), q in {+1,-1}, with its
immediate source and separately priced private work restored. Coefficient
descriptors are immutable, rows do not alias, and there are no concurrent
observers, hidden mutable state or partial exceptions. Internal invocations
restore their source on return; descendants may borrow that source meanwhile.
The external source row0 is read-only at every prefix. This is the same strong
contract as PR1057, not its rounded/nonlinear relaxation.

Use mutable pool {1,2,3,4,5}, consisting of output row1 and four dirty rows.
At an internal node of arity k<=4, exclude the immediate source and target.
At least three pool rows remain, enough for k-1 connectors. Every child uses
the same pool. Thus four dirty rows suffice at every finite depth. No row is
initialized, copied or cleared when lent. This is an upper bound, not a proof
that four rows are necessary for every tree or arbitrary implementation.

Let U_i be the completed child shear along chain ports z_i to z_(i+1), with
z_0=x and z_k=y. Each completed child restores all other rows independently
of the incoming dirty state. This hypothesis permits replacing it by its
abstract shear at child boundaries, even if it borrows ancestor ports inside.
Put C=U_0 ... U_(k-2), D=U_1 ... U_(k-2), execution left to right. Emit

    C; U_(k-1); C^-1; D; U_(k-1)^-1; D^-1.

The first final-child call reads

    z_(k-1) + A_(k-2) z_(k-2) + ... + A_(k-2)...A_0 x.

After C^-1 the connectors are back at entry. D prepares the same sum without
the last x term. Additivity therefore makes the two final-child increments
differ by A_(k-1)...A_0 x. D^-1 restores all connectors. No factor commutes
past another. Induction on the tree proves the exact desired product shear
and restoration of every arbitrary dirty input. Reversing all leaf records
and signs gives the exact negative call. The finite free-module oracle keeps
every initial row symbol and noncommuting factor word, so it tests this full
identity rather than one numerical input. Nonlinear leaves fail the test while
their literal inverse still restores: reversibility alone is insufficient.

## Complete call recurrence and finite optimum

The first and last children occur twice and every middle child four times.
For complete bidirectional leaf prices c_i, the recursive bill is

    W(leaf i)=c_i;
    W(node)=2W(first)+4 sum W(middle)+2W(last).

Inverse and restoration calls are included. The receipt optimizes unit prices
only. F(1)=1, and for n>1, minimize that expression over every contiguous
positive partition of n into k=2,3,4 parts. By induction, every allowed tree
appears under one partition and joining minimizing children attains each
candidate. This proves the minimum in this fixed template class. Other echo
identities, arities>=5, arbitrary circuits, weighted/address-dependent prices
and physical suppliers are excluded. The chosen allocator always supplies
the four-row budget, so no depth-dependent scratch restriction is hidden.

Through56 factors the implementation checks 396550 candidates. It attains
F(56)=1088 versus1568 for PR1057's exact binary/ternary optimum: 480 fewer calls,
30.6122% of the original count, at the cost of one additional dirty row.
The entire binary/ternary cost table and tie-broken tree agree with the pinned
predecessor. An independent complete enumeration of 1099 ordered trees through
seven factors checks the corresponding optima and 173690 signed leaf events.
These computations supplement the written induction; they are not a formal
proof of the full multiplication theorem.

The direct composition enumerator has O(N^4) candidate/constant-arity work,
O(N) saved costs/splits, and a linear-size selected tree. Integer costs use
their actual bit lengths. Word construction, the tree, coefficients and
planning remain separately paid. This verifier materializes all words and
symbolic states; its memory is not the claimed data-array bound.

## Precision and full backend price

For factor infinity norms <=K, integer K>=1, put

    H(leaf)=1+K;
    H(node)=(k+1) K^n max H(child),

where n counts descendant factors. At a completed-child boundary of either
direction, a chain row is a sum of at most k+1 signed products of factors,
each of degree at most n, applied to node-entry rows. Other rows retain their
entry values. Inside a child, its inductive bound multiplies this boundary
bound. This controls borrowed ports and private dense arithmetic too. For
initial joint infinity norm<=D, a sufficient signed width is
bit_length(max(K,D H(root)))+1. This is inherited exact-integer headroom,
not a rounding-error bound. The all-input free-module oracle independently
checks weighted coefficient norms at every leaf boundary.

For L=2, K=2, D=7, sufficient widths are 119 for the predecessor and 113 for the
new word. Both invoices use common P=119. The dense backend and independent
invoice from PR1057 are retained byte-for-byte and applied to both new words.
It uses four clean scalar work registers, separately initialized and explicitly
zeroed. These are paid ordinary assignments, not reversible free erasures.
Per complete leaf, including cleanup, charge

    L^2 M(P) + (L^2+L) A(P) + (L+4) Z(P),

plus 2L^2+L reads and L writes. Four initial scalar zero assignments are
additional. Exact counters are in EXPECTED.json. Each access and the return
to address zero after every leaf are counted by literal replay and a separate
address formula. If E is the number of accesses and S the intercell distance,
charge P E bit accesses and P S+2(P-1)E head steps, plus E R(a) for the chosen
address routine at address width a. Neither R nor arithmetic is assumed free.

Each unrolled record has b=ceil(log2 n)+2ceil(log2(rows))+1 bits (at least one
per non-sign field):13 here. Charge Nb storage/reads,2Nb forward/rewind steps,
and N Q(b,a,log L) dispatcher cost. Include planning, tree/word construction,
coefficient/descriptor preparation, coefficient bits, four scalar work cells,
control storage and any backend-specific frame/routing/private costs. The
concrete backend has no recursive child beyond the charged factor shears.
For any supplier realization those extra operations must be charged explicitly.

| Quantity, either orientation | PR1057 | Four-way borrowing |
|---|---:|---:|
| Complete leaf calls |1568|1088|
| Dirty length-2 arrays |3|4|
| All data bits at common P |1190|1428|
| Multiplications |6272|4352|
| Add/subtracts |9408|6528|
| Primitive commands, excluding four startup zeros |43904|30464|
| Head steps in bits |195914432|137153280|
| Program storage/read bits |20384|14144|

The same positive and negative word costs agree; coefficient storage is
unchanged. This establishes concrete accounting, not a wall-clock speedup or
a fixed-tape compiler. The inherited all-role call obstruction remains:
W>=4n-4 for n>=2 follows by induction from the weights above. Its optimistic
moment 3W/(2n^(1-b)) is already>=3 at b=0, so this does not yield a new kappa.
Rounded leaves, arbitrary nonlinear borrowing, actual supplier hosting,
physical tapes, all-size realization and analytic transfer remain outside scope.
