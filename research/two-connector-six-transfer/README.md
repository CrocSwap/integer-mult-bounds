# Eight transfers are necessary and sufficient in the minimal-call connector

**Scoped computer-assisted query bound; no new kappa.** In the universal
five-source, two-dirty-connector model below, exactly two calls to every source
and output operator require **at least eight one-way transfers**, even when
every source may choose either connector. Eight suffice.

The new result is the **six-transfer exclusion with unrestricted source-port
choice**, resolving the first open question in Gareth Davidson's
[PR1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498), pinned at
`b7baacc8048ab11d31751aee065206f2725a1a16`. The matching eight-transfer word
comes from **Cinna Davis's [Discussion1412](https://github.com/CrocSwap/integer-mult-bounds/discussions/1412)**;
its construction is credited, not claimed as new. That discussion's proposed
lower bound fixes all source calls to one connector. We independently replay
its upper-bound word and establish the lower bound for every port partition.

## Exact interface and reduction

There are five immutable arbitrary rows `x_j`, 31 distinct arbitrary output
rows `y_m` indexed by nonzero masks in F2^5, and two independent arbitrary dirty
rows `z0,z1`. For arbitrary compatible F2-linear maps `A_m,B_j`, the requested
operation is

    y_m += A_m(sum_{j in m} B_j x_j),

with sources and both connectors restored. The maps need not commute or be
invertible. Outputs are observed only after the batch completes. The complete
operation alphabet is exactly

    B_j(p): z_p += B_j x_j,       p in {0,1};
    A_m(p): y_m += A_m z_p,       p in {0,1};
    C:      z0 += z1.

Each child preserves other rows and restores its private scratch, head positions
and entry/exit frames. Port access is part of its complete price. There are no
reverse-direction transfers, free copies, combined queries, source mutations,
connector resets, output feedback or direct `A_m B_j` calls. This is PR1498's
extension of Ross Richardson's one-connector alphabet, not a new extension.

The bound concerns **ten B calls and 62 A calls**: two of each active operator.
Any generic schedule needs at least two of each: one B occurrence leaves a
nonzero source contribution in the connector pair under invertible C updates;
one A occurrence leaves an uncancelled nonzero incoming dirt vector in its
output. Thus 72 is the minimum A/B incidence, but schedules with more A/B calls
are outside the exclusion. Their multiplicities need not all be even.

Write `b_j=B_j x_j`, with independent source symbols and dirt symbols `e0,e1`.
Initially `(z0,z1)=(e0,e1)`. Sources add `b_j` to their chosen connector and C
XORs the two formal rows. An A pair realizes mask m exactly when the XOR of
its two observed expressions is m, with **both dirt coefficients zero**.
Removing all A calls therefore leaves a B/C skeleton; any pair of its connector
values at cuts is a potential readout. This criterion is sufficient by linearity
for arbitrary maps. Necessity already follows by specializing to scalar identity
maps and independent input bits. It does not assume that clean-input replay is
sufficient. Outputs have independent targets, so all valid pairs can be inserted
in one chronological word without interfering.

Restoration forces the two occurrences of each B operator to use the same port.
A call on z0 contributes the final connector column `(1,0)`. A call on z1
contributes `(0,1)` or `(1,1)`, according to subsequent transfer parity. Two
contributions cancel only if their columns agree. Consequently it is complete
to assign one port to each source; the checker still verifies final restoration.
Odd C counts cannot restore the two independent dirt columns. Every restored
word with zero, two or four transfers can be padded at exit with cancelling
C pairs to make six, preserving its readouts. Excluding exactly six therefore
excludes every count below eight. Padding is a proof reduction, not a free cost.

## Complete finite exclusion

For six transfers, the entire reduced domain has

    9!! * binom(16,6) * 2^5 = 242,161,920 skeletons.

Pair the ten B positions and label sources by first occurrence: this gives all
945 source words modulo renaming. Six indistinguishable C calls occupy any
weakly increasing list of six cuts among the eleven B boundaries: 8,008 choices.
Assign either fixed port to each of five sources: 32 choices. Adjacent transfers,
initial/final transfers and every source-port partition are included. Source
renaming preserves universal coverage and restoration; no heuristic pruning is
used. A calls are covered by the exact paired-readout reduction, not enumerated
or silently dropped from the bill.

Of these skeletons, **74,692,800 restore both connectors**. None covers all
32 masks, including zero. The exact maxima and restored counts are:

| Sources writing z1 | Restored skeletons | Maximum masks covered |
|---:|---:|---:|
| 0 | 7,567,560 | 31 |
| 1 | 21,621,600 | 31 |
| 2 | 25,225,200 | 28 |
| 3 | 15,069,600 | 22 |
| 4 | 4,624,200 | 23 |
| 5 | 584,640 | 31 |

[EXPECTED.json](EXPECTED.json) contains every coverage-bin multiplicity.
[census.cpp](census.cpp) generates perfect matchings and transfer cut multisets,
then groups source masks by their dirt signature. [independent.cpp](independent.cpp)
instead generates instructions chronologically, choosing first/second source
occurrences and ports as it goes. It carries full seven-bit source/dirt vectors
and filters pair differences by the dirt bits. Each recursive branch chooses
the next instruction uniquely, so this second generator covers the same domain
without the matching/cut enumeration. The two files share no implementation.
Their entire histograms agree, not just their final maxima.

These are separately implemented checks by the same assisted contributor, not
independent human review or proof-assistant certification. The reduction above
and these exhaustive finite computations establish the stated model bound.

## Credited eight-transfer construction and full price

After exchanging the connector names in Cinna Davis's fixture, all B calls
write z1. The source word and C insertion boundaries, measured by preceding
B calls, are

    B word:       0,1,2,0,3,1,4,2,3,4
    C boundaries: 1,2,3,3,4,6,8,9

[CERTIFICATE.json](CERTIFICATE.json) records the literal 18-step skeleton and
all 31 readout pairs. Mask 21 reads z0 after the third and seventh transfers;
the other masks can use z1. Both connectors restore. Expanding the readouts
gives **ten B, 62 A and eight C calls: 80 total operations**. Free
noncommutative polynomial replay checks every row, arbitrary incoming dirt and
both word orientations. This is an algebraic all-map identity, separate from
the supplementary finite dense-matrix tests.

Let `c_Bj^p`, `c_Am^p` and `sigma` be complete fixed-port child and transfer
prices. Let H pay all remaining admission, coefficient preparation, program
construction, dispatch and frame/control work not already included. With the
certificate's chosen output ports `q_m`, its bill is

    T_new = H_new + 2 sum_j c_Bj^1 + 2 sum_m c_Am^q_m + 8 sigma.

Reserve all **38 root rows**, including two borrowed dirty connectors, plus
the children's private scratch. The old one-connector batch uses 37 root rows.
No clean full row is assumed. For the same complete A/B price c at both ports,
comparison with Richardson's achieved 74-call repair is exactly

    T_new < T_old  iff  8 sigma + H_new - H_old < 2 c.

The previously open six-transfer tariff is unattainable in this minimal-call
family. The displayed favorable condition includes word-specific overhead;
it is not a measured runtime gain or an admitted supplier.

The transfer has a concrete conservative implementation, following PR1498's
priced tape model. Store the 38 length-L rows consecutively and admit one clean
scalar bit. Start at head zero; for each coordinate, load z1 into the bit, visit
z0 and XOR it into the target, revisit z1 to clear the bit, and return to zero.
One complete C uses **3L cell/register XORs and 77L^2-L single-cell head steps**;
source, scratch and head restore. Charge one dispatch per such instruction,
instruction access, loop/control work, preparation and scalar admission in
sigma or H. The verifier checks the tape action and these counts. These are
priced operations, not physical runtime measurements. A/B implementation,
port/frame admission and any selected-supplier instantiation remain obligations.

## Reproduce and verification scope

Python 3.12+ with its standard library and a GCC/Clang C++17 compiler suffice.
No network, downloaded dependencies or predecessor executable is used. From
the repository root, run the **complete** replay:

```sh
python3.12 -I -O -B research/two-connector-six-transfer/verify.py
```

Expected: `PASS_TWO_CONNECTOR_SHARP_EIGHT_TRANSFERS`. Binaries are built in a
temporary directory and normal verification changes no input files. `CXX` can
select the compiler. `--output PATH` writes an optional deterministic receipt.
The dedicated [native workflow](../../.github/workflows/two-connector-six-transfer.yml)
runs both full censuses. [EVIDENCE.json](EVIDENCE.json) records a completed local
replay; hosted CI status is separate.

The replay also checks 12 small domains in both C++ implementations, with a
third set-valued Python multiset-permutation oracle on eight of those domains;
the historical 945-pairing histogram; noncommuting dense banks at widths 1..4
on 380 basis columns in each direction; and the transfer tape at widths 1..5
on 570 columns in each direction. All 80 single-instruction omissions and
seven other wrong-port, output, mask and incomplete-census controls reject.
The guards remain active with `python -O`.

For source metadata and the **upper-bound-only** registered Python hook:

```sh
python3.12 -B scripts/research_package.py --package research/two-connector-six-transfer --check-only
python3.12 -B scripts/research_package.py --package research/two-connector-six-transfer
```

That generic hook intentionally runs `--witness-only` and reports
`PASS_EIGHT_TRANSFER_WITNESS_ONLY`; it does **not** certify the six-transfer
exclusion. Native compilation and the full exclusion have the dedicated replay
above. No selected-frontier cold replay, physical supplier admission, precision
or analytic-transfer proof, Lean theorem or new multiplication exponent is claimed.

## Open next questions

1. **Can extra A/B incidences beat both complete tariffs?** This could change
   the useful interface despite the sharp minimal-incidence obstruction. Start
   with 73 A/B calls, tracking full dirt vectors and charging every port. The
   paired-readout and fixed-source-port reduction used here no longer suffices.
2. **Does a concrete supplier meet the eight-transfer price condition?** Pin
   actual child/port prices, the extra dirty row, frames, scalar scratch and
   dispatch before attempting integration. A legally hosted instance and its
   full cost contract are still missing.

## Sources, coordination and credit

Base main: `ebedc0895eb4c06725af020bc1af165722b0a3ce`. This is the refined
`connector-alphabet-change` card from nonce `7de5e5ad11c402a85f5db9a8f499cac5`;
it keeps the five-source domain and tests the predecessor's specific missing
case. [TASK.json](TASK.json) records selection, overlap and limits.
[SOURCES.json](SOURCES.json) pins the base catalogue, selected context and
Richardson inputs. [PREDECESSORS.json](PREDECESSORS.json) pins the retained
PR1498 README and timestamped Discussion1412 snapshot. No frozen source or
selected record is changed.

Credit **Gareth Davidson (@bitplane), PR1498**, for the four-transfer obstruction,
source-port reduction, priced transfer backend and six-transfer question;
**woklerx, PR1438**, for the two-connector interface and earlier threshold;
**Cinna Davis (@1337isnot1337), Discussion1412**, for the eight-transfer word;
and **Ross Richardson, PR943/934**, for the universal connector, dirty-prefix
criterion and five-source single-connector boundary. Predecessor text is
retained verbatim in `references/`. Their claims are credited with their actual
scopes; this package does not treat a discussion proposal as accepted frontier evidence.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in the derivation, code, verification and writing. New work is Apache-2.0.
The requested Emulate style pass was unavailable. The mathematical and factual
text was reviewed directly against the source records and executable checks.
