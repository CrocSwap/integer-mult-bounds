# A signed projector stream with a fixed work area

This note gives a stream implementation for one affine part of the
correlated native phase sector. It acts on two arbitrary physical owner
fields at one stated cut. It adds the projected source to the target,
restores the source, and clears all temporary work tapes. It adds no
complex native child and no owner family. The main construction retains
every input value in a reversible average-and-detail code.

The affine part has fraction `2^(-n lambda/2)`. It is not a
positive-fraction implementation of the full correlated sector.
The note supplies a local layer and an asymptotic cost. It does not
supply a new full controller or an explicit finite supplier invoice.

## 1. Pinned stream model

Use the fixed-tape model at Git commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The required sources are:

- `upstream/build/sections/02-streams.tex`: elementary split, aligned
  coefficient operation, merge, counters, and work-tape cleanup.
- `notes/compact-control-movement.tex`: a simultaneous selected-bit row
  addition and its fixed work areas.
- `notes/compact-control-layout.tex`: complete compact and spectator
  fields in each recursive role stream.
- `notes/batched-complex-rows.tex`: complete rows, unequal child widths,
  and exact volume `1/W` for each child.

Their byte hashes are in `STREAM.json`. The proof uses the supplied
stream primitives. It does not rerun their Turing-machine proofs.

An owner stream has complete selected address chunks, each of `K` bits,
with the same selected offset `rho`. It also has all its row, compact,
spectator, and polynomial coefficient fields. No row field or compact
field is part of the projector address. Every coefficient is Gaussian
dyadic, and its full guarded representation is retained.

The local node has `n` fixed native slots and an even tensor width
`lambda=2f`. Each slot consists of `2f` consecutive `K`-bit chunks.
Split each slot into its first and second `f` chunks. This is a change
of field names only. It creates `2n` slots of equal width without
moving a record. Since `n` is fixed, their number is fixed.
The existing compact fields have enough bits for row additions on
these shorter slots: `(f-1)G <= (lambda-1)G`.

## 2. The projector and its layout

In each old native slot, pair its first selected column with column
`f+1`, its second with column `f+2`, and so on. This uses the same
pair code as the affine theorem, with a different pairing of columns.
Let `h_(i,j)` translate the two paired selected bits. Define

    Pi = product_(i,j) (I-X_(h_(i,j)))/2,
    k = n f.

Its Fourier support is

    chi_(j+f) = chi_j + omega_n,  0 <= j < f.

Every odd native line has phase `i^f` on this support. The projector
has rank fraction `2^-k` and infinity norm one.

For each old slot, apply the binary address map

    (u,v) -> (u+v,v)

to corresponding selected bits in its two halves. It fixes every
unselected bit. The `n` maps form one fixed binary change of basis `P`.
They send each paired translation to the selected bit in the second
half. Thus

    P Pi P^-1 = Pi_0 = product_b (I-X_b)/2,

where the product uses the `k` selected bits in the second-half slots.
No bit shuffle is needed. The selected bits may remain separated by
unselected address bits.

## 3. A reversible average-and-detail code

First apply `P` to each of the two owner fields. On one selected bit,
split a current active stream into two aligned streams with values
`u,v`. Use the invertible map

    H(u,v) = ((u-v)/2,(u+v)/2).

Call the first output active and the second output detail. Park the
detail stream and recurse only on the active stream, using the next
selected bit. The detail retains its full remaining address set.
After `k` steps, keep the leaf stream and all detail streams. They
contain exactly as many records as the original owner field. No input
coordinate has been discarded.

Let `B` denote this code, and let `E` select its leaf coordinates.
The leaf row is the signed average on each selected-bit coset.
The inverse code uses

    H^-1(a,d) = (a+d,d-a).

It sends a leaf value, with all details zero, to its signed constant
vector on that coset. Therefore

    B^-1 E B = Pi_0.

Encode both arbitrary fields, add the source leaf to the target leaf,
and invert both codes. Undo `P` on both. The exact map is

    (x,y) -> (x,y+Pi x).

The inverse changes only the sign of the leaf addition. The source
restores in full, including every arbitrary detail. The target keeps
its arbitrary complement. No zero source, zero target, or known
borrowed state is assumed.

The code need not be flattened into one stream before the leaf
operation. A fixed LIFO work tape stores each owner's detail streams
with their descriptors. Encode the source, park its leaf, encode the
target, update the aligned target leaf, then invert the target and
source codes. Each pop reads only the last stored detail, and each
merge restores the bit position used by its split. The two encoded
owners still have their original total record count. Their detail
storage is a different layout of the original two fields, not a third
independent signal field. Temporary copies inside stream primitives
remain ordinary owned work tapes and are cleared.

## 4. A separate source-copy realization

Keep the arbitrary source `x` intact. Copy it to an owned work stream
and apply `P` to that copy. For each of the `k` chosen bits, in a fixed
order, split the current work stream on that bit. The two output
streams have the same remaining addresses and coefficient order.
Replace their aligned values by

    a = (u-v)/2.

The new work stream has half the number of records. Clear the old
work streams. Record the removed bit position in a descriptor, not in
an extra address field.

After all reductions, expand in reverse order. Replace each value `a`
by the two streams `(a,-a)` and merge at the restored bit position.
After all expansions, the work stream is `Pi_0 P x` in the original
address shape. Apply `P^-1`. Add the result to the arbitrary target
`y`, then clear the work stream. The exact data map is

    (x,y) -> (x,y+Pi x).

The inverse changes the sign of the final addition. Every unselected
address, spectator value, row index, and polynomial index stays fixed.
The source is never changed. No borrowed value is cleared. The work
streams contain only copies and functions of `x`, and are owned work
areas of the machine. They are cleared before the next owner operation.

For one bit, reduction followed by expansion is

    (u,v) -> ((u-v)/2,(v-u)/2).

The reductions on distinct bits commute as linear maps, with the
remaining address order updated after each reduction. Expansion in
reverse order proves the full product formula. The proof uses no
assumption about the source or target values.

## 5. Time and work area

Let `M` be the initial record count in one field and `V` its guarded
bit volume. At code or reduction step `j`, the current record count is
`M/2^j`. The sum of all reduction input volumes is less than `2V`.
The sum of all expansion output volumes is also less than `2V`.
The source copy and final target addition cost `O(V)`.

Each code step uses one elementary split and one aligned coefficient
pass. Each inverse step uses one aligned coefficient pass and a merge.
Thus both forward codes and both inverse codes cost `O(V)` in total.
The leaf update has only `M/2^k` records. The detail stack holds
`M-M/2^k` records for each owner, and its full volume is scanned only
a fixed number of times. Code descriptors have total polynomial size.

For the source-copy realization, each step uses one elementary split,
one aligned coefficient pass, and one merge or output pass. Its
reduction and expansion also cost
`O(V)`, including scans, rewinds, and cleanup. There is no factor `k`
in the volume bound. The descriptor list has `O(k log(2eK))` bits and
is on ordinary work tape. Computing all step descriptors has polynomial
cost in the global `p`. Every nonempty work stream retains a complete
polynomial record of length `r=2^(Theta(p/d))`; it pays this descriptor
cost in the same parameter family as the source stream theorem.

Before the basis-map work areas, the source-copy pipeline needs
at most two original guarded field volumes plus a fixed number of
coefficient and descriptor registers. For a split, clear the old input
before the coefficient pass. For a merge, clear the old compressed
input before the merge. This gives the stated stock bound on fixed
tapes. The source and target are not counted as work stock. The compact
basis procedure has its own fixed number of work tapes and its own
proved cleanup bound.

The fixed `n` row additions and their inverse, on either two owners
or the source-copy work stream, cost

    O(V ((e log p)^tau + 1)),  0<tau<1,

by the pinned compact-control result, with `e=n lambda`.
The shorter `f` in each row addition only reduces that bound. This
bound includes the binary address algorithm; those maps are not free.
The new layer has zero complex native children. Binary interchange
work inside the compact-control primitive remains in the displayed
time bound.

For the reversible code, each encode uses `M(1-2^-k)` differences,
the same number of sums, and twice that number of halvings. Each
decode uses `M(1-2^-k)` sums and the same number of differences.
There are two encodes, two decodes, and `M/2^k` leaf additions.

For the separate source-copy realization, the work computation uses
`M(1-2^-k)` differences and the same number of halvings. Expansion uses
`M(1-2^-k)` complex negations. The final target pass uses `M` additions.
Copying, bit movement, descriptor work, and the address maps must also
be charged. This count is separate from the earlier pivot graph's
`24s+(4k-16)c` invoice.

## 6. Exact precision and recursive use

If the input grid is `2^-b Z[i]`, after `j` code steps or reductions
the active grid is `2^-(b+j) Z[i]`. Every code value has magnitude at
most its owner's initial maximum, since both sums and differences are
divided by two. A temporary unhalved sum or difference is at most twice
that maximum. The leaf addition is at most the sum of the two owner
maxima. During decoding, the added leaf signal propagates as a signed
constant. The unmodified target part reconstructs the corresponding
original partial average. Each reconstructed value is therefore at
most `||y||_infinity+||x||_infinity`. The source reconstructs its
original values. In a coefficient implementation that saves the two
operands before each local map, one added magnitude bit is sufficient.
This is a prefix bound for the stated shear, not for an arbitrary
operation on unrelated encoded detail coordinates.

For the source-copy realization, each reduction has magnitude at most
the original source maximum and expansion changes only signs. Its
target has the same bound. Thus either shear needs `k` added fractional
bits and at most one added magnitude bit. It does not need the pivot
graph's `k` magnitude bits.
All shifts are exact when these fractional zeros are reserved before
the layer; no internal rounding is used.

Three shears make the projected quarter turn. A direct common-format
bound for that word is `3k` added fractional bits and three magnitude
bits. Idempotence may reduce this bound, but this note does not use
that reduction.

At most a fixed number of such layers in a finite local word adds
`O(e)` denominator depth and fixed magnitude depth at one node.
It adds no child. The existing recursive guard proof can absorb this
term by increasing its fixed local constant: it already permits a
polynomial dependency guard and exact shifts before one outer rounding.
The compact-control recurrence receives overhead of its existing
form `O(V((e log p)^tau+1))`. This statement does not supply new explicit
guard constants or a finite threshold. Those constants must be set
before a new supplier invoice can be accepted.

## 7. A precise completed-owner interface

This layer can run serially at a cut where the physical owner frames
are known complete orthogonal native frames. In a common physical
address chart, suppose source and target frames have the form

    O_i = i^(gamma_i) X_(delta_i) C_(U_i),

tensorized in the same `lambda=2f` columns. Here `U_i` has an
orthonormal basis of rank `r_i`; the translation is the same in every
column; and any coordinate conjugation is an orthogonal map on the
same `n`-space. On the projector range,

    O_i Pi = Pi O_i = eta_i Pi,
    eta_i = i^(gamma_i+r_i f) (-1)^(f omega_n.delta_i).

The Fourier support formula proves the translation sign. Each odd
basis vector has phase `i^f`, which proves the rank factor. Orthogonal
maps fix `omega_n` and preserve the support. Thus the physical operation

    y_physical += eta_target eta_source^-1 Pi x_physical

implements the logical shear `y+=Pi x` on arbitrary owner inputs.
The scalar is a Gaussian unit. Different complete ranks are permitted
in this fixed-phase sector. A view that has an additional unremoved
address permutation must be included in the interface; it cannot be
replaced by the scalar `eta_i`.

This gives an owner-safe local operation once these two frame records
are bound at a specific cut. Both encoded owners remain parked while
the local operation runs, and their physical layouts return before
another owner call. It does not permit a projection at an arbitrary
internal canonical frame. It also does not keep a query in the work
area across owner calls. No selected global schedule is modified by
this packet.

## 8. Limit and next use

The construction resolves the local fixed-tape access problem for this
affine projector. It preserves the full arbitrary complement through
the two-field shear. It does not resolve the exponential coverage cost:
at `n=73, lambda=152`, at least `2^2848` affine parts are needed to cover
the sufficient correlated sector. A useful positive-fraction decoder
must use a non-affine projector, share work across many affine parts,
or use another representation.

`check_stream.py` checks the full basis action, arbitrary target/source
restoration, selected-bit positions, spectator and polynomial indices,
inverse shear, work cleanup, and exact precision bounds in finite
packed examples. It also pins the source proofs. Its checks do not
replace the fixed-tape complexity proof above.

Research and exact checks: OpenAI Codex under the user's direction.
The affine theorem, its equality construction, and the reversible
average-and-detail suggestion are credited to the parent. The
correlated-access packet supplies the original signed-coset graph.
No human review is claimed.
No PR, commit, or push was made. Before any eventual PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
