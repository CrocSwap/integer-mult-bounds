# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- **#446** (cost model, Theorem C), **#595**, **#1590**, **#2111**, **#2125**, **#2162**, **#2228**: the model, the dense pairing, the polar law and the root-code floors that this package extends; **#2228** also stated Conjecture ID, whose branch (a) is corrected here.
- **#968**, **#1077**, **#1180**, **#1212**, **#1236**, **#1744**: the E8 / P112 / P104 floors for 8 terms, for factors in the live root code, rigidity, and the 9-term decoder outside the root code; **#2176**, **#2206**: forced minors; **#2244**: the Lagrangian bound (same model).
- **#1331** (Arham-Tahir64), **#1375** (commdata2338), **#1460** (bbMisk), **#1468** (bitplane), **#1591** (Arham-Tahir64): the "free rectangle" mechanism (zero-cost corrections supported on zero-pairing rectangles; scoped P112 results). Proposition 3.1 is the same move applied to whole units; what is new here is its use against Conjecture ID (a).
- **#1224** (joaqcoo), **#1633** (bbMisk), **#1815** (jmbarrancoml): the E8 / P112 overcomplete and outside-the-root-code structure and the forced-Gram mechanism that Lemma OC and Lemma 7.1 are close to; credited in README §4, §7, §8.
- **#2137**, **#2232**, **#2240**, **#2247** (1337isnot1337): independent exact E6 screens; #2137 found the one-dimensional kernel of the orthogonal-zero constraints independently.
- Tools: kissat 4.0.4 (SAT); `drat-trim` (Marijn Heule and Nathan Wetzler; upstream source vendored in `research/p111-minrank-proof-reconciliation/vendor/drat-trim/`); Lean 4 + Mathlib (`lean/`). The Shadow Lemma is Lemma CR2 / `hadamard_diag_rank_sum` of #2162 (`lean/DecoderDuality.lean`; rectangular Lean form in #2267), cited, not shipped.
- No file is copied from another contributor. `lib/report.py` and `scripts/provenance.py` follow the author's own package `research/line-system-saturation`.

## New in this package

Everything under `research/overcomplete-and-realisation-floors/`: `README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `requirements.txt`, `lib/*.py`, `checks/*.py`, `sat/*.py`, `scripts/provenance.py`, `lean/*`, and the evidence files `data/*.json`, `sat/results.jsonl`, `sat/joint_results.jsonl`, `sat/cnf/`, `sat/models/`, `sat/proofs/` (all produced by the generators in this package; the decoder families of `data/` were exported from the author's working cards and are re-verified by the checks: `c6.decoders` recomputes the exactness of the 26 E6 square decoders).
