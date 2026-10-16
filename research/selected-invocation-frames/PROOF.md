# Local invocation frames for completed sequential callees

This proves a conditional composition rule for the retained sequential bit-tape
primitives. It does not construct the selected recursive supplier. The finite
selected witness below executes the unchanged PR2534 leaf inside three callers.

## 1. Why a local boundary is needed

At PR2534 `f961dcb12061c3959058aed883f48b55f365eb80`, the retained PR2483
`pipeline.invoke` parks its inactive packets, delegates an active packet, copies
the return, and restores the parked packets. It then requires both (a) the
parking head and length equal the **root** floor and (b) every registered tape
outside its own output/restored packets be empty and rewound. A parent parked
packet violates (a); an unrelated live parent tape violates (b). `verify.py`
reproduces both exact rejections using a completed identity callee and verifies
the flat control passes. This is a documented flat-caller scope boundary, not
a counterexample to the predecessor's claimed result.

## 2. Quantified contract and ownership

Consider any finite sequential call tree. At a call node v, let W_v be the
active packet's bit extent and let S_v be the sum of its inactive packet
extents. Extents can be zero and inactive packet lengths can differ. Assume:

1. The active/inactive inputs are distinct registered tapes on one meter,
   each rewound. They are transferred to this invocation. Other existing tapes
   belong to the caller and are not granted to the callee.
2. The shared parking tape is at its current top. Its prefix through that top
   is opaque caller state. Operations are sequential: the parent descriptor
   stays suspended while a child frame is active.
3. A callee receives only its argument and a parking view above all caller
   parking. It accesses only its granted argument, newly owned work tapes,
   and that view through the retained push/pop operations. It neither mutates
   the tape registry nor accesses an ancestor's raw cells, descriptors or
   foreign tapes. This is an access discipline, not a Python security boundary.
4. A completed callee returns one owned rewound tape of exactly W_v bits,
   clears all its other owned working tapes to empty/head zero, and restores
   its parking view to its entry floor and extent. Its mathematical action
   and any arithmetic precision/rounding guarantees are separate premises.

Successful returns are specified. No rollback or transactional failure
semantics are promised. The wrapper checks ownership, extent, head, local
parking closure and invocation-owned cleanup; some access premises require
the callee proof, not only the runtime checks.

`frame.invoke` records the existing registry boundary, takes ownership of the
listed inputs and all subsequently created tapes, and excludes older foreign
tapes from its cleanup check. This exclusion does not grant them as scratch.
When an inner invocation returns, its output/restored packets are newly owned
by the enclosing invocation. The enclosing completed-callee obligation must
consume/clear them except its own eventual single return. Thus ownership does
not disappear at a nested boundary.

## 3. Parking and return induction

`ParkFrame(parent)` takes floor equal to the parent's current head, shares its
cells, and keeps its own head. A push appends above this floor. A pop of size s
first checks the entire inequality `0 <= s <= head-floor`; no partial pop can
cross the boundary. The retained pop consumes the last s bits into a reversed
temporary and reverses them again into the output, preserving packet order.
Neither operation touches cells below the frame floor. At close, the local
head and length equal the entry floor and the suspended parent head is
unchanged. The parent's peak observation is propagated.

An invocation first parks its inactive packets. It then gives its callee a
**second** view whose floor is above those parked packets. Passing the first
view directly would permit a callee to pop its caller's inactive data. The
extra view protects both ancestors and the invocation's own parked packets.
After a completed callee closes this view, the invocation copies its one
return, erases it, and pops its inactive packets in reverse push order into
their original slots. Empty packets cause no data movement and retain their
slot. Local close restores the caller's exact prefix and descriptor.

The active copy and return copy preserve order and extent; source erasure
does not erase the destination. The invocation-owned cleanup check leaves
exactly its output and restored inputs. For a leaf this proves the stated
contract directly from the completed-callee premise. Inductively, each child
contract preserves its caller's foreign state and transfers its survivors
back to that caller. Applying the parent's premise to those survivors proves
the parent contract. Structural induction gives the result for every finite
sequential call tree. It does not infer that a particular recursive numerical
algorithm satisfies these premises or has bounded depth/space.

## 4. Exact additive wrapper tariff

Use the retained `streams.Meter` conventions: a bit read/write moves once;
rewind charges distance; erase charges its rewind plus two moves per bit.
Descriptor construction, registry inspection and Python control are not
included in this payload ledger.

For one active copy-in of W bits, copy costs 2W moves, source erase costs 3W,
and destination rewind costs W: 6W moves, W reads/writes/erases. The return
copy costs the same. Parking one rewound bit costs one read, one parking
write, and source erase: 5 moves, one read/write/erase. Restoring it costs
one parking read/erase, one reversed-temporary write, one reverse read, one
output write, temporary erase and output rewind: 7 moves and two
reads/writes/erases. Summing gives exactly

```
reads = writes = erases = 2 W_v + 3 S_v
moves = 12 (W_v + S_v).
```

The callee's meter delta is excluded. Nested calls therefore compose by
adding these quantities over nodes, plus the callees' other charged work.
No depth-dependent multiplier on each node's wrapper cost is hidden: the
same payload can occur at several nodes and is explicitly counted each time.
The verifier records before/after callback deltas and checks these formulas
for every positive invocation, including zero extents, unequal parked
packets, depth seven identity and depth three selected-child cases.

This tariff does not price the registry/descriptor controller, allocate a
fixed number of tapes, or prove an asymptotic whole-supplier bound. It is a
precise composition invoice in the retained charged payload simulator.

## 5. Finite actual selected-child witness

All retained executable bytes are authenticated before import and compiled
directly. The selected archive binds child 7, frame 0 to frame 9, rank one,
events 9394/9396 in both source program orientations. The PR2534 four-active,
five-spectator factor is checked on all 1,024 monomial columns and all 512
native canonical columns; this is source-binding reuse, not a new native
result. The independent retained oracle forms all 256 columns of the f=2
tensor operator. The physical leaf is unchanged `compose.child`, using
complete Compact adapters, exact C on two axes and literal inverse.

The nested test has all 4,096 address records, one outer row, 24 bits per
Gaussian component, an eight-bit fractional grid and initial numerators
divisible by 16. Three callers each hold their own parked data, live foreign
tape at head two, and zero/unequal-length inactive packets while a child runs.
Independent snapshots compare the entire parent parking prefix, head, foreign
payload/head and ordered restored packets at each return. A forward and
inverse call give eight wrapper invocations. The exact direct oracle checks
the forward payload; the inverse recovers every original bit. Final root
cleanup leaves all registered working tapes empty/head zero and all arithmetic
workspace empty, with the opaque 47-bit ancestor prefix unchanged.

The per-caller dirty fixtures are externally supplied test states; constructing
their Python bytearrays is not a proved tape allocator or a free-workspace
claim. Identity leaves at depths 0, 1, 3 and 7 additionally exercise the
contract independently of the selected arithmetic. This is genuine nested
invocation of a completed selected leaf; it is not a recursive decomposition
of C, a nonleaf supplier implementation or the complete 73-axis payload.

Eight negative controls cover popping caller data, unreturned parking, leaked
owned work, wrong return extent, unrewound return, foreign-return alias,
whole-extent pop preflight, and a raw ancestor mutation. The last deliberately
violates the access premise and is detected by an external snapshot; the
wrapper alone accepts it. Stating this boundary prevents confusing ownership
bookkeeping with hostile-code isolation.
