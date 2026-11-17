# Sharp approximation floor for rectangular native fusion

This scoped written proof with exact finite corroboration was produced by Nick Petalas.
It extends the exact amplitude boundary of ToikY
[#7166](https://github.com/CrocSwap/integer-mult-bounds/pull/7166) to approximate
returned maps. It does not recheck that package's native word or invoice.

For two independent f-bit Gaussian tensor targets, put d=2^f and let a
rank-r child have flat entries of modulus 2^(-rf/2), with r>=2. Allow arbitrary
rectangular complex adapters whose maximum column-sum/row-sum norm product is
at most M, and an arbitrary bypass with at most h nonzeros per column.
The exact minimum maximum Euclidean column error is

```
sqrt(1-h/2^f) max(0,1-M*2^(-(r-1)f/2)).
```

The same formula is the exact minimum normalized Frobenius error. Every column
satisfies the lower bound. A two-spectator projected construction attains both
minima simultaneously, using bank expansion 2^((r-1)f). For fixed M and
sublinear bypass support, the error tends to one. At f=8, r=2 and M=1, error
at most 1/2 needs at least 184 bypass entries per 256-entry target column.

[PROOF.md](PROOF.md) states the full model, proof, attainment and limitations.
The attainer is an algebraic relaxation with expanded banks and an unpriced
bypass. No affordable physical fusion, improved kappa, selected-frontier change
or complete multiplication theorem is claimed. The error metrics are column
error and normalized Frobenius error; spectral-norm optimality is not claimed.

## Reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-approximate-native-fusion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sharp-approximate-native-fusion/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-approximate-native-fusion
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-approximate-native-fusion --check-source-history
```

The direct marker is `PASS_SHARP_APPROXIMATE_NATIVE_FUSION`. The checker
performs exact Gaussian-rational matrix multiplication, independent tensor-entry
checks, all bypass supports in six small tensor shapes, additional mixed-lane
adapters and phase/support/capacity controls. `--receipt PATH` creates a
hash-bound JSON receipt outside the checkout and refuses overwrite. Without
that option the checker writes only stdout. The all-parameter theorem is the
written proof, not an exhaustive numerical search.

Local CPython 3.12.15 checks passed for 140 attainers and 1,300 columns,
40 general adapter cases and 320 columns, 8,784 independent tensor entries,
three semantic controls, four capacity rejections and all 257 supports of the
threshold example. Normal and optimized generated receipts agree byte for byte.
Both registered checks passed. These finite checks corroborate the proof.

The registered replay runs both direct modes. No predecessor scientific suite,
selected cold replay, physical consumer, Lean or Docker check is required or
claimed. Independent human and formal proof-kernel review are unclaimed.

## Sources and scope

The canonical base is e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8, selected #7000. `SOURCES.json` pins the catalogue and selected record
as provenance. The card `coverage-law-change` changes to a local approximate
interface obstruction. This limits an attempted higher-rank fusion before
its full physical bill is known; it does not admit or exclude all suppliers.

The main predecessor is ToikY's #7166, proof at
`6efb5d028b3212fba68edfb725608413622d6ab6`. Its exact amplitude inequality and
projected tensor control are credited inputs. This package independently
implements its own small matrix definitions and uses no predecessor code or
external runtime inputs. Clear1nsight's #4932, #4045 and #3989 give related
scoped fusion boundaries. The retained Gaussian lineage includes zxv,
Clear1nsight #7161 and Rohan Arun #7113. Their results are cited, not audited.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541721).

## Open next questions

1. What is the exact spectral-norm optimum with the same adapter and bypass
   constraints? Column error bounds it below, but the sharp column attainer
   can leave correlated residual columns. Start with f=1 and h=1 and compare
   different bypass support patterns. A proof needs control of all input
   directions, rather than only individual columns.
2. What error is attainable under a charged bank expansion strictly below two?
   The present equality construction expands by 2^((r-1)f), so it does not
   meet that favorable paid-fusion allowance. Start with one exact rectangular
   source/consumer layout and price its bank stock, routing, restoration and
   bypass. This is blocked by a complete physical contract and invoice.

These questions and their blockers are also recorded in `TASK.json`.
