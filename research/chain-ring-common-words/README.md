# Common update words over matrix chain rings

Every two-role target over a finite product of algebras
`M_m(K[t]/t^d)` has a **fixed three-factor word**, including singular and
zero targets, for every field K, m>=1 and d>=1. The paid factors have
right rows `e1,e2,e1` over K. There are no scratch roles or free endpoint
maps in this upper construction. A singular binary matrix-block example
has exact cost three at every nilpotency depth. For a single scalar
`K[t]/t^d` component, two paid factors and a scalar column permutation
suffice, with the exact zero/one/two classification in [PROOF.md](PROOF.md).

This is a scoped algebraic proof with bounded exact corroboration. **No new
kappa or supplier admission is claimed.** The selected conditional kappa
remains 0.00302015. Prepared for Cinna Davis / 1337isnot1337 with substantial
OpenAI Codex assistance; Apache-2.0. No subagents were used.

The specific addition to JoyboyBrian's
[PR5156](https://github.com/CrocSwap/integer-mult-bounds/pull/5156), exact head
`410240294708410635cdbc3d885cf999f8f0c33a`, is its requested singular radical
extension for matrix chain rings at arbitrary nilpotency depth. Its field
matrix-component absorption skeleton is retained. Nick Petalas's #4749
already handles invertible semilocal targets, while #4805 supplies the
matrix-algebra antecedent and #4276 supplies the exact two-factor criterion.
The new rectangular valuation completion handles singular top rows before
the inherited unit-completion argument is applied. Classical elimination
and stable range one retain their classical status. Further credit goes to
ToikY #4334, Wentao Li #4099 and the retained #2513 lineage.

## Complete endpoint

For `M=[[A,B],[C,D]]`, construct `a` and a right-unimodular row `[X Y]`
with `[A B]=a[X Y]`. Choose F with `E=X-YF` invertible and set
`b=(C-DF)E^-1`, `delta=D-bY`. The endpoint is exactly

```text
M = [[a,0],[b,I]] [[I,Y],[0,delta]] [[E,0],[F,I]].
```

The same block-column update sequence works in every component. Singular
coefficients are absorbed into the first factor. The target itself is
never inverted. The proof gives the all-field/all-size result; the finite
constructor searches the residue field for its pivot and is intended for
bounded replay, not an efficient general compiler.

## Reproduction and evidence

With CPython3.12 and its standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/chain-ring-common-words
python3.12 -B scripts/check_research_commit.py --package research/chain-ring-common-words --check-source-history
```

The registered normal and optimized commands both print a JSON receipt with
`PASS_CHAIN_RING_COMMON_WORDS`. The checker uses separate coefficientwise
polynomial convolution and matrix products rather than the constructor's
ring-operation tables. Its bounded domains cover:

- Every scalar target over F2[t]/t^d for d=1,2,3,4, over F3[t]/t^d for
  d=1,2, and over F5,F7: 79,572 targets. The literal two-factor endpoint is
  checked for every target. Exact one-factor costs are corroborated by a
  separately enumerated entire one-factor/free-map orbit in the two binary
  rings of sizes four and eight.
- Deterministic matrix-block targets with m=2,3, odd characteristic,
  torsion and singular top rows, zero targets, and nilpotency through five;
  the fixed skeleton is checked as well as the full output matrix.
- Forty arbitrary dirty-input executions, a three-component product with
  common right rows, nine rejecting two-factor charts for the singular
  sharp example, and eleven arithmetic, ordering, omission or input controls.

Each generated receipt binds all package Python, Markdown and JSON files by
SHA256. The replay writes no package files. `SOURCES.json` pins predecessor
proofs as historical provenance, not live executable dependencies. The pending
PR5156 proof is an explicitly separate immutable bibliographic reference,
with its commit, blob and SHA256 recorded; it is not a publication ancestor. Passing
these checks is author verification of the bounded replay; independent
human or proof-kernel acceptance of the universal proof is unclaimed.

## Research decision and limits

Base: canonical main `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority
revision7. [Canonical scope/claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144678).
The overlap snapshot had complete pagination for open PRs and Discussions
and all 6,918 local notes present at the pinned base; this is coverage, not
a novelty certificate. The original `bit-new-register-model` card is changed
explicitly to this coefficient-algebra side question in `TASK.json`.

The known multigenerator square-zero obstructions remain outside this
chain-ring statement. Nothing here grants arbitrary matrix coefficients
as native calls. Data-discarding factors are allowed in this formal model;
coefficient preparation, recovery of overwritten inputs, physical routing,
ownership, precision, stock and the complete recursive tariff are unknown.
The existing native and selected theorem hypotheses remain unresolved.
No selected operator suite, Lean or Docker run is part of this package.

**Expansion decision:** stop extending the algebraic family after this
proof. A next construction round requires an explicit actual native
producer/consumer and a favorable fully charged budget. Three unpriced
formal updates are insufficient evidence for increasing kappa.

## Open next questions

1. Can one actual native caller implement the emitted coefficients and
   recover overwritten inputs below its removed-work allowance? First
   express a named two-role target's coefficient blocks as permitted
   primitives and compute the entire child histogram, including routing
   and restoration. The absence of a priced coefficient producer is the
   present blocker.
2. Which singular matrix-block targets with two independent radical
   generators admit a common three-factor word? First test whether a
   specified singular top row has a right-unimodular completion. The
   present valuation-divisibility step need not hold, and the predecessor
   quotient obstructions must be retained. No further implementation
   expansion follows automatically from this question.
