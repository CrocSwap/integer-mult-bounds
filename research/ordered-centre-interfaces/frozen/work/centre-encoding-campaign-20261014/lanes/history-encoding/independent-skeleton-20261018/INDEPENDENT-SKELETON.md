# Two monomial shears on the independent native paths

The construction removes all scalar mixing from the two current native
provider words. It retains every native child, physical warp, endpoint
adapter, residual adapter, private allocation, and owned CLEAR. It then
adds 112 transfers. The transfers give the local maps

    F_E: (x, y) -> (x, y + E x),
    B_E: (x, y) -> (x - E* y, y).

Here E is a permutation of the 112 port fields with one unitary monomial
address operator in each nonzero block. Thus E* = E^-1. The 408 arbitrary
helper roles retain their original native endpoint operators. The words
use the original 632 live roles, eight owned C roles, and 91 private zero
roles. They add no native child and no private role.

The local result does not establish a global controller, a change of
productive owners, a finite precision invoice, or a complete kappa
improvement. In particular, a monomial logical response does not by itself
give a free code change at every physical endpoint.

## Pinned inputs and physical convention

`INDEPENDENT-SKELETON.json` pins the current centre-deleted core and the
exact Clifford compiler. The full programs and recipes are in
`INDEPENDENT-SKELETON-PROGRAMS.json.gz`. The two providers are checked
separately.

Both new words use the **forward signed K_G physical warp recipes**.
The new backward word does not use the old literal conjugate-K backward
lowering. This is a deliberate choice of a new physical word. All its
retained native operators have accepted forward recipes.

The accepted native recipe packet is
`../../new-native-recipes-20261017/FREEZE.json`. Its generation receipts
bind the actual frames, child edges, endpoint adapters, physical warps,
and helper residual wrappers. This construction compares those fields
with the current core and checks every recipe-file pin. It does not
regenerate the old child recipes.

All original `scalar` events are removed except the 16 owned C0 CLEARs.
Every other event is retained in its original order. After this deletion,
the forward and backward event streams are byte-equal. Each of the 632
live fields has an empty reduced signed warp word at the end. The 91
private zero fields receive no scalar input and remain zero.

The transfer cuts lie after phase A and before the first exit adapter.
The fields at these cuts have their literal canonical frames. No
intrinsic endpoint frame is treated as a canonical frame without its
adapter.

## Actual equal-rank frame maps

Let U and V be two proper canonical frame subspaces of the same rank r,
where 1 <= r <= 8. The pinned compiler defines

    T_U = K_U F_r K_U^-1,
    T_V = K_V F_r K_V^-1.

The basis extension, address permutation, and quadratic phase of K_U and
K_V are the ones in the actual `canonical_frame` function. They are not
chosen from the ranks alone. Set

    P = K_V K_U^-1.

Then

    P T_U = T_V P.

P and P^-1 are monomial address operators. The producer checks both
factorizations and this ordered identity from the full signed Pauli
table and the exact Gaussian image of the zero basis vector. The two
checks determine the global phase. It also checks all 512 columns of
each emitted monomial recipe against the literal permutation and phase
circuit. A changed global phase is rejected.

For each selected P, the producer also checks that F_9 P F_9^-1 is
monomial. That is a separate endpoint fact. It does not establish a free
conjugate through the 112 individual output holes.

## Matching and chronology

The direct equal-frame graph has 312 edges and maximum matching size 68.
The producer saves a matching and a vertex cover of the same size. This
is only a statement about direct single transfers in the retained frame
history.

The equal-rank graph with empty source and target logical warp histories
has 12,311 edges. It contains a complete matching. The saved matching
uses 106 diagonal port pairs and six other pairs. It is not claimed to
maximize the number of diagonal pairs.

Each matched edge records the source port, target port, original event
cut, two actual frame bases, both empty warp histories, and both exact
monomial recipes. These records make the event placement checkable.

At a forward edge from X_s in T_U to Y_t in T_V, execute

    X_s <- P X_s,
    Y_t <- Y_t + X_s,
    X_s <- P^-1 X_s.

The first operation changes the physical source frame from T_U to T_V
and changes its logical value by P. The ADD therefore has equal physical
frames. The last operation restores the source exactly. The matching
uses each source and each target once. Since both logical prefix warp
words at the cut are empty, this edge gives E_ts = P.

At the same cut in the new backward word, execute

    Y_t <- P^-1 Y_t,
    X_s <- X_s - Y_t,
    Y_t <- P Y_t.

The ADD now has frame T_U. It gives the block -P^-1 in the reciprocal
position. The full matching therefore gives -E^-1. The entire native
chronology is unchanged; the backward construction does not reverse
the child schedule.

## Arbitrary helper states and complete endpoints

No new scalar event reads or writes a helper. With all original scalar
mixing removed, each helper follows its own native path. In canonical
coordinates its total logical warp is the identity. If its entrance and
exit frames are T_i and T_f, its physical path is therefore

    T_f T_i^-1.

The retained residual wrappers give the same productive child operator
as in the accepted input. A proper helper exit is not replaced by FULL,
and the proof does not call this physical path the identity when the two
frames differ.

The logical replay starts with 640 independent input symbols: all 632
live fields and all eight owned C fields. In each of the four complete
words it checks every output coefficient and every frame. All 408
arbitrary helper inputs retain their required logical values. C0 is
cleared, C1 through C7 are unchanged, and every private zero field is
zero when released. Thus the word is valid on the usual owned-zero
input domain, and the replay also checks the effect of arbitrary owned
input values.

With the retained intrinsic endpoint adapters, the physical data
contract is

    input:  X_p = C_p x_p,  Y_p = y_p;
    F_E:    X_p = F_9 x_p,  Y_p = F_9 C_p^-1 (y + E x)_p;
    B_E:    X_p = F_9 (x - E^-1 y)_p,  Y_p = F_9 C_p^-1 y_p.

The intrinsic C_p operators and their ordering are unchanged. The
construction does not identify these equations with a conventional
identity shear without a separately checked code or controller.

## Exact local invoice

Each provider and each direction has the following retained child
profile:

| Child rank | Count |
| --- | ---: |
| 1 | 2433 |
| 2 | 724 |
| 3 | 228 |
| 4 | 102 |
| 5 | 20 |

There are 3,507 children and rank mass 5,073. All 240 physical warp events,
978 endpoint adapter events, 390 residual adapter events, and 91 private
allocations remain. No new native child is added.

The new transfer operations use 224 complex monomial array maps and 112
unit complex ADDs. The retained 16 complex CLEARs remain. With the
inherited scalar compiler, these top-level scalar events cost

    112 * 8 + 16 * 2 = 928 real scalar primitives.

This number excludes the separately counted monomial maps and the
unchanged native lowering cost. It is not a complete finite invoice.

## Verification and scope

Run one process:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/history-encoding/independent-skeleton-20261018/emit_independent_skeleton.py

The producer checks both complete words for both providers, all selected
native phases, all endpoint maps, all helper and private states, the
native profile, and the scalar count. It rejects a wrong global phase,
a wrong view frame, and a wrong backward ADD sign. The separate
independent review is recorded outside this producer packet.

The exact local identities extend to each positive tensor depth, since
the address identities hold as operators and scalar ADD commutes with
tensor application. The tensor statement does not grant a common global
port code after the stage routes. That obligation remains separate.
