# Independent audit of the cancelled-return interval graph

**Independent finite verification; no new kappa and no source discrepancy found.**
This package corroborates [PR1563](https://github.com/CrocSwap/integer-mult-bounds/pull/1563)
at `e7d1ebfc3093a704b55c14ea4d10d0d0bdfdd0db`: its complete fixed-fixture
interval graph, 35-point cost/cap frontier and every published frontier/cap word
agree with a separately implemented checker. At cap 4096 the full word costs
**2,222 ADD/SCALE instructions**, with maximum prefix row-L1 **3,958**.
The unrestricted minimum in this class remains **2,206** at cap **4,116**.
These are predecessor results independently corroborated, not new constructions.

## Precise scope and added coverage

The object is Sagar Thakrar's PR1537 fixture: 53 fixed, ordered integer readers,
five workspace pairs, arbitrary incoming dirt, unit ADDs and binary-power
double/halve returns. Contiguous intervals restore canonical boundaries; the
final output-only return and its inverse may cancel across a disjoint workspace
unload. ADD and SCALE each cost one. Interior observations and different reader
orders, return recipes or child implementations are excluded.

PR1563's own primary checker already covers every interval. Its separate
Fraction oracle checks three complete words. This audit adds a separate
implementation of **all 1,431 intervals**, including **all 53 fused terminal
edges** evaluated with a second exact Fraction evaluator in both contexts.
Of these terminal edges, **37 occur in none of the 42 published frontier/cap
schedule records**; that count excludes PR1563's other control words.
[PR1575](https://github.com/CrocSwap/integer-mult-bounds/pull/1575) checks
PR1552's pure canonical graph and explicitly leaves the PR1563 changed word
outside its audit. No executable or certificate from PR1575 is used here.

[CERTIFICATE.json](CERTIFICATE.json) records:

- 216 cut states obtained by chronological execution; 5,618 contextual interval
  executions, 123,596 integer basis-column executions and 2,332 Fraction terminal
  columns;
- 2,331,416 contextual instruction steps, including children, source transfers,
  frame returns and literal inverses;
- 1,618 cap decisions at every distinct interval peak and the preceding integer,
  plus seed-selected neighbors of powers 2^8 through 2^14;
- all 35 frontier points, reverse Bellman potentials, 42 complete schedule
  records containing 37 distinct words, both full dirty endpoints and exact
  source word reports;
- every one of 128 partitions in a separate eight-child/two-pair seed-82 fixture,
  with direct complete-word costs/peaks and 24 cap decisions;
- 14 semantic rejection controls and six external artifact/relocation tests.

The rebuilt graph SHA256 is
`0ac593e72b8273ad71488e687aae7716fff33ff64dfe62b1671bb8ff95c52429`,
identical to the pinned PR1563 receipt.

## Independence and the coverage argument

[engine.py](engine.py) imports only `fractions`. It reconstructs the fixture and
literal instruction alphabet from the documented contract, without importing
or running predecessor code. The retained model is a source pin, not a module
dependency. Instead of using closed-form accumulated-reader matrices to create
cut states, the engine executes eager neutralized children, the source load and
unload, and reverse chronological inverse children, recording each cut.

Each ordinary interval executes in the four recorded states. Each final edge
executes its whole cancelled middle, including unload or load and the literal
inverse, in both applicable states. All endpoints must match the chronological
reference states. The integer engine propagates basis columns and sums their
absolute scalar traces at each changed coordinate. Every halving must be
integral at every prefix. A separate evaluator runs scalar Fraction columns and
checks every terminal prefix without using the integer division logic.

The interval endpoints establish path-independent boundaries by induction over
the chosen cuts. Every contiguous partition is a path from 0 to 53, and its
complete peak is the maximum of the contextual edge peaks; outer source
transfers are covered by adjoining endpoints. This is the source's scoped
decomposition argument, corroborated by all interval endpoints and the small
direct exhaustion. It represents **2^52 partitions through a graph**; this
package does not enumerate 2^52 complete words or provide a proof-assistant
formalization.

The checker solves from endpoint 53 toward 0, independently of the source's
forward optimizer, and checks source prefix potentials and attaining paths.
Each complete word is then emitted and executed in both directions. With 972
fixed-child ADDs per direction and ten source coordinates, its full bill is
`ADD = 1964 + 2*boundary_ADD`, `SCALE = 2*boundary_SCALE`.
No source access, scratch restoration or final return is left uncharged.

Controls reject corruption of an unused terminal edge, a false potential,
undercharging, missing unload, reversing without inverting, nonintertwining
readers, nonintegral prefixes, illegal coefficients, duplicate cuts and JSON,
an observed midpoint, an aliased unload, and endpoint-only precision checks.
The stale-output example independently reproduces peak **587 instead of 694**
on interval [20,36). It is a concrete failed calculation, not a failed search.

## Reproduce and provenance

From the repository root, CPython 3.12 with no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/independent-cancelled-return-graph
```

Expected: `PASS_INDEPENDENT_CANCELLED_RETURN_GRAPH`, six passing tests, then
`PASS_REGISTERED_RESEARCH_PACKAGE research/independent-cancelled-return-graph outcome=completed`.
The standalone checker also runs without Git in a relocated package:
`python3 -I -O -B research/independent-cancelled-return-graph/verify.py`.
`--emit` prints a deterministically rebuilt certificate to stdout; default replay
does not write artifacts.

Research base: `0a201997097b8a89b638f3a2afcb35db4184c8b2`.
Original PR1537 head: `407f00df6ca0bf86b455b5640f18ec2f62ee77b9`.
[PREDECESSOR.json](PREDECESSOR.json) binds four unchanged source files by exact
commit, Git blob and SHA256; its own digest is fixed in the checker.
[SOURCES.json](SOURCES.json) binds the selected-record/catalogue provenance at
the base. The accepted record is conditional PR1094,
`kappa = 836330098538459/500000000000000000`; this audit does not alter it.

[TASK.json](TASK.json) records OS assignment seed 82, all three candidates,
scope change from the catalogue's selected-moment card, stopping rule and
seed-selected controls. The source fixture seed remains 53. The scoped
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1542#discussioncomment-18914923)
and [CLAIM.md](CLAIM.md) record coordination and overlap coverage.

This audits the flat fixed fixture and its declared graph class. It does not
check PR1563's nested recurrence, prove global nested precision caps, identify
an indivisible selected supplier child, or establish physical routing/hosting,
rounded arithmetic, tape costs, input-size contraction or analytic transfer.
Full selected cold replay, Lean and independent human review are unclaimed.
Local verification and hosted CI are reported separately in
[VALIDATION.md](VALIDATION.md).

## Open next questions

Can globally capped nested calls admit a similarly path-independent cut state?
That matters because the flat caps do not automatically compose. A first step
is to recompute every root-prefix operator in PR1563's fixed three-by-seventeen
fixture and identify the caller-output state needed at a cut. Global nested
optimality and such a state description remain blockers. Check live claims
before extending this work; no nested optimization result is claimed here.

## Credit

Credit **Hanson Sun (@bbMisk), PR1563**, for cancellation, the complete graph,
frontier and written reduction; **Sagar Thakrar, PR1537**, for the fixed readers,
binary returns and interface; **Hanson Sun, PR1552/1575**, for the canonical
frontier and prior independent audit; **Ross Richardson, PR1287/889**, and
the PR1227/1203 lineage for output-frame and reader mechanisms. The retained
READMEs preserve their full notices. Selected context retains Rohan Arun,
Jeremy Kothe, Hao Yan and the PR589/555 supplier lineage.

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** in analysis, implementation, verification and writing. One parent
agent; no subagents or independent human review. Implementation independence
is the specific separation above, not a claim of independent human authorship.
New work and retained sources are Apache-2.0.
