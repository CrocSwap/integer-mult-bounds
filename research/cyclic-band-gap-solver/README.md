# Cyclic band solves with a variable row gap

A complete integer solver now covers every real dyadic cyclic band matrix
with positive diagonal and a certified row gap delta>0. The gap may shrink
with the problem size. [PROOF.md](PROOF.md) gives an explicit all-input error
and integer-range proof. No constant near-identity or Woodbury-smallness
assumption is required.

The factorization uses at most 4NW^2 integer products and retains at most
(4W+1)N entries. Each complex solve uses at most 8NW products and 4N component
roundings/divisions. Exact integer accumulation and one rounding per factor
entry give sufficient precision

    q = max(input precision, output precision
            + O(log N + log(1+M) + log(1+Y) + log(1+1/delta))).

Here M bounds the input matrix row norm and Y bounds the complex RHS norm.
The executable uses the explicit inequalities in the proof, not this O-term.
At delta=1/4096, the 4,097-row width-four fixture needs 60 fractional bits
and a proven signed width of 151 bits. Its observed peak is 132 bits. Factor
preparation uses 261,836 products; each complex solve uses 130,960 products.
The complete residual meets the 2^-20 solution target.

This is an all-size numerical interface, with finite exact corroboration.
It extends the fixed-instance result in
[PR #5260](https://github.com/CrocSwap/integer-mult-bounds/pull/5260) and the
constant-gap band/Woodbury interface in Dugongue's
[PR #4554](https://github.com/CrocSwap/integer-mult-bounds/pull/4554).
Matrix formation, source approximation error, physical movement and the
complete multiplication invoice remain caller obligations. No new kappa,
Gaussian-family admission or selected-frontier change is claimed.

## Reproduce

Requires CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/cyclic-band-gap-solver
```

Expected: `PASS_CYCLIC_BAND_GAP` in normal and optimized modes, followed by
`PASS_REGISTERED_RESEARCH_PACKAGE`. [RESULT.json](RESULT.json) binds all
package files and records the exact results. A separately transcribed pivoted
rational solver checks 72 complex right-hand sides on 36 small cases. The
replay also checks nine matrix/RHS scale pairs, 129 symbolic cyclic patterns,
eight control groups and
original-matrix residuals for 257, 1,025 and 4,097 rows with gap 1/4096.

The source proofs and attribution are pinned in [SOURCES.json](SOURCES.json).
They are provenance, not imported runtime code. The base is canonical main
ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision7. The #5260 result is prior-work context, not an imported runtime or proof
assumption. Every declared source commit is an ancestor of this publication.
No other package is edited.
The full-history wrapper, selected cold replay, Lean and Docker were not run.
No independent human or proof-kernel review is claimed. Dictionary/indexing
and Python allocation overhead are outside the arithmetic count.

## Open next questions

Can a paid Gaussian production family meet the dyadic input contract with an
adequate source error budget? First bind one admitted family's exact delta,
width and coefficient-generation method. Then add its source and final-grid
errors, physical layout and outer recurrence. The numerical solve alone does
not supply those obligations. This question is open and unreserved.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Dugongue supplies the prior constant-gap native band/Woodbury proof; Ryanson
Jonathan supplies its independent scoped check. Classical diagonal dominance,
Gaussian elimination, Wilkinson's error analysis and Higham's exposition retain
their credit. The earlier batched principal-window note is a noncyclic
comparison. The Gaussian identity and source lineage retain OpenAI/math,
Harvey and van der Hoeven credit as stated in the pinned predecessor NOTICE.
No global novelty or new general stability theorem is claimed.
