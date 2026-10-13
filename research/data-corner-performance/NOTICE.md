# Attribution and license

This contribution is under the repository's Apache-2.0 license.

Prepared for Denis (@just-mn) with substantial OpenAI Codex assistance in implementation,
experiment design, documentation and scoped AI review. No independent human
review is claimed.

The actual checker is the unchanged source at
`research/copied-fixed/data_corners.cpp`, pinned in `SOURCE.json`. Its header
credits Rohan Arun's PR39 geometry checker, James Chang's PR34 pivots, and
OpenAI Codex assistance. Douglas R. Colkitt maintains the repository and its
historical integration and verification infrastructure. This package retains
the original source header in both generated compilation units.

The historical source manifest `research/copied-fixed/SOURCE.json` records:

- James Chang / jamesyc, PR34, `7fecbe3651e095fb0f450756afdeefd2a9ee80a2`:
  reversed geometry and all-weight rank-cut identities.
- Rohan Arun, PR39, `70ae24129649f6d6d4ec6360962a80c3c42a38f1`:
  fixed-middle modular nonvanishing method.
- Rohan Arun, PR40, `43f59ff533598762cbc43a5e14af2bbbc76fabbd`:
  the contemporaneous both-fixed baseline.
- The same manifest retains the broader construction and recovery lineage,
  including Dominik Scholz, icekylinx, RaD / hipotures and Chafik Boukhalfa.

eumemic's PR154 (`f571bcbd6e06618aeae0b8279da48060032dc74b`) identified this
repeated historical workload as a verification bottleneck. That report is the
profiling lead; this package introduces the per-pivot update-column optimization
and imports no code from PR154 or any pending optimization PR.

Recent tooling contributions #707, #709, #721, #727, #736, #752, #756, #778 and
#779 improve distinct determinant, geometry, archive, footprint, inverse,
Hermitian, Fano, Gram and reclamation kernels. They were checked for overlap;
they are not dependencies or independent reviewers of this contribution.
