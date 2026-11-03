# A smaller initialized state for one G20 carry column

This contribution was produced by Nick Petalas. The result is a finite
construction certificate with a scoped written all-width proof. It leaves
the selected frontier and its five assumptions unchanged.

## Contract and predecessor

Fix the scale-free port 8, inverse direction, output column 1 of
[PR5820](https://github.com/CrocSwap/integer-mult-bounds/pull/5820). Its column is

`(-1/4, 0, -1, 0, -1, 0, 0, -1)`.

The exact source is `research/g20-sparse-port-construction/RESULT.json` at
canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, SHA256
`44511d9c7da1c88e265f32ba5d77559b92edb6ca1430180231e84727d939d318`.
The new checker reads only that column's scalar word. It does not run a
predecessor scientific verifier or count the other columns.

[PR6474](https://github.com/CrocSwap/integer-mult-bounds/pull/6474), head
`63c65d845d84ae47fa8264c48c289e55c44cdc76`, gives the interleaved carry
invariant. [PR6503](https://github.com/CrocSwap/integer-mult-bounds/pull/6503),
head `03e47a1a258f87d4a5bce86292f1a1b815ed0f52`, constructs the quotient
machines. [PR6531](https://github.com/CrocSwap/integer-mult-bounds/pull/6531),
head `e10a2373a63aa212aea3ae24760f722bd5a43ef0`, gives reversible histories.
Their results are cited dependencies, not results independently audited here.
In particular, the cited quotient model for numerator coefficients
`(-1,-4,-4,-4)` has 2,406 compact states. Its separately encoded quotient and
eight comparisons require `12+8=20` main-state bits. Its exhibited unrestricted
product-state row fiber has 3,328 elements. These predecessor numbers are not
new measurements in this package.

The changed hypothesis is joint reachability from the initialized state.
The new representation keeps a finer raw threshold state, coupled to the four
comparisons that actually affect this column. Four inactive comparisons remain
separate. No independent dirty quotient/comparison entrance state is accepted.
This changes the domain of the finite table, not the source word or packet.

## Integer-prefix invariant

Read binary rows from least significant to most significant. After `l` rows,
put `R=2^l`, and let `X_0,...,X_3,Q` be the four active prefixes and radix
prefix, each in `[0,R)`. Write

`N = -X_0 - 4X_1 - 4X_2 - 4X_3`.

For each `j=-12,...,0`, retain

`D_j = floor((N-jQ)/R)`,

and retain four flags `v_i=1[X_i>=Q]`. Initially `D_j=0` and every flag is one.
For the next active bit mask `m` and radix bit `b`, set

`a(m)=-m_0-4m_1-4m_2-4m_3`.

Appending the row gives `N'=N+Ra(m)`, `Q'=Q+Rb`, `R'=2R`, and therefore

`D'_j = floor((D_j+a(m)-jb)/2)`.

This follows by writing `(N-jQ)/R=D_j+theta`, `0<=theta<1`.
Adding an integer and dividing by two cannot make `theta/2` cross the next
integer. If the new input bit equals `b`, the corresponding flag stays fixed.
Otherwise it becomes that input bit. These updates depend only on the retained
state and one of 32 letters. The four inactive flags obey the same comparison
rule independently.

The closure deliberately permits every binary radix stream, including even
and zero prefixes. Thus it contains all initialized canonical prefixes and
also supports restoration on malformed canonical inputs. It does not assume
that a prefix already satisfies the final `X_i<Q` tests.

## Finite closure certificate and state improvement

`construct()` starts with the initialized state and appends every successor
under every one of the 32 letters. It permits at most 32,768 states and fails
if that capacity is exhausted. The finished closure has exactly **23,789**
distinct states and **761,248** edges. Its deterministic order has state SHA256
`7ffcc00671cae90d50f9b5c3b35b806c1048e7f41f42017f220fe35cff6224f1`
and big-endian 16-bit edge SHA256
`7dca6909984a201fb2237d64a7ac740fd8446c605805703e1f459af66e67544b`.

This is a finite enumeration, not a claim that those values follow from a
closed-form formula. The checker stores one actual integer-prefix witness for
every state. It reconstructs each witness from the discovery tree, recomputes
all thresholds by literal integer division, and checks every outgoing edge by
appending bits to the full integers. This oracle does not call the transition
recurrence. Distinctness, reachability and closure together certify the exact
count for this declared raw-state machine.

Give these states labels `0,...,23788`. Fifteen bits suffice for the active
joint state. Add four inactive flags to obtain **19 main-state bits**, saving
one bit relative to the cited 20-bit representation. This is an upper bound
on a particular representation, not a minimum-state theorem for the packet
function. Residue, radix bits, stream position, input storage, history and
lookup workspace are separately charged below.

The integer-prefix invariant proves that the same finite table implements
arbitrarily long streams: after each row the current state is in the verified
closure and still represents its integer prefixes. The executable checker and
sample runner are deliberately capped at 4,097 rows. The universal statement
rests on this written induction, not on testing all lengths.

## History and literal return

For each known active letter and target state, list source labels in increasing
order. Retain the source's position in that list. The checker enumerates all
761,248 inverse edges, tests every position and confirms that every source
appears exactly once for its letter. The largest active fiber is **203**.
For letter `(m=0,b=1)`, the target is

`((6,5,4,3,2,1,0,-1,-2,-3,-4,-5,-6), flags=0)`.

Its fiber has 203 states. Let `H_a` be the maximum active fiber for letter `a`.
At most four inactive flags collapse. If `k` collapse, save their prior values
as a `k`-bit integer `z` in increasing coordinate order. A row record is

`r = active_predecessor_rank + H_a*z`, with `0<=r<H_a*2^k`.

The row radix `B=H_a*2^k` is known from the immutable row alone. Since
`H_a<=203`, every row has `B<=3248`. This improves the worst available record
alphabet from the cited unrestricted product's 3,328 to **at most 3,248 values**
for this changed representation and domain. Both bounds still need twelve bits
when one allocates an independent fixed-width slot per row. This does not
refute or improve the predecessor's sharp theorem on its different domain.
No sharp full initialized-producer history minimum is claimed here.

A concrete mixed-radix history register starts at `T=0` and updates
`T'=B*T+r`. On return, `divmod(T',B)` recovers `T,r`. Then `divmod(r,H_a)`
recovers `z` and the active predecessor rank. The target, letter and rank recover
the old active state. Restore the inactive flags from `z`. This is a literal
inverse on the transition image. After every row is returned, `T=0`, the state
label is zero and the inactive flags are their prepared value 15. XOR out that
constant. Nothing is discarded.

For `L` rows, `0<=T<product B<=3248^L`. An allocated binary capacity of
`bit_length(3248^L-1)` therefore suffices, including zero bits at `L=0`.
Multiplication and division of this growing register are paid, unimplemented
physical costs. This alphabet/capacity statement is not a faster or cheaper
physical history implementation.

## Packet, validity and additional registers

For a nonempty canonical stream, `Q` is positive and odd, its first and last
radix bits are one, and all eight complete low inputs satisfy `X_i<Q`.
Then `-13<N/Q<=0` except that equality zero is allowed. The threshold signs
supply

`U=-13 + #{j in [-12,0]: D_j>=0} = floor(N/Q)`.

Indeed `D_j>=0` is equivalent to `N>=jQ`, and the displayed range bounds the
number of true thresholds. Retain two residue bits `N mod 4` by adding the
first two weighted rows modulo four. Retain the second radix bit in one extra
bit, so `Q^-1 mod 4 = 1+2*b_1`. These registers update invertibly and need no
overwritten-state history. Row position is supplied by the stream cursor.

Set `c=U-(U-(N mod 4)*(Q^-1 mod 4)) mod 4`. It is the largest integer at most
`N/Q` in its residue class modulo four. Consequently

`c = (N - 4*((N*4^-1) mod Q))/Q`,

with canonical low residue in `[0,Q)`. This is the source's five-bit carry
packet for denominator four. The checker independently evaluates the right
side with modular inversion at concrete canonical inputs.

Validity requires the first/last radix tests and all eight comparisons false.
XOR the five-bit code `(c+16) mod 32` and a sixth validity bit into an arbitrary
dirty six-bit output. Packet bits on invalid canonical inputs are unspecified.
Run the literal return above and undo the residue additions and radix-bit XOR.
All prepared logical work returns to zero, while inputs and dirty output are
preserved. The caller must retain the same input rows through the reverse pass.

## Complete scope and ledger for this component

The main-state saving is `20 -> 19` bits. The two residue bits and one stored
radix bit are additional, so the new displayed arithmetic registers use 22
bits, excluding the known row position. No total-workspace reduction is claimed.
Both implementations need input access in reverse order and incur `2L` row
accesses, an output XOR, preparation and return. The new return also incurs the
mixed-radix arithmetic described above.

A direct ideal packed layout can store a 15-bit next-state label and 8-bit
rank for every active edge, 15-bit inverse prefix offsets for each letter's
23,790 target boundaries, 15-bit predecessor labels for each inverse edge,
and one 8-bit output/active-comparison record per state. Its declared cells
occupy **40,536,936 bits**, or **5,067,117 bytes**, before descriptors, alignment,
lookup scratch and physical addressing. This is a layout capacity calculation,
not an emitted packed backend or a measurement of Python heap usage. Larger
static tables may outweigh the saved register bit. Initialization is a finite
compile step; tables must remain present during both passes.

The package deliberately stops at the first local improvement. Physical table
lookup, arithmetic gates, head routing, input retention/erasure, actual packet
consumer installation, native costs, compiler closure, precision, stock, tape
and outer admission remain open. No whole-G20 replacement, recursive invoice,
runtime improvement, new kappa or complete multiplication theorem is claimed.

## Credit

Ali Romman supplied PR5820, PR6474, PR6503 and PR6531. Credit their retained
ToikY, Tekalign, JoyboyBrian, Kyu, Nick Petalas and G20/native/ROW predecessors.
The new result is this one-column initialized joint-state closure, its smaller
state representation and row-record alphabet, and its exact finite certificate.
Finite-state reachability, interval/carry invariants, predecessor ranks,
mixed-radix coding and compute/copy/uncompute are classical. General literature
priority is unclaimed. Independent human and formal proof-kernel review are
unclaimed.
