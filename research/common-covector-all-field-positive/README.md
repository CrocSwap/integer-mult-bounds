# A common-covector pair is positively correlated over every finite field

This closes the odd-field sign question in Nick Petalas's [PR4807 README
question2](https://github.com/CrocSwap/integer-mult-bounds/pull/4807), as a modest
corollary of that source's exact all-field counting formula. It proves strict
`J>p^2` for every prime powerq>=2 and every dimensionm>=2. The count, marginal,
binary sign and suggested identityqD-A^2=q-1 remain predecessor credit.

The model is precise: independent columns a,c with one covectorb satisfying
ba=bc=1; corank-one complementsI-ab,I-cb; all proper leading principal minors;
complete equally weightedGL_m(F_q) headers. Other two-way pairs, first-pivot
requests, larger families and restricted header distributions are separate.
No physical producer/caller, supplier admission, newkappa or frontier change.

[PROOF.md](PROOF.md) cancels the credited ratio and proves `J/p^2>L>=1`.
It retains strictness at(q,m)=(2,2) and uses explicit positive-coefficient
polynomial identities to cover every dimension. This is a written universal
inequality proof, not extrapolation from finite field sizes.

## Evidence and reproduction

[CASES.json](CASES.json) freezes205 exact parameter pairs: q2..16 withn1..12,
andq25,27,32,49,64 withn1,2,3,8,16, wheren=m-1. Non-prime-power values
6,10,12,14,15 are explicitly algebra-only fixtures. No field arithmetic or
GL/header enumeration is claimed for this package.

The primary uses Fraction closed formulas and exact degree-bounded interpolation
for the four coefficient arrays. The independent engine uses polynomial
convolution, integer recurrences and Euclidean rational normalization. After
separate blind first seals, it compares the submitted205 actual rows and all
coefficient arrays as data. Both source prose files remain inert; no predecessor
executable or peer code is imported or executed. [RUN-RECORDS.json](RUN-RECORDS.json)
and [VALIDATION.md](VALIDATION.md) distinguish first runs and later checks.

From the repository root, CPython3.12, standard library only:

```sh
python3.12 -I -W error -B research/common-covector-all-field-positive/verify.py
python3.12 -I -W error -B research/common-covector-all-field-positive/oracle.py --check-primary research/common-covector-all-field-positive/RESULT.json
python3.12 -W error -B scripts/research_package.py --package research/common-covector-all-field-positive
```

[VERIFY.json](VERIFY.json) also registers both optimized modes. Direct replay
is read-only and needs noGit/network/compiler/Lean/Docker. Source/case/schema
bytes authenticate before computation. Exact receipt keys, integer/rational
and boolean types, duplicate/nonfinite/float guards and complete typed retained
comparisons remain active under-O. Primary controls comprise14 intended
rejections and one boundary fixture. Loops are bounded by205rows, n<=16,
q<=64 and interpolation matrices at most5by5. All new functions are below50
physical lines. CPython dynamic allocation, arbitrary-precision integers and
bounded recursive JSON comparison are declared managed-runtime deviations from
fixed allocation/no recursion. This is not formal verification.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. What is the law for two-way pairs with independent covectors? This is the
   distinct PR4807 question1. Start with a normalized partial-Gram pair; the
   common-covector orbit and formula used here do not transfer automatically.
2. Can a named actual producer and consumer use these headers profitably?
   Pin its legal header distribution and charge selection, emission, dispatch,
   restoration, stock, precision and the complete physical caller. Those costs
   and compatibility remain unknown.
3. Which restricted header catalogues preserve this sign? Start by naming one
   legal catalogue and its exact weights; complete uniform conjugation is an
   essential current premise, so this theorem supplies no restricted law.

## Credit

Nick Petalas4807 supplies the all-field joint law, dependent-pair subtraction,
binary theorem, sign question and suggested identity;4227 supplies the marginal,
4261 the partial-sum/header method,4778 the motivating two-way question and
4769/4274 the contrasting one-way law. Cinna Davis supplies the BIT request
context. source527, commdata2338, Jose Manuel and the retained normalizer/
recursive-closure lineage keep predecessor credit. The exact two prose sources
and original notices are preserved in inputs/ and [SOURCE-PINS.json](SOURCE-PINS.json).
Elementary polynomial expansion and rational inequalities are classical.

Prepared for ToikY with substantial OpenAI Codex assistance and separate AI
primary/oracle/static review. Apache-2.0. Independent human and proof-kernel
acceptance, a re-audit of4807's counts, native implementation and selected
operator replay remain unclaimed. No predecessor or selected source is changed.
