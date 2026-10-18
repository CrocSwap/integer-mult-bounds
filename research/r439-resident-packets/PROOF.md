# Two resident packets, restored at a window boundary

This is a conditional replacement for PR2481's per-event dirty-packet adapter.
The exact 313-event word and snapshot cuts are unchanged. Original owned
packets can remain exchanged across events; neither original-source availability
nor restoration of both borrowed banks at every event boundary is promised.
Every original packet and both banks return to their required values at the
whole-window boundary. This changed ownership permission is essential.

## Payload and route contract

Let family i have an owned P-record packet in its own order and a fixed
invertible coordinate permutation A_i into one common packet order. There are
two disjoint borrowed banks with arbitrary initial payloads d_0,d_1. Correlation
between banks, originals and the immutable snapshot is allowed. Each route
child must preserve every other current record pointwise, including bank dirt
parked in original families, restore its own private workspace and return its
heads. Headers, route-private scratch and control storage are additional
premises, not payload supplied here. Unowned family records are immutable.

A residence interval assigns one family to one bank. At entry, exchange its
packet with that bank using three XOR scans, then apply A_i to the bank. During
residence the family packet holds d_b, while the bank holds the current logical
packet in common order. A role-to-bank table supplies control; changing the
name in the table is not a free movement of any payload.

For an ordinary event t += s, both families must be resident in distinct banks.
XOR the source bank into the target bank. A snapshot event t += z requires only
t resident and reads immutable z in common order. The state of every other
logical packet is unchanged. In particular a previously updated source is read
from its resident bank if it has not yet been evicted, not from the parked dirt
at its original address.

To evict i from b, apply A_i^-1 to b and exchange with i's original packet.
The original receives its updated logical value in its original order, and b
receives its exact original d_b. It can now serve any other family. Flush both
banks at exit. Induction over loads, updates and evictions proves the exact
chronological word, restoration of the banks, immutable snapshot and unchanged
unowned records. All operations are linear over F2, so an independent formal
atom at every input proves arbitrary substitutions, including correlations.

This proves the inverse fragment as well: compile a fresh schedule for the
reversed XOR word and replay it on arbitrary input. The reversed word has the
inverse logical operator, and every residence still has paired entry/exit.

## Exact minimum in the stated residency model

The model fixes the event order and common packet layout. There are at most two
resident families, each occupies a full bank, and an ordinary event requires
both its target and source resident. Snapshot reads need no resident slot. A
load is one exchange and one forward route; each eventual eviction is one
inverse route and one exchange. Banks start and end empty of logical packets.
This model excludes direct updates into originals as used by PR2519, changed
common layouts, fused routes, more banks and event reordering.

For request Q_j={t,s}, or {t} at a snapshot, maintain a state S of at most two
resident families and its minimum load count. No optimal schedule needs to
prefetch: delay any load to its first use without adding loads or exceeding
capacity. No optimal schedule needs to evict an unused resident while space
is available: postpone eviction until its slot is needed or final flush. It
follows that the next state T contains Q_j and is a maximum-size subset, of size
min(2, |S union Q_j|), of S union Q_j. The recurrence is

    C_j(T) = min_S [C_(j-1)(S) + |T minus S|],   C_0(empty)=0.

Keeping the least cost for each T preserves every future possibility. Final
evictions cost no loads, but every load has exactly one eviction and both are
included in the route/exchange invoice. The verifier records the full attaining
state sequence, independently compares a farthest-next-demand implementation,
and tests both against an unrestricted finite state recurrence allowing
prefetch and early eviction on all request words of length up to four over
three families. The written reduction, rather than these small tests, justifies
the restricted recurrence for the full source word.

For the actual forward and reversed windows the minimum is **542 loads**.
PR2481 reloads per event and uses 2*303+10=616 loads. Residence reuses 83
already present slots at the 312 internal boundaries; nine event request slots
are kept only for future use at snapshot boundaries, so 83 is not the saving
616-542. The plan is not a global optimum for arbitrary reversible algorithms.

## Complete outer invoice and tradeoff

With L=542 loads and E=313 events, there are 2L=1084 routes and 1084 exchanges.
Every exchange costs three packet XOR scans and every event one: 6L+E=3565
P-record XOR passes. There are no fresh outer payload records, CLEARs or
disposals. Two P-record dirty banks are borrowed throughout the window.

Each exchange scans the whole relevant N_i-record family once, touching only
its P owned records. Its charged outward/return movement is 2N_i family-head
steps and 2P bank-head steps. Every update charges 4P head steps and two returns.
Finite child route swaps/XORs/head steps are counted separately by the inherited
route interpreter. Header predicates, scheduling control, full stream motion,
uniform route compilation and private scratch admission are not free or proved
by the payload identity.

| Adapter for the same word | Dirty banks | Routes | Exchanges | Outer XOR/P | Restoration |
|---|---:|---:|---:|---:|---|
| PR2481 | 2 | 1232 | 1232 | 4009 | Every event |
| This fixed-model optimum | 2 | 1084 | 1084 | 3565 | Whole window |
| PR2519 | 1 | 1232 | 626 | 2191 | Every event |

PR2519 is a different valid schedule and is outside the minimum just proved.
This result reduces route calls while using more exchanges, XORs and borrowed
capacity than PR2519, with a weaker intermediate ownership guarantee. No
overall runtime dominance, additive saving, improved moment or new kappa
follows. Nonconstant context-dependent route tariffs also prevent inferring a
general weighted cost comparison from call counts alone.

## Source-bound finite evidence

The unchanged PR2448 constructor authenticates the exact PR2407-derived RAW6
window [9070,9384], with 303 ordinary events and ten snapshot taps. The retained
source digest is 856873eac7d6d9d737e83a28c321b6e760ee183d9648bd98e80761b8d4dc9aba.
The endpoint is independently obtained from the 319-event split baseline.

The complete GL2(Z/9) fixture has 111 families of 3888 records, 81 owned records
per family, an immutable 81-record snapshot and two arbitrary 81-record dirty
banks. All 431811 input records are formal independent atoms. All 431568 family
outputs, including 422577 unowned records, are checked against direct full-ring
matrix multiplication, separate from the reused carry route compiler. Resident
logical values and parked dirt are checked at every event; evicted originals
are checked on every return. Forward and reverse fragments pass separately.

Seven reason-bound mutations reject dirty-copy substitution, a missing final
flush, missing inverse routing on eviction, wrong resident bank ownership,
omitted carry arithmetic, a transient snapshot write attempt and changed tap
chronology. The last mutation preserves the event inventory. A modified result
receipt must also reject after replay. Source hashes are checked before import;
a fresh empty bytecode namespace prevents retained loaders using stale local
caches during this verifier's run. That hygiene is not a hostile-code sandbox.

The fixed reduced fixture is not the selected GL64 owner chart, a uniform
compiler, a complete bit-time supplier or a full multiplication theorem.
