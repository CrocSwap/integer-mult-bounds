# Validation receipt

Local execution on macOS, CPython 3.12.13, 2026-10-13. No external packages.

| Check | Result |
|---|---|
| `python3 -I -B research/p112-masked-walsh/verify.py` | PASS; 572,320 cases, minimum 72; full all-real relaxation; 35.63 s wall in a concurrent run |
| `python3 -I -O -B research/p112-masked-walsh/independent_check.py` | PASS; all histograms and 28 literal endpoint identities agree |
| `python3 -I -B research/p112-masked-walsh/test_verify.py` | PASS; isolated optimized standalone relocation, receipt/source/geometry corruption rejection, existing export preservation; 89.28 s |
| Exact source bytes | PR845 geometry, proof and notice hashes checked; generated geometry compared to the frozen artifact |
| Independent receipt rejection | Missing relaxation, corrupted minimum and duplicate pair entry each rejected |
| Scope/whitespace | Selected record byte-identical to base; staged changes confined to this package; `git diff --cached --check` passes |
| Mathematical controls | Cost-64 baseline; dependent/independent F2 ranks; zero terms; omitted-total and corrupted-residual rejection; unmasked Walsh cost 66; 91 rational support probes across four cuts; critical coefficient 2 distinguished; both escape-source augmented ranks equal 9 |

The independent worker first found and corrected its own packed-dual decode
typo before its successful replay. After review, its receipt validation was
tightened to require the relaxation, exact case/min/max counts and 28 unique
pair entries; optimized replay was repeated after that change. The first
implementation does not share its cost code with the direct-pairing checker.
Both use the same pinned geometric data, with separate full Gram/pairing checks.

The initial experiment was a finite unimodular census. Its observed loss led
to the additional all-real support-cell relaxation. This is a documented
refinement within the claimed mechanism, not an unsupported continuous
optimality assertion or a broader failed-search theorem. The primary certificate
was regenerated after adding the refinement and all controls.

This isolated addition changes no existing generator, selected supplier,
selected certificate, global Makefile or upstream source. Repository-wide
`make verify`, selected-supplier cold replay, hosted CI, and Lean were not run.
The sparse worktree contains only the research inputs needed for this scope.
The checks above validate this research package, not the inherited full
multiplication theorem or a physical implementation of the rejected decoder.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The final source/claim overlap receipt is [OVERLAP.json](OVERLAP.json).
