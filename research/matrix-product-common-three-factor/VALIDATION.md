# Validation scope

Python 3.12.2, macOS27.0 arm64, standard library. Registered ordinary and
optimized commands pass in about three seconds together. The receipt is
regenerated from 1286 constructor executions, not an all-target census:
226 distinct binary rank-at-most-one 4x4 targets, zero/identity and 64 seeded
samples per (field,block-size) pair, and four source-cut fixtures. Sample
families may overlap. Fields are 2,3,5,7 and block sizes1..4. The written proof,
not these bounded checks, establishes generality.

The independent endpoint oracle does not use predecessor multiplication or
rank helpers: it checks all fixed columns, full products, and common-chart
rank equality with its own elimination. Six embedded scalar rank-one
components have no common two-factor chart, despite each individually having
one. All96 component dirty-vector executions pass. Thirty executed controls
cover illegal fixed columns, chronology, omitted factors and invalid input.
No independent human or proof-kernel acceptance is claimed.

ROOT REVIEW.json records the exact hash and scope of separate root proof
review; it reviews the upper theorem and lists later checks separately.
Source-history/committed-byte and official export integrity are publication
checks. Git-free cold replay and deliberate source/typed-receipt corruption
checks are recorded in the external publication receipt, rather than claimed
as mathematical or hosted-CI acceptance. No selected/native/Lean replay.

Commands:

```
python3.12 -B scripts/research_package.py --package research/matrix-product-common-three-factor
python3.12 -B scripts/check_research_commit.py --package research/matrix-product-common-three-factor --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/matrix-product-common-three-factor --ref HEAD --output /tmp/common-three-factor.tar
python3.12 -B scripts/export_research_package.py check /tmp/common-three-factor.tar
```

After safe extraction, run the direct `verify.py` command with Python3.12 -I
-B and -O as desired; no Git or undeclared predecessor imports are needed.
The retained PR4805 helper file is explicitly included by VERIFY.json.
