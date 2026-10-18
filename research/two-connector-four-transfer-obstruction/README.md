# Four paid transfers do not complete the universal five-source connector

**Scoped obstruction for an enlarged alphabet; no new kappa.** Even when each
source operator may choose either dirty connector, **four paid one-way XOR
transfers cannot realize all 31 nonzero five-source masks** with exactly two
calls to every active B and A operator. At least **six** transfers are needed
in this incidence-minimal family. Six-transfer sufficiency remains open here.

This answers the explicit open question in [woklerx's PR1438](https://github.com/CrocSwap/integer-mult-bounds/pull/1438),
pinned at `a61170c97c9ea2c396f6d76a953b0cf74a455cdd`. That work proves at
least four transfers and supplies a two-source mixed-mask example. The new
step is a source-port partition proof that excludes four for the full
five-source target. It reduces the exceptional cases to **Ross Richardson's
existing 945-pairing obstruction**, independently reproduced here; it does
not claim that old census as new.

## Exact changed interface

There are five immutable, arbitrary input rows x_j; 31 distinct arbitrary
output rows y_m, indexed by nonzero masks m in F2^5; and **two independent
arbitrary dirty connector rows** z0,z1. The target is

    y_m += sum_{j in m} A_m B_j x_j,

with every source and both connectors restored. A_m and B_j are arbitrary
exact F2-linear maps of compatible dimensions; they need not commute, be
invertible or satisfy any additional identities. Correctness is generic in
the maps and holds for arbitrary incoming source, output and connector dirt.
Special zero maps or restricted input promises do not satisfy this generic
lower-bound hypothesis.

The only complete operations are:

    B_j(p): z_p += B_j x_j,  p in {0,1};
    A_m(p): y_m += A_m z_p, p in {0,1};
    C:      z0 += z1.

Every B_j and A_m occurs exactly twice: ten B and 62 A calls. Complete child
calls preserve all other rows, private scratch and required head/port/frame
state; their full port-specific prices are charged. The second row and C are
the actual extension of the old one-connector alphabet. There are no combined
queries, direct A_m B_j calls, free copies, source mutations, connector resets,
reverse-direction transfers or output feedback. Allowing B and A to choose a
physical port is a contract requirement with a price, not free rebinding of an
existing implementation. The theorem initially permits each occurrence to
choose a port; restoration forces the paired B ports to coincide.

The claim is about the **72-operator-call family**, not every finite word in
this larger alphabet. In particular, odd operator multiplicities can become
legal with extra calls and changing ports. We do not import the predecessor's
general even-incidence argument into the enlarged alphabet.

## Proof

Write b_j=B_j x_j as independent formal source increments. Let e0,e1 be the
two independent incoming connector dirt markers. A readout contributes the
current connector expression with its output's A_m on the left. Since the
outputs have independent, generic A_m, two readouts cancel dirt precisely
when their two dirt coefficient vectors agree. Their source difference is
then the requested mask. Thus we may remove all A calls while studying the
B/C skeleton, retaining every connector value at every cut as a possible
readout. This is a necessary and sufficient paired-readout criterion, not a
clean-input relaxation.

**1. Source ports are fixed by restoration.** A B call on z0 contributes e0
times b_j to the final connector pair. A call on z1 contributes either e1 or
e0+e1, according to the parity of subsequent C calls. Two such contributions
cancel only when their columns agree. Hence both calls of a given B_j use
the same port, and a source assigned z1 has even C parity between its calls.
Partition the sources into J0,J1 and put r=|J1|. This exhausts even schedules
whose two B occurrences were allowed to choose different ports initially.

**2. Four-transfer projection.** Let q0(t),q1(t) be the XOR sums of source
increments directly injected into z0,z1 up to time t. The sets of coordinates
supporting q0 and q1 are disjoint. For exactly four C calls, let u_i be q1
immediately before the i-th transfer. Since each B occurs twice, connector
restoration requires

    u1 + u2 + u3 + u4 = 0.

Here and below addition is XOR. At transfer phase p (after p transfers),

    z1 = e1 + q1(t),
    z0 = e0 + (p mod 2)e1 + q0(t) + S_p,
    S_p = u1 + ... + u_p.

The even-phase S values are 0,u1+u2,0. The odd-phase values are u1,u4.
Consequently, the J1 projection of a dirt-cancelled z0 readout pair belongs
to

    K = {0, u1+u2, u1+u4}.

A pair on z1 has no J0 component. A cross-port pair cannot cancel dirt:
z1 has marker e1 while z0 has e0 or e0+e1. In particular, a **mixed mask**
(meeting both source groups) can have at most **two distinct nonzero J1
projections**.

**3. Nonempty J0 and r>=2.** Universality requires a mixed mask for every
nonzero J1 projection, for example by adjoining one fixed J0 coordinate.
There are 2^r-1>=3 such projections, more than K can supply. This excludes
every split r=2,3,4 without a schedule census. A coarse coverage upper bound,
including the zero mask, is

    2^r + (2^(5-r)-1) + 2(2^(5-r)-1)
      = 2^r + 3*2^(5-r) - 3.

The first term covers pure J1 masks, the second nonzero pure J0 masks, and
the last mixed masks. These split-specific bounds need not be sharp.

**4. Exactly one source on z1.** Call its increment b. The row q1 is b
between its two B calls and zero otherwise. Therefore its nonzero u_i form
one consecutive block. Restoration makes the block length 0,2 or 4.

For block length 0 or 4, both nonzero candidates in K vanish; no mixed mask
is available. For length 2, strip the dirt markers from the z0 history.
Its source part changes at the eight J0 B calls and at exactly the two C
calls with q1=b. It is therefore the prefix path of a **five-label word in
which every label appears twice**. All paired z0 readouts are among the
differences of that path, even after relaxing the equal-dirt restriction.
The only possible z1 readout differences are 0,b, and both already occur in
the projected path, since its b toggle occurs. The old five-source census
therefore bounds the entire coverage by 31 of 32 masks.

**5. A single source group.** If J1 is empty, z0's source path is precisely
the old five-source path and z1 adds only zero. If J0 is empty, z1 follows
the old five-source prefix path. All possible paired z0 differences are in
K, whose two candidates u1+u2 and u1+u4 are already differences of vertices
of that z1 path. Again the old census gives at most 31 masks.

The old census enumerates every pairing of ten positions: 9!!=945, with
labels assigned in order of first occurrence. The set of source-label
renamings preserves coverage. Its histogram of coverage sizes is

    16:42, 19:120, 21:180, 22:56, 23:45, 24:220,
    26:110, 28:150, 31:22.

Two independently implemented matching/interval enumerations reproduce the
histogram and the pinned canonical digest. This is the explicit finite
dependency of the proof; it is not an unrestricted circuit lower bound.

For r=0,...,5, the resulting upper bounds are **31,31,25,17,19,31**.
The overall bound 31 is attained: use the old maximum-coverage word
`0,1,2,0,3,1,4,2,3,4` on z0 and append two cancelling pairs of C. It misses
mask 21 and realizes the other 30 nonzero masks. The verifier emits and
checks the complete paired-readout word. This deliberately simple sharpness
fixture reuses the predecessor's path; it is not a new five-source solution.

Finally, a schedule with zero or two C calls can be padded at exit with
adjacent cancelling C pairs to get exactly four, preserving all existing
readouts and the ten B calls. Odd C counts cannot restore the independent
incoming dirt columns. Hence **every schedule with at most five C calls
fails**, establishing the necessary threshold six. This padding argument
is a correctness reduction; the added calls are not free in any cost bill.

The projection idea also gives a general necessary condition: for 2k C calls
with k>=1 and two nonempty source groups, the even and odd phases each have at
most k distinct restored offset values. Their within-parity differences
provide at most k(k-1) nonzero J1 projections. Universality therefore requires
`2^r-1 <= k(k-1)`. This coarse condition alone does not settle six transfers.

## Completed cost consequence

Let c_Bj^p and c_Am^p be complete fixed-port child prices, and sigma the
complete price of one C call. Let H be **all remaining** parent preparation,
schedule dispatch, admission/reservation, frame access and exit work, counted
once outside those complete calls. An incidence-minimal candidate costs

    T_new = H_new + 2 sum_j c_Bj^p_j + 2 sum_m c_Am^r_m + t*sigma,
    t >= 6.

Both connectors are real dirty rows: 38 root rows for the five sources and
31 outputs, versus the old 37. Reserve the additional length-L row and all
child private storage; price frame/head movement and restoration on the
actual ports. No clean full row is introduced. This is a necessary lower
bill, not a construction attaining it.

For an explicit implementation of C, `independent.py` provides a simple
one-head bit-tape backend. It **admits and prices one clean scalar scratch
bit**, initially and finally zero. For each coordinate, start at head 0,
load z1[k] into that bit by XOR, move to z0[k] and XOR it into the target,
return to z1[k] and XOR it out of the bit, then return the head to 0.
Source, private bit and head restore. For row bases b0,b1 it uses exactly

    3L cell/register XOR instructions,
    2L*b1 + L*(L-1) + 2L*abs(b1-b0) single-cell head steps,
    one instruction dispatch per XOR or head step.

With the 38 root rows stored consecutively, b0=36L,b1=37L, the head bill is
`77L^2-L`; the primitive dispatch bill is `77L^2+2L`. Program preparation,
instruction access, clean-bit admission and call entry/exit still have their
explicit prices in sigma or H. The verifier checks every dirty tape basis
column and the inverse for L=1,...,5. This deliberately conservative backend
shows the transfer is implemented and charged; it is not a selected native
supplier, a runtime benchmark or a cheapest routing claim. A direct
two-address row-XOR realization has L target XORs, but access and restoration
cannot be replaced by a declaration that C costs zero.

For comparison, the predecessor's actual 74-call repair repeats the output
operator for mask 21 (or uses its alternative repeated-source repair). The
output-repair cost at old port0 is

    T_old = H_old + 2 sum_j c_Bj^0 + 2 sum_m c_Am^0 + 2*c_A21^0.

Any favorable new schedule must beat this complete expression, including
changed port prices and H. Under the **additional simplifying assumption**
of equal complete A/B prices c on both ports, a necessary condition is

    6*sigma + (H_new-H_old) < 2*c.

The former optimistic four-transfer comparison is unattainable for this
family. Even the six-transfer inequality is not sufficient: neither a
six-transfer construction nor its admission to a selected supplier is
provided. Extra A/B calls, bidirectional transfers, special common maps and
mutable sources are separate possible routes, outside this theorem.

## Evidence and reproduction

Python 3.12+, standard library only, no network during replay:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/two-connector-four-transfer-obstruction
python3.14 -I -O -B research/two-connector-four-transfer-obstruction/verify.py
```

The registered replay runs the checker and package corruption controls.
`verify.py --write-expected` explicitly regenerates the deterministic receipt;
normal replay only reads it and compares every field. Guards remain enabled
under `-O`. Exact source and retained-file pins are in SOURCES.json and
REMOTE-SOURCES.json. Retained predecessor text is unmodified.

The evidence consists of:

- Independent old-path enumerations through five sources, including all 945
  five-source pairings and the exact source-bound histogram/digest.
- All **37,449** four-transfer prefix tuples over dimensions zero through
  five, independently checking the projection identity. This is the stated
  finite domain, not an enumeration of every five-source schedule.
- Two complete small-skeleton enumerations for one, two and three sources:
  **30, 840 and 25,200** candidates, including every source-port assignment
  and placement of four transfers. Every restored case checks the proof's
  applicable reduction and the arbitrary-dirt paired-readout criterion.
- A complete two-source universal example using the credited PR1438
  skeleton, and the sharp five-source 31-mask example. Both replay in free
  noncommutative operators, forward and inverse, retaining every independent
  dirty row. Separate dense matrix banks at widths 1,...,4 check **880**
  forward and **880** inverse basis columns, including noncommuting maps.
- Omission of each of the two-source example's **six A, four B and four C**
  calls is rejected. Wrong-port and discarded-dirt controls are also checked.
  The transfer backend separately checks **570** forward and **570** inverse
  tape columns.

The general claim follows from the written reductions and the explicit old
finite exclusion. Dense tests and small schedule censuses support the checker;
they are not an extrapolation to all widths or schedules. No full selected
cold replay, physical supplier admission, contraction, precision theorem,
analytic transfer, Lean proof or multiplication exponent is claimed.

## Coordination and provenance

Single random nonce `03de982dd845f2b40aeaaef2a1eecd7c`, revision-2 recursive
interfaces draw, card `connector-alphabet-change`; no reroll. The prescribed
universal-connector first example and selected baseline binding check passed.
Exact base: `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`. The selected #1094
frontier remains a historical context pin, not an input to this theorem.
Published contribution: [1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498); mathematical commit
`5431fba4a80e30925e0c2b2c161b9c68bbac1c17`.
The original claim and result are in [Discussion1486](https://github.com/CrocSwap/integer-mult-bounds/discussions/1486).

The entry overlap check found PR1438 and [Cinna Davis's Discussion1412](https://github.com/CrocSwap/integer-mult-bounds/discussions/1412).
That separate claim fixes every B write to the transfer's source root and
announces an eight-transfer bound/construction. Here the B ports are freely
chosen and the proved lower bound is six. The present result does not
duplicate or establish its stronger restricted-port statement. PR1340/1370
alter source rows under a common-B hypothesis; that alphabet is excluded.
The overlap tool searches open PR bodies, Discussion records and local
top-level notes, not every code diff or every closed submission; its output
does not prove novelty. Final overlap details are in TASK.json.

## Open next questions

1. **Does six suffice with freely chosen source ports?** This decides whether
   the tightened necessary bill can be attained. First apply the source-port
   projection bound to eliminate r>=3 when both groups are nonempty, then
   search only the remaining six-transfer cases with full dirty restoration.
   The all-B-on-one-root case also needs the separately claimed evidence
   checked. No such search or proof is supplied here.
2. **Can a legal concrete supplier afford the surviving interface?** Before
   implementation, pin its actual port prices, child contracts, extra row,
   scalar scratch, instruction access, preparation and dispatch. Compare its
   whole bill with an achieved old repair. The missing construction and
   actual supplier admission are blockers; call counts alone do not answer it.
3. **Can extra operator incidences beat both tariffs?** Keep the same paid
   operation alphabet and first analyze the 73-call boundary. The paired
   source/readout reductions used here no longer suffice; a new all-word
   argument would be required. The old general parity argument is unavailable.

## Credit

Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex
assistance**. Credit woklerx, Ross Richardson, Cinna Davis and all retained
dirty-commutator/common-factor predecessors; see NOTICE.md and the verbatim
source notices. New work is Apache-2.0. No independent human review is asserted.
