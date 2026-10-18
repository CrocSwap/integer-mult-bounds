# Attribution, source status and license

Prepared for **@chinmayarvind23** with substantial **OpenAI Codex** assistance
in research selection, proof development, implementation, automated checking,
code review and documentation. Separate AI agents developed the primary and
independent replays. This does not constitute independent human review, and
no human-only authorship or human review is claimed.

**Concurrent result.** During the final overlap refresh, after this package's
proof and code had been developed, we located **Sagar Thakrar / @thakrarsagar's
[PR #738](https://github.com/CrocSwap/integer-mult-bounds/pull/738)** at
`9671c5d72f3119ba26f3774f40aa7130c67bcf77`. That contribution already states
the same Gaussian copy floor of 40, the closure reduction, the uniform
640-clique certificate, its uniform-weight sharpness and the interval
[40,60]. It was prepared with substantial OpenAI Codex assistance. Those
overlapping conclusions are credited here; this package does not claim a
new discovery of the floor or treat its inclusion of empty-support pairs
as a mathematical advance. No #738 executable code was imported or used
to produce our replays.

The resulting scope is **independent verification plus an extension**.
The inspected #738 proof gives a ceiling of 48 for general nonnegative
clique weights. Section 5 of our [proof](PROOF.md) strengthens that ceiling
to 40 for all nonnegative weighted inclusion-maximal-clique certificates,
including mixtures of different maximal-clique sizes. It does not address
certificates using non-maximal cliques. The pinned
[#738 proof](https://github.com/CrocSwap/integer-mult-bounds/blob/9671c5d72f3119ba26f3774f40aa7130c67bcf77/research/gaussian-clique-copy-bound/PROOF.md)
documents the comparison rather than relying on its PR summary alone.

The Gaussian E8 line configuration, extension-ring reduction, decoder
question, symmetric cost-60 result and open copy-floor problem come from
**Joel Pulikkan / GamingPuzzled's
[PR #620](https://github.com/CrocSwap/integer-mult-bounds/pull/620)**, prepared
with Claude Opus 5.5 assistance. Its retained extension-ring files are pinned
in [SOURCES.json](SOURCES.json). This contribution does not claim that
geometry, problem formulation or upper bound as new.

The weighted-clique rank-averaging approach follows **Douglas R. Colkitt /
Mister-Meeseeks' [PR #703](https://github.com/CrocSwap/integer-mult-bounds/pull/703)**
for the ten Hurwitz E8 lines. The inspected head is
`358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`. Its
[original proof](https://github.com/CrocSwap/integer-mult-bounds/blob/358383e2f1b0f292d4d6eb897c06fd8558a4f5e6/research/hurwitz-asymmetric-copy-floor/PROOF.md)
and [original notice](https://github.com/CrocSwap/integer-mult-bounds/blob/358383e2f1b0f292d4d6eb897c06fd8558a4f5e6/research/hurwitz-asymmetric-copy-floor/NOTICE.md)
are retained byte-for-byte under [vendor/pr703](vendor/pr703), including
their attribution and license statements. Relative links within those
unchanged copies refer to the original package context.

The source/reader pairing-rank model and associated accounting derive from
**DreamingOfClouds' [#446](https://github.com/CrocSwap/integer-mult-bounds/pull/446)
and [#595](https://github.com/CrocSwap/integer-mult-bounds/pull/595)** work as
used by #620. Their use here is explicit and conditional. Standard E8 root
coordinates, Gram-rank identities and clique rank subadditivity are not
claimed as new.

The scoped contribution is the independent exact replays and the proof that
nonnegative weighting of inclusion-maximal-clique rank inequalities cannot
exceed 40 in this geometry. The lower bound and closure reduction overlap
with #738. We neither assert global novelty nor claim to settle the remaining
charge interval [40,60]. No predecessor implementation is imported by either
verifier. Pinned source files are read as data for provenance checks.

The repository base is
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[CLAIM.md](CLAIM.md) records the bounded overlap review; unreviewed PR claims
are source context, not adopted mathematical conclusions. The existing
selected construction and its predecessor lineage retain their credit and
assumptions. This package adds no supplier and changes no selected kappa.

New files are provided under the repository's
[Apache License 2.0](../../LICENSE). The original authorship and license
notices of the retained #703 documents remain in their unchanged copies;
this notice supplements them.
