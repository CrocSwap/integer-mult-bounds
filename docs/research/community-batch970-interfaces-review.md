# Forty-PR batch: recursive interfaces, formal proofs and historical replays

This checkpoint records fourteen scoped contribution reviews. Together with the
[first nine](community-batch970-review.md) and [next sixteen](community-batch970-circuits-review.md),
39 submissions have accepted scoped content. Publication and execution completion
are tracked separately in the [ledger](pr-ledger.md). **The selected conditional
κ remains 0.001661960547713947.** None of these abstract interfaces is silently
substituted into a selected supplier.

| PR | Contributor | Accepted scope |
|---|---|---|
| [#862](https://github.com/CrocSwap/integer-mult-bounds/pull/862) | [Chafik Boukhalfa](https://github.com/chafreaky) | Cubic precision for an in-place cyclic inverse with owned clean low bits, plus a fixed-grid composition interface. Charges factor preparation and undo; 120 exact kernel and 20 composed-word checks. Does not admit arbitrary dirty low bits. |
| [#877](https://github.com/CrocSwap/integer-mult-bounds/pull/877) | [Gareth Davidson](https://github.com/bitplane) | Balanced dirty commutator prefix bound and nonlinear perturbation analysis reduce the inherited sufficient precision overhead to quartic. Full child inverses remain paid; no claim that rounded children are linear. |
| [#905](https://github.com/CrocSwap/integer-mult-bounds/pull/905) | [Chafik Boukhalfa](https://github.com/chafreaky) | Free noncommutative prefix lemma has no repeated factor occurrence. A common cyclic operator then gives cubic precision with arbitrary dirty low bits. Quadratic leaf count and logarithmic dirty-array count remain. |
| [#929](https://github.com/CrocSwap/integer-mult-bounds/pull/929) | [Chafik Boukhalfa](https://github.com/chafreaky) | Two stable polynomial groups execute in four completed calls with one arbitrary dirty connector. O(rL) data arithmetic replaces the quadratic data term, with paid companion powering, exact closure solves, O(r^3(A+log L+log r)) clean scalar workspace and phase access. |
| [#951](https://github.com/CrocSwap/integer-mult-bounds/pull/951) | [Chafik Boukhalfa](https://github.com/chafreaky) | Separated-pole Bezout/Laurent decomposition uses two additive stable filters and no borrowed length-L connector. Source is restored on the full incoming grid; clean scalar workspace and preparation remain paid and may exceed a data array for small L. |
| [#934](https://github.com/CrocSwap/integer-mult-bounds/pull/934) | [Ross Richardson](https://github.com/RossRichardson) | All 512 binary 3x3 product patterns attain two complete queries per active operator in the stated one-connector alphabet. Six-cycle example: 18 to 12 queries, 228 to 198 lowered leaves, four dirty arrays. |
| [#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) | [Ross Richardson](https://github.com/RossRichardson) | Universal four-source path; exhaustive 945 five-source pairings exclude complete coverage at ten toggles. All-31-output example has exact restricted optimum 74 queries, with a 182-leaf construction versus 278 for the comparator. |
| [#944](https://github.com/CrocSwap/integer-mult-bounds/pull/944) | [Ross Richardson](https://github.com/RossRichardson) | All 19683 signed 3x3 patterns classified: 288 in one orbit need 14 rather than 12 queries. Complete restored word achieves 308 leaves versus 388/676 star comparators; exact linear characteristic-zero scope. |
| [#953](https://github.com/CrocSwap/integer-mult-bounds/pull/953) | [Ross Richardson](https://github.com/RossRichardson) | Uniform native BIT dyadic query batches have exact restricted optimum 2|J|+number_of_runs, including off-support excursions. Example drops 15 children/90 affine events to 12/72 with ten XOR scans unchanged; no DATA-to-ADDRESS recursive compiler supplied. |
| [#896](https://github.com/CrocSwap/integer-mult-bounds/pull/896) | [Gareth Davidson](https://github.com/bitplane) | Fresh Lean check of nonlinear dirty-commutator restoration, source-independent target increment and literal inverse, including source-trace correspondence and a nonlinear dirt-dependence counterexample. Numerical accuracy and selected leaf admission remain separate. |
| [#887](https://github.com/CrocSwap/integer-mult-bounds/pull/887) | [Gareth Davidson](https://github.com/bitplane) | Fresh Lean resource model for reserved-scratch ordered echo trees: capacity n<=2^s and exact 50-factor/six-array minimum 2304. Eight general statements, 5474 constructor proofs and nine controls. Wall timeout alone raised for native replay. |
| [#856](https://github.com/CrocSwap/integer-mult-bounds/pull/856) | [Chinmay Arvind](https://github.com/chinmayarvind23) | Exact R420 Boolean scatter lifecycle bound to 9 COPY/568 ADD/9 ERASE operations: original coordinates correct, incoming temp irrelevant, temp ends zero. Fresh four-module macOS kernel replay and 28 probes; authored Linux-pinned checker not claimed passed. |
| [#828](https://github.com/CrocSwap/integer-mult-bounds/pull/828) | [mihir-s-05](https://github.com/mihir-s-05) | Twelve later PR279 target-prefix files retained in a reconstructible companion; all nine native stages freshly replayed at historical kappa 0.000724098741932703. Credits Rohan Arun, eumemic and gen4 lineage. Does not close parent PR279. |
| [#930](https://github.com/CrocSwap/integer-mult-bounds/pull/930) | [Ross Richardson](https://github.com/RossRichardson) | Nineteen post-review PR210 changes reconstructed, eight native stages freshly replayed, and 20108 stream traces independently checked at historical kappa 0.000710069340338651. eumemic construction; Ross Richardson reconciliation. The 128 unresolved ancestral paths remain. |

## Arithmetic interfaces: distinct contracts

#862's recoverable coarse grid requires owned clean low bits. #877 and #905
instead preserve arbitrary dirty low bits by completed target-independent
increments and exact inverse words. The stronger #905 prefix argument is about
ordered, disjoint factor occurrences in a free algebra; a small norm bound then
uses the additional common-cyclic-operator hypothesis. It does not apply the
complementary-factor norm bound to unrelated noncommuting shifts. Rounded errors
are treated as actual state-dependent errors in a variation-of-constants bound.
The preparation/root-separation and leaf interfaces remain inherited hypotheses.

#929 groups the stable inside/outside factors, proves summability of companion
powers, solves the periodic closure, and undoes causal source lifts in reverse
order. We checked the separate treatment of short cycles L<k, repeated roots,
rounded phase windows, rounded initial gauges and exact rational closure solves.
Its two calls to the second group can see different source magnitudes and
precision choices; each error is paid separately. Exact cancellation of the
first group restores the connector without assuming rounded linearity.

#951 replaces that dirty commutator by an additive Laurent split. The two pole
groups are coprime even with repeated poles within a group. Numerator mass is
bounded by Laurent projection, avoiding an unproved small-residue assumption.
Output near the cyclic seam uses the initial negative-index homogeneous history;
finite tests and the written bound include that history and L<k. Both calls
restore the source. The absence of a full connector is not free memory: clean
scalar closure/preparation storage is explicitly paid, and may be larger than
an array for short cycles. Neither construction implements arbitrary-stride
tape routing, irrational-phase supply or the complete multiplication interface.

## Query constructions and exclusions

#934/#943 are exact binary-linear contracts; #944 is an exact signed-linear
contract. They use arbitrary initial dirt, restore connectors and private child
scratch, and retain all source/output rows while a batch is active. The finite
optimality results follow from reductions to closed source-prefix paths, not
merely unsuccessful heuristic searches. #943 permits extra source toggles or
extra readouts to repair the missing mask; the weighted examples are priced
constructions, not a universal weighted optimum. #944 keeps chronological signs
and rejects extending the cancellation identity to nonlinear readouts.

#953 proves an integer closed-walk condition using uniformity over arbitrarily
large odd prime-power moduli. Its component-count lower bound allows visits
outside the required support. Each native query still pays its full ordinary
interchange child and six affine events. Counts alone do not establish a total
runtime gain when coefficient work changes, and a DATA shear is not an ADDRESS
interchange. No self-recurrence or stronger selected moment is inferred.

For #943, mutable historical-context paths were redirected to byte-identical
archived submission-base files. The original SOURCES.json is retained; all seven
context digests, the mathematical certificate and expected results are unchanged.
Its full verifier and relocation/regeneration/corruption suite passed afterward.

## Fresh Lean execution and platform boundary

#896 compiles the general nonlinear model and its source-correspondence proofs
from scratch. Its leaf premise requires deterministic source-restoring increments;
that premise is not a proof of any numerical leaf implementation.

#887's original 180-second subprocess limit expired while compiling the large
generated case file on this machine. A separate maintainer adapter changes only
that wall timeout to 1200 seconds. It retains the version/commit pin, warnings as
errors, heartbeat and recursion limits, exact expected receipt, all generated
proofs and all nine controls. The complete retry passed. This is a resource-model
formalization; a different connector-reuse model is outside its obstruction.

#856 deliberately pins the official Linux compiler and 317 Init source/object
pairs. Its original checker correctly rejected our macOS compiler. Docker Desktop
failed to start, so we did not claim a local Linux pass. A separate macOS replay
used Lean 4.21.0 commit 6741444a63ee, checked every pinned Init source, recorded all
Mac object hashes before and after, and compiled all four modules from fresh
sources. All 28 axiom probes passed. Replacing the lifecycle proof by `sorry`,
while refreshing its source hash, was rejected through the actual compiled
`sorryAx` report. The Linux virtual-memory cap was omitted in this explicitly
separate native replay; CPU and wall limits were retained. Source-binding tests
passed normally and under optimized Python. The original package remains intact.
The theorem is Boolean scatter semantics, not a physical ERASE or tape proof.

## Historical construction coverage

#828 reconstructs 115 later-head inputs and checks the unchanged 116th workflow.
We inspected the actual target-prefix transformation: 220 disjoint squares,
660 setup plus 660 restore additions, 1100 deleted prefix additions and the
unchanged-rank delta {-220 rank-1, -220 rank-20, +220 rank-21}. The fresh replay
checks actual prefix dependencies, the no-active-target-read condition, both
orientations, geometry, banks, complete costs and assembly. It establishes a
historical finite witness and preserves the original package and receipts.
The submitted edits to the central ledger are archived; current records are
rebuilt with a companion link instead of restoring an obsolete whole-ledger copy.

#930 reconstructs the exact 19-file post-review change and runs all eight stages.
Its independent comparison reduces only payload ADD coefficients modulo two;
address frame IDs and COPY ranks stay integral. Stream traces prohibit movement
fusion across retained uses or COPY/ERASE boundaries. The reduction removes
1,783,196 even payload additions and fuses three rank-8/rank-12 pairs into rank-20
children without changing rank mass. It does not clear the separate 128-path
ancestral incorporation question. Both parent PRs remain open and distinguished
from these completed companion reviews.

Fresh outputs, including full historical native replays and the separate platform
replay, are archived under the batch audit and pinned in its integration receipt.
The logs retain initial failures as well as successful retries. Submitted validation
records remain attributed historical evidence; they are not relabeled as our runs.
New Linux workflows are prospective checks, not a claim that hosted jobs have passed.

## Remaining item and attribution

#946 remains deferred: its broad newline normalization changes bytes covered by
immutable historical source pins, including evidence used in this batch. No blanket
repinning or source approval is performed. It stays open with that specific blocker.
#871 was closed by its author before the freeze and was replaced by #953; it is not
counted as a completed review in this batch.

The notes and original notices retain Chafik Boukhalfa, Gareth Davidson, Ross
Richardson, Chinmay Arvind and mihir-s-05 as the respective authors. Construction
lineage includes Alexander Schwartzman's echo optimizer; 0xkilgore's restoration
and count audit; the PR621/628/862 cyclic-kernel work; the PR521/840 native query
lowerings; Rohan Arun and eumemic's historical transforms; DreamingOfClouds' gen4
word; and the original compiler, bank, geometry and analytic contributors. These
reviews do not claim independent human peer review or formal verification of the
full integer-multiplication theorem.
