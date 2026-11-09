# The pinned QSELF-pair interval needs exactly three queries

The original #6937 interval at events 457..575 cannot be replaced by two
QUERYs in the stated fixed q-even linear/affine model, even with arbitrary
finite helpers. Its response between q=+1 and q=-1, D9=1 has an exact
3 by 3 minor of determinant 8. The separately published three-query
replacement attains the bound. **No new kappa.**

This closes one local budget-reduction direction. It does not prove a
whole-caller optimum, a native complexity lower bound, or any of the five
global framework assumptions. The exact independent-input boundary, the
rank-one charged operation and the absence of free odd-q side information
are essential. See `PROOF.md` for the universal statement and exclusions.

## Reproduce

```sh
python3 -I -B research/p104-query-interval-optimum/verify.py
python3 -I -B research/p104-query-interval-optimum/review/check_covectors.py research/p104-query-interval-optimum
python3 -B scripts/research_package.py --package research/p104-query-interval-optimum
python3 -B scripts/check_research_commit.py --package research/p104-query-interval-optimum --check-modes
```

Expected lead status: `PASS_P104_QUERY_INTERVAL_OPTIMUM`, response rank 3,
minor determinant 8, and six deleted-site controls of rank 2. The independent
reverse-covector checker returns the same minor and six singular deletion
controls. Registered commands also run under `python -O`; no safety-critical
check relies on Python assertions. Both source words and the predecessor
formal attainment proof are authenticated locally, without Git or network.
Complete receipts are in `evidence/REPLAY.json` and `review/RESULT.json`.

## Provenance and credit

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Source: CrocSwap/integer-mult-bounds#6937 at
`a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`.
Attainment: [public QUERY-only package](https://github.com/CubeJerry/integer-mult-bounds/tree/617903497387a98f7ca929ad0b6928dd32abffec/research/p104-query-only-interval).
Exact byte and commit pins are in `DEPENDENCIES.json` and `SOURCES.json`.

Prepared for @CubeJerry with substantial OpenAI assistance. The two-chain
source and QUERY-only construction retain their predecessor credit.
The product-difference/rank argument is classical. The source-specific
matching lower bound and its independently coded certificates are this
package's contribution. Separate AI review is not human or proof-kernel
acceptance. Further scope and prior work are in `OVERLAP.md` and `NOTICE.md`.

## Open next questions

Can a complete-caller rearrangement, or a rigorously identified reachable
input subspace, reduce the paid budget? The present fixed-boundary minimum
does not answer that question. A next attempt must count all query-dependent
side information and prove its changed source boundary before applying a
new response bound. Literal rounded precision and native/compiler admission
of the existing three-query construction remain separate obligations.
