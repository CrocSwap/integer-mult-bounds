# One dirty bank for a relative-chart packet update

This is a conditional, all-finite-packet payload identity and a separately
checked finite R439 instance. It does not provide a uniform routing backend,
full supplier, optimal bank count, or a multiplication exponent.

## Contract and changed schedule

Let each distinct family i contain an owned complete packet of P records,
embedded in a stream of N_i records. Values are bit strings of any fixed
length. All original values, the snapshot s, and one disjoint borrowed packet
b are arbitrary and may be correlated. The snapshot is in the common frame
and must remain immutable throughout. Family i has an invertible packet
permutation R_i from its owned layout to that common frame.

Assume completed route children R_i and R_i inverse operate on the active
packet in their specified input layouts, restore their private scratch and
heads, and pointwise preserve **every current parked payload**. In particular,
they cannot borrow the dirt temporarily parked in the original source or the
snapshot. They must accept the active bank in each declared source, common,
and target layout. This is a caller obligation, not a consequence of restoring
named sources at the end of the complete word.

As in PR2481, permit a reversible three-XOR exchange of an owned family
packet with the dirty bank, using a synchronized selector scan. The new
schedule also uses a direct synchronized XOR from the bank, in the target's
layout, into the target's ordered owned records. We explicitly charge that
full target scan; random-access selection is not free. The operation preserves
the bank and unowned target records. Headers and selector/control storage are
separate resources; any reversible header transition and return must be
supplied by the physical caller. The payload bank does not supply clean
headers, control bits, or an uncharged second packet.

PR2481 routes two banks to the common frame. Here an ordinary event routes
one source bank through the common frame into the target's layout. The
mathematical frame maps are unchanged. A backend that implements only the
original two-bank instruction sequence needs the stated additional scan and
layout admission before this schedule can be used.

## Ordinary event

Write the target, source, and borrowed packet as (y,x,b), with distinct
physical source and target. The desired map is

    (y,x,b) -> (y XOR R_i^-1 R_j x, x, b).

Operations below are listed in execution order; the rightmost operator in
an algebraic product acts first.

1. Exchange x and b by three XOR passes. The original source now contains
   the old arbitrary b; the active bank contains x.
2. Apply R_j, then R_i inverse, to the bank. Its layout changes
   j -> common -> i, and its value is R_i^-1 R_j x.
3. XOR the bank into the original target's owned records in one full target
   scan. The bank is unchanged and the target has its required value.
4. Apply R_i, then R_j inverse. The bank is exactly x and its layout is j.
5. Exchange bank and source back. The source is x and the bank is its entry b.

Cancellation in step 4 is R_j^-1 R_i R_i^-1 R_j = I. No commutativity or
idempotence of the chart maps is assumed. Parked payload preservation makes
the original b available for the final exchange. No assumption of independent
or zero dirty data was used. Each exchange is itself valid on correlated
values: (a XOR b, b) -> (a XOR b,a) -> (b,a).

## Snapshot tap and chronology

The snapshot must not be exchanged. Exchange the target with b, apply R_i,
XOR s into the active bank, apply R_i inverse, and exchange back. This gives

    (y,s,b) -> (y XOR R_i^-1 s, s, b).

The snapshot is read only at every prefix. Both event maps are involutions.
At each boundary the source, bank, unowned records and snapshot are restored
or preserved, so induction composes the exact chronological event word.
Later events may use earlier targets as sources. Reversing the event order
therefore gives the inverse word. Reordering a tap across another shear is
not justified by this lemma.

## Complete outer invoice

The bill separates route children from outer payload XORs and scan movement.
Internal swaps of the route compiler are already inside its route cost.
A packet XOR pass here counts P record XOR operations. The three operations
of an exchange are fused at each record pair in a single forward scan; the
XOR count must not be mistaken for three physical family traversals.

| Event | Route calls | Exchanges | Update passes | Outer packet XOR passes |
| --- | ---: | ---: | ---: | ---: |
| ordinary source/target | 4 | 2 | 1 | 7 |
| immutable snapshot | 2 | 2 | 1 | 7 |
| 303 ordinary + 10 taps | 1232 | 626 | 313 | 2191 |

PR2481 has 1232 routes, 1232 exchanges and 4009 outer packet XOR passes,
with two borrowed payload banks. The saving is one P-record bank, 606
exchanges and 1818 outer packet XOR passes. Zero-bank optimality is not
claimed. Compared with PR2448's fresh-copy alternative, the route count
still increases from 929 to 1232.

For a fused forward/return exchange scan, charge 2N_i family-head steps and
2P bank-head steps, with both heads returned. An ordinary direct update costs
2N_i target-head steps plus 2P bank-head steps. A snapshot update costs 4P
steps across its two streams. Thus an ordinary event costs

    2N_i + 4N_j + 6P

outer head steps, while a tap costs 4N_i + 8P. PR2481's corresponding ordinary
cost is 4N_i + 4N_j + 12P; its tap cost is the same. Per ordinary event the
difference is 2N_i + 6P saved. These counts price record head movements,
not bit-level selector, instruction or header work.

The role/direction route multiset per ordinary event is exactly
{R_i, R_i inverse, R_j, R_j inverse} in both adapters. Therefore the sum
of route tariffs is equal **if** a role/direction tariff is valid independently
of the changed bank, neighboring calls, parked values and invocation context.
Otherwise retain the actual new trace's route costs in the invoice; equal
call counts alone do not prove equal runtime. The finite replay's route
programs have such a context-independent record tariff and its counters
agree with the pinned predecessor receipt.

## Exact finite coverage and exclusions

The inherited PR2448 constructor binds PR2407's complete RAW6 stream before
extracting the 313 events. The fixed address domain is GL2(Z/9): 48 low
classes, 81 high lifts, 3888 records per family, 111 families. This is a
carry-aware address fixture, not the actual selected GL64 chart program.

Every family record, snapshot record and dirty-bank record has an independent
formal F2 atom: 431730 inputs. Each finite replay checks 313 source/bank/
snapshot boundaries, 25353 event target records against direct full-ring
address multiplication, and all 431568 final family records, including
422577 unowned records. Forward and reversed words are separate executions
on arbitrary formal inputs. Formal linear equality covers every bit assignment
and correlated payload substitution, not just sampled numeric values.

Eight sensitive faults reject dirty XOR-copy in place of exchange, omitted
exchange-back, omitted source inverse, wrong return order, missing address
carries, a forbidden route-time snapshot write, an unowned write, and a
count-preserving wrong tap cut. The write guard rejects the attempted forbidden
write; it does not claim that a malicious completed callee was simulated.
The independent small-permutation check in REVIEW.md supplies separate
noncommuting examples, not a second implementation of the full R439 replay.

Uniform GL64 routing, external rank-seven COPY/ERASE, source/target ownership
admission, complete header/control restoration, private recursive scratch,
precision/tape costs and global supplier assembly remain open. The formal
atoms and expected-state arrays are verifier instrumentation, not a physical
storage implementation. No formal proof-assistant result is asserted.
