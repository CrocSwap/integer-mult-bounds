# R439 punctured block 1: 35 additions become 30

**Finite bit-supplier construction, with a scoped finite-class optimum. No new
kappa.** PR589's phase-B block 1 can use **30 instead of 35 additions**, with
the same positive integer map on all ten arbitrary inputs. Rebuilding the
required literal reverse cleanup saves five more: the complete local word goes
from **24,305 to 24,295 native ADDs**. Only this research directory is added.

The block includes dirty helper register 465. Its input is never assumed zero.
Every one of the 661 physical registers retains its frame path; all 439 helpers,
nine retained copies, source accesses, restoration and recursive charges remain
accounted for. The positive reverse matrix decreases entrywise. The complete
native payload allowance remains **93 bits**, below the unchanged 104-bit cap.

| Complete local quantity | Original | Replacement |
|---|---:|---:|
| Phase-B block additions | 35 | 30 |
| Corresponding literal cleanup additions | 35 | 30 |
| Native scalar additions, including scatter | 24,305 | 24,295 |
| Native records | 27,234 | 27,224 |
| Frame climbs | 2,911 | 2,911 |
| Positive forward prefix bound | 49,347 | 49,347 |
| Positive reverse prefix bound | 1,113,070 | 1,097,158 |
| Paid rank mass | 5,129 | 5,129 |

The paid histogram is unchanged:
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`.
This is a circuit count, not a runtime benchmark or an exponent improvement.

## Reproduce

Python 3.10+ with its standard library suffices:

```sh
python3 -I -B research/r439-block1-schedule/verify.py
```

Expected final line:

```text
PASS_R439_BLOCK1_SCHEDULE gates=35->30 native_adds=24305->24295 columns=661 rank_mass=5129 controls=13
```

This checks the source pins, the exact factor minima, all 1,024 local Boolean
inputs, the unchanged owning E8/frame/interface checker, all 661 dirty-input
columns, actual exported record semantics and COPY/ERASE lifecycle, complete
positive bounds, the paid profile, and thirteen negative controls. It compares
the complete deterministic report with `CERTIFICATE.json`.

`--output /absolute/new/directory` retains the reconstructed words and native
records; an existing destination is refused. `--write-certificate` explicitly
regenerates only this package's report. Ordinary verification changes no source
or committed artifact.

The exhaustive nomination can also be reproduced, independently of the checker:

```sh
python3 -I -B research/r439-block1-schedule/search.py
```

Expected: `PASS_R439_BLOCK1_SEARCH gates=35->30 minima=14+16 reverse_dominated=True`.
`--write` explicitly regenerates `CANDIDATE.json`.

`python3 -I -B research/r439-block1-schedule/check_package.py` checks isolated,
optimized execution from a minimal source tree with spaces in its path, five
source/receipt/candidate corruptions, and preservation of an existing output
directory. Its expected marker is `PASS_R439_BLOCK1_PACKAGE`.

For the unchanged C++17/Boost legality and five/nine/eleven-stage checkers:

```sh
python3 -I -B research/r439-block1-schedule/native.py
```

Expected: `PASS_R439_BLOCK1_NATIVE words=2 stages=5,9,11 columns=883,1327,1549 bridge_controls=96`.
Set `BOOST_INCLUDE` to the include directory when Boost is installed outside
the default compiler path. `CXX` selects the compiler. `--output` retains logs
in a fresh directory; `--write-receipt` explicitly regenerates `NATIVE.json`.
Only time and the temporary stream pathname are excluded from native receipt
comparison. All proof-relevant receipt fields are compared.

## Circuit and complete cost

The exact object is `B[128:163]` in
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, at frame **507**.
The ordered physical registers are
`[0,3,11,61,62,63,68,69,72,465]`.
The two fixed positive factors are the first **14** and final **21** gates.
The replacement retains their integer maps and uses **14 + 16** gates.

The saving comes from using two existing destinations as accumulated donors.
In the second factor, first perform the original updates to registers 61 and
63. Then update `69 += 68`, allowing registers 0, 11 and 62 to read that sum
directly. Next update `3 += 68`, allowing registers 72 and 465 to read that
sum directly. These five shared pair reads each save one addition. The full
literal schedule and its physical binding are in `CANDIDATE.json`.

There is no new preparation, scratch, source read, COPY, frame or child cost.
Every addition in the substitute and in its regenerated reverse is counted.
The native multistage checks include their bridge additions and arbitrary
helper restoration. The unchanged global supplier is complex-bound; in any
case, an unchanged bit moment supplies no larger kappa. A new globally hosted
invoice is not inferred from these local counts.

## Exactness and scope of the optimum

For each fixed factor, consider only positive-addition schedules in which each
physical destination is finished in one contiguous batch and never changed
again. A batch may be empty. There are no additional wires, permutations,
negative additions, or changes to the boundary between factors. Donors can be
any other current registers. This is a restriction on schedules, not a lower
bound on unrestricted XOR circuits.

At state `S`, a finished row is its prescribed target row and an unfinished row
is its input unit vector. Finalizing destination `r` means adding other current
rows to make exactly `target[r] - e_r`. All target entries are zero or one and
each current row has a diagonal one, so no donor can appear twice. Thus every
possible batch is represented by a donor subset. The cost is its cardinality.
Donors are unchanged within the batch, making their order immaterial.

The state graph is acyclic: an edge adds one destination to `S`. The Bellman
recurrence from the empty state therefore gives exact minimum path costs.
Both graphs have all **1,024** states reachable. Their complete edge counts are
**4,480** and **3,984**; each implementation examines **5,120** state/destination
pairs per factor. Minima **14 and 16** are attained by the recorded schedules.
The stopping rule is exhaustion of these two graphs. No random circuit trials
or time cutoffs are used, and no unrestricted minimum is claimed.

The nomination encodes positive rows as base-11 integers and enumerates every
donor subset, with no carries possible. The verifier instead solves donor
equations by exact elimination over F2, then checks each candidate sum over Z.
Each reachable current matrix is invertible because it comes from elementary
row additions, so its F2 donor representation is unique. Consequently the
verifier cannot miss a positive integer batch. It compares all **2,048** stored
distances, not just the two final minima. These are different implementations
written by the same AI agent, not independent human review.

For circuit correctness, columnwise integer replay proves equality of both
factor matrices, hence of the complete ordered block map over every commutative
ring. The signed inverses also agree. The whole supplier's claimed restored
endpoint is checked over F2, not asserted over Z.

The reversed positive block matrix falls in 10 entries, its entry sum
**174 -> 116**. Inside an addition-only block, positive row bounds never
decrease, so the endpoint dominates every internal prefix. Substitution into
the unchanged positive exterior therefore cannot increase the complete forward
or reverse bound: the forward block matrix is equal, and its positive reverse
is dominated. Actual native prefix replay independently checks this argument.
The payload formula `64 * forward^3 * reverse^2` remains below `2^104`.

## Provenance, overlap and limitations

Base: **`f567884aeb8851b6e794af1184119a3bfbe1e631`**.
Selected conditional kappa there is **0.001661634653669567**, from PR799/589.
The reviewed PR589 supplier head is
**`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`**. `SOURCES.json` pins execution,
native and contextual inputs by SHA256 and base Git blob, plus the original
PR589 paths/blobs for the word, checker and generator. Those original paths
used `e8-bit-p111/`; integration renamed the retained package to
`e8-bit-p111-tuned/`. All four checked original objects match byte for byte.

The OS assignment seed was **8**. `CLAIM.md` records the three alternatives,
seed-based selection among punctured blocks, scope, timebox and coordination
checks. No pinned sprint issue existed, so the claim is local.

PR589's closed transport/Steinberg search does not cover this factor-scheduling
class. PR661's fixed-word frame result and PR827's fixed-prefix cleanup-frame
obstruction do not exclude a scalar rewrite. Related scheduling work is
credited: Yuzhou Wang's [PR789](https://github.com/CrocSwap/integer-mult-bounds/pull/789),
commdata2338's [PR790](https://github.com/CrocSwap/integer-mult-bounds/pull/790),
Jerry Lin's [PR810](https://github.com/CrocSwap/integer-mult-bounds/pull/810),
and Gautam Gupta's [PR844](https://github.com/CrocSwap/integer-mult-bounds/pull/844).
The latter changes R439 block 4; zeusinsight's
[PR857](https://github.com/CrocSwap/integer-mult-bounds/pull/857) changes block 8.
This contribution covers the different ten-wire, dirty-helper block 1.
Sagar Thakrar's PR728 and Ryan Haines' PR792 change phase-A mini-nodes;
PR843 changes the frame-509 source sum. No pending implementation or saving
is imported, and composition with those PRs is not certified.

The final refresh through PR874 found concurrent **navinor's
[PR873](https://github.com/CrocSwap/integer-mult-bounds/pull/873)** at
`117c48527dd4f066dad103121761154cf1bb39cd`. It independently uses a whole-block
single-write class on the neighboring **eleven-wire frame-508 block**
`B[205:242]`. That related contribution is credited; no scheduling-mechanism
priority is claimed. This package changes **ten-wire frame 507** `B[128:163]`,
certifies two fixed factors and supplies fresh native 5/9/11-stage evidence.
It imports none of PR873's code. Main still had the pinned base at refresh.

The complete local word and native multistage checks are covered. Fresh
globally hosted owner programs, invoices, moment/outer assembly, cold supplier
regeneration, repository-wide `make verify`, Lean and remote CI are not claimed.
This isolated addition does not change a selected input or generator, so the
affected checks are the package checks and selected-record integrity; the broad
regenerating suite is not needed to test an unchanged selected construction.
Inherited all-size/compiler, common-label/mutable-basis realization, whole-call
hosting, signed decoder, precision/tape/exact-recovery and analytic assumptions
remain. Finite certificates are not a formal multiplication theorem.

## Credit and license

Prepared for **Krishnendu Purohit (@Deftsalt-debug)** with substantial **OpenAI
Codex assistance** in task selection, circuit derivation, implementation,
verification and writing. No independent human review or delegated-agent review
is claimed. New files are Apache-2.0 under the repository license.

Construction credit remains with **eumemic** (PR543/555 and scalar interface),
**DreamingOfClouds** (PR545/589 puncturing/transports and PR503/510 pricing),
**Dylan Crow** (format and exporter), **Zhihao Chen**, **DaysSky** and the full
lineage in [`NOTICE.md`](../e8-bit-p111-tuned/NOTICE.md), including Jacob
Sussman's E8 unit. The verifier structure adapts **mtpsl's PR691**
[`verify.py`](../r420-quad13/verify.py); the native harness adapts **Ali Romman's
PR688** [`native.py`](../r420-two-block-composition/native.py). Original notices
and assistance disclosures are retained. The new nomination and independently
implemented optimality check import no pending PR implementation.
