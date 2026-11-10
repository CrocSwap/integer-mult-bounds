# Coarse rounding audit of the actual P104 shared opening prefix

[PR #6678](https://github.com/CrocSwap/integer-mult-bounds/pull/6678) replaces
PR #6621's actual opening 18 ADDs with a shared 12-ADD preparation and one
zero-owned lifetime. Its exact h/2-grid identity remains valid. This package
answers its released rounded-backend question for two explicit, coarser h-grid
scalar models, interpreting only that local prefix.

Whole-destination nearest-even rounding gives an exact 512-class parity
classification: 258 entrances preserve public output and legal zero-CLEAR;
252 change public output and 128 leave nonzero owned residue (126 do both).
For odd Y, new-minus-old coordinate j is zero for even D_j and h*(2xi-1) for
odd D_j, where xi=(X+floor(Y/2)) mod 2. The pre-CLEAR owned residue is zero for
even X and h*(-1)^floor(Y/2) for odd X. Even Y is exact throughout.

Fresh independent stochastic half-rounding changes public covariance from
h²I_6/4 to h²11^T/4. Coordinate variance and total Euclidean MSE agree, while
variance in the unit all-ones direction increases sixfold. The new pre-CLEAR
owned residue is nonzero on half the coin assignments. These are delivery
stage covariances, not the distribution of a legal completed caller.
Complemented inverse choices or recorded/recomputed actual increments can
restore zero, with source/tape/control costs still to price. No universal
minimum retained-bit claim is made.

`PROOF.md` gives the all-integer laws. `RESULT.json` retains all 512 deterministic
rows and 256 joint coin outcomes, complete public errors and owned states,
source binding and exact rational covariance. `ORACLE.json` is the independent
implementation's receipt. `SOURCE-PINS.json` authenticates three inert PR #6678
documents, the actual compressed source word and original NOTICE. Only its
first 18 scalar ADDs are interpreted; the suffix is not executed or certified.

From the repository root with CPython 3.12:

```sh
python3.12 -I -W error -B research/p104-shared-prefix-rounded-audit/verify.py
python3.12 -I -O -W error -B research/p104-shared-prefix-rounded-audit/verify.py
python3.12 -I -W error -B research/p104-shared-prefix-rounded-audit/oracle.py --check-primary research/p104-shared-prefix-rounded-audit/RESULT.json
python3.12 -I -W error -B -O research/p104-shared-prefix-rounded-audit/oracle.py --check-primary research/p104-shared-prefix-rounded-audit/RESULT.json
python3.12 -I -W error -B research/p104-shared-prefix-rounded-audit/verify.py --emit /absolute/new/RESULT.json
```

The default strictly compares the retained receipt, including JSON types and
exact keys. Optimized mode retains all checks. Registered commands and
independent verification status are recorded in VERIFY.json/VALIDATION.md.
Exact h/2-grid execution covers all 512 entrances as a positive control;
1,024 signed/large translations test the parity law beyond canonical cases.
Literal CLEAR rejects nonzero owned state. Predecessor checkers are never
imported or executed. Finite evidence corroborates the proof.

Managed-code notes: local runs use the full managed CPython 3.12.14 executable
recorded in validation receipts. Python dynamic containers, arbitrary-precision
integers, exceptions and recursive typed JSON comparison are declared deviations
from low-level Power-of-Ten style; no such compliance is claimed. Source input
is fixed to five objects, gzip expansion is capped at 4 MB, domains are frozen
and every primary function is below 60 lines. Process time/RSS observations
are not physical caller costs or full process-tree admission evidence.

Credit: Nick Petalas's PR #6678 supplies the exact substitution and released
question; DreamingOfClouds's PR #6621 the expression and recipients, retaining
Ali Romman, Rohan Arun, Erwan L. and original NOTICE lineage. Direct earlier
principles include Arham Tahir's #2665 strict-zero cleanup, ywz65's #2730
mixed-grid collector repair, zxv's #6066 complemented stochastic inverse/tape
lifecycle, Nick Petalas's #5912 and ywz65's #2555 whole-sum tie/history, and
Petalas's #6134/#6573 with Ali Romman's #6540 covariance/error-price and
fixed-receiver correlation. Classical quantization, covariance and
compute/uncompute are not new here. Exact predecessor pins and overlap limits
are recorded in TASK.json and NOTICE.

## Open next questions

- Bind the covariance change to an actual receiver and tolerance. Start with
  its fixed reader matrix W and compare W Cov(E) W*. The caller's admitted
  norm/tolerance contract remains required.
- Integrate a legal inverse by recording or recomputing the actual increment,
  or by specifying complementary inverse randomness. First prove the complete
  local public/owned map; source access, tape/control lifecycle and their prices
  remain blockers. Cleanup repair alone need not repair public equivalence.
- Price the exact h/2 implementation and extra zero-owned lifetime on a physical
  caller. Start from PR #6678's 6a-i-c ledger, including allocation and cleanup;
  no concrete physical fee schedule is supplied here.

Full supplier/caller verification under the five inherited framework assumptions
remains open. No new kappa, selected-frontier change, global rounding barrier
or physical runtime saving is claimed.
