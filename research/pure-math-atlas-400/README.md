# Pure Mathematics Atlas: Constructive Lemmas and Research Directions

Four informal volumes contain **400 numbered entries: 379 proved lemmas/theorems and 21 explicitly unproved conjectures or research proposals**, with 100 entries per volume. Every proved entry supplies its hypotheses and English proof; every conjectural entry gives motivation, evidence, and a concrete direction or falsifier. The collection is broader pure mathematics, rather than a multiplication-exponent deliverable.

| Volume | Subject | Proved | Conjectural | Read |
|---|---|---:|---:|---|
| I | Algebra, tensors, symmetry, descent and exact recovery | 96 | 4 | [Algebra](volumes/01-algebra.md) |
| II | Finite geometry, frames, designs and unbiased bases | 93 | 7 | [Geometry](volumes/02-geometry.md) |
| III | Combinatorial certificates and discrete structure | 90 | 10 | [Combinatorics](volumes/03-combinatorics.md) |
| IV | Positivity, moments, stability and harmonic analysis | 100 | 0 | [Analysis](volumes/04-analysis.md) |
| **Total** | | **379** | **21** | [All 400 entries](INDEX.md) |

Start with the [mathematical guide](MATHEMATICAL-GUIDE.md) for useful proof routes and the precise gaps each conjecture addresses. The [conjecture register](CONJECTURES.md) links directly to all 21 statements and distinguishes classical open directions from atlas proposals whose global status was not established.

## Results worth reading first

- [A059](volumes/01-algebra.md#a059): an explicit fractional formula for symplectic chart changes, with the correct invertibility domain and symmetry condition.
- [A084–A089](volumes/01-algebra.md#a084): constructive semilinear Galois descent, including bases, morphisms and compatible algebraic identities.
- [B030](volumes/02-geometry.md#b030): exact weighted reconstruction with a full covariance comparison against every other unbiased linear reconstruction.
- [B097](volumes/02-geometry.md#b097): a prime-phase codimension-one flat matrix can be completed while preserving the prime-root alphabet; a counting proof supplies the missing phase.
- [B098](volumes/02-geometry.md#b098): a deficiency-one symplectic partial spread always completes, by an exact hole-count and orthogonality argument.
- [C035](volumes/03-combinatorics.md#c035), [C074](volumes/03-combinatorics.md#c074), [C097](volumes/03-combinatorics.md#c097): concrete existence certificates from cuts, polynomial coefficients and Fourier energy.
- [D059](volumes/04-analysis.md#d059): a positive flat Hankel extension constructs, and uniquely identifies, an atomic representing measure.
- [D074](volumes/04-analysis.md#d074): the rectangular polar factor minimizes both operator and Frobenius distances to isometries, with a unique Frobenius minimizer and an explicit perturbation bound.

These are useful reconstructions and local derivations, not claims that the listed mathematics is globally new. The two completion statements B097 and B098 have proofs here; the originally proposed deficiency-two spread assertion is not claimed solved.

## Evidence and review

The author of each volume and a separate agent read its statements and proofs. Their [review reports](reviews/REVIEW-INDEX.md) record corrections and final draft hashes. The sources include 31 inspected references to 30 unique files in the linked canonical Lean tree, bounded read-only queries of the authoritative DAG, and primary literature. [Source hash recheck](sources/SOURCE-HASH-RECHECK.json) authenticates the inspected revisions; [attribution](ATTRIBUTION.md) and [bibliography](BIBLIOGRAPHY.md) distinguish precedents from current arguments.

This is an **informal** collection. No new Lean formalization or kernel verification is claimed. The proofs use the elementary and classical background declared in each volume. Source-only indexing, historical DAG receipts, supplied completion data, and open targets are never treated as fresh proofs. The canonical DAG and Lean sources were used read-only.

The 13 literature-identified conjectural directions remain distinct from eight atlas proposals with bounded retrieval and unestablished global status. In particular the collection does not claim 21 newly discovered globally open problems, or 400 new mathematical discoveries. Recent proof announcements are identified as announcements rather than independently audited theorems.

## Files and reuse

[INDEX.md](INDEX.md) is the human entry index; [CATALOG.json](CATALOG.json) provides IDs, kinds, titles, section locations, dependencies and proof/evidence flags. The source ledgers preserve exact inspected paths, declaration excerpts and hashes. The deliverable itself requires no Lean installation. Displayed LaTeX uses GitHub’s documented double-dollar math blocks.

Run `python -B validate_atlas.py` from this directory to check all 400 IDs, proof/evidence fields, relative links, the catalogue and every packaged SHA-256. This validates packaging, not mathematical truth. [MANIFEST.json](MANIFEST.json) contains every final file except itself. [PR-DRAFT.md](PR-DRAFT.md) supplies an accurate suggested branch, title and body; [UPLOAD.md](UPLOAD.md) identifies the single short-path browser batch. Nothing has been published.
