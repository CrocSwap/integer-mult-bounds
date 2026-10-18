# Freely weighted path valuations for the complex register search

PR705 leaves nine fixed eight-call Clifford register words unclassified
because their group collisions have different accumulated Fourier ranks.
This package lets the path weights vary and requires equal weights only for
coefficients that the endpoint must cancel. A determinant valuation argument
then excludes `evolved-27` for **every invertible choice of its four scalar
3-by-3 matrices**, even without a shared final frame per input column.

The certificate is small: interior weights `(1,0,1), (-1,-1,0), (0,0,0)`, row
potentials `(-1,0,0)` and column potentials `(0,1,1)`. Its weighted determinant
has degree zero, but every permitted determinant term has valuation at least
one. [PROOF.md](PROOF.md) supplies the general argument and model limitations.

**No new kappa or positive eight-call construction is claimed.** These are
fixed-word results in the predecessor's formal projective Clifford group
algebra, not a general eight-call impossibility theorem. Eight whole words
remain unclassified. [NOTICE.md](NOTICE.md) credits and pins the predecessors
and discloses substantial OpenAI Codex assistance.

## Exact replay

From the repository root, with Python 3.10 or later:

```sh
python3 -B -S research/weighted-path-valuations/verify.py
```

Expected: `PASS_WEIGHTED_PATH_VALUATIONS`. The replay uses only the standard
library, no numerical optimizer, network or generated work directory. It
also works with an absolute script path from an unrelated directory. Run
without `-O`; inherited source assertions are required, so optimized Python
is rejected explicitly.

`python3 -B -S research/weighted-path-valuations/validate.py` additionally
replays from a temporary directory and checks command-line integrity,
optimized-mode rejection and acceptance of equivalent gzip recompression.

The replay reconstructs the predecessor's nine unresolved cases, enumerates
2,187 full paths, and compares symbolic polynomial paths with independently
multiplied exact Gaussian matrices. Dense conjugation reconstructs Pauli
images; column supports independently check Fourier ranks. It then checks
919 exact certificates, three known nine-call constructions, 104 Laurent
determinant controls and mutations of the theorem hypotheses and coverage.
Source files are hashed; the compressed word corpus is pinned by its
decompressed payload so harmless gzip metadata changes are accepted.

## Finite census

Each choice is a triple of candidate full-rank endpoint frames, one per input
column. A blank numerical nomination is treated only as unclassified.

| Fixed word | Frame choices | Excluded | Unclassified |
| --- | ---: | ---: | ---: |
| evolved-01 | 48 | 40 | 8 |
| evolved-03 | 48 | 36 | 12 |
| evolved-05 | 180 | 168 | 12 |
| evolved-06 | 54 | 48 | 6 |
| evolved-11 | 324 | 322 | 2 |
| evolved-14 | 144 | 136 | 8 |
| evolved-24 | 125 | 118 | 7 |
| evolved-27 | 175 | 175 | 0 |
| evolved-31 | 54 | 50 | 4 |
| **Total** | **1,152** | **1,093** | **59** |

Of these choices, 865 already fail the allowed-entry perfect matching test.
The weighted criterion excludes another **228 of the 287 choices** that
pass that baseline. We do not claim all 1,093 as new exclusions or compare
exhaustively against the predecessor's support/polynomial methods.

`CERTIFICATES.json` contains 104 distinct integer weight/potential vectors.
For each word, `targets` lists sorted candidate frames. `frame_certificates`
is indexed by `itertools.product(*targets)`; an integer selects a vector and
`null` means unclassified. `evolved-27` instead has one `global_certificate`
for the weaker all-rank-three endpoint condition. Its entire frame product
is thereby excluded. `EXPECTED.json` records all counts and canonical hashes.

## Optional discovery

The separate discovery script requires NumPy and SciPy. Tested versions are
recorded in VALIDATION.json. It uses one HiGHS thread and verifies every
rationally reconstructed nomination with exact arithmetic before reporting
it. Solver infeasibility does not establish feasibility of a register word.

```sh
nice -n 15 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -B research/weighted-path-valuations/discover.py \
  --case evolved-27 --out /tmp/evolved27-weights.json

nice -n 15 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -B research/weighted-path-valuations/discover.py \
  --case evolved-11 --all-frames --out /tmp/evolved11-frames.json
```

The first should find a global obstruction; the second found 322 exclusions
among 324 choices in the recorded run. Certificates can differ between solver
versions: only their exact verification matters. `--word FILE.json` accepts
a new literal program in the inherited format for further research.

This standalone addition does not change the selected construction or
`upstream/`. Its affected checks are the local replay, integrity/relocation
controls and optional discovery. The full selected construction suite is
outside the scope of this addition.
