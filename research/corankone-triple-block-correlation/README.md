# A binary corank-one pair is negatively correlated with a third full guard

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof with an exact computer-assisted finite
component. For three pairwise orthogonal rank-one idempotents Ui on F2^m,
m>=3, let Ei mean that every leading principal minor through rank m-1 of
G(I-Ui)G^-1 is nonzero. With one uniformly weighted complete GL_m(F2) header,

```text
Pr(E1 E2 E3) < Pr(E1 E2)Pr(E3), every m>=3.
```

This answers the first bounded step in Open next question 1 of
[#4767](https://github.com/CrocSwap/integer-mult-bounds/pull/4767).
The earlier comparison with three independent marginals does not imply
this stronger two-block inequality. [PROOF.md](PROOF.md) cites the triple,
pair and marginal laws, derives the new ratio, and proves its uniform
tail for m>=43. Forty exact integer comparisons cover 3<=m<=42.
At m=4, the ratio of the joint probability to the block product is 40/189.
The result holds for each permutation of the split by symmetry.

## Reproduction and evidence

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-triple-block-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/corankone-triple-block-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-triple-block-correlation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-triple-block-correlation --check-source-history
```

Another CPython 3.12 interpreter can replace the local path. The direct
verifier prints `PASS_CORANKONE_TRIPLE_BLOCK_CORRELATION` in generated JSON.
It writes no files, uses only the standard library, and hashes all six
package files. Its receipt enumerates each finite proof case with its
positive integer gap and exact rational ratio. Nothing is handwritten
as a verification receipt.

The checks cover all 40 finite proof cases, all 86 additional dimensions
43<=m<=128, the exact integer constants of the uniform tail, and seven
controls. The controls detect grouped independence, a reversed leading
spectral sign, omission of the finite-GL correction, and four invalid
replay dimensions. Explicit checks remain active under optimized Python.
The three cited m=4 probabilities are 9/40, 1/80 and 1/1680.

## Scope, credit and limits

The counting laws are cited mathematical inputs, not the subject of an
independent audit. Nick Petalas's #4275 supplies the binary triple law,
#4261 the pair law, #4227 the marginal law, and #4767 the open grouped
question. Their exact retained-main source bytes are pinned as historical
provenance in SOURCES.json. The verifier imports no predecessor code and
has no external runtime inputs. The source-history check requires full
Git history; the direct verifier runs without Git.

Cinna Davis supplied the BIT request context. Source527, commdata2338 and
Jose Manuel retain the normalizer lineage credit. Chris R / Clear1nsight
retains the earlier #3950 counting context. The original card is
explicitly changed from an interface-formalization task to this counting
side question in TASK.json. Its link to the project is the density of
headers shared by several requests. It supplies no physical caller.

Only three fixed orthogonal kernel lines, binary arithmetic and complete
uniform headers are covered. No general negative-association theorem is
claimed. Odd fields, nonorthogonal kernels, larger blocks and restricted
header distributions remain outside scope. Selection, emission, dispatch,
dirty restoration, stock, precision and a complete paid physical invoice
are unknown. No new kappa, selected-frontier change, supplier admission or
complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and selected cold replay
are unrun. Both registered package modes pass locally. Ruff 0.14.0
E/F/B/UP and the AST function-size inspection also pass.

The card's historical first command, `scripts/research_baseline.py`, raises
`KeyError: 'bit_lower'` on the changed selected certificate schema. The
current replacement, `scripts/research_selected_baseline.py`, passes with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` at selected kappa 60403/20000000.
This is source-binding orientation, not a selected-construction replay.
The historical reporter is outside this package and is unchanged.

The verifier has fixed finite loops, no recursion or dynamic code
execution, and functions below sixty lines. CPython dynamic allocation
deviates from fixed allocation. The declared dimension bound 128,
eight spectral terms, forty retained cases, seven controls and six source
files of at most one MiB each bound this read-only replay. Invalid-domain
controls exercise its bounds. Warnings are errors in both registered
modes. A future expansion must retain or replace these resource bounds.

## Open next questions

1. Does the full three-event Bernoulli vector satisfy negative association?
   Compare E1 union E2 with E3 using `2p2-p3 < p1(2p1-p2)`. Together with
   the proved split and pair inequalities, this would cover the remaining
   increasing-event type on two coordinates. The union comparison is
   not proved here.
2. Does the pair-versus-singleton inequality hold over odd finite fields?
   Start with the cited all-field transfer at k=3 and its grouped ratio.
   An odd-field triple closed form or another uniform bound is missing.
3. Can a producer use a shared header with a favorable complete paid bill?
   Pin its kernel lines and actual header domain, then price selection,
   emission, dispatch, restoration, precision and stock. No such producer
   or complete invoice is supplied here.
