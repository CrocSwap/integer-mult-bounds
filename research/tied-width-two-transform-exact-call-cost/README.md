# Exact two-call cost at tied width two

In the widened complex register-mixing game of JacobAlanSussman PR #4628 and NickPetalas PR #5178, the dense transform at tied width two costs exactly two paid calls for every m>=2 (one for m=1). The written proof supplies all-m sector-algebra generation, the arbitrary-clean-helper lower bound, and a two-call factorization with every helper reset. This is not an affine-engine or physical-cost theorem.

Read PROOF.md for the complete hypotheses and proof. verify.py uses exact integer/rational operations, pins both actual source contracts, checks the first two dimensions and actual complex transform gauges, and requires the complete typed RESULT.json. Finite controls support but do not replace the quantified proof. Source PR #4628 is retained byte-identically as engine-predecessor.md, with its original commit and blob recorded in SOURCES.json.

Reproduce with Python 3.12: `python3 -B research/tied-width-two-transform-exact-call-cost/verify.py`. No dependencies, solver or proof assistant are needed.

## Open next questions

Price the finite free-projector implementation in an actual physical caller, or determine the optimum when the widened free register maps are disallowed. The present result does not settle either question or alter the selected multiplication frontier.

The separate `independent.py` checker adapts the independent root reviewer’s exact sparse-factor construction, with ordered tensor-to-sector conversion and all four-root projectors. It imports no primary verifier. Run it with the same Python command. The engine source pin points to its first retained commit so the export has verifiable publication ancestry.
