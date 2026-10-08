# Community review: PRs #50–#62

The selected conditional witness is

\[
\kappa=\frac{25508460085039}{500000000000000000}
=5.1016920170078\times10^{-5}>2^{-15}.
\]

This is **23.71% above PR #49**, the preceding main-branch checkpoint. It remains
below 2^-14. Avi Eisenberg's PR #62 graph, eumemic's PR #57 compiler and Alejandro
Zarzuelo Urdiales's PR #61 refinement supply the selected composition. The
original OpenAI #109 theorem and retained all-size analytic and fixed-tape
interfaces remain assumed. This is a conditional maintainer review with Codex
assistance, not independent human peer review or a formal proof of multiplication.

## Contributions and dispositions

All reviewed heads appear in the accompanying [validation receipt](community-round2-validation.json).
The previous [follow-up audit](community-followup-review.md) and
[PR #39 transfer review](community-final-audit.md) remain dependencies.

| PR | Contributor | Contribution | Integration disposition |
|---|---|---|---|
| [50](https://github.com/CrocSwap/integer-mult-bounds/pull/50) | Rohan Gupta | Parallel summand-order search; κ=4.129418696e-5 | Full pinned replay passed; preserved branch history and attribution; superseded |
| [51](https://github.com/CrocSwap/integer-mult-bounds/pull/51) | RaD / hipotures | Enlarged signed frames, source partitions and paid whole-chain clones | Research and machinery retained; exact arithmetic replayed, full standalone negative-basis construction not independently replayed |
| [52](https://github.com/CrocSwap/integer-mult-bounds/pull/52) | Rohan Arun | Parallel order/matching improvement; κ=4.136014808e-5 | Full pinned replay passed; preserved branch history and attribution; superseded |
| [53](https://github.com/CrocSwap/integer-mult-bounds/pull/53) | Avi Eisenberg | Skip-prefix leave-one-out strips | Full producer/profile replay; foundational graph and standalone witness retained |
| [54](https://github.com/CrocSwap/integer-mult-bounds/pull/54) | Chafik Boukhalfa | Original-envelope specialization of RaD's paid cloning | Full replay; alternative witness retained |
| [55](https://github.com/CrocSwap/integer-mult-bounds/pull/55) | Rohan Gupta | Dual-suffix strip layout | Full replay; standalone and joint-compiler compositions retained |
| [56](https://github.com/CrocSwap/integer-mult-bounds/pull/56) | Rohan Arun | Skip strips with enlarged positive frames, matching and clones | Full replay plus fresh sufficient-prime recertification; alternative retained |
| [57](https://github.com/CrocSwap/integer-mult-bounds/pull/57) | eumemic | Joint equal-frame compilation and paid retired-wire reclamation | Complete word and profile replay; used by selected witness |
| [58](https://github.com/CrocSwap/integer-mult-bounds/pull/58) | Chafik Boukhalfa | Dual-suffix graph combined with joint compiler | Construction retained through stronger #60; original comparison records retained |
| [59](https://github.com/CrocSwap/integer-mult-bounds/pull/59) | Rohan Garg | Split-pair recursion and paid cloning | Full replay, independent arithmetic and controls; alternative retained |
| [60](https://github.com/CrocSwap/integer-mult-bounds/pull/60) | Chafik Boukhalfa | Descending-frame-rank reclamation priority | Full regeneration/replay and independent arithmetic; preceding best composition retained |
| [61](https://github.com/CrocSwap/integer-mult-bounds/pull/61) | Alejandro Zarzuelo Urdiales | Exact parameter refinement, concrete Lean arithmetic, matrix/parity and search tools | Both #60 and final #62 refinements independently checked; selected final parameter witness |
| [62](https://github.com/CrocSwap/integer-mult-bounds/pull/62) | Avi Eisenberg | Interval strips and core-aware pair assembly | Plain and stacked witnesses fully replayed; selected finite construction |

Rohan Gupta, Rohan Arun and Rohan Garg are distinct contributors. Parallel and
superseded work is credited on its merits; headline selection is not a ranking
of contributors. Earlier contributions and assistance disclosures remain in
[CONTRIBUTORS](../../CONTRIBUTORS.md) and [NOTICE](../../NOTICE).

PR #50 and #52 modify the same baseline directory as #49. Their mathematical
changes were reviewed and tested on separate pinned worktrees, then their heads
were integrated with the `ours` merge strategy. Main deliberately retains the
#49 baseline files so existing historical audits remain reproducible. Their
stronger numerical witnesses are superseded by the later construction, rather
than falsely presented as dependencies of its graph. The late #54/#58/#60 main-sync
heads preserve receipts and ancestry without reverting the combined integration.

## Why the new finite constructions fit the interface

The strip and pair-layout changes preserve exact leave-two-out outputs. Every
scalar addition has disjoint supports and a common point; every retained carrier
link must obey causal order, core/cover containment and distinct-use constraints.
The dense support checks, matching recount and complete dirty-input basis replay
establish these finite facts on both axes. The integer-program optimality claims
in #62 are not dependencies of the accepted witness and were not independently
reproduced. No global optimality claim is made.

The joint compiler groups operations with identical rational envelope frames.
It selects independent requested rows, retains usable incoming rows and completes
them to an invertible binary map. Its emitted elementary XORs, including the
three-XOR implementation of each swap, are charged. A retired role can be reused
only after compatible frame containment and paid signal clearing. Clearing a
source-dependent signal does not assume an arbitrary dirty value becomes zero.

The dirty-workspace wrapper cancels those arbitrary initial values and restores
all auxiliary roles. The independent replay checks every input and dirty basis
vector in both orientations. Its frame-path reconstruction uses the actual XOR
word and checks common gate frames and every transition, rather than trusting a
compiler counter. Equal-frame scalar gates commute with their address shear;
the inherited edge compiler then charges rank differences. This is the finite
extension reviewed here. The general residual compiler, all-size recursion,
address/tape implementation and analytic transfer remain written inherited
obligations, not consequences of a successful finite test alone.

PR #59's recursion partitions each coarse piece exactly, with at least one
retained pair for strict contraction. Its additional clones are actual paid
chains with causal schedules and checked original envelopes. PR #56 uses larger
signed frame generators: finite containment checks and the full physical compiler
are replayed, and rank exactness receives the stronger check described below.

## Exact counts and numerical checks

For the selected stacked #62 network:

- Dimensions 23 and 25, with m=575 and N=4,073,300.
- Axis roles R23=27,918 and R25=36,586; total W=137,151,806.
- L=2,226,400; total rank=78,860,441,550; deficit Wm−s=1,846,900.
- Largest child width 529, strictly below 575.
- Refined bit saving 102039046058023/2000000000000000000; complex saving 717/10^7.

The maintainer [independent arithmetic check](community-pair-arithmetic.json)
reconstructs the complete child multiset from replayed profiles, including data,
exterior banks, copied centers, growth and endpoints. Independent rational
logarithm/exponential enclosures establish strict moment contraction. Direct
parameter identities and all seven margins agree. The 47-row balanced interface
and eventual thresholds are recomputed using its previously reviewed,
hash-pinned implementation. This is independent moment accounting, not a claim
of independently deriving every inherited analytic lemma.

The [preceding #60/#61 check](community-round2-arithmetic.json) is retained too.
PR #61's fine-grid failure to certify a next point is not interpreted as an
optimality or infeasibility proof.

The fixed I+J data geometry is unchanged. Fresh native runs check all 4,073,300
pairs and exact rational recovery of the ten primary-prime failures. The
bounded-minor/CRT proofs are the previously reviewed original-envelope proofs.
For #56's enlarged frames, three primes are merely diagnostic. The integration
now requires RaD's exact Boost multiprecision profiler on every full replay:
10 primes give 310 product bits versus a 293-bit minor bound at h=23; 11 give
341 versus 316 at h=25. Both reproduce the supplied profile exactly.

The separate #51 negative-basis witness retains a narrower review status: its
arithmetic was freshly replayed, but its entire standalone source-graph and
negative-basis data argument was not. Using and fully checking its machinery in
#56 does not silently certify that separate witness.

## Lean and integration checks

The integrated #61 Lean 4.31 package builds and its axiom audit checks **169
distinct declarations**, allowing only `propext`, `Classical.choice` and
`Quot.sound`. Eleven concrete frontier checks bind to exported rational rows,
which the maintainer verifies against the replayed network and independent
logarithm bounds. They check finite Padé/rounding/moment and slack arithmetic;
the analytic enclosure lemmas and full multiplication transfer are not formalized.
The eleven supplied Python tools also pass. The historical Mathlib 4.33.1 source
archive in that package is preserved, not newly claimed as a compiled proof.

Integration fixes are limited and explicit:

1. Remove two duplicate audit lines, preserving all 169 unique declarations.
2. Resolve the matrix tool output directory before changing working directory.
3. Run each test module in its own interpreter. Independent research packages
   reuse names such as `skip_graph`, and combined discovery otherwise picks up
   another package's module. All test files remain covered.
4. Repin source manifests to the integrated tree. The shared binary I/O header
   change consists only of standard includes; corresponding derived certificate
   differences are provenance, not numerical changes. PR62 Windows path keys
   are normalized by native regeneration; its original certificate is archived
   to preserve PR61's exact input hash.
5. Add sufficient-prime enlarged-frame verification and separate CI groups for
   each expensive producer family. No old checks are dropped.

Native checks use Apple Clang; the OpenMP producer uses the installed libomp.
The complete clean Linux matrix checks the same tree on Python 3.11, 3.13 and
3.14, plus the three pinned Lean packages. See the [CI layout](../ci-verification.md)
and [validation receipt](community-round2-validation.json) for the executed scope.
Submissions after #62 and revisions beyond the recorded heads are outside this
checkpoint. No comments or announcements are posted automatically.

## Bounded attempt at 2^-14

Applying #60's reclamation ordering to #62's graph preserves the same role counts.
Complete word replay and exact profiles show a small change in the child mix.
The [exact screen](pair-ranked-screen.json) gives a moment lower bound greater
than one already at bit saving 2^-14, so this particular combination cannot
support the requested multiplication target. The approximate bit root improves
only about 0.02%; no new multiplication witness is claimed or selected.

Reproduce with `python3 scripts/experiments/probe_pair_ranked.py`. The recorded
receipt was extracted from the freshly compiled, independently replayed and
profiled words in this review. This scoped negative result does not rule out a
better graph, different compiler or stronger recurrence analysis.

All **36 jobs passed** on the [integrated code commit 0d235fe](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/37824092076): eleven arithmetic groups on three Python versions, plus three pinned Lean packages. The subsequent release-documentation and late #60 provenance commits change no code or mathematical certificate.
