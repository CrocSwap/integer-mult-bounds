# Attribution and license

Prepared for **@navinor** with substantial **OpenAI GPT-6.1 Sol assistance** in
research, mathematical reasoning, implementation, verification and writing.
A scoped AI worker independently checked the written valuation/polygon argument;
AI code review is recorded in the validation note. Neither is human peer review.

New material is contributed under the repository's **Apache-2.0** license.
No predecessor executable code is copied into this package.

Ali Romman (@aliromman), [PR621](https://github.com/CrocSwap/integer-mult-bounds/pull/621)
at `520774462b19b29af41554b74def31f9d01e997e`, supplied the prime-power kernel
conditioning proof, integral tail-product representation and algebraic-nonunit
conclusion. Those are predecessor results, not claimed as new here.

The kernel originates in OpenAI's exact-DFT preprint at
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`; PR621's source manifest
retains the exact path, classical q-calculus attribution and earlier local-note
context. This package does not import or relicense those sources.

Related concurrent evidence was consulted and is credited: Scott Woolsey
Biggart (@swbiggart), #668's CRT resultant replay; Jason Willems (@at1as),
#666's composite Bezout/lifting package; Ryan Pinto (@Ambassators), #692's
weighted-stride verification; and Chafik Boukhalfa (@chafreaky), #628's rounded
cyclic scan and restoration work. None is a dependency of this verifier.

Hao Yan (@FanPUYen), [PR796](https://github.com/CrocSwap/integer-mult-bounds/pull/796)
at `22902155c7875139e43e4fdf15723142d6709bdd`, independently submitted the same
root-valuation formula and an all-embedding weighted-minimum replay through
radix 68. It appeared after this local claim but before this submission.
The final source/receipt comparison explicitly corroborates its overlapping
results. This contribution claims only distinct integral-divisibility evidence
and radix-81 coverage, not priority for that concurrent formula.

No literature-priority claim, new integer-multiplication exponent or practical
runtime improvement is made.
