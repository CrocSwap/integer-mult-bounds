# Two-sided R420 dirt compensation with shared donors: 8,412 fewer XORs

**Finite circuit construction; no new kappa.** This package replaces only the
frame-zero D compensation in eumemic's historical PR543 R420 bit supplier.
Combining 202 disjoint helper transvections with 68 target transvections
using 47 shared donors reduces D from **19,922 to 11,510 binary ADDs**, and
the complete native word from **26,916 to 18,504** (8,412 fewer, about 31.3%). Preparation
and restoration of both bases are included. Every arbitrary helper and target
input is accounted for.

The helper-only pass costs 12,988 ADDs; factoring target rows **after** that
pass saves another 1,478. This is a concrete combined recipe extending the
credited one-sided mechanisms, not a priority claim for basis factoring.
Our 202 helper pairs differ from PR694's 201-pair matching, despite equal
helper-only cost. For the frozen donor set, each receiver is assigned its best positive-gain donor.
No optimality of the donor set or whole circuit is claimed.

## Reproduce

From the repository root, with Python 3.9+ and the standard library:

```sh
python3 -B research/r420-two-sided-compensation/verify.py
```

Expected final line:

```text
PASS_R420_TWO_SIDED D=19922->11510 native_ADDs=26916->18504 saved=8412 columns=660 no_new_kappa
```

The default run uses a temporary directory. Add `--output /path/to/fresh/output`
to keep the reconstructed candidate, independent report, native records and
execution receipts. Source files and frozen certificates are not regenerated
by the default command. `construct.py` reproduces the seed-3 nomination;
`--write-certificate` explicitly refreshes only this package's certificate.
An available C++ compiler and Boost headers enable the optional unchanged
native C++ checks automatically; otherwise their non-execution is reported.

## Evidence and cost

`CERTIFICATE.json` is compared against a fresh exact recomputation. The main
verifier uses the pinned original E8 label/frame checker, 660 arbitrary-input
columns, the original suffix interface and a semantic D endpoint check.
`audit_independent.py` imports neither producer nor primary verifier; it uses
sets to reconstruct the matrix substitution and independently replays D and
the full word. Corruptions include missing helper restoration, missing target
preparation, missing target restoration, incorrect feed, changed retained
totals and illegal frames. The independent checker rejects a receiver reused
as a donor. A missing serialized D ADD passes legality but fails the physical
column checks. An F2-neutral pair is required to pay both ADDs.

`native.py` invokes the unchanged record exporter and checks the actual
serialized records. The entire 2,958-record MOVE/COPY/ERASE subsequence and
the frame/state files are identical. Helpers remain 420, copies remain nine,
and the paid histogram is `{1:1320,2:1440,4:60,5:120,8:9}`, with rank mass
5,112. Total native records fall from 29,874 to 21,462.

| Exact local quantity | Original | Two-sided |
|---|---:|---:|
| Forward positive-prefix bound | 144,651 | 203,415 |
| Reverse positive-prefix bound | 2,270,064 | 4,284,358 |
| Local payload bit length | 100 | 103 |

The recalculated payload is `64 * 203415^3 * 4284358^2 =
9887816668588668030197998944000 < 2^104`. Thus the local cap passes despite
larger integer envelopes. This does not justify reusing a global hosted invoice.

Python replay of the exported 5/9/11-stage schedules covers 900/1,380/1,620
physical columns and the respective 6/18/24 bridge-omission controls for both
words. Its schedule and prefix formula are ports of the pinned upstream
`columns_k.cpp`; they are **not** an independent proof of that composition
theorem. Fresh unchanged C++ legality and 5/9/11-stage checks also passed for both
words using Apple Clang 21.0.0 and authenticated Boost 1.85.0 headers. Their
receipts and dependency checksum are retained in `VALIDATION.json` and
`NATIVE-CPP.json`. The default standard-library run can report C++ unavailable
when Boost is not configured; use `BOOST_INCLUDE=/path/to/boost_1_85_0` to
repeat those checks. No remote CI, full `make verify`, selected frontier cold
replay, Lean theorem, or hosted-parent replay is claimed.

## Interface and remaining work

The original syntactic H2 and literal K extractor reject the replacement,
as expected. They are left unchanged. [PROOF.md](PROOF.md) states the precise
semantic replacement: D runs first at frame zero and realizes exactly
`(x,s,y) -> (x,s,y+Ks)`, restoring all helpers. Every non-D field is fixed.
The proof uses `M=T K H`, prepares both involutive bases, feeds M, then
restores both bases; the independent checker reconstructs these products.

Integration still requires review of that semantic interface, full
hosted-parent construction and whole-owner routing, revised global invoices,
and changed-word outer assembly. All inherited all-size compiler,
common-label/mutable-basis, pooled-cell hosting, residual, precision/tape and
analytic assumptions remain. Fewer finite XORs do not establish a practical
runtime gain or an improved asymptotic exponent. This package makes no change
to the selected frontier; its baseline is the historical PR543 word, not the
current selected bit supplier.

## Search, source pins and overlap

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 source: `2065fe4f72a914d907f1046603f5a36f17018535`.
Historical selected PR626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
`SOURCES.json` binds the consumed sources; the compressed input is pinned by
canonical JSON payload, allowing equivalent gzip containers. The historical
selected-result hash is provenance only, not a dependency of this finite check.

OS assignment seed **3**, bit-supplier track. The bounded search scores all
175,980 oriented helper pairs, performs one seed-3 greedy disjoint selection,
then scores all 14,280 oriented target pairs on the transformed matrix and
performs one greedy selection. After concurrent PR733 appeared, one extension
allowed shared target donors. The initial 56 donors from the matching undergo
at most 30 strictly improving single-donor add/remove iterations. There are
15 successful iterations followed by a no-improvement stop (1,920 candidate
donor sets evaluated), leaving 47 donors and 68 receivers. For each donor set,
all eligible receiver/donor pairs are scored exactly, paying two basis gates
per receiver. A preliminary 16-donor greedy trial was worse and discarded;
CLAIM.json preserves its result. The search does not cover all donor sets,
matchings, or orderings. No further search followed the stated stop.

The complete open-PR and issue inventory was initially checked through PR730;
a refresh reached PR748 and triggered the recorded single scope extension. The only
open non-PR issue was #650 (Discussions), so the sprint claim is local in
`CLAIM.json`. Relevant concurrent work: #686 and #694 factor helper columns;
#713 and #716 factor target rows; #708 factors separate decoder totals;
#710 changes cleanup. None of their code or frozen circuits is imported.
Concurrent #733 combines helper and disjoint target bases, saving 8,368 ADDs;
#742 permits shared target donors with helpers held fixed. Both are credited.
This package combines the two mechanisms, saving 83 beyond our own disjoint
construction and 44 more than #733 on the same PR543 baseline. The helper
bases differ, so 44 is a total-count comparison, not a patch to #733.
No priority is claimed for two-sided factoring or shared donors. The added
evidence is the explicit combined donor circuit and its exact accounting.
A bounded pre-submission refresh on 2026-10-13 inspected the 200 most recent
open PRs through #946 and complete indexed R420-title, donor and two-sided
searches. No identical recipe surfaced; this is not an exhaustive novelty
guarantee. [PR817](https://github.com/CrocSwap/integer-mult-bounds/pull/817)
(`3147cac35c659152d36db1e0e60b9ce4b152c008`) certifies a different fixed helper
basis with disjoint target matching at D=11,546, versus 11,510 here. Its whole
word count includes separate PR681 changes and is not directly comparable.
[PR794](https://github.com/CrocSwap/integer-mult-bounds/pull/794) supplies a
192-bit hosted invoice for a different target construction; this package does
not supply that invoice. Later R439 constructions concern a different word.
`HANDOFF.md` summarizes review and integration obligations.

## Attribution and license

Apache-2.0, as in the repository. Contributed by
**[franciscoyne001-svg](https://github.com/franciscoyne001-svg)** with substantial
**OpenAI Codex assistance** in construction, proof, checking and packaging,
including separately instructed automated verification workers. No independent
human review is claimed.

Credit to eumemic (PR543/493), Mikhail R. Gadelha (#686), Greer Guthrie (#694),
Scott Woolsey Biggart (#713/#733), Sagar Thakrar (#716/#817), ellipsi2 (#742),
and their predecessors.
The original format/exporter is Dylan Crow's; retain Zhihao Chen's scalar
interface, DreamingOfClouds' totals/pricing and the realization/hosting work
of Chafik Boukhalfa, DaysSky and the full lineage in
[the original notice](../e8-bit-r420/NOTICE.md). Native schedule/prefix code
credits Dylan Crow and DaysSky through the upstream checker. The mathematical
proof gives direct links to the concurrent mechanisms.
