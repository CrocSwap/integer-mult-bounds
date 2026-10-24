# Exact native-query limits

This package retains completed proofs from the October 12 research run. It gives no new supplier, complete kappa value, or integer-multiplication lower bound.

The native model is from [PR #521](https://github.com/CrocSwap/integer-mult-bounds/pull/521), at `a190fdb39f31647fc6f651625353710624627348`. The pinned proof is in `vendor/PR521-PROOF.md`. The original source pins and credit statements remain in each source folder. OpenAI Codex assisted the proofs, checks, reviews, and this package. No literature-priority claim is made.

The retained results are:

- Rational monomial rank-one ADDRESS queries need at least `p*m` negative-determinant queries for `p` productive roles and `m` ADDRESS coordinates. Arbitrary dirty helper roles must return unchanged. The bound is sharp.
- Finite rational ADDRESS groups in three coordinates need at least `3*p` queries. The proof uses the stated finite-reflection classification theorem.
- Three productive roles and a plane endpoint need at least six rational rank-one queries. The proof covers all determinant signs and restored dirty helpers. Six coordinate-reflection queries attain the bound.
- Exactly two queries outside a subgroup with a C2 character give `p <= k+1`, where `k` is the number of active inside queries. A common rational basis with all maps equal to identity modulo two gives the separate bound `q >= p*m`.

These statements require exact formal group-algebra equality. They do not exclude all dense eight-query words in three coordinates or other helper contracts. Old failed search logs and narrower replaced filters are excluded.

Run with Python 3 and the standard library:

```sh
python3 -B verify.py --work /absolute/path/to/a-new-directory
```

The driver checks all source hashes, copies the source to the new directory, and runs five exact checkers. It does not change the package. It checks the monomial bound with two engines, the finite-group representation, and both independent plane certificates. The two-outsider and congruence results have written independent proof reviews. Their general statements are not established by a finite test. Historical source records remain byte-exact; their old paths and dates describe the original run.

The driver removes `PYTHONOPTIMIZE` from the child-process environment so that child checks and their descendants keep assertions enabled. `OPTIMIZATION-ENV-VALIDATION.json` records a fresh replay with `PYTHONOPTIMIZE=1` and an isolated parent interpreter.

## Source credit

[PR #521](https://github.com/CrocSwap/integer-mult-bounds/pull/521) supplies the exact native query model. Its [pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/a190fdb39f31647fc6f651625353710624627348/research/native-unipotent-fusion/PROOF.md) and [source pins](https://github.com/CrocSwap/integer-mult-bounds/blob/a190fdb39f31647fc6f651625353710624627348/research/native-unipotent-fusion/SOURCE-PINS.json) credit the ordered-stream and ADDRESS-interchange contracts. Those source files name no individual contributor for this primitive. No individual author is inferred from its submitter.

Swapnil Jain's [algebraic source](https://doi.org/10.5281/zenodo.23265442) supplies the prior determinant-sign character into dual numbers and broader rank-one relation methods. These are prior methods; the matrix-valued monomial representation and its inner-rank bound are the scoped results reviewed here. The exact inspected algebraic section has SHA-256 `e58a5d5a7fdcbbd583055e0adf419e5c22cc15aebb85ac14b2e05bd53d3e5f63`. The record is in `source/native-dual-independent/SOURCE-PINS.json`. PR #521 also records an older `rho4` construction on an odd-denominator mod-4 grammar. The congruence proof in this package applies that reduction method to an arbitrary common congruence basis and a restored-helper endpoint. It is retained as a precise statement of that method, without a priority claim. This qualification replaces the historical sentence that calls the proof original work. The exact earlier `rho4` note was not identified in the retained source tree. The finite-group result inherits the finite-reflection chamber theorem. `ATTRIBUTION-QUALIFICATION.md` gives the precise primary citation and the prior-method qualifications. This package does not prove the inherited theorem.

## Open next questions

The remaining useful question is whether a dense rational three-coordinate word can escape these restrictions and use eight queries. The first step is to test a proposed word against the two-outsider and congruence conditions, then check its complete formal group-algebra identity. The present proofs do not cover every dense rational group. A paid tape implementation and the full supplier calculation would also be required before any kappa claim. These are open obligations, not work completed by this package.
