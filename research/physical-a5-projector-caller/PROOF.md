# A physical A5 projector service and its complete four-call caller

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
This is a typed successful-call source-machine theorem. It is not an admitted
recursive BIT supplier or a saving in kappa.

## Sources and exact endpoint

Nick Petalas PR5114, head d165f73e8af63e8621e4e8a279f58b54079e48c5,
provides X=[[1,1],[0,1]] and Y=[[0,w],[w^2,1]] over F4 and the action on
256 addresses (two copies of F4^2). Its convention is P_g e_a=e_(ga).
Its regular-orbit argument supplies faithfulness of the full F2[A5] action;
that argument is inherited, not re-proved by a tape replay. Its 360/510
array-XOR counts do not pay physical tape movement.

Wentao Li PR4089, head 73a96c95cb86c6615d7809664dd92ec2eb9bb900,
provides the literal algebraic word

    D_E00(x) D_E00(y) D_E11(y) D_E11(x) = diag([xy],[yx],1).

Execution on columns is rightmost first. The implementation executes this
exact four-call word and restores the third arbitrary dirty stream. Credit
Cinna Davis PR2246/PR3914 and the retained register-model lineage. No new
word lower bound, affine-dimension minimum or group-algebra theorem is claimed.

## Tape contract and charged model

There are three distinct owned data tapes, one distinct borrowed width tape,
and three private tapes: unary guide, binary countdown and output. The seven
ports are disjoint. Each data tape has LEFT at cell0, exactly 256q arbitrary
bits followed by blanks, and head1. Here q>=1 is supplied on the width tape
as canonical positive little-endian binary, followed by END and blanks.
Its head is also1. Record address a occupies cells1+aq through(a+1)q.
The address order is exactly the predecessor's eight-bit order. There are no
unpriced source/target frame changes. All external blank backing may be arbitrary
and finite. All private tapes begin blank; their markers are physically written.

A primitive is a local-symbol read/write, a unit move, or bounded finite control
operation. Python storage/head counters and meters represent the tape machine;
the controller does not inspect backing arrays, visited sets or decoded heads.
The fixed 256-entry permutation and at most15-instruction role circuit are
compiled control, not runtime arrays indexed by input. They can be unrolled
into a finite program independent of q. We give a source-machine implementation,
not a materialized binary transition table or Python wall-time theorem.
Offline compilation is explicit and fixed, with no runtime payload/width input.
The public source program contains no call to a random-access payload oracle.

Initialization, width copying/conversion, all data scans, guide resets, output
transport, erase, head return and final marker disposal are charged. The
constructor's external tapes are caller-owned entry state. Every successful
call returns their heads to1. The descriptor bytes remain unchanged. Three
private roles are reused for all four calls, then have every nonblank cell
including LEFT erased, head1. No transactional guarantee for malformed input,
exceptions, aliased objects or arbitrary modification of internal state is made.
The emitted output replaces the owned input streams; no original-data recovery
is promised beyond the actual invertible target and its dirty spectator.

## Encoded width and source-independent control

setup copies the width digits onto the countdown tape. While it is positive,
subtract one in place, append one unary guide mark, and return the countdown
head. When a highest one becomes zero, replace it by END and erase the old END.
Thus the counter stays canonical and empty-END represents zero. Induction gives
exactly q guide marks. No q is decoded into an integer. A block operation moves
one data head for each guide mark, optionally copying a bit, then physically
rewinds the guide. A loop over an address origin has a fixed upper bound255;
its loop count comes only from the immutable compiled permutation.

For decrements t=q,...,1, the number of traversed bit positions is
h(t)=1+nu_2(t). The sum is at most2q, since
sum_{j>=1} floor(q/2^j)<q. Marker replacement adds bounded work per decrement.
Copying the L=bitlen(q) input and returning heads is O(L), and L<=q.
Therefore setup and eventual guide/counter disposal cost at most1024(q+1)
source primitives, a deliberately loose bound including finite control.
This argument counts full scans and does not use a free integer decrement.

## Complete physical generator action

The offline compiler obtains the exact push permutation p from the retained
source address_action and stores its inverse in finite control. For output
row j, the program returns the source head to1, skips p^-1(j) complete q-bit
records with the guide, and copies the next complete record to the output.
The output head advances sequentially. Induction on j proves that after256
rows, output[j,lane]=input[p^-1(j),lane] for every lane. This is the push
operator P_g. No address or payload value is decoded at runtime.

Only after the whole output exists does the program overwrite its owned source
with that output. It then erases the entire output body and returns both heads.
The source never aliases the output. The guide is reset after every block.
Every row is read at its real physical location, including fixed points and
all shorter source orbits; there is no regular-orbit-only restriction.
The same control works for every q>=1, including nonpowers of two.

## Non-coordinate projectors and the complete caller

Fix nonzero u,v in F2^3 with v^T u=1. Choose an invertible binary B whose first
row is v and whose other two rows form a basis of the annihilator of u.
Then Bu=e0, and

    B^-1 diag(P_g,I,I) B = I+(P_g-I)u v^T = D_(uv^T)(g).

The compiler constructs B and reduces it to I by row additions, replacing
each row swap by three row additions. At most3 swaps and6 other additions
suffice, hence at most15 CNOTs. Reversing the reduction gives the circuit for
B; reversing that circuit gives B^-1. The 28 possible idempotent projectors
are fixed specializations. This is a finite compiled alphabet, not an API for
unbounded runtime register counts or unvalidated runtime circuit inputs.

Each CNOT scans the complete source and target streams in lockstep, writes
their bitwise XOR to the target, and returns both heads. Equal 256q-bit
volumes and disjoint roles are essential. All three roles may be dirty.
Thus mix;permute;inverse-mix realizes the full operator above, not only its
selected output column. In particular u=(1,1,0),v=(0,1,1) uses a non-coordinate
projector: both first roles change by(P_g-I)(X1+X2), while X2 is unchanged.
The verifier's explicit coordinate oracle checks that whole relation.

Applying this service to the four source calls, in column execution order,
gives diag(P_x P_y,P_y P_x,I). P_x P_y=P_xy follows from the retained action.
The third stream is restored for every input and q. Each call ends with empty
output and guide head1, so the same scratch bank composes without fresh tapes.
Only the compiled finite source word is used; there is no host semantic child.

## Complete operation and backing bounds

For a generator permutation, the skipped record count is exactly
0+...+255=32640, independent of which generator. There are256 copied records.
A skip block has tape traffic at most5q+4; a copied block adds3q. Its control
loop has q iterations. All source rewinds together traverse at most32896q
cells; a return over z body cells costs2z+3 local operations. Output/source
final rewinds, complete output transport and erase add a constant number of
256q scans. These counts include guide returns, not merely useful bit copies.
Bounding every source/control bookkeeping point by an additional factor16
leaves each full generator permutation below2^21(q+1) source primitives.
Each role CNOT including both head returns costs at most16(256q+1) primitives.
At most30 CNOTs per projector, plus its generator and finite dispatch, give

    one projector call <= 2^22(q+1),
    setup + four-call caller + close <= 2^25(q+1).

These are conservative upper invoices, not optimized costs and not a claim
that four formal calls cost four physical primitives. Instrumented traffic and
control observations are checked below these bounds; the written count, not
finite measurements, establishes the uniform bound. The finite branching,
call frames and fixed address states are accounted in the extra factor16.

Let K0 be the total allocated backing cells of the four external tapes at
entry, including all blank tails. The implementation never extends those
tapes: data writes stay inside the existing payload, and width is read-only.
Private output backing has at most256q+1 cells, guide at mostq+1, and countdown
at most L+2. Therefore all retained backing, including erased prefixes, obeys

    K <= K0 + 257q + L + 4.

Clearing does not shrink these arrays. This bound remains valid after close;
all private cells are blank but their storage persists. Visited blank end cells
are not confused with allocated cells; a visited-span bound may add three end
cells for the three private tapes. No zero backing baseline is assumed.

## Limits and open next questions

This closes a concrete physical execution boundary for a formal source caller,
not admission into the selected BIT supplier. The favorable recursive use,
source/target frame conversion for another caller, hosting, stock, general
role counts, supplier tariff and outer multiplication remain unknown. The
operation constant is large because the route repeatedly rescans source rows.
A next optimization must preserve the whole invoice and demonstrate a real
consumer benefit; another formal call count or address circuit is insufficient.
A distinct next task is a materialized finite instruction table for this same
ABI, with the above source bound retained. No whole-history census, selected
native replay, Lean proof or independent human/kernel acceptance is claimed.
