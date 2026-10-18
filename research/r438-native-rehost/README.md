# Native checks and hosted emission for the R438 bit supplier

**A complete finite native/hosted replay of the PR2423 improvement. No new κ.**
This package takes the explicit native-emission handoff in commdata2338's
[PR2653](https://github.com/CrocSwap/integer-mult-bounds/pull/2653) and
[Discussion1289](https://github.com/CrocSwap/integer-mult-bounds/discussions/1289).
It emits Sagar Thakrar's fixed transported R438 word and rehosting selection,
checks the actual emitted owners against the independent geometric certificate,
and runs the complete native, parent, hosted and exact-price pipeline.

The circuit, selection and predicted endpoint belong to the predecessors.
The new result is their source-bound emitted realization and complete finite
replay, including the previously untested rank-34 remainder. This does not
promote a selected supplier or settle the inherited all-size interfaces.

| Complete bill | Selected PR589 control | PR2423 emitted candidate |
| --- | ---: | ---: |
| Dirty helpers per local call | 439 | 438 |
| Local ADDs, including compensation/restoration | 24,305 | 24,248 |
| Local COPY / ERASE pairs | 9 | 9 |
| Local paid rank mass | 5,129 | 5,121 |
| Whole hosted helper occurrences | 126,432 | 126,144 |
| Paid recursive children | 904,896 | 904,320 |
| Global paid rank mass | 1,808,352 | 1,808,352 |
| Live data families | 28,416 | 28,416 |
| Nine-stage precision charge | 192 bits | 192 bits |
| Two-level precision charge | 512 bits | 512 bits |
| Exact bit endpoint | 0.001733427039589844234749 | **0.001734846264120199151475** |

Both moment engines accept the reported endpoint and reject the next point
on the `10^-24` grid. The candidate is about 0.08187% above the selected bit
endpoint. The selected complex endpoint remains
`0.001675462676808103522925`, below both; the selected overall result remains
`κ = 836330098538459/500000000000000000`. This work does not combine pending
complex claims with the bit candidate.

## What is implemented

Ali Romman's PR1043 `pipeline.py` is imported from its pinned source without
editing it. Its selection callback is replaced with a small adapter that writes
PR2423's published patterns and stage demands. No emission, geometry, mutation,
precision or moment acceptance predicate is replaced. The old selection format
requires a floating heuristic field; the adapter recomputes that metadata using
the predecessor formula, but it is not used to certify a price or optimum.

The original baseline and the candidate both run through the unchanged C++17
legality checker and native five/nine/eleven-stage formal-column checkers.
The candidate has 882/1,326/1,548 formal columns; the baseline has
883/1,327/1,549. Local arbitrary-dirty replay covers all 660 candidate inputs,
and the original H1–H5 flags and their conclusions all pass.

The unchanged supplier pipeline then emits and audits the parent and hosted
programs and computes the complete invoice. The new `bind_emitted` bridge
compares all 126,144 **actual emitted** helper owners to PR2653's independent
slot expansion, physical family identities and projector supports. It also
compares every emitted remainder histogram, requires the local programs to be
unchanged by hosting, and independently recounts the global profile from those
program costs and emitted remainders. The owner/projector digest must equal
PR2653's independently reconstructed digest.

The rank-34 remainder is the actual complement `[30,64)` of the helper slice
`[22,30)` inside child 6's pending `[22,64)` space. It occurs once per replica
and is charged 32 times. Deleting a helper returns 72 idle-rank units per
replica (2,304 globally); those charges are retained. The global profile is
`{1:380736,2:400352,3:22752,4:26880,5:29376,6:17376,7:26496,34:32,42:320}`.
The maximum child remains 42, with `2*42^2 < 64^2`; the row coefficient is
18,355, below 20,161. All source access, nine copied totals, local cleanup,
whole-helper occupancy, idle remainders and bridge work are included by the
unchanged pipeline.

## Reproduce

Python 3.12, C++17 and Boost headers are required. Install the recorded Python
versions in a virtual environment using `requirements-native.txt`. Set `CXX`
if needed, and `BOOST_INCLUDE` to the directory containing `boost/` if it is
not `/usr/include`. From the repository root, run:

```sh
python3 -B research/r438-native-rehost/verify.py
```

Expected last line:

```text
PASS_R438_NATIVE_REHOST native=5,9,11 owners=126144 children=904320 c=0.001734846264120199151475 no_new_kappa
```

The default uses a temporary directory and compares the entire normalized
certificate with `CERTIFICATE.json`. `--output /absolute/new/directory` retains
the emitted templates, commands, logs and full receipts. The destination must
not exist. Only timing, toolchain metadata and the pipeline's explicitly
historical cited-PR548 outer assembly are excluded from the new certificate;
all mathematical fields of its native and hosted receipts are retained.
The inherited geometry JSON includes elapsed time. Every original geometry
and template hash is checked within its own run, then `semantic_*` digests
omit only `geometry.seconds` and rebind that stable geometry digest inside
the templates. That digest binds every other geometry field; the full generated
geometry remains in the replay output rather than adding a second large copy
to this package.
Source archives are byte-pinned; template identity uses decompressed canonical
JSON, and histogram keys are normalized before comparison.

The registered standard-library command is deliberately a **local-only**
check: `python3 -B scripts/research_package.py --package research/r438-native-rehost`.
It rechecks source pins, both local words, the exact projector certificate and
three candidate faults. Its marker says `native_not_run`; it does not stand
in for the full command above. All modes reject `-O` because inherited engines
use assertions. `--write-certificate FILE` is an explicit fresh-output mode
for rebuilding evidence, not a comparison against the committed certificate.

## Failure detection and scope

The complete run retains 96 native omitted-bridge controls across the two
words, 34 parent-template mutations and 32 hosted-template mutations.
PR2653's ten geometric controls/witnesses are replayed. Nine new controls
reject omitted cleanup, omitted dirty compensation, the old transport frame,
a wrong emitted port, a wrong replica, an equal-width wrong slice, an omitted
or undercharged rank-34 remainder, and a deleted emitted local instruction.
The selected R439 program is the positive end-to-end control.

This is finite conditional construction evidence, not a formal proof of the
full multiplication theorem or an implementation of its physical machine.
The common-label/mutable-source realization, correlated whole-call hosting,
injective cover/all-size compiler, recursive physical storage and routing,
precision/tape and analytic-transfer contracts remain inherited. Native scalar
columns alone do not prove those contracts. PR2653 supplies the geometric
argument, which is reused and bound to the emitted program here; it is not
presented as a new independent proof. The historical PR548 outer assembly
happens to execute inside the original pipeline, but is not used as the
current frontier or as evidence for a new κ. The selected cold replay, full
repository suite and Lean are outside this contribution.

Exact sources are in `SOURCES.json`; the task, three alternatives, seed 08,
local claim, overlap coverage and stopping rule are in `TASK.json`.
Research base: `389fa10d714f5b40afe624908e487eb5e424498d`.
Dependency heads:

- PR1043, Ali Romman: `e309e17f83f5759b1ea1fa24a76f24838784cb4d`.
- PR2423, Sagar Thakrar: `13cd273dc13c98244b1f9bcf588b6e828cbc0347`.
- PR2653, commdata2338: `ff26f4477786cf9ab188e060d6820a39dd2ed117`.
- PR589, DreamingOfClouds: `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.

PR1043 is archived but remains partially reviewed; PR2423 and PR2653 were
incorporated only within their explicitly scoped reviews. Their unresolved
native-emission handoff, not their merge status, motivates this work.

## Open next questions

Review this exact emitted candidate against the retained all-size physical
interfaces before any supplier admission. The concrete first step is to bind
its local program and owner digests to those compiler/hosting hypotheses;
finite native execution does not supply a complete physical routing proof.
Any future overall improvement also needs a stronger admitted complex supplier.
No further packing or transport search was performed here.

## Credit and license

Prepared by **@CubeJerry**, with substantial **OpenAI Codex assistance** in
scoping, implementation, mathematical checking and writing. No independent
human review or proof-kernel certification is claimed.

Credit Ali Romman for helper470 deletion and the complete source pipeline;
Sagar Thakrar for the transport, optimal fixed-slot layout and predicted price;
commdata2338 for the pending-projector proof and independent census. Retain
DreamingOfClouds, eumemic, DaysSky, Zhihao Chen, chafreaky, the PR555/543/545/510
and PR442 hosting lineage, PR1023 packing, and the seed72/seed14 window work.
Their sources and notices are imported unchanged. New material is Apache-2.0.
