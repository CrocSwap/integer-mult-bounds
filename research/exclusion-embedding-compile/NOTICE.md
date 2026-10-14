# Notice — exclusion embedding compile

Douglas R. Colkitt authored the ExclusionCircuit / SharedPoint / positive-side
screens, the reversible embedding compiler, and the original
`verify_embedding` nesting checks consumed by this tooling package.

Merged [CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
already replaced the reverse-frame expected-support genexpr with a closed-form
mask. This package accelerates the residual `compile` / nesting path inside
`verify_embedding` with identical compile maps and embedding receipts, and
updates source pins only.

Prepared by Wentao Li with substantial AI assistance, under Apache-2.0.
