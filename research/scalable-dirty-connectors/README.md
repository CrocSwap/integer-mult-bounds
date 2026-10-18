# Sharp dirty-connector boundaries and a scalable attaining family

This package establishes two optimality results for the universal arbitrary-dirty
F2 connector with **two calls to each source map and two calls to each output map**:

- **Fixed-z0 five-source optimum:** eight paid bidirectional root transfers are
  necessary and sufficient when every source and output call uses physical z0.
  The attaining word improves PR1887's ten-transfer construction by 20% in
  transfer count, changing the source word as well as its readout boundary pairs.
- **Two-root scalability boundary:** two roots cannot realize every nonzero
  source mask for `n >= 6`, even with arbitrary invertible root-frame changes
  and any physical port on each call. Three roots are optimal at six sources.

An attaining family for every `n >= 4` uses `n-3` arbitrary dirty root rows and
pays `8(2^(n-4)-1)` full-row XORs. Each source keeps one physical port; every
output reads root zero. The source and output lower bounds are attained
**simultaneously**, with root rows and transfers explicitly added to the bill.
Root-count optimality for n>=7 remains open.

The attaining family supplies the three-root six-source upper bound. This
package reports scoped optimality results and exact invoices; it makes no
measured-runtime claim.

There is **no new integer-multiplication exponent or selected-supplier claim**.
The construction changes the interface by admitting more dirty roots and
paid star transfers. Its profitability depends on complete child, port,
transfer, hosting and preparation costs.

## Exact interface and invoice

The source rows `x_j`, target rows `y_m`, and roots `z_i` are distinct and
arbitrarily dirty arrays over `F2`. For every nonzero `n`-bit mask `m`, perform

```text
y_m += A_m( XOR_{j: m_j=1} B_j(x_j) ).
```

Sources, coefficient tables and all roots must be unchanged afterward.
The maps are arbitrary compatible linear maps, including rectangular,
singular, nonsymmetric and noncommuting maps. The schedule depends on the
target masks, not data values. The only data operations are complete additive
calls `B_j: z_p += B_j(x_j)`, `A_m: y_m += A_m(z_p)`, and paid root shears
`z_p += z_q`. A complete child restores private scratch and any agreed frames
and head positions. Its private scratch excludes every data/root row. Targets
remain unobserved until the batch completes. No clean full row is supplied.

The scalable family needs only shears `z_0 += z_i`, for `i > 0`. The separate
fixed-port five-source result below uses both shear directions.

| Sources | Star roots | B, star / extra | B, Gray | A, star / Gray | A, extra | Star XORs |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 1 | 8 | 8 | 30 | 30 | 0 |
| 5 | 2 | 10 | 12 | 62 | 64 | 8 |
| 6 | 3 | 12 | 16 | 126 | 156 | 24 |
| 7 | 4 | 14 | 24 | 254 | 368 | 56 |
| 8 | 5 | 16 | 32 | 510 | 828 | 120 |
| 9 | 6 | 18 | 48 | 1,022 | 1,794 | 248 |
| 10 | 7 | 20 | 64 | 2,046 | 3,814 | 504 |

Both one-root comparators use one dirty root and zero transfers. The extra-
readout family fixes a restored `2n`-call interleave source word and chooses a
minimum-cardinality **even** subset of source-prefix boundaries for each
output. A subset DP emits the calls; an independent pair-difference BFS checks
every output's minimum on that fixed word. PR943's five-source extra-readout
repair and PR1185's six-source `12+126+30=168` query floor already establish
this tradeoff. The later review supplies attaining interleave words at n=6..8;
we verify their invoices, not a new global word-optimality census.

The n=4 core and n=5 one-way savings are prior work. The one-root six-source
value 16 is optimal **when every output is restricted to two readouts**;
it is not a lower bound when more A calls are allowed. Beyond n=6 the Gray
count is an achieving upper bound. All schedules have exponential instruction
counts because there are `2^n-1` distinct outputs.

For complete prices, let `g_j` be the actual B multiplicity in the one-root
Gray word, and `r_m` the extra-readout multiplicity; `p_j=0` for `j<4`, otherwise `p_j=j-3`. Let `H` pay initial
admission/layout, root reservation, reusable coefficient preparation, schedule
generation, instruction storage/reads/dispatch, and all costs omitted from the
complete child and shear prices. Then

```text
C_star = H_star + 2 sum_j c_Bj(p_j) + 2 sum_m c_Am(0)
         + 8 sum_{i=1}^{n-4} 2^(n-4-i) c_X(0,i).
C_gray = H_gray + sum_j g_j c_Bj(0) + 2 sum_m c_Am(0).
C_extra = H_extra + 2 sum_j c_Bj(0) + sum_m r_m c_Am(0).
```

The adoption test against these comparators is `C_star < min(C_gray,C_extra)`.
Port independence and equal B prices require justification by an actual caller.
Against Gray, with equal B prices and equal shear prices it becomes
`(G(n)-2n)c_B > T(n)c_X + H_star-H_gray`, where
`G(n)=2^floor(n/2)+2^ceil(n/2)` and `T(n)=8(2^(n-4)-1)`.
Against the stronger minimum-B baseline with no port premium, adoption needs
`sum_m (r_m-2)c_Am > T(n)c_X + H_star-H_extra`; there is no B-call saving.
At n=6 this trades 30 A calls for 24 shears and two extra roots; at n=8, 318 A
calls for 120 shears and four extra roots. Other schedules may offer a better
weighted bill, so beating these two comparators is not a global cost optimum.
Recursive depth-five B calls use 28 dense leaves and three private dirty rows;
the star needs `n-3+3=n` borrowed rows versus four for either one-root baseline.
All input/output rows remain reserved too.

## Construction and all-n proof

Put `s=n-4`. Reserve center `z_0` and leaves `z_1,...,z_s`. Write
`h_j=B_j(x_j)` and initial dirty roots `d_i`. A frame indexed by
`u in F2^s` has center dirty covector

```text
d_0 + sum_i u_i d_(i+1).
```

One Gray edge toggles one `u_i` by a paid `z_0 += z_(i+1)`. Other physical
roots are unchanged. Center injections have normalized axis `e_0` at every
frame.

First run the closed two-source cycle `B0 B1 B0 B1`, whose prefix states are
`0,1,3,2,0`. At each of its four distinct prefix states, tour every `u` using
a reflected Gray path; alternate forward/reverse paths so consecutive tours
share endpoints. Four tours finish at `u=0`. Next inject each `B_j`, `j>=4`,
**once** into leaf `z_(j-3)` at that zero frame. Each leaf now contains
`d_(j-3)+h_j`.

Run the second cycle `B2 B3 B2 B3` with the same four alternating frame tours.
It also finishes at `u=0`. Finally call each extra B again at its same leaf
port. Thus all bulk source responses and extra leaf responses cancel, and
all arbitrary dirty roots are restored.

Write a requested mask uniquely as `m=a | (b<<2) | (c<<4)`, with `a,b` two-bit
masks and `c` an s-bit mask. Read `A_m` at first-phase bulk prefix `a`, frame
`u=c`, and at second-phase prefix `b`, the **same** frame. The two center rows
are respectively

```text
d_0 + sum_i c_i d_(i+1) + sum_{j<2} a_j h_j,
d_0 + sum_i c_i d_(i+1) + sum_{2<=j<4} b_(j-2) h_j
                        + sum_{j>=4} c_(j-4) h_j.
```

Their XOR is exactly the desired source sum, and linearity of `A_m` cancels
all dirt. The variable `b` in the second expression is the two-bit mask;
`h_j` denotes the map response. Each requested mask is read once in each
phase. Skip mask zero. `connector.py` emits every readout as a paid operation.

There are eight tours of `2^s-1` edges and no setup/teardown bridges, giving
exactly `T(n)`. Each source occurs twice; each of `2^n-1` outputs twice.
The proof uses no invertibility or commutativity of the maps.

These map-call counts are optimal in this alphabet, independently of root
count. A generic active source needs a B call to affect its outputs. One B
call injects a nonzero root coefficient vector; later invertible root shears
cannot erase it, and A calls leave roots alone, so at least two are necessary.
One A call sees a nonzero dirty covector because the root frame is invertible;
it cannot cancel arbitrary dirt, so every active output also needs at least
two. **Even B multiplicity is not generally necessary with several roots**:
three distinct injection axes can sum to zero. The verifier includes a
restoring three-call excursion as a positive control for this distinction.
Adam Gall's [PR1915](https://github.com/CrocSwap/integer-mult-bounds/pull/1915)
already uses phase normalization and an order-three odd-parity control for
paid invertible frames on one connector. The new obstruction below extends
the normalized-axis argument to the two-root, n>=6 paired-call model.

## Why two roots stop at five sources

This obstruction assumes exactly two B calls per source, exactly two A calls
per output, arbitrary invertible root frame changes and restoration. It allows
any physical port on each occurrence and places no bound on frame-change cost.

Normalize a source injection by the current root frame `R`: its nonzero axis
is `R^-1 e_p`. Restoration forces its two normalized axes to agree, say `v_j`.
For chronological source prefix parity `q_t`, a physical root with dirty
covector `r` has source coefficient `(r dot v_j)q_t[j]`. A paired output must
use equal dirty covectors, hence realizes

```text
(r dot v_0,...,r dot v_(n-1)) AND (q_a XOR q_b).
```

The all-ones mask requires a covector responding to every occupied source
axis. In `F2^2`, any nonzero covector responds to only two of the three nonzero
axes. Thus a universal two-root schedule has at most two source-axis classes.
Let `D(w)` contain all differences of source prefixes, even at boundaries where
the favorable covector is not actually available. This gives an upper bound.

The complete closed-word censuses give `max |D|=31` for five sources and 49
for six. `obstruction.py` compares two independent word generators and two
difference engines **for every word**: 945 and 10,395 classes. These maxima
are already known from PR943/PR1185; the new step is applying them to arbitrary
two-root frame itineraries.

At six sources, a one-axis schedule covers at most 49/64 masks. With two
classes of sizes `a,b`, one covector sees both classes and the other two see
one each. Their union covers at most
`|D| + (2^a+2^b-1) - 7`, since zero and all six unit masks lie in both sets.
The `2+4` and `3+3` splits therefore cover at most 61 and 57 masks. For `1+5`,
all 31 masks with the singleton and a nonzero five-bit bulk mask are mixed:
only the common covector can see them. Deleting singleton calls projects `D`
to a closed ten-call five-source word, whose maximum 31 includes zero, leaving
at most 30 nonzero bulk masks. Contradiction.

For larger n, specialize other B maps to zero, discard their calls and unused
output targets, and obtain a forbidden six-source schedule. Hence **two roots
cannot attain the minimum map-call counts for n>=6**, however many frame
changes are allowed. The earlier six-transfer five-source witness establishes
the sharp attainability boundary at five. For six, the new star uses three
roots and therefore minimizes root count as well: a one-root schedule embeds
in the forbidden two-root model by leaving a second dirty root untouched.
Root-count optimality for
larger n is not established.

## Fixed-z0 five-source endpoint

The literal word below uses **every B and A at physical z0**, rather than just
one stable port per source:

```text
S10 B0 S10 S01 B1 S01 B2 B3 S10 B0 S10 S01 B4 S01 B3 B1 B4 B2
```

Here `S01` is `z0 += z1` and `S10` is `z1 += z0`. All roots and sources
restore. `fixed_port_five()` inserts all 62 paid readouts at literal boundary
pairs; polynomial/dense replay verifies them. It improves PR1887's pinned
ten-transfer schedule to eight (20% fewer transfers), with identical child
ports and the same 72 child calls. Its leaf count is shared prior work. This settles the broader fixed-port
improvement sought by PR1887's alternative-boundary-pair question. The witness
changes both the source word and readout table; it does not prove that
PR1887's original source word attains eight transfers.

Eight is optimal in this fixed-port, paired-call model. The complete six-X
census has 22 identity direction words, 8,008 placements and 945 pairings per
frame: 166,486,320 skeletons, 34,977,960 legal schedules, maximum 31/32 masks.
Each shear permutes the three nonzero two-bit vectors by a transposition, so
odd-length words cannot restore. Pad a shorter even word with adjacent equal
shears at a boundary; restoration and all old readouts survive. Thus the
six-X exclusion covers every smaller count. The eight-X command replays the literal word and passes its frame through the
same census pairing/coverage engine: 105 legal pairings, one universal. It is
bounded to that frame, **not** an exhaustive eight-X search. The later review
independently reports an exhaustive eight-X physical census with 464,969,376
legal schedules and 828 universal; that run is separate local evidence.

`fixed_port_census.cpp` generates pairings of equal normalized axes; its domain
reduction is the restoration argument above. Its histogram agrees with the
earlier full-pairing search and a separate local physical-row review adapter
that enumerates all directions and filters restoration directly. The adapter
is extra local evidence, not a shipped third engine. `CENSUS.json` records the
complete six-X histogram and the positive fixture.

## Reproduce and verification limits

Standard-library Python 3.12; checks stay active under optimization:

```sh
python3 -I -O -B research/scalable-dirty-connectors/verify.py
```

Expected: `PASS_SCALABLE_DIRTY_CONNECTORS n=4..10 dense=460 rejected=704 extra_rejected=336 fixed_port=8`.
This checks the literal programs and invoices through n=10, 460 rectangular/singular-map forward/inverse cases, all original 704
omission/port/direction/label/schema controls, 336 additional extra-readout
omission/label controls, neutral-extra-pair and odd-source positive controls,
both closed-word censuses, and the independent subset-DP/BFS comparison.
The star/fixed-port paired checks remain strict; only the explicitly selected
extra-readout baseline admits larger even A multiplicities.
The all-n theorem is the proof above; finite replay is corroboration.
`EXPECTED.json` is generated by this checker and guards regressions rather
than furnishing independent mathematical evidence. It deliberately binds
exact serialization. `--write-expected` regenerates it after all actual checks.
The native fixed-port exclusion is separate from this bounded Python hook.

From the upstream repository root, compile **one native command at a time**.
On Linux a configured C++20 `c++` works; this Mac's default linker rejects the
selected SDK, so use the tested Xcode compiler and SDK explicitly:

```sh
/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++ \
  -target arm64-apple-macosx26.5 \
  -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk \
  -O3 -std=c++20 -Wall -Wextra -Wpedantic \
  research/scalable-dirty-connectors/fixed_port_census.cpp -o /tmp/fixed-port-census
/tmp/fixed-port-census 6
/tmp/fixed-port-census 8
```

In this math repository, prefix `research/` with `integer-mult-bounds/`.
macOS SDK/toolchain details and actual verification records are in TASK.json.
The opt-in upstream hook uses `scripts/research_package.py --package
research/scalable-dirty-connectors`. No dependencies or external replay inputs
are needed; source pins are historical provenance. No Lean proof, independent
human review, hosted CI, selected-supplier cold replay, caller admission or
head-return tape integration is claimed.

## Open next questions

The structured questions in TASK.json cover three useful next steps:
find a real recursive caller with these maps and stable ports and price its
full adoption inequality; reduce roots for n>=7 without losing the minimum
map-call count; and realize the paid frame/child program on a concrete tape
layout. The first is blocked by the absent caller contract, the second by the
lack of an attaining lower-root word, and the third by absent caller/head
layout. Each should start with a bounded positive fixture and full invoice.

## Credit, sources and scope

Ross Richardson's [PR934](https://github.com/CrocSwap/integer-mult-bounds/pull/934)
and [PR943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) supply the
dirty query contract, complementary-subspace core, five-source obstruction,
extra-readout repair and balanced recursive echoes. Their retained NOTICE
credits the PR889 common-factor fanout and Chafik Boukhalfa's PR628 dirty
commutator lineage. Douglas Colkitt's
[PR1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) supplies
the six-source one-root census, general Gray bound and extra-readout budget.
The later agent review supplied the attaining interleave extension and
identified the stronger one-root comparator; it is credited here
rather than treated as a new source-call discovery.

Paid one-way two-root predecessors include woklerx's
[PR1438](https://github.com/CrocSwap/integer-mult-bounds/pull/1438), Gareth
Davidson's [PR1498](https://github.com/CrocSwap/integer-mult-bounds/pull/1498),
and Sagar Thakrar's [PR1767](https://github.com/CrocSwap/integer-mult-bounds/pull/1767).
Cinna Davis originated the eight-transfer word in
[Discussion1412](https://github.com/CrocSwap/integer-mult-bounds/discussions/1412).
Hanson Sun's [PR1615](https://github.com/CrocSwap/integer-mult-bounds/pull/1615)
proved the sharp one-way eight-transfer threshold before @nedveder's
[PR1812](https://github.com/CrocSwap/integer-mult-bounds/pull/1812), which also
verifies that threshold and asks the bidirectional question. Those
port/direction contracts differ from the fixed-z0 bidirectional optimum here.
Cinna Davis's [PR1887](https://github.com/CrocSwap/integer-mult-bounds/pull/1887)
already uses both directions at fixed z0 ports and publishes the shared
180-versus-182 leaf comparison. Our eight-X result supplies a lower-count fixed-port word in response to its
alternative-boundary-pair question, changing the source word as well. Cinna Davis's
[PR1675](https://github.com/CrocSwap/integer-mult-bounds/pull/1675) treats a
different signed target. Adam Gall's
[PR1915](https://github.com/CrocSwap/integer-mult-bounds/pull/1915) supplies
the one-connector phase-normalization and odd-parity framed control; these
techniques are inherited, while the two-root n>=6 obstruction is new.

Adam Gall's concurrent [PR2065](https://github.com/CrocSwap/integer-mult-bounds/pull/2065),
at `2721b1e31d718a6e70266a99521f629ce2e1d259`, supplies the six-transfer
five-source endpoint when ports may differ between calls. It is credited
predecessor evidence here, not a new claim. Its port-changing witness differs
from the fixed-z0 optimum, and it does not claim the n>=6 two-root obstruction.
Adam Gall's [PR2063](https://github.com/CrocSwap/integer-mult-bounds/pull/2063)
prices all positive map tariffs for five sources and one root; Aaron Wang's
[PR2056](https://github.com/CrocSwap/integer-mult-bounds/pull/2056) adds combined
pair-source calls. Aaron Wang's subsequent
[PR2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128), at
`697369a971eed02c0fbcd75ebefec9f59945f08e`, extends that pair-source alphabet to
six sources with a fourteen-call source word. Pair-source calls are excluded
here, so its six-source construction has a different contract from our
ordinary-call two-root obstruction. These are different alphabets/domains
from the results here.
Cinna Davis's [PR2134](https://github.com/CrocSwap/integer-mult-bounds/pull/2134)
is a six-source one-TRIO census with sixteen source-map applications; its
combined call and nonminimal source multiplicities are likewise excluded here.

New claims are the all-n star compiler/fully priced tradeoff, the unrestricted
frame two-root minimal-call boundary, and the eight-transfer fixed-z0 optimum.
Canonical-main guidance was reread at
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. This is an
explicitly changed-scope interface side result, not a completion of revision 4's
central supplier handoffs. TASK.json records the fresh overlap audit and its
limits; absence of a match is not a novelty guarantee. Historical scientific
source pins are preserved.

Prepared by @conorholds. Substantial AI assistance was used in mathematical
derivation, implementation and checking. No independent human peer review or
proof-assistant verification is claimed. Apache-2.0; predecessor attribution
and source notices are retained.
