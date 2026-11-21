# Source coverage and remaining obligations

This is a bounded source archive and self-contained Python replay. Exact
repository-relative paths, commits, Git blob IDs and SHA-256 values are in
[SOURCES.json](SOURCES.json). Identical original bytes are retained for every
listed upstream source. The package's own paper proof and Python scripts are
new; they are not represented as upstream files.

| Source | Included | Role in replay and review |
|---|---|---|
| #7852, `41beda1d6435760dc99e38bd7e65f36798aad212` | `LinP104Base.lean`, `LinP104FreeInstBase.lean`, `DecoderWall.lean`, original notice and license | Python parses and pins the label and E8 instance tables. `DecoderWall.lean` is inert model context; Lean imports and the rest of the toolkit are not included or built. |
| #7855, `3a12128490d09cd2070678b989c647169c81c255` | README, original P104 notice and source metadata; the shared license is at packet root | The unchanged README states the single-gauge subset proof. Its `probe.py`, Lean transitive sources and full registered package are not included or rerun. |
| #7869, `06c207a9feb3994a4b987dc3010657b6e85b7956` | `notes/den4.md`, original notice; the shared license is at packet root | Sections 3 and 4 were read for the bounded overlap comparison. The carry/Toeplitz program, other 100 lane notes, certificates and rest of the package were not exhaustively screened or replayed. |

The first-principles input for this replay is exactly the pinned P104 table
and displayed E8 factorization. It independently checks all 10,816 live-mask
decoder equations, all binary prices by two elimination routines, difference
constraints and mod-2 reductions, the maximal-set graph bound, and the
explicit overlap and non-submodularity controls. Integrity mutations are
separately rejected in the cold copy. Source integrity does not establish the
upstream theorems or build history.

To turn the weighted condition into a decoder-independent 56 bound, one
would still need to produce suitable gaugeable sets and row-budget weights
for every decoder in the desired class, including a putative mass-below-56
decoder. To use it for a network, a separate extraction/price domination
argument is needed for its actual factorization. A word or caller bound
would additionally require its own complete transfer and invoice. None of
those obligations is supplied here; neither is a Lean proof of the new lemma.
