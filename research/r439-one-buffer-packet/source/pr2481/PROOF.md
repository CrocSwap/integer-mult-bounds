# Borrowed dirty payload contract

This is a conditional adapter lemma, together with a source-bound finite
replay. It does not discharge the uniform routing or helper-admission premises.

## Event interface

Let every logical family have one owned complete packet of P payload records.
The target and source packets are physically disjoint. A snapshot source is a
separate immutable P-record packet. Two further disjoint P-record buffers have
arbitrary initial contents b and c. No independence of payload values is needed.
Packet headers and control state specify the layouts; they are not arbitrary
dirty payload, and their storage is additional to these two borrowed buffers.

For family i, assume an exact reversible packet permutation R_i to a common
frame and its inverse. Each route call restores its own workspace and head
positions and leaves every other current payload value pointwise unchanged.
In particular, it must preserve the buffer dirt temporarily parked in an
original family. This premise is stronger than preservation of originally
named source values only at the end of the whole word.

The intended target/source event is

    x_i <- x_i XOR R_i^-1 R_j x_j,

with x_j unchanged. A snapshot event substitutes its already-common-frame s
for R_j x_j. The logical source may be temporarily exchanged during the event;
callers requiring it immutable throughout cannot use this adapter unchanged.

## Reversible protocol

Exchange the target packet and the first buffer. An exchange of two record
values uses `(a ^= b; b ^= a; a ^= b)`; this maps `(a,b)` to `(b,a)` for
arbitrary correlated inputs and needs no blank payload record. Route the first
buffer by R_i. For an ordinary source, exchange its packet and the second
buffer and route the latter by R_j. XOR that common-frame source into the
first buffer. For a snapshot, XOR the immutable snapshot directly.

Apply R_i^-1 to the first buffer, then exchange it back with the target. For
an ordinary source, apply R_j^-1 to the second buffer and exchange it back.
The target is now exactly the requested updated value. The source and both
borrowed buffers are exactly their entry values. No other original packet
was written. The snapshot was read only. Every operation is reversible, and
no payload CLEAR, discarded record or fresh payload record occurs in this
outer adapter. The same sequence for the same shear is an involution.

These assertions hold at every event boundary, so sequential composition
implements the chronological word even when later events reuse earlier
targets as sources. Reversing the event order implements the inverse word.
Moving a snapshot tap across a target shear is generally invalid: source
identity and inventory alone do not determine the endpoint.

## Complete outer bill

For a target/source event: four route calls, four packet exchanges, one
P-record XOR update. A snapshot tap: two route calls, two packet exchanges,
one P-record XOR update. Each exchange has three P-record XOR passes.

The pinned window has 303 target/source events and 10 snapshot taps, hence
1,232 route calls, 1,232 packet exchanges, 313 update passes, and 4,009 packet
XOR passes in total. This trades the predecessor's 929 route calls and fresh
payload-copy/disposal contract for more routes and two restored dirty banks.
It is a contract alternative, with no claimed runtime improvement.

For family length N_i, our scan implementation exchanges the P owned records
in a full forward family scan, advancing the buffer only at an owned record,
then returns both heads. Its bill is 2N_i family head steps and 2P buffer head
steps per exchange; the update adds 4P head steps for its two streams and
their returns. Physical feasibility requires a synchronized owned-record
predicate and the declared headers/control mechanism. Their symbol cost,
uniform generation cost and the routing child's private storage are not
proved by this payload lemma.

## What the finite replay establishes

The retained PR2448 compiler enumerates GL2(Z/9): 3,888 family records, 48
invertible low classes and 81 high lifts. Each of 111 families owns one
81-record packet. Sixty-four distinct nonidentity charts include carry-sensitive
routes. The verifier obtains the exact 313 chronological events from the
pinned exporter and constructor, rather than accepting a local event list.

Each physical input record receives a separate formal F2 basis atom: 431,568
family records, 81 snapshot records, and 162 dirty records. XOR expressions
therefore certify every bit assignment to all 431,811 formal inputs, including
correlations by substitution. They also apply independently to each bit of
longer payload records. This is not a sampling argument.

Every route executes an adjacent-swap program and restores its recorded head.
The finite route interface is confined to the active buffer; parked original
streams have a write guard, and snapshot/inactive-buffer contents are checked.
The source and both dirty banks are checked after each of the 313 events.
The endpoint oracle uses the predecessor's separate logical baseline and
direct full-ring address multiplication, without the carry compiler or its
permutation. It checks all 431,568 family records, including 422,577 unowned
records. The reversed word is replayed separately on arbitrary formal inputs.

Six explicit mutations are rejected for their expected reasons: replacing
the first exchange by a dirty XOR-copy; omitting target exchange-back;
omitting source inverse-route; removing carries; attempting a forbidden
transient snapshot write; and moving a tap while preserving its event
inventory. The snapshot control tests rejection at the forbidden write,
not a claim that a completed malicious callee was executed.

The concrete adjacent-swap compiler is not a uniform GL64 routing algorithm.
Its exact finite counters are evidence for this fixture only. For a scalable
implementation, replace it with a proved uniform callee satisfying the stated
ownership, restoration, header and cost premises, then include those premises
in the full supplier ledger.
