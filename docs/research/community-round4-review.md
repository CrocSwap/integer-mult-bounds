# Community review: PRs #81–#83

This is a conditional maintainer review with OpenAI Codex assistance, dated
2026-10-08. It builds on the [#71/#74 construction review](community-round3-review.md).
It is not independent human peer review or a full proof of multiplication.
Main's selected witness is unchanged by this review alone.

| PR | Contributor | Pinned head | Subject |
|---|---|---|---|
| [81](https://github.com/CrocSwap/integer-mult-bounds/pull/81) | Dominik Scholz | `acae4964aef41c69f3c57e72a45e76afc4d4934d` | Balanced columns with envelope ordering and carried-signal exchanges |
| [82](https://github.com/CrocSwap/integer-mult-bounds/pull/82) | Rohan Arun | `3410b940aa26e5876202152dfa7c4f66451ee22c` | Envelope-ordered balanced graphs and coordinate-aware discovery prices |
| [83](https://github.com/CrocSwap/integer-mult-bounds/pull/83) | Joseph Demarest | `183077b7b3ae12e96eb3a87c1dc08023e6494dca` | Exact selection within 64 depth-coarse profiles and an adaptive-recursion barrier |

## Construction changes

#81 combines eumemic's balanced coarse columns, huxint's anchored graph adapter,
Thomas DiFiore's envelope-node order, Chafik Boukhalfa's split/next-use compiler,
and Alejandro Zarzuelo Urdiales's carry exchanges, with the schedules, costs,
live controls and earlier compositions credited to Rohan Arun and Dominik
Scholz. The node-ID support cache is explicitly cleared after renumbering.
The independent dense check evaluates the scalar outputs without that cache.
Exchanges preserve cardinality, unique uses, and local basis independence;
their prices are discovery heuristics, not proof substitutes.

#82 composes these methods before compiling both axes, instead of selecting
already compiled parent axes. At h=25, its oracle prices frame transitions in
the final permuted coordinates. An exact source comparison limits the modified
engine to the oracle frame writer and an attribution comment. That affects
choice among legal operations, while containment and independence remain
mandatory. The emitted word, rather than its estimated price, determines the
paid recurrence. Coordinate relabeling must consistently change source triples,
scatter targets, output indices and frame masks. Full permutations preserve the
I+J basis, I-J/9 metric, and the complete triple-indexed data family.

All earlier credits, including Rohan Garg's split operation, Avi Eisenberg's
graph and eumemic's reversible compiler, remain applicable. These are
compositions of community work, without a new priority claim.

## The scope and proof of #83's barrier

The 64 profiles are pairs of three-letter row/column choices, one for each
axis. Those choices control the first three internal levels of the finite
exclusion construction; they do not already describe adaptive choices at
depths of the growing-width recurrence.

For each complete profile j, the characteristic is
`M_j(alpha) = sum_t (n_j,t/W_j)*(t/575)^alpha`. The coefficients are relative
child volumes, not probabilities. Independently reconstructed profiles satisfy
`M_j(0)>1`, `M_j(1)<1`, and have positive children below 575. The exact comparison
isolates a unique best root, for the `rcr`/`rrr` pair.

Let alpha be that best root and D=13225/2. For every child rank t<=529,
`t*floor(e/575)+D >= (t/575)*(e+D)`. Writing e=575*k+r cancels k; the smallest
residual occurs at r=574. Checking all ranks 1 through 529 gives a positive
minimum slack of 23/25. At alpha every profile has characteristic at least one,
so summing the shifted potential with each child's actual V/W_j preserves its
lower bound. The assumed leaf charge `c0*V*e` starts the induction. This argument
is valid for every realized tree, including adaptive or randomized selection.

The matching upper exponent for the selected profile uses its unshifted
potential and the exact identity relating total leaf and internal-node volumes.
It also requires the stated upper bound on nonrecursive work. The proof is
sound within these hypotheses; it does not turn an upper recurrence into an
unconditional runtime lower bound.

The result excludes an exponent improvement from switching among these fixed
complete profiles. It does not exclude shared child computations, stronger
restricted child contracts, finer per-cell choices, changed compiler policies,
or new network families. In particular it does not cap #81 or #82. Its numerical
headroom of less than `1.565e-16` applies only to this family's unchanged
balanced assembly, not to the repository's current research frontier.

## Validation status

The [validation receipt](community-round4-validation.json) records the pinned
heads, fresh local results, CI evidence and limits of this review.

| PR | Conditional kappa | Local outcome |
|---|---:|---|
| #81 | `51915547765237/10^18` | Both words freshly regenerated, exact raw and compressed Git blobs reproduced, full validator and independent dense scalar audit pass |
| #82 | `5203279888519/10^17` | Both words freshly regenerated; published relabeled raw hashes, complete replay, exact CRT profiles, arithmetic and all 7 focused tests pass |
| #83 | `5164326938841/10^17` | Both selected words freshly regenerated with exact raw and compressed Git blobs; unmodified validator and all 11 focused tests pass |

Each selected witness passes 47 strict assembly constraints and seven margins,
including independent moment bounds and adjacent-grid rejection. All retain
the upstream all-size and transfer assumptions. #82 is the strongest of these
three: about 1.99% above main's selected witness and 0.389% above reviewed #74.

For #82, the local review did not reproduce the original gzip transport bytes.
The regenerated relabeled contents match the published raw SHA256 hashes
exactly. A scoped helper checked 291 other source/artifact hashes, required-path
manifest coverage, physical replay, profiles and arithmetic; four historical
gzip inputs were unavailable locally. The full unmodified validator was not
claimed to pass locally. Its pinned Python 3.11 CI log was inspected and confirms
original-source closure, deterministic regeneration, replay, profiles and tests.
The dedicated Python 3.13 and 3.14 jobs also succeeded.

For #83, all eight pinned family CI logs were inspected: they confirm
regeneration and replay of all 16 axis variants with zero CRT disagreements.
The local audit independently reconstructed all 64 aggregate profiles and
checked their root comparison, but regenerated only the two selected axes.
All 47 CI checks passed at the recorded head.

The first #83 local rebuild helper incorrectly expected metadata emitted by an
older wrapper. The corrected helper compared every emitted computational field
and required the published raw word hash; both subsequent runs passed. This
was a review-helper mismatch, not a changed certificate.

## Integration findings

The submitted finite witnesses have no unresolved mathematical discrepancy in
the checks above. Before integration, address two validation issues:

1. #81 adds no dedicated CI gate for its new package. Its 36 inherited jobs
   remained queued at the recorded check; passing inherited jobs would not
   establish coverage of the new package. Wire its validator into the maintained
   checks, retaining the exact #71 construction baseline that it pins.
2. #81 and #82 use the older replay boundary. Carry over #64's strict binding
   between literal scatter gates, the complete terminal inventory and the paid
   construction. This review separately checked all four submitted words and
   rejected a cancelling duplicate-scatter mutation for each. #82 permutes
   coordinates, so scatter gates can appear in a different order: compare the
   exact incidence multiset, retaining multiplicities. Their controls and
   targets lie in disjoint banks, so these gates commute. A parity-only check
   would incorrectly permit uncharged cancelling pairs.

#82 was still a draft with 43 of 45 CI checks successful and two joint checks
running at the recorded time. Treat it as the preferred numerical integration
candidate after readiness and those checks are resolved. Preserve #81 as a
separately credited, validated composition. #83 is useful for its exact family
selection, stricter validation and scoped barrier, even though its selected
kappa is below #74, #81 and #82. Its barrier must not be described as a limit on
the broader approach.

No PR review comment, merge or publication has been issued in this pass.
