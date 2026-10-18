# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- This package continues the author's #2639 (*Decoder floors, closures*, ready; windows `h = 10, 11`) and its parent #2338 (*Decoder floors are tight in the frontier format*, open); the model, the notation (root code, fitting `B`, Lemmas S and M, the second gauge), the SAT encoder `sat/hk3.py` and the inherited pricing model are theirs, which in turn build on #446, #595, #1590, #2111, #2125, #2162, #2228, #2244, #2277 (author's own).
- **#1212** (burntout76; merged): Theorem 1, global gauge rigidity of the rank-8 realisation on P112, cited in README section 7 for the scope statement; `verify.sh` step 8 only checks that the text is present in the repository tree.
- The pricing model is imported (not copied) from `research/format-limits-corrected/scripts/skel.py` + `cert.py` and `research/complex-local-word-ceiling/ceiling.py` (Douglas R. Colkitt; pinned by sha256 in `SOURCES.json`).
- Tools: kissat 4.0.4 (SAT; never CaDiCaL); `drat-trim` (Marijn Heule and Nathan Wetzler), not vendored; numpy, networkx, pynauty (Brendan McKay and Adolfo Piperno's nauty, via pynauty) for the data and orbit checks.
- No file is copied from another contributor. `lib/e8.py`, `scripts/provenance.py` and `LICENSE` are the author's own files from #2639 / #2338; `sat/hk3.py` is #2639's `evidence/h10/hk3.py` with two marked edits (README section 5); `census/cen.cpp` and `census/mc.cpp` are the author's working-card programs (`mc.cpp` with one marked edit: optional range arguments).
