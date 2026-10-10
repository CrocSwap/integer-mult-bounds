# Supplemental evidence for the 887-entrance composition

This sibling evidence directory preserves the original successful complete
replay, its source-manifest history, and reproducible supplemental audits. It
adds no mathematical hypothesis and does not replace the candidate package's
mandatory source-to-certificate verification.

## Original complete replay

`original-replay/VERIFICATION.json` records the successful complete replay at
conditional kappa `142291570675302016424949/200000000000000000000000000` and
physical-word SHA-256
`8593fa0359aa13b26ede7490f500f239c97d238df2730496a9ac29bcafd7b4ae`.
`original-replay/TOOLCHAIN.json` identifies its tested macOS/Python/Clang/SymPy/Boost environment.
No Linux or CI run is asserted by this historical receipt.

The receipt pins the original candidate manifest. Afterwards only README,
PROOF, and NOTICE prose changed, to clarify `R=A^-1 C`, identify the exact
historical witness overlap, and specify UTC. `original-replay/DOCUMENTATION-REVIEW.json` records
the original and revised manifest hashes; `original-replay/documentation-at-replay/` preserves
the original manifest and prose. Every executable, input witness, and expected
receipt remained byte-identical. These historical receipts are copied unchanged.
A later publication replay, if supplied alongside them, is separate evidence.

The candidate's exact dependency is PR265 commit
`fc00fcf07a554ff6847b2a8764ecc26f5a99542a`. The inherited verifier explicitly checks
its PR263 ancestor; preserve the stacked ancestry and the two inherited package
directories when reproducing. Copying just the candidate directory onto an
unrelated branch is insufficient.

## Supplemental audit reruns

Run with Python assertions enabled, after completing the main package replay.
In the commands below replace `CHECKOUT`, `EVIDENCE`, and `REPLAY` with the
checkout, this evidence directory, and the completed replay output directory.
The output filenames must be new. The drivers use explicit CLI paths and do not
compile native code or repeat the physical-word pipeline.

```sh
python3 -B EVIDENCE/audit/audit_arithmetic_controls.py \
  --package CHECKOUT/research/crosscut-response-pairs \
  --baseline REPLAY/baseline --candidate REPLAY/candidate-plateau \
  --output /tmp/arithmetic-controls.json

python3 -B EVIDENCE/audit/audit_frame_controls.py \
  --checker CHECKOUT/research/crosscut-response-pairs/verify_frame_tables.py \
  --export REPLAY/baseline/temporal/CURRENT249-EXPORT \
  --lead REPLAY/candidate-plateau --output /tmp/frame-controls.json

python3 -B EVIDENCE/audit/audit_response_matrix.py \
  --export REPLAY/baseline/temporal/CURRENT249-EXPORT \
  --selection REPLAY/combined-candidates.json \
  --output /tmp/response-matrix-controls.json
```

The arithmetic audit admits the original candidate, reproduces PR265's exact
intervals, complete 47-constraint/seven-margin assembly, bootstrap and cutoffs,
and rejects nine independent corruptions of its input price/invoice. The frame
audit admits an actual rank-two frame and rejects six corruptions, including a
rank-correct rational frame with a singular weighted Gram matrix. The response
audit checks invertibility of the target prefix block at all four selected cuts,
including the latest cut's 441 elementary target shears.

The saved audit JSONs preserve their original source hashes and historical
scratch-path metadata; those paths are provenance labels, not replay dependencies.
`greedy-plateau-frame-audit.json` also records the independent exact audit of all
916 candidate bases and annihilators. The actual acceptance checker remains in
the sibling candidate package.

## Historical public-witness comparison

`public-comparison/` contains copied public witness bytes, their SHA-256 pins,
and a portable comparison script. The 316 identical added pairs concern
**PR266 snapshot a2b02af47dbaf3d1c55e7586746c30e851b68102, with 851 entrances**.
They do not describe its later 883-entrance update at
`b2b2a33dc95eb2d4ad9ddfade6bb9416ab9ec38e`. No overlap computation against that
later update is claimed. PR267 is pinned to snapshot
`4f849bd0c08787d588d211ef5f5dbe60f32542b2`.

```sh
python3 -B EVIDENCE/public-comparison/compare.py \
  --package CHECKOUT/research/crosscut-response-pairs \
  --output /tmp/historical-witness-overlap.json
```

The script compares exact rational subspaces with SymPy and requires the original
`WITNESS-OVERLAP.json` result. These are attribution comparisons, not independent
replays of PR266 or PR267. The conditional scope, full inherited attribution,
and substantial Codex assistance remain as stated in the candidate's NOTICE.

## Inherited repository checks

`inherited-checks/check-status.json` and its logs record a passing
`make entrance-bank-verify`. A broader `make verify` attempt was interrupted
by request before completion, with no test failure observed before SIGINT.
It is explicitly incomplete; this is not a full-repository-suite pass.

## Final publication replay

`publication-replay/VERIFICATION.json` records a second successful complete
source-to-certificate replay against the final publication package manifest.
All native checkers and pinned receipts passed, with the same exact endpoint
and transcript hash. The stage logs are in `publication-replay/logs/`. This
fresh receipt binds the final documentation as well as all executable sources.
