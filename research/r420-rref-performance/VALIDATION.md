# Validation receipt and limits

Local environment: Linux x86_64, CPython 3.14.7. Assignment seed 94.
Upstream base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

Completed:

1. `python -I -B research/r420-rref-performance/verify.py --out /tmp/r420-rref-final-receipt.json`
   passed and reproduced `EXPECTED.json` exactly: 672 frame RREF/nullspace
   comparisons; 1,090 additional matrix cases; four arithmetic-defect controls;
   five geometry rejections and one valid signed-coordinate permutation;
   four source-pin corruptions; optimized-Python refusal; complete 660-column
   checker; original nine negative and one positive controls with identical
   diagnostics. These are finite tests, not a formal multiplication proof.
2. Seven alternating fresh-process pairs for **each** of the complete checker
   and original mutation harness passed. All 28 timed outputs matched their
   verified output hashes and the corresponding opposite-engine bytes.
   `evidence/benchmark.json` contains every timing and environment/source pins.
   Its measured Python file hashes were checked against the packaged files.
3. A minimal relocated copy in a path containing spaces, containing only this
   package and the three pinned PR543 inputs, passed `verify.py` from `/tmp`.
   No dependency was downloaded and no full repository was available there.
4. Partial selected-record binding passed: exact rational/decimal κ, selected
   assembly SHA-256, and the selected manifest's hashes for the three consumed
   PR543 files. This is explicitly **not** the full selected inventory check.
5. The GitHub-fetched base commit object was reconstructed and SHA-1 verified as
   the exact upstream base; original root and research tree IDs also matched.
   The final contribution commit adds only this package to those trees. Patch
   application and staged whitespace checks are recorded in the handoff.

The source subset was fetched using the GitHub connector because direct Git
transport could not resolve github.com. A local development snapshot is distinct
from the exact upstream parent; the deliverable patch's parent is the latter.
Only the necessary original files were materialized locally.

Not run: repository-wide `make verify`, `make selected-record-check`,
`make frontier626-verify`, C++ physical columns, full supplier reconstruction,
hosted invoices/moments, outer assembly inequalities, Lean, remote CI. This
isolated opt-in adapter changes no generator, default verifier, selected source
manifest, construction or certificate. These broader results are not claimed.

Overlap refresh read the recent queue through #732 and searched all PRs for
RREF and R420/elimination. No duplicate R420 RREF/nullspace adapter was found. #367 is the
explicit arithmetic dependency, #709 is geometry caching, #707 batches Gram
determinants, #721 streams reconciliation archives, and #727 uses owner footprint
masks. #731 independently checks the R420 compensation matrix over F2, whereas
this adapter preserves the frame geometry's rational RREF. All remain distinct.
Main was still the exact base and no pinned coordination issue existed.

An initial clean patch and offline replay package were handed off while no
writable fork was available. The user subsequently created
MrPink604/integer-mult-bounds, and the connection reports push access to that
fork. Publication uses a separate branch based on the exact upstream commit.
Only claim/submission documentation changed after the measured and verified
package; every Python source hash still matches the benchmark receipt. No
upstream or selected-frontier edit was made.

Prepared for @MrPink604 with substantial OpenAI Codex assistance; Apache-2.0.
