# One live COPY reduces the deferred R439 scatter from 94 to 88 ADDs

**Finite construction; no new kappa or optimality claim.** On Sagar Thakrar's
PR1062 R439 word, one retained total can remain copied while the fixed target
undo executes. Ten taps replace sixteen reads of column 0. The complete scatter
uses **88 ADDs**, and the full word uses **11,061**, compared with **94 / 11,067**
for PR2115's known three-gate split. All 306 undo gates remain charged. There
are still nine rank-seven COPY/ERASE pairs, one live private slot, and the same
ordered frame paths and recursive histogram.

This supplies a concrete positive answer to the other-column question in
[Sricharan Vagvala's PR2356](https://github.com/CrocSwap/integer-mult-bounds/pull/2356).
It lies outside the split-ideal class for which
[Charles Bethin's PR2279](https://github.com/CrocSwap/integer-mult-bounds/pull/2279)
proves 94 optimal. It does not contradict that result or improve PR2356's exact
five-tap minimum for column 7. The contribution is this column-0 witness and its
complete finite replay, not a new compensation theorem or an optimal search.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/r439-single-copy-interleaving
```

Direct checks:

```sh
python3.12 -I -O -B research/r439-single-copy-interleaving/verify.py
python3.12 -I -O -B research/r439-single-copy-interleaving/independent.py
```

The primary marker is `PASS_R439_SINGLE_COPY_INTERLEAVING`, with
`scatter=94->88 ADDs=11067->11061 dirty_columns=661 no_new_kappa`.
Ordinary verification consumes the committed `WITNESS.json` and `RESULT.json`;
missing evidence fails. `verify.py --write` explicitly regenerates the receipt.
`verify.py --output /absolute/new-directory` exports the literal candidate record
stream and frames; the directory must not already exist. No optimizer is a
verification dependency.

## Literal witness and complete bill

Keep undo gates **31, 51, 52** in D, as in PR2115. Their indices are zero based
in the original 306-gate undo. Move the remaining 303 gates in their original
order to the scatter interval. First service retained columns 1 through 8,
one COPY/read/ERASE at a time, using the known split's scatter support. Then
COPY column 0 once, execute the 303 undo gates and the taps below, and ERASE.

A cut is the number of deferred undo gates already executed. Target indices are
zero based in the 111-target bank (persistent register is index plus 111).

| cut | target indices receiving the copied total |
|---:|---|
| 0 | 13, 26, 34, 58, 79, 90, 95 |
| 104 | 6 |
| 126 | 24 |
| 182 | 3 |

The copied source is a helper, and every intervening undo gate writes a target.
Consequently the snapshot stays unchanged until its ERASE. The final undo gates
183 through 303 are still executed and paid even though they have no later tap.

| full local schedule | scatter / total ADDs | F | B | local / nine-stage bits |
|---|---:|---:|---:|---:|
| PR1062 source | 527 / 11,500 | 25,717 | 5,911,840 | 95 / 182 |
| PR2115 three-gate split | 94 / 11,067 | 25,717 | 5,024,524 | 95 / 181 |
| this interleaving | **88 / 11,061** | 25,717 | 5,026,856 | 95 / 181 |

B increases slightly relative to the 94-ADD split; a gate saving does not imply
positive-prefix domination. The inherited bounds
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192` both pass with exact integers.
These are this source's normalized positive scalar envelopes, not an all-size
physical precision theorem.

Every row has 2,911 MOVEs, nine COPYs and nine ERASEs, COPY rank sum 63, peak live
COPY slots one, and paid histogram
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, with rank mass **5,129**.
The exponent and supplier selection are unchanged. No rank charge is removed.

## Why the endpoint is correct

Work over F2 on arbitrary source, helper and target inputs. Let S be the original
111-by-9 scatter matrix. Let E be the target preparation, K the product of the
three kept undo gates, and U the product of the 303 remaining gates, in execution
order. The complete target operator is checked exactly: `U K E = I`. The split
scatter is `P = K E S`, hence `U P = S`.

The target undo originally lies before a helper-only restoration tail in D;
it is not the final literal block of D. The verifier checks that this tail and
all of A neither read nor write targets. Thus relocating U across them preserves
their action and the target operator. This observation is necessary for arbitrary
dirty helpers and targets, rather than just clean target tests.

For cut c and target i, let `U_after(c) e_i` be the response at the end of U to a
tap at that cut. For column 0, the ten taps above satisfy exactly

`sum_(c,i) U_after(c) e_i = S[:,0]`.

The other eight columns retain `U P[:,j] = S[:,j]`. Linearity gives the original
scatter for every retained-value vector; no independence assumption about the
actual retained totals is required. Initial dirty targets still undergo the
same invertible operator U. The copied helper is untouched throughout, allowing
literal ERASE. The rest of the original word then gives `(x,y,h) -> (x,y+x,h)`.
All 661 persistent inputs and the clean private COPY slot are replayed through
the full stream forward and backward. The private slot finishes zero.

This is a written argument for the fixed circuit, supported by complete exact
coefficient checks. It is not a formal-kernel proof or exhaustive enumeration of
all interleavings. Discovery tried only one of the initially proposed eighteen
column/order cases and stopped at this successful witness. SciPy/HiGHS nominated
it; neither its floating objective nor its optimal-status flag proves optimality.

## Verification independence and controls

The primary checker adapts PR2356's suffix-column, record-interleaving, and finite
invoice methodology, with predecessor credit retained. It uses the pinned Dylan
Crow exporter and eumemic owner checker. It reconstructs the original source,
the 94-ADD split and the new stream; compares full symbolic states, ordered MOVEs,
COPY lifetimes, rank profiles and positive prefixes; and consumes a fixed receipt.

A separate OpenAI Codex mathematical specialist writes `independent.py` without
importing the primary or predecessor implementations. It reconstructs the
candidate and its forward action independently. The exact scope and review
observations are recorded in `proof-audit.md`. This is algorithmic independence
and a second AI review, not independent human review.

Nine primary controls reject omitted taps, wrong cut/target/retained total,
omitted undo, overlapping copies, premature ERASE, wrong tap frame and underpriced
COPY. Reversing the tap-list presentation is an accepted equivalent control.
`test_package.py` also exercises real entry points, source/witness/receipt faults,
read-only Git-free relocation and removal of a named guard. All checks use
explicit exceptions and remain active under `-O`.

## Source pins, attribution and remaining limits

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
selected-record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
`SOURCES.json` pins every consumed input and predecessor heads. Coordination:
[Discussion2401](https://github.com/CrocSwap/integer-mult-bounds/discussions/2401).
The drawn `bit-helper-contract` card is explicitly changed to the deferred-target
interleaving question because PR1194/PR1311/PR1806 already cover its original
semantic H2/K question. This is a finite scalar/interface result, not completion
of selected-supplier admission.

Credit Sagar Thakrar's PR1062 and deferred basis/split in
PR2115 `b56dceffad83c88e8ad39ffd82a1bdd55c4130da`; Charles Bethin's split-ideal
optimum in PR2279 `81fed971e2269b62eae2ee8e3b6bda394930992c`; Sricharan Vagvala's
interleaving model, column-7 result and checks in PR2356
`8ffeca2cf753d13ac78d90ce159e0037fdfda374`. Gareth Davidson's PR2373
`b52f87f5355ad9f02ca4ac4395117655ac1b19c7` replays a different, non-interleaved
deferred word natively and does not certify this new stream.

Retained lineage: Gareth Davidson's PR915 basis; commdata2338, Scott Woolsey
Biggart and Sagar Thakrar's target-basis work; Sricharan Vagvala's helper stars;
Aaron Wang's B circuits; Ross Richardson's frame circuit; DreamingOfClouds'
PR589 on eumemic's PR555; and the interface/exporter work of Zhihao Chen, eumemic,
woklerx, Arham Tahir and Dylan Crow. Frozen inputs and selected records are unchanged.

The source still fails original syntactic H2/K. Target deferral uses PR2115's
replacement H5 contract. Native parser/address execution with target undo *inside*
a live COPY, 5/9/11-stage native replay, whole-call hosting/invoice, physical
recursive scratch, all-size/compiler/common-label realization, precision/tapes,
exact recovery, analytic transfer and outer assembly remain unexecuted or inherited.
No supplier adoption, stronger selected bound, full cold replay, hosted-CI pass,
full multiplication theorem or optimality is claimed.

Prepared by Ross Richardson with substantial OpenAI Codex assistance in discovery,
mathematics, implementation, independent checking and writing. Apache-2.0.

## Open next questions

First admit this exact emitted stream through the native tools and physical
COPY contract; target-only work now occurs inside a live copied snapshot. Bind
all 303 undo records and all ten taps, and reject a count-preserving reordering
that changes their endpoint. Stop if the parser or physical snapshot contract
cannot represent the chronology. The earlier deferred-word native replay is a
starting point, not evidence for this candidate.

A broader optimization could coordinate several interleaved columns under one
live COPY slot. Independently cheapest column decompositions cannot simply be
combined: their COPY intervals must fit one chronological undo pass. State and
price that lifetime constraint before searching. No such search was performed
here; the structured questions and blockers are in `TASK.json`.
