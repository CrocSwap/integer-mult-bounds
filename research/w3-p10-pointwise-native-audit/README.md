This independent audit uses a distinct literal-word checker, endpoint tiling,
modular determinant elimination with exact Hadamard lifting, and a closed-form
bootstrap/outer-grid calculation. It consumes a completed full package replay:

    python3 -B verify.py --proof /tmp/w3-proof --output /tmp/w3-independent

The package defaults to the sibling `w3-p10-pointwise-native`; `--package` can
select its location. A C++17 compiler is required. The scripts originate in the
OpenAI Codex-assisted p10b independent audit; they share no construction tiling,
determinant or recurrence implementation. The small JSON header is taken from
the manifest-checked construction package.

The operator audit is F2 and verifies forward/inverse restoration and a control
that omits the twin restoration category. Signed elementary-shear inverse
semantics and integer decoder/recovery remain inherited, as do the published
compiler/chart/analytic interfaces. This does not claim a new unconditional or
Lean theorem. Prepared with substantial OpenAI Codex assistance; Apache-2.0.

The included receipts record two complete 21-stage immutable replays, observed
exits 0 in sessions 90130 (Python 3.11) and 84027 (Python 3.12), with identical
mathematical certificates. This separate five-stage audit exited 0 in session
95536. Omitting twin restoration creates 480 wrong rows; both original
orientations restore all rows. Absolute paths in receipts identify original
local inputs and are evidence metadata, not required replay locations.
