# Validation receipt

Local host: macOS 27.0.1 arm64; CPython 3.14.7 (Clang 21.0.0).
Base: `dd6403f774a0891093a006ae9716c02e371b1fdb`.
Predecessor PR1224: `00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`, refreshed before submission.
All commands below ran successfully unless explicitly marked unrun.

```sh
python3 -I -B research/a8-simplex-decoder-floor/verify.py --write
python3 -I -B research/a8-simplex-decoder-floor/verify.py
python3 -I -O -B research/a8-simplex-decoder-floor/verify.py
python3 -I -B research/a8-simplex-decoder-floor/independent.py
python3 -I -B research/a8-simplex-decoder-floor/test_package.py
python3 scripts/research_package.py --package research/a8-simplex-decoder-floor --check-only
python3 scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p 'test_research_*.py'
git diff --check
```

Primary: `PASS_A8_SIMPLEX_DECODER_FLOOR planes=43435 eight_partner_cases=36 cost=72 controls=6`.
Independent: `PASS_A8_SIMPLEX_INDEPENDENT E8_dimension=8 planes=43435 eight_partner_cases=36`.
Eight package tests pass. The research workflow suite has 20 tests, with one
pre-existing environment-dependent skip. Selected-record integrity and package
metadata/source pins pass. Initial metadata validation correctly rejected a
free-text outcome value; TASK.json now uses the required `completed` enumeration
and records the substantive result in a separate field.

## Exact coverage and controls

The primary implementation enumerates every two-dimensional subspace of F2^9
(43,435), eight partner spaces per plane, all 14,400 label/Gram entries, all
14,400 entries of each attaining decoder, and all 36 exceptional eight-partner
cases. S9 symmetry to move any high-deficiency column to column zero is checked
using its eight adjacent transpositions. The independent checker regenerates
120 root lines in R8, reconstructs the pinned A8 weight frame, derives labels
from the Gram pairing and obtains the same complete finite classification.

Semantic controls:

1. Perturbing a witness coefficient breaks exactness.
2. Deleting the single nonzero entry activating term zero breaks exactness.
3. Flipping one label bit breaks the geometry/pairing validation.
4. A single deficiency vector has up to 255 partners, so the two-dimensional
   premise is essential to the one-dimensional-partner conclusion.
5. A concrete plane admits eight partners individually, which would suggest
   the false deficiency total ten; their mutual incompatibility rejects it.
6. A generic complex shift gives no zeros and costs 81, so it cannot evade
   the zero-ratio condition.

Package controls cover changed, missing and incomplete certificates; a changed
predecessor-frame fixture; an unsupported punctured domain; malformed geometry;
and the positive all-nine-active witness. A relocated, read-only package is run
with `-I -O -B`, and file hashes before and after replay agree. The normal replay
fails closed on receipt changes; only explicit `--write` regenerates it.

## Not run or claimed

Python 3.12 is not installed on this host, so the generic replay execution was
not run locally; its version-independent metadata check passed and VERIFY.json
registers all three scoped commands for that environment. Hosted CI is not
claimed. No Lean proof, native supplier admission, complete paid profile,
P112 experiment or full `make frontier1094-verify` replay was performed. The
selected supplier was not modified and is not a proof dependency of this
source-independent finite theorem. Selected-record verification checks binding
integrity, not the all-size theorem.

This is a scoped proof with exhaustive finite lemmas, not a heuristic search
failure. The original OS assignment seed 47 selects the track; the census is
deterministic and covers its complete declared domain. No independent human
review or proof assistant certification is asserted.
