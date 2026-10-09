# Community review: next construction and formalization submissions

Review completed 2026-10-08 with OpenAI Codex assistance. This records a
maintainer review, not independent human peer review. Main remains at
`56b66d58297deca1d7dd130247d720e960f77a37`, with the selected conditional
witness `25508460085039/500000000000000000`. No new submission is promoted
by this review document alone.

## Pinned review scope

| PR | Contributor | Reviewed head | Contribution |
|---|---|---|---|
| [71](https://github.com/CrocSwap/integer-mult-bounds/pull/71) | Chafik Boukhalfa | `f59cb9f54d12a2a02b665afef24a9bb5061ae011` | Anchored split graph, profile-cost reclamation and next-use-aware pending controls |
| [74](https://github.com/CrocSwap/integer-mult-bounds/pull/74) | Thomas DiFiore | `5830ccfca8466aff613767222558e29b57fa8225` | Balanced coarse sums, envelope/core order, and coordinate relabeling on the #71 foundation |
| [80](https://github.com/CrocSwap/integer-mult-bounds/pull/80) | Rohan Arun | `a9ed157ff106fd35557b5896197f66a1272f7f13` | Complete #76/#79 axis selection followed by geometric coordinate flags |
| [64](https://github.com/CrocSwap/integer-mult-bounds/pull/64) | rfu08 | `2d970ab3ca0271cfb2b609dc9aae1b7073b7774d` | Exact profile binding, Lean recurrence/transfer lemmas and concrete tape primitives |

The construction dependencies retain credit for eumemic (#57/#69), Rohan Garg
(#59), Avi Eisenberg (#62), Dominik Scholz (#63/#68/#76), Rohan Arun
(#65/#67/#78), Alejandro Zarzuelo Urdiales (#70), Chafik Boukhalfa
(#60/#71/#79), Thomas DiFiore (#74), and earlier contributors. The present
review does not independently dispose of every dependency's standalone PR.

## Mathematical review

In #71, a pending live role is admitted as a clearing control only if its
current frame F, the current operation frame E, and its assigned next-use
frame G satisfy F contained in E contained in G. The role is used as a
passive XOR control; its signal does not change. The emitted word charges
its frame raises and every clearing XOR. The next-use profile score selects
among legal candidates and is not used as a substitute for the actual
recurrence profile. Four focused pending-control tests, including a mutation
removing future containment, pass in this review.

In #74, regrouping a four-edge coarse sum into shared column sums preserves
the disjoint-support scalar identity. Reordering must preserve every edge
and output, and matching is recomputed. Coordinate permutations commute with
the fixed I+J basis and I-J/9 metric; they preserve the complete triple-indexed
data family while potentially changing ordered child profiles. Those profiles
must therefore be recomputed from the relabeled physical word.

In #80, selecting complete compatible axes is legitimate without adding the
parents' reported percentage improvements. Its own complete profile and width
are the relevant quantities. The width crossing below 2^27 changes the bit
wire count to 27, the product-row coefficient to 843, and the degree gap to
7007/25. Both #74 and #80 recompute these quantities.

Fresh exact arithmetic checks passed for:

* #74: `kappa = 10366199626713/200000000000000000`.
* #80: `kappa = 51778825456819/1000000000000000000`.

Each check includes the complete supplied paid profile, strict characteristic
contraction, adjacent grid rejection, 47 assembly inequalities, and seven
exponent margins. This arithmetic check alone does not establish that a
supplied profile comes from the claimed physical word.

## Formalization scope

The #64 static inventory and source hashes check: 29 source copies, 27 unique
modules, and 298 named declarations. Fresh isolated kernel compilation and
axiom audits pass for all 298 declarations, permitting only `propext`,
`Classical.choice`, and `Quot.sound`. The complete
[kernel audit receipt](community-round3-lean-audit.json) retains module hashes
and the axioms for every declaration. Fresh arithmetic and literal Lean binding
checks pass for its PR64, PR68, and PR73 profiles. The PR73 literal theorem
does not silently become a theorem about the later PR76 or #74 profiles.

The state-cost theorem assumes the actual physical recurrence, uniform base
bound, child widths, and child volumes. It proves their mathematical cost
consequence. Constructing the full fixed-tape multiplier satisfying those
hypotheses remains open in this package. Its counter bound concerns primitive
calls in a fixed direction and excludes dispatcher, payload, and reset costs.

## Reproduction results and disposition

The [validation receipt](community-round3-validation.json) records the exact
heads, local checks, CI evidence, and log hashes.

* **#71 passes the finite construction audit.** Both words were freshly
  regenerated, and their raw and compressed hashes and compiler records match
  the published artifacts. Full dirty-basis replay, literal transitions,
  bounded-minor/CRT profiles, exact assembly, and all 23 focused tests pass.
  Its pinned head also has 36 successful Linux CI jobs.
* **#74 passes the finite construction audit.** Both regenerated words and
  axis receipts match their Git blobs. The independent dense scalar and
  renumbering audit, full dirty-basis replay, literal transitions, CRT profiles,
  complete paid assembly, and independent arithmetic/source audit all pass.
  All 45 Linux checks at the reviewed head pass. Its conditional witness is
  about 1.595701898% above main and 0.100760642% above #80.
* **#80 passes the scoped code/arithmetic review.** Fresh local arithmetic
  and stale-width controls pass. The three focused Linux jobs pass; inspected
  logs at the exact head establish both physical replays, both CRT profiles
  with zero disagreements, and seven tests. This review did not locally
  rebuild its original #76/#79 parent discoveries or repeat its physical
  replay. Preserve it as an alternative composition, distinguishing that
  validation coverage from the fresh #71/#74 construction audits.
* **#64 passes the scoped formal audit.** Accept its formal proof contribution
  with the explicit boundary above. The review checked 230 publication text
  hashes and freshly compiled all 298 declarations, but did not replay ten
  binary publication artifacts or the whole finite-certificate package.

No mathematical defect was found within these reviewed scopes. Recommended
integration order is the #71 foundation, the stronger #74 selected witness,
and #64's separately scoped proof package. Preserve #80's alternative and its
contributors. #74, #80, and #64 were drafts when this review began; this pass
does not change their GitHub status or imply a full-suite integration test.

Pinned source text and available binary blobs were materialized into isolated
review directories and checked against Git object hashes. Because the GitHub
connector cannot transfer gzip binaries, missing #65, #71 and #74 words were
regenerated. Their final bytes match the original hashes, including gzip
metadata. The #74 bootstrap deferred only checks of unavailable binary output
artifacts; its unmodified final source and certificate checks then passed.
No expected digest was changed to make a verification pass.

Main's selected witness remains unchanged until integration. Retain the newer
main-branch social/contributor work when resolving the submissions' older root
documents, and refresh affected provenance only after reviewing the exact
integration changes. No merge, workflow approval, or public review comment
was issued as part of this pass.

## Arrivals after the review was pinned

A final queue refresh found #81 (`acae4964aef41c69f3c57e72a45e76afc4d4934d`),
#82 (`3410b940aa26e5876202152dfa7c4f66451ee22c`), and #83
(`183077b7b3ae12e96eb3a87c1dc08023e6494dca`). The first two advertise larger
conditional witnesses, respectively `5.1915547765237e-5` and
`5.203279888519e-5`; #83 concerns depth-dependent profiles and an adaptive
recursion limit. They were not audited in this pass. #74 is the strongest
freshly construction-audited witness in this review, not a claim that no newer
submission is larger.
