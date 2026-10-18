# Eight paid transfers are exactly necessary for the two-connector universal batch

**Scoped exact result for an enlarged connector alphabet; no new kappa.**
This answers open question 1 of Gareth Davidson's
[PR1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498)
(head `b7baacc8048ab11d31751aee065206f2725a1a16`), which proved that the
universal five-source batch with two dirty connectors needs **at least six**
one-way transfers and left six-transfer sufficiency open.

**Six transfers do not suffice. Eight do, and eight is the exact minimum.**
In the incidence-minimal family (every B and A operator called exactly
twice), an exhaustive census of all 242,161,920 six-transfer schedule orbits
(74,692,800 restored) attains at most **31 of 32** masks for every source-port
split. Two independently written C enumerators agree on every per-split
coverage histogram. Fewer transfers reduce to six by padding, and odd counts
cannot restore the connectors. Two explicit eight-transfer schedules realize
all 31 nonzero masks and are replayed in free noncommutative algebra and on
dense F2 matrices with arbitrary dirty rows.

## Exact interface (unchanged from PR1498)

Five read-only arbitrary source rows x_j, 31 arbitrary output rows y_m (one
per nonzero mask m in F2^5) and two arbitrary dirty connector rows z0, z1.
The target is `y_m += sum_{j in m} A_m B_j x_j`, with sources and both
connectors restored, for generic exact F2-linear A_m, B_j (no commutation,
invertibility or other identities). The complete operations are

    B_j(p): z_p += B_j x_j     A_m(p): y_m += A_m z_p     C: z0 += z1

with p in {0,1}, each child complete and fully priced as in PR1498. The
second connector and C are the alphabet extension relative to Ross
Richardson's [one-connector boundary](../universal-connector-boundary/README.md).
The claim concerns the **72-operator-call family**: exactly ten B calls and
62 A calls, plus t transfers. It does not cover words with extra operator
incidences, reverse transfers, resets, mutable sources or special maps.

## Argument

1. **Ports of a source agree.** z1 changes only through B calls on z1, so
   restoring z1 forces both calls of B_j onto the same port. A source set
   J1 writes z1; the rest write z0. Let r = |J1|.
2. **Paired readouts.** Track formal dirt markers e0, e1 and source
   increments b_j. Two readouts of a generic A_m cancel dirt exactly when
   the two read values have equal dirt coefficients; their source difference
   is then the realized mask. Both enumerators collect every (row, cut) value;
   the literal one also admits cross-row pairs and finds none.
3. **Transfer count.** Each C adds e1 to z0, so restoration needs an even
   count. A schedule with 0, 2 or 4 transfers can be padded at exit with
   adjacent cancelling C pairs, preserving its readouts; a universal schedule
   with at most five transfers would give a universal six-transfer schedule.
   (PR1498 uses the same padding reduction.) Hence the census at t = 6 decides
   every t <= 7.
4. **Six-transfer census.** Relabelling sources acts freely on labelled
   schedules and preserves coverage size. Method A enumerates each S5 orbit
   once as a first-occurrence canonical source word (945) times a port set J1
   (32) times a transfer placement (C(16,6) = 8008), using the derived formula
   z0 source part = q0 + S. Method B uses an independent quotient: J1 is the
   first r labels, the z1-word and z0-word are separately canonical, and three
   streams are interleaved by recursion, with a literal two-row simulation.
   Both cover 242,161,920 orbits, and their six per-split histograms agree.
   The maximum coverage is 31 for every r.
5. **Eight-transfer witnesses.** The skeletons in [EXPECTED.json](EXPECTED.json)
   are expanded into complete 80-call words by choosing, for each mask, the
   first dirt-equal readout pair. Replays check every source, both connectors
   and all 31 outputs.

| Transfers t | Max masks, splits r = 0..5 | Universal orbits |
|---:|---|---:|
| 4 | 31, 31, 21, 17, 19, 31 | 0 |
| 6 | 31, 31, 28, 22, 23, 31 | 0 |
| 8 | 31, 32, 31, 27, 24, 32 | 2,502 (r=1: 2,376; r=5: 126) |

The t = 4 row is consistent with PR1498's split bounds 31, 31, 25, 17, 19, 31
and reproduces its threshold. The t = 8 census (384,199,200 restored orbits
of 1,323,241,920) is recorded from both methods, which agree exactly. Only a
single source on z1 or all five sources on z1 admit universal schedules there.

Witness with **one source on z1** (`B2` is the only z1 source):

    C B0@z0 C B1@z0 C B0@z0 C B1@z0 B2@z1 C B3@z0 C B4@z0 C B3@z0 C B2@z1 B4@z0

Witness with **all sources on z1**:

    B0@z1 C B1@z1 C B2@z1 B0@z1 C B3@z1 B1@z1 C B4@z1 C C B2@z1 C B3@z1 C B4@z1

In the first, the four leading transfers carry only z1's dirt; they change
z0's dirt phase and split the B0/B1 walk into two readout classes. Inside
the B2 window each transfer adds b2 and flips the phase. The all-z1 witness
is consistent with the eight-transfer count that PR1498 attributes to Cinna
Davis's Discussion #1412 for that restricted-port case. That thread could not
be read from this environment, so this is an independent re-derivation, not a
check of its text.

## Completed bill

With complete fixed-port child prices and H the remaining parent work, the
best schedule in this family costs

    T_new = H_new + 2 sum_j c_Bj^(p_j) + 2 sum_m c_Am^(p_m) + 8 sigma.

Ross Richardson's single-connector repair with four readouts of mask 21 costs

    T_old = H_old + 2 sum_j c_Bj^0 + 2 sum_m c_Am^0 + 2 c_A21^0.

The repeated-source repair costs the same with 2 c_B^0 for its repeated source.
With equal complete prices c on both ports, a favorable two-connector schedule
requires `8 sigma + (H_new - H_old) < 2c`. This replaces PR1498's unattainable
necessary condition with six transfers. The second connector is an extra
reserved dirty row (38 root rows instead of 37). PR1498's deliberately
conservative one-head transfer backend has `77L^2 + 2L` primitive dispatches
per C in its layout, so that backend would need `c > 308L^2 + 8L`. A
favorable instance would need a much cheaper hosted transfer, for example a
direct row XOR with explicit access and restoration costs. None is supplied.

## Reproduce

Python 3.10+ standard library; a C99 compiler for the native census:

```sh
python3 -I -B research/two-connector-eight-transfer-threshold/verify.py
python3 -I -O -B research/two-connector-eight-transfer-threshold/verify.py --native
python3 scripts/research_package.py --package research/two-connector-eight-transfer-threshold
```

Expected (the second appends `native_T4_max=31 native_T6_max=31 censuses=agree`):

    PASS_TWO_CONNECTOR_EIGHT_TRANSFER witnesses=2 calls=160 controls=372 old945=max31

The default mode reproduces the predecessor's 945-path histogram against its
pinned [CERTIFICATE.json](../universal-connector-boundary/CERTIFICATE.json),
replays both witnesses and rejects 372 mutants. Every single-call deletion,
every A/B port flip, and every z0 readout moved past the next transfer are
rejected. `--native` compiles [native/](native/) and replays t = 4 and t = 6
with both methods in about two CPU-minutes. `--native-eight` replays the
recorded t = 8 census, roughly ten CPU-minutes per method. It is optional and
is not registered in VERIFY.json.

## Limits

The six-transfer exclusion is a complete finite computation over an explicit
reduction, not a proof-assistant theorem. Its proof-relevant evidence is
native C code. The Python verifier checks the recorded counts' combinatorial
totals but does not repeat the census itself. No instance of this
multi-output interface is claimed inside the selected supplier. Port prices,
transfer hosting, frames, owner admission, compiler/tape integration,
precision and the outer analytic transfer remain uninstantiated. No selected
certificate, supplier, shared generator or upstream file changes.

## Open next questions

1. **Can a hosted transfer meet `8 sigma + Delta H < 2c` on a real port pair?**
   This decides whether the enlarged alphabet can ever beat the old 74-call
   repair. First step: price a two-address row XOR on the selected tape layout
   with its access, restoration and dispatch. Blocker: no instance of this
   multi-output connector interface exists in the selected supplier.
2. **Do bidirectional transfers lower the count below eight?** Allowing
   `z1 += z0` as well changes the phase structure. First step: add a fourth
   event stream to `census_literal.c`; t = 4 and t = 6 are within the same
   budget. No blocker beyond compute.
3. **Is there a short written proof of the six-transfer exclusion?** It would
   make review independent of native code. First step: for r = 1, split by
   the even number of transfers inside the z1 window. Zero or six give no
   mixed mask, and two reduce to the 945-path census. The four-inside case
   remains. Blocker: r = 1 and r = 2 have no written argument yet.

The same questions are in [TASK.json](TASK.json).

## Coordination and provenance

Base `680967accfd4311f3241dc154e1f434869747b43` (CrocSwap main at session start;
selected kappa 836330098538459/5e17 unchanged). Task card
`connector-alphabet-change`, nonce `924f4a5e0911ff460aa4cc58581a981e`, no reroll;
scope refined (see TASK.json): the operation added is PR1498's transfer C, and this
package settles its exact count.

GitHub API and Discussions were unreachable from this session (HTTP 403 on
REST and GraphQL), so no live claim was posted and the overlap helper had no
remote snapshot. Instead, every CrocSwap PR head from #1100 to #1562 was fetched
by Git and its added Markdown was searched for transfer, two-connector and
six/eight-transfer terms. Only PR1438 and PR1498 address this alphabet, and
neither settles six transfers. Discussion #1412 could not be checked.

## Credit

Prepared by @nedveder with substantial Claude Code (Anthropic) assistance.
Builds on Gareth Davidson's PR1498 (six-transfer lower bound, interface and
padding reduction), woklerx's PR1438 (two-connector alphabet, four-transfer
bound) and Ross Richardson's PR943/PR934 (one-connector model and 945-path
census). Cinna Davis's Discussion #1412 is credited for the restricted-port
eight-transfer claim as described in PR1498. New work is Apache-2.0. No
independent human review is asserted.
