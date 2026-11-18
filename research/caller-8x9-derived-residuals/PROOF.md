# Fixed caller accounting identity

Fix the exact caller and native interface in VENDORED.json. Assume the
operation semantics and declared output endpoints of that interface.
Let H(r) count the native MOVE operations of rank r. Let U(r) count the
public native helper targets of rank r. Count occurrences, not distinct
rank values or reused scratch names.

## Paid positions

The caller invokes the native word once in each of 17 stages. Each call
has fresh public helpers and owned banks. Its 400 main contacts are
injective. Each MOVE therefore contributes once per invocation, including
owned MOVEs. This gives the term 17 H(r). Reuse of a caller field at a later
stage does not remove an occurrence.

For each port, the query vector q is a nonzero vector in the first nine
coordinates. A stage has eight coordinate axes outside these coordinates.
Different stages have disjoint axis blocks. Binary elimination therefore
gives rank one for a QUERY, rank 8s for an IDLE_ONE on s stages, and rank
nine for each one-stage IDLE_ODD. The negative query sign changes phase,
not the dimension. The verifier checks the permitted signed-idle form.

The literal event census is:

| Type and operation | Event counts by stage-block count | Ports |
| --- | --- | ---: |
| A QUERY | 4 events | 96 |
| A IDLE_ONE | 4 each at 1 through 7; 2 at 8 | 96 |
| B IDLE_ONE | 34 at 1; 4 each at 2 through 7; 2 at 8 | 8 |
| B IDLE_ODD | 4 at 1 | 8 |

Thus K(1)=384, K(8)=656, K(9)=32, K(8s)=416 for 2<=s<=7,
and K(64)=208. All other entries are zero. The sum is 3776.
ADD, SCALE, SWAP and LAMBDA have no recursive paid child in this tariff.
Their ordinary work is a separate obligation; it is not zero-cost work.
No invoice is read to derive this table.

## Productive targets

Each caller type has 36 declared output fields. Its diagonal records have
query exponent -1. In each type, four fields select each block count from
one through eight; two fields select nine blocks and two select all 17.
The second central exponent is zero. Each selected block has eight fresh
axes and q is independent of all of them. The target rank is 1+8s.
The identity i^(-x)=(-1)^x i^x for a binary coordinate x accounts for the
stated linear phase correction. The correction does not change rank.

Each output owner is the pair (port, field). Equal diagonal records do not
merge owners. The 96 A ports and eight B ports are a disjoint partition of
all 104 ports. Thus K_T(1+8s)=416 for 1<=s<=8, and K_T(73)=K_T(137)=208.
The sum is 3744. Fresh native public helpers supply 17 U(r) additional
targets. Owned scratch and query scratch do not supply productive targets.
Therefore T(r)=17 U(r)+K_T(r).

The caller contribution to the rank surplus is
sum_r r(K_T(r)-K(r))=57728. This is an accounting quantity, not a new
multiplication exponent or a supplier admission.

## Source comparison and transfer condition

Only after the two residuals have been derived does the verifier read the
reported invoice. Independent binary elimination computes each native
MOVE rank and each public helper target rank from the copied native word.
It checks nested subspaces and the public/owned class of every MOVE.
The sums give 110638 paid positions and 22172 productive fields and agree
with every source histogram entry. This census does not check native
chronology, operator correctness or erasure legality.

For any replacement native word with the same source-bound caller and
contact interface, the same derivation gives P=17 H+K and T=17 U+K_T.
A change to caller events, port partition, stage blocks or declared output
owners requires a new derivation. A change to the native operator requires
its own supplier proof even when these histograms remain unchanged.

The proof uses the declared output diagonals. An independent symbolic
endpoint replay remains a distinct obligation. The matching source invoice
cannot prove those endpoints, the physical bindings or the full theorem.
