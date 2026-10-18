# Five early circuit contributions: completed historical integration

This round follows the [100-PR reconciliation](community-reconciliation100-review.md).
It covers **#2, #4, #8, #9 and #12**, including all **126 original changed paths**.
The contributions are retained as complete, runnable historical source snapshots;
their release wrappers do not replace the current selected result. **No new κ is
claimed.** The [selected record](../../certificates/selected-result.json) remains
authoritative.

| PR and contributor | Contribution retained | Focused checks completed |
|---|---|---|
| [#2](https://github.com/CrocSwap/integer-mult-bounds/pull/2), Andrew Barnes / Bortlesboat | Aligned common-point pair groups, saving 14,944 additions and supporting the historical conditional `17·2^-63` witness; proof/review packets and scoped ceiling | Six tests, including full h50 support expansion, small arbitrary-scratch basis checks, both frame orientations and negative controls; certificate and independent patch regeneration |
| [#4](https://github.com/CrocSwap/integer-mult-bounds/pull/4), David Leen / dleen | Retained complex totals composed with eumemic's shared exclusions; smaller h24 producer and additional complex-side headroom, historical `591/10^12` assembly | Five tests, full h24 coefficients and role frames, small dirty-scratch and physical phase checks in both directions, guard/assembly arithmetic and regenerated patch |
| [#8](https://github.com/CrocSwap/integer-mult-bounds/pull/8), Rohan Arun | Separate geometric-envelope complex construction; charged extra label coordinate makes the required binary residuals nonalternating; historical `59/10^11` assembly | Full h25 support and role-path checks; missing-coordinate negative control; 687,360 small physical phase comparisons; all 441 unequal-factor bit-screen cases |
| [#9](https://github.com/CrocSwap/integer-mult-bounds/pull/9), Rohan Arun | Ternary star-template refinement, saving 170,400 additions; historical `19/5000000000` assembly; unsuccessful alternative rules retained | Full h28 native producer twice with identical boundary demands; all 20,475 stars and 365 selected templates; exact F3 dirty-basis and role-support checks |
| [#12](https://github.com/CrocSwap/integer-mult-bounds/pull/12), Rohan Arun | h30 mixed-width composition, historical `12649/10^11` witness; matching/prime-power extensions and six-dimension negative census | Full native census at h24/26/27/29/30/32; seven complete matching enumerations; all 456 h30 templates and 164,002 basis directions per orientation; exact moment/29 assembly constraints, three negative controls and integrated patch |

## Scope of the source review

**Aligned pairing (#2).** The global pairing changes the local ordering, not the
weighted recursion. Relabeling exclusions must also canonicalize pair keys; the
implementation does so. Shared source spans retain a common point, and the
rational positivity argument survives. Both complemented reverse frames and
arbitrary scratch restoration remain necessary. The full h50 expansion checks
the actual merged support DAG, beyond just reproducing its counts. Its ceiling
applies to this fixed construction and historical inequalities only.

**Retained totals (#4).** The scatter formulas must be interpreted as differences
of two passes with arbitrary initial totals. They do not assume dirty totals
already satisfy the clean algebraic relations. Extra half-updates for the
`(5-h)/2` coefficient are charged in the scalar depth bound. The historical
`artifacts/retained-complex-note.pdf` predates the final shared-retained correction;
it is preserved for provenance, **not used as evidence for that corrected
construction**. Use the editable source, tests and regenerated certificate.

**Envelope geometry (#8).** The disjointness DAG uses coordinate envelopes;
intersection-two stars use orthonormal indicator spans. A genuinely charged
unused coordinate supplies a norm-one vector in output/cleanup complements.
This addresses nonalternation, which rank or nondegeneracy alone would not
establish. The small physical audit covers full invocation paths and tensor
stages, while the written residual argument supplies the general-size step.
The 441-case bit census establishes only its stated bounded screen.

**Ternary refinement and dimensions (#9/#12).** The replacement DAGs stay inside
common-four-point stars, preserving the common-pair rational positivity argument.
Exact support equality and both role orientations are checked for every selected
template. The dimension extension replaces the Euler-tour restriction with a
cyclic ordering of complete-graph edges, preserving intersection-two matching.
At h30, the controlled-basis boundary inequalities still hold and the whole
mixed-width moment is charged. Six dimensions lose against #9 under the old
uniform-width cost; h30 wins under #10's mixed-width interface. These are different
cost models, not inconsistent conclusions. The q=5 and q≥7 exclusions concern
the stated retained-center/output compiler; q=4 and other architectures remain
outside them.

## Evidence and integration boundaries

The [source inventory](../../research/community-historical-five-audit/SOURCES.json)
records each full exact-head tree and the original GitHub-base diff. The
[per-file decisions](../../research/community-historical-five-audit/DISPOSITIONS.json)
separate old release wrappers, original notices, already incorporated dependencies,
and newly retained research. A deduplicated archive preserves all five trees,
including proof sources, unsuccessful experiments and original assistance disclosures.
Extraction and focused replay are documented in the
[package guide](../../research/community-historical-five-audit/README.md).

All regenerated certificates, screen reports and patches match the original
tracked bytes. All three new historical patches apply to their bundled upstream.
Checks ran locally on macOS with Python 3.12 and Apple Clang; this report does not
claim a completed Linux run or a rebuilt PDF. The extraction path is separately
checked against the original blob inventories.

The review is agent-assisted source inspection and finite execution. It does not
formally verify the general multiplication theorem, all-size tape compiler,
compact-control/precision interfaces or upstream analytic arguments. In particular,
#12's unchanged #10 controlled-basis, row and Gaussian sources are retained and
identified as inherited dependencies. The existing scoped reviews of those sources
are not replaced by a fresh full theorem audit. Preserving and merging an alternate
historical research construction does not select it as today's supplier.

## Attribution and next work

Andrew Barnes, David Leen and Rohan Arun retain authorship of their contributions.
Predecessors include **eumemic** for shared complex exclusions; **Zhihao Chen /
jacklightChen** for the ternary geometry, paired producers and retained-total
schedule; **icekylinx** for mixed-width controlled batching and the complex
depth/Gaussian corrections; and Douglas Colkitt and all authors named in the
original notices. Parallel alternatives are credited even when their numerical
checkpoint was overtaken. Original AI-assistance disclosures remain intact.

The next reconciliation work is the remaining source families in the frozen
100-PR inventory. The original 100-PR report is a historical snapshot: this round
resolves five of its 97 carry-forwards, leaving **92** from that batch. This is
not a live count of all open GitHub PRs, and does not automatically close separate
predecessor PRs whose other content has not yet been reviewed.
