# Rank-homogeneous paths: a determinant obstruction

**Scoped theorem and exact finite verification. No new kappa or primitive.**

A scalar determinant tracks accumulated unary rank whenever all paths with
the same interior group product have the same rank sum. The resulting
inequality rules out a saving, for any number of scalar mixing blocks and
arbitrary invertible complex coefficients, subject to that explicit path
hypothesis. See [the complete proof](PROOF.md).

This closes eight previously unresolved four-block Clifford words and 23
additional evolved words at m=3, W=3, s=8. It also recovers the 33 exclusions
in [PR #680](https://github.com/CrocSwap/integer-mult-bounds/pull/680) by a
different argument. Nine supplied words fail the new hypothesis and are
kept as unknown, not reported as solutions or impossibility results.

## Replay

Python 3.10+ and the standard library are sufficient. From the repository:

```sh
python3 -I -B research/graded-path-obstruction/verify.py
```

Expected: `PASS_GRADED_PATH_OBSTRUCTION`, with 64 exclusions and nine words
not excluded by this criterion. The checker uses no network, Git checkout
dependencies, external solvers, or sibling research directories. It writes
no files. Assertions are required; optimized execution is explicitly rejected.

The replay checks the finite hypotheses using both signed Clifford tableaus
and exact 8-by-8 Gaussian matrices, including 1,377 interior paths. It also
checks 73 polynomial determinant identities, three exact nine-call positive
controls, a heterogeneous inverse-pair control, and deliberate certificate
corruptions. It compares the complete result with [EXPECTED.json](EXPECTED.json).
Input and source integrity checks are described in [VALIDATION.json](VALIDATION.json).

The general conclusion rests on the written determinant argument, not on
extrapolation from these finite controls. The obstruction is to formal group
algebra words with the stated fixed unary layers. The full W=3, s=8 problem
from [PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288) remains
open. There is no bit-side construction, supplier invoice, all-size compiler
proof, or change to the selected frontier here.

## Search consequence

The eight follow-up words originally survived very short polynomial searches.
Diagonal gauge normalization then provided exact refutations of the seven
stored arithmetic supports, but bounded searches over other supports still
stalled. Inspection of their collision classes exposed the determinant
criterion, which closes the whole fixed words without coefficient search.

For future synthesis, require a collision between **different accumulated
ranks** before spending time on scalar coefficients. This is a necessary
filter, not a score predicting existence. The 32 evolved words here are a
finite literal corpus, not a claim that their generator families are exhausted.

`words.json.gz` contains all 73 literal words; matrix entries at `mix3` gates
are identity placeholders marking locations where the theorem permits any
GL(3,C) matrix. `screen.py` checks the hypotheses. `verify.py` reconstructs
them using independent Gaussian matrices. `model.py` and `dense.py` are
unchanged, attributed copies from the public PR #680 head.

See [NOTICE.md](NOTICE.md) and [ORIGINS.json](ORIGINS.json) for source pins and
attribution. No independent human review, Lean verification, repository-wide
replay, or remote CI is represented as completed.
